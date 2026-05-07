# Review-only at-bat (main-agent fork at step 3)

The main `at-bat` agent reads this file ONLY when step 3 detects
`Form: review` on line 1 of the at-bat file. Review-only at-bats
have no implementation phase: the user reviews something that
already exists (or runs an app to check behavior) and reports
back. There is no subagent, no Red/Green, no diff sanity check.

When this sidecar fires, it REPLACES SKILL.md steps 5-9
(testability gate, subagent dispatch, report processing, diff
sanity, Notes append). Step 4 (dependency check) still runs;
steps 10-12 (file move, commit, lineup hand-off) still run when
the verdict is positive.

## Procedure

1. **Confirm the form fields.** A review-form at-bat has: `Form:
   review` on line 1, then `# At-Bat NNN: <title>`, then `## What`,
   `## Definition of done`, `## Review procedure`, `## Scope
   boundary`, `## Dependencies`, `## Progress`, `## Notes`. The
   distinguishing field is `## Review procedure` (where standard
   form has `## Test plan`). If the file says `Form: review` but
   lacks a Review procedure, stop and tell the user the at-bat is
   malformed.

2. **Run dependency check** per SKILL.md step 4. Review at-bats
   often depend on a prior implementation at-bat ("review the new
   flow added in 003-wire-auth"). If a dependency isn't in
   `completed/`, stop and tell the user.

3. **Skip the testability gate, subagent spawn, and watcher.**
   None apply. Even if `watchAtBat: true`, do NOT start a
   Monitor - there is no subagent producing Progress entries.

4. **Append a start line to `## Progress`.**

   ```
   HH:MM review presented to user
   ```

   Use 24-hour local time.

5. **Present the Review procedure to the user verbatim.** Output
   a short framing block, then the procedure exactly as it
   appears in the at-bat file. The user should be able to
   execute it from your message without scrolling back to the
   file. Shape:

   ```
   ## Review at-bat NNN: <title>

   This at-bat is a human review - no code changes. Run the
   procedure below, then reply with your verdict.

   ### What you're reviewing
   <copied from the at-bat's What section>

   ### Procedure
   <copied from the at-bat's Review procedure section, verbatim>

   ### Definition of done
   <copied from the at-bat's Definition of done>

   ---

   Reply with `pass`, `fail`, or `pass with notes: <text>` /
   `fail: <feedback>` once you're done.
   ```

6. **Wait for the user's reply.** Do NOT proceed without a clear
   verdict. Acceptable shapes:

   - `pass` / `looks good` / `approved` / `lgtm` -> positive
     verdict, proceed to step 7.
   - `pass with notes: <text>` / `pass but <text>` -> positive
     verdict; capture the notes for the at-bat's `## Notes`
     section.
   - `fail` / `not yet` / `no` / `fail: <feedback>` -> negative
     verdict, stop. Append the feedback to `## Notes`. Do NOT
     move the file. Do NOT commit. Do NOT hand off to lineup as
     success. Tell the user the at-bat stays open and suggest
     they either edit it into a follow-up or add a remediation
     at-bat to the lineup.
   - Ambiguous reply -> ask once, plainly: "I need a clear
     pass/fail verdict for at-bat NNN. Which is it?"

7. **On positive verdict, append to `## Progress`:**

   ```
   HH:MM user replied: <verbatim reply, trimmed to one line>
   ```

   Then append a `## Verification` section (or extend an
   existing one) capturing:
   - The verdict.
   - Any notes the user provided.
   - Timestamp.

   If the user provided pass-with-notes feedback, also append a
   one-liner to `## Notes` for postmortem signal.

8. **Proceed to SKILL.md step 10 (Move file to `completed/`).**
   Use `git mv` per the standard flow.

9. **Commit (SKILL.md step 11) if `commitAtBat: true`.** The
   commit contains only the at-bat .md file (move + verdict
   appends). Suggested message:
   `Review at-bat NNN: <slug>`. Note that this commit has no
   code changes - it captures the human review decision in git
   so the bullpen archive shows what was reviewed and when.

10. **Hand off to lineup (SKILL.md step 12).** Use the standard
    hand-off block, with the summary noting this was a review
    at-bat and the verdict.

## Why this form exists

Not every step toward a bullpen's destination is code. Some are
"the user looks at the running app and decides if it's right",
"the user reads the proposed plan and approves it", "the user
checks the deploy on staging." Modeling these as at-bats keeps
the bullpen log honest about what work happened, even when the
work was a human checkpoint and not a commit. Review at-bats
also let the lineup explicitly schedule a human-loop step rather
than tacking it onto an implementation at-bat's Verification
section as an afterthought.

## What review at-bats are NOT for

- **Skipping TDD on an implementation at-bat.** That's the
  no-test escape (`Form: no-test`), not review-only. Review-only
  has no implementation at all.
- **Running tests the subagent already wrote.** The subagent's
  scope already covers Red/Green and any executable manual
  verification. If the subagent is doing it, it's not a review
  at-bat.
- **Asking the user to clarify scope mid-implementation.** Use
  the scope-expansion stop trigger or the testability gate, not
  a separate review at-bat.

If you find yourself reaching for review-only to paper over an
implementation that should have been written and tested, push
back: a review at-bat is for verifying state, not for avoiding
the work of producing it.
