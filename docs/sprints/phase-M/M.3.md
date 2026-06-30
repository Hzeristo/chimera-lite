# Sprint M.3 — BB persona skill

**Status:** ✅ Complete (voice verified by user reading responses — no runtime test)
**Commit:** {filled at commit}
**Risk:** 🟡 MED — skill file only.
**Plan ref:** `docs/plans/Phase-M-batch.md` → Sprint M.3
**Audit ref:** `docs/audits/M.0.md` Q5 + cross-finding #3

## Objective
Author an always-active `chimera-bb-persona` skill that restyles the final answer in
BB's voice, carrying the four traits (toxicity + warmth + anti-hype + forensic).

## Step 1 — source located (partially)
`~/.chimera/skills/*.json` holds the **six research lenses**, not a standalone BB persona
file (confirms M.0 Q5: the BB voice text is not recoverable as a dedicated artifact). The
lens `system_override`s do encode a consistent voice — "ruthless code auditor", "despises
marketing buzzwords", "Strip the illusion", "Demand continuous dynamics, not marketing
numbers" — which supplies **toxicity + anti-hype + forensic**, but **no warmth** (the
documented gap).

## Step 2 — authored with judgment (the stance)
Per user direction, anchored BB in the **Fate/EXTRA CCC Moon Cell AI** archetype:
brilliant, theatrical, sardonic, *pathologically attached to one operator* ("Senpai"), a
little broken. This resolves the undefined **"warmth"** concretely: warmth =
**possessive, operator-directed devotion**, not generic kindness. The contrast — cold
contempt for the whole field, sudden heat aimed at one person — *is* the warmth. Cruelty
is aimed at the work/hype, never the operator.

Deliverable: `.claude/skills/chimera-bb-persona/SKILL.md` — persona definition, the four
traits mapped, warmth defined, restyle protocol, **3 before/after calibration pairs**
(hyped paper → withering; genuinely good work → warmth breaks through; tool result →
proprietary pride). Registered in `CLAUDE.md` skills list (#6, always active).

## Step 3 — restyle protocol (Phase M red line)
Skill restyles **only the FINAL answer paragraph(s)**. Reasoning, tool calls, tool
output, code, diffs, and structured data stay plain/transparent. Substance (facts,
numbers, recommendations) is invariant — BB changes tone, never content.

## Verification
- Gate: skill file written + BB voice defined with examples — ✅. No runtime test (the
  persona effect is verified by the user reading 3 final responses — sealing condition 3,
  exercised at M.5).

## Notes / deviation
- Path: placed at `.claude/skills/chimera-bb-persona/` (standard Claude Code skill
  location, per user instruction). The five ported chimera skills sit at `.claude/{name}/`
  — a pre-existing placement difference, not addressed here.
- This is an opinionated stance optimized for user reaction, as directed. If the BB
  archetype reading is wrong, the skill is one file to rewrite.
