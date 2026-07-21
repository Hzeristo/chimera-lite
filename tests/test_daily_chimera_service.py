"""Phase L.B.2 externalized triage — ``daily_chimera_service.py``: fetch -> convert -> notify
ONLY (no filter stage, no LLM call, no Knowledge node). Heavy I/O (arXiv network, MinerU convert,
Telegram) is stubbed throughout; only the pipelining (queues, anti-hollow-success guard, report
rendering) is under test.

Async pipeline core logic is exercised via ``_run_pipelined_async`` directly (not the sync
``run_daily_pipeline`` wrapper, which calls ``asyncio.run`` and cannot run inside an
already-running pytest-asyncio event loop, ``asyncio_mode = "auto"``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import daily_chimera_service as dcs


class _StubPaperMiner:
    def __init__(self, tmp_path: Path) -> None:
        self.arxivpdf_dir = tmp_path / "arxivpdf"
        self.md_papers_raw_dir = tmp_path / "md_raw"
        self.md_papers_dir = tmp_path / "md_clean"
        self.arxiv_query = "cat:cs.CL"
        self.arxiv_max_results = 5


class _StubSettings:
    """Duck-typed ``ChimeraConfig`` stand-in — only the attributes the pipeline reads."""

    def __init__(self, tmp_path: Path) -> None:
        self.project_root = tmp_path
        self._pm = _StubPaperMiner(tmp_path)

    @property
    def paper_miner_or_default(self) -> _StubPaperMiner:
        return self._pm

    def ensure_directories(self) -> None:
        pass


def _make_fake_arxiv_fetcher(n_records: int):
    """A fake ``ArxivFetcher`` — fakes metadata fetch + queues N fake PDF paths."""

    class _FakeArxivFetcher:
        def __init__(self, *, settings):  # noqa: ANN001
            self.settings = settings

        def fetch_metadata(self) -> list[dict]:
            return [{"id": f"260{i}.0000{i}"} for i in range(n_records)]

        async def download_pdfs_to_queue(self, *, paper_records, target_dir, pdf_queue, semaphore):  # noqa: ANN001
            count = 0
            for i, _rec in enumerate(paper_records):
                await pdf_queue.put(Path(f"/fake/{i}.pdf"))
                count += 1
            await pdf_queue.put(None)
            return count

    return _FakeArxivFetcher


def _make_fake_convert_worker(*, ingested: int, failures: int):
    """A fake ``convert_queue_worker`` — drains ``pdf_queue`` to its sentinel, reports fixed
    ingested/failure counts, and puts the ``md_queue`` sentinel (so ``_drain_md_queue`` exits)."""

    async def _worker(pdf_queue, md_queue, normalized_raw, normalized_clean):  # noqa: ANN001
        while True:
            item = await pdf_queue.get()
            if item is None:
                break
        await md_queue.put(None)
        return ingested, failures

    return _worker


class _FakeTelegramNotifier:
    sent: list[str] = []

    def __init__(self, *, settings):  # noqa: ANN001
        pass

    def send_summary(self, html_message, reply_markup=None):  # noqa: ANN001
        _FakeTelegramNotifier.sent.append(html_message)


@pytest.fixture(autouse=True)
def _reset_fake_telegram():
    _FakeTelegramNotifier.sent.clear()
    yield
    _FakeTelegramNotifier.sent.clear()


async def test_pipeline_fetch_convert_notify_no_filter_stage(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(dcs, "ArxivFetcher", _make_fake_arxiv_fetcher(2))
    monkeypatch.setattr(dcs, "convert_queue_worker", _make_fake_convert_worker(ingested=2, failures=0))
    monkeypatch.setattr(dcs, "TelegramNotifier", _FakeTelegramNotifier)

    summary, counts = await dcs._run_pipelined_async(
        _StubSettings(tmp_path),
        arxiv_query=None,
        arxiv_max_results=None,
        skip_telegram=False,
        task_id=None,
        task_service=None,
    )

    assert counts == dcs.PipelineCounts(new_pdfs=2, ingested=2, convert_failures=0)
    assert "ingested=2" in summary
    assert "chimera-triage-paper" in summary
    assert len(_FakeTelegramNotifier.sent) == 1
    assert "chimera-triage-paper" in _FakeTelegramNotifier.sent[0]
    # L.B.2 dropped the verdict digest — no must-read/skim links in the notify message
    assert "Must Read" not in _FakeTelegramNotifier.sent[0]


async def test_pipeline_skip_telegram_never_sends(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(dcs, "ArxivFetcher", _make_fake_arxiv_fetcher(1))
    monkeypatch.setattr(dcs, "convert_queue_worker", _make_fake_convert_worker(ingested=1, failures=0))
    monkeypatch.setattr(dcs, "TelegramNotifier", _FakeTelegramNotifier)

    summary, counts = await dcs._run_pipelined_async(
        _StubSettings(tmp_path),
        arxiv_query=None,
        arxiv_max_results=None,
        skip_telegram=True,
        task_id=None,
        task_service=None,
    )
    assert counts.ingested == 1
    assert _FakeTelegramNotifier.sent == []


async def test_anti_hollow_success_guard_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Downloaded PDFs but converted NONE — must raise, not silently report success (I-5).
    # Preserved verbatim across the L.B.2 rewrite.
    monkeypatch.setattr(dcs, "ArxivFetcher", _make_fake_arxiv_fetcher(3))
    monkeypatch.setattr(dcs, "convert_queue_worker", _make_fake_convert_worker(ingested=0, failures=3))
    monkeypatch.setattr(dcs, "TelegramNotifier", _FakeTelegramNotifier)

    with pytest.raises(RuntimeError, match="converted 0 of 3"):
        await dcs._run_pipelined_async(
            _StubSettings(tmp_path),
            arxiv_query=None,
            arxiv_max_results=None,
            skip_telegram=True,
            task_id=None,
            task_service=None,
        )


async def test_pipeline_zero_new_pdfs_is_not_hollow_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # No new PDFs at all (everything already seen) is a legitimate no-op run, not a failure.
    monkeypatch.setattr(dcs, "ArxivFetcher", _make_fake_arxiv_fetcher(0))
    monkeypatch.setattr(dcs, "convert_queue_worker", _make_fake_convert_worker(ingested=0, failures=0))
    monkeypatch.setattr(dcs, "TelegramNotifier", _FakeTelegramNotifier)

    summary, counts = await dcs._run_pipelined_async(
        _StubSettings(tmp_path),
        arxiv_query=None,
        arxiv_max_results=None,
        skip_telegram=True,
        task_id=None,
        task_service=None,
    )
    assert counts == dcs.PipelineCounts(new_pdfs=0, ingested=0, convert_failures=0)


def test_render_daily_report_has_no_verdict_digest() -> None:
    report = dcs._render_daily_report(
        dcs.PipelineCounts(new_pdfs=3, ingested=2, convert_failures=1)
    )
    assert "Convert failures" in report
    assert "chimera-triage-paper" in report
    assert "Must Read" not in report and "Skim" not in report


def test_daily_chimera_service_makes_no_generate_structured_data_call() -> None:
    import inspect

    source = inspect.getsource(dcs)
    assert "generate_structured_data" not in source
    # The filter stage / its worker are gone — no import from the now-deleted module, and no
    # BATCH_FILTER pipeline stage left in DailyPipelineStage.
    assert "from batch_filter_workflow import" not in source
    assert not hasattr(dcs, "filter_queue_worker")
    assert not hasattr(dcs.DailyPipelineStage, "BATCH_FILTER")
