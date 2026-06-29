# Phase M — Chimera Lite Migration

**Status:** Active
**Sealed predecessor:** Phase V.A (in project_chimera repo; this is chimera-lite's first phase)
**Driving frictions:**
- Self-built agent loop (oligo) is maintenance liability; Claude Code native loop replaces it
- Astrocyte frontend is maintenance burden; Claude Code UI replaces it
- Tool calling via text DSL (1485 lines parse/repair) → native MCP (zero parse code)
- Per ST 2026-06-27 feasibility audit: migration technically feasible, code health improves

## Mission

Wire the two MCP servers (chimera-vault, chimera-papers) to real domain logic,
add BB persona skill, and verify the complete research workflow runs end-to-end
on Claude Code without any oligo/astrocyte dependency. This is the operational
migration from "self-built agent" to "Claude Code + MCP."

## Sprint Sequence

| Sprint | One-line goal | Status |
|---|---|---|
| M.0 | Audit: current chimera-lite state, import gaps, domain code dependencies, what's wired vs NOT-WIRED | Pending |
| M.1 | Vault MCP wiring: connect 5 vault tools to real VaultReadAdapter + ripgrep logic | Pending |
| M.2 | Papers MCP wiring: connect arxiv_miner / daily_paper_pipeline / check_task_status to real PaperMiner services + TaskService | Pending |
| M.3 | BB persona: create chimera-bb-persona skill (always-on restyle) + verify Claude output carries BB voice | Pending |
| M.4 | Cleanup: delete all NOT-WIRED sentinels, fix remaining imports, remove dead oligo references from copied code | Pending |
| M.5 | E2E smoke: full workflow (爬论文 → Deep Read → vault query → BB analysis) verified live | Pending |

Dependencies: M.0 precedes all. M.1 and M.2 independent (can parallel).
M.3 independent of M.1/M.2. M.4 after M.1+M.2. M.5 after all.

## Cross-Sprint Red Lines

- ❌ NO oligo agent loop code in chimera-lite (the point is to delete it)
- ❌ NO Astrocyte / Tauri / Svelte code in chimera-lite
- ❌ NO text-DSL tool parsing (<tool_call> / <CMD:> / parse_args_with_repair)
- ❌ NO SSE protocol (bb-stream-chunk, bb-phase-transition etc.)
- ❌ NO prompt_composer / late persona bind / two-model split
- ❌ MCP servers MUST be thin adapters (< 200 lines each); domain logic
  stays in the service/port layer unchanged
- ❌ Domain service code (PaperMiner / Vault) should require MINIMAL changes
  from project_chimera — primarily import path fixes, not logic rewrites
- ❌ TaskService poll model, NOT in-request await (Claude Code re-invokes
  on next turn, not suspend-resume within one response)
- ❌ BB persona via skill ONLY — no system prompt hacks, no CLAUDE.md persona
  injection beyond what skills support

## Hard Sealing Conditions

1. (Vault MCP) Claude Code invokes vault_query(type="knowledge") via MCP
   → returns real vault notes with titles + paths in < 2s.
   Verified by live Claude Code session.
2. (Papers MCP) Claude Code invokes daily_paper_pipeline via MCP → returns
   task_id → user says "check status" → Claude polls check_task_status →
   eventually returns real paper titles from completed pipeline.
   Verified by live Claude Code session (may take minutes — that's expected).
3. (BB voice) Claude Code's final output in a research conversation carries
   BB persona characteristics (toxicity + warmth + anti-hype + forensic).
   Verified by reading 3 responses and confirming voice.
4. (Zero sentinel) grep "NOT.WIRED\|NotImplementedError" across mcp-servers/
   returns 0 hits. Every declared tool has real implementation.
5. (Independence) chimera-lite has zero imports from oligo.core / oligo.api /
   astrocyte / src.oligo. grep confirms. It may import from crucible services/ports
   (those are the domain layer being reused).

## Design Decisions (from ST 2026-06-27, not re-derivable)

- **MCP servers are thin adapters, not new logic (ST feasibility audit Q5)**:
  The domain logic (PaperMiner pipeline, VaultReadAdapter, TaskService) is
  already written and tested in project_chimera. MCP servers import and call
  it. They do NOT rewrite it. If a service needs a minor tweak (e.g., return
  type adjustment), that's acceptable; if it needs a rewrite, that's a red flag.

- **TaskService uses poll model (ST feasibility audit Q2/Q4)**:
  Claude Code cannot suspend-resume within one response. Long-running tools
  return task_id immediately. User (or Claude) polls check_task_status in a
  subsequent turn. This is functionally equivalent to oligo's AWAITING_TASK
  but split across turns instead of within one response.

- **BB persona is a skill, not a system hack (ST 2026-06-27)**:
  The "theater" UX (silent reasoning → persona-voiced stream) is retired.
  Claude Code's reasoning is transparent. BB voice is applied to the final
  output paragraph via a forced-injection skill that restyles tone without
  changing substance. Reasoning transparency is accepted as Claude Code's
  philosophy.

- **Reasoning transparency is accepted (ST 2026-06-27)**:
  oligo hid tool calls and reasoning, streaming only persona-voiced output.
  Claude Code shows everything transparently. This is a philosophical shift
  the user accepted. BB voice remains; hidden machinery does not.

- **Concurrency locks move INTO MCP servers (ST feasibility audit Q3/Q4)**:
  oligo enforced "never run daily_paper_pipeline concurrently" via the agent
  loop's concurrency_safe partition. In MCP, the server itself holds the lock
  (asyncio.Lock or file lock). The guarantee moves from "loop enforces" to
  "server enforces." More robust (can't be bypassed by a second client).

- **Vector store is Phase M+1, not Phase M (ST 2026-06-27)**:
  Semantic vault search (embedding K/T/I/D nodes, chromadb) is a new
  capability, not a migration task. Phase M migrates what exists. Semantic
  search is a new feature to add AFTER migration is stable.

## Out of Scope (→ post-migration phases)

- Semantic vault search / vector store (chromadb)
- New tools not in project_chimera (deep_research, ingest_code_to_vault)
- Obsidian plugin development
- Multi-user / auth / deployment
- Skills generalization (making the 5 skills universal for other projects)
- Phase V.C-V.G features (tool chain, image input, etc.)
