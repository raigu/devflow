---
name: adjust
description: Configure a personal devflow for the current project — custom phase map (skip/add/replace phases), ticket definition and fetch command, worktree recipe, and the other project facts. Writes per-user config keyed by the project's git remote, never touching the shared project CLAUDE.md. Use when the user says "adjust", "configure devflow", "customize phases", or when orchestrate/pipeline find no config for the project.
---

# Adjust

Interview the user and write their personal devflow configuration for
the current project. Personal means: stored in plugin data, never in
the project's shared CLAUDE.md — different developers keep different
flows on the same repo.

## Where config lives

```
${CLAUDE_PLUGIN_DATA}/projects/<key>/PROJECT.md
key = $(bash ${CLAUDE_PLUGIN_ROOT}/scripts/projectkey.sh)   # run in the repo
```

The key is the normalized git remote URL, so every clone and worktree
of the repo resolves to the same config (ssh/https forms converge).
Repos without a remote fall back to the root-path slug.

## Flow

1. Compute the key; read the existing PROJECT.md if any.
2. Show the **effective current state** per topic — what would apply
   right now after resolution (PROJECT.md → project CLAUDE.md →
   bundled defaults) and where each value comes from.
3. Interview ONLY gaps and things the user wants changed, topic by
   topic, one question at a time:
   - **Ticket**: ID format, fetch command, per-ticket docs dir.
   - **Worktree**: exact command(s); environment questions spin-offs
     must surface (dedicated DB/venv etc.).
   - **Shipping**: MR/PR target and language; staleness threshold.
   - **Phases**: start from the currently-effective map; for each
     phase offer keep / skip / replace / edit, and allow inserting new
     phases and moving gates. The RESULT is always a complete map —
     no patch syntax exists at runtime.
4. Write the full PROJECT.md (format below), show it to the user
   before saving. Re-running /adjust later edits the same file.

## PROJECT.md format

```markdown
# devflow: <human project name>
- remote: git@gitlab.example.com:gm/gm-is.git
- configured: 2026-08-03

## Project facts
- ticket format: #<n>; fetch: glab issue view <n>
- docs dir: sb/<t>/
- worktree: gm-worktree add <t>   # ask: --own-db on migrations
- MR/PR target: 503-develop; language: Estonian
- staleness threshold: 4h

## Development Phases
<complete phase map — same structure as the bundled PHASES.md:
numbered phases, GATE markers, one **Exit:** line each>
```

Omitted sections simply fall through to the project CLAUDE.md and the
bundled defaults — partial files are fine; partial PHASE maps are not
(a `## Development Phases` section, when present, is the whole map).
