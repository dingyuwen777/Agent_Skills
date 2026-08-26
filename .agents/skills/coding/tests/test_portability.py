from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CODING_PATH = ROOT / ".agents/skills/coding/scripts/coding.py"


def _load_coding():
    """加载 Coding CLI 模块以直接测试项目发现和 Change carrier。"""
    spec = importlib.util.spec_from_file_location("coding_portability", CODING_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 coding.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODING = _load_coding()


class PortabilityTest(unittest.TestCase):
    """验证项目发现和 Change carrier 不依赖固定语言、Web 或业务仓库结构。"""

    def test_discovery_handles_polyglot_facts_without_framework_inference(self) -> None:
        """发现算法应同时识别多语言 Manifest，仅索引事实而不输出框架/数据库猜测。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Local Rules\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "package.json").write_text('{"scripts":{"test":"echo ok"}}\n', encoding="utf-8")
            (root / "Cargo.toml").write_text("[package]\nname='r'\nversion='0.1.0'\n", encoding="utf-8")
            (root / "go.mod").write_text("module example.invalid/x\ngo 1.25\n", encoding="utf-8")
            context = CODING.scan_project(root)
            paths = {item["path"] for item in context["documents"]}
            self.assertTrue(
                {"AGENTS.md", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"} <= paths
            )
            self.assertTrue(context["generated_at"].endswith("+08:00"))
            self.assertEqual(context["package_scripts"]["package.json"]["test"], "echo ok")
            rendered = str(context)
            self.assertNotIn("FastAPI", rendered)
            self.assertNotIn("PostgreSQL", rendered)

    def test_greenfield_empty_repository_is_valid_discovery_input(self) -> None:
        """空仓库发现应返回空事实集合，而不是因为没有 Manifest 就失败。"""
        with tempfile.TemporaryDirectory() as directory:
            context = CODING.scan_project(Path(directory))
            self.assertEqual(context["documents"], [])
            self.assertEqual(context["package_scripts"], {})

    def test_default_change_root_is_agents_local(self) -> None:
        """没有已有 carrier 时 Coding Change 默认使用 `.agents/changes`。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertEqual(CODING.resolve_change_root(root), root / ".agents/changes")
            self.assertEqual(CODING.change_root_relative(root), ".agents/changes")

    def test_existing_top_level_changes_is_respected(self) -> None:
        """项目已有受支持顶层 changes 结构时不强行迁到 `.agents/changes`。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "changes/active").mkdir(parents=True)
            self.assertEqual(CODING.resolve_change_root(root), root / "changes")
            self.assertEqual(CODING.change_root_relative(root), "changes")

    def test_openspec_blocks_implicit_parallel_change_creation(self) -> None:
        """发现 OpenSpec 时 new-change 默认不得静默创建平行 Coding carrier。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "openspec").mkdir()
            with self.assertRaisesRegex(ValueError, "不会静默创建平行 Change"):
                CODING.resolve_change_root(root, for_create=True)
            self.assertEqual(CODING.resolve_change_root(root), root / ".agents/changes")

    def test_existing_coding_carrier_takes_priority_over_openspec(self) -> None:
        """项目已经明确建立 Coding carrier 时，即使存在 OpenSpec 也可继续读取该 carrier。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "openspec").mkdir()
            (root / ".agents/changes/active").mkdir(parents=True)
            self.assertEqual(
                CODING.resolve_change_root(root, for_create=True),
                root / ".agents/changes",
            )

    def test_discover_cache_is_created_locally_and_invalidates(self) -> None:
        """discover 可创建本地 cache，未变化时命中，事实入口变化后刷新。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            _, mode1 = CODING.ensure_project_context(root)
            _, mode2 = CODING.ensure_project_context(root)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            _, mode3 = CODING.ensure_project_context(root)
            self.assertEqual(mode1, "created")
            self.assertEqual(mode2, "cache_hit")
            self.assertEqual(mode3, "refreshed")
            self.assertTrue((root / ".agents/project-context.json").is_file())

    def test_new_change_uses_current_schema(self) -> None:
        """新建 Coding Change 必须写入当前 schema 和 Completion Gate。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = CODING.create_change(
                root,
                change_id="CHG-20260826-portability",
                title="Portability",
                owner="test",
                branch="test/portability",
                level="L2",
            )
            content = path.read_text(encoding="utf-8")
            self.assertIn("schema: coding-change/v1", content)
            self.assertIn("completion_gate: required", content)
            self.assertTrue(str(path).replace("\\", "/").endswith(".agents/changes/active/CHG-20260826-portability/CHANGE.md"))


if __name__ == "__main__":
    unittest.main()
