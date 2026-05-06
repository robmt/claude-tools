# Guidelines and design patterns

## Plugin philosophy
- **One plugin, one purpose** (CONTRIBUTING.md). Resist letting a plugin grow extra responsibilities.
- **ASCII-only file output** — the bullpen plugin explicitly chose ASCII for cross-platform safety. Match this in any new plugin that writes user-visible files.
- **Forks credit upstream** — bullpen credits `obra/superpowers`. Any new fork must include upstream project + commit hash in the plugin README.

## Config resolution pattern (bullpen + lineup)
Both plugins share the same shape in `scripts/resolve-config.py`:
1. Hardcoded `DEFAULTS` dict at module top.
2. Layered merge: defaults <- `~/.bullpen.json` (global) <- `<repoRoot>/.bullpen.json` (per-repo).
3. Per-key application via `apply_layer` — *not* a deep dict merge.
4. Legacy key fallbacks honored explicitly (`.spitball.json` filename, `commitSpitball`, `autoCommit`) with most-specific key winning.
5. Outputs effective config as JSON on stdout. Non-zero exit on hard errors with error JSON on stdout.

If you add a new config knob, mirror this layering and document legacy aliases inline.

## Skill structure
- `SKILL.md` is the entry point — frontmatter triggers, body explains workflow.
- Multi-file skills colocate `templates/` (lineup, postmortem) and supporting prose (`configuration.md`, `bullpen-reviewer-prompt.md` for bullpen).
- Skills are designed to **stop and hand off** rather than auto-chain. The `autoContinue` config governs whether `lineup -> at-bat` auto-runs; lineup-archiving is gated on **explicit user confirmation regardless of autoContinue**.

## Workflow vocabulary (baseball metaphor)
- **bullpen** = design artifact (the warm-up).
- **lineup** = ordered slate of at-bats (At Bat / On Deck / In the Hole).
- **at-bat** = one unit of implementation work, done with red/green tests.
- **postmortem** = retrospective once the bullpen is delivered or has failed.

Use this vocabulary consistently in skill prose and commit messages.

## Don't
- Don't introduce a build system, package manager, or CI without discussing first — repo deliberately stays plain-files.
- Don't add Python deps beyond stdlib in `scripts/`.
- Don't deep-merge config layers; per-key replacement is the contract.
