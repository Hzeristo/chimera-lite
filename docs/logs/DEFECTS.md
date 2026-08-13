# The named defects

> **Consumer:** anyone asking *"have we seen this shape before?"* · **Load:** read the rules and the
> Live status block; **grep the ledgers, do not read them through.** The 38 entries are an index
> into `docs/incidents/` and `docs/logs/`, not reading material.

Every incident and friction in this repo carries a **name** as well as an id. The id is for
linking; the name is for remembering. `friction-260811-01` is unmemorable and therefore
untransmissible — *the green suite that lied* is not, and you will still recognize it in November.

Names are canonical **here**, not in the individual documents. Six legacy friction logs use a
retired schema that must not be retroactively rewritten
(`.claude/skills/chimera-sprint-discipline/assets/friction-entry-template.md`), so a ledger is the
only home that can cover all of them without touching any.

**This file is two documents with different lifespans** (`PHILOSOPHY.md` §5). The rules below are
**generative** — constraints on how future defects get named; they cannot go stale and carry no
date. The ledgers are **historical** — records of what happened; the past does not move, so their
dates order them rather than expiring them. Only the short "Live status" block at the end is
**descriptive**, and it is the only part that needs re-checking.

## The rules — generative, no expiry

1. **Name the shape, not the location.** *The CRLF trap*, not *the agent frontmatter bug*. A name
   that points at a file cannot be recognized when the same failure appears somewhere else — and
   recognizing it elsewhere is the entire purpose.
2. **Two to four words, sayable out loud.** If you would not say it in conversation, it will not
   survive in memory, and a name that lives only on disk is just a second id.
3. **Name at creation, alongside the id.** A defect named weeks later is named from the write-up
   rather than from the failure, and the write-up has already smoothed it.
4. **Never rename.** Append-only, like everything else here (I0.4). A name that turned out
   imprecise gets a note, not a replacement — see *retract in place* in the README.
5. **A reused name is the escalation signal.** When a defect recurs, the new one takes the old name
   plus a marker (*…, again* / *the second …*). **Two instances is a pair; three is a class** and
   gets escalated from `docs/incidents/` to a `docs/logs/friction-*.md` with a name of its own.
   This is the mechanism, not a suggestion: *the unregistered tool* + *the CRLF trap* + one more
   became *the green suite that lied*.

## Frictions — the classes *(historical record)*

| Name | id | The shape |
|---|---|---|
| **The frontend that couldn't open a file** | `friction-260426` | The UI could not touch the filesystem, so every real task escaped to the terminal |
| **The daily report by hand** | `friction-260506` | The automation existed and was still driven manually, because its logs could not be trusted |
| **The subtree that left files behind** | `friction-260518` | A migration merge silently carried only part of a directory |
| **The mock that never passed** | `friction-260523` | A test double with no success path burned the turn limit instead of failing |
| **Reviewer Zero refuses** | `friction-260526` | The agent declined to call tools and reported the refusal as diligence |
| **The crawl that wouldn't** | `friction-260611` | The mining path returned nothing and said nothing about why |
| **The edge nobody types** | `friction-260708-01` | Typed edges must be filled by hand after writing a body; format work at the wrong moment |
| **The observer that never fires** | `friction-260709-01` | An always-active skill that was never actually triggered by the loop |
| **The untunable prompt** | `friction-260710-01` | Judgment quality buried in code, with no surface to adjust it |
| **The node without its gap** | `friction-260713-01` | Synthesis that recorded the mechanism but dropped the motivation and the payoff |
| **The box with mismatched walls** | `friction-260722-01` | A render defect that survived repeated render-and-verify passes |
| **Rules nobody checks** | `friction-260803-01` | Invariants declared in a document with no verifier — the ancestor of `ENFORCEMENT_DEBT.md` |
| **The green suite that lied** | `friction-260811-01` | "Registered" is an untested surface: components shipped unreachable with a fully green suite |

## Incidents — the events *(historical record)*

| Name | id | The shape |
|---|---|---|
| **The mimicked fence** | `2026-06-11-call-fence-parse-failure` | The model copied the example's code fence; the parser stripped it and dropped real tool calls |
| **The unreactive session** | `2026-06-11-session-reactivity` | State changed and the session did not notice |
| **The specificity tie** | `2026-06-12-btn-modifier-specificity` | Two CSS rules of equal weight; source order decided, invisibly |
| **The proxy that ate localhost** | `2026-06-17-proxy-intercept-localhost` | A system proxy intercepted a loopback connection nobody thought was proxied |
| **The silent downgrade** | `2026-06-20-ToolOutput.text-degrades-when-must_read=0` | An output quietly degraded instead of erroring when a flag was zero |
| **The wrong blue** | `2026-06-27-design-token-steel-blue` | A design token carried a colour nobody had chosen |
| **MinerU off the path** | `2026-06-30-mineru-not-on-path` | A pipeline crash from an external binary assumed present |
| **The missing prompts tree** | `2026-06-30-missing-prompts-tree` | A template directory the code required and the deploy did not carry |
| **The invisible pipeline** | `2026-06-30-pipeline-observability` | Failures that produced no output, and parallelism that was silently serial |
| **Swallowed as skip** | `2026-07-01-convert-swallow-as-skip` | A conversion failure recorded as a skip, producing hollow success |
| **The capture deadlock** | `2026-07-01-mineru-capture-deadlock` | A full pipe buffer hung the child; the parent reported success |
| **The headless hang** | `2026-07-02-mineru-hang-in-mcp-server` | Worked from a terminal, hung when spawned by the server — the environment was the variable |
| **The migration gap** | `2026-07-07-single-paper-ingest-migration-gap` | A capability that existed before the migration and not after |
| **The doubled marker** | `2026-07-13-extract-node-double-markers` | Rendering applied twice, so every list marker appeared twice |
| **The silent block** | `2026-07-13-silent-blocking-tools` | Tools that blocked for minutes with no signal that anything was happening |
| **The unregistered tool** | `2026-08-03-analyze-paper-data-unregistered` | The function existed, passed its unit tests, and was never exposed as a tool |
| **The CRLF trap** | `2026-08-10-agent-frontmatter-crlf` | `\r\n` in frontmatter silently unregistered two judgment workers for three weeks |
| **The inert flag** | `2026-08-10-mineru-3x-drift` | An upstream 3.x drift: a device flag that did nothing, a dead output path, a rude timeout |
| **The VLM that bought nothing** | `2026-08-10-mineru-backend-flip` | An expensive backend delivering no measurable gain over the cheap one |
| **The unreadable handoff** | `2026-08-10-paper-markdown-unresolvable-after-triage` | A paper that completed Path 1 could not be read by Path 2 |
| **The overreaching guard** | `2026-08-10-stage-deep-read-blocked-by-gpu-guard` | A GPU busy-guard on a tool that needed no GPU, making a whole path unreachable during any run |
| **The orphaned sidecar** | `2026-08-11-sidecar-orphaned-vram-and-lost-race` | A resident GPU process that could be stranded, and a start race lost silently |
| **The shared worktree** | `2026-08-12-parallel-executors-shared-worktree` | Parallel executors with disjoint *file* scope still share the index, the stash, and `HEAD` |
| **The prune that ate the figures** | `2026-08-12-sidecar-prune-deleted-paper-images` | An automatic duplicate-cleanup deleted the only copy of a paper's images |
| **The CRLF trap, again** | `2026-08-12-vault-query-crlf-silent-truncation` | `vault_query` returned 2 of 6 notes — the same `\r\n` shape, a different tool, two years of notes affected |

## What the ledger shows *(historical — a reading of the record above)*

Reading the names together is the point, and this pattern is visible only this way.

**Silence is this repo's dominant failure mode.** *The silent downgrade*, *swallowed as skip*, *the
invisible pipeline*, *the silent block*, *the green suite that lied*, *the CRLF trap* twice, *the
unregistered tool* — the majority of named defects here did not crash. They returned a plausible
answer and said nothing. That is not a coincidence about this codebase; it is what an epistemic
instrument fails like, and it is the argument for negative controls in one line.

This claim ages with the ledger, not with the calendar: it can only be changed by new entries, and
new entries are append-only.

## Live status *(descriptive — the only part here that can go stale)*

**Checked: 2026-08-12.** Re-verify against the tables above; do not trust these lines on sight.

- **The CRLF trap is at two instances** — agent frontmatter (2026-08-10) and `vault_query`
  (2026-08-12). By rule 5 that is a pair; **one more escalates it to a friction class of its own.**
  Worth knowing before the third, which is the entire reason this line is here.
- **The edge nobody types (`friction-260708-01`) is the live one.** Phase L.C's C.4 exists because
  of it, and C.4's semantic acceptance is still open (`TBD.md`), so the friction is not yet closed.
- **Everything else listed as RESOLVED in its source document is taken as resolved here.** This
  ledger does not re-verify resolutions; the source friction/incident file is authoritative.
