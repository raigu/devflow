---
name: pipeline
description: Drives one ticket session through the full delivery lifecycle — intake, design gate, failing acceptance tests, implementation, review, evidence, MR, CI, merge, close — with exactly two human gates (design approval, ship go-signal). Use when a ticket session starts (a HANDOFF.md says to run it), or when the user says "pipeline", "run the pipeline", or "ship this ticket".
---

# Pipeline

Run the current ticket from intake to closed, phase by phase. Made to
be the FIRST ACTION of a session spun off by `/orchestrate`, but works
standalone on any ticket.

## Phase source — read, never recite

Resolve the phase map in this order and tell the user which applies:

1. The project's CLAUDE.md phase map, when it defines one — followed
   verbatim, including its specialist agents per phase.
2. Otherwise the bundled default: [PHASES.md](PHASES.md).

Quote phase names and exit criteria from the file. Never paraphrase a
phase rule from memory — re-read the file after any compaction.

## Startup

1. Read `HANDOFF.md` (ticket docs dir or worktree root) if present —
   it carries setup, verified anchors, hard scope boundaries, and the
   reporting contract. Re-verify its code anchors before relying on
   them; they go stale as the base branch moves.
2. Read the project's CLAUDE.md for conventions: test commands, commit
   rules, MR target and language, guardrails.
3. If a `STATUS.md` reporting contract applies, write its `started`
   line IMMEDIATELY — before any other work.
4. Present the phase plan: the resolved phase list, each with goal +
   verification in one line, adapted to this ticket. Wait for the
   user's OK, then run.

## Running

- Announce each phase entry in two lines: which phase, and its exit
  criteria. No longer.
- Stop for the user ONLY at the two gates — design approval (end of
  phase 2) and the ship go-signal (phase 7). Everything else proceeds
  autonomously; blockers are reported, not silently worked around.
- On each phase transition, append a timestamped milestone to
  `STATUS.md` (e.g. `design-approved`, `tests-red`, `tests-green`,
  `review-clean`, `evidence-ready`, `mr-proposed !N`, `merged`,
  `blocked: <why>`). This is how the orchestrator tracks progress —
  it costs one line, keep it current.
- Findings outside the handoff's scope boundaries: STOP, record in
  STATUS.md, relay to the orchestrator. Never fix foreign territory.
- A failing test or red CI is diagnosed to a root cause; never
  retry-until-green.

## Done

The ticket is done when the phase map's final exit criteria hold
(default: MR merged, ticket closed with acceptance note, STATUS.md
final line written). Report completion in two lines: what shipped,
and any relayed findings.
