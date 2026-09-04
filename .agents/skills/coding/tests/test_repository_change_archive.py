from __future__ import annotations

import runpy
import subprocess
from pathlib import Path
from typing import Any

import pytest

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


def test_archive_moves_exact_ready_change_and_preserves_body(tmp_path: Path) -> None:
    module = _module()
    change_id = "CHG-20260905-fixture"
    relative = f".agents/changes/active/{change_id}/CHANGE.md"
    original = _change(change_id)
    _write(tmp_path / relative, original)

    result = module["archive_change"](
        tmp_path,
        changed_paths=[relative, "README.md"],
        merged_at="2026-09-04T18:30:00Z",
        expected_source=original,
    )

    target = tmp_path / f".agents/changes/archive/2026-09/{change_id}/CHANGE.md"
    assert result.changed is True
    assert not (tmp_path / relative).exists()
    archived = target.read_text(encoding="utf-8")
    assert "status: done" in archived
    assert "updated: 2026-09-05" in archived
    assert archived.replace("status: done", "status: ready_for_review").replace(
        "updated: 2026-09-05", "updated: 2026-09-04"
    ) == original


def test_archive_is_idempotent_only_for_same_merged_revision_content(tmp_path: Path) -> None:
    module = _module()
    error = module["ArchiveError"]
    change_id = "CHG-20260905-fixture"
    relative = f".agents/changes/active/{change_id}/CHANGE.md"
    original = _change(change_id)
    target = tmp_path / f".agents/changes/archive/2026-09/{change_id}/CHANGE.md"
    _write(target, _change(change_id, status="done", updated="2026-09-05"))

    result = module["archive_change"](
        tmp_path,
        changed_paths=[relative],
        merged_at="2026-09-04T18:30:00Z",
        expected_source=original,
    )
    assert result.changed is False
    assert result.reason == "already_archived"

    _write(target, target.read_text(encoding="utf-8").replace("Archive safely", "other body"))
    with pytest.raises(error, match="does not belong"):
        module["archive_change"](
            tmp_path,
            changed_paths=[relative],
            merged_at="2026-09-04T18:30:00Z",
            expected_source=original,
        )


def test_archive_fails_closed_for_ambiguous_or_drifted_change(tmp_path: Path) -> None:
    module = _module()
    error = module["ArchiveError"]
    with pytest.raises(error, match="exactly one"):
        module["select_change"](
            [
                ".agents/changes/active/CHG-20260905-a/CHANGE.md",
                ".agents/changes/active/CHG-20260905-b/CHANGE.md",
            ]
        )

    change_id = "CHG-20260905-fixture"
    relative = f".agents/changes/active/{change_id}/CHANGE.md"
    original = _change(change_id)
    _write(tmp_path / relative, original.replace("Archive safely", "later main edit"))
    with pytest.raises(error, match="drifted"):
        module["archive_change"](
            tmp_path,
            changed_paths=[relative],
            merged_at="2026-09-04T18:30:00Z",
            expected_source=original,
        )


def test_merged_source_must_be_in_current_main_history(tmp_path: Path) -> None:
    module = _module()
    error = module["ArchiveError"]
    change_id = "CHG-20260905-fixture"
    relative = f".agents/changes/active/{change_id}/CHANGE.md"
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.name", "test")
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _write(tmp_path / relative, _change(change_id))
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "merged")
    revision = _git(tmp_path, "rev-parse", "HEAD")

    assert module["merged_source"](
        tmp_path, revision=revision, source_relative=relative
    ) == _change(change_id)

    _git(tmp_path, "checkout", "--orphan", "other")
    _git(tmp_path, "rm", "-rf", ".")
    _write(tmp_path / "other.txt", "other\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "other history")
    with pytest.raises(error, match="not in current main history"):
        module["merged_source"](tmp_path, revision=revision, source_relative=relative)


def test_workflow_uses_narrow_app_identity_and_serial_archive() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "types: [closed]",
        "workflow_dispatch:",
        "group: change-archive-main",
        "cancel-in-progress: false",
        "environment: change-archive-main",
        "configured=false",
        "actions/create-github-app-token@v2",
        "CHANGE_ARCHIVE_APP_ID",
        "CHANGE_ARCHIVE_APP_PRIVATE_KEY",
        "merge_commit_sha",
        "--merged-revision",
        ".github/scripts/archive_change_after_merge.py",
        ".agents/skills/coding/scripts/ready_check.py --root .",
        "git push origin HEAD:main",
    ]
    for fragment in required:
        assert fragment in workflow
    assert "contents: write" not in workflow
    assert "\n  push:" not in workflow
