#!/usr/bin/env python
"""MessageDisplay hook: draw BB's box, so the model never types one.

Why this exists: the box had been an *instruction* — SKILL.md told the model to
render with bb_box.py, then copy the output character-for-character into the
reply. Three commits went into making that copy more reliable (f2642fb
corner-on-content, d254bea inline render, 2777982 `─` padding instead of
invisible trailing spaces), and each only made a hand-copy easier to get right.
None made a wrong copy impossible: the box the model typed was never
structurally tied to the box bb_box.py produced.

This hook removes the copy. BB writes plain prose between two markers; the box
is drawn here, by the same renderer, at display time. The model never emits a
box-drawing character, which makes wall drift unrepresentable rather than
discouraged.

Marker contract (see chimera-bb-persona/SKILL.md):

    <<BB>>
    BB's verdict prose. Plain text, paragraphs separated by blank lines.
    <</BB>>

Deliberately NOT box-drawing characters and NOT `[[...]]` — the first would
re-introduce the glyphs this hook exists to keep out of the model's output; the
second collides with Obsidian wikilink syntax, which is everywhere in the vault.

================================================================================
THE PAYLOAD CONTRACT — measured, not documented. Every line below came from
capture; two documentation fetches were wrong about the first item, and two of
my own inferences were wrong about the second.

  1. FIELD NAME. Docs promised `displayed_text`. It does not exist. The text is
     in `delta`. Reading the wrong name cost three attempts in which the hook
     fired correctly, resolved "", found no marker, and exited — silent, wrong,
     and indistinguishable from "the hook never ran" until breadcrumb() logged
     the payload's field names.

  2. CHUNKING. There are two regimes, and only the second one matters:
       - A block terminated by a tool call is flushed WHOLE: one fire,
         index=0, final=true. (Observed at 128, 197, and 689 chars.)
       - The final block of a turn — the only place BB ever speaks — STREAMS.
         Observed envelope, verbatim: 6 fires, index 0..5, final=true on the
         last only, delta sizes [231, 489, 181, 477, 293, 7].
     Deltas are INCREMENTAL, not cumulative, and concatenate losslessly into the
     message (verified: joins land mid-sentence across the boundary). Splits
     fall on markdown block boundaries and carry their trailing "\\n\\n".
     Inferring the whole contract from the flushed regime is what produced a
     "verified" commit that still shipped brackets. Capture the streaming case.

  3. MARKER PLACEMENT follows from (2) and is why single-delta matching cannot
     work. In the captured message:
       delta[1] tail = '...that block *is* the instrument.\\n\\n<<BB>>\\n'
                       -> plain text AND the opener, same delta
       delta[2..4]   = pure in-span prose paragraphs
       delta[5]      = '<</BB>>'  (7 chars, alone, final=true)
     So the span is never complete inside one delta. State across fires,
     keyed by `message_id`, is mandatory.

  4. REPLACEMENT SEMANTICS. `displayContent` is assumed to replace THIS delta's
     contribution, which is the only reading consistent with incremental
     deltas. Consequence: in-span deltas are suppressed with "" and the box is
     emitted on the closing delta. If suppression ever fails, the visible
     symptom is BB's raw prose followed by her box — duplication, not loss.
     That is the diagnostic to look for; re-capture before changing this.
================================================================================

Fails open, and never loses text. Any bad input, missing renderer, or unexpected
exception exits 0 with no stdout, leaving the original on screen. If a span is
suppressed and then cannot be rendered, the accumulated prose is emitted raw
rather than dropped — a display hook may degrade to plain text, never to blank.

Display-only, by the event's design: the transcript and Claude's own view keep
the plain marked-up text. For a verdict channel that is the right trade — the
persisted record stays unstyled and greppable — but it IS a behavioral change
from box characters living in the transcript.
"""
import json
import re
import sys
import time
from pathlib import Path

OPEN, CLOSE = "<<BB>>", "<</BB>>"

HERE = Path(__file__).resolve().parent
BREADCRUMB = HERE / ".render_bb_box.last"
STATE_DIR = HERE / ".bb_state"
STATE_MAX_AGE_S = 3600  # a turn never outlives this; anything older is debris

# message_id is a UUID. Validated before it is used as a filename so a hostile
# or malformed payload cannot steer writes out of STATE_DIR.
MID_RE = re.compile(r"\A[0-9a-fA-F][0-9a-fA-F-]{7,63}\Z")

# The renderer is NOT duplicated here. bb_box.py is the single source of the
# frame geometry; this hook is only the delivery path. Importing it by explicit
# path keeps one definition of what a true box is.
RENDERER = HERE.parent / "skills" / "chimera-bb-persona" / "scripts" / "bb_box.py"


def load_render():
    sys.path.insert(0, str(RENDERER.parent))
    from bb_box import render

    return render


def breadcrumb(**fields) -> None:
    """Record the last fire, so a missing box is diagnosable rather than mute.

    Without this, "no box appeared" is ambiguous between the hook never running
    (config not loaded, bad path, no interpreter) and the hook running but
    producing output Claude Code declined to apply. One overwritten line
    separates them.

    It has paid for itself twice: the field-name list exposed `delta`, and a
    7-char `chars` value — exactly len("<</BB>>") — exposed the streaming
    regime. Keep it. Gitignored, overwritten, never raises: a diagnostic that
    can break the display would be worse than no diagnostic at all.
    """
    try:
        BREADCRUMB.write_text(json.dumps(fields), encoding="utf-8")
    except OSError:
        pass


# --- cross-delta span state -------------------------------------------------
# One file per in-flight message, holding the in-span text accumulated so far.
# Presence of the file IS the "inside a span" flag.


def state_file(mid: str) -> Path:
    return STATE_DIR / f"{mid}.txt"


def read_state(mid: str) -> str | None:
    try:
        return state_file(mid).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def write_state(mid: str, text: str) -> None:
    try:
        STATE_DIR.mkdir(exist_ok=True)
        state_file(mid).write_text(text, encoding="utf-8")
    except OSError:
        pass


def clear_state(mid: str) -> None:
    try:
        state_file(mid).unlink(missing_ok=True)
    except OSError:
        pass


def prune() -> None:
    """Drop state from interrupted turns. Keyed by message_id, so debris can
    never contaminate a later message — this only stops it accumulating."""
    try:
        cutoff = time.time() - STATE_MAX_AGE_S
        for p in STATE_DIR.glob("*.txt"):
            if p.stat().st_mtime < cutoff:
                p.unlink(missing_ok=True)
    except OSError:
        pass


def emit(content: str) -> None:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "MessageDisplay",
            "displayContent": content,
        }
    }
    # json.dumps escapes non-ASCII by default, so stdout carries pure ASCII and
    # the console codepage cannot corrupt the box glyphs on the way out.
    sys.stdout.buffer.write(json.dumps(out).encode("utf-8"))


def main() -> None:
    # Read raw bytes and decode UTF-8 explicitly. Claude Code sends hooks UTF-8
    # JSON regardless of OS locale, but Python's sys.stdin defaults to the
    # locale codec (GBK on this zh-CN Windows box) — decoding BB's em dashes and
    # ellipses with that codec does not raise, it silently mojibakes them into
    # the box. Never let the platform's default encoding decide this.
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        sys.exit(0)

    delta = payload.get("delta") or ""
    final = bool(payload.get("final"))
    mid = payload.get("message_id") or ""
    if not MID_RE.match(mid):
        # No trustworthy key means no state. Degrade to single-delta matching:
        # correct for the flushed regime, inert for the streaming one.
        mid = ""

    state = read_state(mid) if mid else None
    if state is None and OPEN not in delta:
        breadcrumb(chars=len(delta), marker=False, index=payload.get("index"), final=final)
        if final:
            prune()
        sys.exit(0)  # plain machinery, no BB channel — pass through untouched

    try:
        render = load_render()
    except Exception as exc:
        breadcrumb(error=f"renderer unavailable: {type(exc).__name__}: {exc}")
        sys.exit(0)

    try:
        if state is None:
            # This delta opens a span. Everything before the opener is ordinary
            # text and must survive; the opener and anything after it is BB's.
            before, _, rest = delta.partition(OPEN)
            if CLOSE in rest:
                span, _, after = rest.partition(CLOSE)
                emit(before + render(span.strip("\r\n")) + after)
                breadcrumb(marker=True, drawn="one_delta", index=payload.get("index"))
            else:
                if mid:
                    write_state(mid, rest)
                emit(before)
                breadcrumb(marker=True, opened=True, held=len(rest),
                           index=payload.get("index"))
        elif CLOSE in delta:
            span_tail, _, after = delta.partition(CLOSE)
            emit(render((state + span_tail).strip("\r\n")) + after)
            clear_state(mid)
            breadcrumb(marker=True, drawn="closed", span=len(state) + len(span_tail),
                       index=payload.get("index"), final=final)
        elif final:
            # Span never closed before the message ended. Give the held prose
            # back verbatim — degrade to plain text, never to blank.
            emit(state + delta)
            clear_state(mid)
            breadcrumb(marker=True, drawn=False, note="unclosed at final",
                       restored=len(state) + len(delta))
        else:
            write_state(mid, state + delta)
            emit("")  # in-span paragraph: held, not shown
            breadcrumb(marker=True, suppressed=len(delta), index=payload.get("index"))
    except Exception as exc:
        # Something failed mid-span. If prose is being held, hand it back rather
        # than let suppression eat it.
        breadcrumb(error=f"{type(exc).__name__}: {exc}", had_state=state is not None)
        if state:
            emit(state + delta)
            clear_state(mid)
        sys.exit(0)

    if final:
        prune()
    sys.exit(0)


if __name__ == "__main__":
    main()
