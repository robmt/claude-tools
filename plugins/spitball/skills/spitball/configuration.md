# Configuration

Spitball reads one configuration file: `.spitball.json` at the repo root. If
the file is absent, defaults apply. To create the file interactively, run the
`spitball-setup` skill.

## Schema

| Key                      | Type    | Default            | What it does                                                    |
|--------------------------|---------|--------------------|-----------------------------------------------------------------|
| `saveDir`                | string  | `docs/spitballs/`  | Directory the spitball file is written to. Repo-relative or absolute. |
| `autoCommit`             | bool    | `true`             | Commit the spitball file to git after writing.                  |
| `visualCompanionDefault` | string  | `"ask"`            | `"ask"` to offer the visual companion when relevant, `"off"` to skip the offer entirely. |

Unknown keys are ignored, so the file is forward-compatible if more knobs are
added later.

## Example `.spitball.json`

Defaults made explicit:

```json
{
  "saveDir": "docs/spitballs",
  "autoCommit": true,
  "visualCompanionDefault": "ask"
}
```

Custom save location, no auto-commit, text-only:

```json
{
  "saveDir": "claude-memories/spitballs",
  "autoCommit": false,
  "visualCompanionDefault": "off"
}
```

## Resolution

1. Look for `.spitball.json` at the repo root.
2. If present and parseable, read each key. Missing keys fall back to defaults.
3. If the file is absent or unparseable, fall back to defaults for all keys.

## First-run setup

If `.spitball.json` is missing, the spitball skill proceeds with defaults and
mentions that the `spitball-setup` skill is available. The user may run
`spitball-setup` at any time to write or update the file.

## Layout

Inside `saveDir`, each spitball gets its own folder named
`YYYY-MM-DD-<topic>/`, containing the file `spitball.md`. The `<topic>`
slug is derived from the spitball's subject. The folder gives every
spitball a place for related notes, mockups, or companion-plugin artifacts
(for example, the `lineup` plugin writes `lineup.md` and at-bat files
inside this same folder). Layout is not configurable in this version.

## Continuation

There is no automatic continuation skill. After the spitball is written and
approved, the skill stops and hands control back to the user.
