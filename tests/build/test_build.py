from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class BuildTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        shutil.copytree(
            REPOSITORY_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git", ".work", "build", "dist", "__pycache__", "*.pyc"
            ),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_build(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", "scripts/build.py", *arguments],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_build_is_deterministic_and_archive_is_runtime_only(self) -> None:
        first = self.root / "out-one"
        second = self.root / "out-two"
        self.assertEqual(self.run_build("--output", str(first)).returncode, 0)
        self.assertEqual(self.run_build("--output", str(second)).returncode, 0)
        first_archive = next(first.glob("*.zip"))
        second_archive = next(second.glob("*.zip"))
        self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())
        checksum = next(first.glob("*.sha256")).read_text(encoding="ascii").split()[0]
        self.assertEqual(
            checksum, hashlib.sha256(first_archive.read_bytes()).hexdigest()
        )
        with zipfile.ZipFile(first_archive) as archive:
            names = set(archive.namelist())
            packaged_readme = archive.read("README.md").decode("utf-8")
        self.assertIn("skills/jedikit-tasks/SKILL.md", names)
        self.assertIn("skills/jedikit-habits/SKILL.md", names)
        self.assertIn("plugin.json", names)
        self.assertIn(".codex-plugin/plugin.json", names)
        self.assertIn(".claude-plugin/plugin.json", names)
        self.assertFalse(
            any(name.startswith(("research/", "evals/", ".work/")) for name in names)
        )
        self.assertIn("Installation and development documentation:", packaged_readme)
        self.assertNotIn("evals/run.py", packaged_readme)

    def test_check_detects_generated_skill_drift(self) -> None:
        target = self.root / "packages/jedikit/skills/jedikit-tasks/SKILL.md"
        target.write_text(
            target.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8"
        )
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated file is stale", result.stderr)

    def test_check_detects_manifest_metadata_mismatch(self) -> None:
        metadata = self.root / "package-metadata.json"
        value = json.loads(metadata.read_text(encoding="utf-8"))
        value["package"]["description"] = "changed source metadata"
        metadata.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".codex-plugin/plugin.json", result.stderr)

    def test_future_semver_is_generated_from_one_source(self) -> None:
        metadata = self.root / "package-metadata.json"
        value = json.loads(metadata.read_text(encoding="utf-8"))
        value["package"]["version"] = "0.1.0-alpha.3"
        metadata.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        output = self.root / "candidate"
        result = self.run_build("--output", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((output / "jedikit-v0.1.0-alpha.3-candidate.zip").is_file())
        manifest = json.loads(
            (self.root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["version"], "0.1.0-alpha.3")

    def test_platform_metadata_cannot_override_common_fields(self) -> None:
        metadata = self.root / "package-metadata.json"
        value = json.loads(metadata.read_text(encoding="utf-8"))
        value["platforms"]["codex"]["version"] = "9.9.9"
        metadata.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("overrides common fields", result.stderr)

    def test_hermes_package_rejects_mcp_and_other_root_files(self) -> None:
        (self.root / "packages/jedikit/mcp.json").write_text("{}\n", encoding="utf-8")
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected Hermes package root entry", result.stderr)

    def test_unknown_canonical_skill_entry_is_rejected(self) -> None:
        (self.root / "skills/shared").mkdir()
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical skills root is invalid", result.stderr)

    def test_generated_parent_symlink_is_rejected_before_write(self) -> None:
        generated = self.root / "packages/jedikit/skills"
        shutil.rmtree(generated)
        external = Path(self.temporary.name) / "external"
        external.mkdir()
        sentinel = external / "sentinel"
        sentinel.write_text("unchanged", encoding="utf-8")
        os.symlink(external, generated)
        result = self.run_build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated parent must not be a symlink", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")

    def test_top_level_archive_input_symlink_is_rejected(self) -> None:
        mcp = self.root / ".mcp.json"
        mcp.unlink()
        external = Path(self.temporary.name) / "external-mcp.json"
        external.write_text('{"sentinel": true}\n', encoding="utf-8")
        os.symlink(external, mcp)
        result = self.run_build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("archive input must not be a symlink: .mcp.json", result.stderr)

    def test_source_skill_symlink_is_rejected(self) -> None:
        source = self.root / "skills/jedikit-habits"
        moved = self.root / "jedikit-habits-source"
        source.rename(moved)
        os.symlink(moved, source)
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical skill path must be a real directory", result.stderr)

    def test_missing_skill_file_fails_closed(self) -> None:
        (self.root / "skills/jedikit-habits/SKILL.md").unlink()
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing skill entrypoint", result.stderr)

    def test_missing_link_target_fails_closed(self) -> None:
        (self.root / "skills/jedikit-tasks/references/core-method.md").unlink()
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken local link", result.stderr)

    def test_local_link_cannot_escape_skill(self) -> None:
        skill = self.root / "skills/jedikit-tasks/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8")
            + "\n[escape](../jedikit-habits/SKILL.md)\n",
            encoding="utf-8",
        )
        result = self.run_build("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local link escapes its skill", result.stderr)


if __name__ == "__main__":
    unittest.main()
