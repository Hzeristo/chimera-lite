# 2026-08-12 — `vault_query` silently returned partial results on CRLF notes

**Class:** code defect (silent partial answer), shipped tool
**Severity:** High — no error, no warning, a plausible-looking shorter list.
**Found:** during Phase L.C sprint C.3c, on the first live call of the new review workflow.
**Fixed:** `mcp-servers/chimera-vault/vault_query.py` — added `--crlf` to the ripgrep invocation.
**Regression:** `tests/test_vault_query_crlf.py` (2 tests, negative-controlled).

## Symptom

`vault_query(status="PENDING_REVIEW")` returned **2** matches. The vault's `Harness/` folder held
**6** artifacts, every one of them at `status: PENDING_REVIEW`, verified by direct file read.

Nothing failed. The tool returned a well-formed answer that was two-thirds wrong.

## Root cause

`vault_query` builds an anchored ripgrep pattern — `^status: {status}$` (or `^type: {type}$`) —
and shells out to `rg`. Without `--crlf`, ripgrep's `$` cannot match past a trailing `\r`, so any
note saved with CRLF line endings fails the pattern and never reaches the Python-side filter.

The vault is edited on Windows and by Obsidian, so its notes carry **mixed** line endings. Measured
in `Harness/`:

| file | CRLF pairs | matched before fix |
|---|---|---|
| `w1_verdict__2501.05510.md` | 0 | ✅ |
| `w1_verdict__2606.16353.md` | 0 | ✅ |
| `w1_verdict__2605.06527-best-model-55.2.md` | 33 | ❌ |
| `w1_verdict__2605.17065.md` | 77 | ❌ |
| `w2_breadth_map__agentic-memory-reliability-over-time.md` | 35 | ❌ |
| `w2_breadth_map__topic_streaming-video-memory.md` | 54 | ❌ |

Proven directly at the shell: `rg` without `--crlf` returns 2 files; `rg --crlf` returns all 6.

## Why this one is worse than a crash

A crash is honest. This returned a shorter list that looked complete, and every consumer would
have treated it as the full set. The workflow that found it — C.3c's review surface — exists
precisely to show the Architect *every* pending verdict before promotion. Built on the unfixed
tool, it would have silently hidden four verdicts from a review whose entire purpose is that
nothing is hidden. The skill's own red line ("never silently truncate the list") would have been
violated by its data source rather than by its logic.

## Blast radius

- **`vault_query` is the only ripgrep call site in the repo** (verified: `grep -rln '"rg"'`), so no
  other tool shares the defect.
- Both filters are affected — `^type: X$` as well as `^status: X$`. `linked_to` is an unanchored
  substring pattern and was never affected.
- **The C.1 friction baseline is unaffected.** Its composition census was built from direct
  filesystem counts, not from `vault_query`; the typed counts reconcile exactly against it
  (399 knowledge = 378 inbox + 18 deep-reads + 3 committed). Had the baseline been taken through
  the tool, it would have been wrong and would have anchored the whole phase's I1.4 measurement.
- One live consequence found: `Insight/Dynamic empirical study on agent memory.md` is CRLF and
  carries `type: insight`, so it was invisible to every typed query since the tool shipped.

## The class

This is the **third distinct manifestation of CRLF-defeats-a-check today**:

1. `.claude/agents/*.md` frontmatter — killed two judgment workers for three weeks
   (`2026-08-10-agent-frontmatter-crlf.md`, `friction-260811-01` instance 3).
2. C.2's first attempt at the guard against (1) — its byte-0 fence check passed on a CRLF file
   while its comment claimed to guard "the CRLF/BOM class".
3. This — `vault_query`'s anchored patterns.

`.gitattributes` pins `.claude/**` markdown to LF, which addresses (1) only. **The vault is not in
the repo and cannot be pinned**, so line-ending tolerance has to be a property of every tool that
reads it, not a property of the files.

## Fix

```
"rg", "--crlf", "--files-with-matches", "-m", "1", "--glob", "*.md", ...
```

with the reason recorded inline, and a regression that writes both an LF and a CRLF fixture **as
bytes** — never letting the platform's newline translation decide what the test is testing.

**Negative control:** removing `--crlf` fails both tests; restoring it passes them. Full suite
236 passed, exit 0.

## Not fixed here

`vault_query.py` carries 6 pre-existing ruff findings (blind `except Exception`, import order,
`asyncio.TimeoutError`). Confirmed identical against `git show HEAD:` — untouched, out of scope.
