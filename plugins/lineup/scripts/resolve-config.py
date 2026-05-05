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
    "commitSpitball": True,
    "commitAtBat": True,
    "nestUnderRepoName": False,
    "autoContinue": "prompt",
}

VALID_AUTO_CONTINUE = {"never", "prompt", "always"}


def apply_layer(config, layer):
    """Merge one config layer into the running config.

    Honors a legacy ``autoCommit`` key by mapping it to ``commitSpitball``
    when no explicit ``commitSpitball`` is set in the same layer. This lets
    users who answered "no commit" at setup time keep that meaning for the
    spitball doc without accidentally suppressing per-at-bat commits, which
    are needed for revertable history.
    """
    if not isinstance(layer, dict):
        return
    if "autoCommit" in layer and "commitSpitball" not in layer:
        config["commitSpitball"] = layer["autoCommit"]
    for k, v in layer.items():
        if k in DEFAULTS:
            config[k] = v


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


def _spitball_entry(path: Path):
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0
    return {"name": path.name, "path": str(path), "mtime": mtime}


def _safe_iterdir(path: Path):
    try:
        return list(path.iterdir())
    except OSError:
        return []


def _is_complete(folder: Path):
    lineup_md = folder / "lineup.md"
    if not lineup_md.exists():
        return None
    try:
        head = lineup_md.read_text(errors="replace").lstrip()
    except OSError:
        return None
    return head.startswith("Status: Complete")


def scan_spitballs(effective):
    """Walk effectiveSaveDir for live and completed spitball folders.

    Live: top-level folders with spitball.md whose lineup.md does not
    start with Status: Complete (or has no lineup.md yet).

    Completed:
    - folders inside <effective>/completed/ that contain spitball.md
      (the archived layout written by lineup on completion), AND
    - top-level folders whose lineup.md starts with Status: Complete
      (legacy, pre-archival layout - included so postmortem can still
      find them).

    Returns (live, completed, lineup_active). Both lists sorted by
    mtime descending. lineup_active is True iff at least one live
    folder has a lineup.md.
    """
    live, completed = [], []
    lineup_active = False

    eff = Path(effective)
    if not eff.is_dir():
        return live, completed, lineup_active

    for child in _safe_iterdir(eff):
        if not child.is_dir():
            continue
        # The archive bucket: a top-level "completed" dir without its
        # own spitball.md. Recurse one level for archived spitballs.
        if child.name == "completed" and not (child / "spitball.md").exists():
            for grandchild in _safe_iterdir(child):
                if not grandchild.is_dir():
                    continue
                if not (grandchild / "spitball.md").exists():
                    continue
                completed.append(_spitball_entry(grandchild))
            continue
        if not (child / "spitball.md").exists():
            continue
        complete = _is_complete(child)
        if complete is True:
            completed.append(_spitball_entry(child))
        else:
            if complete is False:
                lineup_active = True
            live.append(_spitball_entry(child))

    live.sort(key=lambda e: e["mtime"], reverse=True)
    completed.sort(key=lambda e: e["mtime"], reverse=True)
    return live, completed, lineup_active


def main():
    root = repo_root()

    config = dict(DEFAULTS)
    apply_layer(config, load_json(Path.home() / ".spitball.json"))
    if root:
        apply_layer(config, load_json(root / ".spitball.json"))

    if config["autoContinue"] not in VALID_AUTO_CONTINUE:
        config["autoContinue"] = DEFAULTS["autoContinue"]

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

    live_spitballs, completed_spitballs, lineup_active = scan_spitballs(effective)

    result = {
        "saveDir": save_dir,
        "commitSpitball": config["commitSpitball"],
        "commitAtBat": config["commitAtBat"],
        "nestUnderRepoName": config["nestUnderRepoName"],
        "autoContinue": config["autoContinue"],
        "repoName": rname,
        "effectiveSaveDir": effective,
        "repoRoot": str(root) if root else None,
        "lineupActive": lineup_active,
        "liveSpitballs": live_spitballs,
        "completedSpitballs": completed_spitballs,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
