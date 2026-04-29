---
name: spitball-setup
description: "Configure the spitball skill for the current project. Use when the user says 'configure spitball', 'set up spitball', 'spitball setup', 'spitball first run', 'where should spitballs go', or wants to change spitball defaults (save directory, auto-commit, visual companion behavior). Writes `.spitball.json` at the repo root. Run this when `.spitball.json` is missing and the user wants explicit configuration instead of defaults."
---

# Spitball Setup

A short configuration wizard. Asks a few questions one at a time, then writes `.spitball.json` at the repo root.

## When to run

- First time using spitball in a project and the user wants explicit defaults instead of falling back to built-in ones.
- User wants to change a setting (save dir, auto-commit, visual companion).
- User asks to "configure" or "set up" spitball.

## Process

Ask each question on its own, wait for the answer, then move on. Do not bundle questions. Repeat the user's answer back briefly so they can correct typos.

### 1. Save directory

> Where should spitballs be saved in this repo?
>
> Default: `docs/spitballs/`. Repo-relative or absolute paths both work.

Store the answer as `saveDir`. If the user says "default" or hits enter, use `docs/spitballs/`.

### 2. Auto-commit

> After spitball writes a new file, should it auto-commit to git?
>
> Default: yes.

Accept `yes`/`y`/`true` as `true`, `no`/`n`/`false` as `false`. Store as `autoCommit`.

### 3. Visual companion

> When a spitball topic might benefit from visuals (mockups, diagrams), should spitball offer the browser-based visual companion or stay text-only?
>
> Options: `offer` (ask each time), `off` (never offer). Default: `offer`.

Map `offer`/`ask` to `"ask"`, `off`/`never` to `"off"`. Store as `visualCompanionDefault`.

## Write the config

After all three answers, write `.spitball.json` at the repo root:

```json
{
  "saveDir": "<answer 1>",
  "autoCommit": <answer 2>,
  "visualCompanionDefault": "<answer 3>"
}
```

Show the file contents and ask the user to confirm. Fix any typos before continuing.

## Commit

Ask whether to commit `.spitball.json` to git. If yes, commit with a short message like `Add spitball config`. If no, leave it staged or untracked per the user's preference.

## Done

Tell the user that spitball is configured. They can now invoke the `spitball` skill and it will use these values. To reconfigure later, they can run `spitball-setup` again or edit `.spitball.json` directly.

Do NOT auto-invoke the `spitball` skill at the end. Setup ends here.
