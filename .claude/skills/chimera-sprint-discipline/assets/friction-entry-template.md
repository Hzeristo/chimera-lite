# Friction Entry Template

> **Not wired to `<invocation_modes>`.** Unlike the other three assets in this folder, no
> chimera-sprint-discipline mode writes friction entries — friction logging happens continuously
> during a Use Week (see `chimera-core-philosophy` → "Friction-Driven Development"), not at a
> phase gate. This file is a style reference for that practice, kept here because
> `docs/logs/friction-*.md` is a phase-record input this skill reads (bootstrap_protocol,
> batch_planning preconditions, phase_review step 0/6).
>
> **Format scope:** this is the schema actually in use for entries from 2026-07-08 onward
> (see `docs/logs/friction-260708.md` through `friction-260713.md` for worked examples).
> Entries before that date (`friction-260426.md` through `friction-260611.md`) use a retired
> Chinese field-label schema, with variance even among themselves — do not retroactively
> rewrite legacy entries; tolerate format variance when reading them.
>
> A friction log file can hold multiple dated entries; separate them with `---`.

```markdown
# friction-{YYMMDD}-{NN} — {short, specific title naming the gap}

**Date:** YYYY-MM-DD
**Status:** OPEN | RESOLVED ({date}, {phase}) — {one-line resolution summary} | PARTIALLY ADDRESSED — {what's still open}
**Phase context:** {what phase or work was in flight when this was logged}

## What I wanted (or: What I expected / What I wanted to do)
{1-2 sentences — the goal, not the workaround}

## What I actually got (or: What actually happens / What I actually did)
{the gap between expectation and reality — concrete, not vague}

## Root cause
{why, not just what — the mechanism behind the gap}

## {Ideal | Lesson | Resolution | Scope guard — pick what fits, more than one is fine}
{closing section(s). Worked entries close with "Ideal" (desired behavior), "Lesson"
(the generalizable insight), or both.}
```
