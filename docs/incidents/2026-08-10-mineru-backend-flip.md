# Incident — MinerU backend flipped hybrid-engine -> pipeline (the VLM was buying nothing)

**Date:** 2026-08-10
**Surfaced by:** the 5-cell x 3-paper comparison run by `scripts/debug_mineru.py matrix`,
built earlier the same day. Follows `2026-08-10-mineru-3x-drift.md`, which pinned
`-b hybrid-engine` a few hours before this measurement existed.
**Severity:** Low as a defect (nothing was broken), high as a **corpus** decision — it
changes the text of every future ingested paper. Fix difficulty: one token.
**Status:** applied. Operator-approved with the corpus consequence accepted explicitly.

## Why this is a separate record

The drift incident pinned the backend on the reasoning that an *explicit* config beats an
*inherited* default. That reasoning was right; the value was wrong. Pinning and choosing
the right value are two different claims, and the second one only became checkable once
the harness could measure it. Folding this into the earlier document would hide that the
first pin shipped without evidence.

## Measurement

Three papers of different character (formula-heavy `2602.01869`, table-heavy `2604.14004`,
figure-heavy `2602.06507`), first 12 pages each so every cell sees identical input. Recall
is n-gram overlap against the PDF's own text via pypdfium2 — comparative between cells on
the same paper, not meaningful as an absolute.

| paper | cell | secs | VRAM MB | recall% | unbacked% | charts |
|---|---|---|---|---|---|---|
| 2602.01869 | pipeline-auto | **34.3** | 3176 | 67.2 | 37.9 | 0 |
| 2602.01869 | hybrid-auto-medium | 95.4 | 4309 | 66.8 | 35.5 | 0 |
| 2602.01869 | hybrid-auto-high | 325.9 | 5292 | 67.8 | 36.1 | 2 |
| 2602.01869 | vlm-engine | 358.9 | 4768 | 68.8 | 34.6 | 2 |
| 2604.14004 | pipeline-auto | **31.9** | 1061 | 74.9 | 24.7 | 0 |
| 2604.14004 | hybrid-auto-medium | 62.2 | 4681 | 75.1 | 24.1 | 0 |
| 2604.14004 | hybrid-auto-high | 168.7 | 6538 | 75.6 | 27.1 | 7 |
| 2604.14004 | vlm-engine | 281.8 | 5396 | 77.6 | 25.1 | 7 |
| 2602.06507 | pipeline-auto | **32.4** | 1054 | 67.7 | 31.9 | 0 |
| 2602.06507 | hybrid-auto-medium | 46.4 | 4219 | 67.8 | 31.8 | 0 |
| 2602.06507 | hybrid-auto-high | 160.6 | 6554 | 68.0 | 36.4 | 12 |
| 2602.06507 | vlm-engine | 258.1 | 6542 | 69.1 | 34.5 | 12 |

Structure was identical between pipeline and hybrid-medium on all three: images 30/30,
13/13, 24/24; tables 3/3, 7/7, 3/3; equations 21/21, 0/0, 9/9. Spot-check of the case most
likely to diverge (pipeline uses ONNX table models, hybrid uses the VLM) on the table-heavy
paper: 50 vs 49 `<tr>` rows, identical headers and columns.

Two further results from the same run:

- **The method axis is dead.** `hybrid-txt-medium` was byte-identical to
  `hybrid-auto-medium` on all three papers (61428/61428, 57155/57155, 50340/50340). `auto`
  correctly classifies born-digital arXiv as text; `-m txt` buys nothing. `-m auto` stays.
- **Chart fabrication is a VLM-path property, not an effort=high setting.** `vlm-engine`
  was never given an `--effort` flag and still injected 2 / 7 / 12 `<details>` chart
  transcription blocks, because `image_analysis` defaults True. Any road through the VLM
  ends in numbers no author wrote.

## Change

`ports/ingest/paper2md.py`: `MINERU_BACKEND = "hybrid-engine"` -> `"pipeline"`. Nothing
else. `-m auto` unchanged; `--effort` still unset.

## Blast radius (assessed before applying, accepted by the operator)

One token, but it reaches every future convert -> `papers/md_papers/*.md` -> scout cards ->
deep_read K nodes -> W1 verbatim quotes and W2 numbers. The failure mode is **silent**: no
error, the text simply differs. Nothing in the pipeline records which converter produced a
file — `PaperMetadata(extracted_from="MinerU")` (`paper_loader.py:129`, `schemas.py:32`) is
a bare string with no version, backend, or effort, and the clean markdown carries no
provenance header.

Stamping converter identity into the output was proposed as the mitigation and
**declined by the operator**, on the grounds that K nodes are cheap to regenerate and the
Obsidian graph is small enough to repair by hand. Recorded here so the decision is
attributable rather than assumed.

Note the pre-existing condition: the corpus is *already* heterogeneous and already
unstamped — the 10 files in `papers/md_papers/` span a MinerU version drift (manifest still
declares `>=1.4`; installed is 3.4.0). This flip adds one more undocumented stratum to a
corpus that had them before today.

## Follow-ups

- The 10 existing conversions remain hybrid/2.x-era output. Re-converting them under
  `pipeline` costs ~5 min but rewrites text that existing K nodes may quote, so it must
  pair with re-verification. Deliberately NOT done here.
- `pyproject.toml` still declares `mineru[core]>=1.4` against 3.4.0 (carried over from the
  drift incident) — the floor should move to `>=3.4,<4`.
