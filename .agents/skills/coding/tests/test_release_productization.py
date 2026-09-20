from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BUILD_RUNTIME_PATH = ROOT / "scripts/build_runtime.py"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
RUNTIME_PACKAGE_WORKFLOW = ROOT / ".github/workflows/skill-tests.yml"
RUNTIME_PLATFORM_SMOKE = ROOT / "scripts/runtime_platform_smoke.py"


class ReleaseProductizationTest(unittest.TestCase):
    """验证正式 Release identity 不依赖磁盘 manifest sidecar，且三平台证据不降级。"""

    def test_builder_machine_output_carries_identity_without_manifest_sidecar(self) -> None:
        source = BUILD_RUNTIME_PATH.read_text(encoding="utf-8")
        for marker in (
            '"artifact_sha256"', '"release_version"', '"source_commit"',
            '"integrity_fingerprint"', '"python_version"', '"bundle_schema"',
            '"bundle_version"', '"task_route_protocol"', '"routing_manifest_protocol"',
            '"mcp_tool_contract_protocol"', '"project_payload_schema"', '"source_digest"',
            '"routing_digest"', '"payload_digest"',
        ):
            self.assertIn(marker, source)
        for removed in ("RELEASE_IDENTITY_SCHEMA", "install_manifest_schema", "manifest_path", ".manifest.json"):
            self.assertNotIn(removed, source)
        self.assertIn('sys.stdout.reconfigure(encoding="utf-8")', source)
        self.assertIn('sys.stderr.reconfigure(encoding="utf-8")', source)

    def test_release_workflow_uses_job_outputs_for_cross_platform_identity(self) -> None:
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("GITHUB_OUTPUT", workflow)
        for output_name in (
            "release_version", "source_commit", "integrity_fingerprint", "artifact_sha256",
            "python_version", "bundle_schema", "bundle_version", "task_route_protocol",
            "routing_manifest_protocol", "mcp_tool_contract_protocol", "project_payload_schema",
            "source_digest", "routing_digest", "payload_digest",
        ):
            self.assertGreaterEqual(workflow.count(output_name), 4, output_name)
        for platform in ("LINUX", "WINDOWS", "MACOS"):
            self.assertIn(f"{platform}_INTEGRITY_FINGERPRINT", workflow)
            self.assertIn(f"{platform}_ARTIFACT_SHA256", workflow)
            self.assertIn(f"{platform}_SOURCE_COMMIT", workflow)
        self.assertIn("identity != reference", workflow)
        self.assertIn("sha256sum", workflow)
        self.assertIn("check_sha", workflow)
        self.assertNotIn("linux.manifest.json", workflow)
        self.assertNotIn("windows.manifest.json", workflow)
        self.assertNotIn("macos.manifest.json", workflow)
        self.assertIn("*.manifest.json", workflow)
        self.assertNotIn("install_manifest_schema", workflow)
        self.assertNotIn("agent-skills-runtime-release-identity/v1", workflow)

    def test_shared_platform_smoke_verifies_builder_identity_and_no_sidecars(self) -> None:
        """Builder identity/hash/sidecar/install-state 由 shared smoke 单一实现证明。"""
        workflow = RUNTIME_PACKAGE_WORKFLOW.read_text(encoding="utf-8")
        source = RUNTIME_PLATFORM_SMOKE.read_text(encoding="utf-8")
        self.assertIn("python scripts/runtime_platform_smoke.py", workflow)
        for marker in (
            "artifact_sha256",
            "integrity_fingerprint",
            "expected_python_version",
            "agent-skills-runtime-install-state/v1",
            "__install-state",
            "agent-skills-install.json",
            "*.manifest.json",
            "hashlib.sha256",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("install_manifest_schema", source)

    def test_release_is_manual_main_only_and_rejects_existing_identity(self) -> None:
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch", workflow)
        self.assertIn('test "${GITHUB_REF}" = "refs/heads/main"', workflow)
        self.assertIn('test "$(git rev-parse HEAD)" = "${GITHUB_SHA}"', workflow)
        self.assertIn('gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/${TAG}"', workflow)
        self.assertIn('gh release view "${TAG}"', workflow)
        self.assertIn("tag 已存在，拒绝覆盖", workflow)
        self.assertIn("Release 已存在，拒绝覆盖", workflow)
        self.assertRegex(workflow, r"\^v\[0-9\]\+\\\.\[0-9\]\+\\\.\[0-9\]\+")

    def test_release_builds_real_platform_artifacts_and_uses_shared_smoke(self) -> None:
        """Release productization 只证明真实三平台构建与 shared smoke；ZIP surface 由专门 Owner 负责。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "Release Runtime Linux",
            "Release Runtime Windows",
            "Release Runtime macOS",
            "windows-2025",
            "macos-15",
            "ubuntu-24.04",
            "scripts/build_runtime.py",
            "python scripts/runtime_platform_smoke.py",
            "release-runtime-linux",
            "release-runtime-windows",
            "release-runtime-macos",
        ):
            self.assertIn(marker, workflow)

    def test_ci_and_release_share_runtime_platform_smoke_owner(self) -> None:
        """CI 与正式 Release 都必须复用同一 artifact smoke 实现，避免平台 shell 漂移。"""
        self.assertTrue(RUNTIME_PLATFORM_SMOKE.is_file(), "缺少共享 Runtime platform smoke")
        source = RUNTIME_PLATFORM_SMOKE.read_text(encoding="utf-8")
        for marker in (
            "status",
            "self-test",
            "runtime_mcp_smoke.py",
            "__install-state",
            "verify_no_args",
        ):
            self.assertIn(marker, source)

        ci = RUNTIME_PACKAGE_WORKFLOW.read_text(encoding="utf-8")
        release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python scripts/runtime_platform_smoke.py", ci)
        self.assertGreaterEqual(release.count("python scripts/runtime_platform_smoke.py"), 3)

    def test_release_draft_then_publish_gate_remains_atomic(self) -> None:
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        draft_index = workflow.index("- name: Create verified draft Release")
        publish_index = workflow.index("- name: Publish GitHub Release")
        cleanup_index = workflow.index("- name: Cleanup failed draft Release")
        self.assertLess(draft_index, publish_index)
        self.assertLess(publish_index, cleanup_index)
        draft_block = workflow[draft_index:publish_index]
        publish_block = workflow[publish_index:cleanup_index]
        self.assertIn("gh release create", draft_block)
        self.assertIn("--draft", draft_block)
        self.assertIn("--target \"${GITHUB_SHA}\"", draft_block)
        self.assertIn("gh release upload", draft_block)
        self.assertIn("--json isDraft --jq '.isDraft'", draft_block)
        self.assertIn('gh release edit "${RELEASE_TAG}" --draft=false', publish_block)
        self.assertIn('test "$(git rev-list -n 1 "${RELEASE_TAG}")" = "${GITHUB_SHA}"', publish_block)
        self.assertIn("if: failure()", workflow[cleanup_index - 120 :])

    def test_actions_are_pinned_to_commit_shas(self) -> None:
        for path in (RELEASE_WORKFLOW, RUNTIME_PACKAGE_WORKFLOW):
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped.startswith("uses:"):
                    continue
                ref = stripped.split("uses:", 1)[1].strip().split()[0]
                self.assertRegex(ref, r"@[0-9a-f]{40}$", f"未固定 Action commit：{ref}")

    def test_builder_version_pattern_accepts_semver_and_rejects_v_prefix(self) -> None:
        source = BUILD_RUNTIME_PATH.read_text(encoding="utf-8")
        pattern_match = re.search(r'VERSION_PATTERN = re\.compile\(r"([^"]+)"\)', source)
        self.assertIsNotNone(pattern_match)
        pattern = re.compile(pattern_match.group(1))
        for value in ("3.0.0", "3.0.0-rc.1", "3.0.0+build.5"):
            self.assertIsNotNone(pattern.fullmatch(value), value)
        self.assertIsNone(pattern.fullmatch("v3.0.0"))


if __name__ == "__main__":
    unittest.main()
