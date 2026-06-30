# M.5 — Phase M E2E Smoke Checklist (USER-RUN)

**Status:** ⏳ Pending user execution. This is a manual checklist — Claude does NOT run it
(needs a live Claude Code session, LLM API keys, network, and the GPU).
**Purpose:** Verify the 5 Phase M sealing conditions (`docs/phases/phase-M.md:50-64`) live,
then hand to `chimera-sprint-discipline` phase_review to seal Phase M.

Run each test in a **Claude Code session launched from `D:\MAS\chimera-lite`** (so `.mcp.json`
loads `chimera-vault` + `chimera-papers`). Tick the box and note the result.

---

## Prerequisites (verify ALL before Test 1)

- [ ] **ripgrep on PATH** — `vault_query` shells out to `rg`.
  - Check: `rg --version` returns a version.
  - If missing: `winget install BurntSushi.ripgrep.MSVC` (or `scoop install ripgrep`), then
    restart the shell.
- [ ] **LLM API keys in config** — the pipeline's filter stage calls an OpenAI-compatible
  model. Confirm `~/.chimera/config.toml` `[llm.working]` / `[llm.wash]` (or `.env`
  `OPENAI_API_KEY` / `DEEPSEEK_API_KEY`) hold valid keys.
  - Check: `[llm.working].api_key` (or the env var) is set and non-empty.
- [ ] **Network** — arXiv fetch + LLM calls need outbound HTTPS.
- [ ] **GPU / CUDA** — MinerU PDF→Markdown runs on the RTX 5060.
  - Check: `D:\MAS\chimera-lite\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"` → `True`.
- [ ] **MCP servers load** — in the Claude Code session, the `chimera-vault` and
  `chimera-papers` tools appear (e.g. `/mcp` or tool list shows `vault_query`, `arxiv_miner`).

---

## Test 1 — Vault MCP (sealing condition 1)

**Goal:** `vault_query(type="knowledge")` via MCP returns real notes with titles + paths in **< 2s**.

- **Type to Claude:** *"Use vault_query to list knowledge nodes in the vault."*
- **Expect:** a `[vault_query] N match(es)` result listing real note titles + paths from
  `D:\MAS\project_chimera_vault`, returned in under ~2 seconds.
- **Also spot-check:** *"Read the vault note at <one of those paths>."* → `read_vault_file`
  returns the note body.

- [ ] **PASS** / [ ] **FAIL** — notes / time: ____________________

---

## Test 2 — Papers MCP pipeline (sealing condition 2)

**Goal:** `daily_paper_pipeline` → `task_id` → poll `check_task_status` → real paper titles
(full fetch → GPU MinerU ingest → LLM triage). **May take several minutes** — that's expected.

- **Type to Claude:** *"Run the daily paper pipeline, skip telegram."*
- **Expect:** an immediate `[Task Started] Daily pipeline: <8-hex id>` response.
- **Then:** *"Check the status of that task."* (repeat over minutes)
  - **Expect:** `[Task Running] Progress: …%` → eventually `[Task Completed]` with **real
    paper titles** (Must-Read / Skim).
- **Concurrency guard (optional):** while it runs, *"Start arxiv_miner for 'agent memory'."*
  → expect a `[Busy] …` rejection (only one pipeline at a time).
- **GPU check (optional):** during the ingest stage, `nvidia-smi` shows python using GPU memory.

- [ ] **PASS** / [ ] **FAIL** — task_id / titles / time: ____________________

---

## Test 3 — BB voice (sealing condition 3)

**Goal:** Claude's FINAL answer in a research conversation carries BB's voice
(toxicity + warmth + anti-hype + forensic), while reasoning/tool output stay plain.

- **Type to Claude (3 different research questions), e.g.:**
  1. *"Summarize the must-read papers from the last pipeline run."*
  2. *"Is <some hyped paper> worth my time?"*
  3. *"What's missing from <a paper's> evaluation?"*
- **Expect, in the FINAL paragraph of each:** sardonic, forensic, anti-hype tone; "Senpai"
  used sparingly; cruelty aimed at the work/field, never at you; a flash of warmth when the
  work is genuinely good. Reasoning steps + tool results remain plain/transparent.

- [ ] Response 1 carries BB voice
- [ ] Response 2 carries BB voice
- [ ] Response 3 carries BB voice
- [ ] **PASS** / [ ] **FAIL** — note any voice mismatch (esp. the "warmth" read): __________

---

## Test 4 — Independence (sealing conditions 4 & 5)

**Goal:** zero sentinels and zero oligo/astrocyte/crucible imports. (Already green at M.4 —
this is the re-confirmation at seal time.) Run in `D:\MAS\chimera-lite`:

```powershell
# all four must return 0
(Select-String -Path mcp-servers\*.py,mcp-servers\**\*.py -Pattern "NOT.WIRED|NotImplementedError" -ErrorAction SilentlyContinue | Measure-Object).Count
(Select-String -Path mcp-servers\*.py,mcp-servers\**\*.py -Pattern "from src\.oligo|import oligo" -ErrorAction SilentlyContinue | Measure-Object).Count
(Select-String -Path mcp-servers\*.py,mcp-servers\**\*.py -Pattern "src\.crucible" -ErrorAction SilentlyContinue | Measure-Object).Count
(Select-String -Path mcp-servers\*.py,mcp-servers\**\*.py -Pattern "astrocyte" -ErrorAction SilentlyContinue | Measure-Object).Count
```
(or `rg -n "NOT.WIRED|from src\.oligo|src\.crucible|astrocyte" mcp-servers` → no hits)

- **Expect:** all four counts = 0.

- [ ] **PASS** / [ ] **FAIL** — counts: ____________________

---

## Seal

- [ ] Tests 1–4 all PASS → hand to `chimera-sprint-discipline` **phase_review** to seal
  Phase M (update ROADMAP, ACCEPTED_PARTIALS, resolve driving frictions).
- If any test FAILs: log an incident (`docs/incidents/`) or re-open the relevant sprint;
  do not seal.

**Accepted-partial reminders carried from execution** (see `docs/sprints/phase-M/*.md`):
prune-on-port (M.0.5), `config extra=ignore`, +deps (pydantic-settings/tomlkit/dotenv/
requests/torch/mineru/jinja2/openai/tenacity), `uv.lock` gitignored, mypy/`check_taste.ps1`
not yet chimera-lite-wired, BB voice is an opinionated stance pending your review.
