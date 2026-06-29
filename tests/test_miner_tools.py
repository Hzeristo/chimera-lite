"""M.2a tests — task-id contract, the concurrency guard (TaskService.has_active_long_task),
and check_task_status flattening. Deterministic / offline (no real arXiv fetch)."""

from __future__ import annotations

import asyncio
import re

import pytest

import miner_tools
import task_service as ts
from core.schemas import ToolOutput
from task_service import TaskService


@pytest.fixture
def svc(tmp_path):
    s = TaskService(tmp_path / "tasks")
    ts.set_task_service(s)
    yield s
    ts._task_service_singleton = None


def test_task_id_is_8_hex(svc: TaskService) -> None:
    tid = svc.create_task("arxiv_fetch")
    assert re.fullmatch(r"[0-9a-f]{8}", tid), tid


def test_has_active_long_task_transitions(svc: TaskService) -> None:
    assert svc.has_active_long_task() is False
    tid = svc.create_task("arxiv_fetch")  # PENDING
    assert svc.has_active_long_task() is True
    asyncio.run(svc.emit_completed(tid, summary="done"))
    assert svc.has_active_long_task() is False


def test_non_long_task_does_not_block(svc: TaskService) -> None:
    svc.create_task("some_other_type")
    assert svc.has_active_long_task() is False


async def test_check_status_completed_flattens_tooloutput(svc: TaskService) -> None:
    tid = svc.create_task("arxiv_fetch")
    await svc.emit_completed(
        tid, summary=ToolOutput(text="3 papers fetched").model_dump_json()
    )
    assert await miner_tools.check_task_status(tid) == "3 papers fetched"


async def test_check_status_unknown_id(svc: TaskService) -> None:
    assert "Unknown task_id" in await miner_tools.check_task_status("deadbeef")


async def test_arxiv_miner_returns_task_id(svc: TaskService, monkeypatch) -> None:
    async def _fake_fetch(query, n, task_id=None, task_service=None):  # noqa: ANN001
        return "fake ok"

    monkeypatch.setattr(miner_tools, "fetch_and_process_arxiv", _fake_fetch)
    out = await miner_tools.arxiv_miner("memory", max_results=2)
    assert "[Task Started]" in out
    assert re.search(r"[0-9a-f]{8}", out), out
    await asyncio.sleep(0.05)  # let the fire-and-forget task drain
