"""W2 (Phase L.3) bounded reference-expansion BFS — the deterministic scaffold beneath the
breadth-mapping orchestration.

Pure over an injected ``get_refs`` callable so the caps are unit-testable without a live reference
parser (which is deferred — phase-L D5 "citation input: cheap-first"; the parser is a later
increment). The phase-L red line is enforced HERE, in code, not in an orchestration prompt: a
bounded BFS with a HARD depth cap AND a HARD paper cap, so "no unbounded crawl" is an assertable
invariant rather than a hope.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class BfsBounds:
    """Hard caps for W2 reference expansion (both axes are load-bearing red lines)."""

    max_depth: int
    max_papers: int


def plan_expansion(
    seeds: Iterable[str],
    get_refs: Callable[[str], Iterable[str]],
    bounds: BfsBounds,
) -> list[tuple[str, int]]:
    """Deterministic breadth-first expansion of a citation graph, bounded on BOTH axes.

    ``get_refs(paper_id)`` returns the ids a paper references — a fake dict-lookup in tests, the
    reference parser in production. Returns the visited papers as ``(id, depth)`` in BFS order,
    NEVER exceeding ``bounds.max_papers`` (hard paper cap) or ``bounds.max_depth`` (hard depth
    cap — seeds are depth 0, a node is expanded only while ``depth < max_depth``). A paper reached
    by more than one path (a diamond) or through a cycle is visited exactly once.
    """
    visited: dict[str, int] = {}
    order: list[tuple[str, int]] = []
    frontier: list[tuple[str, int]] = [(str(s), 0) for s in seeds]
    i = 0
    while i < len(frontier):
        pid, depth = frontier[i]
        i += 1
        if pid in visited:
            continue  # dedup — a cycle or diamond re-reaches an already-visited node
        if len(order) >= bounds.max_papers:
            break  # hard paper cap
        visited[pid] = depth
        order.append((pid, depth))
        if depth < bounds.max_depth:  # hard depth cap — do not expand at the frontier's edge
            for ref in get_refs(pid):
                ref = str(ref)
                if ref not in visited:
                    frontier.append((ref, depth + 1))
    return order
