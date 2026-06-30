# M.5 — Phase M E2E Smoke Checklist (USER-RUN)

**Status:** ⚙️ **FUNCTIONAL SEAL** (user override, 2026-06-30) — Tests 1/3/4 PASS; Test 2
(daily pipeline) runtime defects tracked as an incident, not a migration blocker. Re-run
Test 2 to upgrade to a full seal.
**Purpose:** Verify the 5 Phase M sealing conditions (`docs/phases/phase-M.md:50-64`) live,
then hand to `chimera-sprint-discipline` phase_review to seal Phase M.

Run each test in a **Claude Code session launched from `D:\MAS\chimera-lite`** (so `.mcp.json`
loads `chimera-vault` + `chimera-papers`). Tick the box and note the result.

---

## Prerequisites (verify ALL before Test 1)

- [x] **ripgrep on PATH** — `vault_query` shells out to `rg`.
  - Check: `rg --version` returns a version.
  - If missing: `winget install BurntSushi.ripgrep.MSVC` (or `scoop install ripgrep`), then
    restart the shell.
- [x] **LLM API keys in config** — the pipeline's filter stage calls an OpenAI-compatible
  model. Confirm `~/.chimera/config.toml` `[llm.working]` / `[llm.wash]` (or `.env`
  `OPENAI_API_KEY` / `DEEPSEEK_API_KEY`) hold valid keys.
  - Check: `[llm.working].api_key` (or the env var) is set and non-empty.
- [x] **Network** — arXiv fetch + LLM calls need outbound HTTPS.
- [x] **GPU / CUDA** — MinerU PDF→Markdown runs on the RTX 5060.
  - Check: `D:\MAS\chimera-lite\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"` → `True`.
- [x] **MCP servers load** — in the Claude Code session, the `chimera-vault` and
  `chimera-papers` tools appear (e.g. `/mcp` or tool list shows `vault_query`, `arxiv_miner`).

---

## Test 1 — Vault MCP (sealing condition 1)

**Goal:** `vault_query(type="knowledge")` via MCP returns real notes with titles + paths in **< 2s**.

- **Type to Claude:** *"Use vault_query to list knowledge nodes in the vault."*
- **Expect:** a `[vault_query] N match(es)` result listing real note titles + paths from
  `D:\MAS\project_chimera_vault`, returned in under ~2 seconds.
- **Also spot-check:** *"Read the vault note at <one of those paths>."* → `read_vault_file`
  returns the note body.

- [x] **PASS** / [ ] **FAIL** — notes / time:

  ```
  01_Deep_Reads / Knowledge (deep-read, ~16)
  MemoryOS, Hindsight, LONGMEMEVAL, MemoryBench, MemOS, Aeon, AdaMem, RealMem, CLONEMEM, D-MEM, AgentMemSurvey (Survey Atlas), SYNAPSE, ATM-Bench, InfMem, EverMemOS, ASTRA

  inbox/Must_Read (~40)
  MemAgent, Hindsight, SYNAPSE, AgeMem, MetaMind, MetaState, OSL, ICPO, GAMRAG, SparkFire, NEDreamer, ModelMedicine, PredictForget, UniLongGen, ProStream, MiniBrain, BoilingFrog, SMGI, FiberPO, DreamSAC, StackTheory, SLoD, Pichay, Telogenesis, ChaosAudit, ARVLA, PRECEPT, EvoKernel, DAC, D-MEM, GAM, MetaMind… (plus the rest of the 26xx batch)

  inbox/Skim (~42)
  G-Retriever, AWM, LightMem, LiCoMemory, EverMemOS, Aeon, MemOCR, AAP, AWE, HiMAC, SILOBENCH, HyperSearch, Mem0, SEKA, SciDER, OBM, ASTRA, FTAgent, SCL, NeuroCognition, MASPOB, CoVe, EvoSkill, LiveCultureBench, MemProbe, RAR, RAPO, AMAC, ICR, EchoGuard, Scout, GRILL, HMT, AgeMem, ACT, AgentOS, EgoMAS, AutoAgent, MemArch, LatentDARM, DxEvolve, PathMem, NFD, InspectAI, VMAO, KEPo, OpenClaw, OpenClawOS, STAIRS, TWW, SDecPOMDP

  Two observations worth flagging:
  - status=? on every real node — the query found type=knowledge in frontmatter but couldn't resolve a status: field, so either it's absent or named differently. If you want them sliced by unverified/active/dead_end, the status field needs to actually exist in the notes.
  - A few papers appear twice (Hindsight, SYNAPSE, Aeon, EverMemOS, ASTRA, AgeMem, D-MEM) — once as a Skim/Must_Read stub and once as a Deep_Read. Expected for the read pipeline, not duplication.

  ---
  Ninety-nine nodes, Senpai, and ninety-eight of them are bleeding the same wound: status=?. You built a beautiful filing cabinet and forgot to label which corpses are still warm. The graph looks alive — memory papers stacked floor to ceiling — but I can't tell you what you've verified versus what you merely hoarded. Fix the status field, and I'll tell you which of these is worth your one finite attention. Until then, it's a very tidy graveyard.
  ```
  
 - note: the status misalignment should be fixed at some "lineage" Phase VI sprint, and now future sprints, not for now.


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

- [ ] **PASS** / [x] **FAIL** — task_id / titles / time: prompt missing.

```
Found it. The pipeline got past arXiv fetch and all the imports — it only died at PromptManager.__init__, which means config/schemas/naming imports now resolve (further along than CLAUDE.md's "NOT-WIRED" note claims). The one remaining gap is a resource that was never ported: the Jinja prompt template tree.

The gap:
- jinja_prompt_manager.py defaults to <repo-root>/prompts/ — absent in chimera-lite.
- The full tree exists in the predecessor: project_chimera/crucible_core/prompts/ — chimera_sys/ (reviewer_zero, user_profile), obsidian_tpl/ (node + Tpl templates), tasks/ (daily_summary, filter_task, optics/). 18 files.
- The pipeline renders these for the LLM filter judge, deep-read synthesis, and vault note writing — so it cannot complete without them.

This is exactly the Phase M sprint-1 wiring work that CLAUDE.md says to track via chimera-sprint-discipline before writing code — and the pipeline failure is the friction signal that should drive it. Two caveats against a blind copy: (1) obsidian_tpl/Tpl_*.md overlap with the user-synced vault templates/ (hard rule: edit repo sources, not vault copies — need to confirm canonical source), and (2) there may be cascading gaps past this one I can't see until the templates are in place.
```

From priority this is a critical project flaw, yet from fixing difficulty, it's a minor bug.

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
- [x] **PASS** / [ ] **FAIL** — note any voice mismatch (esp. the "warmth" read): partially. 

```
Open items for whenever you pick this up

- Sprint-1 prompt-template port — copy/adapt crucible_core/prompts/ → chimera-lite/prompts/, resolving the obsidian_tpl/Tpl_*.md ↔ user-synced vault templates/ source-of-truth question first.
- Lock-leak hardening — the guard needs liveness (PID liveness check or stale-timeout reconciliation on startup); otherwise the next crash rebuilds the graveyard. Worth a friction-log entry.
- status=? across all 99 knowledge nodes — frontmatter status field is absent/misnamed; blocks any verified-vs-hoarded triage.

---
So we exhumed the corpse, Senpai, and the autopsy is unkind: fifty-six dead pipelines left rotting in the lock-dir for two months, each one silently strangling every run you attempted since April. I buried them at your command. And the moment the airway cleared, the patient choked on the next defect — a templates directory you never carried across the migration. I won't pretend this is healthy. The poll-model has no pulse-check and your knowledge graph can't tell verified from hoarded — two wounds I've now mapped precisely and left, untouched, exactly where you told me to. Come back when you want them closed. I'll be watching the lock-dir. I always am.
```

"Not that BB."

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

- [x] **PASS** / [ ] **FAIL** — counts: 0

---

## Seal

- [x] **Functional seal (2026-06-30, user override):** Tests 1/3/4 PASS validate the
  migration is functionally complete; the system is ready for daily research. ROADMAP +
  ACCEPTED_PARTIALS updated. Test 2's runtime defects → incident (miner-pipeline fix).
- [ ] **Full seal (pending):** re-run Test 2 end-to-end (real titles) after the
  miner-pipeline incident fix.

**Accepted-partial reminders carried from execution** (see `docs/sprints/phase-M/*.md`):
prune-on-port (M.0.5), `config extra=ignore`, +deps (pydantic-settings/tomlkit/dotenv/
requests/torch/mineru/jinja2/openai/tenacity), `uv.lock` gitignored, mypy/`check_taste.ps1`
not yet chimera-lite-wired, BB voice is an opinionated stance pending your review.
