"""L.3: W2 bounded reference BFS — hard depth + paper caps, cycle/diamond dedup.

The phase-L red line is "bounded BFS — hard depth cap AND hard paper cap, no unbounded crawl."
These caps are enforced in `plan_expansion` (pure, over an injected `get_refs`) so the invariant
is assertable without a live reference parser.
"""

from __future__ import annotations

from w2_breadth import BfsBounds, plan_expansion


def _graph(edges: dict[str, list[str]]):
    return lambda pid: edges.get(pid, [])


def test_paper_cap_enforced() -> None:
    edges = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F", "G"]}
    order = plan_expansion(["A"], _graph(edges), BfsBounds(max_depth=5, max_papers=4))
    assert len(order) == 4  # hard paper cap, regardless of graph size


def test_depth_cap_enforced() -> None:
    edges = {"A": ["B"], "B": ["C"], "C": ["D"]}
    order = plan_expansion(["A"], _graph(edges), BfsBounds(max_depth=1, max_papers=99))
    ids = [pid for pid, _ in order]
    assert ids == ["A", "B"]  # depth 0 (A) + depth 1 (B); C at depth 2 is excluded
    assert all(d <= 1 for _, d in order)


def test_cycle_terminates_and_dedups() -> None:
    edges = {"A": ["B"], "B": ["A"]}  # cycle A<->B
    order = plan_expansion(["A"], _graph(edges), BfsBounds(max_depth=9, max_papers=99))
    assert sorted(pid for pid, _ in order) == ["A", "B"]  # each once, no infinite loop


def test_diamond_dedups_to_one() -> None:
    edges = {"A": ["B", "C"], "B": ["D"], "C": ["D"]}  # diamond A->{B,C}->D
    order = plan_expansion(["A"], _graph(edges), BfsBounds(max_depth=9, max_papers=99))
    ids = [pid for pid, _ in order]
    assert ids.count("D") == 1


def test_multiple_seeds_all_visited() -> None:
    order = plan_expansion(["A", "B", "C"], _graph({}), BfsBounds(max_depth=1, max_papers=99))
    assert sorted(pid for pid, _ in order) == ["A", "B", "C"]


def test_seeds_beyond_cap_are_truncated() -> None:
    order = plan_expansion(["A", "B", "C", "D"], _graph({}), BfsBounds(max_depth=0, max_papers=2))
    assert len(order) == 2  # the cap bites even on the seed set
