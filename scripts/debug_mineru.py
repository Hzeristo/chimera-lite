#!/usr/bin/env python
"""White-box debug harness for the MinerU PDF->Markdown ingest leg.

Production calls MinerU through exactly one seam --
``mcp-servers/chimera-papers/ports/ingest/paper2md.py::MineruClient.convert`` -- which
sinks the child's output to a temp log, deletes it, and returns a Path. That seam is a
BLACK BOX: you cannot see which device ran, which flags survived, or what the child
actually wrote. This script is the white-box counterpart. It shells out to the same
``mineru`` executable with the same spawn discipline, but keeps every artifact and
measures the run from outside.

Three questions it answers, empirically, on this box:

  1. IS CUDA ACTUALLY CALLED?  MinerU 3.x resolves its device in
     ``mineru/utils/config_reader.py::get_device()`` -- ``MINERU_DEVICE_MODE`` if set,
     else torch autodetect. There is NO ``--device`` CLI flag. The harness pins/reads
     that env var, and independently samples ``nvidia-smi`` (GPU utilization, memory,
     and the per-process compute-app table) WHILE the child runs, so the verdict rests
     on observed device occupancy rather than on a log line the child chose to print.

  2. WHICH PARAMS WORK?  The installed CLI surface is discovered at runtime
     (``probe --cli``), so a MinerU upgrade that renames a flag shows up as a diff
     rather than as a mystery failure. Note that mineru's click command is declared
     ``ignore_unknown_options=True, allow_extra_args=True`` -- UNKNOWN FLAGS DO NOT
     ERROR. They are forwarded verbatim to the spawned ``mineru-api`` child, which is
     ALSO declared ignore-unknown, so a stale flag is silently inert. ``--emulate-prod``
     replays production's exact argv so that inertness is visible instead of assumed.

  3. WHERE DO ARTIFACTS LAND?  MinerU 3.x nests a per-backend parse dir under the stem
     (``mineru/cli/output_paths.py::build_parse_dir``): ``<out>/<stem>/<method>`` for
     pipeline, ``<out>/<stem>/vlm`` for vlm-*, ``<out>/<stem>/hybrid_<method>`` for
     hybrid-*. The harness dumps the full tree, reports which markdown
     ``PaperLoader.extract_and_clean`` would select (first exact ``<stem>.md``, else the
     first ``*.md`` found by rglob), and diffs that against the path ``MineruClient``
     probes first -- ``<out>/<stem>/<stem>.md``.

Nothing here imports the chimera domain layer and nothing writes to the production
papers tree. Output goes to ``playground/mineru_debug/<timestamp>-<tag>/`` (override
with ``--out-root``), so a debug run can never be mistaken for an ingest.

USAGE (repo root, project venv):

    .venv/Scripts/python.exe scripts/debug_mineru.py probe
    .venv/Scripts/python.exe scripts/debug_mineru.py probe --cli

    # one run, defaults (hybrid-engine + medium effort, MinerU 3.x defaults)
    .venv/Scripts/python.exe scripts/debug_mineru.py run --pdf papers/arxivpdf/2509.24871.pdf

    # the expensive path, first 8 pages only, GPU sampled every 2s
    .venv/Scripts/python.exe scripts/debug_mineru.py run --pdf <p.pdf> \
        --backend hybrid-engine --effort high --pages 8 --sample-interval 2

    # replay production's argv verbatim (proves whether `-d cuda` does anything)
    .venv/Scripts/python.exe scripts/debug_mineru.py run --pdf <p.pdf> --emulate-prod

    # force CPU to get a contrast baseline for the CUDA verdict
    .venv/Scripts/python.exe scripts/debug_mineru.py run --pdf <p.pdf> --device cpu

    # A/B the backends and print a comparison table
    .venv/Scripts/python.exe scripts/debug_mineru.py matrix --pdf <p.pdf> --pages 8

Each run writes ``_debug_report.json`` (machine-readable) and ``_mineru.log`` (the
child's full stdout+stderr, kept -- production deletes it) next to the artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = REPO_ROOT / "playground" / "mineru_debug"
DEFAULT_PDF_DIR = REPO_ROOT / "papers" / "arxivpdf"

# Production argv, verbatim from paper2md.py::MineruClient.convert (minus -p/-o).
PROD_EXTRA_ARGS = ("-m", "auto", "-d", "cuda")

# mineru/utils/config_reader.py + mineru/cli/api_client.py read these. Surfaced in the
# probe because they, not the CLI flags, are where device and timeout control actually live.
INTERESTING_ENV = (
    "MINERU_DEVICE_MODE",
    "MINERU_VIRTUAL_VRAM_SIZE",
    "MINERU_MODEL_SOURCE",
    "MINERU_TOOLS_CONFIG_JSON",
    "MINERU_LOG_LEVEL",
    "MINERU_FORMULA_ENABLE",
    "MINERU_TABLE_ENABLE",
    "MINERU_PROCESSING_WINDOW_SIZE",
    "MINERU_HYBRID_BATCH_RATIO",
    "MINERU_API_MAX_CONCURRENT_REQUESTS",
    "MINERU_LOCAL_API_LAUNCH_MODE",
    "MINERU_LOCAL_API_STARTUP_TIMEOUT_SECONDS",
    "MINERU_TASK_RESULT_TIMEOUT_SECONDS",
    "MINERU_ENABLE_PIPELINE_INFERENCE_LOCKS",
    "CUDA_VISIBLE_DEVICES",
)

# The comparison cells. NOT a grid: the axes do not apply uniformly. `--effort` is honoured
# only by hybrid-* backends, `-m method` only by pipeline and hybrid-* (vlm-engine ignores
# both), so a backend x method x effort grid would spend most of its runs on duplicates.
# `ocr` is omitted -- it is the scanned-document path, and this corpus is born-digital arXiv.
# hybrid-txt-medium exists to test one question: does `auto` correctly classify arXiv PDFs
# as text? If it matches hybrid-auto-medium byte for byte, the method axis collapses.
CELLS: dict[str, dict[str, Any]] = {
    "pipeline-auto": {"backend": "pipeline", "method": "auto", "effort": None},
    "vlm-engine": {"backend": "vlm-engine", "method": None, "effort": None},
    "hybrid-auto-medium": {"backend": "hybrid-engine", "method": "auto", "effort": "medium"},
    "hybrid-auto-high": {"backend": "hybrid-engine", "method": "auto", "effort": "high"},
    "hybrid-txt-medium": {"backend": "hybrid-engine", "method": "txt", "effort": "medium"},
}


# --------------------------------------------------------------------------- probing


def resolve_mineru_exe() -> dict[str, Any]:
    """Mirror MineruClient._detect_command so the harness runs the SAME binary.

    The MCP server is launched by the venv interpreter directly, so ``.venv\\Scripts``
    is not on PATH; mineru.exe is found beside ``sys.executable``. Both candidates are
    reported because a PATH-shadowing global install is a real failure mode here.
    """
    on_path = shutil.which("mineru")
    sibling = shutil.which("mineru", path=str(Path(sys.executable).parent))
    return {
        "on_path": on_path,
        "beside_interpreter": sibling,
        "selected": on_path or sibling,
        "shadowed": bool(on_path and sibling and Path(on_path) != Path(sibling)),
    }


def probe_torch() -> dict[str, Any]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment probe
        return {"import_ok": False, "error": repr(exc)}

    info: dict[str, Any] = {
        "import_ok": True,
        "torch_version": torch.__version__,
        "cuda_build": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
    }
    if info["cuda_available"]:
        props = torch.cuda.get_device_properties(0)
        info.update(
            device_count=torch.cuda.device_count(),
            device_name=torch.cuda.get_device_name(0),
            capability=f"sm_{props.major}{props.minor}",
            total_vram_gb=round(props.total_memory / 1024**3, 2),
        )
    return info


def probe_mineru_device() -> dict[str, Any]:
    """Ask MinerU itself which device it would pick -- its resolver, not our guess."""
    try:
        from mineru.utils.config_reader import get_device
        from mineru.version import __version__ as mineru_version
    except Exception as exc:  # pragma: no cover - environment probe
        return {"import_ok": False, "error": repr(exc)}
    return {
        "import_ok": True,
        "mineru_version": mineru_version,
        "get_device": get_device(),
        "env_override": os.environ.get("MINERU_DEVICE_MODE"),
    }


def probe_engine_deps() -> dict[str, str]:
    """hybrid-engine only hard-requires torch, but which VLM runtime is present decides speed."""
    import importlib.metadata as md

    names = (
        "mineru",
        "mineru-vl-utils",
        "torch",
        "torchvision",
        "transformers",
        "onnxruntime",
        "onnxruntime-gpu",
        "vllm",
        "lmdeploy",
        "sglang",
    )
    out: dict[str, str] = {}
    for name in names:
        try:
            out[name] = md.version(name)
        except Exception:
            out[name] = "MISSING"
    return out


def probe_cli_surface(exe: str) -> str:
    proc = subprocess.run(
        [exe, "--help"], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL
    )
    return proc.stdout or proc.stderr


def nvidia_smi_available() -> bool:
    return shutil.which("nvidia-smi") is not None


# ------------------------------------------------------------------------- sampling


@dataclass
class GpuSample:
    t: float
    util_pct: int
    mem_used_mb: int


def descendant_pids(root_pid: int) -> set[int]:
    """The run's own process tree: mineru (child) + the mineru-api worker (grandchild)."""
    try:
        import psutil

        proc = psutil.Process(root_pid)
        return {root_pid} | {child.pid for child in proc.children(recursive=True)}
    except Exception:
        return {root_pid}


def kill_tree(proc: subprocess.Popen) -> None:
    try:
        import psutil

        parent = psutil.Process(proc.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except Exception:
        proc.kill()
    try:
        proc.wait(timeout=30)
    except Exception:
        pass


class GpuSampler(threading.Thread):
    """Poll nvidia-smi during the run.

    This is the load-bearing part of the CUDA verdict: MinerU's own logs can claim a
    device without touching it, and the work happens in a GRANDCHILD (mineru spawns a
    local mineru-api uvicorn worker), so in-process torch introspection would miss it.
    Observed utilization and the compute-app process table cannot be faked by a log line.

    Windows/WDDM lists EVERY desktop app in ``--query-compute-apps`` and reports their
    memory as ``[N/A]``, so a raw dump of that table is ~50 rows of Explorer and browser
    noise and proves nothing. The sampler therefore tracks the run's own process tree and
    reports the intersection separately -- that intersection is the attributable evidence.
    """

    def __init__(self, interval: float) -> None:
        super().__init__(daemon=True)
        self.interval = interval
        self.samples: list[GpuSample] = []
        self.compute_apps: dict[int, str] = {}
        self.tracked_pids: set[int] = set()
        self._root_pid: int | None = None
        self._stop = threading.Event()
        self.enabled = nvidia_smi_available()

    def track(self, root_pid: int) -> None:
        """Called once the child exists; before that the sampler only reads the GPU."""
        self._root_pid = root_pid

    def _query(self, args: list[str]) -> str:
        proc = subprocess.run(
            ["nvidia-smi", *args, "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=15,
            stdin=subprocess.DEVNULL,
        )
        return proc.stdout or ""

    def run(self) -> None:  # pragma: no cover - timing-dependent
        if not self.enabled:
            return
        start = time.monotonic()
        while not self._stop.is_set():
            try:
                if self._root_pid is not None:
                    self.tracked_pids |= descendant_pids(self._root_pid)
                lines = self._query(
                    ["--query-gpu=utilization.gpu,memory.used"]
                ).strip().splitlines()
                if lines:
                    util, mem = (part.strip() for part in lines[0].split(","))
                    self.samples.append(
                        GpuSample(
                            t=round(time.monotonic() - start, 2),
                            util_pct=int(util),
                            mem_used_mb=int(mem),
                        )
                    )
                for row in self._query(
                    ["--query-compute-apps=pid,process_name,used_memory"]
                ).strip().splitlines():
                    if not row.strip():
                        continue
                    pid_text = row.split(",", 1)[0].strip()
                    if pid_text.isdigit():
                        self.compute_apps[int(pid_text)] = row.strip()
            except Exception:
                pass
            self._stop.wait(self.interval)

    def stop(self) -> None:
        self._stop.set()

    def summary(self) -> dict[str, Any]:
        if not self.enabled:
            return {"available": False, "reason": "nvidia-smi not on PATH"}
        if not self.samples:
            return {"available": True, "samples": 0, "note": "run too short to sample"}
        ours = [row for pid, row in sorted(self.compute_apps.items()) if pid in self.tracked_pids]
        return {
            "available": True,
            "samples": len(self.samples),
            "peak_util_pct": max(s.util_pct for s in self.samples),
            "peak_mem_used_mb": max(s.mem_used_mb for s in self.samples),
            "baseline_mem_used_mb": self.samples[0].mem_used_mb,
            "run_compute_apps": ours,
            "run_pids_tracked": len(self.tracked_pids),
            "other_compute_apps_count": len(self.compute_apps) - len(ours),
            "trace": [asdict(s) for s in self.samples],
        }


class LogTail(threading.Thread):
    """Echo the child's log file to the console while it is being written.

    Production sinks mineru's output to a FILE, not to ``capture_output``'s fixed OS
    pipe, because the chatty child deadlocked the pipe
    (docs/incidents/2026-07-01-mineru-capture-deadlock.md). The harness keeps that
    file sink -- it must reproduce production's spawn shape, not a friendlier one --
    and gets live feedback by tailing the file instead.
    """

    def __init__(self, path: Path, echo: bool) -> None:
        super().__init__(daemon=True)
        self.path = path
        self.echo = echo
        self._stop = threading.Event()

    def run(self) -> None:  # pragma: no cover - timing-dependent
        if not self.echo:
            return
        pos = 0
        while not self._stop.is_set():
            try:
                if self.path.exists():
                    with self.path.open("r", encoding="utf-8", errors="replace") as fh:
                        fh.seek(pos)
                        chunk = fh.read()
                        pos = fh.tell()
                    if chunk:
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
            except Exception:
                pass
            self._stop.wait(0.5)

    def stop(self) -> None:
        self._stop.set()


# ------------------------------------------------------------------- output analysis


def pdf_text_baseline(pdf: Path, start_page: int | None, end_page: int | None) -> str:
    """Raw text straight from the PDF, as the ground truth for text fidelity.

    pypdfium2 ships with MinerU, so this needs no poppler/pdftotext on PATH. It is a dumb
    extractor -- no layout reconstruction, no reading order -- which is exactly what makes
    it a fair baseline: it cannot invent text, so anything in the markdown that is absent
    here was either restructured by the backend or made up by it.
    """
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(pdf))
    try:
        first = start_page or 0
        last = end_page if end_page is not None else len(doc) - 1
        last = min(last, len(doc) - 1)
        chunks = []
        for index in range(first, last + 1):
            page = doc[index]
            textpage = page.get_textpage()
            chunks.append(textpage.get_text_bounded())
            textpage.close()
            page.close()
        return "\n".join(chunks)
    finally:
        doc.close()


def normalized_words(text: str) -> list[str]:
    """Lowercase alphanumeric token stream -- strips markdown syntax and layout noise."""
    import re

    return re.findall(r"[a-z0-9]+", text.lower())


def _ngram_set(words: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def text_fidelity(md_text: str, baseline_text: str, n: int = 5) -> dict[str, Any]:
    """Two-sided n-gram comparison of the markdown against the PDF's own text.

    ``source_recall``  -- how much of the PDF's text survived into the markdown. Low means
                          the backend DROPPED content.
    ``unbacked_ratio`` -- how much of the markdown is NOT in the PDF's text. Some is benign
                          (table restructuring, heading markup), but this is also where
                          invented content lands, so a jump between cells is a red flag.
    ``novel_tokens``   -- words present in the markdown and absent from the PDF vocabulary;
                          catches character-level corruption such as "original" -> "origina".

    Read all three COMPARATIVELY, between cells on the same paper. None is meaningful as an
    absolute: the baseline extractor mangles ligatures and hyphenation, so a clean backend
    still scores well short of 100% recall and carries a floor of "novel" tokens. What is
    meaningful is one cell scoring worse than another on identical input.
    """
    md_words = normalized_words(md_text)
    base_words = normalized_words(baseline_text)
    if len(md_words) < n or len(base_words) < n:
        return {"error": "text too short to compare"}

    md_grams = _ngram_set(md_words, n)
    base_grams = _ngram_set(base_words, n)
    base_vocab = set(base_words)
    novel = sorted({w for w in md_words if w not in base_vocab and w.isalpha() and len(w) > 3})

    return {
        "source_recall_pct": round(100 * len(base_grams & md_grams) / len(base_grams), 1),
        "unbacked_ratio_pct": round(100 * len(md_grams - base_grams) / len(md_grams), 1),
        "md_words": len(md_words),
        "baseline_words": len(base_words),
        "novel_token_count": len(novel),
        "novel_tokens_sample": novel[:25],
    }


def chart_transcriptions(md_text: str) -> dict[str, Any]:
    """Count the <details> chart-transcription blocks that effort=high emits.

    Each one is a markdown table of values a VLM read off figure PIXELS ("~55", "~70").
    Those numbers are in no paper's text, sit unmarked beside verbatim prose, and are
    indistinguishable from paper-stated figures to anything downstream that reads this file
    for a number. Counting them makes the laundering surface a measured quantity.
    """
    import re

    summaries = re.findall(r"<summary>([^<]*)</summary>", md_text)
    blocks = md_text.count("<details>")
    approx = len(re.findall(r"~\s*\d", md_text))
    return {
        "details_blocks": blocks,
        "summary_labels": sorted(summaries),
        "approx_number_markers": approx,
    }


def analyze_markdown(md_path: Path) -> dict[str, Any]:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return {
        "bytes": md_path.stat().st_size,
        "lines": len(lines),
        "chars": len(text),
        "image_refs": text.count("!["),
        "html_tables": text.count("<table"),
        "display_formulas": text.count("$$") // 2,
        "headings": sum(1 for line in lines if line.startswith("#")),
        "head": "\n".join(lines[:12]),
    }


def inspect_output(out_root: Path, stem: str) -> dict[str, Any]:
    """Walk the output tree and report what production's two consumers would see."""
    stem_dir = out_root / stem
    tree: list[dict[str, Any]] = []
    if stem_dir.is_dir():
        for path in sorted(stem_dir.rglob("*")):
            if path.is_file():
                tree.append(
                    {
                        "rel": str(path.relative_to(stem_dir)).replace("\\", "/"),
                        "bytes": path.stat().st_size,
                    }
                )

    all_md = sorted(stem_dir.rglob("*.md")) if stem_dir.is_dir() else []
    # MineruClient.convert probes this exact path first, then falls back to rglob.
    mineru_client_fast_path = stem_dir / f"{stem}.md"
    # PaperLoader.extract_and_clean: first md whose stem matches, else md_files[0].
    exact = next((m for m in all_md if m.stem == stem), None)
    loader_pick = exact or (all_md[0] if all_md else None)

    parse_dirs = sorted(
        {str(m.parent.relative_to(stem_dir)).replace("\\", "/") for m in all_md}
    )

    result: dict[str, Any] = {
        "stem_dir": str(stem_dir),
        "stem_dir_exists": stem_dir.is_dir(),
        "file_count": len(tree),
        "total_bytes": sum(item["bytes"] for item in tree),
        "parse_dirs_containing_md": parse_dirs,
        "markdown_files": [
            str(m.relative_to(stem_dir)).replace("\\", "/") for m in all_md
        ],
        "images": sum(1 for item in tree if "/images/" in item["rel"]),
        "mineru_client_fast_path_hit": mineru_client_fast_path.exists(),
        "paper_loader_would_pick": (
            str(loader_pick.relative_to(stem_dir)).replace("\\", "/")
            if loader_pick
            else None
        ),
        "paper_loader_exact_match": exact is not None,
        "tree": tree,
    }
    if loader_pick is not None:
        result["markdown_stats"] = analyze_markdown(loader_pick)
        result["resolved_markdown_path"] = str(loader_pick)
    return result


def quality_metrics(output: dict[str, Any], cfg: "RunConfig") -> dict[str, Any]:
    """Text fidelity + injection, computed against the PDF's own text over the SAME pages."""
    md_path = output.get("resolved_markdown_path")
    if not md_path:
        return {"error": "no markdown produced"}
    md_text = Path(md_path).read_text(encoding="utf-8", errors="replace")
    try:
        baseline = pdf_text_baseline(cfg.pdf, cfg.start_page, cfg.end_page)
    except Exception as exc:
        return {"error": f"baseline extraction failed: {exc!r}"}
    metrics = text_fidelity(md_text, baseline)
    metrics["injection"] = chart_transcriptions(md_text)
    return metrics


# ------------------------------------------------------------------------- the run


@dataclass
class RunConfig:
    pdf: Path
    out_dir: Path
    backend: str | None = None
    effort: str | None = None
    method: str | None = None
    lang: str | None = None
    formula: bool | None = None
    table: bool | None = None
    image_analysis: bool | None = None
    start_page: int | None = None
    end_page: int | None = None
    device: str | None = None
    timeout: int = 3600
    emulate_prod: bool = False
    extra: list[str] = field(default_factory=list)
    spawn_mode: str = "headless"
    sample_interval: float = 3.0
    echo: bool = True

    def argv(self, exe: str) -> list[str]:
        cmd = [exe, "-p", str(self.pdf), "-o", str(self.out_dir)]
        if self.emulate_prod:
            # Verbatim means verbatim: every other flag on this config is DROPPED, so a
            # --pages / --backend passed alongside --emulate-prod does nothing. Warned
            # about in build_run_config rather than silently honoured.
            return cmd + list(PROD_EXTRA_ARGS) + self.extra
        if self.method:
            cmd += ["-m", self.method]
        if self.backend:
            cmd += ["-b", self.backend]
        if self.effort:
            cmd += ["--effort", self.effort]
        if self.lang:
            cmd += ["-l", self.lang]
        if self.start_page is not None:
            cmd += ["-s", str(self.start_page)]
        if self.end_page is not None:
            cmd += ["-e", str(self.end_page)]
        if self.formula is not None:
            cmd += ["-f", str(self.formula)]
        if self.table is not None:
            cmd += ["-t", str(self.table)]
        if self.image_analysis is not None:
            cmd += ["--image-analysis", str(self.image_analysis)]
        return cmd + self.extra


def execute(cfg: RunConfig) -> dict[str, Any]:
    exe_info = resolve_mineru_exe()
    exe = exe_info["selected"]
    if not exe:
        raise SystemExit("mineru executable not found (PATH or beside the interpreter).")

    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    log_path = cfg.out_dir / "_mineru.log"
    cmd = cfg.argv(exe)

    env = os.environ.copy()
    if cfg.device:
        env["MINERU_DEVICE_MODE"] = cfg.device
    # The child inherits the harness env; the report records what it actually saw.
    env_seen = {k: env.get(k) for k in INTERESTING_ENV if env.get(k) is not None}

    # Production spawns mineru from a HEADLESS MCP server process, which hung the child
    # at interpreter startup until it got its own console + process group and a DEVNULL
    # stdin (docs/incidents/2026-07-02-mineru-hang-in-mcp-server.md). "headless" replays
    # those flags; "inherit" runs it like a plain shell invocation, for bisection.
    if cfg.spawn_mode == "headless":
        spawn_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )
    else:
        spawn_flags = 0

    print(f"[debug_mineru] exe        : {exe}")
    if exe_info["shadowed"]:
        print(f"[debug_mineru] WARNING    : PATH mineru shadows the venv one ({exe_info})")
    print(f"[debug_mineru] argv       : {' '.join(cmd)}")
    print(f"[debug_mineru] out_dir    : {cfg.out_dir}")
    print(f"[debug_mineru] device pin : MINERU_DEVICE_MODE={env.get('MINERU_DEVICE_MODE')}")
    print(f"[debug_mineru] spawn_mode : {cfg.spawn_mode} (flags={spawn_flags})")
    print(f"[debug_mineru] log        : {log_path}")
    print("[debug_mineru] --- child output ---")

    sampler = GpuSampler(cfg.sample_interval)
    tail = LogTail(log_path, cfg.echo)
    started_wall = datetime.now().isoformat(timespec="seconds")
    t0 = time.monotonic()
    exit_code: int | None = None
    failure: str | None = None

    sampler.start()
    tail.start()
    with log_path.open("w", encoding="utf-8", errors="replace") as logf:
        try:
            # Popen, not subprocess.run: the harness needs the child's pid to attribute
            # GPU occupancy to this run's process tree. Everything else about the spawn
            # matches production (DEVNULL stdin, file sink, creation flags).
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=logf,
                stderr=subprocess.STDOUT,
                creationflags=spawn_flags,
                env=env,
            )
            sampler.track(proc.pid)
            try:
                exit_code = proc.wait(timeout=cfg.timeout)
            except subprocess.TimeoutExpired:
                failure = f"timeout after {cfg.timeout}s"
                # Production's subprocess.run(timeout=...) kills only the DIRECT child;
                # the mineru-api grandchild can outlive it and keep holding VRAM. The
                # harness kills the whole tree so a timed-out debug run leaves nothing
                # behind -- a divergence from prod worth remembering when reading results.
                kill_tree(proc)
        except OSError as exc:
            failure = f"os-error: {exc!r}"
    elapsed = round(time.monotonic() - t0, 1)
    sampler.stop()
    tail.stop()
    tail.join(timeout=2)
    sampler.join(timeout=5)

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    print("[debug_mineru] --- end child output ---")

    report = {
        "started": started_wall,
        "elapsed_seconds": elapsed,
        "exit_code": exit_code,
        "failure": failure,
        "argv": cmd,
        "emulate_prod": cfg.emulate_prod,
        "spawn_mode": cfg.spawn_mode,
        "config": {
            k: (str(v) if isinstance(v, Path) else v)
            for k, v in asdict(cfg).items()
            if k not in {"echo", "sample_interval"}
        },
        "env_seen": env_seen,
        "mineru_exe": exe_info,
        "torch": probe_torch(),
        "mineru_device_resolver": probe_mineru_device(),
        "gpu": sampler.summary(),
        "log_signals": scan_log(log_text),
        "log_bytes": len(log_text),
        "output": inspect_output(cfg.out_dir, cfg.pdf.stem),
    }
    report["cuda_verdict"] = cuda_verdict(report)
    report["quality"] = quality_metrics(report["output"], cfg)

    (cfg.out_dir / "_debug_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report


def scan_log(text: str) -> dict[str, Any]:
    """Pull the handful of child log lines that carry diagnostic weight."""
    lowered = text.lower()
    keywords = {
        "cuda_mentioned": "cuda",
        "cpu_fallback_mentioned": "using cpu",
        "out_of_memory": "out of memory",
        "local_api_started": "started local mineru-api",
        "api_unhealthy": "exited before becoming healthy",
        "model_download": "downloading",
        "traceback": "traceback (most recent call last)",
    }
    signals = {name: (needle in lowered) for name, needle in keywords.items()}
    interesting = [
        line
        for line in text.splitlines()
        if any(
            token in line.lower()
            for token in ("device", "cuda", "vram", "batch", "backend", "error", "warning")
        )
    ]
    signals["notable_lines"] = interesting[:40]
    signals["tail"] = "\n".join(text.splitlines()[-25:])
    return signals


def cuda_verdict(report: dict[str, Any]) -> str:
    """Decide CUDA-or-not from observed occupancy first, logs only as corroboration.

    Strongest evidence: a process from THIS run's tree in nvidia-smi's compute-app table.
    Weaker but usable: a utilization / VRAM excursion over the pre-run baseline -- weaker
    because another process on the box could have caused it.
    """
    gpu = report.get("gpu", {})
    if not gpu.get("available"):
        return "UNKNOWN - nvidia-smi unavailable, cannot observe device occupancy"
    peak_util = gpu.get("peak_util_pct")
    if peak_util is None:
        return "UNKNOWN - no samples collected (run shorter than the sample interval)"
    mem_delta = (gpu.get("peak_mem_used_mb") or 0) - (gpu.get("baseline_mem_used_mb") or 0)
    ours = gpu.get("run_compute_apps") or []
    if ours:
        return (
            f"CUDA USED - {len(ours)} process(es) from this run held a CUDA context; "
            f"peak util {peak_util}%, VRAM +{mem_delta} MB over baseline"
        )
    if peak_util >= 20 or mem_delta >= 512:
        return (
            f"CUDA LIKELY - peak util {peak_util}%, VRAM +{mem_delta} MB over baseline, "
            "but no process of this run was seen in the compute-app table "
            "(short run, or sampling missed the window)"
        )
    return (
        f"NO GPU WORK OBSERVED - peak util {peak_util}%, VRAM +{mem_delta} MB; "
        "the parse likely ran on CPU"
    )


# ------------------------------------------------------------------------- commands


def pick_default_pdf() -> Path:
    """Smallest available PDF -- the cheapest thing to iterate on."""
    pdfs = sorted(DEFAULT_PDF_DIR.glob("*.pdf"), key=lambda p: p.stat().st_size)
    if not pdfs:
        raise SystemExit(f"No PDFs in {DEFAULT_PDF_DIR}; pass --pdf explicitly.")
    return pdfs[0]


def resolve_pdf(value: str | None) -> Path:
    if value is None:
        chosen = pick_default_pdf()
        print(f"[debug_mineru] --pdf omitted, using smallest available: {chosen.name}")
        return chosen
    path = Path(value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    if not path.is_file():
        raise SystemExit(f"PDF not found: {path}")
    return path


def make_out_dir(out_root: Path, tag: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return out_root / f"{stamp}-{tag}"


def cmd_probe(args: argparse.Namespace) -> int:
    exe_info = resolve_mineru_exe()
    payload = {
        "repo_root": str(REPO_ROOT),
        "interpreter": sys.executable,
        "mineru_exe": exe_info,
        "mineru_device_resolver": probe_mineru_device(),
        "torch": probe_torch(),
        "engine_deps": probe_engine_deps(),
        "nvidia_smi": nvidia_smi_available(),
        "env": {k: os.environ.get(k) for k in INTERESTING_ENV if os.environ.get(k)},
        "prod_argv_extra": list(PROD_EXTRA_ARGS),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.cli:
        if not exe_info["selected"]:
            print("\n[debug_mineru] mineru executable not found; skipping --help dump.")
            return 1
        print("\n--- mineru --help (installed surface) ---")
        print(probe_cli_surface(exe_info["selected"]))
        print(
            "NOTE: mineru's click command is ignore_unknown_options=True. Flags absent "
            "from the list above do NOT error -- they are forwarded to the spawned "
            "mineru-api child, which is also ignore-unknown, and silently do nothing."
        )
    return 0


def build_run_config(args: argparse.Namespace, out_dir: Path, pdf: Path) -> RunConfig:
    start_page = args.start
    end_page = args.end
    if args.pages is not None:
        start_page = 0 if start_page is None else start_page
        end_page = args.pages - 1
    if getattr(args, "emulate_prod", False):
        ignored = [
            name
            for name in ("backend", "effort", "method", "lang", "pages", "start", "end",
                         "formula", "table", "image_analysis")
            if getattr(args, name, None) is not None
        ]
        if ignored:
            print(
                f"[debug_mineru] NOTE: --emulate-prod replays prod argv verbatim; "
                f"ignoring {', '.join(ignored)}. --device and --timeout still apply "
                f"(they are env/harness-side, not argv)."
            )
    return RunConfig(
        pdf=pdf,
        out_dir=out_dir,
        backend=args.backend,
        effort=args.effort,
        method=args.method,
        lang=args.lang,
        formula=args.formula,
        table=args.table,
        image_analysis=args.image_analysis,
        start_page=start_page,
        end_page=end_page,
        device=args.device,
        timeout=args.timeout,
        emulate_prod=args.emulate_prod,
        extra=list(args.extra or []),
        spawn_mode=args.spawn_mode,
        sample_interval=args.sample_interval,
        echo=not args.quiet_child,
    )


def print_run_summary(report: dict[str, Any]) -> None:
    out = report["output"]
    print("\n=== SUMMARY ===")
    print(f"exit_code           : {report['exit_code']}  failure={report['failure']}")
    print(f"elapsed             : {report['elapsed_seconds']}s")
    print(f"cuda verdict        : {report['cuda_verdict']}")
    gpu = report["gpu"]
    for app in gpu.get("run_compute_apps") or []:
        print(f"  this run's CUDA ctx : {app}")
    if gpu.get("other_compute_apps_count"):
        print(
            f"  (ignored {gpu['other_compute_apps_count']} unrelated desktop compute apps; "
            "Windows/WDDM lists them all)"
        )
    print(f"files written       : {out['file_count']} ({out['total_bytes']} bytes)")
    print(f"parse dir(s) w/ md  : {out['parse_dirs_containing_md'] or '(none)'}")
    print(f"markdown files      : {out['markdown_files'] or '(none)'}")
    print(f"images              : {out['images']}")
    print(
        f"MineruClient fast path <stem>/<stem>.md hit: "
        f"{out['mineru_client_fast_path_hit']}  (False => prod relies on its rglob fallback)"
    )
    print(f"PaperLoader would pick: {out['paper_loader_would_pick']}")
    stats = out.get("markdown_stats")
    if stats:
        print(
            f"markdown            : {stats['bytes']} bytes, {stats['lines']} lines, "
            f"{stats['headings']} headings, {stats['image_refs']} image refs, "
            f"{stats['html_tables']} html tables, {stats['display_formulas']} display formulas"
        )
    quality = report.get("quality") or {}
    if "source_recall_pct" in quality:
        inj = quality.get("injection", {})
        print(
            f"text fidelity       : {quality['source_recall_pct']}% of the PDF's text recalled, "
            f"{quality['unbacked_ratio_pct']}% of markdown unbacked by it"
        )
        print(
            f"corruption          : {quality['novel_token_count']} tokens absent from the PDF"
            + (f" e.g. {quality['novel_tokens_sample'][:6]}" if quality["novel_tokens_sample"] else "")
        )
        print(
            f"injected charts     : {inj.get('details_blocks', 0)} details block(s) "
            f"{inj.get('summary_labels') or ''}, {inj.get('approx_number_markers', 0)} '~N' markers"
        )
    elif quality.get("error"):
        print(f"quality             : unavailable ({quality['error']})")
    print(f"report              : {report['config']['out_dir']}\\_debug_report.json")


def cmd_run(args: argparse.Namespace) -> int:
    pdf = resolve_pdf(args.pdf)
    tag = args.tag or (
        "prod" if args.emulate_prod else f"{args.backend or 'default'}-{args.effort or 'na'}"
    )
    out_dir = make_out_dir(Path(args.out_root), tag)
    cfg = build_run_config(args, out_dir, pdf)
    report = execute(cfg)
    print_run_summary(report)
    return 0 if report["exit_code"] == 0 else 1


def cmd_matrix(args: argparse.Namespace) -> int:
    pdfs = [resolve_pdf(value) for value in (args.pdf or [None])]
    names = args.only or list(CELLS)
    unknown = [n for n in names if n not in CELLS]
    if unknown:
        raise SystemExit(f"Unknown cell(s): {unknown}. Known: {list(CELLS)}")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = Path(args.out_root) / f"{stamp}-matrix"
    rows: list[dict[str, Any]] = []
    total = len(pdfs) * len(names)
    done = 0
    for pdf in pdfs:
        for name in names:
            cell = CELLS[name]
            done += 1
            print(f"\n########## [{done}/{total}] {pdf.stem} x {name} ##########")
            run_args = argparse.Namespace(**vars(args))
            run_args.backend = cell["backend"]
            run_args.effort = cell["effort"]
            run_args.method = cell["method"]
            run_args.emulate_prod = False
            cfg = build_run_config(run_args, root / pdf.stem / name, pdf)
            report = execute(cfg)
            print_run_summary(report)
            stats = report["output"].get("markdown_stats") or {}
            quality = report.get("quality") or {}
            inj = quality.get("injection") or {}
            rows.append(
                {
                    "paper": pdf.stem,
                    "cell": name,
                    "exit": report["exit_code"],
                    "seconds": report["elapsed_seconds"],
                    "peak_util": report["gpu"].get("peak_util_pct"),
                    "peak_vram_delta_mb": (report["gpu"].get("peak_mem_used_mb") or 0)
                    - (report["gpu"].get("baseline_mem_used_mb") or 0),
                    "parse_dir": ",".join(report["output"]["parse_dirs_containing_md"]) or "-",
                    "md_bytes": stats.get("bytes", 0),
                    "images": report["output"]["images"],
                    "tables": stats.get("html_tables", 0),
                    "formulas": stats.get("display_formulas", 0),
                    "recall_pct": quality.get("source_recall_pct"),
                    "unbacked_pct": quality.get("unbacked_ratio_pct"),
                    "novel_tokens": quality.get("novel_token_count"),
                    "details_blocks": inj.get("details_blocks"),
                    "approx_markers": inj.get("approx_number_markers"),
                }
            )
            # Written after every cell so a long matrix that dies partway keeps its results.
            (root / "_matrix.json").write_text(
                json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
            )

    print_matrix_table(rows)
    print(f"\nmatrix report: {root}\\_matrix.json")
    return 0


def print_matrix_table(rows: list[dict[str, Any]]) -> None:
    print("\n=== MATRIX ===")
    header = (
        f"{'paper':<12}{'cell':<20}{'exit':>5}{'secs':>7}{'util%':>6}{'vramMB':>8}"
        f"{'md B':>8}{'img':>5}{'tbl':>5}{'eq':>5}{'recall%':>9}{'unbkd%':>8}"
        f"{'novel':>7}{'charts':>7}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['paper']:<12}{row['cell']:<20}{str(row['exit']):>5}{row['seconds']:>7}"
            f"{str(row['peak_util']):>6}{row['peak_vram_delta_mb']:>8}{row['md_bytes']:>8}"
            f"{row['images']:>5}{row['tables']:>5}{row['formulas']:>5}"
            f"{str(row['recall_pct']):>9}{str(row['unbacked_pct']):>8}"
            f"{str(row['novel_tokens']):>7}{str(row['details_blocks']):>7}"
        )


def _bool(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="debug_mineru.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="environment + device resolution, no conversion")
    probe.add_argument("--cli", action="store_true", help="also dump `mineru --help`")
    probe.set_defaults(func=cmd_probe)

    def add_run_args(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
        sp.add_argument("--device", help="pins MINERU_DEVICE_MODE (cuda | cpu | mps | ...)")
        sp.add_argument("--method", choices=["auto", "txt", "ocr"])
        sp.add_argument("--lang")
        sp.add_argument("--start", type=int, help="first page, 0-based")
        sp.add_argument("--end", type=int, help="last page, 0-based")
        sp.add_argument("--pages", type=int, help="sugar for -s 0 -e N-1")
        sp.add_argument("--formula", type=_bool, help="true/false")
        sp.add_argument("--table", type=_bool, help="true/false")
        sp.add_argument("--image-analysis", dest="image_analysis", type=_bool)
        sp.add_argument("--timeout", type=int, default=3600, help="harness-side kill (seconds)")
        sp.add_argument(
            "--spawn-mode",
            choices=["headless", "inherit"],
            default="headless",
            help="headless replays production's CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP spawn",
        )
        sp.add_argument("--sample-interval", type=float, default=3.0)
        sp.add_argument("--quiet-child", action="store_true", help="do not echo the child log live")
        sp.add_argument("--extra", nargs=argparse.REMAINDER, help="raw args appended to the CLI")

    run = sub.add_parser("run", help="one instrumented conversion")
    run.add_argument("--pdf", help="PDF to convert (default: smallest in papers/arxivpdf)")
    add_run_args(run)
    run.add_argument("--backend", help="pipeline | vlm-engine | hybrid-engine | *-http-client")
    run.add_argument("--effort", choices=["medium", "high"], help="hybrid-* only")
    run.add_argument("--tag", help="label for the output folder")
    run.add_argument(
        "--emulate-prod",
        action="store_true",
        help=f"replay production argv verbatim: {' '.join(PROD_EXTRA_ARGS)}",
    )
    run.set_defaults(func=cmd_run)

    matrix = sub.add_parser(
        "matrix", help="compare backend/method/effort cells across one or more PDFs"
    )
    matrix.add_argument(
        "--pdf", nargs="+", help="one or more PDFs; every cell runs against each"
    )
    add_run_args(matrix)
    matrix.add_argument(
        "--only", nargs="+", choices=list(CELLS), help="subset of cells to run"
    )
    matrix.set_defaults(func=cmd_matrix, backend=None, effort=None, tag=None)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
