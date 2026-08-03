# Orchestrate plugin — design

Date: 2026-08-03. Status: approved design, pre-implementation.

## Purpose

A shareable Claude Code plugin that turns one Claude session into a
**ticket orchestrator**: it tracks a set of tickets, maps their
relationships and dependencies, proposes the optimal development order,
spins tickets off into isolated worktree sessions with handoff files,
collects progress reports back, and measures efficiency — estimated
hours vs the real hours the human actually spent at the keyboard,
parallel work counted once.

Extracted from the proven "#609 orchestration" practice (2026-07), but
**project-agnostic**: everything project-specific (ticket naming, how to
fetch a ticket, how to create a worktree) is discovered from the target
project's CLAUDE.md at runtime, never hardcoded.

## Packaging

Plugin (not a bare skill), so it can be shared, versioned, and updated:

```
orchestrate-plugin/                  # git repo = marketplace + plugin
├── .claude-plugin/
│   ├── plugin.json                  # name: orchestrate
│   └── marketplace.json             # lists this repo's own plugin
├── skills/
│   └── orchestrate/
│       └── SKILL.md                 # the orchestrator skill
├── scripts/
│   └── worktime.py                  # active-hours calculator (stdlib only)
├── docs/
│   └── design.md                    # this file
└── README.md                        # install + usage
```

Install (self and others): `claude plugin install` from this repo as a
marketplace. One canonical path — the author installs the same way as
everyone else.

## State

All mutable state lives in `${CLAUDE_PLUGIN_DATA}` (resolves to
`~/.claude/plugins/data/orchestrate/`), the documented plugin-data
convention. Survives plugin updates; removed on uninstall.

```
${CLAUDE_PLUGIN_DATA}/
└── orchestrations/<slug>/
    ├── PLAN.md          # single source of truth (below)
    └── TIMELOG.md       # appended by every time report
```

`PLAN.md` sections:

1. **Project facts** (learned once at start, from the project's
   CLAUDE.md + user answers): ticket ID convention (e.g. `#630`,
   `KL-222`), fetch command (e.g. `glab issue view`, `jira issue view`),
   worktree recipe, handoff/status file location convention, MR/PR
   target.
2. **Scores table**: `ticket | est hrs | simplicity | importance |
   urgency | now/defer | conflicts`. Estimates proposed by Claude,
   confirmed/adjusted by the user. Estimates are *human man-hours*.
3. **Execution graph**: which tickets run now in parallel, what queues
   behind what, the critical path.
4. **Spin-off log**: `ticket | worktree path | branch | base commit |
   session name | spun-off date`. The worktree path is the anchor that
   later ties transcripts to tickets for time measurement.
5. **Decisions / events**: merges, closures, scope changes, blockers —
   appended as they happen (the #609 decision-log habit).

Per-ticket `HANDOFF.md` and `STATUS.md` live where the **project**
keeps per-ticket docs (in gm-is: `sb/<ticket>/`). Fallback when the
project defines nothing: the ticket's worktree root.

## Skill behaviour

Invocation: `/orchestrate <ticket list>` (explicit list — the only
scope source) or `/orchestrate <slug>` to resume.

### Start / resume

- New: read project CLAUDE.md → record Project facts; fetch each
  ticket; analyze relationships (shared files/modules → hard or soft
  conflicts; logical dependencies); propose the scores table and
  execution graph; user approves; write PLAN.md.
- Resume: read PLAN.md, refresh statuses, continue. Never re-ask
  answered questions.

### "spin off <ticket>"

1. Create worktree per the project's recipe (own DB / own venv
   questions per project rules; fallback `git worktree add`).
2. Write `HANDOFF.md` with the six mandatory sections (generalized
   from the #609 standing rules):
   1. **Setup** — worktree path, branch, base commit, test DB, MR/PR
      target, project guardrails.
   2. **FIRST ACTION: present your phase plan** — the session shows its
      numbered phase plan (goal + verification per phase) and waits for
      the user's OK before touching code. Handoff carries an adaptable
      baseline plan; anchors must be re-verified (they go stale).
   3. **Problem in business terms**, then verified code anchors
      (file:line) stamped with date + base commit.
   4. **Scope with hard boundaries** — IN, OUT, which neighbouring
      ticket owns each out-of-scope area; foreign findings → STOP and
      report, don't fix.
   5. **Definition of done** — tests, evidence, MR gated on the user's
      go-signal, project commit conventions.
   6. **Reporting contract** — timestamped one-line milestones in
      `STATUS.md` (`started`, `fix-ready`, `tests-green`,
      `mr-proposed`, `blocked: <why>`, …). `started` is written
      IMMEDIATELY at session start — it is how the orchestrator knows
      the ticket is claimed.
3. Record the spin-off in PLAN.md.
4. Print the start instruction (default model, no extra flags):

   ```
   cd <worktree-path> && claude -n <ticket>-<slug>
   ```

### "status report"

Two tables — NOW and DEFERRED — columns
`ticket | title | status | est | simp | imp | urg | conflicts`, each
followed by its execution graph. Statuses refreshed from every
`STATUS.md` plus the project's MR/issue tool before rendering.

### "time report"

Default output is the **headline**:

- estimated total (sum of confirmed estimates for tickets in scope)
- **real hours** — the human's actual keyboard time, parallel sessions
  deduplicated (see worktime.py)
- **leverage ratio** = estimated total ÷ real hours (e.g. 79 h estimated
  delivered in 20 h real → 4×)
- period covered, tickets included

Appended to TIMELOG.md with a timestamp so history accumulates.

"time report detailed" adds the per-ticket table:
`ticket | est | active hrs | wall clock (started→merged)` — with the
printed caveat that per-ticket active hours do NOT sum to the real
total (overlap is deduplicated only in the union).

## worktime.py — active-hours calculation

Stdlib-only Python; deterministic; ~zero tokens per report.

- **Input**: the transcript directories to scan (the orchestrator's own
  project dir + one per spun-off worktree, derived from PLAN.md's
  spin-off log by encoding the path the way `~/.claude/projects/` does),
  `--since/--until`, `--gap` (default 15 min), `--floor` (default 2 min),
  `--detailed`, `--json`.
- **Signal**: timestamps of *user* messages only (assistant/tool
  activity proves nothing about the human).
- **Intervals**: consecutive user messages ≤ gap apart chain into one
  interval; a larger gap closes it (pauses, lunch, idle days fall out
  automatically). A lone message gets the floor duration.
- **Union**: all intervals from all in-scope sessions merged on one
  timeline; overlaps count once → real hours.
- **Per-source**: same interval logic per transcript dir → per-ticket
  active hours (for the detailed report).
- **Output**: markdown table or JSON: real total, per-source actives,
  message counts, period.

Known limitation (stated in the report footer): thinking/reading
without typing for longer than the gap counts as a pause; the gap is a
flag if reality differs.

## Out of scope (YAGNI) — each with its reason, so none is re-proposed

- No automatic estimate generation from history — estimates are a
  human judgment the user confirms; history is too thin to beat that.
- No GitLab/Jira API integration inside the plugin — the project's own
  CLI/conventions are used via the Project facts.
- No cross-machine/team time aggregation — single-user tool by design.
- No hooks, no background watchers — the orchestrator acts when spoken to.
- **REJECTED (2026-07-24, do not re-propose): per-interaction user
  activity logging** for time tracking — tried in the #609 practice
  and retracted the same day; token cost not worth it. Real hours are
  estimated from message-timestamp density instead (worktime.py).
- **Deferred, deliberate: pass@3 racing** (three worktrees attacking
  one frozen test contract, judge picks the winner) — a possible
  future third skill; not built until the two-skill flow is proven.

## Addendum 2026-08-03 — devflow (v0.2)

Approved extension: the plugin becomes the **development-process
plugin `devflow`** (repo `devflow-plugin/`, marketplace renamed to
**raigu-tools**), containing two interlocking skills:

- **orchestrate** — unchanged (cross-ticket: order, spin-offs,
  tracking, efficiency).
- **pipeline** (new) — runs inside one ticket session and drives the
  full lifecycle. Phase map resolution: the project's CLAUDE.md phase
  map wins verbatim when present; otherwise the bundled
  `skills/pipeline/PHASES.md` default (the eight phases, generalized:
  intake → design → acceptance tests → implement → review → evidence
  → ship → close). Exactly two human gates: design approval (end of
  design phase, includes the failing-test contract) and the ship
  go-signal (before MR/merge). Phase entries announced in two lines,
  quoted from the file, never from memory. STATUS.md milestones are
  written automatically at phase transitions, which is what the
  orchestrator's tracking consumes.

Interlock: the orchestrate HANDOFF template's section 2 changes from
"present your phase plan" to "FIRST ACTION: run /pipeline" (manual
fallback documented for sessions without the plugin).

## Addendum 2026-08-03 — v0.3, review round

Four parallel reviewers (insights-coverage, lessons-conformance,
project-agnosticism, extensibility) audited v0.2; the user triaged
the findings. Changes:

- **Cross-ticket coordination layer** (was lost in generalization):
  the orchestrator reacts to merges — rebase notices appended to
  in-flight tickets' STATUS.md, append-only artifact collision check
  (migrations/lockfiles), unblock proposals; three-kind conflict
  model (hard / soft / append-only); merge-queue scan of open MRs/PRs
  outside the ticket list; contended-file ownership tracked in
  PLAN.md and passed on merge; handoff-declared gate milestones and
  multi-MR tickets.
- **Delegation contract** (both skills): one named deliverable per
  helper, explicit "task finished" declaration on delivery, one nudge
  for silence, then inline takeover with a visible failure record.
  Staleness rule: no milestone within the threshold (Project fact,
  default 4 working hours) → ticket shown stale, never "in progress".
- **Extensibility wiring**: gates read from the resolved phase map
  (no hardcoded phase numbers); concrete phase-map detection
  convention (a CLAUDE.md section titled "Development Phases"/"Phases"
  or explicitly so labeled); project-supplied handoff templates;
  PLAN/TIMELOG formats specified with examples (PLAN-FORMAT.md);
  --gap/--floor documented at the skill surface.
- **Pipeline hardening**: base-commit check only when a red looks
  suspicious (master assumed green — user decision); tool preflight
  in evidence and ship phases; honest milestones (written only after
  the justifying command ran); design-only and closed-as-unnecessary
  outcomes; decision log re-read after compaction; browser-console-
  before-traceback rule; review-phase fallback to self-review.
- **Brevity + clarity ceilings**: handoff sections ≤ ~10 plain lines,
  design-gate items ≤ 2 lines, consequence first, no unshared jargon.
- Kept as-is per user decision: the handoff template's example
  environment fields (test database etc.) — worded as examples, fine.

## Addendum 2026-08-03 — v0.4, /adjust and personal config

Decision: per-project customization is PERSONAL, not shared — the
project CLAUDE.md is a team file and different developers keep
different flows. Therefore:

- New third skill **/adjust**: interviews the user and writes
  `${CLAUDE_PLUGIN_DATA}/projects/<key>/PROJECT.md` — project facts
  plus a complete personal phase map (phase edits are applied at
  write time; no patch syntax exists at runtime, keeping one canonical
  mechanism).
- **Key** = normalized git remote URL (`scripts/projectkey.sh`);
  ssh/https converge, all clones and worktrees share the config.
  Fallback: repo root path slug.
- **Resolution order everywhere**: PROJECT.md (personal) → project
  CLAUDE.md (team) → bundled defaults. Partial PROJECT.md files fall
  through per topic; a `Development Phases` section is always a whole
  map, never a fragment.

## Addendum 2026-08-03 — v0.5, second review round

Two reviewers (project-agnosticism; insights-coverage) audited v0.4;
the user approved all findings (TULD). Changes:

- **De-Djangoed the default phase map**: intake blast radius in
  stack-neutral nouns; evidence in the form the change has (terminal
  transcript / request-response / screenshots), the JS-console rule
  scoped to browser UIs; escape hatches for projects with no test
  harness (manual verification recipe as the contract), no CI (local
  test command is the gate), no MR/PR flow (push to target branch);
  "fast test tier" → detected/confirmed default test command;
  MR/PR text in the documentation language (default English).
- **Third stop removed**: /pipeline prints the phase plan and runs to
  the first gate; it waits for an OK only when the map is ambiguous
  or the handoff demands it. Two gates means two.
- **Phase wiring**: a phase map entry may carry `run: /<command>` or
  name an agent — the pipeline invokes it instead of re-doing the
  work in prose. /adjust asks per phase whether an existing command
  covers it.
- **Recurring defect patterns** got a home: a PROJECT.md section +
  /adjust question; intake's defect-pattern check now has a socket.
- **Premise challenge**: the design gate opens by arguing the ticket
  needs no code (critic agent when the map names one) — the practice
  that closed #613 as unnecessary is now driven, not just permitted.
- **Auditable milestones**: each STATUS.md milestone names the
  command that justifies it.
- **worktime.py hardened**: `~` expansion, non-alphanumeric path
  chars encoded, `CLAUDE_CONFIG_DIR` honored, and hard non-zero exit
  on missing/empty sources or an empty union — a mistyped worktree
  can no longer yield a fabricated leverage ratio.
- **Examples labeled**: PROJECT.md / PLAN.md example facts marked as
  one project's answers with a GitHub+Jira+npm contrast; no-tracker
  and no-worktree modes documented; branch-safe worktree fallback
  (`#630` → branch `630`, sibling of the repo root); resolution order
  stated identically in all four files; bash/python3 fallbacks noted.
- **Hooks rejection re-scoped** (recorded, not implemented): the
  standing "no hooks, no background watchers" rejection covers
  orchestrator polling. Lint-style defect-pattern gates were NOT
  rejected — they are served by the Recurring defect patterns config
  checked at intake/review; shipping actual hook files remains open
  for a future version if prose checks prove insufficient.
- README states the email→issue exclusion as deliberate.

## Addendum 2026-08-03 — v0.6, specialist teams in the default phases

Decision (option A of the teams discussion; pass@k racing stays in
the gravestones as deferred): the default phases gain **dynamic
specialist teams** — no bundled agent files; a specialist is a prompt
composed per ticket. New `skills/pipeline/TEAMWORK.md` holds the
recipe, referenced from the design gate (panel on the decision log)
and the review phase (panel on the diff):

- **Mode from config, never probed**: /pipeline reads the
  `agent teams:` Project fact. Enabled → named teammates with a real
  peer challenge round (the agent-teams feature,
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, experimental and
  off-by-default). Declined/unrecorded → k independent blind
  subagents, the session merges and judges. Consensus is a fixed
  protocol (independent pass → one challenge round → majority
  verdict, one adversarial verify for ties, hard stop) — structure,
  not open-ended chat. Delegation contract applies per round.
- **Model ladder, no inheritance**: every dispatch names its model —
  haiku (mechanical) / sonnet (standard lens, the when-unsure
  default) / opus (hard judgment) / fable (single hardest role, at
  most one per phase, deliberate escalation only). Rationale:
  teammates silently inherit the session's model otherwise.
- **/adjust agent-teams preflight**: checks the env var and the user
  settings `env` block; if off, states in two lines what /pipeline
  loses and offers to enable permanently (settings edit only on an
  explicit yes; experimental; new sessions only). The answer is
  recorded as the `agent teams:` fact — a recorded "declined" is
  never re-asked.

## Validation plan

1. `worktime.py` unit-sanity: run against the real July transcripts for
   the #609 period; cross-check the headline against the lived
   experience and the existing time-report data.
2. Dry-run the skill against the #609 decision log: would it have
   produced the same spin-offs/reports? Note divergences.
3. Install the plugin locally via the marketplace flow (the same way a
   recipient would) and run `/orchestrate` end-to-end on a toy list.
