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
| [spitball](plugins/spitball/) | 0.5.0 | Lightweight design conversation that produces a small spitball artifact. Forked from `obra/superpowers` brainstorming with global+per-repo config, optional repo-name nesting for shared save dirs, and no auto-handoff to a planning skill. Includes a `spitball-setup` skill for first-run configuration. Detects whether `lineup` is in use here and surfaces a passive pointer in the hand-back. |
| [lineup](plugins/lineup/) | 0.4.0 | Companion to spitball. Manages a rolling 3-slot view (At Bat / On Deck / In the Hole) of work toward a spitball's destination. Two skills: `lineup` (reviewer) sharpens the next at-bat; `at-bat` (implementer) does the work with red/green testing. Honors `nestUnderRepoName` for per-repo discovery. Infers target spitball from chat context when possible. |

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
