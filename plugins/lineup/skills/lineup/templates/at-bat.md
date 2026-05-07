# At-bat file template

Used by lineup when creating a new `NNN-<slug>.md` file (in the lineup
folder root for the current At Bat, or initially during first-run
bootstrap). The at-bat skill reads this same file when executing an
at-bat.

## Three forms

Every at-bat is one of three forms. The form is signaled by an
explicit `Form:` line at the very top of the file (line 1, before
the `# At-Bat NNN: ...` header). Absence of a `Form:` line means
`Form: standard` for backward compatibility.

- `Form: standard` - implementation + Red/Green executable test.
  The default and most common.
- `Form: no-test` - implementation + manual verification because
  the test framework genuinely can't reach it (visual layout,
  hardware-in-loop, etc.). The at-bat skill's testability gate
  asks the user for eyes-open consent before proceeding.
- `Form: review` - no implementation. The user reviews something
  (an app, a deployed change, a proposed plan, an external state)
  and reports back. The at-bat skill skips subagent dispatch
  entirely and waits for the user's verdict.

Lineup creates the at-bat file with the appropriate form when
sharpening. If the user redirects ("the next at-bat should be a
review of the staging deploy", "have the user run the app and
check"), lineup writes `Form: review` and uses the review-form
fields below. The form is locked when the at-bat is created -
shifting between forms means editing the file before invoking
at-bat, or creating a different at-bat.

## Standard form (Red/Green executable test)

```markdown
Form: standard

# At-Bat NNN: <title>

## What
<concrete description of the unit of work>

## Definition of done
<observable outcome that proves "done">

## Test plan
- Red: <a failing test/command that captures "done">
- Green: <the same test/command, now passing>

## Scope boundary
- In: <thing>
- Out: <related thing we are NOT touching here>

## Dependencies
- <prior at-bat or external thing>

## Progress
<append-only log written DURING the at-bat. Each entry is one line,
prefixed with `HH:MM` (24-hour local). Subagent appends after each
meaningful step; main agent appends at gate transitions. The first
line is `Started: <ISO 8601 timestamp>` written by the main agent
just before spawning the subagent. This section is read by the
watcher (when watchAtBat is on) for thrash signals and runtime
ceiling. Empty until the at-bat actually runs.>

## Notes
<freeform appends, written during or after the at-bat. Surprises,
course corrections, scope leaks caught, why the obvious approach
didn't work, anything postmortem-future-you will wish you'd kept.
Leave empty if nothing was surprising. One-liners beat paragraphs.

Progress vs Notes: Progress is real-time log ("14:05 green attempt
1, fails: <reason>"); Notes is curated postmortem-worthy signal
("the obvious approach didn't work because X"). Different
audiences, different lifetimes.>
```

Red and Green should be the same command - only the expected outcome
flips. `dotnet test X` exits 1 before, exits 0 after. `curl URL`
returns 404 before, 200 after. If you find yourself writing
"Red: project doesn't exist" or "Red: visual inspection," reshape into
a runnable command, or use the no-test escape below with explicit
eyes-open consent.

## No-automated-test escape

If the work genuinely cannot be tested by a runnable command (pure
docs, no-behavior config, exploratory spike, visual layout requiring
human eyes), replace the Test plan section with explicit honesty:

```markdown
## Test plan
- No automated test: <specific reason - "needs visual confirmation
  the new icon aligns with the row text," not a generic "manual">
- Manual verification: <runnable procedure: URLs, start commands,
  expected responses, what counts as pass and fail. The user should
  be able to paste these steps into a terminal.>
```

**Push back on the escape if the at-bat could be tested.** The escape
is for cases where automated testing genuinely doesn't fit, not for
cases where it's inconvenient. The at-bat skill's testability gate
will stop at the start of the at-bat and ask the user to confirm
eyes-open consent if this form is used.

The full file for a no-test at-bat begins with `Form: no-test` on
line 1; the rest of the structure (What, Definition of done, Test
plan, Scope boundary, Dependencies, Progress, Notes) is identical
to the standard form.

## Review-only form (human verifies, no code)

Use when the at-bat's entire work IS the user reviewing something
that already exists - running the app, inspecting a deployed
change, signing off on a proposed plan, sanity-checking an
external system. There is no implementation, no subagent, no
Red/Green. The at-bat is the procedure plus the capture of the
user's verdict.

```markdown
Form: review

# At-Bat NNN: <title>

## What
<what is being reviewed - "the new auth flow in the running app",
"the deploy on staging", "the proposed migration plan in
docs/auth-migration.md", "the QuickBooks sync output for this
week">

## Definition of done
<what counts as "done" - "user confirms the flow works as
expected end-to-end", "user signs off on the plan", "deploy
verified by user against the live environment". The verdict is
the user's reply, not a command's exit code.>

## Review procedure
- <step 1: exactly what the user does. Include URLs, start
  commands, files to open, etc. The user should be able to read
  this section and execute it without further explanation.>
- <step 2: what they look for>
- <pass criterion: what they should see if it's good>
- <fail criterion: what they should see if it's not, or what
  feedback they'd give>

## Scope boundary
- In: <what's being reviewed>
- Out: <related thing NOT in scope of this review - so the user
  knows what to ignore even if they notice it>

## Dependencies
- <prior at-bat or external state - "003-deploy-to-staging" must
  be in completed/ before this review at-bat makes sense>

## Progress
<append-only log. Main agent appends `HH:MM review presented to
user` when it shows the procedure, and `HH:MM user replied:
<verdict>` when the user answers. No subagent, no other entries.>

## Notes
<surprises - feedback that didn't match expectations, follow-up
at-bats the user wanted, redirects.>
```

The at-bat skill detects `Form: review` at step 3 (Read the At
Bat file). It skips the testability gate, the subagent, the diff
sanity check, and any code/test handling. Instead it presents the
Review procedure to the user verbatim, waits for their reply,
records the verdict, and proceeds to the file move + commit +
lineup hand-off as a code-free at-bat (the only file changing in
the commit is the at-bat .md itself, moved to `completed/`).

If the user's reply is negative (e.g., "the flow breaks at step
3, see screenshot"), the at-bat skill stops and surfaces the
feedback. Do NOT move the file, do NOT commit, do NOT hand off
to lineup as success - the review failed. The user typically
either edits the at-bat into a follow-up (e.g., "fix the step 3
bug" as a new standard at-bat in the lineup) or re-runs the
review after a fix lands.
