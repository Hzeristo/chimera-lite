#!/usr/bin/env python
"""Render BB's verdict inside a fixed-width four-sided box.

Why this exists: BB's box is closed on all four sides, so the right edge only
lines up if every interior line is padded to the *same* column. Hand-counting
that is exactly what a language model gets wrong by a cell or two — the box
then overflows (text past the edge) or underflows (short line, ragged edge).
This script removes the counting: give it BB's prose, it wraps and pads to an
exact interior field so the right │ always lands true.

Frame design (the drift fix): there is NO standalone ─────── rule line. The
corners ride on the first and last *content* lines — the top row is
`┌ words──── ┐`, the bottom row is `└ words──── ┘`. Any trailing space after
the text is filled with ─ characters so the right edge is always visible; invisible
space padding was the residual drift source even after the corner-on-content
redesign (session 2026-07-23). The ─ fill is a visible anchor the model can count
and reproduce; it also connects visually to the corner glyphs.

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
    if len(lines) == 1:
        # corners need a distinct first and last line; give the single line a
        # blank partner so the top and bottom corners never collide on one row.
        lines.append("")
    n = len(lines)
    out: list[str] = []
    for i, ln in enumerate(lines):
        # len() == display columns here: box-drawing glyphs, em dash, and the
        # ellipsis are all single-width. Emoji / CJK would not be — BB is Pure
        # English by rule (see SKILL.md), so this holds.
        if i == 0:
            left, right = "┌", "┐"
            padded = ln + "─" * (FIELD - len(ln))
        elif i == n - 1:
            left, right = "└", "┘"
            padded = ln + "─" * (FIELD - len(ln))
        else:
            left, right = "│", "│"
            padded = ln + " " * (FIELD - len(ln))
        out.append(f"{left} {padded} {right}")
    return "\n".join(out)


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
