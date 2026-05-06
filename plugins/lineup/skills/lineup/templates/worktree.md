# Worktree decision (first-run bootstrap step 4)

A worktree decision is made once, at first-run bootstrap, and
applies to every at-bat in the bullpen. Lineup is the only skill
that creates the worktree; at-bat reads the `Worktree:` header
from `lineup.md` and operates inside that path.

Ask the user whether to run this bullpen in a git worktree.
Recommend `yes` if the bullpen's scope looks substantial; `no` for
small, contained bullpens.

## When to recommend a worktree

- The bullpen's scope spans multiple at-bats and is likely to
  touch files outside a single area.
- The work is risky or speculative and the user benefits from a
  clean branch they can throw away.
- The user is currently mid-flight on another branch in the main
  checkout and shouldn't have to stash/switch.

## When to skip a worktree

- The bullpen is small (one or two at-bats) and contained.
- The work is a quick fix or a doc change.
- The bullpen folder lives outside any git repo (`repoRoot` is
  null).

## Procedure when the user opts in

1. **Pick a branch name.** Default: the bullpen folder's slug with
   the leading `YYYY-MM-DD-` stripped. Offer this default and let
   the user override.
2. **Pick a worktree path.** Default:
   `<repoRoot>/../worktrees/<slug>` (sibling-of-repo). Confirm
   with the user; their workflow may want it elsewhere.
3. **Run** `git -C <repoRoot> worktree add <path> -b <branch>`.
   If the branch already exists, drop the `-b` and add it as a
   pre-existing branch. If the path already exists, stop and ask
   the user.
4. **Prepend** `Worktree: <path>` as the first line of
   `lineup.md` (above any other content, including a future
   `Status: Complete` marker - those compose as two header lines).
5. **Mention the worktree in the hand-back** so the user knows
   where to `cd` if they want to inspect work in progress.

When the user declines, do nothing. No `Worktree:` header is
written; at-bat will run from the current cwd as usual.
