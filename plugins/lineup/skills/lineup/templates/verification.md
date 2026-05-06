# Verification mode (lineup checklist step 5)

Run these checks before promoting when invoked from at-bat.

1. **Locate the at-bat file.** The just-completed at-bat is the
   most-recently-modified file in `completed/` for the active lineup.
   Confirm it exists and that the lineup folder's `lineup.md` still
   references it as At Bat (i.e., at-bat moved the file but lineup
   hasn't yet updated the pointer - that's exactly the state lineup
   is here to resolve).
2. **Read the Definition of done section.** Each line is a criterion.
3. **Verify each criterion concretely.** Don't just read; check.
   - File-existence claims -> confirm the file exists.
   - Build claims (`dotnet build` clean, `npm run build` succeeds) ->
     re-run the named command. Capture exit status.
   - Test claims -> re-run the named test command. Ideally this is
     the SAME command at-bat ran for Red and Green; only the expected
     exit code/output flips.
   - Grep claims (e.g., "no remaining `StaticPlugin*` references") ->
     re-run the grep.
   - Behavior claims that can be made executable (start a backend in
     the background, `curl`, kill the backend) -> run them yourself.
     Don't accept "deferred to user" if you have the tools.
   - Behavior claims with eyes-open no-test consent (recorded in the
     at-bat's `## Verification` section) -> trust the consent and
     skip those checks. The user accepted the exception explicitly.
   - Behavior claims that genuinely require human eyes (visual
     layout, interactive UX) -> the at-bat should have left a
     runnable verification procedure in its `## Verification`
     section. Re-state it concisely and ask the user to confirm.
     Don't silently mark "done."
4. **Verify the at-bat's Scope boundary.** Glance at the diff (or
   `git status` since the prior commit, if `commitAtBat: true` was
   on) and confirm nothing listed in the Scope boundary's Out
   section was touched. If something Out was touched, that's a
   verification failure.
5. **Decide.**
   - All criteria met, scope respected -> continue to checklist
     step 6 (Check completion). Note in the hand-back: "Verified
     at-bat NNN: <list of checks that passed>."
   - Any criterion fails -> STOP. Output a verification-failure
     report: header `## Verification failed for at-bat NNN`, list
     of failed checks with specifics (command output, missing
     files, scope leaks). Do NOT update `lineup.md`. Do NOT
     promote. Do NOT invoke at-bat. The user fixes the issue and
     re-invokes lineup, or moves the file back out of `completed/`
     to redo the at-bat.

When invoked directly by the user (no at-bat hand-back in the
prior turn), skip verification - the user is asserting the prior
state.
