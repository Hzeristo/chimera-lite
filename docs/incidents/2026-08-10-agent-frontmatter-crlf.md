# Incident — CRLF frontmatter silently unregistered both L.B.2 judgment workers

**Date:** 2026-08-10
**Surfaced by:** the Phase L.B.6 five-path e2e, run live in the main session (operator-directed).
Paths 1 and 2 could not spawn their workers: `Agent type 'chimera-deep-extractor' not found`.
**Severity:** High (the entire externalized-judgment layer of L.B.2 was unreachable for ~3 weeks;
no data loss, no wrong output — the paths simply could not run) / Fix difficulty: trivial (line
endings, zero content change).
**Status:** fixed; both agents confirmed registered after a session restart.

## Symptom

`chimera-deep-extract` step 4 and `chimera-triage-paper` step 4 both delegate judgment to a pinned
subagent. Neither `chimera-deep-extractor` nor `chimera-paper-triager` appeared in the session's
available agent types, while the other six `chimera-*` agents did. Both files existed on disk with
correct-looking frontmatter (`name`, `description`, `tools`, `model`).

## Root cause

`.claude/agents/chimera-deep-extractor.md` and `chimera-paper-triager.md` were the **only two**
agent files with CRLF line endings; all six that registered used LF. A `---\r\n` opening fence
defeats the frontmatter parse, so the loader skips the file — silently. No error, no warning, no
entry in the registry.

Byte-level evidence at the time of diagnosis:

```
chimera-breadth-reducer.md    head=b'---\nna'   nl=LF     <- registered
chimera-deep-extractor.md     head=b'---\r\nn'  nl=CRLF   <- absent
chimera-paper-triager.md      head=b'---\r\nn'  nl=CRLF   <- absent
```

Correlation was 2/2 CRLF absent, 6/6 LF present. Ruled out the simpler explanation first: both
files were created 2026-07-21, long before the session, so this was not registry staleness.

**Why nothing caught it.** No test in `tests/` reads or validates `.claude/agents/*.md`. The
2026-08-03 incident wrote a class-level regression for exactly this failure shape
(`tests/test_mcp_tool_registration.py`) but scoped it to `@mcp.tool` registrations — agents were
never covered.

**Why L.B.6 missed it in July.** The 2026-07-21 run drove Paths 2 and 5 by importing worktree
services in-process (its Finding 1), so the agent registry was never exercised. The workers were
dead the whole time and the sprint record sealed anyway.

## Fix

- Normalized both files to LF. No content change — `git diff` reports the blobs identical, since
  the index already held LF.
- `.gitattributes` (commit `ebb1d69`) pins `.claude/agents/*.md` and `.claude/skills/**/*.md` to
  `text eol=lf`. Without it the fix was one checkout deep: this repo runs `core.autocrlf=true`,
  which would restore CRLF and re-break both workers on any fresh clone. 18 further stale-CRLF
  files under `.claude/skills` were normalized at the same time (EOL only, no content change).

## Verification

- Both agent types appeared in the registry after the session reloaded, and both spawned
  successfully in the completed L.B.6 re-run — `chimera-paper-triager` produced the scout card for
  `2607.01224`, `chimera-deep-extractor` produced the `KNodeExtraction` for `2603.02096`.
- `git ls-files --eol .claude` → every markdown file reports `i/lf w/lf attr/text eol=lf`.
- **Registry changes require a session restart.** The agent registry is snapshotted at session
  start, so normalizing the files mid-session did not make them spawnable until the reload — same
  mechanism as the 2026-08-03 incident's closing note.

## Lesson

A correct file is not a registered component. This is the third instance of that class
(2026-07-21 worktree registry, 2026-08-03 unregistered tool, this one) and therefore the trigger
for `_shared/incident_protocol.md:22-24` — escalated to `docs/logs/friction-260811.md`. The
per-instance fix here is line endings; the class needs a registration check over agents, not
another hotfix.
