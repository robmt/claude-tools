# lineup

A companion to `spitball`. The spitball owns the destination: where you are
going and what done looks like. The lineup owns the next three batters.

Three slots, hard cap:

- **At Bat** — concrete, currently being worked
- **On Deck** — fuzzy, next up
- **In the Hole** — very fuzzy, after that

Anything past In the Hole is in the dugout: not tracked, not speculated
about. The lineup never reaches the end of itself by design — completion
comes from the spitball's criteria, not from running out of batters.

## Install

```bash
/plugin install lineup@claude-tools
```

**Requires `spitball`** (one-way dependency). Install spitball first:

```bash
/plugin install spitball@claude-tools
```

The lineup skill will refuse to run if no spitball exists in the target
folder.

## How it works

Each spitball gets its own folder under `<saveDir>` (configured in
`.spitball.json`, defaults to `docs/spitballs/`). The lineup adds files
inside that same folder:

```
docs/spitballs/2026-04-29-foo/
  spitball.md             # written by spitball
  lineup.md               # rolling state index (At Bat / On Deck / In the Hole)
  004-wire-cli-flag.md    # current at-bat (only the concrete one is a file)
  completed/
    001-bootstrap-loader.md
    002-add-yaml-parser.md
    003-validate-schema.md
```

`lineup.md` is short — a pointer to the current at-bat file plus inline
bullets for On Deck and In the Hole. Only the **At Bat** slot ever gets a
file; fuzzy slots stay as bullets so we don't over-specify work we don't
yet understand.

## Two skills

### `lineup` (the reviewer)

Reads the spitball and current state, then:

1. Checks the spitball's completion criteria. If met → marks the lineup
   `Status: Complete` and stops.
2. Otherwise: promotes On Deck → At Bat (creates the next `NNN-<slug>.md`
   file with full structure including a required Test plan), promotes In
   the Hole → On Deck, drafts a new In the Hole bullet.
3. Stops. Does not auto-invoke `at-bat`.

The reviewer enforces red/green test plans when sharpening. If a test
genuinely can't be written, the at-bat must explicitly justify why and
provide manual verification steps.

### `at-bat` (the implementer)

Reads the current At Bat file and does the work:

1. **Red.** Writes the failing test described in the Test plan.
2. **Green.** Implements until the test passes.
3. Verifies scope boundary — only this at-bat, nothing more.
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

- One live → use it
- Many → ask the user which
- None → tell user to run spitball first

## Configuration

`lineup` reads `.spitball.json` for shared values (`saveDir`,
`autoCommit`). It does not introduce its own config file. If a
lineup-specific knob is needed later, it'll be added then.

## Layout invariant

Every `lineup.md` is a sibling of a `spitball.md` in the same folder. The
pair travels together. `lineup` will not create a lineup file in a folder
that doesn't already contain `spitball.md`.
