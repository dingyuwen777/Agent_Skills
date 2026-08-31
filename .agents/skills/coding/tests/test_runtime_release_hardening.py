from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime import project_installer as INSTALLER
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_BUILDER_PATH = ROOT / "scripts/build_runtime.py"
SKILL_TESTS_WORKFLOW = ROOT / ".github/workflows/skill-tests.yml"
RUNTIME_PACKAGE_WORKFLOW = ROOT / ".github/workflows/runtime-package-tests.yml"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"
PINNED_PYTHON = "3.14.7"


def _load_module(name: str, path: Path):
    """从仓库真实路径加载待验证脚本，避免复制 Builder 实现。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeReleaseHardeningTest(unittest.TestCase):
    """验证 Tag 驱动版本、安装失败安全、固定构建环境与 Context footprint。"""

    def test_release_version_is_explicit_and_root_version_file_is_removed(self) -> None:
        """正式版本只能显式传入 Builder，普通构建使用稳定 development identity。"""
        builder = _load_module("runtime_hardening_version", RUNTIME_BUILDER_PATH)
        self.assertFalse((ROOT / "VERSION").exists(), "根 VERSION 不应继续形成第二个版本事实源")
        self.assertEqual(builder.DEVELOPMENT_VERSION, "0.0.0-dev")
        self.assertEqual(builder._normalise_release_version(None), "0.0.0-dev")
        self.assertEqual(builder._normalise_release_version("2.3.4"), "2.3.4")
        with self.assertRaises(ValueError):
            builder._normalise_release_version("v2.3.4")
        source = RUNTIME_BUILDER_PATH.read_text(encoding="utf-8")
        self.assertIn("--release-version", source)
        self.assertNotIn("_read_release_version", source)

    def test_owned_codex_table_without_managed_marker_fails_closed(self) -> None:
        """manifest 仍在也不能猜测无 marker 的同名 Codex table 属于 Agent Skills。"""
        existing = (
            b"[mcp_servers.agent-skills]\n"
            b'command = ".agents/runtime/agent-skills-mcp"\n'
            b'args = ["serve"]\n'
        )
        with self.assertRaisesRegex(ValueError, "marker|同名 MCP server"):
            INSTALLER._updated_codex_config(
                existing,
                ".agents/runtime/agent-skills-mcp",
                True,
            )

    def test_owned_codex_marker_with_duplicate_external_table_fails_closed(self) -> None:
        """合法 managed block 外再出现同名 table 时 ownership 已歧义，升级不能保留重复 TOML。"""
        existing = (
            b"# keep\n\n"
            + INSTALLER.CODEX_MANAGED_START.encode("utf-8")
            + b"\n[mcp_servers.agent-skills]\n"
            + b'command = ".agents/runtime/agent-skills-mcp"\n'
            + b'args = ["serve"]\n'
            + INSTALLER.CODEX_MANAGED_END.encode("utf-8")
            + b"\n\n[mcp_servers.agent-skills]\n"
            + b'command = "project-owned-duplicate"\n'
        )
        with self.assertRaisesRegex(ValueError, "重复|同名 MCP server"):
            INSTALLER._updated_codex_config(
                existing,
                ".agents/runtime/agent-skills-mcp",
                True,
            )

    def test_install_reports_rollback_failure_instead_of_swallowing_it(self) -> None:
        """安装写入失败且快照恢复也失败时，必须显式报告不完整回滚和原始异常。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            target = temp_root / "target"
            target.mkdir()
            artifact = temp_root / "agent-skills-mcp"
            artifact.write_bytes(b"runtime-fixture")
            install_project(target, payload, artifact, release_version="1.0.0")

            entry_target = (target / ".agents/skills/ENTRY.md").resolve()
            agents_target = (target / "AGENTS.md").resolve()
            original_atomic_write = INSTALLER._atomic_write
            original_restore_file = INSTALLER._restore_file
            install_failed = False
            rollback_failed = False

            def controlled_atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
                """只在第二次安装写 Entry 时制造原始安装失败。"""
                nonlocal install_failed
                if Path(path).resolve() == entry_target and not install_failed:
                    install_failed = True
                    raise OSError("fixture install write failure")
                original_atomic_write(path, content, mode)

            def controlled_restore_file(path: Path, snapshot: tuple[bytes, int] | None) -> None:
                """只让 AGENTS 快照恢复失败，验证错误不能被静默吞掉。"""
                nonlocal rollback_failed
                if Path(path).resolve() == agents_target and not rollback_failed:
                    rollback_failed = True
                    raise OSError("fixture rollback failure")
                original_restore_file(path, snapshot)

            with patch.object(INSTALLER, "_atomic_write", side_effect=controlled_atomic_write):
                with patch.object(INSTALLER, "_restore_file", side_effect=controlled_restore_file):
                    with self.assertRaises(RuntimeError) as captured:
                        install_project(target, payload, artifact, release_version="1.0.1")

            self.assertIn("回滚不完整", str(captured.exception))
            self.assertIn("AGENTS.md", str(captured.exception))
            self.assertIsInstance(captured.exception.__cause__, OSError)
            self.assertIn("fixture install write failure", str(captured.exception.__cause__))

    def test_permanent_and_release_workflows_pin_python_31210(self) -> None:
        """常规 Skill、三平台 Runtime 专项 CI 与 Release 都必须固定 Python 和 action SHA。"""
        setup_marker = f"actions/setup-python@{SETUP_PYTHON_SHA}"
        skill_workflow = SKILL_TESTS_WORKFLOW.read_text(encoding="utf-8")
        runtime_workflow = RUNTIME_PACKAGE_WORKFLOW.read_text(encoding="utf-8")
        release_workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(skill_workflow.count(setup_marker), 1)
        self.assertGreaterEqual(runtime_workflow.count(setup_marker), 3)
        self.assertGreaterEqual(release_workflow.count(setup_marker), 4)
        self.assertGreaterEqual(skill_workflow.count(f'python-version: "{PINNED_PYTHON}"'), 1)
        self.assertGreaterEqual(runtime_workflow.count(f'python-version: "{PINNED_PYTHON}"'), 3)
        self.assertGreaterEqual(release_workflow.count(f'python-version: "{PINNED_PYTHON}"'), 4)
        self.assertNotIn("runs-on: windows-latest", runtime_workflow)
        self.assertNotIn("runs-on: windows-latest", release_workflow)

    def test_release_workflow_uses_tag_only_and_publishes_from_verified_draft(self) -> None:
        """Release tag 是唯一正式版本输入，并在完整 preflight 后经 Draft 资产校验再发布。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for forbidden in (
            "< VERSION",
            "Get-Content VERSION",
            "仓库 VERSION",
            "FILE_VERSION",
        ):
            self.assertNotIn(forbidden, workflow)
        for required in (
            'VERSION="${TAG#v}"',
            '--release-version "${RELEASE_VERSION}"',
            "--release-version $env:RELEASE_VERSION",
            "python -m unittest discover",
            "-s .agents/skills/coding/tests",
            "ready_check.py --root .",
            "gh release create",
            "--draft",
            "gh release upload",
            "gh release edit",
            "--draft=false",
        ):
            self.assertIn(required, workflow)
        self.assertLess(workflow.index("python -m unittest discover"), workflow.index("gh release create"))
        self.assertLess(workflow.index("gh release upload"), workflow.index("--draft=false"))

    def test_release_workflow_uses_no_immutability_gate_or_custom_admin_secret(self) -> None:
        """正式发布不读取仓库 Immutability 设置，也不要求自定义管理 Secret。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for removed_gate in (
            "secrets.RELEASE_SETTINGS_TOKEN",
            "RELEASE_SETTINGS_TOKEN",
            "immutable-releases",
            "immutable_status",
            "Release Immutability",
            "Administration: read",
            ".immutable",
        ):
            self.assertNotIn(removed_gate, workflow)
        for preserved_gate in (
            'GH_TOKEN: ${{ github.token }}',
            'git/ref/tags/${TAG}',
            'gh release view "${TAG}"',
            "python -m unittest discover",
            "ready_check.py --root .",
            "Create verified draft Release",
            "gh release upload",
            "--draft=false",
        ):
            self.assertIn(preserved_gate, workflow)

    def test_failed_release_job_cleans_only_unpublished_draft(self) -> None:
        """Draft 创建/上传失败后必须可重试；失败清理只能删除仍为 Draft 的本次 Release。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "Cleanup failed draft Release",
            "if: failure()",
            "--json isDraft",
            'if [ "${is_draft}" = "true" ]',
            "gh release delete",
            "--cleanup-tag",
            "--yes",
        ):
            self.assertIn(required, workflow)
        cleanup_index = workflow.index("Cleanup failed draft Release")
        publish_index = workflow.index("- name: Publish GitHub Release")
        self.assertGreater(cleanup_index, publish_index)
        cleanup = workflow[cleanup_index:]
        self.assertIn('if [ "${is_draft}" = "true" ]', cleanup)
        self.assertNotIn('if [ "${is_draft}" = "false" ]', cleanup)

    def test_builder_reports_context_footprint_without_reference_details(self) -> None:
        """维护构建输出量化聚合 Context 字节，但不需要公开单个 Reference 身份。"""
        builder = _load_module("runtime_hardening_context", RUNTIME_BUILDER_PATH)
        bundle = build_bundle(ROOT)
        budget = builder._context_budget(ROOT, bundle)
        skills = list(bundle["skills"])
        self.assertGreater(budget["entry_bytes"], 0)
        self.assertGreater(budget["router_bytes"], 0)
        self.assertEqual(sorted(budget["skill_core_bytes"]), skills)
        self.assertEqual(sorted(budget["reference_bytes_by_skill"]), skills)
        self.assertEqual(sorted(budget["base_router_plus_core_bytes"]), skills)
        for skill in skills:
            core_path = ROOT / ".agents/skills" / skill / "SKILL.md"
            self.assertEqual(budget["skill_core_bytes"][skill], len(core_path.read_bytes()))
            self.assertEqual(
                budget["base_router_plus_core_bytes"][skill],
                budget["entry_bytes"]
                + budget["router_bytes"]
                + (0 if skill == "router" else budget["skill_core_bytes"][skill]),
            )
            expected_reference_bytes = sum(
                int(entry["size"])
                for entry in bundle["references"]
                if str(entry["skill"]) == skill
            )
            self.assertEqual(budget["reference_bytes_by_skill"][skill], expected_reference_bytes)
        self.assertNotIn("references", budget)
        self.assertNotIn("reference_ids", budget)


if __name__ == "__main__":
    unittest.main()
