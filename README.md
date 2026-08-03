# devflow

A Claude Code plugin packaging a complete development process as two
interlocking skills:

- **/orchestrate** — cross-ticket management: tracks an explicit list
  of tickets, maps dependencies and file conflicts, proposes the
  optimal development order, spins tickets off into isolated
  git-worktree sessions with handoff files, and measures efficiency —
  estimated man-hours vs the real hours you actually spent at the
  keyboard, parallel sessions counted once.
- **/pipeline** — per-ticket delivery: drives one ticket session
  through the full lifecycle (intake → design → failing acceptance
  tests → implement → review → evidence → MR → CI → merge → close)
  with exactly two human gates: design approval and the ship
  go-signal.

Project-agnostic: ticket naming (`#630`, `KL-222`, …), fetch commands,
worktree recipes, test commands, MR conventions, and — when the
project defines one — the phase map itself are learned from the target
project's CLAUDE.md at runtime. The bundled default phase model in
`skills/pipeline/PHASES.md` applies otherwise.

## Install

```bash
claude plugin marketplace add <this-repo-url-or-path>
claude plugin install devflow@raigu-tools
```

## Use

| Command | Effect |
|---|---|
| `/orchestrate 630 631 634` | Start: fetch tickets, map conflicts, propose estimates + execution order |
| `/orchestrate <slug>` | Resume an existing orchestration |
| `spin off 631` | Worktree + HANDOFF.md + one-line session start instruction |
| `/pipeline` | (in the ticket session) resolve phase map, present phase plan, run to merged+closed |
| `status report` | NOW / DEFERRED tables + execution graphs, refreshed from STATUS.md files |
| `time report` | Estimated total vs real keyboard hours (parallel-deduplicated) + leverage ratio |
| `time report detailed` | Adds the per-ticket estimate / active / wall-clock table |

The two skills interlock through files: each spin-off's `HANDOFF.md`
tells the new session to run `/pipeline`; the pipeline writes
timestamped milestones to `STATUS.md` at every phase transition; the
orchestrator reads those for status and time reports.

State lives in `~/.claude/plugins/data/devflow/orchestrations/<slug>/`
(`PLAN.md` + `TIMELOG.md`); per-ticket `HANDOFF.md`/`STATUS.md` live in
the project's per-ticket docs directory.

## How real hours are measured

`scripts/worktime.py` (stdlib-only) reads your session transcripts in
`~/.claude/projects/`, takes the timestamps of messages *you* wrote,
chains messages less than 15 minutes apart into activity intervals
(bigger gaps = pauses, excluded automatically), and merges intervals
from all parallel sessions onto one timeline so overlapping work counts
once. Known limitation: thinking without typing for longer than the gap
reads as a pause — tune `--gap`.
