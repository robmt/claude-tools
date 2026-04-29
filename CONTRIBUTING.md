# Contributing

How to add or update a plugin in this marketplace.

## Add a new plugin

1. Create the plugin directory under `plugins/<plugin-name>/`.
2. Add a manifest at `plugins/<plugin-name>/.claude-plugin/plugin.json`:

   ```json
   {
     "name": "<plugin-name>",
     "version": "0.1.0",
     "description": "One sentence about what it does."
   }
   ```

3. Add the plugin's components in standard locations:

   ```
   plugins/<plugin-name>/
     .claude-plugin/plugin.json
     README.md
     skills/<skill-name>/SKILL.md
     commands/<name>.md
     agents/<name>.md
     hooks/hooks.json
   ```

4. Write a `README.md` at the plugin root that explains:
   - what the plugin does
   - how to install it (`/plugin install <plugin-name>@claude-tools`)
   - any configuration files it reads
   - attribution if forked or derived from another project

5. Register the plugin in `.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "<plugin-name>",
     "source": "./plugins/<plugin-name>",
     "description": "Same one-line description as the manifest.",
     "version": "0.1.0"
   }
   ```

   Keep `description` and `version` in sync between `marketplace.json` and the plugin's `plugin.json`.

## Update an existing plugin

1. Bump `version` in both `plugins/<plugin-name>/.claude-plugin/plugin.json` and the entry in `.claude-plugin/marketplace.json`.
2. Update the plugin's `README.md` and the table in the root `README.md` if the description changed.

## Versioning

Use semver (`MAJOR.MINOR.PATCH`):

- `PATCH` for fixes that do not change behavior the user relies on
- `MINOR` for new skills, commands, or options that are backward compatible
- `MAJOR` for breaking changes (renamed skill, removed option, changed schema)

## Validation

Before opening a PR, verify:

- `marketplace.json` is valid JSON and lists the plugin
- the plugin manifest exists at `plugins/<plugin-name>/.claude-plugin/plugin.json`
- versions match between the marketplace entry and the plugin manifest
- the plugin's `README.md` includes install instructions and attribution if forked

You can run the `plugin-dev:plugin-validator` agent against a plugin to catch common issues.

## Conventions

- Plugin names are lowercase, hyphen-separated, and match the directory name.
- Skill names follow the same rule and live under `skills/<name>/SKILL.md`.
- Forks from other projects must credit the upstream project and commit hash in the plugin's `README.md`.
- Keep plugin scope small. One plugin, one purpose.
