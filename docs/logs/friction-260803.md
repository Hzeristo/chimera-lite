# friction-260803-01 — the invariant SOT declares R1-R6 but nothing checks them; the dataflow map derives edges without checking rules

**Date:** 2026-08-03
**Status:** OPEN
**Phase context:** Phase L.B (branch `phase-L`), raised while fixing the L.B.5 dataflow map
(`scripts/gen_architecture_diagram.py`). Not itself an L.B deliverable — an ARCHITECTURE-tier gap
surfaced by that work.

## What I wanted
`docs/ARCHITECTURE/ARCHITECTURE_RULES.md` is the single source of truth for the six invariants that
hold across all phases (R1 no LLM call inside any MCP server process, R2 no truth advance without a
human action, R3 staging-gate universality with `ascend_node` as sole writer to `Knowledge/`, R4
`chimera_tier` integrity, R5 provenance load-bearing, R6 human authorship of T/I/D bodies). I wanted
the generated dataflow map to be the place those invariants are *checked* against live code, so a
violation shows up as a failing artifact rather than as prose nobody re-reads.

## What I actually got
The rules are stated and nothing verifies them. Concretely, after this session's rewrite:

- The map now derives every write edge from a real reference chain (accuracy, not just determinism).
  That is a genuine check — but it checks *shape*, not *rules*. It answers "which tool reaches which
  write surface", never "does any invariant currently hold".
- R1 is the sharpest example. `mcp-servers/chimera-papers/optics_service.py:134` still calls
  `generate_structured_data_async` — an LLM call physically inside an MCP server package. It is dead
  code (no server path imports it), so R1 is not *actively* breached, but nothing in the repo
  asserts that. The distinction between "dead LLM call" and "live R1 violation" is currently held by
  a human remembering to grep.
- R3's sole-writer guarantee is genuinely structural (`staging_service.py:140-145` — `promote_node`
  raises on `chimera_tier == 'deep_read'`) and is test-covered. R4 is partly enforced
  (`create_staging_node` refuses to default a `knowledge` node's tier). R2, R5, R6 have no
  mechanical check at all.
- `ARCHITECTURE_RULES.md` itself marks each rule STRUCTURAL or ADVISORY, and its Appendix B
  acknowledges the ADVISORY ones as debt. So the gap is *declared* — but a declared gap that
  persists across phases starts to read as a shipped guarantee to anyone skimming the SOT.

## Root cause
Invariants live in prose; verification lives in code; nothing joins them. Each phase adds rules to
the SOT because writing a rule is cheap, and each phase defers the checker because writing a checker
is not. The dataflow map was the obvious join point — it already introspects both servers, the tool
inventory, the agent pins, and now the write surfaces — and it was built to describe topology only.

This is the same defect class that produced the two failures already fixed this session, at a
higher altitude: a test proved a primitive worked but never that it was reachable; a generator
proved it reproduced itself but never that it was true; and now a rule SOT states invariants but
never that they hold. Each time, the cheap property was measured and the load-bearing one assumed.

## Cost
Unquantified but compounding. The visible cost so far is that a seal reviewer must hand-grep each
invariant at every phase seal (I did exactly that for R1 this session), which is precisely the
biological-bandwidth drain Phase L exists to remove. The latent cost is worse: CLAUDE.md's north
star says advisory rigor is *negative* value, because a rule that only performs enforcement
launders opinion into knowledge. Six invariants with two-and-a-bit enforced is currently on the
wrong side of that line.

## Proposed direction (not yet scheduled)
Add an R1-R6 conformance section to the generated map — Part 2 of the L.B.5 fix, deliberately NOT
bundled into Part 1 so that unverified content is not shipped alongside the verified edges. Each
rule renders as PASS / VIOLATED / UNCHECKED with the derivation or an explicit "no mechanical check
exists". The value is as much in an honest `UNCHECKED` as in a `PASS`: it makes the enforcement
frontier visible in a generated artifact instead of buried in an appendix. Rules that can be
checked cheaply today: R1 (AST-scan both server packages for LLM client calls, separating live from
dead by import reachability — the machinery this session's reference graph already provides), R3
(the guard exists; assert it), R4 (assert every K writer supplies a tier).

## Lesson
A rule SOT is only as load-bearing as its cheapest available check. Writing the rule down is the
part that feels like rigor and costs nothing; wiring the check is the part that delivers it. When a
generated artifact already introspects the code the rules constrain, that artifact is where the
rules should be adjudicated — otherwise the SOT slowly becomes a wish list that reads like a
guarantee.
