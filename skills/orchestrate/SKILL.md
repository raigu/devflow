---
name: orchestrate
description: Ticket orchestrator for parallel development. Tracks an explicit list of tickets, maps dependencies and file conflicts, proposes the optimal development order, spins tickets off into git-worktree sessions with handoff files and a reporting contract, and measures efficiency (estimated hours vs real deduplicated keyboard hours). Use when the user says "orchestrate", "spin off <ticket>", "status report", or "time report".
---

# Orchestrate

Turn this session into a ticket orchestrator. State lives in
`${CLAUDE_PLUGIN_DATA}/orchestrations/<slug>/PLAN.md` (+ `TIMELOG.md`).
Nothing project-specific is hardcoded — learn conventions from the
project's CLAUDE.md and record them in PLAN.md.

## Start: `/orchestrate <ticket list>` or `/orchestrate <slug>` (resume)

Resume = read PLAN.md, refresh statuses, continue. Never re-ask
answered questions. New orchestration:

1. **Project facts** — from the project's CLAUDE.md (ask the user only
   for gaps): ticket ID format (`#630`, `KL-222`, …) and fetch command;
   worktree recipe (fallback: `git worktree add ../<repo>-<ticket> -b <ticket>`);
   per-ticket docs dir for HANDOFF/STATUS (fallback: worktree root);
   MR/PR target and language. Record in PLAN.md, plus this session's
   own working directory (needed for time attribution).
2. **Intake** — fetch every ticket. Identify shared files/modules
   (hard conflicts = same code, run serially; soft = merge-order only)
   and logical dependencies.
3. **Scores table** — `ticket | est hrs | simp 1-5 | imp 1-5 | urg 1-5 |
   now/defer | conflicts`. Estimates are human man-hours; propose,
   let the user adjust, record only confirmed values.
4. **Execution graph** — parallel NOW wave, queues behind conflicts,
   critical path. Get user approval, write PLAN.md.

PLAN.md sections: Project facts / Scores / Execution graph /
Spin-off log / Decisions (append merges, closures, scope changes,
blockers as they happen — it is the memory across compaction).

## "spin off <ticket>"

1. Create the worktree per Project facts (surface the project's own-DB /
   own-venv questions if its CLAUDE.md raises them).
2. Write `HANDOFF.md` in the ticket's docs dir following
   [HANDOFF-TEMPLATE.md](HANDOFF-TEMPLATE.md) — all six sections,
   anchors stamped with base commit and date.
3. Append to the Spin-off log: `ticket | worktree path | branch |
   base commit | session name | date`.
4. Show the user only:

   ```
   cd <worktree-path> && claude -n <ticket>-<short-slug>
   ```

   plus one line on what the session will do first (run `/pipeline`,
   which presents its phase plan and waits for OK).

Progress arrives via each ticket's `STATUS.md` (milestone lines, see
template). A ticket is claimed when its `started` line exists.

## "status report"

Refresh from every STATUS.md and the project's MR/issue tool, then
render two tables — NOW and DEFERRED — columns
`ticket | title | status | est | simp | imp | urg | conflicts`,
each followed by its execution graph. Update PLAN.md statuses.

## "time report"

Run the bundled calculator over the orchestrator workdir + every
worktree in the Spin-off log:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/worktime.py \
  --since <orchestration start date> \
  orchestrator=<orchestrator workdir> <worktree paths...>
```

Default output (the headline):
- **estimated total** — sum of confirmed estimates in scope
- **real hours** — the union figure from worktime.py (activity
  intervals from the human's message timestamps, 15-min gap rule,
  parallel sessions merged so overlapping time counts once)
- **leverage = estimated ÷ real** (e.g. 50 h estimated in 7 h real → 7×)
- period, tickets included, and the caveat: silence longer than the
  gap counts as pause — tune `--gap` if it misreads reality.

Append the report to TIMELOG.md with a timestamp.

Only when asked for **"time report detailed"**: add `--detailed` and
show per ticket `est | active hrs | wall clock (STATUS started →
merged)`, with the printed note that per-ticket hours don't sum to
the union.
