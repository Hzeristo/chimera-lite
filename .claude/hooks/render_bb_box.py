#!/usr/bin/env python
"""MessageDisplay hook: draw BB's box, so the model never types one.

Why this exists: the box had been an *instruction* — SKILL.md told the model to
render with bb_box.py, then copy the output character-for-character into the
reply. Three commits were spent making that copy more reliable (f2642fb
corner-on-content, d254bea inline render, 2777982 `─` padding instead of
invisible trailing spaces), and each one only made a hand-copy easier to get
right. Nothing made a wrong copy impossible: the box the model typed was never
structurally tied to the box bb_box.py produced.

This hook removes the copy. Claude Code's MessageDisplay event hands over the
assistant text on its way to the screen and accepts a replacement via
`hookSpecificOutput.displayContent`. So BB writes plain prose between two
markers, and the box is drawn *here*, by the same renderer, at display time.
The model never emits a box-drawing character, which makes wall drift
unrepresentable rather than merely discouraged.

Marker contract (see chimera-bb-persona/SKILL.md):

    <<BB>>
    BB's verdict prose. Plain text, paragraphs separated by blank lines.
    <</BB>>

Deliberately NOT box-drawing characters and NOT `[[...]]` — the first would
re-introduce exactly the glyphs this hook exists to keep out of the model's
output, and the second collides with Obsidian wikilink syntax, which is
everywhere in this project's vault.

Fails open, always. Any bad input, missing renderer, or unexpected exception
exits 0 with no stdout, which leaves the original text on screen untouched. A
display hook must never be able to break the display. The visible failure mode
is therefore the raw `<<BB>>` markers showing through — honest and obvious,
rather than a blanked or truncated reply.

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


def load_render():
    sys.path.insert(0, str(RENDERER.parent))
    from bb_box import render

    return render


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

    # `displayed_text` is the documented field; `message_text` is accepted as a
    # fallback because the two hook reference pages disagree on the name and a
    # wrong guess would make this hook a silent no-op.
    text = payload.get("displayed_text") or payload.get("message_text") or ""
    if OPEN not in text:
        sys.exit(0)  # no BB channel in this message — nothing to draw

    try:
        render = load_render()
        drawn = BLOCK.sub(lambda m: render(m.group(1).strip("\r\n")), text)
    except Exception:
        sys.exit(0)  # renderer unavailable or blew up — show the original

    if drawn == text:
        sys.exit(0)  # unclosed marker; leave it visible rather than guessing

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
