# TBD — what is waiting on the Architect

> **Consumer:** the Architect at session start; any agent asking what is unfinished ·
> **Load:** short by design, safe to read whole · **Kind:** descriptive — check the sync date below.

**This file has no authority.** It is a reminder index; every item links to the document that
actually owns it. If this file and its target disagree, **the target is right** — fix this file.

Last synced: **2026-08-13**, after the L.D design discussion.

**Vault inventory at that date:** 17 converted papers · **3** Knowledge nodes · 6 W1 verdicts ·
2 W2 maps · 10 hand-authored T/I nodes · staging empty. The binding constraint is extraction depth,
not paper supply — and `evidence_base` still has **0** live instances, which is what Phase K.1's
monotonicity gate would need to read.

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

- [x] ~~An unreviewed `deep_read` node in `docs/staging/`~~ — MemDreamer (2606.07512) **ascended
      2026-08-12** on the Architect's order. `Knowledge/` is now 3 nodes; staging is empty.

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

## Decided in design, waiting for Phase L.D

Reached in discussion 2026-08-13 and recorded so the reasoning is not re-derived. `phase-L.D.md`
does not exist yet; this is input for it, not a plan.

- [ ] **Gaps attach to claims as a thin object — not a parallel section, and not an edge.**
      Promote `ClaimFlag` from a bare enum to `{kind, statement, what_would_fill_it}`.

      **Why not an edge.** An edge relates two *existing* nodes; a gap is the absence of one, so
      there is nothing to point at. That is why `dead_ends` has been legal for months and sits at
      **0** vault-wide, while `flags` — the same information as an attribute — is populated 3 times
      in a single node. K therefore does **not** need `dead_ends` added, and `_TYPE_EDGES` does not
      move.

      **Why not a parallel `G01…G0N` section.** A K node is already 203 lines / ~4.4K tokens with
      claims at 33%. A matching gap section pushes it to ~6K, and five nodes in one query to 30K —
      "context is the load" inside the vault. The gaps also already attach to specific claims in
      practice (`suspicious_dependency` on C01, `no_ablation` on C03 and C04).

      **It pays for itself.** Fixing `friction-260813-01` (drop `status_note`, cap titles) frees
      ~190 words per node — about what the gap fields cost. Net-flat node size.

- [ ] **Still unhoused: the cross-paper gap.** W2 produces "nobody in this subfield does X," which
      belongs to no single K node and has no home under the above. Deliberately left open — its
      shape cannot be known until frequency data exists, and frequency is the thing that separates
      a gap worth recording from noise. Related: a gap seen once is an *observation* (candidate
      tier); a gap seen across N papers is a *finding* (committed, Architect-promoted) — the same
      two-clock structure the formal model already uses.

- [ ] **Claim status `[H]/[S]/[R]` and W1's `[V]/[P]/[U]` stay two axes, not one.** Maturity (is
      this mechanism established?) versus attestation (does the cited text assert it?). They
      diverge usefully: `[V]` + `[H]` means "the paper says it clearly and has not earned it," and
      `[U]` + `[S]` is a fabrication alarm. They are also not mappable — W1 has no `refuted`, since
      `[U]` is absence of evidence rather than evidence of absence.

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
