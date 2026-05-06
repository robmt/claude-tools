# At-bat file template

Used by lineup when creating a new `NNN-<slug>.md` file (in the lineup
folder root for the current At Bat, or initially during first-run
bootstrap). The at-bat skill reads this same file when executing an
at-bat.

## Standard form (Red/Green executable test)

```markdown
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

## Notes
<freeform appends, written during or after the at-bat. Surprises,
course corrections, scope leaks caught, why the obvious approach
didn't work, anything postmortem-future-you will wish you'd kept.
Leave empty if nothing was surprising. One-liners beat paragraphs.>
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
