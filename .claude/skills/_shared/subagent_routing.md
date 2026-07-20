# Subagent Routing (shared policy)

Single source for the generic delegation policy used by chimera-code-taste and
chimera-sprint-discipline. Each skill's SKILL.md keeps its own specific
delegate / do-not-delegate lists (and code-taste keeps the exit-code return
contract); this file holds only the common rules.

## Bind the model in the agent def, never at the call site (regime-(a))

Delegate to a PINNED agent type — the model lives in the agent definition's
frontmatter, so a spawn can never silently inherit an Opus session. Do NOT spawn a
generic `general-purpose` subagent with a `model:` param: a dropped param falls back to
the session model, which is exactly the dev-time overspend the model-routing audit
flagged (`docs/audits/model-routing-gaps.md`, gaps #3–#5). The pinned dev-time types:

- `chimera-repo-scout` (Haiku) — mechanical read-only recon: repo-wide pattern scans,
  migration-drift detection, test/lint output parsing, the scout-before-audit pass (R1).
- `chimera-verify-runner` (Haiku) — runs check_taste.ps1 / pytest / ruff / mypy and
  returns the verbatim tail + exit code (code-taste).
- `chimera-sprint-executor` (Sonnet) — applies ONE pre-approved sprint and returns the
  diff + exit codes (code-taste batch_execution).

The Phase-L judgment workers (`chimera-paper-classifier`, `chimera-verbatim-verifier`,
`chimera-breadth-reducer`) follow the same regime — Sonnet pinned in their agent defs.

## Never delegate the reasoning that IS the work

Never spawn a subagent for planning decisions, audit/review verdicts, rule application,
editing code outside batch_execution, or reading source for editing context. Those stay
in the main session.

## Returns are evidence, never verdicts

Subagents return compact STRUCTURED results (file:line of violations, or the contracted
verification tail + exit code), never verbatim file contents. A subagent's prose is
evidence for the main session, never the verdict.
