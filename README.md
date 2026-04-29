# claude-tools

A small Claude Code plugin marketplace.

## Add this marketplace

In any Claude Code session:

```
/plugin marketplace add robmt/claude-tools
```

Then browse and install plugins:

```
/plugin
```

Or install directly:

```
/plugin install <plugin-name>@claude-tools
```

## Plugins

| Plugin | Version | Description |
| --- | --- | --- |
| [spitball](plugins/spitball/) | 0.2.0 | Lightweight design conversation that produces a small spitball artifact. Forked from `obra/superpowers` brainstorming with configurable save location and no auto-handoff to a planning skill. Includes a `spitball-setup` skill for first-run configuration. |

## Layout

```
.claude-plugin/
  marketplace.json     # marketplace manifest, lists every plugin
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json
    README.md
    skills/, commands/, agents/, hooks/, ...
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or update a plugin.

## License

Each plugin states its own license and attribution in its README. The marketplace metadata in this repo is offered without warranty.
