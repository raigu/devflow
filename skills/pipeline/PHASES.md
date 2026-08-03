# Default phase model

Used when the project's CLAUDE.md defines no phase map of its own.
A project map, when present, wins verbatim — including its phase
numbering, names, and any specialist agents it assigns per phase.

Gates marked GATE are the only two points where the pipeline stops
for the user. Everything else proceeds without asking.

## 1. Intake

Read the ticket (and HANDOFF.md when present). Restate the scope in
business terms and map the blast radius — the models, views,
templates, tests, and migrations the change will ripple through.
**Exit:** scope + blast radius stated in two short paragraphs.

## 2. Design — GATE

Maintain a decision log (Decided / Open / Rejected — each rejection
with its reason). Express every behaviour change as a Given/When/Then
scenario. Present the decisions and the list of acceptance tests the
scenarios will become (name + one-line Given/When/Then each).
**Exit:** the user approves the decisions and the test list. This
list is the implementation contract.

## 3. Acceptance tests

Convert the approved scenarios into failing tests following the
project's test conventions (API-level where the UI is not the point).
**Exit:** the new tests fail for the right reason; existing suite
still green.

## 4. Implement

Make the contract tests green. Follow the project's coding
conventions. A new requirement discovered mid-implementation → update
the scenario and its test FIRST, then the code.
**Exit:** contract tests green, project's fast test tier green.

## 5. Review

Run the project's review mechanisms (review agents, spec-conformance
checks, linters). Fix or explicitly accept every finding.
**Exit:** no unaddressed findings.

## 6. Evidence

For user-visible changes: drive the affected screens yourself and
produce an evidence pack — before/after screenshots, console clean,
per-scenario pass/fail. Never claim a UI change works from code
reading alone; if browser automation is unavailable, say so.
**Exit:** evidence pack, or an explicit "no user-visible change".

## 7. Ship — GATE

Commit per the project's commit conventions. Push. Create the MR/PR
with a file-based description (never inline shell quoting of `$` or
newlines), in the project's language. **The user's go-signal is
required before creating/merging per the project's rules.** Then
watch CI to green — diagnose failures, never retry blind.
**Exit:** MR merged.

## 8. Close

Close the ticket with a concise acceptance note (project language),
write the final STATUS.md milestone, and relay any out-of-scope
findings to the orchestrator instead of fixing them.
**Exit:** ticket closed, STATUS.md final.
