from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
READY_CHECK = ROOT / ".agents/skills/coding/scripts/ready_check.py"
TEMPLATE = ROOT / ".agents/skills/coding/assets/CHANGE.template.md"


def _change_document(
    *,
    schema: str = "coding-change/v1",
    status: str = "ready_for_review",
    requirement_status: str = "satisfied",
    source: str = "AGENTS.md",
    evidence: str = "tests: ready-check",
    audit_checked: bool = True,
    completion_gate: str = "required",
    chinese: bool = False,
) -> str:
    """生成用于 Ready Check 单元测试的最小 Coding Change。"""
    checked = "x" if audit_checked else " "
    traceability_heading = "# 需求追溯" if chinese else "# Requirement Traceability"
    completion_heading = "# 完成审计" if chinese else "# Completion Audit"
    table_header = (
        "| 编号 | 要求 | 来源 | 状态 | 证据 |"
        if chinese
        else "| ID | Requirement | Source | Status | Evidence |"
    )
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
completion_gate: {completion_gate}
depends_on: []
affected_areas: []
affected_paths: []
contracts: []
data_changes: []
---

{traceability_heading}

{table_header}
| --- | --- | --- | --- | --- |
| R1 | 必须满足上游要求 | {source} | {requirement_status} | {evidence} |

{completion_heading}

- [{checked}] upstream_re_read：已重新读取所有上游正式事实源并独立重建完成定义。
- [{checked}] change_coverage：已确认当前 Change 覆盖全部上游要求。
- [{checked}] reverse_audit：已执行适用反向审计并复核验证矩阵。
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

    @staticmethod
    def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        """在临时仓库中运行测试需要的 Git 命令。"""
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_template_enables_current_schema_and_completion_gate(self) -> None:
        """Change 模板必须只生成当前 schema、默认启用门禁并使用中文正文。"""
        content = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("schema: coding-change/v1", content)
        self.assertIn("completion_gate: required", content)
        self.assertIn("# 需求追溯", content)
        self.assertIn("# 验证矩阵", content)
        self.assertIn("# 完成审计", content)

    def test_complete_ready_change_passes(self) -> None:
        """历史英文格式的完整 ready Change 仍应通过当前门禁。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document())
            result = self._run(root, "--require-active-ready")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("carrier=.agents/changes", result.stdout)

    def test_chinese_ready_change_passes(self) -> None:
        """新模板使用的中文标题和表头必须通过同一 Ready Check。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(chinese=True))
            result = self._run(root, "--require-active-ready")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("carrier=.agents/changes", result.stdout)

    def test_rvc_schema_is_rejected_without_compatibility(self) -> None:
        """明确拒绝历史 rvc-change/v1，不保留兼容读取路径。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(schema="rvc-change/v1"))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("不支持的 Change schema", result.stdout + result.stderr)

    def test_missing_completion_gate_is_rejected(self) -> None:
        """当前 schema 不允许通过弱化或删除 Completion Gate 绕过 Ready。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(completion_gate="optional"))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("completion_gate 必须为 required", result.stdout + result.stderr)

    def test_not_satisfied_blocks_ready(self) -> None:
        """未满足 Requirement 不能进入 Ready。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(requirement_status="not_satisfied", chinese=True))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not_satisfied", result.stdout + result.stderr)

    def test_unchecked_completion_audit_blocks_ready(self) -> None:
        """完成审计未勾选时必须阻止 Ready。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(audit_checked=False, chinese=True))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("完成审计", result.stdout + result.stderr)

    def test_missing_requirement_source_blocks_ready(self) -> None:
        """仓库 Requirement Source 不存在时必须失败。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_change(root, _change_document(source="docs/missing.md", chinese=True))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("docs/missing.md", result.stdout + result.stderr)

    def test_current_change_cannot_source_itself(self) -> None:
        """当前 Change 不能把自身当作 Requirement Source。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = ".agents/changes/active/CHG-20260826-ready-check-fixture/CHANGE.md"
            self._write_change(root, _change_document(source=source, chinese=True))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("不能把自身作为 Requirement Source", result.stdout + result.stderr)

    def test_placeholder_evidence_blocks_ready(self) -> None:
        """Ready Requirement Evidence 不允许保留占位值。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(evidence="TBD", chinese=True))
            result = self._run(root, "--require-active-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TBD", result.stdout + result.stderr)

    def test_archive_requires_done(self) -> None:
        """归档 Change 必须处于 done。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(status="ready_for_review", chinese=True), archive=True)
            result = self._run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("done", result.stdout + result.stderr)

    def test_done_change_cannot_remain_active(self) -> None:
        """done Change 不能继续留在 active。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(status="done", chinese=True))
            result = self._run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("不得继续留在 active", result.stdout + result.stderr)

    def test_changed_since_requires_changed_active_change_ready(self) -> None:
        """changed-since 只对当前 diff 中变动的 Active Change 强制 Ready。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._git(root, "init", "-b", "main")
            self._git(root, "config", "user.name", "ready-check")
            self._git(root, "config", "user.email", "ready-check@example.invalid")
            (root / "README.md").write_text("baseline\n", encoding="utf-8")
            self._git(root, "add", "README.md")
            self._git(root, "commit", "-m", "建立测试基线")
            base = self._git(root, "rev-parse", "HEAD").stdout.strip()
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            self._write_change(root, _change_document(status="in_progress", chinese=True))
            self._git(root, "add", ".agents/changes", "AGENTS.md")
            self._git(root, "commit", "-m", "新增测试变更")
            result = self._run(root, "--changed-since", base)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ready_for_review", result.stdout + result.stderr)

    def test_existing_top_level_carrier_is_checked(self) -> None:
        """仓库已有顶层 changes carrier 时 Ready Check 必须沿用而不是只看 `.agents/changes`。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            path = root / "changes/active/CHG-20260826-ready-check-fixture/CHANGE.md"
            path.parent.mkdir(parents=True)
            path.write_text(_change_document(chinese=True), encoding="utf-8")
            result = self._run(root, "--require-active-ready")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("carrier=changes", result.stdout)


if __name__ == "__main__":
    unittest.main()
