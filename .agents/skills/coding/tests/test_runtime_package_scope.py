from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
WORKFLOW = ROOT / ".github/workflows/skill-tests.yml"
CLASSIFIER = ROOT / ".github/scripts/runtime_package_scope.py"
MAINTENANCE = ROOT / ".agents/MAINTENANCE.md"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"


def _load_classifier():
    """从真实维护脚本加载 classifier，避免在测试中复制第二份路径规则。"""
    spec = importlib.util.spec_from_file_location("runtime_package_scope", CLASSIFIER)
    if spec is None or spec.loader is None:
        raise AssertionError("无法加载 Runtime Package scope classifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimePackageScopePolicyTest(unittest.TestCase):
    """验证普通 CI 按证据边界分级，而正式 Release 保持全平台验证。"""

    def test_runtime_package_scope_has_dedicated_classifier(self) -> None:
        self.assertTrue(CLASSIFIER.is_file(), "缺少 Runtime Package scope classifier")
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("runtime_scope", workflow)
        self.assertIn(".github/scripts/runtime_package_scope.py", workflow)
        self.assertNotIn("runtime/*|runtime/**/*", workflow)

    def test_core_scope_pins_python_and_disables_rename_collapsing(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        core_section = workflow.split("  runtime-windows-package:", 1)[0]
        self.assertIn("Setup Python", core_section)
        self.assertIn('python-version: "3.14.7"', core_section)
        self.assertIn('git diff --name-only --no-renames "${BASE_SHA}" "${HEAD_SHA}"', core_section)

    def test_governance_paths_skip_three_platform_binary(self) -> None:
        classify_paths = _load_classifier().classify_paths
        for path in (
            "README.md",
            "runtime/README.md",
            ".agents/MAINTENANCE.md",
            ".agents/changes/active/CHG-example/CHANGE.md",
        ):
            with self.subTest(path=path):
                self.assertEqual(classify_paths([path]), "governance")

    def test_runtime_content_paths_use_semantic_tests_without_binary_build(self) -> None:
        classify_paths = _load_classifier().classify_paths
        for path in (
            ".agents/skills/ENTRY.md",
            ".agents/skills/coding/SKILL.md",
            ".agents/skills/coding/references/13_example.md",
            ".agents/skills/coding/assets/AGENTS.managed.md",
            ".agents/skills/coding/scripts/coding.py",
            "USAGE.md",
        ):
            with self.subTest(path=path):
                self.assertEqual(classify_paths([path]), "content")

    def test_package_paths_require_three_platform_binary(self) -> None:
        classify_paths = _load_classifier().classify_paths
        for path in (
            ".gitattributes",
            "runtime/requirements.txt",
            "runtime/requirements-build.txt",
            "runtime/agent_skills_runtime/runtime.py",
            "runtime/agent_skills_runtime/crypto.py",
            "scripts/build_runtime.py",
            "scripts/runtime_mcp_smoke.py",
            ".github/scripts/runtime_package_scope.py",
            ".github/workflows/skill-tests.yml",
            ".github/workflows/runtime-package-tests.yml",
            ".github/workflows/release.yml",
        ):
            with self.subTest(path=path):
                self.assertEqual(classify_paths([path]), "package")

    def test_mixed_paths_take_highest_evidence_scope(self) -> None:
        classify_paths = _load_classifier().classify_paths
        self.assertEqual(
            classify_paths(
                [
                    "README.md",
                    ".agents/skills/coding/SKILL.md",
                    "runtime/agent_skills_runtime/server.py",
                ]
            ),
            "package",
        )
        self.assertEqual(
            classify_paths(["README.md", ".agents/skills/coding/SKILL.md"]),
            "content",
        )
        self.assertEqual(classify_paths([]), "governance")

    def test_package_jobs_only_run_for_package_scope(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            workflow.count("steps.runtime-scope.outputs.runtime_scope == 'package'"), 4
        )
        self.assertGreaterEqual(
            workflow.count("needs.agent-skills-core.outputs.runtime_scope == 'package'"), 2
        )
        self.assertIn('RUNTIME_SCOPE: ${{ needs.agent-skills-core.outputs.runtime_scope }}', workflow)
        for marker in ("governance|content)", "package)"):
            self.assertIn(marker, workflow)

    def test_skill_ci_compiles_and_smokes_classifier(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(".github/scripts/runtime_package_scope.py", workflow)
        self.assertIn("runtime_package_scope.py --help", workflow)

    def test_maintenance_owns_evidence_boundary_rule(self) -> None:
        maintenance = MAINTENANCE.read_text(encoding="utf-8")
        for marker in (
            "governance / content / package",
            "L3 ≠ 必然三平台打包",
            "正式 Release",
            "每次仍验证 Linux、Windows、macOS",
        ):
            self.assertIn(marker, maintenance)

    def test_release_workflow_still_builds_all_platform_artifacts(self) -> None:
        release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in ("Release Runtime Linux", "Release Runtime Windows", "Release Runtime macOS"):
            self.assertIn(marker, release)
        self.assertNotIn("runtime_package_scope.py", release)


if __name__ == "__main__":
    unittest.main()
