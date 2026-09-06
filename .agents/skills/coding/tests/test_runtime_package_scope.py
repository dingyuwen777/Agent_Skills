from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
WORKFLOW = ROOT / ".github/workflows/skill-tests.yml"
CLASSIFIER = ROOT / ".github/scripts/runtime_package_scope.py"
MAINTENANCE = ROOT / ".agents/MAINTENANCE.md"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"


def _load_selector():
    """从真实维护脚本加载 selector，避免在测试中复制第二份路径规则。"""
    spec = importlib.util.spec_from_file_location("runtime_package_scope", CLASSIFIER)
    if spec is None or spec.loader is None:
        raise AssertionError("无法加载 CI Evidence Selector")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _selection(*paths: str):  # type: ignore[no-untyped-def]
    """返回 changed paths 对应的正式 EvidenceSelection。"""
    return _load_selector().select_evidence(paths)


class RuntimePackageScopePolicyTest(unittest.TestCase):
    """验证 CI 按语义 Evidence 与 Runtime package 风险多轴选择。"""

    def test_stable_classifier_path_is_multi_axis_evidence_selector(self) -> None:
        self.assertTrue(CLASSIFIER.is_file(), "缺少稳定 CI Evidence Selector")
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("runtime_scope", workflow)
        self.assertIn("semantic_profile", workflow)
        self.assertIn("--json", workflow)
        self.assertIn("--run-selected-tests", workflow)
        self.assertIn(".github/scripts/runtime_package_scope.py", workflow)
        self.assertNotIn("runtime/*|runtime/**/*", workflow)

    def test_human_docs_are_targeted_without_runtime_setup_or_package(self) -> None:
        for path in ("README.md", "runtime/README.md"):
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "governance")
                self.assertEqual(selected.semantic_profile, "human_docs")
                self.assertIn("human_docs", selected.semantic_groups)
                self.assertNotEqual(selected.test_files, ("*",))
                self.assertFalse(selected.runtime_dependencies_required)
                self.assertFalse(selected.compile_required)
                self.assertFalse(selected.cli_smoke_required)
                self.assertFalse(selected.full_required)

    def test_usage_selects_human_docs_and_release_surface_without_binary(self) -> None:
        selected = _selection("USAGE.md")
        self.assertEqual(selected.runtime_scope, "content")
        self.assertEqual(selected.semantic_profile, "human_docs")
        self.assertEqual(set(selected.semantic_groups), {"human_docs", "release_surface"})
        self.assertFalse(selected.runtime_dependencies_required)
        self.assertFalse(selected.compile_required)
        self.assertFalse(selected.cli_smoke_required)
        self.assertFalse(selected.full_required)
        self.assertIn("test_release_platform_zips.py", selected.test_files)

    def test_repository_governance_uses_targeted_governance_evidence(self) -> None:
        for path in (
            "AGENTS.md",
            ".agents/MAINTENANCE.md",
            ".github/ISSUE_TEMPLATE/03-technical-change.yml",
            ".github/PULL_REQUEST_TEMPLATE.md",
        ):
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "governance")
                self.assertEqual(selected.semantic_profile, "governance")
                self.assertIn("governance", selected.semantic_groups)
                self.assertNotEqual(selected.test_files, ("*",))
                self.assertFalse(selected.runtime_dependencies_required)
                self.assertFalse(selected.compile_required)
                self.assertFalse(selected.cli_smoke_required)

    def test_professional_skills_select_owner_and_router_closure(self) -> None:
        cases = {
            ".agents/skills/docs/SKILL.md": "docs_skill",
            ".agents/skills/figma/SKILL.md": "figma_skill",
            ".agents/skills/testing/SKILL.md": "testing_skill",
            ".agents/skills/review/SKILL.md": "review_skill",
        }
        for path, owner_group in cases.items():
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "content")
                self.assertEqual(selected.semantic_profile, "content_targeted")
                self.assertEqual(set(selected.semantic_groups), {"router", owner_group})
                self.assertTrue(selected.runtime_dependencies_required)
                self.assertFalse(selected.compile_required)
                self.assertFalse(selected.cli_smoke_required)
                self.assertFalse(selected.full_required)
                self.assertNotEqual(selected.test_files, ("*",))

    def test_coding_router_and_entry_keep_broad_semantic_fail_closed(self) -> None:
        for path in (
            ".agents/skills/ENTRY.md",
            ".agents/skills/router/SKILL.md",
            ".agents/skills/coding/SKILL.md",
            ".agents/skills/coding/references/07_通用验证与证据策略.md",
        ):
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "content")
                self.assertEqual(selected.semantic_profile, "full")
                self.assertEqual(selected.test_files, ("*",))
                self.assertTrue(selected.runtime_dependencies_required)
                self.assertFalse(selected.compile_required)
                self.assertFalse(selected.cli_smoke_required)
                self.assertTrue(selected.full_required)

    def test_coding_script_change_adds_compile_and_cli_smoke(self) -> None:
        for path in (
            ".agents/skills/coding/scripts/coding.py",
            ".agents/skills/coding/scripts/ready_check.py",
        ):
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "content")
                self.assertTrue(selected.full_required)
                self.assertTrue(selected.runtime_dependencies_required)
                self.assertTrue(selected.compile_required)
                self.assertTrue(selected.cli_smoke_required)

    def test_change_carrier_alone_uses_change_only_without_semantic_tests(self) -> None:
        selected = _selection(".agents/changes/active/CHG-example/CHANGE.md")
        self.assertEqual(selected.runtime_scope, "change_only")
        self.assertEqual(selected.semantic_profile, "change_only")
        self.assertFalse(selected.semantic_tests_required)
        self.assertFalse(selected.runtime_dependencies_required)
        self.assertFalse(selected.compile_required)
        self.assertFalse(selected.cli_smoke_required)
        self.assertEqual(selected.test_files, ())

    def test_archive_control_plane_is_targeted_governance_not_runtime_package(self) -> None:
        for path in (
            ".github/workflows/change-archive.yml",
            ".github/scripts/archive_change_after_merge.py",
        ):
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "governance")
                self.assertFalse(selected.full_required)
                self.assertIn("ci_self", selected.semantic_groups)
                self.assertIn("governance", selected.semantic_groups)
                self.assertNotEqual(selected.test_files, ("*",))

    def test_ordinary_test_only_change_runs_that_test_without_full_promotion(self) -> None:
        selected = _selection(".agents/skills/coding/tests/test_testing_skill.py")
        self.assertEqual(selected.runtime_scope, "content")
        self.assertEqual(selected.semantic_profile, "test_only")
        self.assertEqual(selected.test_files, ("test_testing_skill.py",))
        self.assertTrue(selected.runtime_dependencies_required)
        self.assertFalse(selected.full_required)

    def test_ci_self_tests_and_workflows_fail_closed_to_full_package(self) -> None:
        for path in (
            ".github/scripts/runtime_package_scope.py",
            ".github/workflows/skill-tests.yml",
            ".github/workflows/release.yml",
            ".agents/skills/coding/tests/test_runtime_package_scope.py",
            ".agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py",
        ):
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "package")
                self.assertEqual(selected.semantic_profile, "full")
                self.assertEqual(selected.test_files, ("*",))
                self.assertTrue(selected.runtime_dependencies_required)
                self.assertTrue(selected.compile_required)
                self.assertTrue(selected.cli_smoke_required)
                self.assertTrue(selected.full_required)

    def test_runtime_and_package_paths_keep_three_platform_evidence(self) -> None:
        for path in (
            ".gitattributes",
            "runtime/requirements.txt",
            "runtime/requirements-build.txt",
            "runtime/agent_skills_runtime/runtime.py",
            "runtime/agent_skills_runtime/crypto.py",
            "scripts/build_runtime.py",
            "scripts/runtime_mcp_smoke.py",
        ):
            with self.subTest(path=path):
                selected = _selection(path)
                self.assertEqual(selected.runtime_scope, "package")
                self.assertTrue(selected.full_required)
                self.assertTrue(selected.runtime_dependencies_required)
                self.assertTrue(selected.compile_required)
                self.assertTrue(selected.cli_smoke_required)

    def test_unknown_or_empty_paths_fail_closed_to_full_package(self) -> None:
        for paths in (("tools/new_machine_control.bin",), ()):
            with self.subTest(paths=paths):
                selected = _selection(*paths)
                self.assertEqual(selected.runtime_scope, "package")
                self.assertTrue(selected.full_required)
                self.assertEqual(selected.test_files, ("*",))

    def test_mixed_paths_only_expand_evidence(self) -> None:
        docs_and_testing = _selection("README.md", ".agents/skills/testing/SKILL.md")
        self.assertEqual(docs_and_testing.runtime_scope, "content")
        self.assertFalse(docs_and_testing.full_required)
        self.assertIn("human_docs", docs_and_testing.semantic_groups)
        self.assertIn("testing_skill", docs_and_testing.semantic_groups)
        self.assertIn("router", docs_and_testing.semantic_groups)

        package = _selection("README.md", "runtime/agent_skills_runtime/runtime.py")
        self.assertEqual(package.runtime_scope, "package")
        self.assertTrue(package.full_required)
        self.assertEqual(package.test_files, ("*",))

    def test_all_group_mappings_point_to_real_tests(self) -> None:
        module = _load_selector()
        test_dir = ROOT / ".agents/skills/coding/tests"
        for group, names in module._GROUP_TEST_FILES.items():
            with self.subTest(group=group):
                self.assertTrue(names, f"test group 为空：{group}")
                for name in names:
                    self.assertTrue((test_dir / name).is_file(), f"{group} 引用了不存在的测试：{name}")

    def test_default_classify_paths_remains_backward_compatible(self) -> None:
        classify_paths = _load_selector().classify_paths
        self.assertEqual(classify_paths(["README.md"]), "governance")
        self.assertEqual(classify_paths(["USAGE.md"]), "content")
        self.assertEqual(classify_paths(["runtime/agent_skills_runtime/runtime.py"]), "package")

    def test_workflow_keeps_package_ready_signal_and_three_platform_gates(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("package_evidence_required", workflow)
        self.assertIn("change_gate_ready", workflow)
        self.assertIn("ready_for_review", workflow)
        self.assertIn("github.event.pull_request.draft", workflow)
        self.assertGreaterEqual(
            workflow.count("steps.runtime-scope.outputs.runtime_scope == 'package'"), 4
        )
        self.assertGreaterEqual(
            workflow.count("needs.agent-skills-core.outputs.runtime_scope == 'package'"), 2
        )

    def test_setup_python_uses_dependency_cache_not_binary_cache(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("cache: 'pip'", workflow)
        self.assertIn("runtime/requirements.txt", workflow)
        self.assertIn("runtime/requirements-build.txt", workflow)
        self.assertNotIn("cache-path: .runtime-dist", workflow)
        self.assertNotIn("actions/cache", workflow)

    def test_maintenance_owns_changed_scope_evidence_boundary_rule(self) -> None:
        maintenance = MAINTENANCE.read_text(encoding="utf-8")
        for marker in (
            "多轴 CI Evidence Selector",
            "changed-scope Evidence Check",
            "content 不再机械等于全 492+ self-contained tests",
            "unknown→full",
            "[skip ci]",
            "不得再次 checkout/setup Python/重复 ready_check",
            "正式 Release 不复用普通 CI binary",
        ):
            self.assertIn(marker, maintenance)

    def test_release_workflow_still_builds_all_platform_artifacts(self) -> None:
        release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in ("Release Runtime Linux", "Release Runtime Windows", "Release Runtime macOS"):
            self.assertIn(marker, release)
        self.assertNotIn("runtime_package_scope.py", release)


if __name__ == "__main__":
    unittest.main()
