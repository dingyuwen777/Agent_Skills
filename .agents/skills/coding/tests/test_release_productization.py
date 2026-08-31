from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
import zipfile
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

from runtime.agent_skills_runtime.runtime import MCP_TOOL_CONTRACT_PROTOCOL


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_BUILDER_PATH = ROOT / "scripts/build_runtime.py"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
RUNTIME_PACKAGE_WORKFLOW = ROOT / ".github/workflows/runtime-package-tests.yml"
SKILL_TESTS_WORKFLOW = ROOT / ".github/workflows/skill-tests.yml"
RUNTIME_README = ROOT / "runtime/README.md"
RUNTIME_REFERENCE = ROOT / ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"


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
    """验证显式版本输入、onefile Runtime 和平台 ZIP Release-only 资产合同。"""

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

    def test_release_publishes_platform_zips_after_validating_three_platform_identities(self) -> None:
        """Identity 只作构建验证；最终 Release 精确暴露三个平台 ZIP。"""
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
            '.python_version == "3.14.7"',
            '."TaskRoute协议" == "Agent Skills 任务路由/v1"',
            '."RoutingManifest协议" == "Agent Skills 路由清单/v1"',
            f'."MCP工具契约协议" == "{MCP_TOOL_CONTRACT_PROTOCOL}"',
            '.install_manifest_schema == "agent-skills-install/v3"',
            '."Routing摘要" | test',
            "artifact_sha256",
            "USAGE.md",
            "--notes-file USAGE.md",
            'rm release-assets/*.manifest.json',
            "Build platform distribution ZIPs",
            'f"agent-skills-v{version}-linux.zip"',
            'f"agent-skills-v{version}-windows.zip"',
            'f"agent-skills-v{version}-macos.zip"',
            '"agent-skills-v${RELEASE_TAG#v}-linux.zip"',
            '"agent-skills-v${RELEASE_TAG#v}-windows.zip"',
            '"agent-skills-v${RELEASE_TAG#v}-macos.zip"',
            'gh release upload "${RELEASE_TAG}" release-package/agent-skills-v*-linux.zip release-package/agent-skills-v*-windows.zip release-package/agent-skills-v*-macos.zip',
        ):
            self.assertIn(marker, workflow)
        self.assertNotIn('f"agent-skills-v{version}.zip"', workflow)
        self.assertNotIn('expected_package="agent-skills-v${RELEASE_TAG#v}.zip"', workflow)
        self.assertNotIn('gh release upload "${RELEASE_TAG}" release-assets/*', workflow)
        self.assertNotIn("SHA256SUMS", workflow)
        for obsolete in ("agent-skills-full-kit", "runtime-kit", "--generate-notes"):
            self.assertNotIn(obsolete, workflow.lower() if obsolete == "runtime-kit" else workflow)

    def test_release_identity_uses_lf_and_compares_all_platforms(self) -> None:
        """Release 必须固定 canonical 文本换行并比较三平台公共 identity。"""
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes.splitlines())

        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "Release identity 字段校验失败",
            "三平台 Release identity 不一致",
            "del(.artifact, .artifact_sha256)",
            "diff -u",
        ):
            self.assertIn(marker, workflow)

    def test_skill_changes_do_not_require_runtime_package_or_release(self) -> None:
        """纯 Skill 修改只走 Skill Tests，不自动触发三平台 package 或 Release。"""
        skill_tests = SKILL_TESTS_WORKFLOW.read_text(encoding="utf-8")
        runtime_package = RUNTIME_PACKAGE_WORKFLOW.read_text(encoding="utf-8")
        release = RELEASE_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('      - ".agents/**"', skill_tests)
        self.assertNotIn('      - ".agents/**"', runtime_package)
        self.assertIn('      - ".gitattributes"', skill_tests)
        self.assertIn('      - ".gitattributes"', runtime_package)
        self.assertIn("workflow_dispatch:", release)
        self.assertNotIn("\n  pull_request:\n", release)
        self.assertNotIn("\n  push:\n", release)

    def test_release_identity_policy_is_documented(self) -> None:
        """Runtime 文档与 canonical Reference 必须说明 mode 和三平台 identity 规则。"""
        for path in (RUNTIME_README, RUNTIME_REFERENCE):
            content = path.read_text(encoding="utf-8")
            self.assertIn("Git index", content)
            self.assertIn("`0644`", content)
            self.assertIn("`0755`", content)
            self.assertIn("artifact", content)
            self.assertIn("artifact_sha256", content)
            self.assertIn("三平台", content)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "需要非 Windows bash 验证 Release Shell 语义")
    def test_release_rejects_cross_platform_identity_drift(self) -> None:
        """三平台公共 identity 任一漂移时必须 fail closed，修正后才能继续。"""
        script = _extract_workflow_run_block("Validate release identity and assets")
        version = "2.0.0"
        platforms = (
            ("linux", f"agent-skills-mcp-v{version}-linux"),
            ("windows", f"agent-skills-mcp-v{version}-windows.exe"),
            ("macos", f"agent-skills-mcp-v{version}-macos"),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            subprocess.run(["git", "init", "--quiet"], cwd=temp_root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Agent Skills Test",
                    "-c",
                    "user.email=agent-skills-test@example.invalid",
                    "commit",
                    "--quiet",
                    "--allow-empty",
                    "-m",
                    "建立 Release 测试 HEAD",
                ],
                cwd=temp_root,
                check=True,
            )
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=temp_root, text=True, encoding="utf-8"
            ).strip()
            release_assets = temp_root / "release-assets"
            release_assets.mkdir()
            (release_assets / "USAGE.md").write_text("usage", encoding="utf-8")

            manifests: dict[str, dict[str, object]] = {}
            for platform, artifact in platforms:
                artifact_bytes = f"binary-{platform}".encode("utf-8")
                (release_assets / artifact).write_bytes(artifact_bytes)
                manifest = {
                    "schema": "agent-skills-runtime-release-identity/v1",
                    "release_version": version,
                    "source_commit": commit,
                    "artifact": artifact,
                    "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
                    "python_version": "3.14.7",
                    "bundle_schema": "agent-skills-runtime-bundle/v2",
                    "bundle_version": "1" * 16,
                    "TaskRoute协议": "Agent Skills 任务路由/v1",
                    "RoutingManifest协议": "Agent Skills 路由清单/v1",
                    "MCP工具契约协议": MCP_TOOL_CONTRACT_PROTOCOL,
                    "project_payload_schema": "agent-skills-project-payload/v2",
                    "install_manifest_schema": "agent-skills-install/v3",
                    "source_digest": "2" * 64,
                    "Routing摘要": "3" * 64,
                    "payload_digest": "4" * 64,
                    "skill_count": 4,
                    "skills": ["coding", "docs", "figma", "review"],
                }
                manifests[platform] = manifest
                manifest_path = release_assets / f"agent-skills-mcp-v{version}-{platform}.manifest.json"
                manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

            manifests["windows"]["bundle_version"] = "5" * 16
            windows_manifest = release_assets / f"agent-skills-mcp-v{version}-windows.manifest.json"
            windows_manifest.write_text(
                json.dumps(manifests["windows"], ensure_ascii=False), encoding="utf-8"
            )

            stub_dir = temp_root / "bin"
            stub_dir.mkdir()
            gh_stub = stub_dir / "gh"
            gh_stub.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
            gh_stub.chmod(0o755)

            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{stub_dir}{os.pathsep}{env['PATH']}",
                    "RELEASE_TAG": f"v{version}",
                    "RELEASE_VERSION": version,
                    "GITHUB_REF": "refs/heads/main",
                    "GITHUB_SHA": commit,
                    "GITHUB_REPOSITORY": "example/repository",
                    "GH_TOKEN": "test-token",
                }
            )
            rejected = subprocess.run(
                ["bash", "-euo", "pipefail", "-c", script],
                cwd=temp_root,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("三平台 Release identity 不一致", rejected.stderr)

            manifests["windows"]["bundle_version"] = "1" * 16
            windows_manifest.write_text(
                json.dumps(manifests["windows"], ensure_ascii=False), encoding="utf-8"
            )
            accepted = subprocess.run(
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
                accepted.returncode,
                0,
                msg=f"identity 校验执行失败\nstdout:\n{accepted.stdout}\nstderr:\n{accepted.stderr}",
            )

    def test_release_upload_sources_are_not_hidden(self) -> None:
        """三平台内部 artifact 上传源必须位于非隐藏目录，避免 upload-artifact 默认排除。"""
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
    def test_release_zip_step_packages_only_expected_platform_assets(self) -> None:
        """平台 ZIP 只能打包当前平台 Runtime 与 USAGE，排除 identity、其他平台和临时文件。"""
        script = _extract_workflow_run_block("Build platform distribution ZIPs")
        version = "2.0.0"
        binaries = {
            "linux": f"agent-skills-mcp-v{version}-linux",
            "windows": f"agent-skills-mcp-v{version}-windows.exe",
            "macos": f"agent-skills-mcp-v{version}-macos",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            release_assets = temp_root / "release-assets"
            release_assets.mkdir()
            for index, asset in enumerate((*binaries.values(), "USAGE.md")):
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
                msg=f"ZIP step 执行失败\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )
            for platform, binary in binaries.items():
                package = temp_root / "release-package" / f"agent-skills-v{version}-{platform}.zip"
                with zipfile.ZipFile(package) as archive:
                    names = archive.namelist()
                self.assertEqual(names, [binary, "USAGE.md"])
                self.assertNotIn("unexpected.tmp", names)
                self.assertFalse(any(name.endswith(".manifest.json") for name in names))
                for other_binary in binaries.values():
                    if other_binary != binary:
                        self.assertNotIn(other_binary, names)

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
