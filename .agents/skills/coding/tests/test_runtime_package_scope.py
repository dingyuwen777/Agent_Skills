from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
WORKFLOW = ROOT / ".github/workflows/runtime-package-tests.yml"
CLASSIFIER = ROOT / ".github/scripts/runtime_package_scope.py"
MAINTENANCE = ROOT / ".agents/MAINTENANCE.md"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"


class RuntimePackageScopePolicyTest(unittest.TestCase):
    """验证普通 CI 按证据边界分级，而正式 Release 保持全平台验证。"""

    def test_runtime_package_scope_has_dedicated_classifier(self) -> None:
        """Scope 判定必须有可单测的唯一 classifier，不能继续只靠内联宽泛 glob。"""
        self.assertTrue(CLASSIFIER.is_file(), "缺少 Runtime Package scope classifier")
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("runtime_scope", workflow)
        self.assertIn(".github/scripts/runtime_package_scope.py", workflow)
        self.assertNotIn("runtime/*|runtime/**/*", workflow)

    def test_runtime_package_jobs_only_run_for_package_scope(self) -> None:
        """三平台 binary jobs 必须只由 package 档触发，governance/content 都应跳过。"""
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(workflow.count("needs.scope.outputs.runtime_scope == 'package'"), 3)
        self.assertIn('RUNTIME_SCOPE: ${{ needs.scope.outputs.runtime_scope }}', workflow)
        for marker in ('governance)', 'content)', 'package)'):
            self.assertIn(marker, workflow)

    def test_maintenance_owns_evidence_boundary_rule(self) -> None:
        """维护规则必须明确 L3 与三平台打包解耦，并保留 Release 全平台责任。"""
        maintenance = MAINTENANCE.read_text(encoding="utf-8")
        for marker in (
            "governance / content / package",
            "L3 ≠ 必然三平台打包",
            "正式 Release",
            "每次仍验证 Linux、Windows、macOS",
        ):
            self.assertIn(marker, maintenance)

    def test_release_workflow_still_builds_all_platform_artifacts(self) -> None:
        """普通 CI 的 scope 优化不得改变正式 Release 三平台 artifact 证明责任。"""
        release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in ("Release Runtime Linux", "Release Runtime Windows", "Release Runtime macOS"):
            self.assertIn(marker, release)
        self.assertNotIn("runtime_package_scope.py", release)


if __name__ == "__main__":
    unittest.main()
