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


def repo_name(root: Path):
    """Parse remote.origin.url to org-repo; fall back to root basename."""
    try:
        url = subprocess.check_output(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        url = ""
    if url:
        # git@github.com:org/repo.git -> org/repo
        # https://github.com/org/repo(.git) -> org/repo
        m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", url)
        if m:
            return m.group(1).replace("/", "-")
    return root.name


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
