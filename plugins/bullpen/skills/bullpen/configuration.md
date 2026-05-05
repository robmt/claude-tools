# Configuration

Bullpen reads configuration from two files, merged per-key. To create either
file interactively, run the `bullpen-setup` skill.

## Files

| Path                      | Purpose                                                                |
|---------------------------|------------------------------------------------------------------------|
| `~/.bullpen.json`        | User-global defaults applied to every project.                         |
| `<repoRoot>/.bullpen.json` | Per-project override. Any key here wins over the global value.       |

Either file may be absent. If both are absent, hardcoded defaults apply.

## Schema

| Key                  | Type    | Default            | What it does                                                                                  |
|----------------------|---------|--------------------|-----------------------------------------------------------------------------------------------|
| `saveDir`            | string  | `docs/bullpen/`  | Directory the bullpen file is written to. Repo-relative or absolute.                         |
| `commitBullpen`     | bool    | `true`             | Commit the bullpen doc to git after writing. Set `false` if `saveDir` is not a git repo.     |
| `commitAtBat`        | bool    | `true`             | Commit each at-bat (test+impl+file-move) as a single commit. `true` keeps each at-bat individually revertable. |
| `nestUnderRepoName`  | bool    | `false`            | When true, save path becomes `<saveDir>/<repo-name>/YYYY-MM-DD-<topic>/bullpen.md`. See below. |
| `autoContinue`       | string  | `"prompt"`         | `"never"`, `"prompt"`, or `"always"`. Governs the lineup -> at-bat handoff (at-bat -> lineup is mandatory and not configurable). See "Continuation" below. |

Legacy: two older key names are honored as fallbacks for `commitBullpen`,
in precedence order `commitBullpen` > `commitSpitball` > `autoCommit`.
The most-specific key in a layer wins. This lets users who configured
"no commit" under the previous skill name (`commitSpitball`) or the
original (`autoCommit`) keep that meaning for the bullpen doc without
accidentally suppressing per-at-bat commits.

Filename legacy: when `.bullpen.json` is absent at a given location,
the resolver falls back to `.spitball.json` at the same path (the name
this plugin used previously). Rename the file at your convenience.

Unknown keys are ignored, so the file is forward-compatible if more knobs are
added later.

## Resolution

1. Start with hardcoded defaults.
2. If `~/.bullpen.json` exists and is parseable, overlay each key it sets;
   otherwise fall back to `~/.spitball.json` (legacy).
3. If `<repoRoot>/.bullpen.json` exists and is parseable, overlay each key
   it sets; otherwise fall back to `<repoRoot>/.spitball.json` (legacy).
4. The result of that merge is the effective config.

Unparseable JSON in either file is treated as missing for that file, and the
skill mentions the parse error to the user.

## `nestUnderRepoName` and repo name derivation

When `nestUnderRepoName: true`, every save path is prefixed with the current
repo's name. This lets a single shared `saveDir` (e.g.,
`/mnt/notes/bullpen`) hold bullpens from many repos without collision.

**Repo name resolution:**

1. Run `git remote get-url origin`. Strip protocol, host, and trailing
   `.git`; replace `/` with `-`. Example: `git@github.com:robmt/claude-tools.git`
   becomes `robmt-claude-tools`.
2. If there is no `origin` remote: fall back to the basename of
   `git rev-parse --show-toplevel`.
3. If the current directory is not inside a git repo at all AND
   `nestUnderRepoName: true`: refuse to run. Tell the user to either run
   bullpen from inside a git repo, or set `nestUnderRepoName: false` for this
   project. Do not silently invent a name.

**Lineup discovery interaction:** the `lineup` plugin honors the same setting.
When `nestUnderRepoName: true`, lineup scans only `<saveDir>/<repo-name>/`,
not the full `<saveDir>` - so running `lineup` in repo X only sees X's
bullpens even if the saveDir is shared with other repos.

## Examples

### Per-repo (default)

`<repoRoot>/.bullpen.json`:

```json
{
  "saveDir": "docs/bullpen",
  "commitBullpen": true
}
```

Bullpens land at `docs/bullpen/YYYY-MM-DD-<topic>/bullpen.md` inside this
repo.

### Central, nested under repo name

`~/.bullpen.json`:

```json
{
  "saveDir": "/mnt/notes/bullpen",
  "commitBullpen": false,
  "nestUnderRepoName": true
}
```

No per-repo file needed. Bullpens from `robmt/claude-tools` land at
`/mnt/notes/bullpen/robmt-claude-tools/YYYY-MM-DD-<topic>/bullpen.md`.
Bullpens from `robmt/other-repo` land in their own subfolder. Lineup
discovery in either repo only sees that repo's bullpens.

### Global default + one project that opts out

`~/.bullpen.json`:

```json
{
  "saveDir": "/mnt/notes/bullpen",
  "commitBullpen": false,
  "nestUnderRepoName": true
}
```

`<repoRoot>/.bullpen.json` (in a project that wants its own location):

```json
{
  "saveDir": "docs/bullpen",
  "commitBullpen": true,
  "nestUnderRepoName": false
}
```

Per-key merge means this project gets all three keys overridden; bullpens
go in-repo and get auto-committed.

## First-run setup

If neither file exists, the bullpen skill proceeds with defaults and mentions
that the `bullpen-setup` skill is available. The setup wizard asks about
scope (global vs per-repo) first and writes to the right file.

## Folder layout inside `saveDir`

Each bullpen gets its own folder named `YYYY-MM-DD-<topic>/`, containing
the file `bullpen.md`. The `<topic>` slug is derived from the bullpen's
subject. The folder gives every bullpen a place for related notes,
mockups, or companion-plugin artifacts (for example, the `lineup` plugin
writes `lineup.md` and at-bat files inside this same folder). Layout
inside each bullpen folder is not configurable in this version.

When the lineup plugin marks a bullpen `Status: Complete`, it moves
the entire folder into `<effectiveSaveDir>/completed/<folder>/` so the
top-level `effectiveSaveDir` only shows in-flight work. The archive
bucket is flat (no nesting by year or topic) and is reserved - do not
name a bullpen `completed`. Postmortem operates on archived folders.

## Continuation

Bullpen itself never auto-invokes a downstream skill: after the bullpen is
written and approved, it stops and hands control back to the user. (When
`lineupActive` is true for the current `effectiveSaveDir`, bullpen's hand-back
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
    `autoContinue: "always"` to `<repoRoot>/.bullpen.json` for persistence.
  - `"always"` - lineup invokes at-bat directly after promoting, no prompt.
