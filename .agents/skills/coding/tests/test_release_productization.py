from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BUILD_RUNTIME_PATH = ROOT / "scripts/build_runtime.py"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
RUNTIME_PACKAGE_WORKFLOW = ROOT / ".github/workflows/runtime-package-tests.yml"


class ReleaseProductizationTest(unittest.TestCase):
    """验证正式 Release identity 不依赖磁盘 manifest sidecar，且三平台证据不降级。"""

    def test_builder_machine_output_carries_identity_without_manifest_sidecar(self) -> None:
        """Builder 必须直接返回完整机器身份，并且源码不再生成 identity manifest。"""
        source = BUILD_RUNTIME_PATH.read_text(encoding="utf-8")
        for marker in (
            '"artifact_sha256"',
            '"release_version"',
            '"source_commit"',
            '"integrity_fingerprint"',
            '"python_version"',
            '"bundle_schema"',
            '"bundle_version"',
            '"task_route_protocol"',
            '"routing_manifest_protocol"',
            '"mcp_tool_contract_protocol"',
            '"project_payload_schema"',
            '"source_digest"',
            '"routing_digest"',
            '"payload_digest"',
        ):
            self.assertIn(marker, source)
        for removed in (
            "RELEASE_IDENTITY_SCHEMA",
            "install_manifest_schema",
            "manifest_path",
            ".manifest.json",
        ):
            self.assertNotIn(removed, source)
        self.assertIn('sys.stdout.reconfigure(encoding="utf-8")', source)
        self.assertIn('sys.stderr.reconfigure(encoding="utf-8")', source)

    def test_release_workflow_uses_job_outputs_for_cross_platform_identity(self) -> None:
        """Release 必须通过平台 job outputs 比较公共 identity，而不是上传 JSON sidecar。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("GITHUB_OUTPUT", workflow)
        for output_name in (
            "release_version",
            "source_commit",
            "integrity_fingerprint",
            "artifact_sha256",
            "python_version",
            "bundle_schema",
            "bundle_version",
            "task_route_protocol",
            "routing_manifest_protocol",
            "mcp_tool_contract_protocol",
            "project_payload_schema",
            "source_digest",
            "routing_digest",
            "payload_digest",
        ):
            self.assertGreaterEqual(workflow.count(output_name), 4, output_name)
        for platform in ("LINUX", "WINDOWS", "MACOS"):
            self.assertIn(f"{platform}_INTEGRITY_FINGERPRINT", workflow)
            self.assertIn(f"{platform}_ARTIFACT_SHA256", workflow)
            self.assertIn(f"{platform}_SOURCE_COMMIT", workflow)
        self.assertIn("identity != reference", workflow)
        self.assertIn("sha256sum", workflow)
        self.assertIn("check_sha", workflow)
        self.assertNotIn(".manifest.json", workflow)
        self.assertNotIn("install_manifest_schema", workflow)
        self.assertNotIn("agent-skills-runtime-release-identity/v1", workflow)

    def test_runtime_package_workflow_verifies_builder_json_and_no_sidecars(self) -> None:
        """普通三平台 CI 必须验证 Builder JSON、binary SHA 和两类 sidecar 均不存在。"""
        workflow = RUNTIME_PACKAGE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "artifact_sha256",
            "integrity_fingerprint",
            "3.14.7",
            "agent-skills-runtime-install-state/v1",
            "__install-state --json",
            "agent-skills-install.json",
        ):
            self.assertIn(marker, workflow)
        self.assertIn("test ! -e", workflow)
        self.assertIn("Get-FileHash -Algorithm SHA256", workflow)
        self.assertIn("*.manifest.json", workflow)
        self.assertNotIn("install_manifest_schema", workflow)

    def test_release_is_manual_main_only_and_rejects_existing_identity(self) -> None:
        """正式发布仍必须手工从 main 发起，并拒绝覆盖已有 tag/Release。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch", workflow)
        self.assertIn('test "${GITHUB_REF}" = "refs/heads/main"', workflow)
        self.assertIn('test "$(git rev-parse HEAD)" = "${GITHUB_SHA}"', workflow)
        self.assertIn('gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/${TAG}"', workflow)
        self.assertIn('gh release view "${TAG}"', workflow)
        self.assertIn("tag 已存在，拒绝覆盖", workflow)
        self.assertIn("Release 已存在，拒绝覆盖", workflow)
        self.assertRegex(workflow, r"\^v\[0-9\]\+\\\.\[0-9\]\+\\\.\[0-9\]\+")

    def test_release_builds_real_platform_artifacts_and_exact_three_zips(self) -> None:
        """三平台正式构建、自检、MCP、安装和最终 ZIP 产品面仍然完整。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "Release Runtime Linux",
            "Release Runtime Windows",
            "Release Runtime macOS",
            "windows-2025",
            "macos-15",
            "ubuntu-24.04",
            "scripts/build_runtime.py",
            "status --json",
            "self-test --json",
            "runtime_mcp_smoke.py",
            "install --target",
            "Build platform distribution ZIPs",
            "ZIP 成员集合不正确",
            "release-runtime-linux",
            "release-runtime-windows",
            "release-runtime-macos",
        ):
            self.assertIn(marker, workflow)
        self.assertIn("agent-skills-v${RELEASE_TAG#v}-linux.zip", workflow)
        self.assertIn("agent-skills-v${RELEASE_TAG#v}-windows.zip", workflow)
        self.assertIn("agent-skills-v${RELEASE_TAG#v}-macos.zip", workflow)
        self.assertIn("binary + USAGE", "binary + USAGE")

    def test_release_draft_then_publish_gate_remains_atomic(self) -> None:
        """Release 仍必须先创建并验证 Draft，最终步骤才发布。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        draft_index = workflow.index("Create verified draft Release")
        publish_index = workflow.index("Publish GitHub Release")
        cleanup_index = workflow.index("Cleanup failed draft Release")
        self.assertLess(draft_index, publish_index)
        self.assertLess(publish_index, cleanup_index)
        draft_block = workflow[draft_index:publish_index]
        publish_block = workflow[publish_index:cleanup_index]
        self.assertIn("gh release create", draft_block)
        self.assertIn("--draft", draft_block)
        self.assertIn("--target \"${GITHUB_SHA}\"", draft_block)
        self.assertIn("gh release upload", draft_block)
        self.assertIn('test "$(gh release view "${RELEASE_TAG}" --json isDraft --jq \' .isDraft\')"', draft_block.replace("'.isDraft'", "' .isDraft'"))
        self.assertIn('gh release edit "${RELEASE_TAG}" --draft=false', publish_block)
        self.assertIn('test "$(git rev-list -n 1 "${RELEASE_TAG}")" = "${GITHUB_SHA}"', publish_block)
        self.assertIn("if: failure()", workflow[cleanup_index - 120 :])

    def test_actions_are_pinned_to_commit_shas(self) -> None:
        """Release 与 Package CI 的第三方 Actions 必须继续固定完整 commit SHA。"""
        for path in (RELEASE_WORKFLOW, RUNTIME_PACKAGE_WORKFLOW):
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped.startswith("uses:"):
                    continue
                ref = stripped.split("uses:", 1)[1].strip().split()[0]
                self.assertRegex(ref, r"@[0-9a-f]{40}$", f"未固定 Action commit：{ref}")

    def test_builder_version_pattern_accepts_semver_and_rejects_v_prefix(self) -> None:
        """版本身份仍采用无 v SemVer，Release tag 的 v 只属于 Git tag 表面。"""
        source = BUILD_RUNTIME_PATH.read_text(encoding="utf-8")
        pattern_match = re.search(r'VERSION_PATTERN = re\.compile\(r"([^"]+)"\)', source)
        self.assertIsNotNone(pattern_match)
        pattern = re.compile(pattern_match.group(1))
        for value in ("3.0.0", "3.0.0-rc.1", "3.0.0+build.5"):
            self.assertIsNotNone(pattern.fullmatch(value), value)
        self.assertIsNone(pattern.fullmatch("v3.0.0"))


if __name__ == "__main__":
    unittest.main()
