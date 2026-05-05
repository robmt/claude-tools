# bullpen

A lightweight design conversation. The output is a small artifact called a
*bullpen*: a design captured at the depth we honestly know it, no further.
We don't write hundreds of lines of forward plan that won't survive contact
with reality.

Forked from `obra/superpowers/skills/brainstorming`. Intentional changes:

- Configurable save location (per-repo or central with optional repo-name nesting).
- The skill stops after the bullpen is written; it does not auto-invoke any
  planning or implementation skill. Continuation is the user's call.
- The visual companion (browser-based mockups) was removed - text-only.

## Install

```bash
/plugin install bullpen@claude-tools
```

Requires `python3` and `git` on PATH (used by the config-resolution helper script).

## Configuration

Two files, merged per-key:

- `~/.bullpen.json` - global default for every project.
- `<repoRoot>/.bullpen.json` - per-repo override.

The fastest path is to run the `bullpen-setup` skill, which asks scope
(global vs. this repo) first and writes to the right file:

> "Set up bullpen"

Or write the file yourself. Global example for a shared, central save dir:

```json
{
  "saveDir": "/mnt/notes/bullpen",
  "commitBullpen": false,
  "commitAtBat": true,
  "nestUnderRepoName": true,
  "autoContinue": "prompt"
}
```

With `nestUnderRepoName: true`, bullpens land at
`<saveDir>/<repo-name>/YYYY-MM-DD-<topic>/bullpen.md`, where `<repo-name>`
is parsed from `git remote get-url origin` (e.g., `robmt-claude-tools`),
falling back to the repo basename. Routing markers like Azure DevOps's
`_git/`, Bitbucket Server's `scm/`, and Azure SSH's `v3/` are stripped,
so URLs like `https://dev.azure.com/org/project/_git/repo` produce
`project-repo`. Lineup discovery honors the same flag.

If both files are absent, defaults apply (`saveDir`: `docs/bullpen/`,
`commitBullpen`: `true`, `commitAtBat`: `true`, `nestUnderRepoName`:
`false`, `autoContinue`: `"prompt"`). The legacy `commitSpitball` and
`autoCommit` keys still work as synonyms for `commitBullpen`, and
`.spitball.json` is read as a fallback when `.bullpen.json` is absent
(rename the file at your convenience). See
`skills/bullpen/configuration.md` for the full schema.

## Layout

```
plugins/bullpen/
  .claude-plugin/plugin.json
  README.md
  skills/bullpen/
    SKILL.md                       # the skill itself
    configuration.md               # config schema and resolution rules
    bullpen-reviewer-prompt.md    # subagent prompt for self-review
  skills/bullpen-setup/
    SKILL.md                       # configuration wizard
  scripts/
    resolve-config.py              # merges global+per-repo config, derives repo name
```

## Attribution

Original brainstorming skill is from
[obra/superpowers](https://github.com/obra/superpowers). This plugin is a
fork at commit `6efe32c9`.
