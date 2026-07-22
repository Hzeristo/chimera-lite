#!/usr/bin/env python
"""Verify a BB box: every line — top rule, content, bottom rule — is one width.

Why this exists: bb_box.py renders a correct box, but the box only *stays*
correct if it's copied out verbatim. The observed failure mode is subtle — the
64-char content lines get copied faithfully while the top/bottom ─── rules get
re-typed from habit at a shorter width (a memorized "standard box" prior). The
result reads fine at a glance yet the frame is 34 cols where the body is 68.

So this checker treats the box as data, not eyeballs it: it reads the box you
are about to ship and asserts all box lines share one display width. It exits 0
and says so when the frame is true; it exits 1 and points at the offending
lines when a rule (or a stray content line) drifts. Run it on the final box
before sending — if it fails, re-render with bb_box.py and copy the WHOLE thing.

Usage:
    python check_bb_box.py < final_answer_box.txt
    python check_bb_box.py final_answer_box.txt
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
