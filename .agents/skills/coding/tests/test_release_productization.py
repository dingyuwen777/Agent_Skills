from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
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


class ReleaseProductizationTest(unittest.TestCase):
    """验证 VERSION、onefile Runtime 和 Release-only 资产合同。"""

    def test_version_source_of_truth_is_valid_semver(self) -> None:
        """Runtime Builder 应直接使用根 VERSION 作为 Release 版本事实源。"""
        builder = _load_module("runtime_release_version", RUNTIME_BUILDER_PATH)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, builder.VERSION_PATTERN)
        self.assertEqual(builder._read_release_version(ROOT), version)

    def test_runtime_builder_embeds_project_payload_and_version(self) -> None:
        """Runtime Builder 同时保持 Reference 与 Project Payload 两个完整性域。"""
        source = RUNTIME_BUILDER_PATH.read_text(encoding="utf-8")
        for marker in ("source_digest", "payload_digest", "PROJECT_PAYLOAD_B64", "VERSION"):
            self.assertIn(marker, source)
        self.assertNotIn("build_distribution_kit", source)
        self.assertNotIn("runtime-kit", source.lower())

    def test_release_workflow_is_manual_and_immutable(self) -> None:
        """Release 只允许 main 手工输入 v<VERSION>，且已存在 tag/Release 时拒绝覆盖。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "workflow_dispatch",
            "inputs:",
            "tag:",
            "refs/heads/main",
            'VERSION="${TAG#v}"',
            "输入 tag ${TAG} 与仓库 VERSION=${FILE_VERSION} 不一致",
            "gh release view",
            "gh api",
            "git rev-parse",
        ):
            self.assertIn(marker, workflow)
        self.assertNotIn("\n  push:\n", workflow)
        self.assertEqual(workflow.count("contents: write"), 1)

    def test_release_publishes_three_binaries_usage_and_checksums(self) -> None:
        """最终 Release 只面向使用者发布三平台 binary、USAGE 和 checksum。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "agent-skills-mcp-v${RELEASE_VERSION}-linux",
            "agent-skills-mcp-v$env:RELEASE_VERSION-windows.exe",
            "agent-skills-mcp-v${RELEASE_VERSION}-macos",
            "USAGE.md",
            "SHA256SUMS",
            "--notes-file USAGE.md",
            'test "$(wc -l < SHA256SUMS)" -eq 4',
        ):
            self.assertIn(marker, workflow)
        for obsolete in ("agent-skills-full-kit", "runtime-kit", "--generate-notes"):
            self.assertNotIn(obsolete, workflow.lower() if obsolete == "runtime-kit" else workflow)

    def test_release_upload_sources_are_not_hidden(self) -> None:
        """三平台 artifact 上传源必须位于非隐藏目录，避免被 upload-artifact 默认排除。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn(".release-assets", workflow)
        for marker in (
            'cp "${artifact}" "release-assets/agent-skills-mcp-v${RELEASE_VERSION}-linux"',
            'Copy-Item $artifact "release-assets\\agent-skills-mcp-v$env:RELEASE_VERSION-windows.exe"',
            'cp "${artifact}" "release-assets/agent-skills-mcp-v${RELEASE_VERSION}-macos"',
            "path: release-assets/agent-skills-mcp-v*-linux",
            "path: release-assets/agent-skills-mcp-v*-windows.exe",
            "path: release-assets/agent-skills-mcp-v*-macos",
        ):
            self.assertIn(marker, workflow)

    def test_user_guide_is_final_user_only(self) -> None:
        """USAGE 必须是纯用户操作说明，不混入源码维护、内部 Contract 或治理术语。"""
        usage = (ROOT / "USAGE.md").read_text(encoding="utf-8")
        for marker in ("Windows", "Linux", "macOS", "升级", "回退", "status --json", "self-test --json"):
            self.assertIn(marker, usage)
        for maintainer_only in (
            "源仓库",
            "维护者",
            "canonical",
            "Reference Stub",
            "Project Payload",
            "managed block",
            ".agents/",
            "SKILL.md",
            "scripts/build_runtime.py",
            ".agents/changes",
            "Completion Audit",
            "PyInstaller",
            "AES-GCM",
            "onefile",
            "fallback",
            "local stdio",
            "Remote MCP",
        ):
            self.assertNotIn(maintainer_only, usage)


if __name__ == "__main__":
    unittest.main()
