# Phase Audit: Phase N.A — Lens Skills

**Scope:** Read-only audit prerequisite for `batch_planning` of Phase N.A (crystallize the 6
research-analysis lenses as Claude Code skills + `chimera-academic-observe`).
**Output location:** `docs/audits/N.A.0.md` (named for the N.A.0 sprint that authors it).
**Date:** 2026-07-04
**Mode:** Read-only w.r.t. source — no fix proposals, no code changes. The one write is this report.
**Q-list:** approved by user (2026-07-04). `~/.chimera` source: user opted to paste but did
not supply it this session; answered from in-project evidence + the prior extraction in
`docs/sprints/phase-M/M.3.md`. The divergence check against the real `~/.chimera/skills/*.json`
is left OPEN (see cross-finding 5).

---

## Files read

| Path | Lines | Notes |
|---|---|---|
| `docs/phases/phase-N.A.md` | 1–39 | full — phase intent, 6 target lens names, sealing conditions |
| `mcp-servers/chimera-papers/optics_lens_registry.py` | 1–255 | full — 6 builtin `LensConfig`s (3 paper + 3 survey) |
| `mcp-servers/chimera-papers/optics_service.py` | 1–261 | full — `irradiate`, `SCHEMA_REGISTRY`, `DeepReadAtlas` assembly |
| `mcp-servers/chimera-papers/core/schemas.py` | 145–273 | grep — `LensConfig` + 6 extraction models + `DeepReadAtlas` |
| `mcp-servers/chimera-papers/core/config.py` | 1, 57–60, 131–138, 283–286, 393–399, 445–449 | grep — `lenses_dir` resolution to `~/.chimera/lenses` |
| `prompts/tasks/optics/method_scalpel.j2` | 1–21 | full — Decompiler + **Agentic Reality Check (Plumbing Audit)** |
| `prompts/tasks/optics/eval_scalpel.j2` | 1–14 | full — **ruthless Forensic Auditor** (LLM-as-Judge bias, mock-vs-streaming) |
| `prompts/tasks/optics/synthesis.j2` | 1–10 | full — `reproduction_risks` |
| `prompts/chimera_sys/user_profile.j2` | 1–32 | full — research stance; **Big Three Diagnostic Targets** + Falsifiability Check |
| `docs/sprints/phase-M/M.3.md` | 1–40 | lines 1–40 — `~/.chimera/skills/*.json` lens source note |
| `.claude/skills/chimera-bb-persona/SKILL.md` | scout | anti-hype principle + always-on trigger pattern |
| `mcp-servers/chimera-vault/server.py` (+ `vault_read_adapter.py`, `vault_query.py`) | scout | vault tool surface / graph-query capability |

---

## Findings

| Q# | Driving sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| Q1 | N.A.1 | Ancestor of **Forensic Leakage Audit**? Leakage/contamination checks present? | Yes — `eval_scalpel.j2` "ruthless Forensic Auditor" already exposes LLM-as-Judge self-enhancement bias, mock-vs-streaming, asymmetric prompting; sharper than the wired `eval_rigor`. | `prompts/tasks/optics/eval_scalpel.j2:2-11`; `optics_lens_registry.py:100-110` | Low |
| Q2 | N.A.1 | Ancestor of **Thermodynamic Decay Probe**? Falsifiable decay probe or descriptive? | Concept named as "Temporal Decay… across long, high-entropy interaction horizons"; `memory_physics` supplies `forgetting_mechanism`. Descriptive today; probe/falsifiability not operationalized. | `user_profile.j2:11`; `schemas.py:186-206`; `optics_lens_registry.py:111-123` | Low |
| Q3 | N.A.2 | Ancestor of **State Collision StressTest**? Or net-new? | Concept PRESENT as stance criteria ("State Overwrite", "Cognitive Inertia") + `memory_physics` "overwrites", but NO operationalized lens. The one target with no wired registry ancestor — author fresh from the stance vocabulary. | `user_profile.j2:12-13`; `schemas.py:192` | **Med** |
| Q4 | N.A.2 | Ancestor of **Agentic Illusion Stripper**? Or net-new / overlaps bb-persona? | Yes — `method_scalpel.j2` "AGENTIC REALITY CHECK (Plumbing Audit)": "be explicitly critical if the 'agent' is really a one-shot API call". Reinforced by M.3 source material and bb-persona anti-hype. Strong operational ancestor. | `prompts/tasks/optics/method_scalpel.j2:9-13`; `docs/sprints/phase-M/M.3.md:17`; `chimera-bb-persona/SKILL.md:41` | Low |
| Q5 | N.A.3 | `math_arch` extracts math; does the **Math Decoration Validator** judgment (load-bearing vs decorative) exist? | Partial — extraction present (`math_arch` + `method_scalpel.j2` Obj 1); the *validation* stance exists separately ("value grounded modeling over boilerplate; EXPOSE if it only scales context without true dynamics"). Must fuse judgment onto extraction. | `optics_lens_registry.py:86-98`; `user_profile.j2:24-25` | Med |
| Q6 | N.A.3 | `survey_taxonomy` emits categories; does **Ontological Map Scanner** need relations/axes (a map)? | Partial — `survey_taxonomy` already emits `classification_axes` + architectural-bound distinctions (more than a flat list); the inter-concept **edges** ("map") are the delta. Stance: "opinionated Taxonomy / Architectural Metacognition". | `optics_lens_registry.py:129-143`; `schemas.py:208-223`; `user_profile.j2:27-31` | Low |
| Q7 | N.A.4 | Precedent for proactive always-on academic observation? Which always-on pattern? | PARTIAL — planned, not implemented; no existing proactive-observation system (inspiration/random-walk is speculative Phase-IV Horizon, deferred). Pattern = bb-persona: universal trigger in `description:` + act-on-every-output body. | `phase-N.A.md:23,30-31`; `chimera-bb-persona/SKILL.md:3`; `ROADMAP.md` Horizon | **Med** |
| Q8 | N.A.4 | Which vault MCP tools surface node connections, staying pure-prompt / no MCP changes? | YES with existing tools — `obsidian_graph_query` (BFS over wikilinks + `graph_edges`, depth 1–8) and `vault_query` (`linked_to` → `graph_edges` match). No MCP changes needed (red line safe). | `chimera-vault/server.py:87,106`; `vault_read_adapter.py:442-544`; `vault_query.py:74` | Low |
| Q9 | all | Which academic-taste requirements (mechanism/evidence/falsifiability) are present vs to-add? | Mechanism + evidence partially present per-lens; **falsifiability is centralized** in `user_profile.j2` "The Falsifiability Check", NOT in any per-lens registry prompt. Each new lens skill must embed it (sealing condition 2). | `user_profile.j2:21-25`; `optics_lens_registry.py:84-169` | Med |
| Q10 | all | Authoritative source to port from? Consistent? | In-project authoritative = `optics_lens_registry.py` builtins (wired → `DeepReadAtlas`) + `user_profile.j2` (names the targets). `prompts/tasks/optics/*.j2` = UNWIRED alternates with DIFFERENT schemas (richer tone). Out-of-project = `~/.chimera/skills/*.json` + `~/.chimera/lenses/*.yaml` — not supplied; M.3 already extracted their voice. | `optics_lens_registry.py:84-169`; `eval_scalpel.j2:2-3`; `M.3.md:14-18`; `config.py:395-396` | **Med** |

---

## Cross-references discovered

- **`user_profile.j2` "Big Three Diagnostic Targets"** (Temporal Decay / State Overwrite /
  Cognitive Inertia) is the naming source for 3 of the 6 target lenses. Evidence:
  `prompts/chimera_sys/user_profile.j2:9-13`.
- **Two parallel in-project lens prompt families:** wired registry builtins (structured JSON
  schemas) vs unwired `*.j2` scalpels (richer forensic tone, incompatible schemas). Evidence:
  `optics_lens_registry.py:84-169` vs `prompts/tasks/optics/{method_scalpel,eval_scalpel,synthesis}.j2`.
- **`DeepReadAtlas` has exactly 6 lens slots** (`math_arch`, `eval_rigor`, `memory_physics`,
  `taxonomy`, `consensus_bottlenecks`, `structural_gaps`). Evidence:
  `optics_service.py:171-198`; `schemas.py:262-273`.

---

## Notable cross-findings (no fix proposals — flagging for planning)

1. **The 6 targets are NOT a 1:1 rename of the 6 registry lenses.** The registry splits 3 paper
   + 3 survey; the N.A targets are 6 paper-analysis lenses auto-selected *by paper type*.
   `survey_consensus` and `survey_gaps` have no direct target equivalent — they likely consolidate
   under Ontological Map Scanner (map/survey papers) and/or fold into Agentic Illusion Stripper
   (bottleneck exposure). **Batch planning must decide the survey-lens disposition; do not assume a
   clean 6→6 port.** Evidence: `optics_lens_registry.py:127-168`; `phase-N.A.md:20-23`.

2. **Falsifiability is centralized, not per-lens.** The requirement (sealing condition 2) lives once
   in `user_profile.j2:21-25`, absent from every registry lens prompt. A shared academic-taste
   fragment (candidate for `.claude/skills/_shared/`) embedded into all 6 lens skills is the natural
   enforcement mechanism. Evidence: `user_profile.j2:21-25`.

3. **The sharper voice lives in the UNWIRED `.j2` scalpels + `~/.chimera`, not the wired registry.**
   `eval_scalpel`/`method_scalpel` carry the forensic/plumbing-audit edge the target names imply,
   but they are not used by `OpticsService` and use different schemas. Lens skills should draw
   *tone* from the `.j2` scalpels + M.3-extracted `~/.chimera` voice, *structure* from the registry
   schemas. Evidence: `prompts/tasks/optics/eval_scalpel.j2`, `method_scalpel.j2`; `M.3.md:14-18`.

4. **`academic-observe` is behaviorally net-new but infrastructure-ready.** No proactive-observation
   precedent exists, yet the vault graph tools (`obsidian_graph_query`, `vault_query`) already
   support connection-surfacing with zero MCP changes. The risk is **trigger design** (always-on
   without being noisy), not capability. Evidence: `chimera-vault/server.py:87,106`; `phase-N.A.md:30-31,36`.

5. **`~/.chimera` source not supplied this session.** The spec's N.A.0 names "lens-related skills in
   `~/.chimera`" (`~/.chimera/skills/*.json` per `M.3.md:14`; `~/.chimera/lenses/*.yaml` per
   `config.py:395`). Both are out-of-project (the no-external-files boundary). The in-project registry
   + M.3's prior extraction cover the essentials, but a **divergence check against the actual
   `~/.chimera/skills/*.json` remains OPEN** — fold into N.A.1 or accept as a documented partial.
   Evidence: `docs/sprints/phase-M/M.3.md:14-18`.

---

## Tentative old → new lens mapping (evidence-anchored; batch planning confirms)

| Target lens (N.A) | Primary in-project ancestor(s) | Wired registry lens | Disposition |
|---|---|---|---|
| Math Decoration Validator | `method_scalpel.j2` Obj 1 + `user_profile.j2:24-25` | `math_arch` | port + fuse validation judgment |
| Forensic Leakage Audit | `eval_scalpel.j2` | `eval_rigor` | port (scalpel is the sharp ancestor) |
| Thermodynamic Decay Probe | `user_profile.j2:11` "Temporal Decay" | `memory_physics` | port + reframe as probe |
| State Collision StressTest | `user_profile.j2:12-13` (Overwrite + Inertia) | — (none) | **author fresh** from stance vocabulary |
| Agentic Illusion Stripper | `method_scalpel.j2:9-13` "Plumbing Audit" | — (none) | port from `method_scalpel` Obj 2 |
| Ontological Map Scanner | `user_profile.j2:27-31` + `survey_taxonomy` | `survey_taxonomy` (+ consensus/gaps?) | port + add inter-concept edges; absorb survey lenses |

---

## Audit complete

- 10 questions answered
- ~30 `file:line` references
- 3 cross-references
- 5 notable cross-findings (+ tentative 6-lens mapping table)

**Suggested next:** `batch_planning` for Phase N.A — sprint tasks for N.A.1–N.A.4, resolving the
survey-lens disposition (cross-finding 1), the shared falsifiability fragment (cross-finding 2),
the tone-vs-structure source split (cross-finding 3), and the `academic-observe` trigger design +
`~/.chimera` divergence check (cross-findings 4–5).

---

*Generated by chimera-sprint-discipline phase_audit mode.*
