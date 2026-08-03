# orchestrate

A Claude Code plugin that turns one session into a **ticket
orchestrator**: it tracks an explicit list of tickets, maps their
dependencies and file conflicts, proposes the optimal development
order, spins tickets off into isolated git-worktree sessions with
handoff files and a reporting contract, and measures your efficiency —
estimated man-hours vs the real hours you actually spent at the
keyboard, parallel sessions counted once.

Project-agnostic: ticket naming (`#630`, `KL-222`, …), how to fetch a
ticket, and how to create a worktree are learned from the target
project's CLAUDE.md at runtime.

## Install

```bash
claude plugin marketplace add <this-repo-url-or-path>
claude plugin install orchestrate@rait-tools
```

## Use

| Command | Effect |
|---|---|
| `/orchestrate 630 631 634` | Start: fetch tickets, map conflicts, propose estimates + execution order |
| `/orchestrate <slug>` | Resume an existing orchestration |
| `spin off 631` | Worktree + HANDOFF.md + one-line session start instruction |
| `status report` | NOW / DEFERRED tables + execution graphs, refreshed from STATUS.md files |
| `time report` | Estimated total vs real keyboard hours (parallel-deduplicated) + leverage ratio |
| `time report detailed` | Adds the per-ticket estimate / active / wall-clock table |

State lives in `~/.claude/plugins/data/orchestrate/orchestrations/<slug>/`
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
