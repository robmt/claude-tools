# lineup.md file template

Used by the lineup skill when creating or updating `lineup.md` for a
spitball folder.

## Active lineup

```markdown
# Lineup: <topic>

Spitball: spitball.md

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

## Completed lineup

When the spitball's completion criteria are met, prepend
`Status: Complete` as the first line of the file:

```markdown
Status: Complete

# Lineup: <topic>

Spitball: spitball.md

## At Bat
(none - spitball delivered)

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

## Counter rules

- The counter is monotonic per lineup folder.
- The next counter is `max(NNN across all files in the folder +
  completed/) + 1`.
- Counters are zero-padded to three digits (`001`, `002`, ..., `099`,
  `100`).
- If a counter is abandoned (file deleted before completion), do NOT
  reuse it. The next promotion gets the next integer.
