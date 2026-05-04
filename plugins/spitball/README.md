# spitball

A lightweight design conversation. The output is a small artifact called a
*spitball*: a design captured at the depth we honestly know it, no further.
We don't write hundreds of lines of forward plan that won't survive contact
with reality.

Forked from `obra/superpowers/skills/brainstorming`. Intentional changes:

- Configurable save location (per-repo or central with optional repo-name nesting).
- The skill stops after the spitball is written; it does not auto-invoke any
  planning or implementation skill. Continuation is the user's call.
- The visual companion (browser-based mockups) was removed — text-only.

## Install

```bash
/plugin install spitball@claude-tools
```

Requires `python3` and `git` on PATH (used by the config-resolution helper script).

## Configuration

Two files, merged per-key:

- `~/.spitball.json` — global default for every project.
- `<repoRoot>/.spitball.json` — per-repo override.

The fastest path is to run the `spitball-setup` skill, which asks scope
(global vs. this repo) first and writes to the right file:

> "Set up spitball"

Or write the file yourself. Global example for a shared, central save dir:

```json
{
  "saveDir": "/mnt/notes/spitballs",
  "autoCommit": false,
  "nestUnderRepoName": true
}
```

With `nestUnderRepoName: true`, spitballs land at
`<saveDir>/<repo-name>/YYYY-MM-DD-<topic>/spitball.md`, where `<repo-name>`
is parsed from `git remote get-url origin` (e.g., `robmt-claude-tools`),
falling back to the repo basename. Lineup discovery honors the same flag.

If both files are absent, defaults apply (`saveDir`: `docs/spitballs/`,
`autoCommit`: `true`, `nestUnderRepoName`: `false`). See
`skills/spitball/configuration.md` for the full schema.

## Layout

```
plugins/spitball/
  .claude-plugin/plugin.json
  README.md
  skills/spitball/
    SKILL.md                       # the skill itself
    configuration.md               # config schema and resolution rules
    spitball-reviewer-prompt.md    # subagent prompt for self-review
  skills/spitball-setup/
    SKILL.md                       # configuration wizard
  scripts/
    resolve-config.py              # merges global+per-repo config, derives repo name
```

## Attribution

Original brainstorming skill is from
[obra/superpowers](https://github.com/obra/superpowers). This plugin is a
fork at commit `6efe32c9`.
