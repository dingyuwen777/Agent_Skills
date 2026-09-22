"""为 Issue/PR creation-time Governance Contract 与统一 Runtime projection 建立 Red 回归。"""

from __future__ import annotations

import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PATH = ROOT / ".agents/skills/coding/scripts/governance_contract.py"
CANONICAL_PR = ROOT / ".agents/skills/coding/assets/PULL_REQUEST_TEMPLATE.md"
SOURCE_SYNC = ROOT / "scripts/sync_repository_governance_assets.py"
LEGACY_SYNC = ROOT / "scripts/sync_repository_issue_forms.py"
SERVER_PATH = ROOT / "runtime/agent_skills_runtime/server.py"
FORMS = ROOT / ".agents/skills/coding/assets/issue-templates"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = _load_module(CONTRACT_PATH, "governance_creation_contract_subject")


class GovernanceCreationContractRedTests(unittest.TestCase):
    """先锁定本次变更必须建立的真实缺口，再进入生产实现。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = build_bundle(ROOT)
        cls.payload = build_project_payload(ROOT, cls.bundle)

    def test_canonical_pr_template_is_project_payload_asset(self) -> None:
        """PR Template 必须成为 Coding canonical asset，并沿现有 Payload 自动分发。"""
        self.assertTrue(CANONICAL_PR.is_file(), "缺少 canonical PULL_REQUEST_TEMPLATE.md")
        managed = {str(entry["path"]) for entry in self.payload["files"]}
        self.assertIn("coding/assets/PULL_REQUEST_TEMPLATE.md", managed)

    def test_issue_validator_exposes_creation_mode(self) -> None:
        """Issue validator 必须显式区分 create/live/closure，不能只做写后宽松检查。"""
        signature = inspect.signature(CONTRACT.validate_issue_instance)
        self.assertIn("mode", signature.parameters)

    def test_pr_validator_is_first_class_machine_contract(self) -> None:
        """PR 必须有与 Issue 同级的 canonical machine validator。"""
        self.assertTrue(hasattr(CONTRACT, "validate_pr_instance"))
        self.assertTrue(hasattr(CONTRACT, "load_pr_profile"))

    def test_required_checkbox_is_part_of_issue_creation_profile(self) -> None:
        """Technical Change 的 required checkbox 不能被 textarea-only Profile 丢失。"""
        profile = CONTRACT.resolve_issue_profile(
            "[技术变更] creation profile",
            forms_dir=FORMS,
        )
        self.assertIn("重复检查", profile.required_headings)
        self.assertEqual(profile.required_headings[0], "重复检查")

    def test_source_repository_sync_is_unified_and_markerless(self) -> None:
        """Source repository 必须使用 Issue+PR 统一 sync，canonical Form 不再携带 ownership marker。"""
        self.assertTrue(SOURCE_SYNC.is_file())
        self.assertFalse(LEGACY_SYNC.exists())
        for path in FORMS.glob("*.yml"):
            data = path.read_bytes()
            self.assertNotIn(b"agent-skills:governance-issue-form", data)

    def test_server_does_not_own_a_second_projection_transaction(self) -> None:
        """Runtime CLI 只调用 install_project；governance projection transaction 属于 installer。"""
        server = SERVER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("issue_form_projection_transaction", server)
        self.assertIn("result = install_project(", server)

    def test_first_install_projects_issue_and_pr_assets_via_installer(self) -> None:
        """干净 first install 必须由 install_project 自身创建根 Issue+PR projections。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-red-fixture")
            install_project(target, self.payload, artifact, release_version="9.9.9")
            self.assertTrue((target / ".github/ISSUE_TEMPLATE/01-requirement.yml").is_file())
            self.assertTrue((target / ".github/PULL_REQUEST_TEMPLATE.md").is_file())

    def test_first_install_rejects_different_existing_pr_before_mutation(self) -> None:
        """PR projection 首次引入时，不同 target 必须 fail closed，不能静默认领。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            pr = target / ".github/PULL_REQUEST_TEMPLATE.md"
            pr.parent.mkdir(parents=True)
            pr.write_text("project-owned\n", encoding="utf-8")
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-red-fixture")
            with self.assertRaises(ValueError):
                install_project(target, self.payload, artifact, release_version="9.9.9")
            self.assertEqual(pr.read_text(encoding="utf-8"), "project-owned\n")
            self.assertFalse((target / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
