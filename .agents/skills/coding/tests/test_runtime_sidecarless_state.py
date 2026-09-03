from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime import project_installer as PROJECT_INSTALLER
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]
BUILDER = ROOT / "scripts/build_runtime.py"
INSTALLER = ROOT / "runtime/agent_skills_runtime/project_installer.py"
SERVER = ROOT / "runtime/agent_skills_runtime/server.py"
RUNTIME_PACKAGE_WORKFLOW = ROOT / ".github/workflows/runtime-package-tests.yml"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
LEGACY_INSTALL_MANIFEST = Path(".agents/agent-skills-install.json")


def _load_module(name: str, path: Path):
    """从仓库真实路径加载 Builder，验证其机器输出合同。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeSidecarlessStateTest(unittest.TestCase):
    """固定 Runtime 安装和构建不再产生 JSON sidecar 的产品合同。"""

    def test_first_project_install_leaves_no_install_manifest(self) -> None:
        """首次安装完成后目标项目不得保留 agent-skills-install.json。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            target = temp_root / "target"
            target.mkdir()
            artifact = temp_root / "agent-skills"
            artifact.write_bytes(b"runtime-fixture")

            result = install_project(target, payload, artifact, release_version="3.1.0")

            self.assertFalse((target / LEGACY_INSTALL_MANIFEST).exists())
            self.assertNotIn("manifest", result)

    def test_installer_uses_runtime_embedded_previous_ownership_not_persistent_sidecar(self) -> None:
        """正常新安装状态必须来自旧 Runtime 自描述，legacy manifest 只能用于一次迁移。"""
        source = INSTALLER.read_text(encoding="utf-8")
        self.assertIn("install-state", source)
        self.assertIn("legacy", source.lower())
        self.assertNotIn("def _build_manifest(", source)
        self.assertNotIn('manifest_path: _build_manifest(', source)

    def test_old_runtime_install_state_query_has_bounded_timeout(self) -> None:
        """旧 Runtime 卡死时 ownership 查询必须在有限时间失败，不能让升级无限等待。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / "agent-skills"
            runtime.write_bytes(b"runtime-fixture")
            timeout = PROJECT_INSTALLER._INSTALL_STATE_QUERY_TIMEOUT_SECONDS
            with patch.object(
                PROJECT_INSTALLER.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(cmd=[str(runtime)], timeout=timeout),
            ) as run:
                with self.assertRaisesRegex(RuntimeError, "install-state 查询超过 .* 秒"):
                    PROJECT_INSTALLER._query_installed_runtime_state(runtime)

            self.assertGreater(timeout, 0)
            self.assertEqual(run.call_args.kwargs["timeout"], timeout)

    def test_runtime_has_internal_install_state_without_expanding_public_status(self) -> None:
        """旧 binary 必须能内部返回 ownership，但普通 status/MCP 不新增 managed 文件清单。"""
        source = SERVER.read_text(encoding="utf-8")
        self.assertIn("install-state", source)
        self.assertIn("INSTALL_STATE_SCHEMA", source)
        help_section = source[source.index("def _build_parser"):source.index("def _public_install_result")]
        self.assertNotIn("__install-state", help_section)
        public_section = source[source.index("def _public_install_result"):]
        self.assertNotIn('"managed_files"', public_section)

    def test_builder_does_not_create_release_identity_manifest_sidecar(self) -> None:
        """Builder 机器结果直接携带完整性证据，不再写 `<artifact>.manifest.json`。"""
        builder = _load_module("runtime_sidecarless_builder", BUILDER)
        source = BUILDER.read_text(encoding="utf-8")
        self.assertNotIn("RELEASE_IDENTITY_SCHEMA", source)
        self.assertNotIn("manifest_path", source)
        self.assertNotIn("install_manifest_schema", source)
        self.assertNotIn(".manifest.json", source)
        self.assertIn("integrity_fingerprint", source)
        self.assertIn("artifact_sha256", source)
        self.assertTrue(hasattr(builder, "_normalise_release_version"))

    def test_permanent_workflows_use_outputs_and_only_negative_sidecar_checks(self) -> None:
        """三平台 CI/Release 只允许负向检查 sidecar 不存在，不得生成、复制或上传 manifest。"""
        runtime_workflow = RUNTIME_PACKAGE_WORKFLOW.read_text(encoding="utf-8")
        release_workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for workflow in (runtime_workflow, release_workflow):
            self.assertNotIn("install_manifest_schema", workflow)
            self.assertNotIn("manifest_path", workflow)
            self.assertNotIn("linux.manifest.json", workflow)
            self.assertNotIn("windows.manifest.json", workflow)
            self.assertNotIn("macos.manifest.json", workflow)
            self.assertNotIn("cp \"${artifact}.manifest.json\"", workflow)
            self.assertNotIn("Copy-Item \"$artifact.manifest.json\"", workflow)
            self.assertIn("*.manifest.json", workflow)
        for marker in ("integrity_fingerprint", "artifact_sha256"):
            self.assertIn(marker, release_workflow)
        self.assertIn("GITHUB_OUTPUT", release_workflow)
        self.assertIn("sha256", release_workflow.lower())
        self.assertIn("agent-skills-install.json", runtime_workflow)
        self.assertIn("test ! -e", runtime_workflow)


if __name__ == "__main__":
    unittest.main()
