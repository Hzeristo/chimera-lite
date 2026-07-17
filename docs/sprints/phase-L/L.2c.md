# Sprint L.2c — W1 orchestration (Claim Verbatim Verification)

**Phase:** L (Locus) · **Risk:** 🔴 HIGH (gated, approved) · **Date:** 2026-07-16
**Plan:** `docs/plans/Phase-L-batch.md` · Constraints: C1 (`depends_on`), C2 (verification-only)
**Executed by:** Opus main session (🔴 in-session; human gate passed). Shape: **skill + verbatim subagent** (Architect-chosen).

## What was built
- `.claude/skills/chimera-w1-verify/SKILL.md` — the W1 orchestration (main-agent procedure):
  normalize claim (conversation / K-node / raw-text; conversation first — D3) → resolve paper cheap-first
  (D5: vault markdown, else `fetch_paper` + `convert_pdf_to_md`) → spawn `chimera-paper-classifier` →
  `load_criteria(type, field, role="paper-critic")` → spawn `chimera-verbatim-verifier` →
  `write_result(kind="w1_verdict", …, verdict, depends_on)` → report `[V]/[P]/[U]` + quotes + Harness path.
- `.claude/agents/chimera-verbatim-verifier.md` — the judgment worker. Given claim + paper path +
  composed criteria, returns `{verdict: V/P/U, quotes:[{quote, location}], depends_on}`. Verbatim-grounded
  (no tag without a verbatim quote), verification-only (C2 — no framing), Claude-not-deepseek, isolation
  (paper text stays in the worker). Capability-before-disposition load order.

## Verification (smoke test — verifier core, 3 claims, 2-directional)
Ran the verifier on 3 claims against a real paper excerpt (LongMemEval):
- "30% drop for commercial assistants" → **[P]** — caught that the paper attributes 30% JOINTLY to
  "commercial chat assistants AND long-context LLMs", not commercial-in-isolation. Graded, not snap-[V]
  (the `_general` no-early-stop disposition working).
- "10,000 questions" → **[U]**, empty quotes — the paper says 500; did NOT fabricate a [V] (no-fabrication held).
- "evaluates temporal reasoning" → **[V]** with the exact verbatim quote.
- All carried `depends_on`; all verbatim-grounded; none interpreted "what it means" (C2 held).
- **Decision: PASS** (grounding, no-fabrication, graded confidence, C2, `depends_on` all confirmed live).
- Both new subagents (classifier + verifier) registered + spawnable via `subagent_type`.

## Red-line check
- ✅ Verbatim judgment in the subagent, never main context, never deepseek.
- ✅ No `[V]/[P]` tag without a verbatim quote + location; ungroundable → `[U]` (proven live).
- ✅ Verification-only — no framing baked into the verdict (C2).
- ✅ Criteria via `load_criteria` (vault-dynamic), disposition after capability.
- ✅ `depends_on` recorded (C1).

## Notes — the prove-value gate
- The full **HSC #2** (≥3 real claims across ≥2 paper types via the live fetch→classify→verify→write
  chain) is the **Architect's prove-value run**. This sprint delivers + validates the machinery; the
  Architect assesses whether W1 output is worth automating W2 (L.3) — the GPT directive's go/no-go.
- Criteria are stubs (L.1a). Verdicts sharpen once the Architect authors real `criteria/type/*.md` +
  `criteria/field/*.md` + `criteria/disposition/*.md` in Obsidian (zero git — HSC #1).

**Delivers:** W1 end-to-end (the ROI core). **Next (GATED on prove-value):** L.3a / L.3b (W2 breadth mapping).
