#!/usr/bin/env python3
"""Resolve the effective spitball config for the current cwd.

Reads ~/.spitball.json (global) and <repoRoot>/.spitball.json (per-repo),
merges them per-key over hardcoded defaults, derives the repo name from
git, and computes the effective save directory. Prints the result as
JSON to stdout.

Exits non-zero (with an error JSON on stdout) if nestUnderRepoName is
true but the cwd is not inside a git repo.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULTS = {
    "saveDir": "docs/spitballs",
    "autoCommit": True,
    "nestUnderRepoName": False,
}


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        with path.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(
            f"warning: could not parse {path}: {e}",
            file=sys.stderr,
        )
        return None


def repo_root():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return Path(out) if out else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


_ROUTING_SEGMENTS = {"_git", "scm", "v3"}


def repo_name(root: Path):
    """Derive a stable folder name from remote.origin.url.

    Walks the URL's path segments and joins the last two human-named ones
    with a dash. Routing markers like Azure DevOps's ``_git``, Bitbucket
    Server's ``scm``, and Azure SSH's ``v3`` are filtered so URLs like
    ``https://dev.azure.com/org/project/_git/repo`` produce ``project-repo``
    instead of ``_git-repo``.
    """
    try:
        url = subprocess.check_output(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        url = ""
    if not url:
        return root.name

    path = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", "", url)
    if ":" in path and "/" not in path.split(":", 1)[0]:
        host, _, rest = path.partition(":")
        path = f"{host}/{rest}"

    parts = path.split("/")[1:]
    if parts and parts[-1].endswith(".git"):
        parts[-1] = parts[-1][:-4]
    parts = [p for p in parts if p and p not in _ROUTING_SEGMENTS]

    if not parts:
        return root.name
    if len(parts) == 1:
        return parts[0]
    return f"{parts[-2]}-{parts[-1]}"


def main():
    root = repo_root()

    config = dict(DEFAULTS)
    home_cfg = load_json(Path.home() / ".spitball.json")
    if isinstance(home_cfg, dict):
        config.update({k: v for k, v in home_cfg.items() if k in DEFAULTS})
    if root:
        repo_cfg = load_json(root / ".spitball.json")
        if isinstance(repo_cfg, dict):
            config.update({k: v for k, v in repo_cfg.items() if k in DEFAULTS})

    save_dir = config["saveDir"]
    if not os.path.isabs(save_dir):
        base = root if root else Path.cwd()
        save_dir = str(base / save_dir)

    rname = None
    effective = save_dir
    if config["nestUnderRepoName"]:
        if not root:
            print(json.dumps({
                "error": "nestUnderRepoName is true but cwd is not inside a git repo",
                "fix": "run from inside a git repo, or set nestUnderRepoName: false in this project's .spitball.json",
            }))
            sys.exit(1)
        rname = repo_name(root)
        effective = os.path.join(save_dir, rname)

    lineup_active = False
    live_spitballs = []
    try:
        eff = Path(effective)
        if eff.is_dir():
            candidates = []
            for child in eff.iterdir():
                if not child.is_dir():
                    continue
                if not (child / "spitball.md").exists():
                    continue
                lineup_md = child / "lineup.md"
                if lineup_md.exists():
                    try:
                        head = lineup_md.read_text(errors="replace").lstrip()
                        if head.startswith("Status: Complete"):
                            continue
                    except OSError:
                        pass
                    lineup_active = True
                try:
                    mtime = child.stat().st_mtime
                except OSError:
                    mtime = 0
                candidates.append((mtime, child))
            candidates.sort(key=lambda t: t[0], reverse=True)
            live_spitballs = [
                {"name": c.name, "path": str(c), "mtime": m}
                for m, c in candidates
            ]
    except OSError:
        pass

    result = {
        "saveDir": save_dir,
        "autoCommit": config["autoCommit"],
        "nestUnderRepoName": config["nestUnderRepoName"],
        "repoName": rname,
        "effectiveSaveDir": effective,
        "repoRoot": str(root) if root else None,
        "lineupActive": lineup_active,
        "liveSpitballs": live_spitballs,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
