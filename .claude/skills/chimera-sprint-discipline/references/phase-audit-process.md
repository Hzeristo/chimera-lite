# Phase Audit Process

<key_insight>
Phase audit produces the file:line evidence base that all sprints in the phase
will plan against. An audit fails when it produces guesses. An audit succeeds
when every claim is anchored.
</key_insight>

## Hard Preconditions
1. Phase doc exists at docs/phases/phase-{X.Y}.md (lowercase `phase-`)
2. Phase doc has Mission + Driving frictions + Sprint name list
3. Phase doc does NOT have detailed per-sprint task lists (those are batch_planning's job)

## Steps

<step n="1">
Read phase doc. Identify sprint names + each sprint's one-line goal.
</step>

<step n="2">
For each sprint goal, derive 1-3 audit questions. Output Q list before reading code.
Ask user for Q list approval (one round of clarification permitted).
</step>

<step n="3">
SCOUT FIRST, then read only what the scout selects (R1 + R3 — mandatory, not
opportunistic; Phase H.0 did this ad-hoc, it is now the process). Do NOT read the
whole in-scope tree up front — that is the Opus overspend this step exists to remove.

3a. Fan out one `chimera-repo-scout` (pinned Haiku — model bound in the agent def,
    never a call-site param) PER audit question from step 2, spawned in parallel — not
    one scout for everything. Each scout receives a spec:
      { question_id, question, file_globs: [...], patterns: [...] }
    and returns ONLY:
      { question_id, files: [<paths worth reading in full>],
        hits: [ { file, line, snippet } ], line_counts: { <path>: <int> },
        risk: "Low|Med|High" }
    Dedup before forking: group questions that share file_globs so the same files are
    not re-scanned by multiple scouts.

3b. The main (Opus) session reads IN FULL only the union of the scouts' `files` sets —
    never the whole in-scope tree (R3 context surgery). The scout hits are the evidence
    base; the audit synthesizes them into step-4 answers. Scout output is evidence,
    never the verdict.
</step>

<step n="4">
For each Q, write answer with file:line evidence + Risk (Low/Med/High).
</step>

<step n="5">
Identify cross-findings (audit revelations not directly answering a Q).
Flag, do not propose fixes.
</step>

<step n="6">
Output using assets/phase-audit-template.md. Write to the phase audit path —
see references/path_conventions.md (audit naming).
</step>

## Success Criteria
- [ ] Every Q has file:line answer
- [ ] Cross-findings flagged separately from Q answers
- [ ] No fix proposals
- [ ] Output committed to docs/audits/{prerequisite-sprint-id}.md
