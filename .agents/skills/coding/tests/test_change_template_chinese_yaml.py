from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CODING_PATH = ROOT / ".agents/skills/coding/scripts/coding.py"
TEMPLATE_PATH = ROOT / ".agents/skills/coding/assets/CHANGE.template.md"


def _load_coding():
    """加载 Coding CLI 模块以验证 Change 模板生成结果。"""
    spec = importlib.util.spec_from_file_location("coding_change_template", CODING_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 coding.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODING = _load_coding()


class ChangeTemplateChineseYamlTest(unittest.TestCase):
    """验证 Change 模板中文表达、GitHub YAML 合法性和现有机器契约兼容性。"""

    def test_raw_frontmatter_has_no_standalone_template_keys(self) -> None:
        """原始模板 frontmatter 不能出现 GitHub YAML 无法解析的独立占位行。"""
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        standalone = [
            line
            for line in frontmatter.splitlines()
            if line.strip().startswith("$")
        ]
        self.assertEqual(standalone, [], f"frontmatter 存在非法独立占位行：{standalone}")
        for field in (
            "depends_on",
            "affected_areas",
            "affected_paths",
            "contracts",
            "data_changes",
        ):
            self.assertIn(f"{field}: ${field}", frontmatter)

    def test_human_readable_template_labels_are_chinese(self) -> None:
        """人类可读标题、表头和验证层名称使用中文，不保留旧英文自然语言标签。"""
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        for expected in (
            "# 需求追溯",
            "# 验证矩阵",
            "# 完成审计",
            "| 编号 | 要求 | 来源 | 状态 | 证据 |",
            "| 验证层 | 是否要求 | 范围 / 证据 |",
            "行为 / 单元 / 组件",
            "接口 / 契约",
            "集成 / 持久化 / 运行依赖",
            "用户 / 工作流验收",
            "跨组件关键路径",
            "外部依赖 / 供应方探测",
            "构建 / 打包 / 运行",
            "文档 / 治理 / 其他",
        ):
            self.assertIn(expected, text)
        for obsolete in (
            "# Requirement Traceability",
            "# Validation Matrix",
            "# Completion Audit",
            "| ID | Requirement | Source | Status | Evidence |",
            "| Layer | Required | Scope / Evidence |",
            "Unit / Component",
            "Workflow Acceptance",
            "Golden Path",
            "External Dependency / Provider Probe",
            "Build / Package / Runtime",
            "Docs / Governance / Other",
        ):
            self.assertNotIn(obsolete, text)

    def test_generated_change_keeps_current_machine_contract(self) -> None:
        """中文化与 YAML 修复后，new-change 仍生成当前 schema 所需字段与列表。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = CODING.create_change(
                root,
                change_id="CHG-20260830-template-yaml",
                title="模板验证",
                owner="test",
                branch="test/template-yaml",
                level="L2",
                affected_areas=["治理"],
                affected_paths=["README.md"],
                contracts=["coding-change/v1"],
                data_changes=[],
                depends_on=["CHG-20260829-parent"],
            )
            metadata = CODING.read_change_metadata(path)
            self.assertEqual(metadata["schema"], "coding-change/v1")
            self.assertEqual(metadata["status"], "proposed")
            self.assertEqual(metadata["completion_gate"], "required")
            self.assertEqual(metadata["depends_on"], ["CHG-20260829-parent"])
            self.assertEqual(metadata["affected_areas"], ["治理"])
            self.assertEqual(metadata["affected_paths"], ["README.md"])
            self.assertEqual(metadata["contracts"], ["coding-change/v1"])
            self.assertEqual(metadata["data_changes"], [])


if __name__ == "__main__":
    unittest.main()
