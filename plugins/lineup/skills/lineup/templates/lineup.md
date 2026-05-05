# lineup.md file template

Used by the lineup skill when creating or updating `lineup.md` for a
bullpen folder.

## Active lineup

```markdown
# Lineup: <topic>

Bullpen: bullpen.md

## At Bat
-> NNN-<slug>.md

## On Deck
- <fuzzy bullet, one sentence>

## In the Hole
- <very fuzzy bullet, one sentence>

## Completed
- NNN-<slug>.md
- NNN-<slug>.md
```

If the user opted in to a worktree at first-run bootstrap, prepend a
single header line:

```markdown
Worktree: /abs/path/to/worktrees/<slug>

# Lineup: <topic>
...
```

The header is one line, no fenced block, no blank line before it.
At-bat reads this line in its discovery step and `cd`s into the path
before running anything. See SKILL.md "Worktree decision" for when to
write it.

## Completed lineup

When the bullpen's completion criteria are met, prepend
`Status: Complete` as the first line of the file. Any prior
`Worktree:` header is stripped at the same time - the worktree is
removed during the completion archive step (see SKILL.md "Completion
archive").

```markdown
Status: Complete

# Lineup: <topic>

Bullpen: bullpen.md

## At Bat
(none - bullpen delivered)

## On Deck
(none)

## In the Hole
(none)

## Completed
- 001-<slug>.md
- 002-<slug>.md
- ...
```

That marker is how a lineup becomes inactive. There is no separate
metadata file or json sidecar - the filesystem is the truth.

When lineup writes `Status: Complete`, it also moves the entire
bullpen folder from `<effectiveSaveDir>/<folder>/` to
`<effectiveSaveDir>/completed/<folder>/`. Past that point the folder
lives in the archive bucket; postmortem and future reads find it
there. See SKILL.md "Completion archive" for the move procedure.

## Counter rules

- The counter is monotonic per lineup folder.
- The next counter is `max(NNN across all files in the folder +
  completed/) + 1`.
- Counters are zero-padded to three digits (`001`, `002`, ..., `099`,
  `100`).
- If a counter is abandoned (file deleted before completion), do NOT
  reuse it. The next promotion gets the next integer.
