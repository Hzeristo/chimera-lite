# Sprint C.2 — Registration reachability

**Phase:** L.C (Colligo) · **Risk:** 🟢 LOW · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Audit:** `docs/audits/L.C.0.md` Q9
**Friction:** `friction-260811-01` (OPEN → this sprint is its phase home)
**Executed by:** `chimera-sprint-executor` (pinned Sonnet), two rounds. Reviewed + verified
independently by the Opus main session; commit owned by main.
**Outcome:** ✅ Pass — **after the first round failed its own negative control.**

## What was done

`tests/test_mcp_tool_registration.py` → `tests/test_registration.py` (`git mv`), extended from
one registration surface to both:

| Test | Asserts |
|---|---|
| `test_skill_required_tools_are_registered` | (existing) skill-named MCP tools are `@mcp.tool`-registered |
| `test_analyze_paper_data_is_registered` / `..._delegates_to_miner_tools` | (existing, **verbatim**) instance-2 regressions |
| `test_every_skill_is_covered_by_the_map` | every `.claude/skills/*/SKILL.md` directory has a `_SKILL_REQUIRED_TOOLS` entry (`[]` valid) |
| `test_every_agent_definition_parses` | per `.claude/agents/*.md`: no CRLF · fence at byte 0 · YAML parses · `name`/`description`/`tools` present · `name` == filename stem |
| `test_every_skill_definition_has_no_crlf` | same byte-level guard over `.claude/skills/*/SKILL.md` |
| `test_agents_named_by_skills_exist` | every `chimera-*` agent reference in a SKILL.md body resolves to a real agent file |

Map grown 4 → **17** skills (all of them), read per-file, never regex-inferred.

## The round-1 defect — the sprint's own target class

Round 1 returned green: 22 passed, full suite 226, ruff clean, exit 0 everywhere. It did not
pass acceptance.

The main session ran the sprint's required negative control — injected CRLF into
`.claude/agents/chimera-repo-scout.md` (`2d 2d 2d 0d 0a`) — and the suite returned **22 passed,
exit 0**. The check did not catch instance 3's actual failure mode, while its own comment claimed
to guard "the CRLF/BOM class."

Cause: `raw.startswith(b"---")` is **True** for a file beginning `---\r\n`. The byte-0 fence
check guards a *prepended* byte (BOM), not a CRLF fence. `_parse_flat_frontmatter` compounded it —
the stray `\r` lands inside a `json.dumps`-quoted value and parses cleanly.

This is instance **4** of `friction-260811-01`, and it arrived inside the sprint built to stop the
class. Caught only by running the negative control, never by the suite being green.

## Round-2 fix

- `_assert_no_crlf(path, raw)` — one shared byte-level assertion, named after the incident, and
  explicit that `.gitattributes` is an unenforced pin rather than the check.
- Called from the agent test and from a skill-file sibling. **One mechanism, two surfaces** —
  the friction's "one registry assertion, not two."
- The fence-check comment corrected to claim only what it does (a prepended byte / BOM), with the
  CRLF guarantee attributed to `_assert_no_crlf`.

Skill-file coverage is a faithful reading of the friction ("tools and agents are the same class"),
not scope creep: same one-line assertion, same helper, no second mechanism.

## Verification (main session, independent — not taken on the executor's report)

| Control | Result | Exit |
|---|---|---|
| CRLF into `.claude/agents/chimera-verbatim-verifier.md` | `FAILED ...::test_every_agent_definition_parses`, names the file | **1** |
| CRLF into `.claude/skills/chimera-w1-verify/SKILL.md` | `FAILED ...::test_every_skill_definition_has_no_crlf` | **1** |
| both restored (`git checkout --`) | `23 passed` | **0** |
| full suite | `227 passed in 7.03s` | **0** |
| `uvx ruff check tests/test_registration.py` | `All checks passed!` | **0** |

Suite 213 → **227**. Working tree after the controls carried no residual diff on either probed
file.

## Judgment calls accepted on review

1. **`read_vault_file` added to `chimera-w1-verify`'s tool list** — correct; `SKILL.md:32` uses it
   for the K-node claim branch, and the original 4-skill map had simply missed it.
2. **`chimera-papers` / `chimera-vault` excluded** from the agent-reference scan — correct; both
   `chimera-triage-paper` and `chimera-deep-extract` reference those as MCP *servers*, not agents.
3. **`_parse_flat_frontmatter` pre-quotes values before `yaml.safe_load`** — accepted. Every agent
   file's prose `description:` contains its own colon, which trips PyYAML's block-mapping
   ambiguity on the raw block; the real loader evidently tolerates flat single-line frontmatter.
   The helper models that, and PyYAML still performs the parse. Noted as the weakest link in the
   module: it is a model of the loader, not the loader.

## Acceptance

- [x] `pytest tests/test_registration.py -q` green (exit 0)
- [x] Negative control **fails**, on both surfaces, naming the offending file
- [x] All 17 skill directories are map keys; all 8 agent files parse
- [x] Full suite does not regress (227, exit 0); ruff clean
- [x] Red lines held: `tests/` only · no regex-inference of tool names · both
      `analyze_paper_data` regressions verbatim · no opportunistic refactoring

## Findings carried out

1. **A green suite proved nothing here, twice.** Round 1 was green and defective; the defect
   surfaced only under a deliberately broken input. The negative control is what made this sprint
   real, and it belongs in the seal for every check L.C adds.
2. `_parse_flat_frontmatter` approximates the Claude Code agent loader rather than invoking it. If
   the real loader's rules ever diverge, this module passes while the runtime fails — the same
   shape as the class it guards. Recorded, not fixed (out of scope).
