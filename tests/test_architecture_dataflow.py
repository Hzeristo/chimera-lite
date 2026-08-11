"""L.B.5 acceptance, redesigned from DETERMINISM to ACCURACY (2026-08-03).

The original acceptance was "re-running reproduces the artifact byte-for-byte." A hardcoded
literal reproduces perfectly forever while being false, and that is exactly what happened: the
flow section kept asserting `daily_paper_pipeline` / `ingest_paper` wrote scout cards to
`inbox/` long after L.B.2 moved that write behind `write_scout_card`. Reproducibility was
measured; correctness was assumed.

The acceptance is now: **every flow edge must map to a real write call site.** These tests
assert the derivation itself — each declared write surface's writer exists in source, each
rendered edge is backed by a reference chain that terminates at that writer, and the specific
falsehoods that rotted are absent. Determinism is retained as a secondary property, not as the
proof of correctness.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_GEN_PATH = _REPO_ROOT / "scripts" / "gen_architecture_diagram.py"
_ARTIFACT = _REPO_ROOT / "docs" / "ARCHITECTURE" / "ARCHITECTURE.md"


def _load_generator():
    spec = importlib.util.spec_from_file_location("gen_architecture_diagram", _GEN_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gen = _load_generator()


@pytest.fixture(scope="module")
def flows():
    tools_by_server = {name: gen.parse_tools(path) for name, path in gen.SERVERS.items()}
    graph = gen.build_reference_graph()
    return gen.derive_flows(tools_by_server, graph)


# --- accuracy: the anchors are real -------------------------------------------------------


@pytest.mark.parametrize("surface", gen.WRITE_SURFACES, ids=lambda s: s.surface_id)
def test_writer_symbol_exists_in_declared_module(surface) -> None:
    # verify_writer_symbol raises SystemExit if the writer is gone — a declared surface may
    # never describe code that does not exist.
    line = gen.verify_writer_symbol(surface)
    assert line > 0


# --- accuracy: every rendered edge maps to a real write call site --------------------------


def test_every_edge_has_a_chain_terminating_at_the_writer(flows) -> None:
    for surface, _line, edges in flows:
        for _server, tool, chain in edges:
            assert chain, f"{tool} -> {surface.surface_id} has an empty chain"
            assert chain[0] == tool, f"chain for {tool} does not start at the tool: {chain}"
            assert chain[-1] == surface.writer_symbol, (
                f"chain for {tool} -> {surface.surface_id} does not terminate at "
                f"{surface.writer_symbol!r}: {chain}"
            )


def test_every_mermaid_edge_is_a_derived_edge(flows) -> None:
    """Nothing may appear in the diagram that the derivation did not produce."""
    derived = {
        (tool, surface.surface_id) for surface, _line, edges in flows for _s, tool, _c in edges
    }
    text = _ARTIFACT.read_text(encoding="utf-8")
    mermaid = text.split("```mermaid", 1)[1].split("```", 1)[0]

    rendered: set[tuple[str, str]] = set()
    for line in mermaid.splitlines():
        if "-->" not in line:
            continue
        left, right = line.split("-->", 1)
        tool = left.strip().split("[", 1)[0].removeprefix("tool_")
        surface_id = right.strip().removesuffix("_dest")
        rendered.add((tool, surface_id))

    assert rendered == derived, (
        f"diagram edges diverge from derivation.\n"
        f"  only in diagram: {sorted(rendered - derived)}\n"
        f"  only in derivation: {sorted(derived - rendered)}"
    )


# --- the specific rot this replaces --------------------------------------------------------


def test_scout_writes_come_only_from_write_scout_card(flows) -> None:
    inbox = next(f for f in flows if f[0].surface_id == "inbox")
    reaching = {tool for _s, tool, _c in inbox[2]}
    assert reaching == {"write_scout_card"}, (
        f"inbox/ must be reachable ONLY via write_scout_card (L.B.2 sole scout writer); got {reaching}"
    )


@pytest.mark.parametrize("tool", ["daily_paper_pipeline", "ingest_paper"])
def test_fetch_convert_tools_no_longer_write_scout_cards(flows, tool: str) -> None:
    # The rotted literal claimed both wrote to inbox/<verdict>/ at chimera_tier=scout. L.B.2
    # made them fetch+convert primitives that write no node at all.
    inbox = next(f for f in flows if f[0].surface_id == "inbox")
    assert tool not in {t for _s, t, _c in inbox[2]}


def test_no_mcp_tool_to_subagent_edges() -> None:
    """MCP tools never spawn subagents — skills do. The old diagram drew phantom triager edges."""
    text = _ARTIFACT.read_text(encoding="utf-8")
    mermaid = text.split("```mermaid", 1)[1].split("```", 1)[0]
    for agent in ("chimera-paper-triager", "chimera-deep-extractor", "triager", "extractor"):
        assert agent not in mermaid, f"phantom subagent edge for {agent!r} is back in the diagram"


def test_orphaned_surface_is_reported_not_drawn(flows) -> None:
    legacy = next(f for f in flows if f[0].surface_id == "deep_reads_legacy")
    assert legacy[2] == [], "01_Deep_Reads/ has a live MCP writer now — the note is stale"
    assert "ORPHANED" in _ARTIFACT.read_text(encoding="utf-8")


# --- secondary: the artifact is current and reproducible ----------------------------------


def test_committed_artifact_matches_current_source(flows) -> None:
    tools_by_server = {name: gen.parse_tools(path) for name, path in gen.SERVERS.items()}
    agents = []
    for agent_path in sorted((_REPO_ROOT / ".claude" / "agents").glob("*.md")):
        parsed = gen.parse_agent_model(agent_path)
        if parsed is not None:
            agents.append(parsed)
    agents.sort(key=lambda pair: pair[0])

    rules = gen.parse_rules()
    graph = gen.build_reference_graph()
    expected = gen.render(
        tools_by_server,
        agents,
        flows,
        rules,
        gen.count_skill_layer(),
        gen.verify_rules(rules, tools_by_server, graph),
    )
    actual = _ARTIFACT.read_text(encoding="utf-8")
    assert actual.replace("\r\n", "\n") == expected, (
        "ARCHITECTURE.md is stale — regenerate with scripts/gen_architecture_diagram.py"
    )


# --- coverage honesty: a partial map must declare itself partial ---------------------------


def test_coverage_declares_its_fraction() -> None:
    text = _ARTIFACT.read_text(encoding="utf-8")
    verified = sum(1 for _n, status, _e in gen.COVERAGE_LAYERS if status == "VERIFIED")
    total = len(gen.COVERAGE_LAYERS)
    assert f"## Coverage — {verified} of {total} layers verified (PARTIAL)" in text
    # Coverage must precede content: a reader cannot meet an edge before its caveat.
    assert text.index("## Coverage") < text.index("## Write surfaces")


def test_every_coverage_layer_is_rendered() -> None:
    text = _ARTIFACT.read_text(encoding="utf-8")
    for name, status, _evidence in gen.COVERAGE_LAYERS:
        assert name in text, f"coverage layer {name!r} missing from the artifact"
        assert f"**{status}**" in text


def test_a_layer_claims_verified_only_with_a_verifier() -> None:
    """Layers 1 and 2 have verifiers; layer 3 must never claim VERIFIED without one."""
    verified = [name for name, status, _e in gen.COVERAGE_LAYERS if status == "VERIFIED"]
    assert verified == [
        "1. Dataflow / write surfaces",
        "2. Invariant conformance (R1-R6)",
    ], f"a layer claims VERIFIED without a verifier: {verified}"
    skill_layer = next(item for item in gen.COVERAGE_LAYERS if item[0].startswith("3."))
    assert skill_layer[1] != "VERIFIED"


# --- layer 2: rules PARSED from the human SSOT, verdicts from real verifiers ----------------


def test_rules_are_parsed_from_the_sot() -> None:
    rules = gen.parse_rules()
    assert rules, "no invariants parsed from ARCHITECTURE_RULES.md"
    sot = gen.RULES_DOC.read_text(encoding="utf-8")
    for rule_id, title, _tier in rules:
        assert f"## {rule_id} — {title}" in sot, (
            f"{rule_id} was not read back from the SOT — the map must point at it, not restate it"
        )


def test_generator_does_not_hardcode_rule_text() -> None:
    """The invariants are a human-authored SSOT; this script may only implement verifiers.

    A hardcoded rule title would be an unauthorized restatement (CLAUDE.md drift rule) AND would
    drift silently when the Architect edits the SOT.
    """
    source = _GEN_PATH.read_text(encoding="utf-8")
    for rule_id, title, _tier in gen.parse_rules():
        assert title not in source, (
            f"{rule_id}'s title is hardcoded in the generator — parse it from the SOT instead"
        )


@pytest.fixture(scope="module")
def verdicts():
    tools_by_server = {name: gen.parse_tools(path) for name, path in gen.SERVERS.items()}
    graph = gen.build_reference_graph()
    return gen.verify_rules(gen.parse_rules(), tools_by_server, graph)


def test_every_sot_rule_gets_a_verdict(verdicts) -> None:
    """Every SOT rule is adjudicated, and every verdict belongs to a real SOT rule.

    A rule may be split into sub-rules (R5 → R5a/R5b) when its halves sit at different
    maturities — a single merged verdict would let an enforced half carry an unenforced one to a
    clean bill of health. Coverage is therefore checked in BOTH directions against the base id:
    no SOT rule may go unadjudicated, and no verdict may name a rule the SOT does not declare.
    """
    sot_ids = {rid for rid, _t, _tier in gen.parse_rules()}
    covered = {gen._base_rule_id(v.rule_id) for v in verdicts}
    assert sot_ids <= covered, f"SOT rules with no verdict: {sorted(sot_ids - covered)}"
    assert covered <= sot_ids, f"Verdicts for rules absent from the SOT: {sorted(covered - sot_ids)}"


def test_split_rules_do_not_hide_an_unenforced_half(verdicts) -> None:
    """A sub-rule split must not be a laundering device.

    If a rule is adjudicated as sub-rules, each sub-verdict stands on its own in the report. This
    pins the specific case the split exists for: R5a (tag well-formedness, schema-enforced) must
    never be allowed to represent R5 as a whole while R5b (monotonicity) has no enforcement.
    """
    by_id = {v.rule_id: v for v in verdicts}
    if "R5a" not in by_id:
        pytest.skip("R5 is not currently split into sub-rules")
    assert "R5b" in by_id, "R5 was split but R5b is unadjudicated — the unenforced half vanished"
    assert "R5" not in by_id, "R5 has both a merged verdict and sub-verdicts; the merged one hides"


def test_verdict_statuses_are_from_the_allowed_set(verdicts) -> None:
    allowed = {"PASS", "VIOLATED", "PARTIAL", "UNCHECKABLE"}
    for verdict in verdicts:
        assert verdict.status in allowed, f"{verdict.rule_id} has status {verdict.status!r}"


def test_no_verdict_passes_without_stating_what_was_checked(verdicts) -> None:
    """A PASS with no derivation is exactly the advisory theater this replaces."""
    for verdict in verdicts:
        assert verdict.checked.strip(), f"{verdict.rule_id} states no check"
        assert verdict.evidence.strip(), f"{verdict.rule_id} states no finding"


def test_an_unknown_rule_is_uncheckable_not_a_pass() -> None:
    """A rule added to the SOT after these verifiers must NOT inherit a clean bill of health."""
    tools_by_server = {name: gen.parse_tools(path) for name, path in gen.SERVERS.items()}
    graph = gen.build_reference_graph()
    result = gen.verify_rules([("R99", "Invented Rule", "STRUCTURAL")], tools_by_server, graph)
    assert [v.status for v in result] == ["UNCHECKABLE"]


def test_r1_reports_live_llm_calls_as_violations() -> None:
    """Negative control for the sharpest rule: a reachable LLM call must read VIOLATED.

    Injected via a synthetic graph where a real tool reaches a real LLM call's enclosing function,
    so the verifier's verdict logic is exercised rather than trusted.
    """
    sites = gen.find_llm_call_sites()
    assert sites, "no LLM call sites found — the R1 scanner is not looking at anything"
    _module, _line, func, _cls, _ident = sites[0]
    tools_by_server = {"chimera-papers": ["ingest_paper"], "chimera-vault": []}
    rigged = {"ingest_paper": {func}, func: set()}
    verdict = gen._verify_r1(tools_by_server, rigged)
    assert verdict.status == "VIOLATED"
    assert "ingest_paper" in verdict.evidence


def test_rule_roster_matches_the_sot_exactly() -> None:
    """No rule may be dropped from or added to the roster the SOT declares."""
    sot_ids = {
        rid for rid, _title in gen.RULE_HEADING_RE.findall(gen.RULES_DOC.read_text(encoding="utf-8"))
    }
    parsed_ids = {rid for rid, _title, _tier in gen.parse_rules()}
    assert parsed_ids == sot_ids, (
        f"roster diverges from the SOT.\n  only parsed: {sorted(parsed_ids - sot_ids)}"
        f"\n  only in SOT: {sorted(sot_ids - parsed_ids)}"
    )


# --- layer 3: out of scope, and honest about it --------------------------------------------


def test_skill_layer_declared_out_of_scope_with_real_counts() -> None:
    skills, agents = gen.count_skill_layer()
    assert skills > 0 and agents > 0, "skill/agent counts should be non-zero in this repo"
    text = _ARTIFACT.read_text(encoding="utf-8")
    assert "## Layer 3 — skill / context layer: OUT OF SCOPE" in text
    assert f"{skills} skills and {agents} pinned subagents" in text


def test_no_skill_to_tool_edges_are_drawn() -> None:
    """Layer 3 is unmapped; the mermaid block must not imply otherwise."""
    text = _ARTIFACT.read_text(encoding="utf-8")
    mermaid = text.split("```mermaid", 1)[1].split("```", 1)[0]
    for skill_dir in sorted(_REPO_ROOT.joinpath(".claude", "skills").glob("*/SKILL.md")):
        assert skill_dir.parent.name not in mermaid, (
            f"skill {skill_dir.parent.name!r} appears in the diagram, but layer 3 is unmapped"
        )
