---
name: spitball-setup
description: "Configure the spitball skill. Use when the user says 'configure spitball', 'set up spitball', 'spitball setup', 'spitball first run', 'where should spitballs go', or wants to change spitball defaults (save directory, auto-commit, central vs per-repo storage). Writes `~/.spitball.json` (global default) or `<repoRoot>/.spitball.json` (per-repo override) depending on scope chosen by the user."
---

# Spitball Setup

A short configuration wizard. Asks a few questions one at a time, then writes the appropriate config file.

Spitball reads two config files and merges them per-key: `~/.spitball.json` (global) is the default for every project, and `<repoRoot>/.spitball.json` (per-repo) overrides any keys it sets. See `configuration.md` in the spitball skill for the full schema and resolution rules.

## When to run

- First time using spitball and the user wants explicit defaults instead of falling back to built-in ones.
- User wants to change a setting (save dir, auto-commit, nesting under repo name).
- User asks to "configure" or "set up" spitball.

## Process

Ask each question on its own, wait for the answer, then move on. Do not bundle questions. Repeat the user's answer back briefly so they can correct typos.

### 1. Scope

> Set spitball as a global default for every project, or just configure this one repo?
>
> Options: `global` (writes `~/.spitball.json`, used by every project unless overridden), `repo` (writes `<repoRoot>/.spitball.json`, only this repo). Default: `global` if no `~/.spitball.json` exists yet, otherwise `repo`.

Store the answer as `scope`. The two paths diverge here:

- `global` → continue with question 2 in "Global path" below.
- `repo` → continue with question 2 in "Per-repo path" below.

### Global path

#### 2g. Save directory (central)

> Where should spitballs be saved? This will be the central location for all your projects.
>
> Default: `docs/spitballs/`. Absolute paths are typical for central storage (e.g., `/mnt/notes/spitballs`).

Store as `saveDir`.

#### 3g. Auto-commit

> After spitball writes a new file, should it auto-commit to git?
>
> Default: `no` for central locations (the saveDir usually isn't a git repo).

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `autoCommit`.

#### 4g. Nest under repo name

> Spitballs from different repos will all share this saveDir. Nest each spitball under a subfolder named for its repo, so they don't collide?
>
> Default: `yes`. (Strongly recommended for shared saveDirs. If `no`, spitballs from all your repos pile into one directory.)

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `nestUnderRepoName`.

If the user picks `yes` and the current cwd is not in a git repo, warn them: spitball will refuse to run from non-git directories when this flag is on. Setup itself still proceeds (the global config can be written from anywhere).

### Per-repo path

#### 2r. Save directory (in-repo)

> Where in this repo should spitballs be saved?
>
> Default: `docs/spitballs/`. Repo-relative paths are typical here.

Store as `saveDir`.

#### 3r. Auto-commit

> After spitball writes a new file, should it auto-commit to git?
>
> Default: `yes`.

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `autoCommit`.

#### 4r. Nest under repo name

Skip this question. For per-repo configs the default `nestUnderRepoName: false` is correct — there's only one repo writing here.

If the user explicitly asks for nesting in a per-repo config (unusual but valid as an override on top of a global default), accept it and add the key.

## Write the config

Build the JSON from the answers and write to:

- `~/.spitball.json` if scope is `global`
- `<repoRoot>/.spitball.json` if scope is `repo`

Global example:

```json
{
  "saveDir": "/mnt/notes/spitballs",
  "autoCommit": false,
  "nestUnderRepoName": true
}
```

Per-repo example:

```json
{
  "saveDir": "docs/spitballs",
  "autoCommit": true
}
```

Show the file contents and the path you'll write to. Ask the user to confirm. Fix any typos before continuing.

## Commit

- Global config (`~/.spitball.json`): not committed anywhere. It's a user-level file.
- Per-repo config (`<repoRoot>/.spitball.json`): ask whether to commit. If yes, commit with a short message like `Add spitball config`. If no, leave it staged or untracked per the user's preference.

## Done

Tell the user where the config was written and that spitball will pick it up on next invocation. To reconfigure later, they can run `spitball-setup` again or edit the file directly.

Do NOT auto-invoke the `spitball` skill at the end. Setup ends here.
