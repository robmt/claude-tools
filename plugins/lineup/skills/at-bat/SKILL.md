---
name: at-bat
description: "Use this skill to execute the current At Bat slot in an active lineup. Trigger on phrases like 'do the at-bat', 'run the at-bat', 'play the at-bat', 'step up to the plate', 'next play', 'implement what's at-bat', or whenever the user wants to actually do the work the lineup has already sharpened. Reads the current at-bat file, writes the failing test (red), implements until it passes (green), verifies scope, and moves the file to completed/. Never auto-invokes lineup."
---

# At-Bat: Execute the Current Slot

Implements the unit of work described in the current At Bat file. Pairs
with the `lineup` skill, which sharpens the next at-bat. This skill does
the work. The two are deliberately separate so the user drives the loop.

<HARD-GATE>
This skill operates ONLY on the current At Bat file. It does not read
On Deck, In the Hole, or any future slot. It does not modify the lineup
state. It does not promote slots. The implementation phase (Red, Green,
scope verification, manual verification) MUST be delegated to a fresh
general-purpose subagent - one per at-bat - so the main session's
context stays clean across a long lineup. The user-interaction gates
(testability gate, mid-Green scope-expansion surfacing) and the file
move / commit / lineup hand-off remain in the main agent. When the
implementation is verified, the main agent MUST invoke `lineup` -
this handoff is mandatory and not user-configurable. Lineup is the
verifier of at-bat's self-reported completion; bypassing it lets a
broken at-bat ship as "done." It NEVER invokes any other implementation
skill.
</HARD-GATE>

## Output rule: ASCII only

All files this skill writes (test files, code edits, commit messages, the hand-off block) MUST use ASCII characters only. No emoji, no em-dashes, no curly quotes, no arrows, no non-breaking spaces. Use `-` for dashes, `->` for arrows, `"` and `'` for quotes, `...` for ellipses. This keeps content portable across editors, terminals, and operating systems.

## Where the implementation rules live

Red, Green, scope-boundary policing, the mid-Green stop trigger, the
"default to executing" rules, and the implementation-phase anti-patterns
all govern the subagent and live in
`${CLAUDE_PLUGIN_ROOT}/skills/at-bat/templates/subagent-prompt.md`. The
main agent reads that file at step 6 and passes its body to the
subagent verbatim - do NOT inline those rules here, and do NOT execute
them yourself. They are sidecar to keep this SKILL.md focused on the
main-agent-only flow.

## Main-agent anti-patterns

- **"I'll just refresh the lineup at the end."** No. This skill always
  hands off to lineup at the end (mandatory verification). It just does
  not perform the lineup's own promote logic itself.
- **"I'll just run Red/Green in the main session."** No. The
  implementation phase belongs in a fresh subagent (one per at-bat).
  If you (the main agent) reach for Edit or a test-running Bash
  command after the testability gate has passed, you are doing the
  subagent's job and bloating the main session's context. The only
  reads/edits the main agent performs against code or tests are the
  diff sanity check (`git status`, `git diff --stat`) and the final
  `git mv` + commit.

## Checklist

Create a task for each item and complete in order:

1. **Discover active lineup.** Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.py` once. Parse
   the JSON for `effectiveSaveDir`, `commitAtBat`, `autoContinue`, and
   `repoRoot`. Use `effectiveSaveDir` as the **discovery root**. If exit
   code is non-zero, the cwd is not in a git repo while
   `nestUnderRepoName: true` - refuse and tell the user.

   Scan immediate children of the discovery root for folders that
   contain `lineup.md` without a `Status: Complete` marker.
   - Zero live -> tell user to run `lineup` (or `bullpen` first if no
     bullpen exists).
   - Exactly one live -> use it.
   - Multiple live -> ask the user which one.
2. **Read the lineup.** Find the At Bat pointer in `lineup.md`. If the
   At Bat slot is empty (no pointer), tell the user to run `lineup`
   first to sharpen one.

   While reading, also check the very first line for a `Worktree:
   <path>` header. If present, that path is the working directory for
   every subsequent step (Red, Green, scope check, manual
   verification, `git mv`, commit). `cd <path>` before running any
   command and stay there for the rest of the at-bat. The bullpen
   folder itself is unchanged - the at-bat file move and any reads of
   `lineup.md` still happen in the bullpen folder, regardless of cwd.
   If the worktree path doesn't exist on disk, stop and tell the user
   - lineup recorded a worktree that's no longer there.
3. **Read the At Bat file.** This is the file `NNN-<slug>.md` referenced
   by the At Bat pointer. Confirm it has the required sections: What,
   Definition of done, Test plan, Scope boundary, Dependencies.
4. **Verify dependencies.** If the at-bat lists prior at-bats as
   dependencies, confirm those are in `completed/`. If a dependency
   isn't met, stop and tell the user.
5. **Testability gate (BEFORE writing any code).** Look at the at-bat's
   Test plan and Definition of done. Decide:

   (a) Can the verification be expressed as a runnable command (or
       short script) whose exit code or output flips between Red
       and Green? Examples: `dotnet test X`, `curl URL`, `grep -q`,
       `npm run build`, `ls FILE`, `pnpm test`. This is the path -
       proceed to step 6 (Red).

   (b) Can it be expressed as runnable commands that YOU can execute
       (start a backend in the background, `curl`, kill the backend),
       even if it's not a test framework? Same path - treat the
       command(s) as the test and proceed.

   (c) Does the verification truly require human eyes or
       hardware-in-the-loop (visual layout judgment, animation feel,
       physical device, interactive UX)? STOP before writing code and
       surface this to the user with three options:

       1. **Restructure the at-bat** so a runnable check is possible
          (e.g., for "icon aligns with text," propose a screenshot
          diff or a CSS regression test as the actual check).
       2. **Skip TDD for this at-bat with eyes-open consent.** The
          user explicitly accepts that this one at-bat won't have
          a Red/Green - a deliberate exception, not an unexamined
          punt. Record the consent in the at-bat file.
       3. **Install or configure the missing tooling first.** This
          becomes its own at-bat (suggest adding it to the lineup);
          the current at-bat waits.

       Don't proceed to implementation until the user picks an option.
       Discovering "oh, I can't actually verify this" mid-implementation
       is the failure mode this gate exists to prevent.

6. **Delegate implementation to a fresh subagent.** Spawn ONE new
   `general-purpose` subagent (via the Agent tool) per at-bat. Never
   reuse, never spawn more than one in the happy path. Read
   `${CLAUDE_PLUGIN_ROOT}/skills/at-bat/templates/subagent-prompt.md`
   only at this step (not before - it is sidecar). Build the prompt
   exactly as that file describes: a brief at the top with the at-bat
   file content and absolute path, the worktree path (or "no worktree,
   run from <repoRoot>"), and the testability-gate outcome from step 5;
   then the body of the sidecar verbatim.

   The subagent does NOT run `git mv`, does NOT commit, and does NOT
   invoke lineup. Those are the main agent's job in steps 8-10.
7. **Process the subagent's report.** The report shape is defined in
   the sidecar; expect a fixed block with `status`, `red_command`,
   `green_command`, `files_touched`, `scope_status`,
   `manual_verification`, and `notes`.
   - `status: ok` and `scope_status: clean` -> proceed to the diff
     sanity check below, then step 8.
   - `status: scope_expansion_needed` -> the mid-Green stop trigger
     fired inside the subagent. Surface to the user with the
     ambiguity laid out:

     > "Going from Red to Green requires changes to `<file>`, which
     > the Scope boundary lists Out. The at-bat's test plan
     > implicitly needs Out work - the doc is wrong. Two ways
     > forward: (a) split, leave this at-bat test-only with the
     > assertions weakened or deferred and file a precursor at-bat
     > for the Out work, or (b) expand this at-bat's Scope boundary
     > explicitly to include `<file>`. Which?"

     Wait for the user to pick. On `expand`, edit the at-bat file's
     Scope boundary to move the file from Out to In, then re-spawn a
     fresh subagent with the updated at-bat content. (This is the one
     place the "one subagent per at-bat" rule allows a second spawn -
     the prior run was a bounced attempt, not a completed
     implementation.) On `split`, surface the precursor at-bat to the
     user as a candidate for the lineup and stop; do not move the
     file, do not commit, do not hand off.
   - Any other failure status (`red_did_not_fail`, `green_failed`,
     `manual_verification_failed`) -> stop and report the subagent's
     notes to the user. Do not move the file, do not commit, do not
     hand off. The user fixes the at-bat (or the code) and re-invokes.

   **Use the same command shape as Red and Green when possible.** If
   Red was "with backend down, `curl /foo` returns connection refused"
   and Green is "with backend up after this change, `curl /foo`
   returns 200," then verification re-runs the Green form. The flip
   between Red and Green is the test, even when there isn't a test
   framework involved.

   **If you genuinely cannot execute, propose a runnable command for
   the user.** Don't write "browser smoke test deferred to you." Write
   the exact procedure: the URLs, the start commands, the expected
   responses, what counts as pass and fail. The user should be able to
   paste your steps into a terminal and run them. Name the specific
   reason you couldn't run it yourself (not "manual verification" -
   "needs visual confirmation that the new icon aligns with the row
   text," or whatever the actual blocker is).

   Record the outcome (commands run, status codes, relevant output
   snippets, or the proposed-runnable-procedure if deferred) under a
   `## Verification` header at the bottom of the at-bat file. Kill any
   background processes you started.
8. **Diff sanity check.** Run `git status` and `git diff --stat` from
   the worktree (or `repoRoot` if no worktree). If files outside the
   Scope boundary's In list appear in the diff, treat it as
   `scope_expansion_needed` regardless of what the subagent reported -
   the diff is authoritative, the report is a self-assessment. Surface
   to the user with the same wording as above.
9. **Append to `## Notes` (if surprising).** Before moving the file,
    add freeform one-liners to the at-bat's `## Notes` section if
    anything happened that postmortem-future-you would want to know:
    a stop-trigger fired (mid-Green Out edit, scope leak revert,
    eyes-open no-test consent), the obvious approach didn't work and
    why, the user redirected shape mid-flight, sizing felt off. Skip
    if nothing was surprising - empty is honest, ritual logging is
    not. The section already exists in the template; just append.
10. **Move file to `completed/`.** Use `git mv` so history is preserved.
    The filename does not change; only its location.
11. **Commit if `commitAtBat` is true** (default). One commit covering
    the implementation, the test, and the file move. Suggested message:
    `At-bat NNN: <slug>`. The single-commit boundary matters: each
    at-bat should be revertable as one unit, so do not split this into
    multiple commits or fold it into an unrelated commit.
12. **Hand off to lineup for verification.** End your at-bat output
    with a short status block in EXACTLY this shape:

    ```
    ## At-bat NNN finished - handing to lineup for verification

    <2-5 bullet summary of what shipped: artifacts, build/test status,
    commit state, anything left uncommitted>
    ```

    Then immediately read `${CLAUDE_PLUGIN_ROOT}/skills/lineup/SKILL.md`
    and execute its checklist starting at step 1. Lineup's step 5 will
    detect your hand-off line and run verification mode against the
    just-completed at-bat. If verification passes, lineup promotes the
    next at-bat and applies its `autoContinue` rules. If verification
    fails, lineup stops with a failure report and does not promote.

    This handoff is mandatory - do not stop after the status block. Do
    NOT add a "Next step" line; lineup owns the user-facing
    call-to-action from here on.

## Configuration

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.py` to get the
merged config. The script reads `~/.bullpen.json` and
`<repoRoot>/.bullpen.json` over defaults and returns JSON. See the
bullpen plugin's `configuration.md` for the schema. At-bat uses:

- `effectiveSaveDir` - discovery root for the active lineup.
- `commitAtBat` - whether to commit the test+impl+file-move together
  after the at-bat passes (default `true`). Defaults to true so each
  at-bat is revertable as a single commit.
- `autoContinue` - passed through to lineup at hand-off; lineup decides
  whether to advance into the next at-bat after verifying.
- `repoRoot` - repo root path (used for `git mv` and commit operations).

There is no `.lineup.json`. Lineup and at-bat share bullpen's config.

## Key principles

- **One at-bat at a time.** This skill operates on the At Bat slot
  only. On Deck and In the Hole are not your business.
- **Implementation runs in a fresh subagent.** One per at-bat. The main
  agent owns gates, diff sanity, file move, commit, and hand-off; the
  subagent owns Red/Green/scope/manual-verify. Implementation rules
  live in the sidecar at `templates/subagent-prompt.md`.
- **Scope boundary is law.** The diff sanity check is the main agent's
  enforcement; the subagent's `scope_status` is a self-report and the
  diff overrules it.
- **Always hand off to lineup.** Mandatory verification of the
  at-bat's self-reported completion. Never bypass.
- **Run inside the worktree if one is named.** If `lineup.md` starts
  with a `Worktree: <path>` header, `cd` into it in step 2 and stay
  there for every command and commit.
