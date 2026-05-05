# Configuration

Spitball reads configuration from two files, merged per-key. To create either
file interactively, run the `spitball-setup` skill.

## Files

| Path                      | Purpose                                                                |
|---------------------------|------------------------------------------------------------------------|
| `~/.spitball.json`        | User-global defaults applied to every project.                         |
| `<repoRoot>/.spitball.json` | Per-project override. Any key here wins over the global value.       |

Either file may be absent. If both are absent, hardcoded defaults apply.

## Schema

| Key                  | Type    | Default            | What it does                                                                                  |
|----------------------|---------|--------------------|-----------------------------------------------------------------------------------------------|
| `saveDir`            | string  | `docs/spitballs/`  | Directory the spitball file is written to. Repo-relative or absolute.                         |
| `commitSpitball`     | bool    | `true`             | Commit the spitball doc to git after writing. Set `false` if `saveDir` is not a git repo.     |
| `commitAtBat`        | bool    | `true`             | Commit each at-bat (test+impl+file-move) as a single commit. `true` keeps each at-bat individually revertable. |
| `nestUnderRepoName`  | bool    | `false`            | When true, save path becomes `<saveDir>/<repo-name>/YYYY-MM-DD-<topic>/spitball.md`. See below. |
| `autoContinue`       | string  | `"prompt"`         | `"never"`, `"prompt"`, or `"always"`. Governs the lineup -> at-bat handoff (at-bat -> lineup is mandatory and not configurable). See "Continuation" below. |

Legacy: a key called `autoCommit` is honored as a fallback for `commitSpitball`
when `commitSpitball` is not explicitly set in the same layer. This lets users
who answered "no commit" at setup time keep that meaning for the spitball doc
without accidentally suppressing per-at-bat commits.

Unknown keys are ignored, so the file is forward-compatible if more knobs are
added later.

## Resolution

1. Start with hardcoded defaults.
2. If `~/.spitball.json` exists and is parseable, overlay each key it sets.
3. If `<repoRoot>/.spitball.json` exists and is parseable, overlay each key it sets.
4. The result of that merge is the effective config.

Unparseable JSON in either file is treated as missing for that file, and the
skill mentions the parse error to the user.

## `nestUnderRepoName` and repo name derivation

When `nestUnderRepoName: true`, every save path is prefixed with the current
repo's name. This lets a single shared `saveDir` (e.g.,
`/mnt/notes/spitballs`) hold spitballs from many repos without collision.

**Repo name resolution:**

1. Run `git remote get-url origin`. Strip protocol, host, and trailing
   `.git`; replace `/` with `-`. Example: `git@github.com:robmt/claude-tools.git`
   becomes `robmt-claude-tools`.
2. If there is no `origin` remote: fall back to the basename of
   `git rev-parse --show-toplevel`.
3. If the current directory is not inside a git repo at all AND
   `nestUnderRepoName: true`: refuse to run. Tell the user to either run
   spitball from inside a git repo, or set `nestUnderRepoName: false` for this
   project. Do not silently invent a name.

**Lineup discovery interaction:** the `lineup` plugin honors the same setting.
When `nestUnderRepoName: true`, lineup scans only `<saveDir>/<repo-name>/`,
not the full `<saveDir>` - so running `lineup` in repo X only sees X's
spitballs even if the saveDir is shared with other repos.

## Examples

### Per-repo (default)

`<repoRoot>/.spitball.json`:

```json
{
  "saveDir": "docs/spitballs",
  "commitSpitball": true
}
```

Spitballs land at `docs/spitballs/YYYY-MM-DD-<topic>/spitball.md` inside this
repo.

### Central, nested under repo name

`~/.spitball.json`:

```json
{
  "saveDir": "/mnt/notes/spitballs",
  "commitSpitball": false,
  "nestUnderRepoName": true
}
```

No per-repo file needed. Spitballs from `robmt/claude-tools` land at
`/mnt/notes/spitballs/robmt-claude-tools/YYYY-MM-DD-<topic>/spitball.md`.
Spitballs from `robmt/other-repo` land in their own subfolder. Lineup
discovery in either repo only sees that repo's spitballs.

### Global default + one project that opts out

`~/.spitball.json`:

```json
{
  "saveDir": "/mnt/notes/spitballs",
  "commitSpitball": false,
  "nestUnderRepoName": true
}
```

`<repoRoot>/.spitball.json` (in a project that wants its own location):

```json
{
  "saveDir": "docs/spitballs",
  "commitSpitball": true,
  "nestUnderRepoName": false
}
```

Per-key merge means this project gets all three keys overridden; spitballs
go in-repo and get auto-committed.

## First-run setup

If neither file exists, the spitball skill proceeds with defaults and mentions
that the `spitball-setup` skill is available. The setup wizard asks about
scope (global vs per-repo) first and writes to the right file.

## Folder layout inside `saveDir`

Each spitball gets its own folder named `YYYY-MM-DD-<topic>/`, containing
the file `spitball.md`. The `<topic>` slug is derived from the spitball's
subject. The folder gives every spitball a place for related notes,
mockups, or companion-plugin artifacts (for example, the `lineup` plugin
writes `lineup.md` and at-bat files inside this same folder). Layout
inside each spitball folder is not configurable in this version.

When the lineup plugin marks a spitball `Status: Complete`, it moves
the entire folder into `<effectiveSaveDir>/completed/<folder>/` so the
top-level `effectiveSaveDir` only shows in-flight work. The archive
bucket is flat (no nesting by year or topic) and is reserved - do not
name a spitball `completed`. Postmortem operates on archived folders.

## Continuation

Spitball itself never auto-invokes a downstream skill: after the spitball is
written and approved, it stops and hands control back to the user. (When
`lineupActive` is true for the current `effectiveSaveDir`, spitball's hand-back
includes a passive pointer to `/lineup`, but does not invoke it.)

The lineup <-> at-bat loop has its own continuation rules:

- **at-bat -> lineup is mandatory.** When at-bat finishes a unit of work, it
  hands off to lineup, which verifies the at-bat's Definition of done before
  promoting. This handoff is not user-configurable - bypassing the verifier
  lets a broken at-bat ship as "done."
- **lineup -> at-bat is governed by `autoContinue`.**
  - `"never"` - lineup writes a `**Next step:** run /at-bat` anchor and
    stops. The user types the next slash command.
  - `"prompt"` (default) - lineup ends with a question
    `Continue? (yes / session / always / no)`. `session` treats the rest of
    the conversation as `"always"`. `always` writes
    `autoContinue: "always"` to `<repoRoot>/.spitball.json` for persistence.
  - `"always"` - lineup invokes at-bat directly after promoting, no prompt.
