# PLAN.md and TIMELOG.md formats

Keep these exact section names and line formats so any session (or the
user, by hand) can read and edit the files safely.

## PLAN.md

The Project facts below are EXAMPLE answers from one project (a
GitLab shop with its own worktree helper); yours will differ — e.g. a
GitHub + Jira + npm project: `ticket format: KL-<n>; fetch: jira
issue view KL-<n>`, `worktree: git worktree add ../app-KL-222 -b
KL-222`, `MR/PR target: main   # language: English`.

```markdown
# Orchestration: <slug>

## Project facts
- ticket format: #<n>          # fetch: glab issue view <n>
- worktree: gm-worktree add <t>
- docs dir: sb/<t>/
- MR/PR target: 503-develop    # language: Estonian
- staleness threshold: 4h
- orchestrator workdir: /home/user
- started: 2026-08-03

## Scores
| ticket | est hrs | simp | imp | urg | now/defer | conflicts |
|---|---|---|---|---|---|---|
| #630 | 8 | 3 | 5 | 4 | NOW | hard: #632 (api_views.py) |

## Execution graph
NOW, parallel: #630, #631
after #630: #632 -> #634 (serial, same save path)
gate: #632 waits on #630 milestone `api-settled`
critical path: #630 -> #632 -> #634 (~18h of 30h)

## Ownership
| file/area | owner | passes to |
|---|---|---|
| api_views.py save path | #630 | #632 |

## Spin-offs
| ticket | worktree | branch | base | session | date |
|---|---|---|---|---|---|
| #630 | /home/u/repo-630 | 630 | a1b2c3d | 630-sensoneo | 2026-08-03 |

## Relayed findings
| finding | from | status |
|---|---|---|
| autocomplete lacks auth | #627 | awaiting user decision |

## Decisions
- 2026-08-03 #630 spun off; owns save path while open
- 2026-08-04 #630 MERGED (!655) — rebase notices sent to #631
```

## TIMELOG.md

One entry per report, appended:

```markdown
## 2026-08-03 15:40
estimated 30h | real 6.8h | leverage 4.4x | period 07-22..08-03
tickets: #630 #631 #632 | scope changes: #632 grew (+4h, new gate)
```
