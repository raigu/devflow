# devflow

The author's best practice for shipping software with AI — not a
concept, but a working process distilled from months of daily
tickets, dead ends, and reruns, packaged as a Claude Code plugin.
The leverage comes from four moves:

- **Plan the work** — order tickets so the ones that produce knowledge
  or architectural decisions run before the ones that depend on them.
- **Raise the AI's output quality** — with Claude's agent teams
  (experimental in Claude Code as of 2026 — enabled explicitly, /adjust
  handles it), specialists challenge each other's work until it holds
  up, so the first answer is already the reviewed one.
- **Shrink your part** — the skills focus your time on defining what
  DONE means, in a form the AI actually understands. The sharper the
  DONE, the more often the AI reaches it autonomously — and with the
  result you expected, on the first run. Your keyboard time goes into
  judgment, not supervision.
- **Sharpen the saw** — the evolution of your development process is
  built into the flow: the AI mines your own session histories for
  friction — every correction you made, every instruction you had to
  repeat. Every struggle becomes a lesson learned, refined into the
  project's adjustments. Every ticket you ship makes the next one
  smoother.

The author is a developer working across multiple projects, so devflow
is deliberately project-agnostic — yet tunes itself per project, and
can incorporate your custom skills and agents into the phases, with
every adjustment stored on your side, never in the repository. Your
fellow developers see clean commits, not your tooling.

Four skills, in the order you use them:

- **/adjust** — adapt the pipeline to the project, once: an interview
  that stores your adjustments per project in the plugin's data
  directory — each project needs different handling by AI tools in
  its phases (test commands, review agents, shipping rules, the
  phases themselves).
- **/orchestrate** — pick the next ticket: it tracks your ticket
  list, dependencies, and conflicts, and spins the chosen ticket off
  into its own worktree session. Also reports estimated vs real
  keyboard hours.
- **/pipeline** — develop the ticket in that session, phase by phase,
  to a merged MR/PR, stopping only at the phase map's gates.
- **/sharpen-your-saw** — close the loop: analyze the project's
  session histories (your corrections, repeated instructions,
  delegation failures) and propose improvements to the adjustments
  /adjust made — the flow tunes itself from how it actually went.

Conventions resolve in order: your `/adjust` config → the project's
CLAUDE.md → bundled defaults. Full design and formats:
[docs/design.md](docs/design.md).

## Why agent teams?

By default Claude delegates to **subagents**: atomic workers — dispatch
one, it works alone, returns one result. Fine for mechanical tasks,
blind for judgment.

**Teammates talk to each other.** Ask for a design and the pipeline
spins up an architect, a security expert, a performance expert, a
domain expert. The architect proposes; the security expert objects; the
architect refines; the performance expert pushes back — until the panel
reaches consensus. Objections that would otherwise surface in your
review surface **before the first line of code**. Better quality on the
first run, not the third.

## Install

```bash
claude plugin marketplace add raigu/devflow
claude plugin install devflow@raigu-tools
```
