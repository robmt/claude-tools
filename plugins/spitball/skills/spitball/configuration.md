# Configuration

Spitball reads one configuration file: `.spitball.json` at the repo root. If
the file is absent, defaults apply.

## Schema

| Key       | Type    | Default            | What it does                                                    |
|-----------|---------|--------------------|-----------------------------------------------------------------|
| `saveDir` | string  | `docs/spitballs/`  | Directory the spitball file is written to. Path is repo-relative or absolute. |

Unknown keys are ignored, so the file is forward-compatible if more knobs are
added later.

## Example `.spitball.json`

```json
{
  "saveDir": "docs/spitballs"
}
```

```json
{
  "saveDir": "claude-memories/spitballs"
}
```

```json
{
  "saveDir": "/absolute/path/to/spitballs"
}
```

## Resolution

1. Look for `.spitball.json` at the repo root.
2. If present and parseable, read `saveDir`. If `saveDir` is missing or empty,
   fall back to the default.
3. If the file is absent or unparseable, fall back to the default.

## Filename

Inside `saveDir`, the spitball is written as
`YYYY-MM-DD-<topic>-spitball.md`. The `<topic>` slug is derived from the
spitball's subject. The filename pattern is not configurable in this version.

## Continuation

There is no automatic continuation skill in this version. After the spitball
is written and approved, the skill stops and hands control back to the user.
The user invokes any planning or implementation skill manually.
