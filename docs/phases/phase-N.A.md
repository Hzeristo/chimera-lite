# Phase N.A — Lens Skills

**Status:** ✅ Sealed 2026-07-06 — all 3 HSC met (auto-select · academic-taste · proactive-observe); 7 pure prompt skills, zero MCP changes. Seal: `docs/plans/Phase-N.A-batch.md`, `docs/sprints/phase-N.A/*.md`.
**Driving frictions:**
- friction-chimera-lite-01: lens skills don't exist in chimera-lite(project_chimera had them as OpticsService prompts, not Claude Code skills)
**Sealed predecessor:** Phase M (chimera-lite migration)

## Mission

Crystallize the6 research analysis lenses as Claude Code skills.
Enable Claude's native skill discovery to auto-select the appropriate
lens by paper type. Academic taste built into each lens (mechanism /
evidence / falsifiability required in all outputs).

## Sprint Sequence

| Sprint | One-line goal |
|---|---|
| N.A.0 | Audit: read the6 original lens configs from project_chimera archive + lens-related skills in ~/.chimera |
| N.A.1 | Forensic Leakage Audit skill + Thermodynamic Decay Probe skill |
| N.A.2 | State Collision StressTest + Agentic Illusion Stripper |
| N.A.3 | Math Decoration Validator + Ontological Map Scanner |
| N.A.4 | chimera-academic-observe skill (proactive academic thoughts) |

## Hard Sealing Conditions

1. All 6 lens skills have `description:` that enable Claude to auto-select
   by paper type (no manual /lens-name invocation required)
2. Each lens requires mechanism + evidence + falsifiability in output
3. chimera-academic-observe proactively surfaces connections to vault nodes
   without being asked

## Design Decisions

- Lens skills are PURE PROMPT SKILLS — no new tools, no MCP changes
- academic-observe is always-on (like bb-persona), lenses are trigger-based
- North star (multi-source synthesis) is NOT a separate phase — it emerges
  from N.A.1-4 + Claude Code's native parallel tool-calling
