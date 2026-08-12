# Chimera-Lite Invariants

Architect-authored canonical. Three tiers by mutability. Tier 0 is absolute.
Tier 1 requires strong justification to change. Tier 2 is a mutable choice,
documented on change. Below the tiers: an explicit non-invariant list.

---

## Tier 0 — Epistemic Invariants (absolute; violation = no longer L2)

### I0.1 — Human-Time Supremacy
Truth advances exclusively on human-time. Machine-time accumulates candidates;
human-time commits truth.

**Violation:** any code path that advances committed status without an
Architect-initiated action. This is the definition of L2 — violating it means
the system is no longer L2.

### I0.2 — Provenance Load-Bearing
Verification tags ([V]/[P]/[U]) are structural gates, not advisory suggestions.
Monotonicity (a synthesis's status ≤ the minimum status of its dependencies)
**MUST BE pipeline-enforced**. This is a structural target, not a descriptive
claim of current state.

**Violation:** a tag that only performs rigor while downstream reasoning ignores it.
"Advisory rigor" is the failure mode this exists to prevent.

**Current status:** monotonicity is not yet enforced — see ENFORCEMENT_DEBT.md R5b.

### I0.3 — Verification Tier-Separation
No single verifier assesses truth, novelty, and importance simultaneously.
Each requires a different grade of independence: factual truth via verbatim
grounding, novelty via bounded witness search, significance via human judgment
(no independent verifier exists).

**Violation:** treating one verification type as a proxy for another. Conflation
produces systematic attribution errors.

### I0.4 — Append-Only with Supersession
Committed nodes are never deleted, only superseded and marked STALE.
Provenance decay propagates STALE downstream: when a source node is superseded,
nodes depending on it become STALE and require human re-evaluation.

**Violation:** rewriting or deleting committed history. Truth revision happens by
supersession, not erasure.

**Current status:** provenance decay not yet implemented — see ENFORCEMENT_DEBT.md.

### I0.5 — Judgment vs Evidence Authorship
Judgment-type nodes (T/I/D) have Architect-authored bodies. Evidence-type nodes
(K) may be AI-authored, then human-committed.

**Distinction:** I0.1 governs commitment (human settles truth). I0.5 governs
authorship. A promoted AI-written K node satisfies I0.1 while its body is not
Architect-authored — legal. A T/I/D node with an AI-written body violates I0.5 —
illegal, even if promoted.

AI outputs may inform a T/I/D node; provenance records `informed_by` (I2.2),
never `derives_from`, and never substitutes for authorship. An informed_by edge
documents the tool used; it does not transfer authorship.

---

## Tier 1 — Architectural Invariants (change requires strong justification)

### I1.1 — MCP Primitives Make No Judgment
MCP servers fetch, read, write, and convert. They never invoke an LLM for
judgment **by any route** — client construction, host sampling
(ctx.session.create_message / ctx.sample), or any other delegation. The
prohibition is on judgment **location** (inside a tool call), not on client
construction. Judgment lives in skills orchestrating subagents.

**Violation:** structural collapse. An MCP-internal verdict is the boundary this
system exists to hold.

### I1.2 — Staging Gate Universality
AI-authored Knowledge node enters a staging buffer 
before any committed tier. Promotion into the committed tier passes through a
single gate (ascend_node), which is the sole writer of the committed tier.

**Violation:** any writer other than the ascension gate reaching the committed tier.
This is what makes the human gate structural rather than conventional.

### I1.3 — Proof Graph, Not Computation Graph
The research artifact is a proof graph: nodes carry claims and judgments, edges
carry support relations. A node's truth is determined by the traversability of
its support chain, not by reduction of a term. Normal form is honest provenance
(a support chain traceable to Tier-1 evidence, or an explicitly documented weak
tag), not full reduction.

**Consequence:** [P]/[U] have no computational value by design — they annotate
support-chain weakness and trigger human review; they do not participate in
automatic combination. This is L2's stance: computation is machine-side,
judgment is human-side.

**I-node support requirement:** an I-node's well-formed support chain requires
verified T-node groups. The synthesis must rest on a set of T-nodes, each
grounded (per I0.2) and confirmed (per I0.1 human commit). An I-node derived
from unverified T-nodes violates normal form.

### I1.4 — Three Consumption Routes, Equal Friction
Three routes from candidate material to committed artifact must carry equal
friction: (1) pure observation (read a paper, write a T-node, zero AI),
(2) AI-assisted (read original + AI outputs, author T/I informed by both),
(3) batch-promote (review [V] claims, promote). The system augments; it never
nudges toward or away from AI.

**Violation:** any feature that smooths one route while adding ceremony to another.
This is the formal meaning of "augmentation, not replacement."

### I1.5 — Tier Existence
A tier stratification must exist: candidate material and committed truth are
structurally distinguishable at all times.

**Violation:** any state where an observer cannot mechanically tell a candidate from
committed truth. The existence of stratification is architectural; the specific
tier values (I2.1) are not.

---

## Tier 2 — Implementation Choices (mutable; document on change, justify against Tier 0/1)

### I2.1 — Node Types and Tier Values
The current committed-node sort $S_c = \{\mathtt{K}, \mathtt{T}, \mathtt{I}, \mathtt{D}\}$
and tier value set $\{$scout, deep_read, harness_candidate, synthesis$\}$ are mutable
choices. Node types may be added; tier values may be added, merged, or renamed.
The stratification itself (I1.5) and the committed/harness sort distinction may not.

**Changes** documented in NODE_ONTOLOGY.md and justified against Tier 0/1.

**Current harness-artifact sort:** $S_h = \{\mathtt{W1}, \mathtt{W2}\}$ (tracked in
NODE_ONTOLOGY.md, not elevated to committed-node status).

### I2.2 — Edge Types
The current edge vocabulary $\{$derives_from, supersedes, contradicts, dead_ends,
drives_decision, synthesizes, evidence_base, collides_with, informed_by$\}$ is mutable.
Edges may be added or merged, subject to: **support-bearing edges** (evidence_base,
synthesizes, derives_from) must remain structural (auto-written, traversable) per I0.2.

**Changes** documented in NODE_ONTOLOGY.md.

**Support-bearing edges:** monotonicity (I0.2) propagates along these. informed_by
is not support-bearing — it records a tool context, not a dep`endency.

### I2.3 — Dual-Clock Implementation
The current implementation (docs/staging/ and vault/Harness/ as machine-time
buffers; promote / ascend_node as the human-time action) is a mutable choice.
The mechanism may change (e.g., CRDTs), provided human-time supremacy (I0.1)
remains mechanically verifiable.

**Status vocabulary crosswalk** (abstract ↔ concrete, see NODE_ONTOLOGY.md §7.2):
- candidate ↔ unverified (scout-tier inbox nodes)
- staged ↔ PENDING_REVIEW (staging/ and Harness/)
- committed ↔ active (base state)
                / cross_verified (I-node substate after advisor confirmation)
- stale ↔ (not yet implemented; see ENFORCEMENT_DEBT.md)

### I2.4 — Criteria Externalization
The current placement (criteria/*.md in the vault, effective immediately, zero-git)
is a mutable choice. The mechanism may change, provided the property it implements
holds: criteria are Architect-controlled and do not depend on the code release
cycle (an implementation of I1.4).

---

## Non-Invariants (may be discarded at any time)

The following are neither Tier 0, 1, nor 2. They carry no protection. Do not
defend them on grounds of history or prior investment:

- The form of a W2 breadth map as a persistent artifact
- The "Phase Q sealed" historical status of extract_paper
- The "independent observer" framing of T-nodes (they are observations,
  possibly AI-informed, authored by the Architect — the framing is not load-bearing)
- Any specific number ("20 papers", "3 subfields") as an HSC gate
- Any hardcoded literal (e.g., INGESTION_PATHS)
- The specific wording in prompts/ (only the semantic correspondence to Tier 0/1 matters)
- The field order in .j2 templates
- The function names of MCP tools (only the thin-adapter principle holds)

**Git history is not an invariant.** The phase in which something was built is not
an architectural fact. When a change preserves Tier 0/1, it is a legal evolution,
not a violation — regardless of what it discards.
