# HANDOFF.md — mandatory six sections

Write every spin-off handoff with exactly these sections, filling
project specifics from PLAN.md's Project facts.

## 1. Setup

Worktree path, branch, base commit, test database, MR/PR target and
language, project guardrails (off-limits areas, package/migration
rules).

## 2. FIRST ACTION — present your phase plan

The session must display its numbered solution phases (each phase =
goal + how it is verified + which subagents it uses) and WAIT for the
user's OK before touching code. Include an adaptable baseline phase
list. First phase always re-verifies this handoff's code anchors —
they go stale as the base branch moves.

## 3. Problem

The problem in business terms first. Then verified code anchors
(file:line), each stamped with the date and base commit they were
verified against.

## 4. Scope — hard boundaries

What is IN. What is OUT — naming the neighbouring ticket/branch that
owns each out-of-scope area. Standing rule: a finding in foreign
territory means STOP and report to the orchestrator, never fix.

## 5. Definition of done

Tests (the project's tiers), evidence expected (e.g. browser
screenshots for UI work), MR/PR gated on the user's explicit
go-signal, the project's commit conventions.

## 6. Reporting contract

Keep `STATUS.md` (next to this file) current with timestamped
one-line milestones:

```
2026-08-03 10:15 started
2026-08-03 11:40 fix-ready
2026-08-03 12:05 tests-green
2026-08-03 12:30 mr-proposed !123
2026-08-03 13:00 blocked: <why>
```

The `started` line is written IMMEDIATELY at session start, before any
other work — it is how the orchestrator knows the ticket is claimed.
List any findings the orchestrator specifically needs relayed.
