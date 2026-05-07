#!/usr/bin/env python3
"""Resolve the effective bullpen config for the current cwd.

Reads ~/.bullpen.json (global) and <repoRoot>/.bullpen.json (per-repo),
merges them per-key over hardcoded defaults, derives the repo name from
git, and computes the effective save directory. Prints the result as
JSON to stdout.

Legacy: if .bullpen.json is absent, falls back to the older
.spitball.json filename at the same path with a one-line stderr note.

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
    "saveDir": "docs/bullpen",
    "commitBullpen": True,
    "commitAtBat": True,
    "nestUnderRepoName": False,
    "autoContinue": "prompt",
    "watchAtBat": False,
    "watchCeilingSec": 1800,
}

VALID_AUTO_CONTINUE = {"never", "prompt", "always"}


def apply_layer(config, layer):
    """Merge one config layer into the running config.

    Honors two legacy keys that map to ``commitBullpen``:
    - ``commitSpitball`` (the previous name for this knob)
    - ``autoCommit`` (the original name, predating the spitball/at-bat split)

    The most-specific key in the layer wins: ``commitBullpen`` over
    ``commitSpitball`` over ``autoCommit``. This lets users who answered
    "no commit" at setup time keep that meaning for the bullpen doc
    without accidentally suppressing per-at-bat commits, which are needed
    for revertable history.
    """
    if not isinstance(layer, dict):
        return
    if "commitBullpen" not in layer:
        if "commitSpitball" in layer:
            config["commitBullpen"] = layer["commitSpitball"]
        elif "autoCommit" in layer:
            config["commitBullpen"] = layer["autoCommit"]
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


def load_config_layer(base: Path):
    """Load the config layer at ``base``, preferring .bullpen.json.

    Falls back to legacy .spitball.json with a one-line stderr note if
    only the legacy file is present. Returns the parsed dict (or None).
    """
    bp = base / ".bullpen.json"
    if bp.exists():
        return load_json(bp)
    sp = base / ".spitball.json"
    if sp.exists():
        print(
            f"note: reading legacy {sp}; rename to {bp} when convenient.",
            file=sys.stderr,
        )
        return load_json(sp)
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
    # Collapse a trailing duplicate. Azure DevOps's
    # dev.azure.com/{org}/{project}/_git/{repo} leaves [org, project, repo]
    # after _git is filtered; when project == repo (a common pattern), the
    # naive join would yield "repo-repo".
    if parts[-1] == parts[-2]:
        return parts[-1]
    return f"{parts[-2]}-{parts[-1]}"


def _bullpen_entry(path: Path):
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


def _has_bullpen_doc(folder: Path):
    """A folder is a bullpen folder if it contains bullpen.md or the
    legacy spitball.md. New folders are written with bullpen.md; legacy
    folders are still recognized so existing data keeps working.
    """
    return (folder / "bullpen.md").exists() or (folder / "spitball.md").exists()


def _is_complete(folder: Path):
    lineup_md = folder / "lineup.md"
    if not lineup_md.exists():
        return None
    try:
        head = lineup_md.read_text(errors="replace").lstrip()
    except OSError:
        return None
    return head.startswith("Status: Complete")


def scan_bullpens(effective):
    """Walk effectiveSaveDir for live and completed bullpen folders.

    Live: top-level folders with bullpen.md (or legacy spitball.md) whose
    lineup.md does not start with Status: Complete (or has no lineup.md
    yet).

    Completed:
    - folders inside <effective>/completed/ that contain bullpen.md (or
      legacy spitball.md), the archived layout written by lineup on
      completion, AND
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
        # own bullpen doc. Recurse one level for archived folders.
        if child.name == "completed" and not _has_bullpen_doc(child):
            for grandchild in _safe_iterdir(child):
                if not grandchild.is_dir():
                    continue
                if not _has_bullpen_doc(grandchild):
                    continue
                completed.append(_bullpen_entry(grandchild))
            continue
        if not _has_bullpen_doc(child):
            continue
        complete = _is_complete(child)
        if complete is True:
            completed.append(_bullpen_entry(child))
        else:
            if complete is False:
                lineup_active = True
            live.append(_bullpen_entry(child))

    live.sort(key=lambda e: e["mtime"], reverse=True)
    completed.sort(key=lambda e: e["mtime"], reverse=True)
    return live, completed, lineup_active


def main():
    root = repo_root()

    config = dict(DEFAULTS)
    apply_layer(config, load_config_layer(Path.home()))
    if root:
        apply_layer(config, load_config_layer(root))

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
                "fix": "run from inside a git repo, or set nestUnderRepoName: false in this project's .bullpen.json",
            }))
            sys.exit(1)
        rname = repo_name(root)
        effective = os.path.join(save_dir, rname)

    live_bullpens, completed_bullpens, lineup_active = scan_bullpens(effective)

    result = {
        "saveDir": save_dir,
        "commitBullpen": config["commitBullpen"],
        "commitAtBat": config["commitAtBat"],
        "nestUnderRepoName": config["nestUnderRepoName"],
        "autoContinue": config["autoContinue"],
        "watchAtBat": config["watchAtBat"],
        "watchCeilingSec": config["watchCeilingSec"],
        "repoName": rname,
        "effectiveSaveDir": effective,
        "repoRoot": str(root) if root else None,
        "lineupActive": lineup_active,
        "liveBullpens": live_bullpens,
        "completedBullpens": completed_bullpens,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
