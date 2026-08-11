"""Generate the living dataflow map (docs/ARCHITECTURE/ARCHITECTURE.md).

Everything rendered here is DERIVED from source. Nothing about the flow is asserted by hand:

  - the ``@mcp.tool()`` inventory of both MCP servers (parsed from server.py source);
  - the pinned worker model of every ``.claude/agents/*.md`` subagent (YAML frontmatter);
  - for each declared WRITE SURFACE, the set of MCP tools that actually REACH it, computed by
    walking a reference graph over both server packages;
  - and the invariant roster (I-ids / titles / mutability tiers) parsed from the canonical
    ``INVARIANTS.md``.

The map is PARTIAL and renders its own coverage first (``COVERAGE_LAYERS``): layer 1 (dataflow)
is verified, layer 2 (I0.x/I1.x conformance) is listed but NOT checked, layer 3 (the skill/context
call graph) is absent. Stating the frontier is load-bearing — an artifact that looks complete
while covering a third is the same lie as a literal that reproduces while being false.

Why the reference graph rather than a hand-drawn flow (the L.B.5 defect, 2026-08-03): the
previous generator carried the four ingestion paths as a hardcoded literal. When L.B.2 moved
scout-card writing out of ``daily_paper_pipeline`` / ``ingest_paper`` and into the
``chimera-triage-paper`` skill's ``write_scout_card``, the literal kept asserting the old flow.
It reproduced byte-for-byte on every run while being false — determinism is not accuracy. A
write surface with no reachable tool is now reported as ORPHANED rather than silently drawn.

A declared write surface whose writer symbol no longer exists is a hard failure (SystemExit),
not a silently stale diagram.

Deterministic: no timestamps, no randomness; all collections sorted. Re-running against
unchanged source reproduces this file byte-for-byte.

Regenerate at every phase seal:
    .venv\\Scripts\\python.exe scripts/gen_architecture_diagram.py
"""

from __future__ import annotations

import ast
import re
import string
from collections import deque
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SERVERS = {
    "chimera-papers": REPO_ROOT / "mcp-servers" / "chimera-papers" / "server.py",
    "chimera-vault": REPO_ROOT / "mcp-servers" / "chimera-vault" / "server.py",
}
RULES_DOC = REPO_ROOT / "docs" / "ARCHITECTURE" / "INVARIANTS.md"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"

# What this map covers, and what it does NOT. Rendered into the artifact so a reader can never
# mistake a partial map for a whole one. `status` is the map's OWN coverage, not a code verdict.
COVERAGE_LAYERS = [
    (
        "1. Dataflow / write surfaces",
        "VERIFIED",
        (
            "Every write edge is derived from a reference chain in source and asserted by "
            "`tests/test_architecture_dataflow.py`; an unreached surface renders ORPHANED."
        ),
    ),
    (
        "2. Invariant conformance (canonical I-ids)",
        "VERIFIED",
        (
            "Each invariant in the canonical is adjudicated by a mechanical verifier below. An "
            "invariant with no possible mechanical check reports UNCHECKABLE with the reason, "
            "never a silent pass. Compliance detail: ENFORCEMENT_DEBT.md."
        ),
    ),
    (
        "3. Skill / context layer",
        "OUT OF SCOPE",
        (
            "Which skill invokes which tool and spawns which subagent is NOT mapped, and is not "
            "pursued: skill bodies name tools in red lines precisely to FORBID them, so any "
            "derivation short of real intent-parsing would mint edges asserting the opposite of "
            "the source's meaning. Declared here so the map's edge is legible, not as pending work."
        ),
    ),
]

# The canonical states invariants as `### I<n>.<m> — <title>` under `## Tier N — ...`
# mutability headings. The `declared` column is that MUTABILITY tier (the canonical's own claim
# about how changeable a rule is) — NOT an enforcement claim. The canonical deliberately carries no
# enforcement axis; compliance lives in ENFORCEMENT_DEBT.md and is never inferred here.
RULE_HEADING_RE = re.compile(r"^### (I\d+\.\d+) — (.+)$", re.MULTILINE)
MUTABILITY_HEADING_RE = re.compile(r"^## (Tier \d+)\b", re.MULTILINE)
SERVER_PKGS = [
    REPO_ROOT / "mcp-servers" / "chimera-papers",
    REPO_ROOT / "mcp-servers" / "chimera-vault",
]

TOOL_RE = re.compile(r"@mcp\.tool\(\)\s*\n\s*(?:async\s+)?def (\w+)\(")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(\S+)", re.MULTILINE)
MODEL_RE = re.compile(r"^model:\s*(\S+)", re.MULTILINE)


@dataclass(frozen=True)
class WriteSurface:
    """A terminal write destination, anchored to the ONE function that performs the write.

    ``writer_symbol`` must exist in ``module``; which tools reach it is derived, never declared.
    """

    surface_id: str
    destination: str
    module: str  # repo-relative
    writer_symbol: str
    note: str = ""


# The declared write surfaces. Only the ANCHOR (where the write happens) is stated here — it is
# verified against source on every run. Every edge into these surfaces is derived.
WRITE_SURFACES = [
    WriteSurface(
        surface_id="inbox",
        destination="inbox/<verdict>/  [chimera_tier=scout]",
        module="mcp-servers/chimera-papers/ports/vault/vault_note_writer.py",
        writer_symbol="write_knowledge_node",
        note="Scout tier. Never auto-promoted; ascension is a separate operator action.",
    ),
    WriteSurface(
        surface_id="staging",
        destination="docs/staging/  [chimera_tier=deep_read | synthesis]",
        module="mcp-servers/chimera-papers/staging_service.py",
        writer_symbol="create_staging_node",
        note="Review gate. Nothing here is live vault content until promoted or ascended.",
    ),
    WriteSurface(
        surface_id="committed",
        destination="<vault>/Knowledge|Thoughts|Insights|Decisions/",
        module="mcp-servers/chimera-papers/staging_service.py",
        writer_symbol="_promote_write",
        note=(
            "Shared write mechanics for promote_node + ascend_node. promote_node REFUSES "
            "chimera_tier=deep_read, which is what makes ascend_node the sole writer of "
            "Knowledge/ (structural, not conventional)."
        ),
    ),
    WriteSurface(
        surface_id="harness",
        destination="<vault>/Harness/",
        module="mcp-servers/chimera-papers/result_service.py",
        writer_symbol="write_result",
        note="W1 verdicts + W2 breadth maps. Review area, not the committed tier.",
    ),
    WriteSurface(
        surface_id="deep_reads_legacy",
        destination="<vault>/01_Deep_Reads/",
        module="mcp-servers/chimera-papers/ports/vault/vault_note_writer.py",
        writer_symbol="write_deep_read_node",
        note="Oligo-era surface; its only caller is the retired OpticsService.irradiate path.",
    ),
]


def parse_rules() -> list[tuple[str, str, str]]:
    """Read (invariant_id, title, mutability tier) from the Architect-authored canonical.

    The rules are the Architect's to write; this script may only ever implement VERIFIERS against
    them (CLAUDE.md: reference the rule SOT, never restate or override it). So this is a re-parse on
    every run, never a hardcoded copy — a copy would drift exactly like the flow literal did, and
    would additionally be an unauthorized restatement of a human-owned authority.

    The tier reported is each rule's OWN claim about itself. This map verifies NONE of it (coverage
    layer 2), and renders UNCHECKED rather than implying otherwise.
    """
    if not RULES_DOC.is_file():
        raise SystemExit(f"[dataflow] canonical missing: {RULES_DOC}")
    text = RULES_DOC.read_text(encoding="utf-8")
    matches = list(RULE_HEADING_RE.finditer(text))
    if not matches:
        raise SystemExit(
            "[dataflow] no `### I<n>.<m> — <title>` invariant headings found in the canonical"
        )

    rules: list[tuple[str, str, str]] = []
    for match in matches:
        # The mutability tier is the nearest `## Tier N` heading ABOVE this invariant.
        preceding = [m for m in MUTABILITY_HEADING_RE.finditer(text) if m.start() < match.start()]
        tier = preceding[-1].group(1) if preceding else "UNDECLARED"
        rules.append((match.group(1), match.group(2).strip(), tier))
    return rules


def count_skill_layer() -> tuple[int, int]:
    """Size the unmapped skill/context layer: (skills, agents). Counted, not enumerated —
    an honest scale for a layer this map does not yet derive."""
    skills = len([p for p in SKILLS_DIR.glob("*/SKILL.md")]) if SKILLS_DIR.is_dir() else 0
    agents = len(list(AGENTS_DIR.glob("*.md"))) if AGENTS_DIR.is_dir() else 0
    return skills, agents


def parse_tools(server_path: Path) -> list[str]:
    return sorted(TOOL_RE.findall(server_path.read_text(encoding="utf-8")))


def parse_agent_model(agent_path: Path) -> tuple[str, str] | None:
    match = FRONTMATTER_RE.match(agent_path.read_text(encoding="utf-8"))
    if not match:
        return None
    frontmatter = match.group(1)
    name_match = NAME_RE.search(frontmatter)
    model_match = MODEL_RE.search(frontmatter)
    if not name_match or not model_match:
        return None
    return name_match.group(1), model_match.group(1)


def _alias_map(tree: ast.Module) -> dict[str, str]:
    """``from x import y as _y`` → {"_y": "y"}. The servers lazy-import under aliases, so an
    unresolved alias would break every reachability chain that crosses a module boundary."""
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for entry in node.names:
                if entry.asname:
                    aliases[entry.asname] = entry.name.rsplit(".", maxsplit=1)[-1]
    return aliases


def build_reference_graph() -> dict[str, set[str]]:
    """Map every function name to every symbol its body references.

    References, not just call-expression targets: this codebase routes blocking work through
    ``asyncio.to_thread(some.writer, ...)``, where the writer is an ARGUMENT rather than the
    callee. A call-only graph would miss `create_staging_node` entirely.

    Names are merged across modules (a bare function name is one node). That is deliberate — it
    resolves both the thin-adapter chain, where a tool and its delegate share a name, and method
    calls on instances, without needing full type inference.
    """
    graph: dict[str, set[str]] = {}
    for pkg in SERVER_PKGS:
        for py_path in sorted(pkg.rglob("*.py")):
            try:
                tree = ast.parse(py_path.read_text(encoding="utf-8"))
            except SyntaxError:  # not our source to police; skip rather than fail the map
                continue
            aliases = _alias_map(tree)
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                bucket = graph.setdefault(node.name, set())
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        raw = child.id
                    elif isinstance(child, ast.Attribute):
                        raw = child.attr
                    else:
                        continue
                    bucket.add(raw)
                    if raw in aliases:
                        bucket.add(aliases[raw])
    return graph


def find_chain(start: str, target: str, graph: dict[str, set[str]]) -> list[str] | None:
    """Shortest reference chain start → target, or None when the target is unreachable."""
    if start == target:
        return [start]
    seen = {start}
    queue: deque[list[str]] = deque([[start]])
    while queue:
        chain = queue.popleft()
        for ref in sorted(graph.get(chain[-1], set())):
            if ref == target:
                return [*chain, ref]
            if ref not in seen and ref in graph:
                seen.add(ref)
                queue.append([*chain, ref])
    return None


def verify_writer_symbol(surface: WriteSurface) -> int:
    """Return the writer's def line, or fail loudly. A declared surface whose writer vanished
    means the map is describing code that no longer exists — the exact rot this replaces."""
    module_path = REPO_ROOT / surface.module
    if not module_path.is_file():
        raise SystemExit(f"[dataflow] write surface {surface.surface_id!r}: missing {surface.module}")
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == surface.writer_symbol:
            return node.lineno
    raise SystemExit(
        f"[dataflow] write surface {surface.surface_id!r}: writer {surface.writer_symbol!r} "
        f"not found in {surface.module}. The map cannot describe code that does not exist."
    )


def derive_flows(
    tools_by_server: dict[str, list[str]], graph: dict[str, set[str]]
) -> list[tuple[WriteSurface, int, list[tuple[str, str, list[str]]]]]:
    """For each write surface: its verified anchor line and every (server, tool, chain) reaching it."""
    all_tools = sorted(
        (server, tool) for server, tools in tools_by_server.items() for tool in tools
    )
    derived = []
    for surface in WRITE_SURFACES:
        line = verify_writer_symbol(surface)
        edges = []
        for server, tool in all_tools:
            chain = find_chain(tool, surface.writer_symbol, graph)
            if chain is not None:
                edges.append((server, tool, chain))
        derived.append((surface, line, edges))
    return derived


@dataclass(frozen=True)
class RuleVerdict:
    """One rule's mechanical adjudication. `status` is this map's finding, never the rule's claim."""

    rule_id: str  # a SOT rule id, or a sub-rule of one (R5 → R5a / R5b)
    status: str  # PASS | VIOLATED | PARTIAL | UNCHECKABLE
    # NOTE on vocabulary: an invariant with NO enforcement machinery reports VIOLATED, not a
    # softer "missing"/"unenforced". A status that reads as an empty slot gets skipped by a
    # reader, which is how an aspirational rule comes to be mistaken for a shipped guarantee.
    # UNCHECKABLE means "no mechanical check is possible", never "the check found nothing".
    checked: str  # exactly what was mechanically tested
    evidence: str


# Exact AST identifiers for an LLM invocation. Matched as whole Name/Attribute ids, never as
# substrings — `OpenAICompatibleClient` is a different identifier from `OpenAI` and must not match.
LLM_CALL_IDS = frozenset(
    {
        "generate_structured_data",
        "generate_structured_data_async",
        "generate_raw_text",
        "AsyncOpenAI",
        "OpenAI",
    }
)


def find_llm_call_sites() -> list[tuple[str, int, str, str, str]]:
    """Every LLM invocation physically inside a server package.

    Returns (module, line, function, enclosing_class, identifier). The class matters: a call inside
    ``__init__`` is only executed if the CLASS is instantiated, and instantiation references the
    class name, never ``__init__`` — so reachability must be anchored on both or a client
    constructor would be written off as dead without justification.
    """
    sites: list[tuple[str, int, str, str, str]] = []
    for pkg in SERVER_PKGS:
        for py_path in sorted(pkg.rglob("*.py")):
            try:
                tree = ast.parse(py_path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            rel = py_path.relative_to(REPO_ROOT).as_posix()
            owner: dict[int, str] = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for member in node.body:
                        if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            owner[id(member)] = node.name
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                enclosing_class = owner.get(id(node), "")
                for child in ast.walk(node):
                    ident = (
                        child.id
                        if isinstance(child, ast.Name)
                        else child.attr
                        if isinstance(child, ast.Attribute)
                        else None
                    )
                    if ident in LLM_CALL_IDS:
                        sites.append((rel, child.lineno, node.name, enclosing_class, ident))
    return sorted(set(sites))


def _tool_names(tools_by_server: dict[str, list[str]]) -> list[str]:
    return sorted({t for tools in tools_by_server.values() for t in tools})


def _base_rule_id(rule_id: str) -> str:
    """The SOT rule a verdict belongs to: `R5a` → `R5`, `R5` → `R5`. Strips a sub-rule suffix
    rather than slicing a fixed width, so a two-digit rule id (`R10a`) resolves correctly."""
    return rule_id.rstrip(string.ascii_lowercase)


def _server_python_files() -> list[Path]:
    """Every .py inside a server package — the R5b sweep must cover the service/port layers too,
    not just `server.py`, since a Gate-1 comparison could legitimately live one layer down."""
    roots = {path.parent for path in SERVERS.values()}
    return sorted({py for root in roots for py in root.rglob("*.py")})


def _function_source(module_rel: str, symbol: str) -> str:
    """Source text of one function, for guard checks. Empty when absent."""
    path = REPO_ROOT / module_rel
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
            return ast.get_source_segment(text, node) or ""
    return ""


def _verify_r1(tools_by_server: dict[str, list[str]], graph: dict[str, set[str]]) -> RuleVerdict:
    """R1 — no LLM call inside any MCP server process. Live reachability, not mere presence."""
    sites = find_llm_call_sites()
    tools = _tool_names(tools_by_server)
    live: list[str] = []
    dead: list[str] = []
    for module_rel, line, func, enclosing_class, ident in sites:
        # Anchor on the function AND its class: a constructor is reached via the class name.
        anchors = [func] + ([enclosing_class] if enclosing_class else [])
        reaching = sorted(
            {t for t in tools for anchor in anchors if find_chain(t, anchor, graph) is not None}
        )
        where = f"`{func}`" + (f" of `{enclosing_class}`" if enclosing_class else "")
        label = f"`{module_rel}:{line}` (`{ident}` in {where})"
        if reaching:
            live.append(f"{label} reachable from {', '.join(f'`{t}`' for t in reaching)}")
        else:
            dead.append(label)
    checked = (
        f"AST-scanned both server packages for {len(LLM_CALL_IDS)} LLM identifiers, then tested "
        "whether each call's enclosing function OR its enclosing class is reachable from any "
        "registered MCP tool via the reference graph."
    )
    if live:
        return RuleVerdict("I1.1", "VIOLATED", checked, "LIVE: " + "; ".join(live))
    if dead:
        return RuleVerdict(
            "I1.1",
            "PASS",
            checked,
            (
                f"No LLM call is reachable from any MCP tool. {len(dead)} call site(s) exist but are "
                f"unreachable (dead code): {'; '.join(dead)}."
            ),
        )
    return RuleVerdict("I1.1", "PASS", checked, "No LLM call identifiers present in either package.")


def _verify_r2(tools_by_server: dict[str, list[str]], graph: dict[str, set[str]]) -> RuleVerdict:
    """R2 — no truth advance without a human action: committed-tier writes only via MCP tools."""
    tools = _tool_names(tools_by_server)
    writers = sorted(t for t in tools if find_chain(t, "_promote_write", graph) is not None)
    background = [
        entry
        for entry in ("run_subprocess_task", "create_task", "_run_task", "daily_paper_pipeline")
        if find_chain(entry, "_promote_write", graph) is not None
    ]
    checked = (
        "Tested which entry points reach `_promote_write` (the only committed-tier write "
        "mechanic): registered MCP tools vs background/scheduled task entry points."
    )
    if background:
        return RuleVerdict(
            "I0.1", "VIOLATED", checked, f"Non-human entry reaches the committed tier: {background}"
        )
    return RuleVerdict(
        "I0.1",
        "PASS",
        checked,
        (
            f"`_promote_write` is reached only by human-invoked MCP tool(s): "
            f"{', '.join(f'`{w}`' for w in writers)}. No background/scheduled path reaches it."
        ),
    )


def _verify_r3() -> RuleVerdict:
    """R3 — ascend_node is the sole writer of Knowledge/, enforced by promote_node's refusal."""
    module = "mcp-servers/chimera-papers/staging_service.py"
    promote = _function_source(module, "promote_node")
    ascend = _function_source(module, "ascend_node")
    checked = (
        "AST-extracted `promote_node` / `ascend_node` and tested for the tier guards that make "
        "the sole-writer guarantee structural rather than conventional."
    )
    promote_guards = "deep_read" in promote and "raise" in promote
    ascend_guards = "deep_read" in ascend and "raise" in ascend
    if promote_guards and ascend_guards:
        return RuleVerdict(
            "I1.2",
            "PASS",
            checked,
            (
                f"`promote_node` refuses `chimera_tier=deep_read` and `ascend_node` requires it "
                f"(`{module}`), so `ascend_node` is structurally the sole `Knowledge/` writer."
            ),
        )
    missing = [
        name
        for name, ok in (("promote_node refusal", promote_guards), ("ascend_node gate", ascend_guards))
        if not ok
    ]
    return RuleVerdict("I1.2", "VIOLATED", checked, f"Missing guard(s): {', '.join(missing)}")


def _verify_r4() -> RuleVerdict:
    """R4 — tier integrity: a `knowledge` node is never silently defaulted to a tier."""
    module = "mcp-servers/chimera-papers/staging_service.py"
    creator = _function_source(module, "create_staging_node")
    checked = (
        "AST-extracted `create_staging_node` and tested that its tier default excludes "
        "`knowledge` (forcing its writer to declare scout vs deep_read)."
    )
    defaults_line = next(
        (ln for ln in creator.splitlines() if "tier is None" in ln and "node_type in" in ln), ""
    )
    if defaults_line and "knowledge" not in defaults_line:
        return RuleVerdict(
            "I1.5",
            "PASS",
            checked,
            (
                f"Tier defaulting is restricted to thought/insight/decision; `knowledge` is "
                f"excluded (`{module}`), so an untiered K node stays untiered rather than "
                "being silently mis-tiered."
            ),
        )
    return RuleVerdict(
        "I1.5",
        "VIOLATED" if defaults_line else "UNCHECKABLE",
        checked,
        (
            f"`knowledge` appears in the tier-default guard: {defaults_line.strip()!r}"
            if defaults_line
            else "Could not locate the tier-default guard; the check cannot be made honestly."
        ),
    )


def _verify_r5() -> list[RuleVerdict]:
    """R5 — provenance load-bearing. TWO independent halves, adjudicated separately.

    The canonical splits this rule (I0.2) because its halves sit at different
    maturities, and a single verdict over both would launder the unenforced half under the
    enforced one: a `[V]` can be perfectly well-formed and still be unearned. R5a is a property
    of source and is checkable; R5b is a graph property with no implementation to check.
    Reporting one merged `PASS` here is the exact cosmetic-rigor failure R5 exists to name.
    """
    return [_verify_r5a(), _verify_r5b()]


def _verify_r5a() -> RuleVerdict:
    """R5a — tag well-formedness: is the verdict tag structurally constrained to V/P/U?"""
    module = "mcp-servers/chimera-vault/server.py"
    source = _function_source(module, "write_result")
    checked = (
        "AST-extracted `write_result` and tested whether its `verdict` parameter is constrained "
        'to `Literal["V","P","U"]` (structural) or accepts an arbitrary string (advisory).'
    )
    verdict_line = next((ln for ln in source.splitlines() if ln.strip().startswith("verdict")), "")
    if "Literal" in verdict_line:
        return RuleVerdict(
            "I0.2a",
            "PASS",
            checked,
            (
                f"`verdict` is schema-constrained: {verdict_line.strip()!r}. A malformed tag is "
                "rejected by pydantic at the JSON-RPC boundary before the handler body runs. "
                "This covers WELL-FORMEDNESS ONLY — see R5b for whether the tag is earned."
            ),
        )
    return RuleVerdict(
        "I0.2a",
        "VIOLATED",
        checked,
        (
            f"`verdict` is an unconstrained string ({verdict_line.strip()!r} in `{module}`), so a "
            "`[V]` carries no structural guarantee. This CONFIRMS the SOT's own ADVISORY "
            "admission — the rule is aspirational until Phase K lands schema-reject."
        ),
    )


# The support-bearing edge set monotonicity quantifies over. Canonical: `FORMAL_MODEL.md`
# (`support(v)`) + `INVARIANTS.md` I2.2. `depends_on` was RETIRED by canonical r2 — checking it
# would make this verifier return VIOLATED even after the gate is correctly built (debt R5b-v).
# `informed_by` is deliberately excluded: it records tool context, not a dependency.
SUPPORT_BEARING_EDGES = ("evidence_base", "synthesizes", "derives_from")


def _verify_r5b() -> RuleVerdict:
    """R5b — monotonicity propagation: is Gate 1 (`status(n) ≤ min over support(v)`) enforced?"""
    checked = (
        "Traced every use of the support-bearing edges "
        f"({', '.join('`' + e + '`' for e in SUPPORT_BEARING_EDGES)}) across both server packages "
        "and tested whether ANY code path reads a support node's status and constrains the "
        "artifact's verdict against it (Gate 1 monotonicity), rather than merely recording edges."
    )
    readers: list[str] = []
    for module in _server_python_files():
        try:
            source = module.read_text(encoding="utf-8")
        except OSError:
            continue
        for lineno, line in enumerate(source.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") or not any(e in stripped for e in SUPPORT_BEARING_EDGES):
                continue
            # A gate must COMPARE, not just store. Assignment/record/param-declaration is not a gate.
            if any(op in stripped for op in ("<=", ">=", " < ", " > ", "min(", "max(")):
                readers.append(f"{module.relative_to(REPO_ROOT).as_posix()}:{lineno}")
    if readers:
        return RuleVerdict(
            "I0.2b",
            "PASS",
            checked,
            f"A monotonicity comparison over a support-bearing edge exists at: {', '.join(readers)}.",
        )
    return RuleVerdict(
        "I0.2b",
        "VIOLATED",
        checked,
        (
            "No enforcement exists. Support edges are WRITTEN into node frontmatter "
            "(`chimera-vault/server.py` `write_result`) and never read back for a comparison — no "
            "code path computes `min` over support-node statuses or refuses a verdict that exceeds "
            "one. A well-formed `[V]` resting on a `[U]` dependency is accepted today. The "
            "machinery is ABSENT rather than broken (the SOT declares R5b ADVISORY and homes it at "
            "Phase K.1, Queued) — but absence is reported as VIOLATED, not as a softer 'missing', "
            "because the guarantee the rule states does not hold in the code and a status that "
            "reads as an empty slot gets skipped. R5a passing says NOTHING about this half."
        ),
    )


def _verify_r6(tools_by_server: dict[str, list[str]], graph: dict[str, set[str]]) -> RuleVerdict:
    """R6 — human authorship of T/I/D bodies. Only partially mechanisable."""
    checked = (
        "Tested whether any T/I/D body content can be machine-generated inside the servers: "
        "(a) no LLM call is tool-reachable (see R1), and (b) `create_staging_node`'s `body` is a "
        "caller-supplied parameter rather than generated in-module."
    )
    creator = _function_source("mcp-servers/chimera-papers/staging_service.py", "create_staging_node")
    body_is_param = "body: str" in creator or "body," in creator.split(")")[0]
    r1 = _verify_r1(tools_by_server, graph)
    if body_is_param and r1.status == "PASS":
        return RuleVerdict(
            "I0.5",
            "PARTIAL",
            checked,
            (
                "Both mechanisable halves hold: `body` is a caller-supplied parameter and no "
                "tool-reachable LLM call exists, so no server path can synthesise a T/I/D body. "
                "NOT fully verifiable: nothing prevents a FUTURE path from populating a body, and "
                "whether the human actually authored the text is outside code's reach. The SOT "
                "declares this CONVENTION; that remains accurate."
            ),
        )
    return RuleVerdict(
        "I0.5",
        "VIOLATED" if not body_is_param else "PARTIAL",
        checked,
        "A server path can supply T/I/D body content without a human action.",
    )


def verify_rules(
    rules: list[tuple[str, str, str]],
    tools_by_server: dict[str, list[str]],
    graph: dict[str, set[str]],
) -> list[RuleVerdict]:
    """Adjudicate every rule the SOT declares. An unknown rule id yields UNCHECKABLE, never a pass.

    The SOT is human-authored and owns the rules; this function only implements verifiers against
    it. A rule appearing in the SOT with no verifier here is reported as such, so adding a rule
    upstream cannot silently inherit a clean bill of health.
    """
    verdicts: list[RuleVerdict] = []
    for rule_id, _title, _tier in rules:
        # Legacy R-ids map onto canonical I-ids (ARCHITECTURE_RULES.md pointer table):
        # R1→I1.1 · R2→I0.1 · R3→I1.2 · R4→I1.5 · R5→I0.2 (split a/b) · R6→I0.5.
        if rule_id == "I1.1":
            verdicts.append(_verify_r1(tools_by_server, graph))
        elif rule_id == "I0.1":
            verdicts.append(_verify_r2(tools_by_server, graph))
        elif rule_id == "I1.2":
            verdicts.append(_verify_r3())
        elif rule_id == "I1.5":
            verdicts.append(_verify_r4())
        elif rule_id == "I0.2":
            # I0.2 is adjudicated as two sub-rules (well-formedness / monotonicity).
            verdicts.extend(_verify_r5())
        elif rule_id == "I0.5":
            verdicts.append(_verify_r6(tools_by_server, graph))
        else:
            verdicts.append(
                RuleVerdict(
                    rule_id,
                    "UNCHECKABLE",
                    "No verifier implemented for this rule id.",
                    "Declared in the SOT after the verifiers were written; needs one here.",
                )
            )
    return verdicts


def _md_cell(text: str) -> str:
    """Escape a value for a markdown table cell — destinations contain `|` (alternation)."""
    return text.replace("|", "\\|")


def _mermaid_label(text: str) -> str:
    """Mermaid labels choke on `|`, `<`, `>` and nested brackets; keep it legible but inert."""
    return (
        text.replace('"', "'")
        .replace("|", " / ")
        .replace("<", "")
        .replace(">", "")
        .replace("[", "(")
        .replace("]", ")")
    )


def render(
    tools_by_server: dict[str, list[str]],
    agents: list[tuple[str, str]],
    flows: list[tuple[WriteSurface, int, list[tuple[str, str, list[str]]]]],
    rules: list[tuple[str, str, str]],
    skill_counts: tuple[int, int],
    verdicts: list[RuleVerdict],
) -> str:
    lines: list[str] = []
    verified = sum(1 for _name, status, _ev in COVERAGE_LAYERS if status == "VERIFIED")
    total = len(COVERAGE_LAYERS)
    edge_count = sum(len(edges) for _s, _l, edges in flows)
    skills, agent_count = skill_counts

    lines.append("# Chimera Lite — Architecture Map (generated)")
    lines.append("")
    lines.append(
        "Generated by `scripts/gen_architecture_diagram.py`. Do not hand-edit — regenerate "
        "at every phase seal. Describes actual code as it stands; never aspiration."
    )
    lines.append("")
    lines.append(f"## Coverage — {verified} of {total} layers verified (PARTIAL)")
    lines.append("")
    lines.append(
        "**This map is deliberately incomplete, and states so.** A partial map presented as whole "
        "is the failure mode this artifact already suffered once: its flow section was a hardcoded "
        "literal that reproduced byte-for-byte while asserting write paths L.B.2 had removed "
        "(`docs/sprints/phase-L.B/L.B.5.md`, amendment 2026-08-03). Coverage is therefore rendered "
        "before any content."
    )
    lines.append("")
    lines.append("| layer | status | what that means |")
    lines.append("|---|---|---|")
    for name, status, evidence in COVERAGE_LAYERS:
        lines.append(f"| {name} | **{status}** | {_md_cell(evidence)} |")
    lines.append("")
    lines.append(
        f"Derived this run: **{len(flows)} write surfaces**, **{edge_count} write edges**, "
        f"**{len(tools_by_server['chimera-papers']) + len(tools_by_server['chimera-vault'])} MCP "
        f"tools**, **{len(agents)} pinned subagents**. Not derived: "
        f"**{len(rules)} invariants** (layer 2) and the **{skills} skills / {agent_count} agents** "
        f"call graph (layer 3)."
    )
    lines.append("")

    lines.append("## MCP tool inventory")
    lines.append("")
    for server_name in sorted(tools_by_server):
        lines.append(f"### {server_name}")
        lines.append("")
        for tool_name in tools_by_server[server_name]:
            lines.append(f"- `{tool_name}`")
        lines.append("")

    lines.append("## Subagent -> model pins")
    lines.append("")
    lines.append("| agent | model |")
    lines.append("|---|---|")
    for agent_name, model in agents:
        lines.append(f"| {agent_name} | {model} |")
    lines.append("")

    lines.append("## Write surfaces (derived)")
    lines.append("")
    lines.append(
        "Judgment is externalized out of the MCP layer entirely (Phase L.B): the MCP servers "
        "make NO LLM call. Subagents are spawned by Claude Code SKILLS, never by an MCP tool — "
        "so no tool-to-subagent edge is drawn here, because none exists in code."
    )
    lines.append("")
    lines.append("| destination | writer | anchor | reached by |")
    lines.append("|---|---|---|---|")
    for surface, line, edges in flows:
        anchor = f"`{surface.module}:{line}`"
        writer = f"`{surface.writer_symbol}`"
        reached = (
            ", ".join(f"`{tool}`" for _, tool, _ in edges)
            if edges
            else "**ORPHANED — no MCP tool reaches this**"
        )
        lines.append(f"| `{_md_cell(surface.destination)}` | {writer} | {anchor} | {reached} |")
    lines.append("")

    lines.append("### Derived reference chains")
    lines.append("")
    lines.append("Each edge above, with the chain that proves it:")
    lines.append("")
    for surface, _line, edges in flows:
        for _server, tool, chain in edges:
            lines.append(
                f"- `{tool}` -> `{surface.destination}` via `{' -> '.join(chain)}`"
            )
    lines.append("")

    for surface, _line, _edges in flows:
        if surface.note:
            lines.append(f"- `{surface.destination}` — {surface.note}")
    lines.append("")

    lines.append("```mermaid")
    lines.append("flowchart TD")
    for surface, _line, edges in flows:
        dest_node = f"{surface.surface_id}_dest"
        lines.append(f'    {dest_node}["{_mermaid_label(surface.destination)}"]')
        for _server, tool, _chain in edges:
            lines.append(f'    tool_{tool}["{tool}"] --> {dest_node}')
    lines.append("```")
    lines.append("")

    status_counts: dict[str, int] = {}
    for verdict in verdicts:
        status_counts[verdict.status] = status_counts.get(verdict.status, 0) + 1
    tally = ", ".join(f"{count} {status}" for status, count in sorted(status_counts.items()))

    lines.append(f"## Layer 2 — invariant conformance ({tally})")
    lines.append("")
    lines.append(
        "The invariants are a HUMAN-AUTHORED SSOT: `docs/ARCHITECTURE/INVARIANTS.md` owns "
        "them, and this generator may only ever implement VERIFIERS against it — never author, "
        "restate, or override a rule (CLAUDE.md drift rule). Rule ids, titles, and declared tiers "
        "are re-parsed from that file on every run, so those columns are a pointer that cannot "
        "drift, not a copy that can."
    )
    lines.append("")
    lines.append(
        "**`declared` is the rule's claim about itself; `verdict` is this map's mechanical "
        "finding.** Where the two disagree, the verdict is the one backed by a check. A rule with "
        "no possible mechanical check reports `UNCHECKABLE` with the reason — never a silent pass."
    )
    lines.append("")
    lines.append("| rule | invariant | declared | verdict |")
    lines.append("|---|---|---|---|")
    # A SOT rule may be adjudicated as several sub-rules (R5 → R5a/R5b). Each gets its OWN row:
    # collapsing them would let an enforced half carry an unenforced one to a clean verdict.
    by_base: dict[str, list[RuleVerdict]] = {}
    for verdict in verdicts:
        by_base.setdefault(_base_rule_id(verdict.rule_id), []).append(verdict)
    for rule_id, title, tier in rules:
        found = by_base.get(rule_id)
        if not found:
            lines.append(f"| {rule_id} | {_md_cell(title)} | {_md_cell(tier)} | **UNCHECKABLE** |")
            continue
        for verdict in found:
            lines.append(
                f"| {verdict.rule_id} | {_md_cell(title)} | {_md_cell(tier)} | "
                f"**{verdict.status}** |"
            )
    lines.append("")
    lines.append("### Verifier findings")
    lines.append("")
    for verdict in verdicts:
        lines.append(f"**{verdict.rule_id} — {verdict.status}**")
        lines.append("")
        lines.append(f"- *Checked:* {verdict.checked}")
        lines.append(f"- *Finding:* {verdict.evidence}")
        lines.append("")

    lines.append("### Where the verifiers stop (the border)")
    lines.append("")
    lines.append(
        "**A verifier cannot cover every violation of a stated invariant, and this one does not "
        "claim to.** The rules are human-authored intent; a static checker reaches only the part "
        "of that intent expressible as a property of source. The border is stated here so a `PASS` "
        "is read as \"this check held\", never as \"this rule is safe\":"
    )
    lines.append("")
    lines.append(
        "- **Reachability is name-merged, not type-inferred.** The graph keys on bare "
        "function/class names, so a name collision across modules could invent an edge or mask "
        "one. It resolves aliases and argument-passed callables; it does not resolve `getattr`, "
        "dynamic import, or dispatch through a variable."
    )
    lines.append(
        "- **\"Dead code\" means statically unreachable.** A site reached only at runtime — a "
        "plugin hook, a string-named import — would be reported dead while being live."
    )
    lines.append(
        "- **Source is not behaviour.** These verifiers read code, never a running system. They "
        "cannot observe what an operator or a subagent actually did."
    )
    lines.append(
        "- **Intent is out of reach entirely.** R6 asks whether a human authored a body; code can "
        "show that no server path *synthesised* one, and nothing more. That gap is why R6 reports "
        "PARTIAL rather than PASS, and why the SOT's CONVENTION tier stays accurate."
    )
    lines.append("")
    lines.append(
        "Everything past that line is the Architect's judgment, not the map's. Reporting the limit "
        "IS the deliverable: a checker that overstated its reach would be the advisory theater "
        "these rules exist to prevent."
    )
    lines.append("")

    lines.append("## Layer 3 — skill / context layer: OUT OF SCOPE")
    lines.append("")
    lines.append(
        f"{skills} skills and {agent_count} pinned subagents exist, and the edges between them and "
        "the tools above are NOT mapped. That layer would show how judgment reaches a write "
        "surface — skill invokes tool, skill spawns subagent, subagent returns a payload a tool "
        "then writes."
    )
    lines.append("")
    lines.append(
        "It is out of scope by decision, not pending work. Skill bodies mention tool names inside "
        "red lines specifically to FORBID them (`chimera-deep-extract` names `ascend_node` only to "
        "disclaim it), so any derivation short of real intent-parsing would mint edges asserting "
        "the opposite of the source's meaning — the same class of falsehood as the literal this "
        "generator replaced, reached by a different route. Recorded so the map's edge is legible."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    tools_by_server = {name: parse_tools(path) for name, path in SERVERS.items()}
    agents_dir = REPO_ROOT / ".claude" / "agents"
    agents: list[tuple[str, str]] = []
    for agent_path in sorted(agents_dir.glob("*.md")):
        parsed = parse_agent_model(agent_path)
        if parsed is not None:
            agents.append(parsed)
    agents.sort(key=lambda pair: pair[0])

    graph = build_reference_graph()
    flows = derive_flows(tools_by_server, graph)
    rules = parse_rules()
    skill_counts = count_skill_layer()
    verdicts = verify_rules(rules, tools_by_server, graph)

    out_path = REPO_ROOT / "docs" / "ARCHITECTURE" / "ARCHITECTURE.md"
    out_path.write_text(
        render(tools_by_server, agents, flows, rules, skill_counts, verdicts),
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
