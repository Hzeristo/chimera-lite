#!/usr/bin/env python
"""Verify a BB box: every line — top rule, content, bottom rule — is one width.

Scope note (changed): this was written as a pre-send gate, back when the model
hand-copied bb_box.py's output into the reply and the copy could drift. That
copy no longer exists — `.claude/hooks/render_bb_box.py` draws the box at
MessageDisplay time from the same renderer, so a shipped box is bb_box.py's
output by construction and cannot disagree with it.

What remains is a **regression check on the renderer itself**: pipe bb_box.py
through this to confirm a change to FIELD or the padding logic still produces a
uniform-width frame. It is a development tool, not a guarantee in the reply
path — do not cite it as one.

Usage:
    python bb_box.py "some prose" | python check_bb_box.py
    python check_bb_box.py rendered_box.txt
"""
import sys

BOX_CHARS = "┌┐└┘│─"


def check(text: str) -> tuple[bool, list[str]]:
    # Consider only the box lines (rules + content); ignore any prose around it.
    box_lines = [
        ln.rstrip("\n")
        for ln in text.splitlines()
        if ln.strip() and ln.strip()[0] in BOX_CHARS
    ]
    msgs: list[str] = []
    if not box_lines:
        return False, ["no box found (no line begins with a box-drawing glyph)"]

    widths = {len(ln.strip()) for ln in box_lines}
    if len(widths) == 1:
        w = widths.pop()
        return True, [f"box is true: all {len(box_lines)} lines are {w} columns wide"]

    # Mismatch: the majority width is almost certainly the intended one; the
    # outliers are the bug. Report both so the fix is obvious.
    from collections import Counter

    counts = Counter(len(ln.strip()) for ln in box_lines)
    intended, _ = counts.most_common(1)[0]
    msgs.append(f"WIDTH MISMATCH — intended width looks like {intended}; offenders:")
    for ln in box_lines:
        w = len(ln.strip())
        if w != intended:
            msgs.append(f"  {w:>3} cols (off by {w - intended:+d}): {ln.strip()}")
    return False, msgs


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        try:
            sys.stdin.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
        text = sys.stdin.read()
    ok, msgs = check(text)
    print("\n".join(msgs))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
