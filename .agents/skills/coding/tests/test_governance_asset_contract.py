"""验证治理资产机器 Contract 对不同宿主写入结果给出一致判定。"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CODING_PATH = ROOT / ".agents/skills/coding/scripts/coding.py"
CONTRACT_PATH = ROOT / ".agents/skills/coding/scripts/governance_contract.py"
TEMPLATE_PATH = ROOT / ".agents/skills/coding/assets/CHANGE.template.md"


def _load_module(path: Path, name: str):
    """从指定路径加载 stdlib-only 工具模块。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODING = _load_module(CODING_PATH, "governance_contract_coding")
CONTRACT = _load_module(CONTRACT_PATH, "governance_contract_subject")


REQUIREMENT_BODY = """## 问题背景
当前需要统一治理资产。

## 目标
不同宿主使用同一机器 Contract。

## 用户 / 使用场景
开发者通过网页端或本地 Agent 交付代码。

## 范围
治理资产创建与校验。

## 非目标
不修改历史记录。

## 验收标准
- [ ] AC1：新实例遵守当前 Contract
- [ ] AC2：历史记录保持不变

## 必须保持不变
历史归档不可变。

## 上游事实源 / 相关资料
用户要求与 canonical 规则。

## 风险与依赖
无额外外部依赖。

## 验证要求
正反例自动测试。
"""

BUG_BODY = """## 实际行为
不同宿主可产生不同治理资产。

## 期望行为
相同输入得到相同机器 Contract 判定。

## 影响范围
治理与交付链。

## 环境 / 版本
当前 main。

## 复现步骤
1. 通过不同写入路径创建 Issue。

## 证据
现有实例差异。

## 回归范围
Issue/Change validator。

## 验收标准
- [ ] AC1：不合规实例稳定失败

## 验证要求
运行 targeted regression。

## 上游事实源 / 相关资料
canonical Requirement Source 规则。
"""

TECHNICAL_BODY = """## 动机 / 根因
规则读取统一但机器产物仍可漂移。

## 当前状态
validator 只覆盖部分结构。

## 目标状态
建立宿主无关机器 Contract。

## 范围
Change 与 Requirement Source。

## 非目标
不修改历史记录。

## 兼容与迁移
历史只读兼容，无数据迁移。

## 风险与回滚
误判时 revert 当前 PR。

## 验收标准
- [ ] AC1：新 Change 使用秒级 ID
- [ ] AC2：Issue 使用稳定 Acceptance task list

## 验证要求
运行正反例与分发回归。

## 上游事实源 / 相关资料
canonical Coding 规则。
"""


class GovernanceAssetContractTests(unittest.TestCase):
    """覆盖 Change 新实例与 GitHub Requirement Source 的稳定机器语义。"""

    def test_current_change_id_and_legacy_identity_are_distinct(self) -> None:
        """历史可读 ID 与当前新建 ID 必须由不同机器判据表达。"""
        self.assertTrue(CONTRACT.is_current_change_id("CHG-20260917-145659-machine-contract"))
        self.assertFalse(CONTRACT.is_current_change_id("CHG-20260917-machine-contract"))
        self.assertTrue(CONTRACT.is_legacy_change_id("CHG-20260917-machine-contract"))
        self.assertFalse(CONTRACT.is_legacy_change_id("CHG-20260917-145659-machine-contract"))

    def test_generated_current_l3_change_passes_new_instance_contract(self) -> None:
        """canonical 模板生成的秒级 L3 Change 应通过当前实例校验。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = CODING.create_change(
                root,
                change_id="CHG-20260917-145659-machine-contract",
                title="机器 Contract",
                owner="test",
                branch="test/machine-contract",
                level="L3",
            )
            errors = CONTRACT.validate_new_change_file(path, template_path=TEMPLATE_PATH)
        self.assertEqual(errors, [])

    def test_new_legacy_id_change_is_rejected_without_breaking_legacy_parser(self) -> None:
        """低层 parser 可继续读取历史 ID，但新实例 Contract 必须拒绝新的日期级 Change。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = CODING.create_change(
                root,
                change_id="CHG-20260917-legacy-new-change",
                title="历史格式新实例",
                owner="test",
                branch="test/legacy-new-change",
                level="L2",
            )
            self.assertEqual(
                CODING.read_change_metadata(path)["id"],
                "CHG-20260917-legacy-new-change",
            )
            errors = CONTRACT.validate_new_change_file(path, template_path=TEMPLATE_PATH)
        self.assertTrue(any("HHMMSS" in error for error in errors), errors)

    def test_new_change_missing_template_heading_is_rejected(self) -> None:
        """直接 API/文件写入不能通过省略 canonical 模板结构绕过治理。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = CODING.create_change(
                root,
                change_id="CHG-20260917-145700-missing-heading",
                title="缺少结构",
                owner="test",
                branch="test/missing-heading",
                level="L2",
            )
            text = path.read_text(encoding="utf-8").replace("# 验证矩阵", "# 被错误改名的验证矩阵")
            path.write_text(text, encoding="utf-8")
            errors = CONTRACT.validate_new_change_file(path, template_path=TEMPLATE_PATH)
        self.assertTrue(any("验证矩阵" in error for error in errors), errors)

    def test_l3_change_requires_tradeoff_section(self) -> None:
        """L3 新实例必须保留方案取舍入口，不能通过精简正文降低治理强度。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = CODING.create_change(
                root,
                change_id="CHG-20260917-145701-l3-tradeoff",
                title="L3 取舍",
                owner="test",
                branch="test/l3-tradeoff",
                level="L3",
            )
            text = path.read_text(encoding="utf-8").replace("## 备选方案与取舍", "## 已删除取舍入口")
            path.write_text(text, encoding="utf-8")
            errors = CONTRACT.validate_new_change_file(path, template_path=TEMPLATE_PATH)
        self.assertTrue(any("备选方案与取舍" in error for error in errors), errors)

    def test_three_default_issue_profiles_pass(self) -> None:
        """需求、缺陷、技术变更三类默认 Requirement Source 应共享稳定 Acceptance Contract。"""
        fixtures = (
            ("[需求] 统一机器 Contract", REQUIREMENT_BODY),
            ("[缺陷] 修复治理资产漂移", BUG_BODY),
            ("[技术变更] 收紧治理门禁", TECHNICAL_BODY),
        )
        for title, body in fixtures:
            with self.subTest(title=title):
                self.assertEqual(CONTRACT.validate_issue_instance(title, body), [])

    def test_issue_without_type_prefix_is_rejected(self) -> None:
        """API 直接创建 Issue 也不能绕过标准类型身份。"""
        errors = CONTRACT.validate_issue_instance("统一机器 Contract", TECHNICAL_BODY)
        self.assertTrue(any("标题" in error for error in errors), errors)

    def test_issue_missing_required_semantic_section_is_rejected(self) -> None:
        """只有 AC 的精简 Issue 不能冒充完整 Requirement Source。"""
        body = TECHNICAL_BODY.replace("## 非目标\n不修改历史记录。\n\n", "")
        errors = CONTRACT.validate_issue_instance("[技术变更] 收紧治理门禁", body)
        self.assertTrue(any("非目标" in error for error in errors), errors)

    def test_acceptance_must_be_contiguous_task_list(self) -> None:
        """Acceptance 必须由可回写且连续的 AC task list 承担最终状态。"""
        body = TECHNICAL_BODY.replace("AC2：Issue", "AC3：Issue")
        errors = CONTRACT.validate_issue_instance("[技术变更] 收紧治理门禁", body)
        self.assertTrue(any("连续" in error for error in errors), errors)

    def test_closure_requires_all_acceptance_items_checked(self) -> None:
        """Closure machine validation 不能用 comment-only Evidence 代替 body task list 状态。"""
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] 收紧治理门禁",
            TECHNICAL_BODY,
            require_all_checked=True,
        )
        self.assertTrue(any("尚未勾选" in error for error in errors), errors)
        completed = TECHNICAL_BODY.replace("- [ ] AC", "- [x] AC")
        self.assertEqual(
            CONTRACT.validate_issue_instance(
                "[技术变更] 收紧治理门禁",
                completed,
                require_all_checked=True,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
