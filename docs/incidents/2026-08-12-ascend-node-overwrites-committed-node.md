# Incident — `ascend_node` could silently overwrite a committed Knowledge node

**Name:** the gate that overwrites
**Date:** 2026-08-12 · **Status:** RESOLVED (same day) · **Severity:** high — silent destructive
write to the committed tier, contradicting a Tier-0 invariant
**Found by:** the Architect, asking why a node's filename contained the paper's full title

## Symptom

`Knowledge/MEMDREAMER_Hierarchical_Graph_Memory_and_Agentic_Tool_Retrie.md` — a filename cut
mid-word. Cosmetic on its face. The cause was not.

## Root cause

`staging_service._ascend_write` derived the committed filename itself:

```python
slug = _SLUG_RE.sub("_", fm.get("title", "untitled"))[:60].rstrip("_")
dest_path = dest_dir / f"{slug}.md"
dest_path.write_text(...)          # no existence check
```

Two independent defects in three lines.

**(a) It reimplemented naming that already existed.** `core/naming.py` has carried the vault's
convention all along — `expected_stem(arxiv_id, short_moniker) -> f"{arxiv_id}-{short_moniker}"`,
with `compute_fancy_basename` documented as "与 Obsidian 一致". `vault_note_writer` and
`paper_archive_adapter` both use it, which is why every paper asset and every `derives_from` target
reads like `2404.16130v2-GraphRAG`. **Only the committed-tier writer diverged**, and it diverged to
something worse: a 60-character cut of the title.

**(b) It wrote unconditionally into the committed tier.** I0.4 states committed nodes are never
deleted, only superseded and marked STALE. Two nodes whose slugged titles share 60 characters
resolve to one path, and the second `write_text` destroys the first — with `supersedes` never
consulted and nothing recorded.

The realistic trigger is not a contrived collision. **It is one paper re-extracted after a new arXiv
version appears**: same title, therefore same stem, therefore silent replacement of a committed node
along with whatever edges and verdicts had accumulated against it.

## Why it survived

`ascend_node` is the *sole* guarded door into `Knowledge/` and was hardened twice (L.B.3 gated the
callers on tier; the L.B seal moved the guard onto the destination). Both passes asked "may this
node be written here?" Neither asked "is something already there?" A door reviewed for
authorization, never for collision — and its name advertised safety, which is why nobody looked
again.

## Fix

- `_committed_stem(fm)` derives `{arxiv_id}-{moniker}` through the existing `core.naming`
  helpers. The moniker is the title's pre-colon segment, which is not a scrape:
  `KNodeExtraction.title` specifies the shape `"<system/model name>: <one-line what-it-is>"`
  (`core/schemas.py:363`). Falls back to the sanitized title when there is no colon.
- `_ascend_write` refuses to overwrite an existing committed node **unless that node is named in
  the incoming node's `supersedes`**. Supersession becomes explicit or does not happen; the
  staging file is left intact on refusal so nothing is lost.

Regressions in `tests/test_ascend_node.py`: the stem convention, the overwrite refusal, and the
deliberate-supersession escape hatch.

**Negative controls, both run and recorded.** Restoring the old `title[:60]` stem fails the naming
and supersession tests; disabling the guard alone fails the overwrite test and leaves the other two
green — confirming the two fixes are independently checked rather than one test covering both.
Full suite 244 passed.

## Vault repair (Architect-authorized)

- `MEMDREAMER_…_Tool_Retrie.md` → `2606.07512-MEMDREAMER.md`
- `FluxMem_…_for_Str.md` → `2603.02096-FluxMem.md`
- Both verified to have **no inbound wikilinks** before renaming.
- `2506.06326v1-MemoryOS_Deep_Read.md` was **not renamed**: it already leads with its id, and it is
  linked from a hand-authored Thought — renaming would have edited a wikilink inside an
  Architect-authored judgment body (I0.5).

**A third defect found during the repair.** That node's frontmatter read
`arxiv_id: "2506.06326v1-MemoryOS"` — the stem, not an id. `chimera-w1-review` resolves a verdict's
K node with `search_vault_attribute(key="arxiv_id", …)`, so **no W1 verdict for that paper could
ever have found its Knowledge node**, and the row would have rendered as the ordinary
"no committed K node" case. Corrected to `2506.06326v1`; filename and title left alone to preserve
the inbound link.

## Lesson

Two, and the second is the transferable one.

**Do not write a naming scheme without looking for the one that exists.** The Architect's standing
order here — *fetch existing naming mechanisms before implementing one* — turned a proposed new
convention into the discovery that it was already implemented, tested, and in use everywhere except
the one writer that mattered.

**A guard is scoped to the question it was written to answer.** This one was built to answer
"who may write here", asked at the moment I1.2 was under scrutiny, and it answers that question
correctly to this day. It was never asked "what is already there", so it never checked — and
because it is the door everything else defers to, its silence read as safety. When a check is
hardened, the review should ask what the *new* check does not cover, not only whether the old gap
closed.
