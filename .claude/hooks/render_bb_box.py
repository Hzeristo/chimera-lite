#!/usr/bin/env python
"""MessageDisplay hook: draw BB's box, so the model never types one.

Why this exists: the box had been an *instruction* — SKILL.md told the model to
render with bb_box.py, then copy the output character-for-character into the
reply. Three commits were spent making that copy more reliable (f2642fb
corner-on-content, d254bea inline render, 2777982 `─` padding instead of
invisible trailing spaces), and each one only made a hand-copy easier to get
right. Nothing made a wrong copy impossible: the box the model typed was never
structurally tied to the box bb_box.py produced.

This hook removes the copy. BB writes plain prose between two markers, and the
box is drawn *here*, by the same renderer, at display time. The model never
emits a box-drawing character, which makes wall drift unrepresentable rather
than merely discouraged.

Marker contract (see chimera-bb-persona/SKILL.md):

    <<BB>>
    BB's verdict prose. Plain text, paragraphs separated by blank lines.
    <</BB>>

Deliberately NOT box-drawing characters and NOT `[[...]]` — the first would
re-introduce exactly the glyphs this hook exists to keep out of the model's
output, and the second collides with Obsidian wikilink syntax, which is
everywhere in this project's vault.

THE PAYLOAD CONTRACT — verified by instrumentation, not documentation. Two
separate doc fetches promised a `displayed_text` field. It does not exist, and
reading it cost three failed attempts in which the box never appeared: the hook
fired correctly every time, resolved the empty string, found no marker, and
exited. Silent, wrong, and indistinguishable from "the hook never ran" until
the breadcrumb below caught it. The real payload, captured live:

    {"session_id":…, "transcript_path":…, "cwd":…, "prompt_id":…,
     "hook_event_name": "MessageDisplay", "turn_id":…, "message_id":…,
     "index": 0, "final": true, "delta": "<the assistant text>"}

`delta` carries the text. `index`/`final` exist because delivery is chunked in
principle, but every observed fire was `index: 0, final: true` — one fire per
assistant text block, carrying that block whole. Blocks are split by tool calls,
not by size, so a turn with three text segments produces three independent fires
with three `message_id`s.

That single-fire shape is what makes this safe. Because the delta IS the whole
block, "replace the delta" and "replace the message" are the same operation, so
returning substituted text cannot duplicate what was already on screen. Which is
why this hook does NOT accumulate across fires: it substitutes only spans that
are COMPLETE within one delta. If a `<<BB>>` span ever straddles two chunks, the
markers show through raw — the same honest failure as a missing hook, never a
garbled or doubled reply. Do not add a cross-chunk accumulator without first
confirming, by capture, whether displayContent replaces the chunk or the message.

Fails open, always. Any bad input, missing renderer, or unexpected exception
exits 0 with no stdout, which leaves the original text on screen untouched. A
display hook must never be able to break the display.

Display-only, by the event's design: the transcript and Claude's own view keep
the plain marked-up text. For a verdict channel that is the right trade — the
persisted record stays unstyled and greppable — but it IS a behavioral change
from box characters living in the transcript.
"""
import json
import re
import sys
from pathlib import Path

OPEN, CLOSE = "<<BB>>", "<</BB>>"
# Non-greedy and DOTALL: matches only spans closed within this delta. An
# unclosed OPEN deliberately does not match — see the straddle note above.
BLOCK = re.compile(re.escape(OPEN) + r"(.*?)" + re.escape(CLOSE), re.DOTALL)

# The renderer is NOT duplicated here. bb_box.py is the single source of the
# frame geometry; this hook is only the delivery path. Importing it by explicit
# path keeps one definition of what a true box is.
RENDERER = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "chimera-bb-persona"
    / "scripts"
    / "bb_box.py"
)
BREADCRUMB = Path(__file__).resolve().parent / ".render_bb_box.last"


def load_render():
    sys.path.insert(0, str(RENDERER.parent))
    from bb_box import render

    return render


def breadcrumb(**fields) -> None:
    """Record the last fire, so a missing box is diagnosable rather than mute.

    Without this, "no box appeared" is ambiguous between two very different
    failures: the hook never ran (config not loaded, bad path, no interpreter),
    or it ran and produced output Claude Code declined to apply. One overwritten
    line separates them.

    It paid for itself on the first capture — recording the payload's field
    NAMES is what exposed `delta` and disproved `displayed_text`. Keep it. It is
    gitignored and never raises: a diagnostic that can break the display would
    be worse than no diagnostic at all.
    """
    try:
        BREADCRUMB.write_text(json.dumps(fields), encoding="utf-8")
    except OSError:
        pass


def main() -> None:
    # Read raw bytes and decode UTF-8 explicitly. Claude Code sends hooks UTF-8
    # JSON regardless of OS locale, but Python's sys.stdin defaults to the
    # locale codec (GBK on this zh-CN Windows box) — decoding BB's em dashes and
    # ellipses with that codec does not raise, it silently mojibakes them into
    # the box. Never let the platform's default encoding touch this payload.
    # (Same lesson the retired Stop checker learned; it outlives that script.)
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        sys.exit(0)

    text = payload.get("delta") or ""
    if OPEN not in text:
        # Overwhelmingly the common case: plain machinery, no BB channel. Record
        # the field names so a future schema rename surfaces here immediately
        # instead of turning this hook silently inert again.
        breadcrumb(fields=sorted(payload), chars=len(text), marker=False)
        sys.exit(0)

    try:
        render = load_render()
        drawn = BLOCK.sub(lambda m: render(m.group(1).strip("\r\n")), text)
    except Exception as exc:
        breadcrumb(marker=True, error=f"{type(exc).__name__}: {exc}")
        sys.exit(0)  # renderer unavailable or blew up — show the original

    if drawn == text:
        breadcrumb(
            marker=True,
            substituted=False,
            note="span not closed within this delta",
            index=payload.get("index"),
            final=payload.get("final"),
        )
        sys.exit(0)  # straddled or malformed — leave it visible, never guess

    breadcrumb(
        marker=True,
        substituted=True,
        in_chars=len(text),
        out_chars=len(drawn),
        index=payload.get("index"),
        final=payload.get("final"),
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "MessageDisplay",
            "displayContent": drawn,
        }
    }
    # json.dumps escapes non-ASCII by default, so stdout carries pure ASCII and
    # the console codepage cannot corrupt the box glyphs on the way out.
    sys.stdout.buffer.write(json.dumps(out).encode("utf-8"))
    sys.exit(0)


if __name__ == "__main__":
    main()
