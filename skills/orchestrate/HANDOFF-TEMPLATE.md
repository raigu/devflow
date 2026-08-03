# HANDOFF.md — mandatory six sections

Write every spin-off handoff with exactly these sections, filling
project specifics from PLAN.md's Project facts. A project may name its
own handoff template in its CLAUDE.md — it then extends or replaces
this one. Keep every section short and plain: at most ~10 lines,
consequence first, no jargon the reader hasn't used. A handoff that
needs a second read has failed.

## 1. Setup

Worktree path, branch, base commit, environment/data setup specific
to the project (e.g. test database, seed data — omit what doesn't
apply), MR/PR target and language, project guardrails. Standing rule:
when the orchestrator reports a sibling merge, rebase before
continuing.

## 2. FIRST ACTION — run /pipeline

The session's first action is invoking the `pipeline` skill (same
plugin). It resolves the phase map (personal PROJECT.md → project
CLAUDE.md → bundled default), prints the phase plan, and runs to the
map's first gate. Its first phase re-verifies this handoff's code
anchors — they go stale as the base branch moves. If the pipeline
skill is unavailable in the session, fall back to doing the same by
hand: print numbered phases (goal + verification each), then run,
stopping only at the gates.

## 3. Problem

The problem in business terms first. Then verified code anchors
(file:line), each stamped with the date and base commit they were
verified against.

## 4. Scope — hard boundaries

What is IN. What is OUT — naming the neighbouring ticket/branch that
owns each out-of-scope area, and which contended files THIS ticket
owns while open (ownership passes on merge, per the orchestrator's
plan). Standing rule: a finding in foreign territory means STOP and
report to the orchestrator, never fix.

## 5. Definition of done

Tests (the project's tiers), evidence expected (e.g. browser
screenshots for UI work), MR/PR gated on the user's explicit
go-signal, the project's commit conventions. More than one MR/PR is
allowed only when stated here, with what each delivers.

## 6. Reporting contract

Keep `STATUS.md` (next to this file) current with timestamped
one-line milestones:

```
2026-08-03 10:15 started
2026-08-03 11:40 fix-ready
2026-08-03 12:05 tests-green
2026-08-03 12:30 mr-proposed <id>
2026-08-03 13:00 blocked: <why>
```

The `started` line is written IMMEDIATELY at session start, before any
other work — it is how the orchestrator knows the ticket is claimed.
A milestone is written only after the command that justifies it has
run. Custom milestone names are fine; name here any **gate
milestones** — lines other tickets wait on — so the orchestrator can
put them in its graph. List any findings the orchestrator specifically
needs relayed.
