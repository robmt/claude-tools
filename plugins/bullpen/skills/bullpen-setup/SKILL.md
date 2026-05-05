---
name: bullpen-setup
description: "Configure the bullpen/lineup/at-bat skills. Use when the user says 'configure bullpen', 'set up bullpen', 'bullpen setup', 'bullpen first run', 'where should bullpens go', or wants to change defaults (save directory, commit behavior, auto-continue between skills, central vs per-repo storage). Writes `~/.bullpen.json` (global default) or `<repoRoot>/.bullpen.json` (per-repo override) depending on scope chosen by the user."
---

# Bullpen Setup

A short configuration wizard. Asks a few questions one at a time, then writes the appropriate config file.

## Output rule: ASCII only

The config file this skill writes is JSON, which is already ASCII-friendly. User-facing prose written by this skill (questions, confirmations, the "Done" message) MUST also use ASCII only: no emoji, no em-dashes, no curly quotes, no arrows. Use `-` for dashes, `->` for arrows, `"` and `'` for quotes. This keeps the wizard portable across editors, terminals, and operating systems.

Bullpen reads two config files and merges them per-key: `~/.bullpen.json` (global) is the default for every project, and `<repoRoot>/.bullpen.json` (per-repo) overrides any keys it sets. See `configuration.md` in the bullpen skill for the full schema and resolution rules.

## When to run

- First time using bullpen and the user wants explicit defaults instead of falling back to built-in ones.
- User wants to change a setting (save dir, auto-commit, nesting under repo name).
- User asks to "configure" or "set up" bullpen.

## Process

Ask each question on its own, wait for the answer, then move on. Do not bundle questions. Repeat the user's answer back briefly so they can correct typos.

### 1. Scope

> Set bullpen as a global default for every project, or just configure this one repo?
>
> Options: `global` (writes `~/.bullpen.json`, used by every project unless overridden), `repo` (writes `<repoRoot>/.bullpen.json`, only this repo). Default: `global` if no `~/.bullpen.json` exists yet, otherwise `repo`.

Store the answer as `scope`. The two paths diverge here:

- `global` -> continue with question 2 in "Global path" below.
- `repo` -> continue with question 2 in "Per-repo path" below.

### Global path

#### 2g. Save directory (central)

> Where should bullpens be saved? This will be the central location for all your projects.
>
> Default: `docs/bullpen/`. Absolute paths are typical for central storage (e.g., `/mnt/notes/bullpen`).

Store as `saveDir`.

#### 3g. Commit the bullpen doc?

> After bullpen writes a new file (the design doc itself), should it auto-commit to git?
>
> Default: `no` for central locations (the saveDir usually isn't a git repo).

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `commitBullpen`.

This setting governs ONLY the bullpen doc. The at-bat work (test + impl + file move) is committed separately and is controlled by `commitAtBat` - see question 5.

#### 4g. Nest under repo name

> Bullpens from different repos will all share this saveDir. Nest each bullpen under a subfolder named for its repo, so they don't collide?
>
> Default: `yes`. (Strongly recommended for shared saveDirs. If `no`, bullpens from all your repos pile into one directory.)

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `nestUnderRepoName`.

If the user picks `yes` and the current cwd is not in a git repo, warn them: bullpen will refuse to run from non-git directories when this flag is on. Setup itself still proceeds (the global config can be written from anywhere).

#### 5g. Commit each at-bat?

> When at-bat finishes a unit of work, should it commit the test+impl+file-move as a single commit?
>
> Default: `yes`. Each at-bat as one commit means each at-bat is revertable independently - strongly recommended unless you have a specific reason to defer commits.

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `commitAtBat`.

#### 6g. Auto-continue between skills?

> When at-bat hands off to lineup, and lineup wants to step into the next at-bat, how should the handoff work?
>
> Options:
> - `never` - show a "Next step: run /at-bat" anchor and wait. The user always types the next slash command.
> - `prompt` (default) - at each handoff, ask `Continue? (yes / session / always / no)`. Lightest friction with full control.
> - `always` - chain skills automatically without asking. Smoothest UX, but you give up the inspection beat between slots.

Store as `autoContinue` with the literal string value `"never"`, `"prompt"`, or `"always"`. (Note: at-bat -> lineup is mandatory regardless of this setting; lineup verifies at-bat's completion criteria. This setting governs only the lineup -> at-bat transition.)

### Per-repo path

#### 2r. Save directory (in-repo)

> Where in this repo should bullpens be saved?
>
> Default: `docs/bullpen/`. Repo-relative paths are typical here.

Store as `saveDir`.

#### 3r. Commit the bullpen doc?

> After bullpen writes a new file (the design doc itself), should it auto-commit to git?
>
> Default: `yes`.

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `commitBullpen`.

#### 4r. Commit each at-bat?

> When at-bat finishes a unit of work, should it commit the test+impl+file-move as a single commit?
>
> Default: `yes`. Each at-bat as one commit means each at-bat is revertable independently.

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `commitAtBat`.

#### 5r. Auto-continue between skills?

> When lineup wants to step into the next at-bat, how should the handoff work?
>
> Options: `never`, `prompt` (default), `always`. See the global path's question 6g for full descriptions.

Store as `autoContinue` (string).

#### 6r. Nest under repo name

Skip this question. For per-repo configs the default `nestUnderRepoName: false` is correct - there's only one repo writing here.

If the user explicitly asks for nesting in a per-repo config (unusual but valid as an override on top of a global default), accept it and add the key.

## Write the config

Build the JSON from the answers and write to:

- `~/.bullpen.json` if scope is `global`
- `<repoRoot>/.bullpen.json` if scope is `repo`

Global example:

```json
{
  "saveDir": "/mnt/notes/bullpen",
  "commitBullpen": false,
  "commitAtBat": true,
  "nestUnderRepoName": true,
  "autoContinue": "prompt"
}
```

Per-repo example:

```json
{
  "saveDir": "docs/bullpen",
  "commitBullpen": true,
  "commitAtBat": true,
  "autoContinue": "always"
}
```

Show the file contents and the path you'll write to. Ask the user to confirm. Fix any typos before continuing.

## Commit

- Global config (`~/.bullpen.json`): not committed anywhere. It's a user-level file.
- Per-repo config (`<repoRoot>/.bullpen.json`): ask whether to commit. If yes, commit with a short message like `Add bullpen config`. If no, leave it staged or untracked per the user's preference.

## Done

Tell the user where the config was written and that bullpen will pick it up on next invocation. To reconfigure later, they can run `bullpen-setup` again or edit the file directly.

Do NOT auto-invoke the `bullpen` skill at the end. Setup ends here.
