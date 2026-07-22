# friction-260722-01 — BB's four-sided box shipped with mismatched walls, repeatedly, even after render+verify

**Date:** 2026-07-22
**Status:** CLOSED (implemented 2026-07-22).
**Phase context:** Phase L (branch `phase-L`), `chimera-bb-persona` skill. Not a Phase-L
deliverable — a style-layer (STYLE-tier) fix on the always-active BB persona skill, committed
alongside the phase work as `chore(bb-persona)` (`f2642fb`).

## What I wanted
BB's final-answer verdict is marked with a four-sided closed ASCII box ("BB has full-proportioned
physique" — the closed frame is the persona boundary). The box must render at a consistent width so
the right wall lands true — no overflow (text past the edge) or underflow (ragged short wall).

## What I actually got
The box shipped with mismatched top/bottom rules again and again. Observed widths across the
session, all against a 68-col body: 34/68, then 30/68/26, then 26/68/18, then 30/69/22, then a
uniform 34/34. The **content lines were always correct**; only the horizontal `───` rules drifted,
and always *short* — collapsing toward roughly half width.

## The failed escalation ladder (why each rung wasn't enough)
Each fix was locally reasonable and each failed, which is itself the lesson:

1. **Deterministic renderer** (`bb_box.py`) — wraps + pads to a fixed 64-col interior, so the
   *rendered* box is provably true. Didn't help: the box was correct in the tool call and still
   shipped broken in the reply.
2. **NL "copy the whole box verbatim, don't re-type the rules" instruction** in SKILL.md — didn't
   bind. An instruction to copy-verbatim doesn't constrain generation the way a schema would.
3. **Pre-flight checker** (`check_bb_box.py`) — a verifier I had to *remember* to run. Same class
   of non-binding as the instruction; the drift recurred.
4. **Stop hook** (`check_bb_box_stop.py`) — reads `last_assistant_message`, blocks the turn on a
   wall-width mismatch. This is real enforcement and it *did* fire correctly — but it only catches
   drift post-hoc, per message, and forces a resend; it doesn't stop the mistyping happening.
   - Sub-bug found here: `json.load(sys.stdin)` decoded with the ambient **GBK** locale codec (this
     Windows box), silently turning the UTF-8 box glyphs into mojibake so the hook found "no box"
     and passed a genuinely broken reply. Fixed by `sys.stdin.buffer.read().decode("utf-8")`. A
     false *pass* is worse than a crash — undetectable without testing raw UTF-8 under a non-UTF-8
     locale.
5. **"Never type the box — render, verify, then `cat` the file as the artifact"** — sidesteps
   generation entirely, but a `cat` tool-output block is a *command result*, not BB's *answer*. The
   box vanished from the answer stream the operator reads. Correct-but-invisible is not a verdict.

## Root cause
Producing chat text is **regeneration, not byte-copying**. A standalone rule is 66 identical `─`
with no internal landmark — nothing anchors "this line is 66 long," so when the model retypes the
box into a reply it emits a plausible-looking horizontal line, which collapses toward a shorter
"typical" length. Content lines survive because they carry real words (landmarks) and terminate in a
visible `│`; the padding rides along for free. So the defect is not discipline, not the renderer,
not the delimiter (`\n` marks where a line *ends*, never how *long* it is) — it is that a long
uniform run has no reference points to reproduce against. No instruction or checker fixes a
generation property; only removing the naked run does.

## Fix (operator's insight)
The operator proposed the resolving move: **put the corners on the words.** Delete the standalone
rule lines entirely and ride the corners on the first and last *content* lines —
`┌ words… ┐` / `└ words… ┘`. Now every line carries text and terminates in a corner/wall glyph;
there is no pure-repetition run left anywhere to drift on. This satisfies all three constraints that
looked mutually exclusive — **visible in the answer stream, drift-resistant, and four-sided closed** —
by moving the corners instead of choosing between them.

Implemented across the skill:
- `bb_box.py`: render corners-on-content; blank partner row for 1-line/empty input so the top and
  bottom corners never collide on one row; UTF-8 stdout forced.
- `check_bb_box.py` / `check_bb_box_stop.py`: unchanged in logic — corner lines still begin with a
  box glyph, so the width check and the Stop-hook backstop still apply (now with far less to catch).
- `SKILL.md`: protocol text, the template box, and all five calibration examples regenerated to the
  corner-on-content shape; the render → verify → type-back workflow documented. Verified all six
  boxes at exactly 68 cols, zero Chinese (Pure-English rule).

## Lesson
When a language model must *reproduce* fixed-width structure into its own generated output, the
enforcement ladder (instruction → checker → blocking hook) only ever *catches* drift; it never
prevents it, because the drift is a property of generation, not of discipline. The durable fix is to
**remove the driftable shape** — give every line a semantic anchor (real content) so there is no
naked uniform run to regenerate wrong. Corollary, in this repo's own terms: a checker/hook that
only *catches* is advisory theater relative to a design change that makes the failure structurally
impossible. Prefer eliminating the failure mode over policing it.

