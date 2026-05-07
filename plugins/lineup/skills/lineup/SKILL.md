---
name: lineup
description: "Use this skill to review the rolling work state next to a bullpen and sharpen the next at-bat. Trigger on 'update the lineup', 'review the lineup', 'what's at-bat', 'what's next', 'sharpen the next at-bat', 'is the bullpen done'. Also trigger when the user shapes the next at-bat ('the next at-bat should X') - lineup owns that, not base Claude. Promotes the slots, stops. Never auto-invokes at-bat."
---

# Lineup: Review the Next Three Batters

Manages a small rolling state document next to a bullpen. The bullpen
owns the destination. The lineup owns three slots: At Bat (concrete),
On Deck (fuzzy), In the Hole (very fuzzy). This skill reads current
state and updates the lineup. It does NOT do the work - that is
`at-bat`.

## Hard rules

- Never write code. Never plan more than one new In-the-Hole bullet
  per cycle.
- Three slots, hard cap. Filesystem is truth (no JSON sidecars). The
  bullpen owns completion - lineup reads criteria, doesn't define them.
- When invoked from at-bat, verify the just-completed at-bat's
  Definition of done before promoting (see
  `templates/verification.md`). On failure, stop with a failure
  report; do NOT promote.
- Never archive a bullpen on Claude's judgment. The completion gate
  requires explicit user confirmation (see `templates/completion.md`).
  `autoContinue` does NOT bypass the gate - it governs the at-bat
  loop, not the archive decision.
- May invoke `at-bat` only at hand-back, only when the user has
  opted in via `autoContinue` (`always`, `session` for this
  conversation, or `yes` at the per-handoff prompt). NEVER invoke
  any other implementation skill.
- At first-run bootstrap, may run `git worktree add` if the user
  opts in (see `templates/worktree.md`). On confirmed completion
  archive, may run `git worktree remove`. Those are the only
  filesystem/git mutations lineup performs outside of writing
  markdown files.
- Never run build or test commands (`vue-tsc`, `npm test`,
  `dotnet build`, `cypress`, etc.) and never inspect the
  implementation working tree (`git status`, `git diff`, `git log`
  against the repoRoot). The only files lineup reads are
  `bullpen.md`, `lineup.md`, and at-bat files under the bullpen
  folder. The only files lineup writes are `lineup.md` and a new
  at-bat file. The only commits lineup makes contain only those
  two files (plus the folder rename on a confirmed-completion
  archive). If you find yourself wanting to verify implementation
  state, stop - that is at-bat's job, not lineup's.

## Output rule: ASCII only

All files this skill writes (`lineup.md`, at-bat files, commit
messages, user-facing prose) MUST use ASCII characters only. No
emoji, em-dashes, curly quotes, arrows, or non-breaking spaces.
Use `-` for dashes, `->` for the At Bat pointer, `"` and `'` for
quotes, `...` for ellipses.

## Checklist

1. **Discover active lineup.** Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.py` once.
   Parse the JSON for `effectiveSaveDir`, `commitAtBat`,
   `autoContinue`, `repoRoot`, and `liveBullpens` (an array of
   `{name, path, mtime}` for every folder under `effectiveSaveDir`
   with a `bullpen.md` not marked `Status: Complete`, sorted by
   mtime descending). If exit code is non-zero, the cwd is not in
   a git repo while `nestUnderRepoName: true` - refuse and tell
   the user.

   **Infer target from chat context first.** If a
   `liveBullpens[*].name` matches recent messages (exact slug or
   path, topic-word match like "the auth rewrite" matching
   `2026-05-04-auth-rewrite`, or a recent `/bullpen` hand-back
   referencing a folder under `effectiveSaveDir`), announce it
   ("Picking up the `<name>` bullpen from earlier in this chat -
   say if that's wrong.") and use it without prompting. Otherwise:
   - 0 live -> stop, tell user to run bullpen first.
   - 1 live -> use it.
   - >1 live -> list names (most recent first), ask which.

2. **Verify bullpen.md exists** in the target folder. If not,
   refuse; tell the user lineup requires a bullpen anchor.

3. **Read the bullpen.** Identify completion criteria. If the
   bullpen lacks explicit criteria, ask the user to add them -
   lineup can't determine "done" without them.

4. **Read or create `lineup.md`.** If absent, this is the first
   lineup cycle for this bullpen: see "First-run bootstrap" below.

5. **Verification mode (when invoked from at-bat).** If the
   immediately prior assistant turn was an at-bat hand-back
   ("At-bat NNN finished - handing to lineup for verification"),
   read `${CLAUDE_PLUGIN_ROOT}/skills/lineup/templates/verification.md`
   and follow it. On failure, stop with the prescribed report; do
   NOT update `lineup.md`, do NOT promote. On success, continue.
   When invoked directly by the user (no at-bat hand-back in the
   prior turn), skip verification entirely - including any
   independent investigation of working-tree state. Trust
   `completed/` and `lineup.md` as written. Do not run `git
   status`, `git diff`, or build/test commands to "check" whether
   the prior at-bat is really done.

   **Unfinished-prior-at-bat check.** Before promoting, confirm
   the file that `lineup.md`'s At Bat pointer references has been
   moved into `completed/`. If it still exists at the top level
   of the bullpen folder (not in `completed/`), the previous
   at-bat has not finished - moving the file is at-bat's last
   step. Stop and tell the user:

   > At-bat NNN appears unfinished: still At Bat in lineup.md and
   > the file is not in completed/. Run /at-bat to finish it (or
   > move the file manually if it is already done), then
   > re-invoke lineup.

   Do NOT attempt to finish the at-bat yourself - no commits, no
   `git mv`, no implementation. Lineup only promotes; it never
   plays at-bat.

6. **Check completion.** Compare current state (codebase, recent
   commits, completed at-bats) to the bullpen's completion
   criteria. If criteria appear met, read
   `${CLAUDE_PLUGIN_ROOT}/skills/lineup/templates/completion.md`
   and follow the gate + archive procedure. On `archive`, skip
   ahead to step 9 (commit) and step 10 (hand-back); steps 7-8
   are not run on a confirmed-complete archive. On `not yet`,
   fall through to step 7 and continue the normal loop. On
   `cancel`, stop with no writes.

7. **Promote.**
   - On Deck -> At Bat: create the next `NNN-<slug>.md` file using
     the `templates/at-bat.md` sidecar. Counter is the next unused
     integer for this folder; never reuse, never reset.
   - In the Hole -> On Deck (inline bullet in `lineup.md`).
   - Draft a new In the Hole bullet. Exactly one. No more.

   **Honor user direction.** If the user's invoking message
   included specific direction for the next at-bat ("the next
   at-bat should use a multiselect combobox with chips", "this
   one is Vue test only"), incorporate it into the new at-bat's
   What / Definition of done / Test plan / Scope boundary rather
   than inferring from the bullpen alone. The user is the source
   of truth; lineup's job is to shape, not to outvote. If the
   direction conflicts with the bullpen's stated destination,
   surface the conflict back to the user before writing.

   **Three at-bat forms.** Most at-bats are `Form: standard`
   (implementation + Red/Green); the at-bat skill detects and
   handles `Form: no-test` (eyes-open consent) and `Form: review`
   (no implementation, user verifies something) automatically.
   Pick the form that fits when shaping:

   - User says "have me run the app and check" / "review the
     staging deploy" / "approve the proposed plan first" ->
     `Form: review`. Fill the Review procedure section instead of
     Test plan; see `templates/at-bat.md` "Review-only form."
   - User says "this one needs visual confirmation" / "no good
     way to test this automatically" -> `Form: no-test`. Keep
     the Test plan section but use the no-test escape shape.
   - Otherwise -> `Form: standard`. Default; omit the Form line
     for backward compatibility, or write `Form: standard`
     explicitly. Both are fine.

   Write the form line on line 1 of the at-bat file when it is
   `no-test` or `review`. Lineup never silently picks `review`
   without user signal - always ask if you are unsure.

8. **Update `lineup.md`.** Replace the At Bat pointer with the new
   file name. Update On Deck and In the Hole. Append the
   previously-completed at-bat to the Completed list (its file
   should already be in `completed/` - that move is `at-bat`'s
   job, not yours).

9. **Commit if `commitAtBat` is true** (default). Commit the new
   at-bat file and the updated `lineup.md` together with a short
   message like `Lineup: promote NNN-<slug>`. On a confirmed
   completion archive, the commit also captures the folder move
   into `completed/`; use a message like
   `Lineup: <topic> complete (archived)`.

10. **Hand back to user.** End your message with a hand-back block
    in EXACTLY this shape so the call-to-action is impossible to
    miss:

    ```
    ## Lineup sharpened

    <2-4 bullet summary of what changed: new At Bat, On Deck, In the Hole,
    commit state>

    ---

    **Next step:** run `/at-bat` to play NNN-<slug>.
    ```

    On first-run bootstrap, replace the header with
    `## Lineup bootstrapped` and the summary with the three slots
    you just filled. On completion, replace the block with a
    `## Bullpen delivered` header, list the new archive path
    (`Archived to <effectiveSaveDir>/completed/<folder>/`), and
    replace the Next-step line with a single passive pointer:
    `Optional: run /postmortem to reflect.` The loop is over - do
    not prompt or auto-continue.

    The `---` rule and bold **Next step:** line are required -
    they are the visual anchor that tells the user the loop is
    paused waiting for them.

    **Honor `autoContinue`** (from step 1's helper output, or from
    earlier in this conversation if the user said "session" at a
    prior prompt):

    - `"never"` -> end with the hand-back block above and stop.
      The user types `/at-bat` themselves.
    - `"prompt"` (default) -> after the hand-back block, ask:
      `Continue to /at-bat? (yes / session / always / no)`. On
      `yes` -> invoke at-bat now. On `session` -> invoke at-bat
      now and treat `autoContinue` as `"always"` for the rest of
      this conversation. On `always` -> invoke at-bat now AND
      write `autoContinue: "always"` into `<repoRoot>/.bullpen.json`
      (creating it if absent), so the setting persists across
      sessions for this repo. On `no` -> stop.
    - `"always"` -> skip the prompt, just invoke at-bat directly
      after the hand-back block. The user can interrupt at any
      time.

    This is the only place lineup may invoke at-bat. The hard
    rules above stay in force everywhere else: never auto-invoke
    when the user hasn't opted in via `autoContinue`. The user
    always drives the loop - `autoContinue` is a shortcut for
    typing the next command, not a license to chain.

## First-run bootstrap

If `lineup.md` does not exist yet for a bullpen:

1. Read the bullpen carefully. Identify the first concrete unit
   of work the user could plausibly do toward the destination.
2. Identify two more units, progressively fuzzier.
3. Create `lineup.md` with all three slots filled:
   - **At Bat**: pointer to a new `001-<slug>.md` file (created
     using the `templates/at-bat.md` sidecar).
   - **On Deck**: inline bullet, fuzzy.
   - **In the Hole**: inline bullet, very fuzzy.
4. **Worktree decision.** Read
   `${CLAUDE_PLUGIN_ROOT}/skills/lineup/templates/worktree.md`
   and follow it. If the user opts in, the procedure prepends a
   `Worktree:` header to `lineup.md`.
5. Confirm with the user before committing. First-run
   bootstrapping is the one place the reviewer is making
   structural decisions; the user should approve the initial
   three slots.

## Notes appends

Each at-bat file has a `## Notes` section. Lineup appends
freeform one-liners to it on three triggers (verification
surprises, user-redirected promotions, `not yet` completion
replies) so the postmortem skill can read in-flight surprises
later instead of losing them on `/clear`. See
`${CLAUDE_PLUGIN_ROOT}/skills/lineup/templates/notes.md` when one
of those triggers fires.

Bar: only when surprising or non-obvious. Empty Notes sections
are honest; ritual logging is noise.

## Templates

Sidecars live under `${CLAUDE_PLUGIN_ROOT}/skills/lineup/templates/`
and are read only when the corresponding branch fires - they are
NOT loaded by default:

- `at-bat.md` - new at-bat file structure (three forms:
  standard Red/Green, no-test escape with eyes-open consent,
  and review-only for human verification at-bats).
- `lineup.md` - active and completed `lineup.md` structure +
  monotonic counter rules.
- `verification.md` - verification-mode procedure (checklist
  step 5).
- `completion.md` - completion gate + archive procedure
  (checklist step 6).
- `worktree.md` - worktree decision (first-run bootstrap step 4).
- `notes.md` - notes-append rules (the three triggers above).

## Configuration

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.py` to
get the merged config. The script reads `~/.bullpen.json` and
`<repoRoot>/.bullpen.json` over defaults, derives the repo name,
and returns JSON. See the bullpen plugin's `configuration.md` for
the schema. Lineup uses these fields:

- `effectiveSaveDir` - directory to scan for bullpen folders.
  Already includes the `<repo-name>` subfolder when
  `nestUnderRepoName: true`.
- `liveBullpens` - pre-computed list of folders with a
  non-complete `bullpen.md`, sorted most-recently-touched first.
  Used for chat-context inference of the target bullpen.
- `commitAtBat` - whether to commit the new at-bat file and
  updated `lineup.md` after promotion (default `true`).
- `autoContinue` - `"never"` / `"prompt"` (default) / `"always"`.
  Governs whether lineup invokes at-bat after promotion. See
  step 10's hand-back rules.
- `repoRoot` - repo root path (used for staging files relative
  to the repo).

There is no `.lineup.json`. Lineup shares bullpen's config.
