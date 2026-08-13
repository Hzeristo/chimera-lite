# friction-260811-01 — "registered" is an untested surface: three shipped components, none reachable

**Date:** 2026-08-11
**Status:** OPEN — escalated from incidents per `_shared/incident_protocol.md:22-24`
(same class ≥3 → promote to FRICTION). Needs a phase home; no more standalone hotfixes.
**Phase context:** surfaced across Phase L.B (L.B.2 externalization, L.B.6 gate). Not an
L.B deliverable — the defect class is about how components become *reachable*, which is
workflow/architecture, not research harness.

## The friction

A Chimera component becomes usable in two independent steps: it is **written** (a domain
function, an agent definition) and it is **registered** (an `@mcp.tool` decorator, a
parseable frontmatter block the agent loader accepts). Every test in this repo covers the
first step. Almost nothing covers the second.

The failure mode is uniform and silent: the artifact exists, its unit tests are green, a
sprint record says it is wired — and at runtime nothing can reach it. No error, no warning.
The component is simply absent from the registry, and the first symptom is an operator
hitting a dead step mid-workflow.

## Recurrence — the escalation trigger

| # | date | component | why it was unreachable |
|---|---|---|---|
| 1 | 2026-07-21 | L.B tools + pinned agent types | `.mcp.json` resolved to the main checkout while the work sat in an unmerged worktree; L.B.6 Paths 2 and 5 had to be driven by importing worktree code in-process (`docs/sprints/phase-L.B/L.B.6.md` Finding 1) |
| 2 | 2026-08-03 | `analyze_paper_data` | written, documented, unit-tested; the `@mcp.tool` registration was never added (`docs/incidents/2026-08-03-analyze-paper-data-unregistered.md`) |
| 3 | 2026-08-10 | `chimera-deep-extractor`, `chimera-paper-triager` | correct files, CRLF frontmatter fence defeated the agent parse; both L.B.2 judgment workers were dead from 2026-07-21 until found (`docs/incidents/2026-08-10-agent-frontmatter-crlf.md`) |

Three instances, one class. That is the protocol's threshold, and the reason it exists:
each fix was individually correct and the class kept arriving anyway.

## Why the previous fix did not hold

Instance 2 already diagnosed this correctly. Its record's Lesson reads: *"a test that proves
the primitive but not its reachability is advisory rigor: it reports safety it does not
deliver."* It then wrote a deliberately class-level regression —
`tests/test_mcp_tool_registration.py` — which parses both `server.py` files for
`@mcp.tool()` names and asserts every primitive each Phase-L skill orchestrates is
registered.

The boundary was drawn one surface too narrow. That test covers **MCP tools**. The class is
**registered things**. Verified 2026-08-11: no test in `tests/` reads, loads, or validates
`.claude/agents/*.md` at all — the agent-registration surface has zero coverage, which is
precisely the gap instance 3 fell through, three weeks after instance 2 was closed.

## What a sprint here has to deliver

Not another fix — the check that would have failed in July:

- **Agent registration coverage.** Every `.claude/agents/*.md` parses under the loader's
  rules (frontmatter fence, required keys), and every agent type named by a `chimera-*`
  skill exists. This is the direct analogue of `test_mcp_tool_registration.py` on the
  surface it does not cover.
- **One registry assertion, not two.** Tools and agents are the same class; a single
  skill→dependency check covering both is what stops instance 4 arriving through a third
  door (hooks? MCP resources? whatever registers next).
- **Reachability belongs in the seal, not the sprint record.** Instances 1 and 2 were both
  masked by a sprint record asserting a wiring that did not exist
  (`docs/sprints/phase-L.B/L.B.2.md:39`, and L.B.6's own five-path table). A phase gate must
  exercise components through the live client, not through in-process imports — L.B.6's
  Finding 1 documented that gap and it went on to hide instance 3.

## Not in scope

`.gitattributes` (commit `ebb1d69`) pins `.claude/**` markdown to LF so instance 3's specific
cause cannot recur via `core.autocrlf`. That is a patch on one door, deliberately not a
substitute for the check above.
