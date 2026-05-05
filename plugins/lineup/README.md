# lineup

A companion to `bullpen`. The bullpen owns the destination: where you are
going and what done looks like. The lineup owns the next three batters.

Three slots, hard cap:

- **At Bat** - concrete, currently being worked
- **On Deck** - fuzzy, next up
- **In the Hole** - very fuzzy, after that

Anything past In the Hole is in the dugout: not tracked, not speculated
about. The lineup never reaches the end of itself by design - completion
comes from the bullpen's criteria, not from running out of batters.

## Install

```bash
/plugin install lineup@claude-tools
```

**Requires `bullpen`** (one-way dependency). Install bullpen first:

```bash
/plugin install bullpen@claude-tools
```

Also requires `python3` and `git` on PATH (used by the config-resolution helper script, identical to bullpen's).

The lineup skill will refuse to run if no bullpen exists in the target
folder.

## How it works

Each bullpen gets its own folder under `<saveDir>` (or
`<saveDir>/<repo-name>` when `nestUnderRepoName: true`; configured via
`~/.bullpen.json` and/or `<repoRoot>/.bullpen.json`, defaults to
`docs/bullpen/`). The lineup adds files inside that same folder:

```
docs/bullpen/2026-04-29-foo/         # in flight
  bullpen.md             # written by bullpen
  lineup.md               # rolling state index (At Bat / On Deck / In the Hole)
  004-wire-cli-flag.md    # current at-bat (only the concrete one is a file)
  completed/              # at-bat history (inside a bullpen folder)
    001-bootstrap-loader.md
    002-add-yaml-parser.md
    003-validate-schema.md
docs/bullpen/completed/              # archive bucket (sibling of live folders)
  2026-03-14-bar/         # entire bullpen folder, moved here on completion
    bullpen.md
    lineup.md             # starts with `Status: Complete`
    completed/            # at-bat history travels with the folder
      001-...md
    postmortem.md         # written later by /postmortem (optional)
```

The `completed/` inside a bullpen folder is at-bat history. The
top-level `<saveDir>/completed/` is the archive bucket of finished
bullpens. They share a name only because both mean "done at this
level" - they are at different depths and never overlap.

`lineup.md` is short - a pointer to the current at-bat file plus inline
bullets for On Deck and In the Hole. Only the **At Bat** slot ever gets a
file; fuzzy slots stay as bullets so we don't over-specify work we don't
yet understand.

## Two skills

### `lineup` (the reviewer)

Reads the bullpen and current state, then:

1. Checks the bullpen's completion criteria. If met -> marks the lineup
   `Status: Complete`, moves the folder into `<saveDir>/completed/`,
   and stops. The archive keeps live bullpens uncluttered for
   directory previews (Obsidian, IDE trees) and `git status`.
2. Otherwise: promotes On Deck -> At Bat (creates the next `NNN-<slug>.md`
   file with full structure including a required Test plan), promotes In
   the Hole -> On Deck, drafts a new In the Hole bullet.
3. Stops. Does not auto-invoke `at-bat`.

The reviewer enforces red/green test plans when sharpening. If a test
genuinely can't be written, the at-bat must explicitly justify why and
provide manual verification steps.

### `at-bat` (the implementer)

Reads the current At Bat file and does the work:

1. **Red.** Writes the failing test described in the Test plan.
2. **Green.** Implements until the test passes.
3. Verifies scope boundary - only this at-bat, nothing more.
4. Marks complete and moves the file to `completed/`.
5. Stops. Does not auto-invoke `lineup` to refresh.

The user drives the loop; neither skill chains into the other.

## Counter and naming

At-bat files are named `NNN-<slug>.md`. The counter is monotonic per
lineup folder, assigned by `lineup` at promotion time, and never reused.
If at-bat 003 is abandoned, the next one is 004. `completed/` reads as a
clean ordered history of work done.

## Active lineup discovery

Filesystem-only. No pointer files, no `.lineup.json`. The skills scan
`<saveDir>` for folders containing a `lineup.md` without a `Status:
Complete` marker:

- One live -> use it
- Many -> ask the user which
- None -> tell user to run bullpen first

## Configuration

`lineup` reads bullpen's merged config (`~/.bullpen.json` overlaid by
`<repoRoot>/.bullpen.json`) for shared values: `saveDir`, `commitAtBat`,
`autoContinue`, and `nestUnderRepoName`. It does not introduce its own
config file. The legacy `autoCommit` key is honored as a fallback for
`commitBullpen` only - the per-at-bat commit behavior is now
controlled separately by `commitAtBat` so each at-bat lands as a single
revertable commit. If `nestUnderRepoName: true`, lineup discovery scans only
`<saveDir>/<repo-name>/`, so working in repo X only surfaces X's
bullpens even when the saveDir is shared across repos. See the bullpen
plugin's `configuration.md` for the full schema. If a lineup-specific
knob is needed later, it'll be added then.

## Layout invariant

Every `lineup.md` is a sibling of a `bullpen.md` in the same folder. The
pair travels together. `lineup` will not create a lineup file in a folder
that doesn't already contain `bullpen.md`.
