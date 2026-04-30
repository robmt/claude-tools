# Lineup

A companion plugin to `spitball`. Manages a rolling, narrow view of the work
in front of you on the way to a spitball's destination. The spitball owns
the W (where you are going and what done looks like). The lineup owns the
next three batters.

## Why

Spitball stops at the design. It deliberately does not produce a forward
plan, because long forward plans don't survive contact with reality. But
when you sit down to actually work toward a spitball, you need *something*
in front of you that's concrete enough to act on. You don't need the whole
roadmap; you need the next at-bat.

`lineup` fills that gap, and only that gap. It never tries to plan the full
path to the destination — that is precisely what we said we wouldn't do.
It tells you what's at-bat, what's on-deck, and what's in-the-hole. Past
that is the dugout, and we don't track the dugout.

## States

Exactly three slots, hard cap. Three batters visible at any time:

- **At Bat** — concrete, currently being worked. One unit, fully specified,
  including its test plan.
- **On Deck** — fuzzy, next up. A sentence or two. No file yet.
- **In the Hole** — very fuzzy, after that. A sentence. No file yet.

Anything past In the Hole is in the dugout: not tracked, not speculated
about. The user can ask explicitly to see further out, but the default is
three.

The In the Hole slot is *not* the closing batter. It is just the third
batter we currently see. The lineup never reaches the end of itself by
design — completion comes from the spitball's criteria, not from running
out of batters.

## Layout

One folder per spitball. Spitball and lineup live side by side.

```
docs/spitballs/<date>-<topic>/
  spitball.md
  lineup.md
  NNN-<slug>.md            # current at-bat
  completed/
    NNN-<slug>.md          # finished at-bats, in order
```

The folder is created by spitball (see "Spitball plugin tweak" below).
Lineup adds `lineup.md`, the at-bat file, and `completed/` when first
invoked.

### lineup.md

Short organizational index. Example:

```markdown
# Lineup: Foo

Spitball: spitball.md

## At Bat
→ 004-wire-cli-flag.md

## On Deck
- Add validation for the new flag (depends on at-bat 004)

## In the Hole
- Migration of legacy flag callers

## Completed
- 003-validate-schema.md
- 002-add-yaml-parser.md
- 001-bootstrap-loader.md
```

When the spitball's completion criteria are met, the reviewer adds a
`Status: Complete` marker at the top. That is how a lineup becomes inactive
— filesystem-visible state, no separate metadata.

### At-bat file

`NNN-<slug>.md`, where NNN is a zero-padded counter, monotonic per lineup
folder, never reused. If at-bat 003 is abandoned, the next is 004.

Required structure:

```markdown
# At-Bat NNN: <title>

## What
<concrete description of the unit of work>

## Definition of done
<observable outcome>

## Test plan
- Red: <a failing test that captures "done">
- Green: <expected behavior when it passes>

## Scope boundary
- In: <thing>
- Out: <related thing we are NOT touching here>

## Dependencies
- <prior at-bat or external thing>
```

If the work genuinely cannot be tested (pure docs, no-behavior config,
exploratory spike), the Test plan section is replaced with explicit
honesty:

```markdown
## Test plan
- No automated test: <reason>
- Manual verification: <concrete steps>
```

The reviewer pushes back on this when sharpening: if the at-bat *could*
reasonably be tested, the no-test escape hatch is not allowed.

## Skills

Two separate skills. The user drives the loop; neither auto-invokes the
other.

### lineup (the reviewer)

What it does:

1. Discovers active lineups by scanning `<saveDir>` for folders containing
   a `lineup.md` without a `Status: Complete` marker. If none → tells the
   user to run spitball first. If one → uses it. If many → asks which.
2. Reads the spitball and current lineup state.
3. Checks the spitball's completion criteria against current state. If
   met → writes `Status: Complete` and stops. The user goes back to the
   spitball or starts a new one.
4. Otherwise: promotes On Deck → At Bat by creating the next NNN-slug.md
   file with the full required structure. Promotes In the Hole → On Deck
   (inline bullet). Drafts a new In the Hole bullet.
5. Enforces test plan presence in any at-bat it sharpens.
6. Stops. Hands back to user.

The lineup skill never executes work. It only updates the lineup state.

### at-bat (the implementer)

What it does:

1. Discovers active lineup the same way. Reads the current At Bat file.
2. **Red.** Writes the failing test described in the Test plan.
3. **Green.** Implements until the test passes.
4. Verifies scope boundary — only this at-bat, nothing more.
5. Marks the at-bat complete and moves the file to `completed/`.
6. Stops. Does *not* auto-invoke `lineup` to refresh — the user calls the
   next play.

If the at-bat carries the no-automated-test escape, the implementer runs
the manual verification steps (or asks the user to) and stops there
instead.

## Counter, naming, and discovery

- **Counter** is monotonic per lineup folder, assigned by the `lineup`
  skill at the moment of promotion. Counter never resets, never reuses.
- **Filename** is `NNN-<kebab-slug>.md`. The slug is 3–5 words derived
  from the at-bat's topic.
- **Active lineup discovery** is filesystem-only. No pointer files, no
  json state. The skills walk the spitballs directory and apply the
  one/many/none rule above.

## Configuration

`lineup` reads `.spitball.json` for shared values:

- `saveDir` — same place spitballs go.
- `autoCommit` — same auto-commit behavior for at-bat completions and
  lineup updates.

There is no `.lineup.json`. If a lineup-specific knob is needed later, we
add it then.

## Dependency

`lineup` depends on `spitball`. Strictly one-way:

- The lineup README states spitball is a prerequisite.
- Lineup runtime checks for `spitball.md` in the target folder. No
  spitball → skill stops with a "run spitball first" message.
- Spitball is not modified to know about lineup. Spitball remains usable
  standalone with no awareness that lineup exists.

The lineup plugin's `plugin.json` declares the dependency if Claude Code's
plugin manifest supports it; otherwise the README carries the constraint.

## Spitball plugin tweak

Spitball currently writes to `<saveDir>/<date>-<topic>-spitball.md` (flat
file). It will instead write to `<saveDir>/<date>-<topic>/spitball.md`
(folder containing the spitball).

This change is justified independently — it gives every spitball a place
to drop related notes, mockups, attachments, etc. — and is neutral to
whether lineup is installed. A spitball-only user gets a folder containing
one file. Slightly heavier, but small and forward-compatible.

The change is local to spitball's "Write spitball doc" step. No other
spitball behavior changes.

Pre-existing flat-form spitballs are not auto-migrated. They continue to
work for spitball; lineup simply won't be available for them unless the
user manually moves them into a folder.

## Out of scope (for v1)

- Visual companion integration. (Could come later.)
- An at-bat that pulls from multiple spitballs. One at-bat = one spitball.
- Showing more than three slots by default.
- Automated migration of pre-existing flat spitballs.
- A `lineup-switch` skill or any pointer-based active-lineup mechanism.

## Completion criteria for this design

This spitball is "delivered" when:

1. `lineup` plugin exists in `plugins/lineup/` with `plugin.json`, README,
   and the two skills (`lineup`, `at-bat`).
2. Each skill follows the discipline described above (filesystem-only
   discovery, three-slot cap, red/green test enforcement, no auto-invoke).
3. The spitball plugin has been updated to write into a folder layout.
4. A smoke test: run spitball, then lineup, then at-bat, on a small
   contrived design, and confirm the artifacts match this spec.
