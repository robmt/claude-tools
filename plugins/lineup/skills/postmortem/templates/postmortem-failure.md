# Postmortem template - failure mode

Used when something broke (verification failed, an at-bat regressed, a
deploy went bad) and the user wants to capture cause and prevention.

```markdown
# Postmortem: <topic>

Bullpen: bullpen.md
Date: YYYY-MM-DD
Mode: failure

## What broke
<concrete symptom; file:line, test name, build error>

## Proximate cause
<the immediate thing>

## Underlying cause
<the upstream decision or assumption that made the proximate cause
possible - often: the bullpen was wrong, or an at-bat skipped a step,
or scope crept>

## Detection
<who or what caught it, how fast - verification step, test, user, or
only after the fact>

## Prevention
<one concrete change to the bullpen, the lineup bootstrap, or the
at-bat template that would catch this earlier next time. Resist a
list - one suggestion>
```

Anchor every claim. Point at commits, at-bat files, test output, build
logs. If you don't have evidence, write "unknown" rather than guess.
