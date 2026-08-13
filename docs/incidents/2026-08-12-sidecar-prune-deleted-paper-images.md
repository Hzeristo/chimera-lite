# Incident — an automatic "duplicate" prune deleted the only copy of a paper's figures

**Date:** 2026-08-12
**Surfaced by:** re-running MinerU before writing the Phase L.B seal artifact (operator-directed:
*"rerun mineru after this fix before real sealing artifact"*). The first successful sidecar
conversion produced markdown referencing an image that existed nowhere on disk.
**Severity:** High (silent data loss — a converted paper's figures, unrecoverable without
re-conversion; no error, no warning) / Fix difficulty: minor.
**Status:** fixed; the destroyed image recovered by re-conversion; all 101 image references
across `md_papers/` now resolve.

## Symptom

`daily_paper_pipeline` converted `2608.08883` (AquiLLM) cleanly — `new_pdfs=1 ingested=1
convert_failed=0`. The promoted markdown `papers/md_papers/2608.08883.md` carried

```
![](images/c94ea2f3c48be176f83eeaae573922ebe0c1592b9cac47f58d8e2700743a9788.jpg)
```

and a filesystem-wide search for that name returned nothing. No `md_papers_raw/2608.08883/`
had been written either.

## Root cause — two defects, one old and one introduced hours earlier

**(1) Pre-existing, since repo init.** `PaperLoader.extract_and_clean` promotes ONLY the `.md`
into `md_papers/`. MinerU writes figure links relative to the markdown (`images/<sha256>.jpg`)
and leaves the images in the raw output tree. So every promoted markdown has had dangling
image links from the moment it was written — 101 references across the corpus, none resolving
from the directory the file actually lives in. Survivable only because the raw tree was
permanent and nothing depended on the links.

**(2) Introduced 2026-08-11 in the sidecar work.** `prune_output` was wired into spawn and
stop to bound the growth of `MINERU_API_OUTPUT_ROOT` (60 MB across 7 parses), on the stated
premise that the tree is "a FULL duplicate of the paper ... whose authoritative home is
`papers/md_papers_raw/<id>/`". That premise is false on the path it ran on: under `--api-url`
the client keeps only the clean markdown, so for a sidecar-parsed paper the extracted
`images/` exist ONLY in the sidecar's output root. Pruning at stop deleted them.

Defect (1) made the images the only copy; defect (2) deleted it. Either alone is survivable.

**Why it was not caught.** The premise was checked against a paper converted by the OLD path,
where `md_papers_raw/<id>/hybrid_auto/images/` does exist, and generalised to a path that
behaves differently. This is the same shape as the verifier defects found the same day: a
check aimed one surface away from the claim it licenses.

## Fix

- `ports/papers/paper_loader.py` — `_copy_images_alongside` copies MinerU's `images/` into
  `clean_dir/images/` after promoting the markdown. A single shared directory is correct
  rather than per-paper: the relative link is exactly `images/<name>`, and MinerU names files
  by content hash, so identical figures dedupe and cannot collide. Existing files are skipped
  for the same reason. Never raises — a missing figure must not fail a good conversion.
- Same file — the early return for an already-promoted markdown now copies images too.
  Without that, a paper converted before this fix could never be repaired by re-running, and
  the function would not be idempotent.
- `ports/ingest/mineru_sidecar.py` — pruning restored at **spawn only, never at stop**, under
  two rules now written on `prune_output`: only prune what has already been promoted, and
  never delete evidence at the moment of failure (stop is exactly when a failed batch's
  artifacts are what you would diagnose from — the same mistake truncate-on-start made with
  the log). Growth is bounded to one batch instead of accumulating forever.

## Verification

- Direct exercise of the promotion path on a raw tree with figures: 36 images copied, 15
  references, **0 unresolved**.
- Backfill of existing papers (pure copy, nothing deleted): 471 images promoted.
- The destroyed image recovered by re-converting `2608.08883` through the fixed path.
- Corpus-wide: **101 image references across `md_papers/`, 0 unresolved**, 474 images.
- Full suite: 210 passed.
- Note during recovery: `ingest_paper` did not promote the images on the first attempt because
  the running MCP server held `paper_loader` imported from before the edit. Confirmed by
  running the same call in a fresh interpreter, which promoted them. Server-level module
  reloads need an MCP restart — the third time that has bitten this session.

## Lesson

"Duplicate" is a claim about two locations, and it must be checked on the path that will
actually run — not on a neighbouring path that happens to be easier to inspect. The reclaim
was worth 60 MB; the thing it deleted was irreplaceable without re-running a GPU conversion.
When a cleanup and a correctness property disagree, the cleanup is the one that yields:
prune only what has been promoted, and never at the moment something has just failed.
