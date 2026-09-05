from __future__ import annotations

import re
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
ARCHIVER = ROOT / ".github" / "scripts" / "archive_change_after_merge.py"
WORKFLOW = ROOT / ".github" / "workflows" / "change-archive.yml"


def _module() -> dict[str, Any]:
    return runpy.run_path(str(ARCHIVER))


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _change(
    change_id: str, *, status: str = "ready_for_review", updated: str = "2026-09-04"
) -> str:
    return f"""---
schema: coding-change/v1
id: {change_id}
title: Archive fixture
level: L2
status: {status}
owner: test
branch: test/archive
created: 2026-09-04
updated: {updated}
completion_gate: required
depends_on: []
affected_areas:
  - governance
affected_paths:
  - requirement.md
contracts: []
data_changes: []
---

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Archive safely | requirement.md#AC1 | satisfied | evidence |

# Completion Audit

- [x] upstream_re_read: done
- [x] change_coverage: done
- [x] reverse_audit: done
- [x] unresolved_cleared: done
"""


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


class RepositoryChangeArchiveAutomationTest(unittest.TestCase):
    """锁定 Agent_Skills 仓库自身 Change 自动归档的确定性边界。"""

    def test_archive_cli_help_is_self_contained(self) -> None:
        """新增维护脚本必须在统一 Skill CI 已安装的最小依赖面内可独立启动。"""
        result = subprocess.run(
            [sys.executable, str(ARCHIVER), "--help"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--merged-revision", result.stdout)
        self.assertIn("--changed-paths-file", result.stdout)

    def test_archive_moves_exact_ready_change_and_preserves_body(self) -> None:
        module = _module()
        change_id = "CHG-20260905-fixture"
        relative = f".agents/changes/active/{change_id}/CHANGE.md"
        original = _change(change_id)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write(root / relative, original)

            result = module["archive_change"](
                root,
                changed_paths=[relative, "README.md"],
                merged_at="2026-09-04T18:30:00Z",
                expected_source=original,
            )

            target = root / f".agents/changes/archive/2026-09/{change_id}/CHANGE.md"
            self.assertTrue(result.changed)
            self.assertFalse((root / relative).exists())
            archived = target.read_text(encoding="utf-8")
            self.assertIn("status: done", archived)
            self.assertIn("updated: 2026-09-05", archived)
            self.assertEqual(
                archived.replace("status: done", "status: ready_for_review").replace(
                    "updated: 2026-09-05", "updated: 2026-09-04"
                ),
                original,
            )

    def test_archive_is_idempotent_only_for_same_merged_revision_content(self) -> None:
        module = _module()
        error = module["ArchiveError"]
        change_id = "CHG-20260905-fixture"
        relative = f".agents/changes/active/{change_id}/CHANGE.md"
        original = _change(change_id)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / f".agents/changes/archive/2026-09/{change_id}/CHANGE.md"
            _write(target, _change(change_id, status="done", updated="2026-09-05"))

            result = module["archive_change"](
                root,
                changed_paths=[relative],
                merged_at="2026-09-04T18:30:00Z",
                expected_source=original,
            )
            self.assertFalse(result.changed)
            self.assertEqual(result.reason, "already_archived")

            _write(
                target,
                target.read_text(encoding="utf-8").replace("Archive safely", "other body"),
            )
            with self.assertRaisesRegex(error, "does not belong"):
                module["archive_change"](
                    root,
                    changed_paths=[relative],
                    merged_at="2026-09-04T18:30:00Z",
                    expected_source=original,
                )

    def test_archive_fails_closed_for_ambiguous_or_drifted_change(self) -> None:
        module = _module()
        error = module["ArchiveError"]
        with self.assertRaisesRegex(error, "exactly one"):
            module["select_change"](
                [
                    ".agents/changes/active/CHG-20260905-a/CHANGE.md",
                    ".agents/changes/active/CHG-20260905-b/CHANGE.md",
                ]
            )

        change_id = "CHG-20260905-fixture"
        relative = f".agents/changes/active/{change_id}/CHANGE.md"
        original = _change(change_id)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write(root / relative, original.replace("Archive safely", "later main edit"))
            with self.assertRaisesRegex(error, "drifted"):
                module["archive_change"](
                    root,
                    changed_paths=[relative],
                    merged_at="2026-09-04T18:30:00Z",
                    expected_source=original,
                )

    def test_merged_source_must_be_in_current_main_history(self) -> None:
        module = _module()
        error = module["ArchiveError"]
        change_id = "CHG-20260905-fixture"
        relative = f".agents/changes/active/{change_id}/CHANGE.md"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _git(root, "init", "-b", "main")
            _git(root, "config", "user.name", "test")
            _git(root, "config", "user.email", "test@example.invalid")
            _write(root / relative, _change(change_id))
            _git(root, "add", ".")
            _git(root, "commit", "-m", "merged")
            revision = _git(root, "rev-parse", "HEAD")

            self.assertEqual(
                module["merged_source"](
                    root,
                    revision=revision,
                    source_relative=relative,
                ),
                _change(change_id),
            )

            _git(root, "checkout", "--orphan", "other")
            _git(root, "rm", "-rf", ".")
            _write(root / "other.txt", "other\n")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "other history")
            with self.assertRaisesRegex(error, "not in current main history"):
                module["merged_source"](
                    root,
                    revision=revision,
                    source_relative=relative,
                )

    def test_workflow_uses_narrow_app_identity_serial_archive_and_path_filter(self) -> None:
        """自动触发只服务携带 Active Change 的 PR；手工 dispatch 仍可重跑历史 merged PR。"""
        workflow = WORKFLOW.read_text(encoding="utf-8")
        required = [
            "types: [closed]",
            'paths: [".agents/changes/active/**"]',
            "workflow_dispatch:",
            "group: change-archive-main",
            "cancel-in-progress: false",
            "environment: change-archive-main",
            "configured=false",
            "actions/create-github-app-token@",
            "CHANGE_ARCHIVE_APP_ID",
            "CHANGE_ARCHIVE_APP_PRIVATE_KEY",
            "merge_commit_sha",
            "--merged-revision",
            ".github/scripts/archive_change_after_merge.py",
            ".agents/skills/coding/scripts/ready_check.py --root .",
            "git push origin HEAD:main",
        ]
        for fragment in required:
            self.assertIn(fragment, workflow)
        for line in workflow.splitlines():
            stripped = line.strip()
            if stripped.startswith("uses:"):
                ref = stripped.split("uses:", 1)[1].strip().split()[0]
                self.assertRegex(ref, r"@[0-9a-f]{40}$", f"未固定 Action commit：{ref}")
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("\n  push:", workflow)


if __name__ == "__main__":
    unittest.main()
