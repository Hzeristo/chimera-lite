# Phase Codenames — The Dev Motif

> The **development** story only. Production releases carry no motif (there is no
> release version yet). This is the internal arc of the build.

## The arc: from neural horror to epistemology

The predecessor named itself after the **meat of cognition** — `astrocyte` (the Svelte/Tauri
frontend) and `oligo` (the agent loop), both glial cells, brain support-tissue. That was the
neural-horror register: software named for the wet substrate.

The migration (**M**) is the threshold. Everything built *after* the port is named from
**epistemology** — the philosophy of knowing, not the tissue of the knower. The project renamed
itself from the substrate of cognition to the *goal* of cognition as it matured from a bespoke
mechanism into a Claude-native research instrument.

## The grammar (this is the rule, not just a list)

The motif has a hidden grammar. **A phase's letter, relative to M, is a claim about the kind of
work — and that claim selects the name's register.** You can read the intent before you read a
word of the phase.

- **M — the threshold.** The only plain-English name, because M is not a concept but an *event*:
  the passage itself. It earns no Greek term.
- **Forward of M (N, O, P, Q, R, S…) — additive / incremental phases** that *build new capability*.
  Named from **ontology** — the metaphysics of being and essence (Platonic / Aristotelian /
  Scholastic). These names answer *"what does the system now KNOW / possess?"*
- **Backward of M (L, K, J, I…) — refactor / consolidation phases** that reach back and *restructure
  the foundation*. Named from **epistemology** — the Stoic criterion and seat of knowledge. These
  names answer *"is what we hold FAITHFULLY held?"*

Build order is free; **alphabet position is the semantic claim.** The two backward phases (L, K)
were built *after* the forward run (N–R), because the refactor insight came late — but they take
letters before M because they *restructure*, they don't *extend*. Two decisions drove that reverse
growth: (1) *RIP deepseek, welcome subagents* — judgment moved into isolated Claude workers, i.e.
kataleptic fidelity; (2) *lifecycle of research artifacts fully managed by Claude, MCP demoted to a
thin client* — a re-centering of the locus of control. Neither is an increment. Both are refactors.

## The ledger

| Letter | Codename | Register | Direction | Gloss | Status |
|---|---|---|---|---|---|
| **K** | Katalepsis | Stoic epistemology | ← refactor | The *kataleptic impression* — a grasp whose structure guarantees its truth; the Stoic criterion dividing knowledge from opinion. Makes provenance load-bearing, not advisory theater. | Qued (after L) |
| **L** | Locus | epistemology (seat) | ← refactor | The seat, the centralized place of control. Artifact lifecycle pulled fully into Claude; MCP demoted to thin primitives; judgment centralized in W1/W2 subagents. | Active |
| **M** | Migration | — (threshold) | ⟂ pivot | The passage from neural horror to epistemology — the port of oligo+astrocyte onto Claude Code + MCP. The one plain name. | ✅ Sealed 2026-07-03 |
| **N** | Noesis | ontology (Plato) | → additive | Direct intellectual apprehension / insight. The phase that gave the system *insight*: auto-selected research lenses (N.A) + always-on vault observation. (N.B deep-recall cancelled.) | ✅ N.A sealed / ⛔ N.B cancelled |
| **O** | Ousia | ontology (Aristotle) | → additive | Substance / essence / being. The exocortex write surface — `create_node` / `link_nodes` / typed edges — the phase where the vault gained actual substance. | ✅ Sealed 2026-07-08 |
| **P** | Parergon | ontology (the frame) | → additive | The by-work; the frame neither fully inside nor outside the work (Derrida). Fittingly never built — the supplement that stayed a ghost. | ⚪ Never done |
| **Q** | Quiddity | ontology (Scholastic) | → additive | The "whatness," essence-as-definition. `extract_paper` assigns each node its quiddity — the K/T/I/D ontology + citation-grounded edges. | ✅ Re-sealed 2026-07-13 |
| **R** | *(unnamed)* | ontology | → additive | Vault-aware reasoning & tooling completion. A forward phase that dissolved *backward* — absorbed into L before execution. See "Open slots." | ⛔ Retired / absorbed into L |

## Rituals — how the motif stays alive

1. **Name at open = a hypothesis.** When a phase opens, pick its codename from the register its
   direction demands (forward → ontology/essence; backward → epistemology/criterion), and write it
   into the H1 as `# Phase X — Codename: descriptive subtitle`, plus a `## VISION — Why {Codename}`
   stub. The name is a *bet* about what the phase will mean.
2. **Earned meaning at seal = the verdict.** When a phase seals, add one line stating what the name
   turned out to mean once built — the name earns itself in retrospect. (Quiddity earned it:
   `extract_paper` literally assigns each node its "whatness." Katalepsis earns it if provenance
   becomes load-bearing.) A name that *can't* be earned is a signal the phase drifted.
3. **The H1 convention is the contract.** Every phase file's H1 = `Phase X — Codename: subtitle`.
   Retired/cancelled phases keep the name struck-through with the retirement note; ghosts (P, and
   R until decided) stay ghosts.
4. **Branch = letter.** Branches are already `phase-L`, `phase-K`; the letter is the git spine.
   This is why the codename never needs to enter a commit message — the letter already carries it.
5. **This file is the index.** One source of truth for the motif. Link it from `docs/ROADMAP.md`
   and `CLAUDE.md`.

## Open slots

- **R** — the forward phase that dissolved backward into L. Currently a ghost. Two honest options:
  (a) leave it nameless, like P — a forward letter that never earned its essence-name; or
  (b) name it from the ontology register with a term that fits its actual content (vault-aware
  *reasoning*) — candidate: **Ratio** (the reasoned account of a thing). Decision deferred to the
  Architect.
- **ROADMAP sync** — `docs/ROADMAP.md` still lists phases by their old descriptive headers
  (`### Phase N.A — Lens Skills`). Prepending codenames there would make the index consistent with
  the phase files. Not yet done.
