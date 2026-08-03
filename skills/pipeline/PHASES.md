# Default phase model

Used when neither the user's personal PROJECT.md (written by
`/adjust`) nor the project's CLAUDE.md defines a phase map — the
resolution order is always PROJECT.md → project CLAUDE.md → this
file. A found map wins verbatim — including its phase numbering,
names, and any specialist agents it assigns per phase.

Gates marked GATE are the only two points where the pipeline stops
for the user. Everything else proceeds without asking.

## 1. Intake

Read the ticket (and HANDOFF.md when present). Restate the scope in
business terms and map the blast radius — the code paths, data
shapes, tests, and any stored-state or schema change the fix will
ripple through (use the project's own structural vocabulary when its
conventions define one). When the project documents recurring defect
patterns (PROJECT.md or CLAUDE.md), list which touched spots fall
under them and state the check for each.
**Exit:** scope + blast radius stated in two short paragraphs.

## 2. Design — GATE

Open by challenging the premise: before designing anything, argue the
strongest case that this ticket needs NO code — already solved,
solvable by configuration, or not worth its cost. Dispatch the
project's critic agent for this when the phase map names one,
otherwise make the case yourself. "Closed as unnecessary" is a win,
not a failure. For a non-trivial design, run the decision log and
scenarios past a specialist panel before presenting the gate —
recipe, consensus protocol, and model ladder in
[TEAMWORK.md](TEAMWORK.md).
Maintain a decision log (Decided / Open / Rejected — each rejection
with its reason). Express every behaviour change as a Given/When/Then
scenario. Present the decisions and the list of acceptance tests the
scenarios will become (name + one-line Given/When/Then each) —
at most two plain-language lines per item, consequence first, no
jargon the user hasn't used.
**Exit:** the user approves the decisions and the test list (the
implementation contract) — OR concludes the ticket needs no code:
design-only deliverable, or "closed as unnecessary" with the reason
recorded. Both are legitimate ends of the pipeline.

## 3. Acceptance tests

Convert the approved scenarios into failing tests following the
project's test conventions (API-level where the UI is not the point).
If the project has no test harness at all, agree a written manual
verification recipe per scenario at the design gate and treat that
recipe as the contract instead.
**Exit:** the new tests fail for the right reason; existing suite
still green (or the manual recipe is written and approved).

## 4. Implement

Make the contract tests green. Follow the project's coding
conventions. A new requirement discovered mid-implementation → update
the scenario and its test FIRST, then the code.
**Exit:** contract tests green, and the project's default test
command green — if none is configured, detect it from the repo's
build files, confirm it with the user once, then reuse it.

## 5. Review

Run the project's review mechanisms (review agents, spec-conformance
checks, linters); if the project defines none, run a specialist panel
on the diff per [TEAMWORK.md](TEAMWORK.md) — a deliberate self-review
pass suffices only for trivial diffs. Fix or explicitly accept every
finding.
**Exit:** no unaddressed findings.

## 6. Evidence

Produce evidence in the form the change has: a terminal transcript
for a CLI, request/response pairs for an API, before/after output for
a library or data pipeline, before/after screenshots for a UI. Open
by checking the needed tools work (can the evidence be captured and
attached?) — if not, report and agree a fallback BEFORE doing the
phase's work. Drive the affected behaviour yourself, per-scenario
pass/fail; never claim a change works from code reading alone.
For browser-driven UIs only: the console must be clean, and a
browser-test timeout is a JS error until proven otherwise — read the
captured console before the stack trace; an uncaught JS error fails
the evidence pack.
**Exit:** evidence pack, or an explicit "no observable change".

## 7. Ship — GATE

Open by checking the shipping tools work (MR/PR creation, any
attachment upload path) — agree a fallback before starting if not.
Commit per the project's commit conventions. Push. Create the MR/PR
with a file-based description (never inline shell quoting of `$` or
newlines), written in the project's documentation language (default:
English). **The user's go-signal is required before creating/merging
per the project's rules.** Then watch CI to green — diagnose
failures, never retry blind. No CI → the project's test command run
locally is the gate. No MR/PR flow → the exit is the approved change
pushed to the target branch.
**Exit:** MR/PR merged (or the no-flow equivalent above).

## 8. Close

Close the ticket with a concise acceptance note (project language),
write the final STATUS.md milestone, and relay any out-of-scope
findings to the orchestrator instead of fixing them.
**Exit:** ticket closed, STATUS.md final.
