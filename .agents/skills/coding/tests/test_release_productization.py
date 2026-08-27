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
RUNTIME_BUILDER_PATH = ROOT / "scripts/build_runtime.py"
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
    """验证正式版本、Full Distribution Kit 和手工 tag Release workflow 的产品合同。"""

    def test_version_source_of_truth_is_valid_semver(self) -> None:
        """永久门禁应接受未来合法版本，而不是把首个 1.0.0 永久写死在测试中。"""
        builder = _load_module("full_distribution_version", FULL_BUILDER_PATH)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, builder.VERSION_PATTERN)
        self.assertEqual(builder.read_release_version(ROOT), version)

    def test_full_distribution_kit_is_source_independent_and_excludes_repository_state(self) -> None:
        """Full Kit 解压后应可独立安装三个完整 Skill，并携带真实可用的用户说明。"""
        self.assertTrue(FULL_BUILDER_PATH.is_file(), "缺少 Full Distribution Kit Builder")
        builder = _load_module("full_distribution_builder", FULL_BUILDER_PATH)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            output = temp / "dist"
            result = builder.build_full_distribution(ROOT, output)
            zip_path = Path(result["distribution_kit"])
            self.assertTrue(zip_path.is_file())
            self.assertEqual(result["release_version"], version)
            self.assertEqual(zip_path.name, f"agent-skills-full-kit-v{version}.zip")

            extract_root = temp / "extract"
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(extract_root)
            kit = extract_root / f"agent-skills-full-kit-v{version}"
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
            user_readme = (kit / "README.md").read_text(encoding="utf-8")
            self.assertIn("Agent Skills Full Distribution Kit", user_readme)
            self.assertIn("scripts/install.py --target", user_readme)
            self.assertNotIn("scripts/build_runtime.py", user_readme)

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

    def test_runtime_builder_reads_current_release_version_without_changing_reference_digest_contract(self) -> None:
        """Runtime Builder 应读取当前 VERSION，且 source_digest 仍保持独立 canonical Reference 合同。"""
        builder = _load_module("runtime_release_version", RUNTIME_BUILDER_PATH)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(builder._read_release_version(ROOT), version)
        source = RUNTIME_BUILDER_PATH.read_text(encoding="utf-8")
        self.assertIn("source_digest", source)
        self.assertIn("VERSION", source)

    def test_release_workflow_requires_manual_tag_and_builds_immutable_release(self) -> None:
        """正式 Release 必须手工输入 tag，从 main 构建三平台资产后创建不可覆盖 Release。"""
        self.assertTrue(RELEASE_WORKFLOW.is_file(), "缺少正式 Release workflow")
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "workflow_dispatch",
            "inputs:",
            "tag:",
            "Release tag，例如 v1.0.0",
            "${{ inputs.tag }}",
            "refs/heads/main",
            'VERSION="${TAG#v}"',
            "输入 tag ${TAG} 与仓库 VERSION=${FILE_VERSION} 不一致",
            "ubuntu-24.04",
            "windows-latest",
            "macos-15",
            "scripts/build_full_distribution.py",
            "scripts/build_runtime.py",
            "agent-skills-full-kit-v${RELEASE_VERSION}.zip",
            "agent-skills-mcp-runtime-kit-v${RELEASE_VERSION}-linux.zip",
            "agent-skills-mcp-runtime-kit-v${RELEASE_VERSION}-windows.zip",
            "agent-skills-mcp-runtime-kit-v${RELEASE_VERSION}-macos.zip",
            "SHA256SUMS",
            'gh release create "${RELEASE_TAG}"',
            "contents: write",
            "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
            "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
        ):
            self.assertIn(marker, workflow)
        self.assertEqual(workflow.count("contents: write"), 1)
        self.assertNotIn("\n  push:\n", workflow)
        self.assertNotIn('branches: ["main"]', workflow)
        self.assertNotIn('paths: ["VERSION"]', workflow)
        self.assertIn("gh release view", workflow)
        self.assertIn("gh api", workflow)
        self.assertIn("git rev-parse", workflow)

    def test_release_documentation_exists(self) -> None:
        """维护者 Release、Full Kit 用户说明和版本历史必须有独立正式文档。"""
        self.assertTrue((ROOT / "RELEASING.md").is_file())
        self.assertTrue((ROOT / "FULL_DISTRIBUTION.md").is_file())
        self.assertTrue((ROOT / "CHANGELOG.md").is_file())


if __name__ == "__main__":
    unittest.main()
