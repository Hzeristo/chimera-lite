# Lens: Ontological Map

## Trigger (function-based)
Apply when the paper FUNCTIONS as a field-mapping claim — it surveys, reviews, or stakes a
position across a body of prior work rather than reporting its own raw experiments, and asks
the reader to accept its organization of the field as useful. Do not apply merely because the
paper cites many other papers; apply because the paper's contribution IS the organization it
imposes on the field. Do not apply to the paper-analysis lenses (forensic-leakage,
thermodynamic-decay, state-collision, agentic-illusion, math-decoration) — those target a
single paper's own claims, not a field.

## Method
Read the paper AS a map, not as a table of contents. Judge it on Architectural Metacognition,
not on math: an opinionated, architecturally-grounded taxonomy is high value; a lazy SOTA
laundry list (enumerate every model in the space with no distinguishing structure) is low
value, regardless of how many papers it cites.

Produce ONE consolidated map with these five dimensions — do not emit them as separate,
unrelated outputs:

a. **Axes.** The abstract dimensions the authors use to structure the field (not a flat model
   enumeration) — the conceptual coordinates a reader should use to place any new work.
b. **Categories.** Each category paired with the *architectural bound* that distinguishes it
   from its neighbors — a short label plus a dense technical distinction (e.g. "episodic memory
   as timestamped vector-JSON retrieved via Top-K" vs. "external memory as a tool-call KV
   store"). A category without a stated architectural distinction does not belong in the map.
c. **Bottlenecks.** The paradigm-level flaws and hard bottlenecks the field agrees on — each
   stated densely and concretely, not as a generic complaint ("scalability is a challenge").
d. **Gaps.** Open structural voids, each pairing a research direction with the specific
   technical reason the field has not closed it — no vague wish lists ("more research is
   needed").
e. **Edges.** The inter-concept relations between categories/axes — subsumes, competes-with,
   composes-into. This is the delta that turns a category list into an actual map; do not omit
   it.

## Discipline
Every finding must satisfy the mandatory triple, adapted for a map:
1. **Mechanism** — for each bottleneck/gap, the concrete architectural limit that causes it
   (not "needs more research" — name the actual constraint).
2. **Evidence** — the metacognition verdict: is this an opinionated, architecturally-grounded
   taxonomy (must-read) or a laundry list of SOTA models with no real structure (low value)?
   State the reason from the paper's own content.
3. **Falsifiability** — for each claimed gap or bottleneck, state the concrete architectural
   limit that makes it real and checkable, not aspirational. If a claimed gap cannot be tied to
   a specific technical cause, treat it as an unsupported assertion rather than a structural
   finding.
