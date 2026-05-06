# Finalize: self-review + user review gate

After the bullpen document has been written (checklist step 6), run
the inline self-review (step 7), then ask the user to review (step 8).

## Self-review

After writing the bullpen document, look at it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or
   vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other?
   Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single piece of
   work, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two
   different ways? If so, pick one and make it explicit.
5. **Speculation check:** Anything written as if known that is
   actually a guess? Either remove it or mark it explicitly as
   speculation.

Fix any issues inline. No need to re-review, just fix and move on.

## User review gate

After the self-review passes, ask the user to review the written
file before stopping:

> "Bullpen written and committed to `<path>`. Please review it and
> let me know if you want to make any changes. When you are ready
> to start work or build a plan, kick off the next thing yourself."

If `lineupActive` was `true` in step 1's config output, append one
short line to that message:

> "(Lineup is in use here - run `/lineup` when you're ready to fold
> this into the rolling work view.)"

Do NOT add the nudge when `lineupActive` is `false`. The nudge is a
passive pointer, not a recommendation; never auto-invoke `lineup`.

Wait for the user's response. If they request changes, make them
and re-run the self-review loop. Only stop once the user approves.

## Stop

The bullpen ends here. Do NOT invoke any planning or implementation
skill. If the user has a follow-up planning skill they prefer (for
example, `north-star-planning` or `writing-plans`), they will
invoke it themselves.
