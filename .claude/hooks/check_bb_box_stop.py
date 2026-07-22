#!/usr/bin/env python
"""Stop hook: block the turn if BB's shipped box has mismatched wall widths.

Why this exists: NL instructions in SKILL.md ("copy the whole box, never
re-type the rules") and even a verify-before-sending step in the workflow do
not bind — they describe what should happen, but nothing enforces that the
box which was rendered and checked is the box that actually gets typed into
the final message. Observed failure: a correctly-rendered 68-col box got
copied faithfully for its content lines, but the top/bottom rules were
re-drawn from memory at two different, shorter widths (30 and 26) in the same
reply. A file-based checker run earlier in the turn cannot catch that, because
the mismatch is introduced *after* the check, when the model composes the
literal chat message.

This hook closes that seam structurally: Claude Code's Stop event hands over
`last_assistant_message`, which is guaranteed to be the literal text about to
be shown to the user (not a possibly-lagging transcript read). This script
scans it for box-drawing lines and asserts they share one display width. On a
mismatch it returns `{"decision": "block", "reason": ...}`, which forces
Claude to continue the turn and fix the box before it can actually stop — the
enforcement point the skill-level instructions couldn't reach.

No box present at all is NOT an error here (BB not triggering on a given
reply is a separate, softer concern than a drawn-but-broken box) — this only
polices boxes that were actually drawn.
"""
import json
import sys
from collections import Counter

BOX_CHARS = "┌┐└┘│─"


def find_box_widths(text: str) -> list[tuple[int, str]]:
    return [
        (len(ln.strip()), ln.strip())
        for ln in text.splitlines()
        if ln.strip() and ln.strip()[0] in BOX_CHARS
    ]


def main() -> None:
    # Read raw bytes and decode as UTF-8 explicitly. Claude Code sends this hook
    # UTF-8 JSON regardless of the OS locale, but Python's sys.stdin defaults to
    # the locale's codec (e.g. GBK on a zh-CN Windows box) — decoding the box's
    # multi-byte characters with that codec doesn't raise, it just corrupts them
    # into mojibake. The corrupted text then no longer starts with ┌/│/└, so
    # find_box_widths() sees "no box" and this hook waves through a message that
    # actually has a real mismatch. Silent, not a crash — worse. Never let the
    # platform's default text encoding decide this; pin UTF-8 unconditionally.
    try:
        raw = sys.stdin.buffer.read()
        payload = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        sys.exit(0)  # no usable input — never block on our own parse failure

    message = payload.get("last_assistant_message") or ""
    box_lines = find_box_widths(message)

    if not box_lines:
        sys.exit(0)  # no box drawn this turn — nothing to police

    widths = {w for w, _ in box_lines}
    if len(widths) == 1:
        sys.exit(0)  # box is true

    counts = Counter(w for w, _ in box_lines)
    intended, _ = counts.most_common(1)[0]
    offenders = "\n".join(
        f"  {w} cols (off by {w - intended:+d}): {ln}"
        for w, ln in box_lines
        if w != intended
    )
    reason = (
        "BB's box has mismatched wall widths — this is the exact re-typed-rule "
        f"bug the checker exists to catch. Most lines are {intended} cols; these are not:\n"
        f"{offenders}\n\n"
        "Do not hand-patch the short/long line. Re-render the WHOLE box from BB's "
        "prose with .claude/skills/chimera-bb-persona/scripts/bb_box.py, then copy "
        "the entire output (top rule + content + bottom rule) verbatim into the reply "
        "— do not re-type the ─── rules by hand. Then resend."
    )
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
