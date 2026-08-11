# Formal Model

## Research Artifact Graph

Let $\mathcal{G} = (V, E, \tau, \sigma, \lambda, \preceq)$ where:

- $V$ is a finite set of *artifact nodes*
- $E \subseteq V \times V$ is a set of *typed edges*
- $\tau: V \to \{\mathtt{K}, \mathtt{T}, \mathtt{I}, \mathtt{D}, \mathtt{W1}, \mathtt{W2}\}$
  is the *node type function*
- $\sigma: V \to \{\mathtt{candidate}, \mathtt{staged}, \mathtt{committed}, \mathtt{stale}\}$
  is the *lifecycle status*
- $\lambda: E \to \{\mathtt{derives\_from}, \mathtt{depends\_on}, \mathtt{collides\_with}, \mathtt{contradicts}, \mathtt{supersedes}\}$ is the *edge label function*
- $\preceq \subseteq V \times V$ is a partial order on nodes induced by provenance

## Evidence Tiers

Evidence sources are stratified into three tiers:

$$
\begin{aligned}
\text{Tier}_1 &= \{\text{table entries, equation definitions, arXiv metadata}\} \\
\text{Tier}_2 &= \{\text{method descriptions, result statements with context}\} \\
\text{Tier}_3 &= \{\text{author claims in intro/conclusion}\}
\end{aligned}
$$

with epistemic warrant ordering $\text{Tier}_1 \succ \text{Tier}_2 \succ \text{Tier}_3$.

## Verification Tags

Let $\mathcal{T} = \{\mathtt{V}, \mathtt{P}, \mathtt{U}\}$ with numeric encoding
$\llbracket \mathtt{V} \rrbracket = 2$, $\llbracket \mathtt{P} \rrbracket = 1$,
$\llbracket \mathtt{U} \rrbracket = 0$.

A verification judgment is a triple $\langle c, s, q \rangle$ where:

- $c$ is a claim (syntactic term)
- $s \in \mathcal{T}$ is the verification tag
- $q$ is a verbatim quote from source $\in \text{Tier}_1 \cup \text{Tier}_2$
  (empty if $s = \mathtt{U}$)

**Tag semantics:**

$$
\begin{aligned}
\mathtt{V}(c) &\triangleq \exists q \in \text{Tier}_{1,2}.\ q \vdash c
  \land \text{cited}(q, c) \\
\mathtt{P}(c) &\triangleq \exists q.\ q \rightharpoonup c
  \land (\text{confounded}(q) \lor q \in \text{Tier}_3) \\
\mathtt{U}(c) &\triangleq \neg \exists q \in \text{checked sources}.\
  q \vdash c \lor q \rightharpoonup c
\end{aligned}
$$

where $q \vdash c$ denotes entailment and $q \rightharpoonup c$ denotes partial support.

## State Transitions

The artifact graph evolves under two clocks:

- **Machine-time** $t_m \in \mathbb{N}$: candidate accumulation
- **Human-time** $t_h \in \mathbb{N}$: truth commitment ($t_h \ll t_m$ in cardinality)

**Candidate production** (machine-time transition):

$$
\frac{\text{W1}(c, p) = \langle c, s, q \rangle}
     {\mathcal{G} \xrightarrow{t_m} \mathcal{G}' \text{ where }
      V' = V \cup \{v_{\text{new}}\}, \sigma(v_{\text{new}}) = \mathtt{candidate}}
$$

**Human commit** (human-time transition):

$$
\frac{v \in V, \sigma(v) = \mathtt{candidate}, \text{Architect}(v) = \texttt{promote}}
     {\mathcal{G} \xrightarrow{t_h} \mathcal{G}' \text{ where }
      \sigma'(v) = \mathtt{committed}}
$$

**Provenance monotonicity** (structural gate):

$$
\forall v \in V.\ \sigma(v) = \mathtt{committed} \implies
  \llbracket \text{tag}(v) \rrbracket \leq
  \min_{u \in \text{deps}(v)} \llbracket \text{tag}(u) \rrbracket
$$

where $\text{deps}(v) = \{u \mid (u,v) \in E, \lambda(u,v) = \mathtt{depends\_on}\}$.

**Provenance decay** (temporal propagation):

$$
\frac{(u,v) \in E, \lambda(u,v) = \mathtt{derives\_from},
      \sigma(u) \xrightarrow{t} \mathtt{stale}}
     {\sigma(v) \xrightarrow{t} \mathtt{stale}}
$$

## System Invariants

**I1. Human-time supremacy:**

$$
\forall v \in V.\ \sigma(v) = \mathtt{committed} \implies
  \exists t_h.\ \text{action}_{\text{human}}(v, t_h)
$$

**I2. Tier-grounded verification:**

$$
\forall v.\ \text{tag}(v) = \mathtt{V} \implies
  \exists q \in \text{Tier}_{1,2}.\ \text{anchor}(v, q)
$$

**I3. Well-formed support chain:**

$$
\forall v \in V_{\text{committed}}.\
  \text{reachable}(v, \text{Tier}_1 \cup \{\text{human-authored}\}) \lor
  \text{tag}(v) \in \{\mathtt{P}, \mathtt{U}\}
$$

A committed node either traces to Tier-1 evidence or explicitly admits weakness.

**I4. Append-only with supersession:**

$$
\forall v, v' \in V, t < t'.\ \sigma(v, t) = \mathtt{committed} \implies
  \sigma(v, t') \in \{\mathtt{committed}, \mathtt{stale}\}
$$

Committed nodes are never deleted, only superseded and marked stale.

## Phase Locus Colligo: Reduction Operations

**R1. Claim extraction** (K-node $\Rightarrow$ W1-queue):

$$
\frac{\tau(v) = \mathtt{K}, \text{claims}(v) = \{c_1, \ldots, c_n\}}
     {\text{offer}(\{c_1, \ldots, c_n\})}
$$

**R2. Batch verification** (W1-queue $\Rightarrow$ verdict-set):

$$
\frac{\text{queue} = \{c_1, \ldots, c_n\},
      \forall i.\ \text{W1}(c_i, p) = \langle c_i, s_i, q_i \rangle}
     {\text{verdicts} = \{\langle c_1, s_1, q_1 \rangle, \ldots,
      \langle c_n, s_n, q_n \rangle\}}
$$

**R3. Provenance commit** (verdict $\Rightarrow$ depends-on edge):

$$
\frac{\text{promote}(\langle c, s, q \rangle) = v_{\text{claim}},
      \text{source}(q) = v_{\text{evidence}}}
     {E' = E \cup \{(v_{\text{evidence}}, v_{\text{claim}})\},
      \lambda(v_{\text{evidence}}, v_{\text{claim}}) = \mathtt{depends\_on}}
$$

**R4. Stream mode** (online term rewriting):

$$
\mathcal{G}(t) \xrightarrow{\text{W1}_{\text{stream}}} \mathcal{G}(t+\Delta t)
\quad \text{where } \Delta t < \text{read-completion-time}
$$

Verification proceeds concurrently with document reading, not sequentially after.

**Seal condition:**

$$
\forall v \in V.\ \sigma(v) = \mathtt{candidate} \implies
  \exists \text{review-action}(v) \lor
  \text{age}(v) < \epsilon
$$

No unreviewed candidate older than $\epsilon$ (stale threshold).
