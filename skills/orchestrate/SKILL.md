---
name: orchestrate
description: Ticket orchestrator for parallel development. Tracks an explicit list of tickets, maps dependencies and file conflicts, proposes the optimal development order, spins tickets off into git-worktree sessions with handoff files, reacts to merges (rebase notices, unblocked tickets), and measures efficiency (estimated hours vs real deduplicated keyboard hours). Use when the user says "orchestrate", "spin off <ticket>", "status report", or "time report".
---

# Orchestrate

Turn this session into a ticket orchestrator. State lives in
`${CLAUDE_PLUGIN_DATA}/orchestrations/<slug>/PLAN.md` (+ `TIMELOG.md`)
— formats and example lines in [PLAN-FORMAT.md](PLAN-FORMAT.md).
Nothing project-specific is hardcoded. Conventions resolve in order:
the user's personal config
`${CLAUDE_PLUGIN_DATA}/projects/$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/projectkey.sh)/PROJECT.md`
(written by `/adjust`; resolve the path in a shell first — file tools
don't expand variables or `$(...)`) → the project's CLAUDE.md →
bundled defaults.

## Start: `/orchestrate <ticket list>` or `/orchestrate <slug>` (resume)

Resume = read PLAN.md, re-check Project facts against the live
PROJECT.md/CLAUDE.md (never trust the cached copy over the live
files), refresh statuses, continue. Never re-ask answered questions. New orchestration:

1. **Project facts** — resolve per the order above (ask the user only
   for gaps, and suggest `/adjust` to persist the answers): ticket ID
   format (`#630`, `KL-222`, …) and fetch command (`glab issue view`,
   `gh issue view`, `jira issue view`, …) — no tracker: a ticket is a
   short name + description the user types once, stored in PLAN.md;
   worktree recipe — fallback: `git worktree add <path> -b <branch>`
   where branch = the ticket ID with non-branch-safe characters
   stripped (`#630` → `630`) and path = a SIBLING of the repository
   root (`git rev-parse --show-toplevel`), never relative to the
   current directory; no-worktree projects run tickets serially in
   place, conflict analysis reduced to ordering;
   per-ticket docs dir for HANDOFF/STATUS (fallback: worktree root);
   MR/PR target and language; staleness threshold (default 4 working
   hours). Record in PLAN.md, plus this session's own working
   directory (needed for time attribution).
2. **Intake** — fetch every ticket. Identify three conflict kinds:
   **hard** (same code — run serially, one owner at a time), **soft**
   (merge-order only), **append-only** (migrations, lockfiles,
   changelogs — never conflict in-branch, collide on merge; check
   after every merge). Also scan open MRs/PRs *outside* the list that
   touch the same areas — the merge queue is often the real
   bottleneck, not dev hours.
3. **Scores table** — `ticket | est hrs | simp 1-5 | imp 1-5 | urg 1-5 |
   now/defer | conflicts`. Estimates are human man-hours; propose,
   let the user adjust, record only confirmed values. NOW/DEFER
   guidance: NOW = broken core flow, data loss, or blocks the
   cluster; DEFER = convenience layers the core works without.
4. **Execution graph** — parallel NOW wave, queues behind conflicts,
   critical path. Get user approval, write PLAN.md.

## "spin off <ticket>"

1. Create the worktree per Project facts (surface the project's own
   environment questions — e.g. dedicated database/venv — if its
   CLAUDE.md raises them).
2. Write `HANDOFF.md` in the ticket's docs dir following
   [HANDOFF-TEMPLATE.md](HANDOFF-TEMPLATE.md) — all six sections,
   anchors stamped with base commit and date. A project may provide
   its own handoff template (named in its CLAUDE.md); it extends or
   replaces the bundled one.
3. Record in PLAN.md: the spin-off log row, and **ownership** of every
   contended file this ticket takes (`file | owner ticket | passes to`).
   A handoff may also declare **gate milestones** — named STATUS.md
   lines other tickets wait on — and may plan more than one MR/PR;
   record those gates in the execution graph.
4. Show the user only:

   ```
   cd <worktree-path> && claude -n <ticket>-<short-slug>
   ```

   plus one line: the session's first action is `/pipeline`, which
   prints its phase plan and runs to the first gate.

## Ticket events — react, don't just record

On every merge/close/blocked signal (from STATUS.md or the tracker):

- Update PLAN.md: statuses, graph, ownership passes to the next ticket
  in the queue.
- **Rebase notice**: append a line to the STATUS.md of every in-flight
  ticket sitting on an older base:
  `orchestrator: <t> merged as <sha> — rebase before continuing`.
- **Append-only check**: did the merge create colliding sequence
  artifacts (two migrations with one number, lockfile drift)? Surface
  immediately — this breaks every fresh branch.
- **Unblock check**: list queued tickets whose blockers are now gone
  and propose the next spin-off(s) to the user.

## Delegation and staleness

Two different relationships, two different rules. Helpers THIS
session dispatches can be nudged; spun-off ticket sessions are
launched by the user in their own terminal and cannot — for those,
the staleness rule below is the only signal.

When dispatching any helper (subagent, reviewer, teammate session):
name ONE deliverable and the exact FILE path to write it to — a file
survives a helper that goes silent; read it on the idle signal. The
helper must explicitly declare the task finished when delivering. A
silent helper gets ONE nudge; after that, do the work here and record
the delegation failure visibly in PLAN.md. Never assume a helper
reported — verify the deliverable file exists.

A spun-off ticket with no new STATUS.md milestone within the staleness
threshold is marked **stale** in the status report and surfaced to the
user — silence is never read as progress.

## "status report"

Refresh from every STATUS.md and the project's MR/issue tool, then
render two tables — NOW and DEFERRED — columns
`ticket | title | status | est | simp | imp | urg | conflicts`
(stale tickets flagged `⚠ stale <hours>h`), each table followed by its
execution graph. Update PLAN.md statuses.

## "time report"

Run the bundled calculator over the orchestrator workdir + every
worktree in the spin-off log:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/worktime.py \
  --since <orchestration start date> \
  [--gap <min, default 15>] [--floor <min, default 2>] \
  orchestrator=<orchestrator workdir> <worktree paths...>
```

(`python3` missing → try `python`.) `--gap` = silence that ends a
work interval; `--floor` = minimum credit for an isolated message.
The script EXITS NON-ZERO when a source has no transcripts or the
union is empty — fix the path and re-run; never report a leverage
ratio from a failed run. Default output (the headline):

- **estimated total** — sum of confirmed estimates in scope
- **real hours** — the union figure from worktime.py (activity
  intervals from the human's message timestamps, gap rule, parallel
  sessions merged so overlapping time counts once)
- **leverage = estimated ÷ real** (e.g. 50 h estimated in 7 h real → 7×)
- period, tickets included; flag scope changes that explain estimate
  deltas; caveat: silence longer than the gap counts as pause.

Append the report to TIMELOG.md (entry format in PLAN-FORMAT.md).

Only when asked for **"time report detailed"**: add `--detailed` and
show per ticket `est | active hrs | wall clock (STATUS started →
merged)`, with the printed note that per-ticket hours don't sum to
the union.
