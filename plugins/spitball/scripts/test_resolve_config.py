"""Tests for repo_name() in resolve-config.py.

Run: python3 plugins/spitball/scripts/test_resolve_config.py
"""

import importlib.util
import subprocess
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

    def test_legacy_autoCommit_maps_to_commitSpitball(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"autoCommit": False})
        self.assertFalse(cfg["commitSpitball"])
        self.assertTrue(cfg["commitAtBat"])  # at-bat default preserved

    def test_explicit_commitSpitball_wins_over_legacy(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"autoCommit": False, "commitSpitball": True})
        self.assertTrue(cfg["commitSpitball"])

    def test_commitAtBat_independent_of_legacy_autoCommit(self):
        cfg = self._base()
        rc.apply_layer(cfg, {"autoCommit": False, "commitAtBat": False})
        self.assertFalse(cfg["commitSpitball"])  # via legacy
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


if __name__ == "__main__":
    unittest.main()
