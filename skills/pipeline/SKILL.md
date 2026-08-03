---
name: pipeline
description: Drives one ticket session through the full delivery lifecycle — intake, design gate, failing acceptance tests, implementation, review, evidence, MR/PR, CI, merge, close — stopping only at the gates the phase map marks. Use when a ticket session starts (a HANDOFF.md says to run it), or when the user says "pipeline", "run the pipeline", or "ship this ticket".
---

# Pipeline

Run the current ticket from intake to closed, phase by phase. Made to
be the FIRST ACTION of a session spun off by `/orchestrate`, but works
standalone on any ticket.

## Phase source — read, never recite

Resolve the phase map in this order and tell the user which applies:

1. The user's personal project config, when it defines one:
   `${CLAUDE_PLUGIN_DATA}/projects/$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/projectkey.sh)/PROJECT.md`
   (written by `/adjust`) — section `Development Phases`.
2. The project's CLAUDE.md, when it defines a phase map — recognized
   by a section titled `Development Phases` / `Phases`, or any section
   the CLAUDE.md itself calls the phase map.
3. Otherwise the bundled default: [PHASES.md](PHASES.md).

A found map is followed verbatim, including its numbering, specialist
agents, and gates. A phase entry may name how its work is done:
`run: /<command>` (invoke that skill/command for the phase instead of
re-doing its job inline) or an assigned agent (dispatch it, under the
delegation contract below). If the map doesn't mark its gates,
propose gate placement in the phase plan and let the user fix it.

Quote phase names, gates, and exit criteria from the file. Never
paraphrase a phase rule from memory — re-read the file after any
compaction. Likewise re-read the ticket's decision log after any
compaction or resume, and never re-open a Decided or Rejected item.

## Startup

1. Read `HANDOFF.md` (ticket docs dir or worktree root) if present —
   it carries setup, verified anchors, hard scope boundaries, and the
   reporting contract. Re-verify its code anchors before relying on
   them; they go stale as the base branch moves.
2. Read the conventions (same resolution order: PROJECT.md → project
   CLAUDE.md): test commands, commit rules, MR/PR target and language,
   guardrails, documented recurring defect patterns.
3. If a `STATUS.md` reporting contract applies, write its `started`
   line IMMEDIATELY — before any other work.
4. Print the phase plan and PROCEED — no waiting: one line naming
   which map applies and its source file, then the phase list (goal +
   verification in one line each, adapted to this ticket). The first
   stop is the first GATE. Wait for an OK first ONLY when the map is
   ambiguous (gates unmarked) or the handoff explicitly demands it.

## Running

- Announce each phase entry in two lines: which phase, and its exit
  criteria. No longer.
- Stop for the user ONLY at the gates the resolved phase map marks
  (bundled default: design approval and the ship go-signal).
  Everything else proceeds autonomously; blockers are reported, not
  silently worked around.
- On each phase transition, append a timestamped milestone to
  `STATUS.md` (e.g. `design-approved`, `tests-red`, `tests-green`,
  `review-clean`, `evidence-ready`, `mr-proposed <id>`, `merged`,
  `blocked: <why>`). Handoffs may define extra milestones — including
  gate milestones other tickets wait on — and a ticket may ship in
  more than one MR/PR when its handoff says so. **A milestone is
  written only after the command that justifies it has actually run**,
  and names that command so the line is auditable — e.g.
  `12:05 tests-green — npm test (0 failures)`. Every claim in any
  report must trace to a command output or a file.
- Delegating to a helper (subagent, review agent): name ONE
  deliverable and where to deliver it; the helper must explicitly
  declare the task finished. One nudge for a silent helper, then do
  the work inline and record the delegation failure in STATUS.md.
- An orchestrator line in STATUS.md (e.g. `orchestrator: <t> merged —
  rebase`) is acted on at the next phase boundary, not ignored.
- Findings outside the handoff's scope boundaries: STOP, record in
  STATUS.md, relay to the orchestrator. Never fix foreign territory.
- A failing test or red CI is diagnosed to a root cause; never
  retry-until-green. If a red looks unrelated to your change, verify
  it on the untouched base commit before debugging further — the
  environment is assumed clean, but suspicion is checked, not argued.

## Done

The ticket is done when the phase map's final exit criteria hold
(default: MR/PR merged, ticket closed with acceptance note, STATUS.md
final line written). Design-only tickets end at their agreed
deliverable instead, and **"closed as unnecessary" is a legitimate
outcome of the design gate** — record why and close. Report completion
in two lines: what shipped (or why nothing needed to), and any relayed
findings.
