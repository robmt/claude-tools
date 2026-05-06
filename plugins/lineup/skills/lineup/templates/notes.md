# Notes appends

Each at-bat file has a `## Notes` section (see `at-bat.md`).
Lineup appends freeform one-liners to it on three triggers, so the
postmortem skill can read in-flight surprises later instead of
losing them on `/clear`.

## Triggers

- **Verification mode** (verification.md, step 5). If verification
  failed, append the failure to the just-completed at-bat's Notes.
  If verification passed but something surfaced (a check needed to
  be re-run unusually, scope was tight, the at-bat was sized wrong
  in retrospect), append that too.
- **Promotion** (checklist step 7). If the user's invoking message
  redirected the next at-bat's shape ("the next at-bat should X"),
  append a one-liner to the newly-promoted at-bat's Notes
  recording the redirect and why - the at-bat file itself reads
  as if the shape was always the plan, but the Notes preserve the
  pivot.
- **Completion gate, `not yet` reply** (completion.md). When the
  user declines the archive prompt, append a one-liner tagged
  `(bullpen-level)` to the most-recently-completed at-bat's Notes
  recording what they said was missing - that's the
  sizing-and-criteria signal postmortem cares about.

## Bar

Only when surprising or non-obvious. Do not narrate routine
promotion. Empty Notes sections are honest; ritual logging is
noise. One-liners beat paragraphs.
