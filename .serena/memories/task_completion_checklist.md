# When a task is complete

There is no CI, no formatter, no linter. The completion checklist is light but specific:

1. **If you touched Python in `plugins/*/scripts/`** — run that plugin's tests:
   ```bash
   python3 plugins/<plugin>/scripts/test_resolve_config.py
   ```
   No coverage, no ruff. Just make the tests pass.

2. **If you bumped a plugin's behavior** — update *both* version fields:
   - `plugins/<plugin>/.claude-plugin/plugin.json` -> `version`
   - `.claude-plugin/marketplace.json` -> matching `plugins[].version`
   They must match. Same for the `description` field.

3. **If you changed user-visible plugin behavior** — update:
   - the plugin's own `README.md`
   - the table row in the root `README.md` (description / version)

4. **Validation before PR** (per `CONTRIBUTING.md`):
   - `marketplace.json` parses as JSON and lists the plugin
   - `plugins/<plugin>/.claude-plugin/plugin.json` exists
   - versions match between marketplace entry and plugin manifest
   - plugin README has install instructions and (if forked) attribution

5. **Optional but recommended** — invoke the `plugin-dev:plugin-validator` agent on the plugin you changed.

6. **Commit style** — `<plugin> <new-version>: <imperative summary>`. **Do not** add `Co-Authored-By: Claude` (user memory).
