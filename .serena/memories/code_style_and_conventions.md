# Style and conventions

## Naming
- Plugin names: lowercase, hyphen-separated, match directory name.
- Skill names: same rule, live under `skills/<name>/SKILL.md`.
- Bullpen artifact directories: `docs/bullpen/<YYYY-MM-DD>-<slug>/`.

## Markdown content
- Skills follow Claude Code's SKILL.md frontmatter format (`---` block with `name`, `description`, etc.).
- Forks must credit upstream project + commit hash in the plugin's README.
- Keep plugin scope small — "one plugin, one purpose" is in CONTRIBUTING.md.

## Python (scripts/)
- Module docstrings at top of file describing purpose + behavior + exit conditions.
- 4-space indent, snake_case functions, `UPPER_SNAKE` module-level constants.
- Triple-quoted docstrings on non-trivial functions explaining *why* (e.g., legacy key precedence) — not just *what*.
- Standard library only. Subprocess for git, `pathlib.Path` for paths, `json` for I/O.
- Tests use `unittest` + `unittest.mock.patch`, loaded via `importlib.util` because the script filename has a hyphen.
- File ends with `if __name__ == "__main__": unittest.main()` for tests.

## Versioning (CONTRIBUTING.md)
- Semver: PATCH for non-behavioral fixes, MINOR for new backward-compatible skills/options, MAJOR for breaking changes.
- Keep `version` and `description` in lockstep between `plugins/<name>/.claude-plugin/plugin.json` and the `marketplace.json` entry.

## Commit style (observed in `git log`)
- One-liner subject `<plugin> <version>: <imperative summary>` (e.g., `lineup 1.3.0: capture in-flight learnings in at-bat ## Notes section`).
- User memory says: **omit the Claude co-author trailer**.
