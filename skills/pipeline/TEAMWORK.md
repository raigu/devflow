# Specialist teams

How the pipeline puts several specialists on one artifact (a design
under the gate, a diff under review). Referenced by the default phase
map; a project map may override any of it.

## Mode — read, don't probe

Read the user's recorded choice (the `agent teams:` Project fact,
written by /adjust):

- **enabled** → spawn specialists as named teammates — they can
  message each other, so challenge rounds are real.
- **declined or unrecorded** → k independent subagents, blind to each
  other; this session merges and judges. Never nudge the user to
  enable teams — /adjust owns that conversation.

## Recipe — dynamic, chosen per ticket

No agent files are required: a specialist is a prompt composed for
this ticket. When the project defines named agents for a phase, use
those as the panel members instead.

1. **Choose 2–4 lenses** that fit the change (correctness, data
   integrity, security, performance, UX, operability, …). Give each
   specialist ONE named deliverable.
2. **Independent pass** — each specialist reports blind to the others.
3. **Challenge round** (teams mode only) — each specialist reads the
   others' findings and challenges peer-to-peer; the challenged
   defend or concede. Exactly one round, hard stop.
4. **Verdict** — a finding survives if uncontested, or upheld by a
   majority of lenses after challenge. Contested-and-tied findings
   get ONE adversarial verify dispatch. The session decides on the
   positions that exist at the stop — no open-ended debate.
5. The delegation contract applies **per round**: one deliverable,
   explicit "finished" on delivery, one nudge for silence, then take
   the work inline and record the failure in STATUS.md.

## Model per dispatch — chosen by role, never by inheritance

Name a model on EVERY dispatch; an unnamed one silently inherits the
session's model. Match the model to the role:

- **haiku** — mechanical work: pattern sweeps, file collection,
  checklist verification.
- **sonnet** — the standard specialist lens: panel critic, scenario
  reviewer, evidence verifier. When unsure, sonnet.
- **opus** — hard judgment: adversarial verification of contested
  findings, synthesis across conflicting reports.
- **fable** — the single hardest reasoning role in the flow, at most
  one per phase (e.g. the final judge on the decision the whole
  ticket hinges on). Escalate to it deliberately, never as a default.

Escalate one tier only when the cheaper tier's failure would be
expensive to detect; downgrade freely.
