from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import tempfile
import textwrap
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


def _extract_workflow_run_block(step_name: str) -> str:
    """从 Release Workflow 中提取指定 step 的 run Shell 正文。"""
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    step_marker = f"      - name: {step_name}\n"
    step_start = workflow.find(step_marker)
    if step_start < 0:
        raise AssertionError(f"Release Workflow 缺少 step：{step_name}")
    run_marker = "        run: |\n"
    run_start = workflow.find(run_marker, step_start)
    if run_start < 0:
        raise AssertionError(f"Release Workflow step 缺少 run block：{step_name}")
    run_start += len(run_marker)
    next_step = workflow.find("\n      - name:", run_start)
    run_end = len(workflow) if next_step < 0 else next_step
    return textwrap.dedent(workflow[run_start:run_end]).strip() + "\n"


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

    @unittest.skipUnless(shutil.which("bash"), "需要 bash 验证 Release Shell 语义")
    def test_release_checksum_step_hashes_only_expected_assets(self) -> None:
        """checksum step 必须只校验四个正式资产并排除输出文件与其他临时文件。"""
        script = _extract_workflow_run_block("Generate SHA256SUMS")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        expected_assets = (
            f"agent-skills-mcp-v{version}-linux",
            f"agent-skills-mcp-v{version}-windows.exe",
            f"agent-skills-mcp-v{version}-macos",
            "USAGE.md",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            release_assets = temp_root / "release-assets"
            release_assets.mkdir()
            for index, asset in enumerate(expected_assets):
                (release_assets / asset).write_bytes(f"release-asset-{index}".encode("utf-8"))
            (release_assets / "unexpected.tmp").write_text("temporary", encoding="utf-8")

            env = os.environ.copy()
            env["RELEASE_VERSION"] = version
            result = subprocess.run(
                ["bash", "-euo", "pipefail", "-c", script],
                cwd=temp_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=f"checksum step 执行失败\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )
            checksum_lines = (release_assets / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(checksum_lines), 4)
            self.assertFalse(any(line.endswith("  SHA256SUMS") for line in checksum_lines))
            self.assertFalse(any(line.endswith("  unexpected.tmp") for line in checksum_lines))
            for asset in expected_assets:
                self.assertEqual(sum(line.endswith(f"  {asset}") for line in checksum_lines), 1)

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
