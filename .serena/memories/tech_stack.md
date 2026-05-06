# Tech stack

- **Markdown** is the dominant content type. Plugins are mostly skills (`SKILL.md`), templates, and READMEs — no application code in the typical sense.
- **Python 3** (3.12 observed via `__pycache__`) for the small `scripts/resolve-config.py` helpers in each plugin. Standard library only; no third-party deps, no `requirements.txt`, no `pyproject.toml`.
- **JSON** for plugin manifests (`plugin.json`) and the marketplace manifest (`marketplace.json`).
- **No build system, no package manager, no CI config** committed.

## Targets
- Linux/macOS/Windows runtime for plugin consumers — README explicitly notes ASCII-only file output for cross-platform safety. Keep new content ASCII unless there is a strong reason otherwise.
