"""I-5 regression: convert_queue_worker COUNTS per-PDF convert failures (not swallow-as-skip).

Bug (incident 2026-07-01 I-5): every per-PDF convert exception was caught, logged, and
dropped; the worker returned only success_count. A run converting 0 of N PDFs then reported
ingested=0 errors=0 completed (hollow success). The worker now returns
(success_count, failure_count); the pipeline raises on a total convert failure.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import ports.ingest.mineru_pipeline as mp


async def test_convert_worker_counts_failures(monkeypatch, tmp_path: Path) -> None:
    def _boom(self, pdf_path):  # noqa: ANN001
        raise RuntimeError("simulated MinerU failure")

    monkeypatch.setattr(mp.MineruClient, "convert", _boom)

    pdf_q: asyncio.Queue = asyncio.Queue()
    md_q: asyncio.Queue = asyncio.Queue()
    for name in ("a.pdf", "b.pdf"):
        await pdf_q.put(tmp_path / name)
    await pdf_q.put(None)

    success, failure = await mp.convert_queue_worker(
        pdf_q, md_q, tmp_path / "raw", tmp_path / "clean"
    )
    assert (success, failure) == (0, 2)  # failures counted, not swallowed
    assert await md_q.get() is None  # only the sentinel — no clean_md queued
