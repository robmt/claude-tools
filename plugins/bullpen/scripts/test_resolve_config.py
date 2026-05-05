"""Tests for resolve-config.py.

Run: python3 plugins/bullpen/scripts/test_resolve_config.py
"""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "rc", Path(__file__).parent / "resolve-config.py"
)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)


class RepoNameTests(unittest.TestCase):
    def _name_for(self, url, root_basename="fallback"):
        with patch.object(rc.subprocess, "check_output", return_value=url + "\n"):
            return rc.repo_name(Path(f"/tmp/{root_basename}"))

    def test_github_ssh(self):
        self.assertEqual(self._name_for("git@github.com:org/repo.git"), "org-repo")

    def test_github_ssh_no_git_suffix(self):
        self.assertEqual(self._name_for("git@github.com:org/repo"), "org-repo")

    def test_github_https(self):
        self.assertEqual(self._name_for("https://github.com/org/repo.git"), "org-repo")

    def test_github_https_no_git_suffix(self):
        self.assertEqual(self._name_for("https://github.com/org/repo"), "org-repo")

    def test_github_https_trailing_slash(self):
        self.assertEqual(self._name_for("https://github.com/org/repo/"), "org-repo")

    def test_azure_devops_https_strips_git_routing_segment(self):
        # Regression: previously returned "_git-myrepo" because the old regex
        # greedily matched the last two path segments without filtering routing
        # markers. Real-world URL: dev.azure.com/{org}/{project}/_git/{repo}.
        self.assertEqual(
            self._name_for("https://dev.azure.com/myorg/myproject/_git/myrepo"),
            "myproject-myrepo",
        )

    def test_azure_devops_ssh(self):
        self.assertEqual(
            self._name_for("git@ssh.dev.azure.com:v3/myorg/myproject/myrepo"),
            "myproject-myrepo",
        )

    def test_azure_devops_project_equals_repo_collapses_duplicate(self):
        # Regression: dev.azure.com/{org}/{project}/_git/{repo} where
        # project == repo (a common Azure DevOps pattern) previously
        # produced "its-monorepo-its-monorepo".
        self.assertEqual(
            self._name_for(
                "https://dev.azure.com/HighQA-ITS/its-monorepo/_git/its-monorepo"
            ),
            "its-monorepo",
        )

    def test_azure_devops_ssh_project_equals_repo_collapses_duplicate(self):
        self.assertEqual(
            self._name_for(
                "git@ssh.dev.azure.com:v3/HighQA-ITS/its-monorepo/its-monorepo"
            ),
            "its-monorepo",
        )

    def test_self_hosted_tfs_https(self):
        self.assertEqual(
            self._name_for(
                "https://tfs.example.com/tfs/Collection/Project/_git/MyRepo"
            ),
            "Project-MyRepo",
        )

    def test_bitbucket_server_strips_scm_routing_segment(self):
        self.assertEqual(
            self._name_for("https://bitbucket.example.com/scm/proj/repo.git"),
            "proj-repo",
        )

    def test_no_origin_falls_back_to_root_basename(self):
        with patch.object(
            rc.subprocess,
            "check_output",
            side_effect=subprocess.CalledProcessError(1, "git"),
        ):
            self.assertEqual(rc.repo_name(Path("/tmp/myrepo")), "myrepo")

    def test_empty_origin_falls_back_to_root_basename(self):
        with patch.object(rc.subprocess, "check_output", return_value="\n"):
            self.assertEqual(rc.repo_name(Path("/tmp/myrepo")), "myrepo")


class ApplyLayerTests(unittest.TestCase):
    def _base(self):
        return dict(rc.DEFAULTS)

    def test_none_layer_is_noop(self):
        cfg = self._base()
        rc.apply_layer(cfg, None)
        self.assertEqual(cfg, self._base())

    def test_legacy_autoCommit_maps_to_commitBullpen(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"autoCommit": False})
        self.assertFalse(cfg["commitBullpen"])
        self.assertTrue(cfg["commitAtBat"])  # at-bat default preserved

    def test_legacy_commitSpitball_maps_to_commitBullpen(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"commitSpitball": False})
        self.assertFalse(cfg["commitBullpen"])
        self.assertTrue(cfg["commitAtBat"])

    def test_explicit_commitBullpen_wins_over_legacy_keys(self):
        cfg = self._base()
        rc.apply_layer(
            cfg,
            {"autoCommit": False, "commitSpitball": False, "commitBullpen": True},
        )
        self.assertTrue(cfg["commitBullpen"])

    def test_commitSpitball_wins_over_autoCommit(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"autoCommit": False, "commitSpitball": True})
        self.assertTrue(cfg["commitBullpen"])

    def test_commitAtBat_independent_of_legacy_autoCommit(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"autoCommit": False, "commitAtBat": False})
        self.assertFalse(cfg["commitBullpen"])  # via legacy
        self.assertFalse(cfg["commitAtBat"])  # explicit

    def test_unknown_keys_ignored(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"someBogusKey": "value"})
        self.assertEqual(cfg, self._base())

    def test_repo_layer_overrides_home_layer(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"commitAtBat": False})
        rc.apply_layer(cfg, {"commitAtBat": True})
        self.assertTrue(cfg["commitAtBat"])


class LoadConfigLayerTests(unittest.TestCase):
    """Filename-precedence tests for load_config_layer()."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_neither_file_returns_none(self):
        self.assertIsNone(rc.load_config_layer(self.base))

    def test_bullpen_json_wins(self):
        (self.base / ".bullpen.json").write_text('{"saveDir": "from-bullpen"}')
        (self.base / ".spitball.json").write_text('{"saveDir": "from-legacy"}')
        layer = rc.load_config_layer(self.base)
        self.assertEqual(layer["saveDir"], "from-bullpen")

    def test_legacy_spitball_json_used_when_bullpen_absent(self):
        (self.base / ".spitball.json").write_text('{"saveDir": "from-legacy"}')
        layer = rc.load_config_layer(self.base)
        self.assertEqual(layer["saveDir"], "from-legacy")

    def test_only_bullpen_json(self):
        (self.base / ".bullpen.json").write_text('{"saveDir": "from-bullpen"}')
        layer = rc.load_config_layer(self.base)
        self.assertEqual(layer["saveDir"], "from-bullpen")


class ScanBullpensTests(unittest.TestCase):
    """Filesystem layout tests for scan_bullpens()."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _make_bullpen(self, path, lineup_status=None, doc_name="bullpen.md"):
        path.mkdir(parents=True)
        (path / doc_name).write_text("# bullpen\n")
        if lineup_status is not None:
            head = "Status: Complete\n\n" if lineup_status == "complete" else ""
            (path / "lineup.md").write_text(head + "# Lineup\n")

    def test_missing_dir_returns_empty(self):
        live, done, active = rc.scan_bullpens(str(self.root / "nope"))
        self.assertEqual(live, [])
        self.assertEqual(done, [])
        self.assertFalse(active)

    def test_live_folder_with_lineup_marks_active(self):
        self._make_bullpen(self.root / "2026-05-01-foo", lineup_status="active")
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual([e["name"] for e in live], ["2026-05-01-foo"])
        self.assertEqual(done, [])
        self.assertTrue(active)

    def test_live_folder_without_lineup_not_active(self):
        # Bullpen written, lineup not yet bootstrapped.
        self._make_bullpen(self.root / "2026-05-01-foo", lineup_status=None)
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual([e["name"] for e in live], ["2026-05-01-foo"])
        self.assertEqual(done, [])
        self.assertFalse(active)

    def test_legacy_spitball_md_still_recognized(self):
        # Folders written by the previous-name version of this skill use
        # spitball.md; the scan must keep finding them.
        self._make_bullpen(
            self.root / "2026-04-01-old", lineup_status="active", doc_name="spitball.md"
        )
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual([e["name"] for e in live], ["2026-04-01-old"])
        self.assertTrue(active)

    def test_archive_bucket_lists_completed(self):
        self._make_bullpen(
            self.root / "completed" / "2026-04-01-old", lineup_status="complete"
        )
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual(live, [])
        self.assertEqual([e["name"] for e in done], ["2026-04-01-old"])
        self.assertFalse(active)

    def test_archive_bucket_with_legacy_spitball_md(self):
        self._make_bullpen(
            self.root / "completed" / "2026-03-01-legacy",
            lineup_status="complete",
            doc_name="spitball.md",
        )
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual(live, [])
        self.assertEqual([e["name"] for e in done], ["2026-03-01-legacy"])

    def test_legacy_top_level_complete_classified_as_done(self):
        # Pre-archival layout: complete bullpen still at top level.
        self._make_bullpen(
            self.root / "2026-03-01-legacy", lineup_status="complete"
        )
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual(live, [])
        self.assertEqual([e["name"] for e in done], ["2026-03-01-legacy"])
        self.assertFalse(active)

    def test_mixed_layout(self):
        self._make_bullpen(self.root / "2026-05-01-live", lineup_status="active")
        self._make_bullpen(
            self.root / "2026-04-15-legacy", lineup_status="complete"
        )
        self._make_bullpen(
            self.root / "completed" / "2026-04-01-archived",
            lineup_status="complete",
        )
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual([e["name"] for e in live], ["2026-05-01-live"])
        self.assertEqual(
            sorted(e["name"] for e in done),
            ["2026-04-01-archived", "2026-04-15-legacy"],
        )
        self.assertTrue(active)

    def test_completed_named_folder_with_no_doc_treated_as_archive(self):
        # Edge case: bucket detection wins when "completed" has no
        # bullpen doc of its own. Real bullpens should never be named
        # "completed".
        (self.root / "completed").mkdir()
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual(live, [])
        self.assertEqual(done, [])
        self.assertFalse(active)

    def test_completed_folder_with_its_own_doc_is_treated_as_bullpen(self):
        # If someone literally names a bullpen "completed" (with
        # bullpen.md directly inside), respect that and don't recurse.
        self._make_bullpen(self.root / "completed", lineup_status="active")
        live, done, active = rc.scan_bullpens(str(self.root))
        self.assertEqual([e["name"] for e in live], ["completed"])
        self.assertEqual(done, [])
        self.assertTrue(active)


if __name__ == "__main__":
    unittest.main()
