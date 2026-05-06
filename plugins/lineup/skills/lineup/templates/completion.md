# Completion gate + archive (lineup checklist step 6)

Lineup never archives a bullpen on its own judgment. Before any
`Status: Complete` write, folder rename, worktree removal, or
archive commit, lineup MUST ask the user to confirm.

`autoContinue` does NOT bypass this gate. The at-bat loop autopilot
governs whether lineup invokes at-bat between cycles; it has nothing
to say about whether the bullpen is finished. Treating `"always"` as
license to archive turns a fuzzy judgment call into a silent burial.

## Gate procedure

1. **Show your work.** Print each completion criterion from the
   bullpen verbatim, and next to it the concrete evidence you're
   using to call it met: the at-bat that delivered it, the commit
   SHA, the file path, the test that's now passing, the grep that
   comes up empty. One line of evidence per criterion. If a
   criterion's evidence is weak ("seems done", "probably covered
   by 003"), say so plainly - that is exactly the kind of judgment
   the user needs to see before saying yes.
2. **Ask.** End with the literal prompt:
   `Completion criteria look met. Archive the bullpen now? (archive / not yet / cancel)`
3. **Branch on the reply.**
   - `archive` -> proceed with the archive procedure below.
   - `not yet` -> the user disagrees with one or more criteria, or
     wants more work first. Fall through to checklist step 7
     (promote slots) and continue the normal loop. Do NOT write
     `Status: Complete`. Do NOT move the folder. Do NOT remove the
     worktree. Append a one-liner tagged `(bullpen-level)` to the
     most-recently-completed at-bat's Notes recording what they
     said was missing (see `templates/notes.md`).
   - `cancel` -> stop entirely. Do not promote, do not archive,
     do not commit.
4. **No silent ratification.** Never treat absence of objection,
   `autoContinue: "always"`, or a previous session's `archive`
   confirmation as standing consent for the current archive. If the
   reply is ambiguous, ask again with the same three options.

## Archive procedure (only after `archive` confirmation)

1. **Update `lineup.md` in place** at the current location,
   prepending `Status: Complete` per the lineup template's
   "Completed lineup" section. Do this before the move so the move
   is a clean rename.
2. **Ensure the archive bucket exists.** If
   `<effectiveSaveDir>/completed/` is missing, create it. The
   bucket is a flat directory of completed bullpen folders; do not
   nest by year or topic.
3. **Move the folder.** Rename
   `<effectiveSaveDir>/<folder>/` to
   `<effectiveSaveDir>/completed/<folder>/`. If `commitAtBat` is
   true, use `git mv` so history follows. If false, use a plain
   rename.
4. **Refuse on collision.** If
   `<effectiveSaveDir>/completed/<folder>/` already exists, stop
   and tell the user; do not overwrite. Manual resolution required.
5. **Commit (if `commitAtBat` is true)** with a message like
   `Lineup: <topic> complete (archived)`. The commit captures both
   the `Status: Complete` edit and the rename.

The archive bucket is reserved: bullpens must not be named
`completed`. The resolve-config scan treats a top-level
`completed/` folder without its own `bullpen.md` as the bucket and
walks one level down for archived folders.

## Worktree teardown (if `lineup.md` carries a `Worktree:` header)

1. Strip the `Worktree:` header from `lineup.md` (the line is gone
   in the completed form; only `Status: Complete` remains at the
   top).
2. Run `git -C <repoRoot> worktree remove <path>`. If the worktree
   has uncommitted changes, this fails - stop and tell the user.
   They can either commit/discard and re-invoke lineup, or remove
   the worktree manually with `--force`.
3. Note the removal in the hand-back ("Worktree at `<path>`
   removed") so the user knows the cleanup happened.

The branch the worktree was on is left intact so the user can merge
or delete it on their own schedule.
