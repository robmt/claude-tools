# Postmortem template - completion mode

Used when a bullpen has been delivered (`Status: Complete` on
`lineup.md`) and the user wants to reflect on the at-bat history.

```markdown
# Postmortem: <topic>

Bullpen: bullpen.md
Date: YYYY-MM-DD
Mode: completion

## What shipped (vs the plan)
<concrete: which bullpen criteria met, any deviations, evidence>

## Surprises
<concrete: things we did not expect, with at-bat or commit anchors>

## At-bat sizing
<which at-bats felt right, which were too big or small, by NNN>

## Carry forward
<one or two patterns to repeat>

## Avoid next time
<one or two traps to avoid>
```

Sections may be omitted when truly empty; write "Nothing notable" if
the section was asked but had no real content. Anchor every claim in
concrete evidence (at-bat file names, commit short SHAs, test output).
Avoid abstract praise or blame.
