# Suggested commands (Linux)

## Tests
There is no top-level test runner. Each plugin's Python helper has a colocated test file:

```bash
python3 plugins/bullpen/scripts/test_resolve_config.py
python3 plugins/lineup/scripts/test_resolve_config.py
```

Both use `unittest`, so `-v` works for verbose output.

## Linting / formatting
None configured — no ruff/black/flake8/mypy config in the repo. Match surrounding style by hand.

## Run the plugins' helper directly
```bash
python3 plugins/bullpen/scripts/resolve-config.py    # prints effective config JSON
python3 plugins/lineup/scripts/resolve-config.py
```

## Plugin validation (from inside Claude Code)
Use the `plugin-dev:plugin-validator` agent against a plugin to catch manifest/structure issues. Mentioned in `CONTRIBUTING.md`.

## Marketplace install (consumer-side, for manual smoke-testing)
```
/plugin marketplace add robmt/claude-tools
/plugin install bullpen@claude-tools
/plugin install lineup@claude-tools
```

## Standard Linux utilities used
`git`, `ls`, `cd`, `grep`, `find`, `cat`, `head`, `tail`, `python3` — all standard GNU coreutils on this Linux system. Nothing project-specific.

## Git
- Branch is `main`. PRs land on `main`.
- Commits use the `<plugin> <version>: <summary>` style.
- Do **not** add a `Co-Authored-By: Claude` trailer (per user memory).
