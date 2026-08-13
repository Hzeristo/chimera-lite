# Incident 2026-07-13 — extract_paper doubled list markers ("1. 1.", "> 💥 💥")

**Severity:** cosmetic (render defect). **Status:** fixed.
**Surfaced by:** the first live run of the rebuilt `extract_paper` (Phase Q, `friction-260710-02`) on
STALE (arXiv 2605.06527).

## Symptom
The staged K node rendered algorithm steps as `1. 1. …`, `2. 2) …` and attack vectors as
`> 💥 💥 …`.

## Root cause
The extraction LLM sometimes prefixes each algorithm step with its own enumerator (`1.`, `2)`) and
each attack vector with a `💥` — and `_render_node_body` *also* prepends `{i}. ` and `> 💥 `. Two
markers, one line.

## Fix
Defensive stripping in `_render_node_body` (`single_paper_extract.py`):
- `_STEP_ENUM_RE = re.compile(r"^\s*\d+[.):]\s*")` strips a leading enumerator from each step.
- `_ATTACK_MARK_RE = re.compile(r"^[\s💥️]+")` strips leading `💥` runs (+ variation selectors) from
  each vector.
Belt-and-suspenders prompt notes added to `extract_node.j2` ("do NOT prefix a step number / the 💥
emoji; the renderer adds it"). Regression test: `tests/test_extract_paper.py::test_render_strips_double_markers`.

## Secondary finding — prompt hot-reload vs. code cold-load
During the fix, the re-extraction showed *clean steps but still-doubled emoji*. Cause: an MCP server
re-reads `prompts/*.j2` from disk every call (a fresh `PromptManager()` per extraction), so the new
step-prompt note took effect immediately — but it holds `single_paper_extract.py` in memory from
process start, so the code-level strips do NOT apply until the server is reconnected/restarted. When
validating a Python-layer fix against a live MCP tool, reconnect the server first (prompt-only fixes
don't need it). This is the general MCP-seam lesson (`chimera-mcp-taste`): the code is correct; the
running process is stale.
