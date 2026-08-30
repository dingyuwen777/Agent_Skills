from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from types import SimpleNamespace
from unittest import mock
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
    """验证显式版本输入、onefile Runtime 和 Release-only 资产合同。"""

    def test_release_version_source_is_explicit_and_development_build_has_stable_identity(self) -> None:
        """仓库不保留 VERSION；正式版本显式传入，普通构建使用固定 development SemVer。"""
        builder = _load_module("runtime_release_version", RUNTIME_BUILDER_PATH)
        self.assertFalse((ROOT / "VERSION").exists())
        self.assertEqual(builder.DEVELOPMENT_VERSION, "0.0.0-dev")
        self.assertEqual(builder._normalise_release_version(None), "0.0.0-dev")
        self.assertEqual(builder._normalise_release_version("2.0.0"), "2.0.0")
        with self.assertRaises(ValueError):
            builder._normalise_release_version("v2.0.0")

    def test_runtime_builder_embeds_project_payload_and_version(self) -> None:
        """Runtime Builder 同时保持 Source/Routing/Project Payload、构建环境与版本身份。"""
        source = RUNTIME_BUILDER_PATH.read_text(encoding="utf-8")
        for marker in (
            "source_digest",
            "routing_digest",
            "payload_digest",
            "SOURCE_COMMIT",
            "RELEASE_IDENTITY_SCHEMA",
            "install_manifest_schema",
            "PROJECT_PAYLOAD_B64",
            "DEVELOPMENT_VERSION",
            "--release-version",
            "python_version",
            "context_budget",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("_read_release_version", source)
        self.assertNotIn("build_distribution_kit", source)
        self.assertNotIn("runtime-kit", source.lower())

    def test_formal_build_requires_github_sha_to_match_real_head(self) -> None:
        """正式 GitHub build 必须把 source_commit 绑定到实际 checkout，拒绝伪造或错配。"""
        builder = _load_module("runtime_source_commit", RUNTIME_BUILDER_PATH)
        head = "a" * 40
        completed = SimpleNamespace(returncode=0, stdout=head + "\n")
        with mock.patch.object(builder.subprocess, "run", return_value=completed):
            with mock.patch.dict(os.environ, {"GITHUB_SHA": head}, clear=True):
                self.assertEqual(builder._source_commit(ROOT), head)
            with mock.patch.dict(os.environ, {"GITHUB_SHA": "b" * 40}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "GITHUB_SHA 与当前源码 HEAD 不一致"):
                    builder._source_commit(ROOT)

    def test_release_workflow_is_manual_tag_driven_without_immutability_gate(self) -> None:
        """Release 只允许 main 手工 tag，不依赖 Immutability 或自定义管理 Secret。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "workflow_dispatch",
            "inputs:",
            "tag:",
            "refs/heads/main",
            'VERSION="${TAG#v}"',
            "gh release view",
            "gh api",
            "git rev-parse",
            "--draft",
            "gh release upload",
            "gh release edit",
            "--draft=false",
        ):
            self.assertIn(marker, workflow)
        for obsolete in ("FILE_VERSION", "Get-Content VERSION", "仓库 VERSION", "< VERSION"):
            self.assertNotIn(obsolete, workflow)
        for removed_gate in (
            "RELEASE_SETTINGS_TOKEN",
            "immutable-releases",
            "Release Immutability",
            ".immutable",
        ):
            self.assertNotIn(removed_gate, workflow)
        self.assertNotIn("\n  push:\n", workflow)
        self.assertEqual(workflow.count("contents: write"), 1)

    def test_release_publishes_only_three_binaries_usage_and_checksums(self) -> None:
        """Identity 只作构建验证；最终 Release 仍只发布三平台 binary、USAGE 和 checksum。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "agent-skills-mcp-v${RELEASE_VERSION}-linux",
            '"agent-skills-mcp-v$env:RELEASE_VERSION-windows"',
            "agent-skills-mcp-v${RELEASE_VERSION}-macos",
            "linux.manifest.json",
            "windows.manifest.json",
            "macos.manifest.json",
            "agent-skills-runtime-release-identity/v1",
            ".source_commit == $commit",
            '.python_version == "3.12.10"',
            '."TaskRoute协议" == "Agent Skills 任务路由/v1"',
            '."RoutingManifest协议" == "Agent Skills 路由清单/v1"',
            '."MCP工具契约协议" == "Agent Skills MCP工具契约/v2"',
            '.install_manifest_schema == "agent-skills-install/v3"',
            '."Routing摘要" | test',
            "artifact_sha256",
            "USAGE.md",
            "SHA256SUMS",
            "--notes-file USAGE.md",
            'rm release-assets/*.manifest.json',
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
            'cp "${artifact}" "release-assets/${name}"',
            'Copy-Item $artifact "release-assets\\$name.exe"',
            'Copy-Item $identity "release-assets\\$name.manifest.json"',
            "release-assets/agent-skills-mcp-v*-linux",
            "release-assets/agent-skills-mcp-v*-linux.manifest.json",
            "release-assets/agent-skills-mcp-v*-windows.exe",
            "release-assets/agent-skills-mcp-v*-windows.manifest.json",
            "release-assets/agent-skills-mcp-v*-macos",
            "release-assets/agent-skills-mcp-v*-macos.manifest.json",
        ):
            self.assertIn(marker, workflow)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "需要非 Windows bash 验证 Release Shell 语义")
    def test_release_checksum_step_hashes_only_expected_assets(self) -> None:
        """checksum step 必须只校验四个正式输入资产并排除 identity、输出与临时文件。"""
        script = _extract_workflow_run_block("Generate SHA256SUMS")
        version = "2.0.0"
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
            (release_assets / f"agent-skills-mcp-v{version}-linux.manifest.json").write_text(
                "{}", encoding="utf-8"
            )
            (release_assets / "unexpected.tmp").write_text("temporary", encoding="utf-8")

            env = os.environ.copy()
            env["RELEASE_VERSION"] = version
            result = subprocess.run(
                ["bash", "-euo", "pipefail", "-c", script],
                cwd=temp_root,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
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
            self.assertFalse(any(line.endswith(".manifest.json") for line in checksum_lines))
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
            ".manifest.json",
        ):
            self.assertNotIn(maintainer_only, usage)


if __name__ == "__main__":
    unittest.main()
