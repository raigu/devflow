# devflow

A Claude Code plugin packaging a complete development process:

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

Project-agnostic. Conventions resolve in order: your `/adjust`
config → the project's CLAUDE.md → bundled defaults. Full design and
formats: [docs/design.md](docs/design.md).

## Install

```bash
claude plugin marketplace add raigu/devflow
claude plugin install devflow@raigu-tools
```
