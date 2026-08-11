"""Convert PDF files to markdown via MinerU CLI."""

import logging
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Device pin. MinerU has NO --device flag; it resolves the device from this env var,
# falling back to torch autodetect (mineru/utils/config_reader.py::get_device). The old
# `-d cuda` argv flag was inert — silently swallowed, since both `mineru` and the
# `mineru-api` worker it spawns are declared ignore_unknown_options. Pinning here is
# deliberate: a silent CPU fallback would make ingest an order of magnitude slower with
# no error to notice. Unset CHIMERA_MINERU_DEVICE (or export MINERU_DEVICE_MODE) to
# restore autodetect. See docs/incidents/2026-08-10-mineru-3x-drift.md.
MINERU_DEVICE = os.getenv("CHIMERA_MINERU_DEVICE", "cuda")

# Backend pin. `pipeline` runs NO VLM — layout + OCR + table models only. Measured over
# 5 cells x 3 papers (docs/incidents/2026-08-10-mineru-backend-flip.md): it matches
# hybrid-engine's text recall to within noise, produces identical image/table/equation
# counts, and runs 1.4-2.8x faster on a quarter of the VRAM. Every VLM path (hybrid-* and
# vlm-engine alike) transcribes chart PIXELS into markdown tables of approximate numbers
# that appear in no paper's text; `pipeline` cannot, because there is no VLM to do it.
# `--effort` is deliberately NOT set — it applies only to hybrid-* and is the expensive
# half of that fabrication.
MINERU_BACKEND = "pipeline"

# Conversion budget. MinerU enforces these ITSELF (passed via env below), so the normal
# deadline path is a child-side abort that runs mineru's own cleanup — it stops the
# mineru-api worker it spawned and removes its temp dir. Our wait() below is only a
# backstop for a child too wedged to honour its own deadline.
MINERU_TASK_BUDGET_SECONDS = 1200
MINERU_API_STARTUP_BUDGET_SECONDS = 300
# How long past the child's own deadline we wait before intervening.
BACKSTOP_MARGIN_SECONDS = 120
# Between the polite stop and the tree kill.
SHUTDOWN_GRACE_SECONDS = 30


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


def _resolve_output_markdown(target_dir: Path, stem: str) -> Path | None:
    """Locate the converted markdown inside MinerU's output folder for one paper.

    MinerU >= 3 nests a PER-BACKEND parse dir one level under the stem
    (mineru/cli/output_paths.py::build_parse_dir):
        <out>/<stem>/<method>/<stem>.md        backend=pipeline   (auto | txt | ocr)
        <out>/<stem>/vlm/<stem>.md             backend=vlm-*
        <out>/<stem>/hybrid_<method>/<stem>.md backend=hybrid-*
    MinerU < 3 wrote <out>/<stem>/<stem>.md flat. Probing only the flat path (as this
    module used to) means the primary lookup NEVER hits on 3.x and every convert limps
    through the recursive fallback — including the exists-check that is supposed to make
    conversion idempotent, which silently stopped working.

    Order: nested parse dir, then flat, then a recursive scan as the true last resort.
    """
    if not target_dir.is_dir():
        return None

    for parse_dir in sorted(p for p in target_dir.iterdir() if p.is_dir()):
        candidate = parse_dir / f"{stem}.md"
        if candidate.is_file():
            return candidate

    flat = target_dir / f"{stem}.md"
    if flat.is_file():
        return flat

    mds = sorted(target_dir.rglob("*.md"))
    if not mds:
        return None
    if len(mds) > 1:
        logger.warning(
            "[Ingest] No %s.md in any parse dir of %s; %s markdown files present, using %s",
            stem,
            target_dir,
            len(mds),
            mds[0].name,
        )
    return mds[0]


def _stop_child_gracefully(proc: "subprocess.Popen[bytes]", pdf_name: str) -> None:
    """End a wedged MinerU child without orphaning its GPU-holding worker.

    `mineru` spawns a `mineru-api` uvicorn worker as a GRANDCHILD. TerminateProcess
    (Popen.kill) ends only the direct child, leaving that worker alive holding ~4 GB of
    VRAM — the next convert then contends with a ghost. Escalation:
      1. Ctrl-Break to the process group (we own one, via CREATE_NEW_PROCESS_GROUP at
         spawn) — mineru's `finally` stops its local API server and cleans its temp dir.
      2. `taskkill /F /T` — kills the whole tree, no extra dependency.
    """
    try:
        if sys.platform == "win32":
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.terminate()
        logger.warning("[Ingest] Asked MinerU to shut down for %s; waiting %ss", pdf_name, SHUTDOWN_GRACE_SECONDS)
        proc.wait(timeout=SHUTDOWN_GRACE_SECONDS)
        logger.info("[Ingest] MinerU shut down cleanly for %s", pdf_name)
        return
    except subprocess.TimeoutExpired:
        logger.warning("[Ingest] MinerU ignored the shutdown request for %s; killing the tree", pdf_name)
    except (OSError, ValueError) as exc:
        logger.warning("[Ingest] Could not signal MinerU for %s (%s); killing the tree", pdf_name, exc)

    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60,
                check=False,
            )
        else:
            proc.kill()
        proc.wait(timeout=60)
    except Exception as exc:  # last resort — never let cleanup mask the real failure
        logger.error("[Ingest] Failed to kill the MinerU tree for %s: %s", pdf_name, exc)


class MineruNotInstalledError(Exception):
    """`mineru` 可执行文件不在 PATH 中（与 PDF 缺失等 OSError 区分开）。"""


class MineruOutputMissingError(RuntimeError):
    """MinerU exited 0 but wrote no markdown — a CONVERSION failure, not a missing input.

    This used to be a bare ``FileNotFoundError``, which the tool layer catches as
    "[Convert Error] PDF not found" (miner_tools.py:233) — the operator was told the input
    was missing when in fact the input was fine and the converter produced nothing. A
    RuntimeError subclass falls through to the generic branch, which reports the real message.
    """


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

        existing_md = _resolve_output_markdown(target_dir, folder_name)
        if existing_md is not None:
            logger.info("[Ingest] Skipping conversion, MD exists: %s", existing_md)
            return existing_md

        cmd = [
            self.cmd,
            "-p",
            str(pdf_path),
            "-o",
            str(self.output_root),
            "-m",
            "auto",
            "-b",
            MINERU_BACKEND,
        ]

        # Device and deadlines travel in the ENV, not argv — that is where MinerU reads
        # them. An operator-set value wins, so a debug session can override without a
        # code change.
        child_env = os.environ.copy()
        if MINERU_DEVICE:
            child_env.setdefault("MINERU_DEVICE_MODE", MINERU_DEVICE)
        child_env.setdefault(
            "MINERU_TASK_RESULT_TIMEOUT_SECONDS", str(MINERU_TASK_BUDGET_SECONDS)
        )
        child_env.setdefault(
            "MINERU_LOCAL_API_STARTUP_TIMEOUT_SECONDS",
            str(MINERU_API_STARTUP_BUDGET_SECONDS),
        )

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
        backstop = MINERU_TASK_BUDGET_SECONDS + BACKSTOP_MARGIN_SECONDS
        with log_path.open("w", encoding="utf-8", errors="replace") as logf:
            try:
                # Popen, not run(): a deadline has to be able to shut the child down
                # politely, and run()'s timeout only offers TerminateProcess.
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.DEVNULL,
                    stdout=logf,
                    stderr=subprocess.STDOUT,
                    creationflags=_spawn_flags,
                    env=child_env,
                )
                try:
                    returncode = proc.wait(timeout=backstop)
                except subprocess.TimeoutExpired as exc:
                    # The child blew through its OWN budget without self-aborting.
                    _stop_child_gracefully(proc, pdf_path.name)
                    failure, reason = exc, "timeout"
                except BaseException:
                    # subprocess.run() killed the child on ANY exception escaping the wait;
                    # Popen does not, so a KeyboardInterrupt or a cancelled caller would
                    # otherwise orphan MinerU and its GPU-holding worker. Restore that
                    # guarantee, then let the exception through untouched.
                    _stop_child_gracefully(proc, pdf_path.name)
                    raise
                else:
                    if returncode != 0:
                        failure = subprocess.CalledProcessError(returncode, cmd)
                        reason = "non-zero exit"
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
            logger.error(
                "[Ingest] MinerU ignored its own %ss budget for %s (backstop at %ss)",
                MINERU_TASK_BUDGET_SECONDS,
                pdf_path.name,
                backstop,
            )
            _log_mineru_streams(mineru_stdout, mineru_stderr, pdf_name=pdf_path.name, reason="timeout")
            raise RuntimeError(
                f"Conversion timed out for {pdf_path.name} "
                f"(wedged past its {MINERU_TASK_BUDGET_SECONDS}s budget; process tree stopped)"
            ) from failure
        if reason == "non-zero exit":
            logger.error("[Ingest] MinerU non-zero exit for %s", pdf_path.name)
            _log_mineru_streams(mineru_stdout, mineru_stderr, pdf_name=pdf_path.name, reason="non-zero exit")
            # L.B.6 F4: the child's output is sunk to a temp log, so the actual cause (commonly a
            # CUDA OOM) never reached the caller — only "Conversion failed". Carry the diagnostic
            # substring into the exception message so the MCP layer can surface it.
            # The hint must MATCH the failure, not merely co-occur with it: the device is now
            # pinned to cuda in the env, so bare "cuda" appears in healthy logs too and would
            # label every failure an OOM.
            lowered = mineru_stdout.lower()
            hint = ""
            if "out of memory" in lowered or "cuda_error_out_of_memory" in lowered:
                hint = " (CUDA out of memory)"
            elif "timed out waiting for" in lowered or "task timed out" in lowered:
                hint = f" (hit its own {MINERU_TASK_BUDGET_SECONDS}s budget and self-aborted)"
            raise RuntimeError(
                f"Conversion failed for {pdf_path.name}{hint}"
            ) from failure

        converted_md = _resolve_output_markdown(target_dir, folder_name)
        if converted_md is None:
            _log_mineru_streams(
                mineru_stdout,
                mineru_stderr,
                pdf_name=pdf_path.name,
                reason="exit 0 but no .md",
            )
            raise MineruOutputMissingError(
                f"Conversion reported success but no MD found in {target_dir}"
            )

        return converted_md
