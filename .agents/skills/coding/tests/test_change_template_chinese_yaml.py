from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timezone
import importlib.util
from io import StringIO
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo


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

    def test_slug_cli_generates_beijing_second_precision_id(self) -> None:
        """`--slug` 应使用北京时间生成秒级 Change ID 并写入真实 carrier。"""
        fixed_now = datetime(2026, 9, 2, 14, 35, 27, tzinfo=ZoneInfo("Asia/Shanghai"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stdout = StringIO()
            with mock.patch.object(CODING, "_beijing_now", return_value=fixed_now):
                with redirect_stdout(stdout):
                    exit_code = CODING.main(
                        [
                            "new-change",
                            "--root",
                            str(root),
                            "--slug",
                            "analysis-scheme",
                            "--title",
                            "分析方案",
                            "--owner",
                            "test",
                            "--branch",
                            "test/analysis-scheme",
                            "--level",
                            "L2",
                        ]
                    )

            change_id = "CHG-20260902-143527-analysis-scheme"
            expected = root / ".agents/changes/active" / change_id / "CHANGE.md"
            self.assertEqual(exit_code, 0)
            self.assertEqual(stdout.getvalue().strip(), expected.relative_to(root).as_posix())
            self.assertEqual(CODING.read_change_metadata(expected)["id"], change_id)

    def test_current_schema_accepts_legacy_and_second_precision_dependencies(self) -> None:
        """同一 schema 应兼容旧日期 ID 与新秒级 ID 的依赖引用。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = CODING.create_change(
                root,
                change_id="CHG-20260902-143527-analysis-scheme",
                title="依赖兼容",
                owner="test",
                branch="test/dependency-compatibility",
                level="L2",
                depends_on=[
                    "CHG-20260901-legacy-parent",
                    "CHG-20260902-140000-current-parent",
                ],
            )
            self.assertEqual(
                CODING.read_change_metadata(path)["depends_on"],
                [
                    "CHG-20260901-legacy-parent",
                    "CHG-20260902-140000-current-parent",
                ],
            )

    def test_explicit_legacy_id_cli_remains_supported(self) -> None:
        """兼容入口 `--id` 应继续创建既有日期级 Change ID。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = CODING.main(
                    [
                        "new-change",
                        "--root",
                        str(root),
                        "--id",
                        "CHG-20260901-legacy-explicit",
                        "--title",
                        "显式兼容",
                        "--owner",
                        "test",
                        "--branch",
                        "test/legacy-explicit",
                        "--level",
                        "L2",
                    ]
                )

            expected = (
                root
                / ".agents/changes/active/CHG-20260901-legacy-explicit/CHANGE.md"
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(stdout.getvalue().strip(), expected.relative_to(root).as_posix())
            self.assertEqual(
                CODING.read_change_metadata(expected)["id"],
                "CHG-20260901-legacy-explicit",
            )

    def test_generated_change_id_converts_aware_time_to_beijing(self) -> None:
        """显式传入其他时区时也必须转换为北京时间，不能照抄宿主时钟。"""
        utc_now = datetime(2026, 9, 2, 6, 35, 27, tzinfo=timezone.utc)
        self.assertEqual(
            CODING.generate_change_id("analysis-scheme", now=utc_now),
            "CHG-20260902-143527-analysis-scheme",
        )

    def test_generated_change_id_rejects_non_kebab_slug(self) -> None:
        """自动生成入口必须拒绝会产生歧义目录名的非 kebab-case slug。"""
        fixed_now = datetime(2026, 9, 2, 14, 35, 27, tzinfo=ZoneInfo("Asia/Shanghai"))
        with self.assertRaisesRegex(ValueError, "slug"):
            CODING.generate_change_id("Analysis_Scheme", now=fixed_now)


if __name__ == "__main__":
    unittest.main()
