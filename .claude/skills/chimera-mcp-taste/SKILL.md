---
name: chimera-mcp-taste
description: MCP-server-layer engineering discipline — the class of bugs where the code is correct but the MCP runtime changes its behavior. Invoke whenever writing, reviewing, or debugging code that runs as an MCP server, or when a tool "works when I run it in a shell but not as an MCP tool." Trigger on .mcp.json, an mcp-servers/ dir, FastMCP imports, a @mcp.tool that shells out / reads env vars / imports a heavy stack, or a hang/silent-failure that only appears under the server. Enforces venv interpreter resolution, env-var binding, child output sinks, headless-spawn isolation, direct-before-transport bisection, thin adapters, and lazy heavy deps.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Write
  - Agent
  - Bash
  - PowerShell(nvidia-smi:*, pytest:*, ruff:*, git diff:*, git show:*, git status:*)
---

<skill_identity>
MCP-server-layer taste arbiter. Guards the seam between correct domain code and the
runtime that hosts it. Applies when code executes inside an MCP server process rather
than a shell — a different PATH, no console, stdio bound to JSON-RPC, a launcher-provided
environment. Reviews and edits code; every MCP-layer claim it makes it also PROVES.
Applies to both repos (chimera-lite primary; project_chimera archived — skills are shared).
</skill_identity>

<the_thesis>
**The code is correct. The MCP environment changes its behavior.**

These bugs do not appear in normal coding. They appear only when the exact same code runs
as an MCP server, because the server process is *not* your shell:

- its **PATH** is the launcher's (Claude Code / anaconda / system), not your activated venv;
- it has **no console** — a console-subsystem child auto-allocates one and can hang;
- its **stdin/stdout are the JSON-RPC transport**, not a terminal;
- its **environment** is whatever `.mcp.json` + the launcher hand it, not your `.bashrc`;
- it imports the **whole tool module at startup**, so a heavy top-level import sinks the server.

The failure signature is always the same: *"it works when I run it, but not as a tool."*
The instinct to rewrite the (correct) domain logic is the trap. The fix is at the seam.
</the_thesis>

<core_principles>
1. **Interpreter resolution** — resolve venv executables from `sys.executable`, never a bare PATH lookup.
2. **Env-var binding** — an env var only counts if it maps to a real config field; prove it with a NON-DEFAULT value.
3. **Progress observability** — a captured/non-TTY child hides tqdm; emit stage-level stderr logs, accept per-page loss.
4. **Child output sink** — never `capture_output=True` for a chatty child; never `sys.stdout` in an stdio MCP server.
5. **Headless-spawn isolation** — a console child from a console-less server needs `CREATE_NO_WINDOW` + detached stdin.
6. **Asset migration** — logic migrates, assets don't; verify every prompt/template/config resolves before smoke.
7. **Venv independence** — build the venv on a standalone interpreter, not the base anaconda/system one.
8. **Direct before transport** — verify the domain call directly first; if only the transport fails, the bug is the seam.
9. **Thin adapter** — the server module is <200 lines of contract + delegation; the concurrency lock is the one exception.
10. **Heavy deps lazy + optional** — ML stacks import inside the function and raise a clear NotInstalled error.
</core_principles>

<when_this_applies>
Activate when any of these are in view:
- `.mcp.json`, an `mcp-servers/` directory, or `from mcp.server.fastmcp import FastMCP`.
- A `@mcp.tool` body that shells out (`subprocess`), reads env/config, or imports torch/MinerU/an ML stack.
- A reported hang, 0-CPU stall, or *silent* wrong result that only reproduces under the server
  (the tell: it runs fine from the shell / a direct python call).
- Migrating domain code onto MCP (Phase M): interpreter, env, assets, and transport all shift at once.
</when_this_applies>

<verification_first>
**Every MCP-layer claim must be checkable. Inference is not evidence.**

The GPU scare (audit I-2) is the cautionary tale: three-way reasoning from the code —
nvidia-smi showed `anaconda\python.exe` as the compute process — nearly filed a verdict of
"CUDA wasted, CPU fallback." One `nvidia-smi` during an actual convert settled it in seconds:
VRAM climbed 1.7 GB → 7 GB, power 15 W → 74 W. GPU real; the anaconda path was a benign
reporting artifact of a base-coupled venv (a *different*, real bug — principle 5).

So: do not argue about MCP-layer behavior from the source. Run the check that makes the
difference observable. `references/verification.md` gives the proof procedure for each rule
(nvidia-smi for the interpreter/GPU, a non-default env object for binding, a headless MCP
client for the spawn/output rules, direct-before-transport for bisection).
</verification_first>

<rules_summary>
Full rules with real bad/good code: `references/mcp_rules.md`.
How to PROVE each (and the anti-patterns): `references/verification.md`.

**Quick do:**
- Resolve tools via `sys.executable`'s dir, not PATH.
- Test env overrides with a NON-DEFAULT value.
- Redirect chatty children to a temp file (or `sys.stderr`).
- Spawn console children with `CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP`, `stdin=DEVNULL`.
- Call the domain function directly before blaming the tool.
- Keep the server module a thin adapter; lazy-import heavy deps.

**Quick do-not:**
- `shutil.which("tool")` with no venv-sibling fallback.
- Assume an env var bound because "it runs" (default == intended hides the no-op).
- `subprocess.run(..., capture_output=True)` on a uvicorn/tqdm child.
- Redirect a child to `sys.stdout` in a stdio MCP server (corrupts JSON-RPC).
- Rewrite correct domain logic to chase a transport-only failure.
- `import torch` / `import mineru` at module top of the server.
</rules_summary>
