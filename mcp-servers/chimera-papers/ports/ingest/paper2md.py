"""Convert PDF files to markdown via MinerU CLI."""

import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def _log_mineru_streams(
    stdout: str | None,
    stderr: str | None,
    *,
    pdf_name: str,
    reason: str,
) -> None:
    """失败或疑似成功却无产物时，输出子进程完整 stdout/stderr 便于排查。"""
    out = (stdout or "").strip() or "(empty)"
    err = (stderr or "").strip() or "(empty)"
    logger.error("[Ingest] MinerU %s | %s | stdout:\n%s", reason, pdf_name, out)
    logger.error("[Ingest] MinerU %s | %s | stderr:\n%s", reason, pdf_name, err)


class MineruNotInstalledError(Exception):
    """`mineru` 可执行文件不在 PATH 中（与 PDF 缺失等 OSError 区分开）。"""


class MineruClient:
    """MinerU 命令行适配器，负责将 PDF 转换为 Markdown。"""

    def __init__(self, output_root: Path) -> None:
        if not output_root.is_absolute():
            raise ValueError(
                f"output_root MUST be an absolute path. Got: {output_root}"
            )

        self.output_root = output_root
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.cmd = self._detect_command()

    def _detect_command(self) -> str:
        found = shutil.which("mineru")
        if found:
            return found
        # The MCP server is launched via the venv interpreter directly (see
        # .mcp.json), not through venv activation, so .venv\Scripts is NOT on
        # PATH. mineru.exe ships beside the interpreter — resolve it there.
        sibling = shutil.which("mineru", path=str(Path(sys.executable).parent))
        if sibling:
            return sibling
        raise MineruNotInstalledError("MinerU is not installed or not in PATH.")

    def convert(self, pdf_path: Path) -> Path:
        if not pdf_path.is_absolute():
            raise ValueError(f"pdf_path MUST be an absolute path. Got: {pdf_path}")
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a .pdf file, got: {pdf_path.name}")

        folder_name = pdf_path.stem
        target_dir = self.output_root / folder_name
        target_md = target_dir / f"{folder_name}.md"

        if target_md.exists():
            logger.info("[Ingest] Skipping conversion, MD exists: %s", target_md)
            return target_md

        cmd = [
            self.cmd,
            "-p",
            str(pdf_path),
            "-o",
            str(self.output_root),
            "-m",
            "auto",
            "-d",
            "cuda",
        ]

        # MinerU (`mineru.exe`) is a console-subsystem app that spawns a uvicorn worker.
        # This MCP server is launched by Claude Code as a HEADLESS process (no inheritable
        # console). Spawned from there, mineru hung at interpreter startup — 5 MB RSS,
        # 0 CPU, zero output — until the timeout, though it runs fine from any shell.
        # Two things isolate the child from the headless parent's process context:
        #   * creationflags=CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP — give it its own
        #     clean console + process group instead of inheriting the server's console
        #     state / Ctrl-event group.
        #   * stdin=DEVNULL — never inherit the MCP JSON-RPC stdin pipe.
        # Output still goes to a temp FILE (unbounded sink) rather than capture_output's
        # fixed OS pipe, which separately deadlocked the chatty child.
        # See docs/incidents/2026-07-01-mineru-capture-deadlock.md and
        # docs/incidents/2026-07-02-mineru-hang-in-mcp-server.md.
        _spawn_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )
        with tempfile.NamedTemporaryFile(suffix=".mineru.log", delete=False) as tmp:
            log_path = Path(tmp.name)
        failure: Exception | None = None
        reason: str | None = None
        with log_path.open("w", encoding="utf-8", errors="replace") as logf:
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    stdin=subprocess.DEVNULL,
                    stdout=logf,
                    stderr=subprocess.STDOUT,
                    timeout=600,
                    creationflags=_spawn_flags,
                )
            except subprocess.TimeoutExpired as exc:
                failure, reason = exc, "timeout"
            except subprocess.CalledProcessError as exc:
                failure, reason = exc, "non-zero exit"
            except OSError as exc:
                failure, reason = exc, "os-error"
        # File handle is closed here — safe to read back (Windows share rules).
        mineru_stdout = log_path.read_text(encoding="utf-8", errors="replace")
        mineru_stderr = None
        log_path.unlink(missing_ok=True)

        if reason == "os-error":
            logger.error("[Ingest] Failed to execute MinerU command '%s': %s", self.cmd, failure)
            raise RuntimeError("Failed to execute MinerU command.") from failure
        if reason == "timeout":
            logger.error("[Ingest] MinerU timed out for %s", pdf_path.name)
            _log_mineru_streams(mineru_stdout, mineru_stderr, pdf_name=pdf_path.name, reason="timeout")
            raise RuntimeError(f"Conversion timed out for {pdf_path.name}") from failure
        if reason == "non-zero exit":
            logger.error("[Ingest] MinerU non-zero exit for %s", pdf_path.name)
            _log_mineru_streams(mineru_stdout, mineru_stderr, pdf_name=pdf_path.name, reason="non-zero exit")
            raise RuntimeError(f"Conversion failed for {pdf_path.name}") from failure

        if not target_md.exists():
            mds = sorted(target_dir.rglob("*.md"))
            if len(mds) == 1:
                return mds[0]
            if len(mds) > 1:
                logger.warning(
                    "[Ingest] Multiple markdown files found in %s, using %s",
                    target_dir,
                    mds[0].name,
                )
                return mds[0]
            _log_mineru_streams(
                mineru_stdout,
                mineru_stderr,
                pdf_name=pdf_path.name,
                reason="exit 0 but no .md",
            )
            raise FileNotFoundError(
                f"Conversion reported success but no MD found in {target_dir}"
            )

        return target_md
