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
| [spitball](plugins/spitball/) | 0.6.0 | Lightweight design conversation that produces a small spitball artifact. Forked from `obra/superpowers` brainstorming with global+per-repo config, optional repo-name nesting for shared save dirs, separate `commitSpitball`/`commitAtBat` flags, and an `autoContinue` setting that controls how the lineup -> at-bat handoff works. Includes a `spitball-setup` skill for first-run configuration. ASCII-only file output for cross-platform safety. |
| [lineup](plugins/lineup/) | 0.7.1 | Companion to spitball. Manages a rolling 3-slot view (At Bat / On Deck / In the Hole) of work toward a spitball's destination. Three skills: `lineup` (reviewer) sharpens the next at-bat AND verifies a just-completed at-bat's Definition of done before promoting; `at-bat` (implementer) does the work with red/green testing - including an early testability gate that stops before code is written if verification needs human eyes - and hands off to lineup unconditionally on completion; `postmortem` reflects on the spitball + at-bat history when a spitball is delivered or when something broke. `autoContinue` config governs the lineup -> at-bat side of the loop. |

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
