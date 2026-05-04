---
name: postmortem
description: "Use this skill to write a postmortem reflecting on a spitball's at-bats: what shipped vs the plan, what surprised us, whether the at-bats were sized right, what to carry forward, what to avoid. Trigger on phrases like 'postmortem', 'retro', 'retrospective', 'wrap up the spitball', 'look back at the spitball', 'what did we learn from', 'do a postmortem', or whenever a spitball has been delivered (Status: Complete) and the user wants to reflect. Reads the spitball + lineup.md + completed at-bats + git log; asks 3-5 reflection questions; writes postmortem.md in the spitball folder. Works in two modes: completion (default, spitball delivered) and failure (something broke; what was the cause)."
---

# Postmortem: Reflect On A Spitball's At-Bats

Looks back over a spitball and the at-bats executed against it, captures
what we learned, and writes a small `postmortem.md` artifact next to
`spitball.md`. Pairs with `lineup` and `at-bat`: those drive the work
forward, this looks back.

<HARD-GATE>
This skill never writes code, never invokes `lineup` or `at-bat`, and
never modifies `spitball.md` or `lineup.md`. It reads existing artifacts
and writes exactly one new file: `postmortem.md` in the spitball folder
(or `postmortem-NNN.md` if one already exists). It does not advance the
loop in any direction.
</HARD-GATE>

## Output rule: ASCII only

All files this skill writes (`postmortem.md`, commit messages,
user-facing prose) MUST use ASCII characters only. No emoji, no
em-dashes, no curly quotes, no arrows, no non-breaking spaces. Use `-`
for dashes, `->` for arrows, `"` and `'` for quotes, `...` for ellipses.

## When to use

- A spitball was delivered (lineup.md starts with `Status: Complete`),
  and the user wants to reflect before moving on.
- Mid-flight reflection: the user explicitly asks for one even though
  the spitball isn't complete (rare but valid).
- Failure mode: something went wrong (verification failed, an at-bat
  regressed, the design didn't survive contact). The user invokes
  postmortem to capture cause and prevention.

The skill picks up the right mode from chat context. If unclear, ask
once: "Completion postmortem (looking back over a delivered spitball)
or failure postmortem (something broke; what was the cause)?"

## Anti-patterns

- **"Let me write the whole epic."** No. The postmortem is short and
  honest: 3-5 sections, each a few sentences. If a section has nothing
  honest to say, write "Nothing notable" and move on. Don't pad.
- **"Score the team."** No. The postmortem is about the work and the
  process, not about who did what. Names appear only when concretely
  useful for follow-up.
- **"Recommend a giant refactor."** No. The carry-forward section is
  for patterns to repeat or traps to avoid in the next spitball.
  Concrete next-spitball suggestions live in the user's head until they
  open `/spitball`. Don't try to write the next plan here.
- **"Speculate on root cause without evidence."** In failure mode,
  point at the commits, the at-bat files, the test output, the build
  logs. If you don't have evidence, say "unknown" rather than guess.

## Checklist

Create a task for each item and complete in order:

1. **Resolve config.** Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.py` once. Parse
   the JSON for `effectiveSaveDir`, `commitAtBat`, `repoRoot`, and
   `liveSpitballs`. If exit code is non-zero, the cwd is not in a git
   repo while `nestUnderRepoName: true` - refuse and tell the user.

2. **Pick the target spitball.** Try chat-context inference first (same
   rules as lineup's discovery): exact slug or path, topic words
   matching a folder name, the most recent `/spitball` or `/lineup` or
   `/at-bat` invocation. If matched, announce and proceed.

   Without a chat match, scan immediate children of `effectiveSaveDir`
   for folders that contain `spitball.md`. Two candidate sets:
   - **Completed**: folders whose `lineup.md` starts with
     `Status: Complete`.
   - **Live**: folders whose `lineup.md` does not start with
     `Status: Complete` (or has no `lineup.md`).

   Default rules:
   - Zero candidates -> stop and tell the user no spitball folder was
     found.
   - Exactly one (live or completed) -> use it.
   - Multiple -> list candidates with their status (live vs complete)
     sorted by mtime descending and ask which to operate on.

3. **Verify the folder has at-bats to reflect on.** Look for either a
   `completed/` directory with at least one `NNN-*.md` file, or
   numbered at-bat files (`NNN-*.md`) at the folder root. If neither
   exists, stop and tell the user: "There are no at-bats to look back
   on. The postmortem skill operates on at-bat history. If you want to
   reflect on the spitball alone, open the file and write notes
   directly." Do NOT proceed with an at-bat-less postmortem.

4. **Read the artifacts.**
   - `spitball.md` - the design and completion criteria.
   - `lineup.md` - current state (or final state if completed).
   - All `NNN-*.md` files in `completed/` and at the folder root - the
     executed at-bats.
   - Optional: `git log --oneline` for commits touching this folder
     (`git log -- <effectiveSaveDir>/<folder>/`) and commits in the
     `repoRoot` from the spitball's start date forward, scoped to paths
     touched by the at-bats. Use these to ground claims about what
     shipped.

5. **Decide the mode.**
   - **Completion mode**: lineup.md starts with `Status: Complete`, or
     the user said "wrap up" / "deliver" / "retro the spitball." This
     is the default.
   - **Failure mode**: the user said "verification failed" / "regressed"
     / "broke" / "what went wrong," or there's a `## Verification
     failed` block in a recent at-bat or in chat context. Use a slightly
     different question set (see "Failure mode questions" below).

6. **Ask reflection questions one at a time.** 3-5 questions max. Wait
   for each answer before moving on. Multiple-choice when a useful
   shape exists; open-ended otherwise. The questions should be
   *informed* by what you read in step 4 - if `001-foo.md` was
   completed but `002-bar.md` ballooned into 5 commits, ask about
   sizing on bar specifically. Generic questions are weak; pointed
   ones surface useful insight.

   See "Question library" below for starting points. Pick the 3-5 most
   relevant; do not ask all of them.

7. **Synthesize and write `postmortem.md`** to the spitball folder. If
   `postmortem.md` already exists, write `postmortem-002.md` (next
   unused integer; never overwrite a previous postmortem). Use the
   structure in "Postmortem file structure" below. Anchor every claim
   in concrete evidence: at-bat file names, commit short SHAs, test
   output snippets. Avoid abstract praise or blame.

8. **Self-review.** Re-read what you wrote. Look for:
   - Padding ("the team did a great job") - cut.
   - Speculation framed as fact - either anchor it or mark as "unknown."
   - Sections with nothing honest to say - replace with "Nothing
     notable" rather than fabrication.
   - Action items disguised as observations - if it's an action, list
     it under Carry-forward; if it's not, drop it.

9. **User reviews.** Ask the user to read the file before stopping:

   > "Postmortem written to `<path>`. Please review and tell me if you
   > want any changes."

   If they request changes, edit and re-run step 8. Only stop when they
   approve.

10. **Commit if `commitAtBat` is true** (default). The postmortem lives
    in the spitball folder alongside the at-bat history; it shares the
    at-bat commit flag, not the spitball-doc commit flag (which only
    governs the original spitball write). Use a short commit message
    like `Postmortem: <topic>`. If `commitAtBat` is false, leave it for
    the user.

11. **Hand back to user.** End with a short closing block in EXACTLY
    this shape:

    ```
    ## Postmortem written

    <1-3 bullets summarizing the most useful insight - what to carry
    forward, what to avoid>
    ```

    Do NOT add a "Next step" line. The postmortem is terminal. The user
    decides whether to start a new spitball, return to existing work,
    or close the loop here.

## Question library

Pick 3-5 of these per run, weighted by what the artifacts and chat
context suggest is interesting. Don't ask all of them.

### Completion mode

- **What shipped vs the plan?** Specifically, did any of the spitball's
  Completion criteria not get met, or get met in a way that differs
  from the spitball's described approach?
- **What surprised us?** Constraints we didn't see in the spitball.
  Tools or APIs that didn't behave as expected. Decisions that flipped
  mid-stream.
- **At-bat sizing.** Were any at-bats too big (multiple commits, dragged
  on, scope crept)? Too small (felt like ceremony for a one-line
  change)? Just right? Name the at-bat file numbers.
- **Verification value.** Did lineup's verification step catch anything
  real, or was it always rubber-stamping? If it caught something,
  describe it.
- **Carry-forward.** Patterns that worked well in this spitball that we
  want to repeat. (One or two; resist building a process manual.)
- **Avoid next time.** Specific traps we hit that a future-spitball-self
  would benefit from knowing. (Same: one or two.)

### Failure mode questions

- **What broke?** Concretely - what test failed, what build error, what
  symptom. Name files and lines.
- **Proximate cause.** The immediate thing that did it. (Don't stop
  here.)
- **Underlying cause.** The decision or assumption upstream that made
  the proximate cause possible. (Often: the spitball was wrong, or an
  at-bat skipped a step, or scope crept.)
- **Detection.** Was it caught at verification, by a test, by a user,
  or only after the fact? How fast?
- **Prevention.** What single change to the spitball, the lineup
  bootstrap, or the at-bat template would catch this earlier next
  time? (One concrete suggestion. Resist a list.)

## Postmortem file structure

Write `postmortem.md` (or `postmortem-NNN.md`) with this skeleton.
Sections may be omitted when truly empty; write "Nothing notable" if
the section was asked but had no real content. The asterisk on Mode
indicates: replace `<completion or failure>` with the actual mode.

```markdown
# Postmortem: <topic>

Spitball: spitball.md
Date: YYYY-MM-DD
Mode: <completion or failure>

## What shipped (vs the plan)
<concrete: which spitball criteria met, any deviations, evidence>

## Surprises
<concrete: things we did not expect, with at-bat or commit anchors>

## At-bat sizing
<which at-bats felt right, which were too big or small, by NNN>

## Carry forward
<one or two patterns to repeat>

## Avoid next time
<one or two traps to avoid>
```

For failure mode, replace the post-shipped sections with:

```markdown
## What broke
<concrete symptom; file:line, test name, build error>

## Proximate cause
<the immediate thing>

## Underlying cause
<the upstream decision or assumption>

## Detection
<who or what caught it, how fast>

## Prevention
<one concrete change to spitball, lineup, or at-bat template>
```

## Process Flow

```dot
digraph postmortem {
    "Resolve config" [shape=box];
    "Pick target spitball" [shape=box];
    "Has at-bats?" [shape=diamond];
    "Stop, no at-bats" [shape=doublecircle];
    "Read artifacts" [shape=box];
    "Decide mode" [shape=diamond];
    "Ask 3-5 questions" [shape=box];
    "Write postmortem.md" [shape=box];
    "Self-review" [shape=box];
    "User reviews?" [shape=diamond];
    "Commit if commitAtBat" [shape=box];
    "Hand back" [shape=doublecircle];

    "Resolve config" -> "Pick target spitball";
    "Pick target spitball" -> "Has at-bats?";
    "Has at-bats?" -> "Stop, no at-bats" [label="no"];
    "Has at-bats?" -> "Read artifacts" [label="yes"];
    "Read artifacts" -> "Decide mode";
    "Decide mode" -> "Ask 3-5 questions" [label="completion or failure"];
    "Ask 3-5 questions" -> "Write postmortem.md";
    "Write postmortem.md" -> "Self-review";
    "Self-review" -> "User reviews?";
    "User reviews?" -> "Write postmortem.md" [label="changes"];
    "User reviews?" -> "Commit if commitAtBat" [label="approved"];
    "Commit if commitAtBat" -> "Hand back";
}
```

## Configuration

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.py` to get the
merged config. Postmortem uses these fields:

- `effectiveSaveDir` - directory to scan for spitball folders.
- `commitAtBat` - whether to commit the postmortem.md after writing
  (postmortem lives in the at-bat-history side of the folder, so it
  rides the at-bat commit flag, not the spitball-doc flag).
- `repoRoot` - repo root path (used for staging files relative to the
  repo).

There is no `.postmortem.json`. Postmortem shares spitball's config.

## Key principles

- **Anchored, not abstract.** Every claim points at a file, a commit,
  or a test. Vague reflection is theater.
- **Short.** A postmortem under one printed page is more useful than a
  long one. Resist the urge to compose.
- **No next plan.** This is the look-back. The look-forward starts when
  the user opens `/spitball` again.
- **Honest about unknowns.** "We don't know why X happened" is a
  legitimate finding. Mark it and move on.
- **Never auto-invoke.** Postmortem is terminal. Do not chain into
  spitball, lineup, or at-bat at the end.
