# devflow

A Claude Code plugin packaging a complete development process:

- **/orchestrate** — pick the next ticket: it tracks your ticket
  list, dependencies, and conflicts, and spins the chosen ticket off
  into its own worktree session. Also reports estimated vs real
  keyboard hours.
- **/pipeline** — develop the ticket in that session, phase by phase,
  to a merged MR/PR, stopping only at the phase map's gates.
- **/adjust** — adapt the pipeline to the project, once — each
  project needs different handling by AI tools in its phases (test
  commands, review agents, shipping rules, the phases themselves).

Project-agnostic. Conventions resolve in order: your `/adjust`
config → the project's CLAUDE.md → bundled defaults. Full design and
formats: [docs/design.md](docs/design.md).

## Install

```bash
claude plugin marketplace add raigu/devflow
claude plugin install devflow@raigu-tools
```
