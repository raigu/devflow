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

## Out of scope (YAGNI)

- No automatic estimate generation from history.
- No GitLab/Jira API integration inside the plugin — the project's own
  CLI/conventions are used via the Project facts.
- No cross-machine/team time aggregation.
- No hooks, no background watchers — the orchestrator acts when spoken to.

## Validation plan

1. `worktime.py` unit-sanity: run against the real July transcripts for
   the #609 period; cross-check the headline against the lived
   experience and the existing time-report data.
2. Dry-run the skill against the #609 decision log: would it have
   produced the same spin-offs/reports? Note divergences.
3. Install the plugin locally via the marketplace flow (the same way a
   recipient would) and run `/orchestrate` end-to-end on a toy list.
