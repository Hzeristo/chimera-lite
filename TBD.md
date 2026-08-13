# TBD — what is waiting on the Architect

> **Consumer:** the Architect at session start; any agent asking what is unfinished ·
> **Load:** short by design, safe to read whole · **Kind:** descriptive — check the sync date below.

**This file has no authority.** It is a reminder index; every item links to the document that
actually owns it. If this file and its target disagree, **the target is right** — fix this file.

Last synced: **2026-08-12**, at Phase L.C's functional seal.

---

## Blocking a green seal on L.C

Phase L.C is **⚠️ functionally sealed**, not green
([seal review](docs/audits/phase-L.C-seal-review.md)). Two conditions are open, and both need you
doing research — neither can be produced by a build session.

- [ ] **Condition 4 — one authoring session.** Write a T/I/D node in Obsidian while consulting
      something (a W1 verdict, a W2 map, a deep-read node). Then ask for links to be proposed;
      `chimera-propose-links` proposes `informed_by`; you order the apply. That single loop is the
      entire acceptance test for C.4, and it cannot be faked without fabricating provenance.
      → `docs/sprints/phase-L.C/C.4b.md`

- [ ] **Condition 7 — the VISION gate.** Three real research sessions, with friction re-counted in
      the same three registers and set beside the baseline. **If any route got worse, this does not
      seal green** regardless of how the sessions felt.
      → `docs/audits/L.C.1-friction-baseline.md`

- [ ] **Condition 3 — partial, closes on its own.** Route 3's promote half is live; the
      `evidence_base` staging half has never run end-to-end, because the only `[V]` verdict is for a
      paper with no committed K node. It closes the first time a `[V]` lands on a paper that has
      one. Nothing to do but notice when it happens.

---

## Small, and yours because they are judgment or vault-side

- [ ] **`criteria/disposition/_general.md` does not exist.** `chimera-w1-verify` documents it as the
      disposition layer that counters early-stopping and binary snap-verdicts, and `load_criteria`
      degrades to a silent `[no criteria file: ...]` marker rather than complaining. **Every W1
      verdict you have ever produced ran without it.** Writing criteria is your judgment, not the
      repo's. → `docs/sprints/phase-L.C/C.5.md`

- [ ] **An unreviewed `deep_read` node sits in `docs/staging/`** — MemDreamer (2606.07512), from
      C.6's acceptance run. `ascend_node` it or delete it. It is deliberately untracked in git; no
      staged node has ever been committed. → `docs/sprints/phase-L.C/C.6.md`

- [ ] **Vault template sync — check it took.** You synced `informed_by: []` into the vault's own
      `templates/` copies by hand on 2026-08-12. The repo may not touch those files, so nothing here
      can verify it. Worth one glance, because the C.4b measurement says **template presence
      predicts edge population**: `derives_from` (in the template) is filled 15 times,
      `informed_by` (absent) zero.

---

## Repo hygiene — no research required

- [ ] **`CLAUDE.md` is stale.** It lists 5 `chimera-vault` tools; 11 exist. Needs its own pass;
      it was outside the L.C batch's write authority.

- [ ] **Phase L has never been sealed.** Six sprint records, no review, and its VISION gate has
      never been assessed — the parent forgotten under its children.
      → `docs/phases/phase-L.md`

- [ ] **ROADMAP lags the build.** Phases L, Q, K and the codename motif are recorded in their phase
      docs but not fully reflected in `docs/ROADMAP.md` (the file says so itself).

---

## Known-and-deliberate, listed so they are not rediscovered as surprises

These are **not** todos. They are decisions with a recorded home, repeated here only because they
look like bugs to a fresh reader.

- **D-8** — a newly authored agent or skill is unreachable for the turn that authors it; no
  in-process test can assert the live registry. One turn wide, not session-wide.
- **D-1** — supersession is implemented as **deletion**, which I0.4 forbids. Verified by execution.
  Homed to Phase H, currently unhomed in practice.
- **D-5** — eight of fourteen canonical invariants have no mechanical verifier.
- **The staged-patch gate leaves no durable record.** A patch is consumed on apply, so a later
  observer cannot tell a proposed-and-ordered edge from a hand-typed one. Edge-level provenance is
  impossible by construction (D-7); any record belongs at the node level, and that is **Phase K**.

Full and authoritative: [`docs/ARCHITECTURE/ENFORCEMENT_DEBT.md`](docs/ARCHITECTURE/ENFORCEMENT_DEBT.md).
