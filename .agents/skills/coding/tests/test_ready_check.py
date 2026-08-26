from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
READY_CHECK = ROOT / ".agents/skills/coding/scripts/ready_check.py"


def _change_document(
    *,
    schema: str = "coding-change/v1",
    status: str = "ready_for_review",
    requirement_status: str = "satisfied",
    source: str = "AGENTS.md",
    evidence: str = "tests: ready-check",
    audit_checked: bool = True,
) -> str:
    """生成用于 Ready Check 单元测试的最小 Coding Change。"""
    checked = "x" if audit_checked else " "
    return f"""---
schema: {schema}
id: CHG-20260826-ready-check-fixture
title: Ready Check Fixture
level: L2
status: {status}
owner: test
branch: test/ready-check
created: 2026-08-26
updated: 2026-08-26
completion_gate: required
depends_on: []
affected_areas: []
affected_paths: []
contracts: []
data_changes: []
---

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 必须满足上游要求 | {source} | {requirement_status} | {evidence} |

# Completion Audit

- [{checked}] upstream_re_read：已重新读取所有上游正式事实源并独立重建完成定义。
- [{checked}] change_coverage：已确认当前 Change 覆盖全部上游要求。
- [{checked}] reverse_audit：已执行适用反向审计并复核 Validation Matrix。
- [{checked}] unresolved_cleared：所有 not_satisfied 已清零并有依据。
"""


class ReadyCheckTest(unittest.TestCase):
    """验证当前 coding-change/v1 的 Ready/Archive 机器门禁。"""

    def _run(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        """运行 Ready Check 并捕获完整输出。"""
        return subprocess.run(
            [sys.executable, str(READY_CHECK), "--root", str(root), *extra],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    @staticmethod
    def _write_change(root: Path, document: str, *, archive: bool = False) -> Path:
        """把测试 Change 写入默认 `.agents/changes` carrier。"""
        if archive:
            path = root / ".agents/changes/archive/2026-08/CHG-20260826-ready-check-fixture/CHANGE.md"
        else:
            path = root / ".agents/changes/active/CHG-20260826-ready-check-fixture/CHANGE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document, encoding="utf-8")
        return path

    def test_complete_ready_change_passes(self) -> None:
        """完整 ready Change 应通过当前门禁。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document())
            result = self._run(root, "--require-active-ready")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_old_schema_is_rejected_without_compatibility(self) -> None:
        """任意非当前 schema 必须直接失败，不再兼容。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(schema="legacy-change/v0"))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("不支持的 Change schema", result.stdout + result.stderr)

    def test_not_satisfied_blocks_ready(self) -> None:
        """未满足 Requirement 不能进入 Ready。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(requirement_status="not_satisfied"))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not_satisfied", result.stdout + result.stderr)

    def test_unchecked_completion_audit_blocks_ready(self) -> None:
        """Completion Audit 未勾选时必须阻止 Ready。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(audit_checked=False))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Completion Audit", result.stdout + result.stderr)

    def test_missing_requirement_source_blocks_ready(self) -> None:
        """仓库 Requirement Source 不存在时必须失败。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_change(root, _change_document(source="docs/missing.md"))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("docs/missing.md", result.stdout + result.stderr)

    def test_archive_requires_done(self) -> None:
        """归档 Change 必须处于 done。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(status="ready_for_review"), archive=True)
            result = self._run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("done", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
