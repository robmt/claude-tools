# claude-tools — Project Overview

A small **Claude Code plugin marketplace** owned by Robert Thomas. Distributes personal Claude Code plugins via `/plugin marketplace add robmt/claude-tools`.

## Purpose
Hosts plugins (currently `bullpen` and `lineup`) that implement a baseball-themed workflow for design + iterative implementation:
- **bullpen** — lightweight design conversation that produces a small bullpen artifact (forked from `obra/superpowers` brainstorming, with global+per-repo config, repo-name nesting, separate commit flags, and an `autoContinue` setting).
- **lineup** — companion that manages a rolling 3-slot view (At Bat / On Deck / In the Hole) toward a bullpen's destination. Includes `lineup` (reviewer), `at-bat` (implementer with red/green tests + testability gate), and `postmortem` skills.

## Repo layout
```
.claude-plugin/marketplace.json   # marketplace manifest
plugins/<name>/
  .claude-plugin/plugin.json      # per-plugin manifest
  README.md
  skills/<skill>/SKILL.md         # primary unit; may include templates/, helpers
  scripts/                        # optional plugin helpers (Python)
docs/bullpen/<date>-<slug>/       # bullpen artifacts (this repo eats its own dogfood)
CONTRIBUTING.md                   # how to add/update plugins
README.md                         # plugin table + install instructions
```

## Plugins
- **bullpen** v1.0.1 — skills: `bullpen`, `bullpen-setup`. Has `scripts/resolve-config.py` that merges `~/.bullpen.json` (global) + `<repoRoot>/.bullpen.json` (per-repo) over hardcoded defaults, with legacy fallbacks for `.spitball.json`, `commitSpitball`, `autoCommit`.
- **lineup** v1.3.0 — skills: `at-bat`, `lineup`, `postmortem`. Mirrors bullpen's `resolve-config.py` pattern.

Both plugins use `.bullpen.json` config; lineup reuses the same file.
