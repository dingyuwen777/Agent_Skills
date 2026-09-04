"""验证多人交付授权、仓库原生 Change 归档与稳定 Acceptance 绑定。"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
READY_CHECK_PATH = ROOT / ".agents/skills/coding/scripts/ready_check.py"
REF14 = ROOT / ".agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md"
REF15 = ROOT / ".agents/skills/coding/references/15_规则内容守恒与Skill维护.md"
REF23 = ROOT / ".agents/skills/coding/references/23_端到端交付与合并后收尾.md"
TEMPLATE = ROOT / ".agents/skills/coding/assets/CHANGE.template.md"


def _load_ready_check():
    """加载 canonical Ready validator，直接验证当前实现语义。"""
    spec = importlib.util.spec_from_file_location("delivery_ready_check", READY_CHECK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 Ready validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


READY_CHECK = _load_ready_check()


def _change_document(*, source: str, status: str = "ready_for_review") -> str:
    """生成最小 gated Change，用于稳定 Acceptance 绑定回归。"""
    return f"""---
schema: coding-change/v1
id: CHG-20260904-delivery-archive-fixture
title: Delivery Archive Fixture
level: L3
status: {status}
owner: test
branch: test/delivery-archive
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas: []
affected_paths: []
contracts: []
data_changes: []
---

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 必须对应上游稳定验收项 | {source} | satisfied | targeted test 已证明当前要求 |

# 完成审计

- [x] upstream_re_read：已重读上游来源。
- [x] change_coverage：已覆盖全部要求。
- [x] reverse_audit：已完成反向审计。
- [x] unresolved_cleared：未满足项已清零。
"""


class DeliveryArchiveGovernanceTest(unittest.TestCase):
    """覆盖本次多人交付与自动归档治理 Contract。"""

    def test_delivery_modes_and_effective_authorization_are_explicit(self) -> None:
        """提交 PR 与端到端交付必须是不同授权，文字请求不能升级真实权限。"""
        text = REF23.read_text(encoding="utf-8")
        self.assertIn("develop-and-submit", text)
        self.assertIn("PR Ready", text)
        self.assertIn("Requested Action", text)
        self.assertIn("Effective Authorization", text)
        self.assertIn("BLOCKED_BY_AUTHORIZATION", text)
        self.assertIn("authenticated principal", text)

        git_text = REF14.read_text(encoding="utf-8")
        self.assertIn("Requested Action", git_text)
        self.assertIn("Effective Authorization", git_text)
        self.assertIn("BLOCKED_BY_AUTHORIZATION", git_text)

    def test_repository_native_archive_is_not_agent_git_delivery(self) -> None:
        """Change 归档必须由目标仓库基础设施执行，Agent 只验证结果。"""
        text = REF23.read_text(encoding="utf-8")
        required = [
            "repository-native",
            "active → archive",
            "status → done",
            "不创建归档 PR",
            "不执行归档 commit",
            "blocked/incomplete",
            "不自行接管",
            "不等价于 Requirement",
        ]
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_skill_mutation_requires_rule_to_runtime_impact_audit(self) -> None:
        """规则变化必须反查模板、机器门禁、CI、测试与 Runtime/Source parity。"""
        text = REF15.read_text(encoding="utf-8")
        for fragment in (
            "Rule / Contract",
            "Template",
            "Parser / Validator",
            "CLI",
            "CI",
            "Tests",
            "Runtime / Source parity",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_change_template_teaches_stable_acceptance_binding(self) -> None:
        """新 Change 模板不能再示范只有 generic Requirement Source 的 R 行。"""
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("#123 / AC1", text)
        self.assertIn("稳定 Acceptance", text)

    def test_active_ready_change_requires_stable_acceptance_binding(self) -> None:
        """新的 Active Ready Change 只有泛化来源时必须被机器门禁拒绝。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            path = root / ".agents/changes/active/CHG-20260904-delivery-archive-fixture/CHANGE.md"
            path.parent.mkdir(parents=True)
            path.write_text(_change_document(source="AGENTS.md"), encoding="utf-8")
            result = READY_CHECK.check_repository(root, require_active_ready=True)
        self.assertFalse(result["ok"])
        self.assertIn("Acceptance", str(result["errors"]))

    def test_issue_acceptance_binding_is_accepted(self) -> None:
        """GitHub Issue 的 `#123 / AC1` 是可解析的稳定验收绑定。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / ".agents/changes/active/CHG-20260904-delivery-archive-fixture/CHANGE.md"
            path.parent.mkdir(parents=True)
            path.write_text(_change_document(source="#207 / AC1"), encoding="utf-8")
            result = READY_CHECK.check_repository(root, require_active_ready=True)
        self.assertTrue(result["ok"], result["errors"])

    def test_untouched_historical_archive_keeps_legacy_source_compatibility(self) -> None:
        """新 AC 绑定规则不能强制批量改写历史 untouched archive。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            path = root / ".agents/changes/archive/2026-08/CHG-20260904-delivery-archive-fixture/CHANGE.md"
            path.parent.mkdir(parents=True)
            path.write_text(_change_document(source="AGENTS.md", status="done"), encoding="utf-8")
            result = READY_CHECK.check_repository(root)
        self.assertTrue(result["ok"], result["errors"])


if __name__ == "__main__":
    unittest.main()
