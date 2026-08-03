---
name: sharpen-your-saw
description: Mines this project's session histories for friction — user corrections and interruptions, repeated instructions, delegation failures, recurring defects — and proposes improvements to the project's devflow configuration (PROJECT.md), plus plugin-level notes. Use when the user says "sharpen your saw", "sharpen the saw", "improve my flow", or asks what to adjust based on past sessions.
---

# Sharpen your saw

Read what actually happened in this project's sessions and turn the
friction into configuration. Deliverable: a ranked proposal of
PROJECT.md changes (written only on the user's approval) plus
plugin-improvement notes. Helper mode (teams vs one-shot subagents)
and the model for every dispatch: per the recipe and model ladder in
[TEAMWORK.md](../pipeline/TEAMWORK.md).

## 1. Collect

Resolve the project config (PROJECT.md → project CLAUDE.md → bundled
defaults). Sources: the repo's `git worktree list` paths, the current
directory, and any worktrees named in orchestration PLAN.md spin-off
logs. Then:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/digest.py \
  --out <dir> --since <date> <source paths...>
```

`--out` = a fresh subdirectory of the session's scratchpad/temp
directory (`--since` is optional; use it to skip long-dead history).

Digests hold only the human's messages plus counts — raw transcripts
never enter any context window. Non-zero exit = fix the paths, don't
proceed on partial data.

## 2. Harvest — haiku, 2–4 workers

Split the digest files among the workers. ONE deliverable each:
`category | evidence (quoted line + date) | suggested lever`.
Categories: correction/interruption, instruction repeated across
sessions, delegation failure, tool breakage, re-asked question,
estimate-vs-actual gap, recurring defect. Delegation contract
applies.

## 3. Synthesize — sonnet

Cluster the union, dedupe, and keep only patterns with ≥2
independent occurrences — single events are listed as observations,
never acted on. Map each pattern to a lever: Project fact | phase
edit | defect pattern | handoff tweak | plugin note.

## 4. Optimize — opus

Draft the concrete change per lever: exact PROJECT.md lines (a phase
edit yields the complete new map, never a fragment), ranked by user
time saved. Plugin-shaped findings become notes, never file edits.

## 5. Review — panel per TEAMWORK.md

Panel the draft. One additional hard check: nothing a gravestone
forbids — the plugin design doc's YAGNI/rejected list, the project's
decision-log Rejected sections, and facts the user already declined
(e.g. `agent teams: declined`). A rejected idea may return only
under an explicit "previously rejected — new evidence:" heading.

## 6. Propose

Present the ranked items, at most two lines each: the friction
(quoted evidence) → the change. The user picks. Write PROJECT.md the
/adjust way — show the full file before saving. Plugin notes are
reported separately; they are for the user to act on, never written
anywhere by this skill.
