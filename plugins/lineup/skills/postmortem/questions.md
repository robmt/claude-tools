# Postmortem question library

Pick 3-5 of these per run, weighted by what the artifacts and chat
context suggest is interesting. Don't ask all of them. Tailor each to
specific evidence: name at-bat numbers, commit SHAs, file paths, test
output you actually saw. Generic questions are weak; pointed ones
surface useful insight.

## Completion mode

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

## Failure mode

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
