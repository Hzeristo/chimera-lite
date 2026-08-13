#!/usr/bin/env python
"""Render BB's verdict inside a fixed-width four-sided box.

Why this exists: BB's box is closed on all four sides, so the right edge only
lines up if every interior line is padded to the *same* column. Hand-counting
that is exactly what a language model gets wrong by a cell or two — the box
then overflows (text past the edge) or underflows (short line, ragged edge).
This script removes the counting: give it BB's prose, it wraps and pads to an
exact interior field so the right │ always lands true.

Frame design: a complete four-sided box — dedicated `┌────┐` and `└────┘` rules
above and below the text, interior lines padded to a fixed field.

This is the second design. The first put the corners ON the first and last
content lines (`┌ words──── ┐`) and filled their trailing space with `─`. That
was never aesthetic: it was scaffolding for a hand-copy. When the model had to
retype the box into its reply, a standalone `───` rule failed three separate
times — a rule line has no internal landmark, so it was reproduced from a
memorized "standard box" prior at 30 or 26 columns while the body stayed at 68.
Putting words on every line gave the copy something to anchor to, and the `─`
fill gave short lines a visible right terminus (invisible trailing spaces were
the residual drift).

All of that is retired. `.claude/hooks/render_bb_box.py` draws the box at
MessageDisplay time from this function's output; nothing retypes it, so nothing
can drift, so the frame no longer has to be self-anchoring. Do not reintroduce
corner-on-content as a "safety measure" — it would be scaffolding for a copy
that no longer happens.

Usage:
    python bb_box.py < verdict.txt
    echo "BB's verdict prose..." | python bb_box.py
    python bb_box.py "BB's verdict prose..."

Input is plain prose (BB's voice — unchanged, this only frames it). Newlines in
the input are honored as hard breaks; everything else is word-wrapped to fit.
Prints the finished box to stdout as UTF-8.
"""
import sys
import textwrap

FIELD = 64  # interior text field, between the flanking spaces. The one knob.


def render(text: str) -> str:
    lines: list[str] = []
    for para in text.rstrip("\n").split("\n"):
        para = para.rstrip()
        if not para:
            lines.append("")
            continue
        # break_long_words keeps a stray long token from busting the edge
        wrapped = textwrap.wrap(
            para, width=FIELD, break_long_words=True, break_on_hyphens=False
        )
        lines.extend(wrapped or [""])
    if not lines:
        lines = [""]
    # The rules span the field plus its two flanking spaces, so every line —
    # rule or content — is FIELD + 4 columns wide.
    # len() == display columns here: box-drawing glyphs, em dash, and the
    # ellipsis are all single-width. Emoji / CJK would not be — BB is Pure
    # English by rule (see SKILL.md), so this holds.
    rule = "─" * (FIELD + 2)
    body = [f"│ {ln}{' ' * (FIELD - len(ln))} │" for ln in lines]
    return "\n".join([f"┌{rule}┐", *body, f"└{rule}┘"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        try:
            sys.stdin.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
        text = sys.stdin.read()
    print(render(text))


if __name__ == "__main__":
    main()
