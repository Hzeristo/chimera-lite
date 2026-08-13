# Incident — a paper that completed Path 1 triage was unreadable to Path 2

**Date:** 2026-08-10
**Surfaced by:** the Phase L.B.6 five-path e2e. `get_paper_markdown("2603.02096")` returned
`[Extract Error] No converted markdown` for a paper whose markdown demonstrably existed on disk.
**Severity:** High (Path 1 and Path 2 could not compose — the deep-read path was unreachable for
any paper the triage path had already processed) / Fix difficulty: minor (one resolver, ~35 lines).
**Status:** fixed; regression-tested over all three layouts.

## Symptom

`chimera-deep-extract` step 1 calls `get_paper_markdown(paper_id)`. For `2603.02096` it failed,
while `papers/md_papers_raw/2603.02096/hybrid_auto/2603.02096.md` (60,835 bytes) sat on disk. Five
other papers were in the same state. The e2e could only proceed after a manual file copy — a
workaround, not a fix, and one that masked the defect.

## Root cause

Three producers write converted markdown to three different layouts; the resolver knew one.

| producer | writes to |
|---|---|
| `ingest_to_papers` | `md_papers/<id>.md` |
| `convert_pdf_to_md` | `md_papers_raw/<id>/hybrid_auto/<id>.md` (`miner_tools.py:222` — output root is the RAW dir) |
| triage archive | `filtered/<verdict>/<id>-<Moniker>.md` |

`_resolve_markdown` (`single_paper_extract.py`) checked only `md_papers/<id>.md` and raised
otherwise. Two consequences, the second worse than the first:

1. A `convert_pdf_to_md` result was never resolvable — that tool writes only to the raw tree.
2. `PaperArchiveAdapter.route_and_cleanup` (`paper_archive_adapter.py:56`) **moves** the clean MD
   out of `md_papers/` into `filtered/<verdict>/` and renames it `<id>-<Moniker>.md`. So completing
   Path 1 triage actively *removed* the file Path 2 was looking for. The two halves of the pipeline
   were structurally unable to compose.

## Fix

`_resolve_markdown` searches all three layouts in order and returns the first hit; it never moves
or copies. The archive branch globs `<id>*.md` because the archive renames with a moniker — a
literal `<id>.md` would have matched nothing and the fix would have failed its own acceptance
criterion. Optional config is read with `getattr` so test stubs supplying only `md_papers_dir`
still work. The error now lists every location searched instead of one.

## Verification

- Direct resolution after removing the manual copies — all four L.B.6 fixtures resolved from the
  raw tree, and `2607.01224` (a paper that had been through triage) resolved from
  `filtered/Skim/2607.01224-AutoMem.md`, which is the acceptance criterion.
- A nonexistent id still raises, listing all three searched paths.
- `analyze_paper_data` inherits the fix — it resolved `2607.01224` for the triage re-run, which it
  could not have done before.
- Three regression tests in `tests/test_extract_paper.py`: raw-MinerU fallback, triage-archive
  fallback, and clean-copy-wins precedence. Full suite 187 passed at the time of the fix.

## Lesson

A read path and a write path can each be correct and still not meet. Nothing was broken in
isolation — the archive move is intentional, the resolver's original single lookup was intentional
— and the defect lived entirely in the assumption that one component's output location was the
other's input location. The unit tests passed on both sides throughout; only an end-to-end run
across the seam could surface it, which is the argument for the L.B.6 gate existing at all.
