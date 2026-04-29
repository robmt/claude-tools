# spitball

A lightweight design conversation. The output is a small artifact called a
*spitball*: a design captured at the depth we honestly know it, no further.
We don't write hundreds of lines of forward plan that won't survive contact
with reality.

Forked from `obra/superpowers/skills/brainstorming`. Two intentional changes:

- Save location is configurable per project via `.spitball.json`.
- The skill stops after the spitball is written; it does not auto-invoke any
  planning or implementation skill. Continuation is the user's call.

The visual companion (browser-based mockups and diagrams) is included.

## Install

```bash
/plugin install spitball@claude-tools
```

Visual companion requires Node.js if you want to run mockups in a browser. The
core skill works without it.

## Configuration

Drop a `.spitball.json` at the repo root to set the save directory:

```json
{
  "saveDir": "docs/spitballs"
}
```

If the file is absent, the default `docs/spitballs/` is used. See
`skills/spitball/configuration.md` for the full schema.

## Layout

```
plugins/spitball/
  .claude-plugin/plugin.json
  README.md
  skills/spitball/
    SKILL.md                       # the skill itself
    configuration.md               # .spitball.json schema
    spitball-reviewer-prompt.md    # subagent prompt for self-review
    visual-companion.md            # browser-based mockup workflow
    scripts/                       # visual-companion server (Node)
      frame-template.html
      helper.js
      server.cjs
      start-server.sh
      stop-server.sh
```

## Attribution

Original brainstorming skill, visual companion design, and server scripts are
from [obra/superpowers](https://github.com/obra/superpowers). This plugin is a
fork at commit `6efe32c9`.
