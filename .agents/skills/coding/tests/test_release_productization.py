from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[4]
INSTALL_PATH = ROOT / "scripts/install.py"
FULL_BUILDER_PATH = ROOT / "scripts/build_full_distribution.py"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"


def _load_module(name: str, path: Path):
    """从仓库路径加载待验证脚本模块。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstallerSourceBoundaryTest(unittest.TestCase):
    """验证安装器不会把 Agent_Skills 安装进自身或自身后代目录。"""

    def test_target_inside_source_is_rejected_before_copy(self) -> None:
        """source descendant target 必须在任何复制或 Bootstrap 前被拒绝。"""
        install = _load_module("installer_source_boundary", INSTALL_PATH)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = source / "nested" / "target"
            source.mkdir()
            target.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "源仓库内部"):
                install._validate_target(source, target)

    def test_sibling_target_remains_allowed(self) -> None:
        """与 source 同级的普通目标目录不应被 descendant 防护误伤。"""
        install = _load_module("installer_sibling_boundary", INSTALL_PATH)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            install._validate_target(source, target)


class ReleaseProductizationTest(unittest.TestCase):
    """验证正式版本、Full Distribution Kit 和 Release workflow 的产品合同。"""

    def test_version_source_of_truth_is_semver_1_0_0(self) -> None:
        """首个正式产品化版本必须由根 VERSION 唯一声明为 1.0.0。"""
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "1.0.0")

    def test_full_distribution_kit_is_source_independent_and_excludes_repository_state(self) -> None:
        """Full Kit 解压后应可独立安装三个完整 Skill，且不携带源仓库治理状态。"""
        self.assertTrue(FULL_BUILDER_PATH.is_file(), "缺少 Full Distribution Kit Builder")
        builder = _load_module("full_distribution_builder", FULL_BUILDER_PATH)
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            output = temp / "dist"
            result = builder.build_full_distribution(ROOT, output)
            zip_path = Path(result["distribution_kit"])
            self.assertTrue(zip_path.is_file())
            self.assertEqual(result["release_version"], "1.0.0")
            self.assertEqual(zip_path.name, "agent-skills-full-kit-v1.0.0.zip")

            extract_root = temp / "extract"
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(extract_root)
            kit = extract_root / "agent-skills-full-kit-v1.0.0"
            self.assertTrue((kit / "scripts/install.py").is_file())
            self.assertTrue((kit / ".agents/skills/coding/SKILL.md").is_file())
            self.assertTrue((kit / ".agents/skills/review/SKILL.md").is_file())
            self.assertTrue((kit / ".agents/skills/docs/SKILL.md").is_file())
            self.assertTrue((kit / "agent-skills-full-kit.json").is_file())
            self.assertFalse((kit / "AGENTS.md").exists())
            self.assertFalse((kit / ".agents/changes").exists())
            self.assertFalse((kit / ".agents/project-context.json").exists())
            reference = kit / ".agents/skills/coding/references/02_跨项目研发任务路由.md"
            self.assertNotIn("Runtime 入口", reference.read_text(encoding="utf-8"))

            target = temp / "target"
            target.mkdir()
            completed = subprocess.run(
                [sys.executable, str(kit / "scripts/install.py"), "--target", str(target), "--json"],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["mode"], "full")
            self.assertTrue((target / "AGENTS.md").is_file())

    def test_runtime_builder_records_release_version_without_changing_reference_digest_contract(self) -> None:
        """Runtime manifest 与 Kit metadata 应增加 release_version，但 source_digest 仍独立来自 canonical References。"""
        source = (ROOT / "scripts/build_runtime.py").read_text(encoding="utf-8")
        self.assertIn('"release_version"', source)
        self.assertIn("source_digest", source)
        self.assertIn("VERSION", source)

    def test_release_workflow_builds_three_platforms_and_creates_immutable_release(self) -> None:
        """正式 workflow 必须由 VERSION/main 驱动，三平台构建后汇总校验和并创建 Release。"""
        self.assertTrue(RELEASE_WORKFLOW.is_file(), "缺少正式 Release workflow")
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "workflow_dispatch",
            'branches: ["main"]',
            'paths: ["VERSION"]',
            "ubuntu-24.04",
            "windows-latest",
            "macos-15",
            "scripts/build_full_distribution.py",
            "scripts/build_runtime.py",
            "agent-skills-full-kit-v${VERSION}.zip",
            "agent-skills-mcp-runtime-kit-v${VERSION}-linux.zip",
            "agent-skills-mcp-runtime-kit-v${VERSION}-windows.zip",
            "agent-skills-mcp-runtime-kit-v${VERSION}-macos.zip",
            "SHA256SUMS",
            "gh release create",
            "contents: write",
            "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
            "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
        ):
            self.assertIn(marker, workflow)
        self.assertIn("gh release view", workflow)
        self.assertIn("git rev-parse", workflow)

    def test_release_documentation_exists(self) -> None:
        """维护者 Release 流程和版本历史必须有独立正式文档。"""
        self.assertTrue((ROOT / "RELEASING.md").is_file())
        self.assertTrue((ROOT / "CHANGELOG.md").is_file())


if __name__ == "__main__":
    unittest.main()
