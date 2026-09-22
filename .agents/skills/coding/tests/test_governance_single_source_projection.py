"""验证 Issue/PR governance canonical source、markerless projection 与统一 installer transaction。"""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest.mock import patch

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime import governance_projection as PROJECTION
from runtime.agent_skills_runtime import project_installer as INSTALLER
from runtime.agent_skills_runtime.governance_projection import (
    PROJECT_SIDE_PROJECTION_DRIFT,
    apply_governance_projection_plan,
    build_governance_projection_plan,
)
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PATH = ROOT / ".agents/skills/coding/scripts/governance_contract.py"
CANONICAL_FORMS = ROOT / ".agents/skills/coding/assets/issue-templates"
CANONICAL_PR = ROOT / ".agents/skills/coding/assets/PULL_REQUEST_TEMPLATE.md"
ROOT_FORMS = ROOT / ".github/ISSUE_TEMPLATE"
ROOT_PR = ROOT / ".github/PULL_REQUEST_TEMPLATE.md"
SYNC_PATH = ROOT / "scripts/sync_repository_governance_assets.py"
LEGACY_SYNC_PATH = ROOT / "scripts/sync_repository_issue_forms.py"


def _load_module(name: str, path: Path):
    """按真实路径加载治理模块，避免测试复制生产实现。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载治理模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = _load_module("single_source_governance_contract", CONTRACT_PATH)
SYNC = _load_module("single_source_governance_sync", SYNC_PATH)


class GovernanceSingleSourceProjectionTests(unittest.TestCase):
    """覆盖 source projection、Payload、markerless upgrade/removal 与 installer rollback。"""

    @classmethod
    def setUpClass(cls) -> None:
        """构建当前真实 Bundle/Payload，作为 governance projection 测试基线。"""
        cls.bundle = build_bundle(ROOT)
        cls.payload = build_project_payload(ROOT, cls.bundle)
        cls.payload_files = {
            str(entry["path"]): decode_payload_file(entry)
            for entry in cls.payload["files"]
            if isinstance(entry, dict)
        }

    def _write_previous_source_and_projection(
        self,
        target: Path,
        source: PurePosixPath,
        content: bytes,
    ) -> None:
        """写入 previous canonical source 与相同 root projection fixture。"""
        source_path = target / ".agents/skills" / Path(source.as_posix())
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(content)
        target_relative = PROJECTION._target_for_source(source)
        if target_relative is None:
            self.fail(f"fixture source 没有 projection target：{source}")
        projection = target / Path(target_relative.as_posix())
        projection.parent.mkdir(parents=True, exist_ok=True)
        projection.write_bytes(content)

    def _current_issue_sources(self) -> tuple[PurePosixPath, ...]:
        """返回当前 canonical Issue Form 在 Project Payload 中的 source 路径。"""
        return tuple(
            PurePosixPath(f"coding/assets/issue-templates/{path.name}")
            for path in sorted(CANONICAL_FORMS.glob("*.yml"))
        )

    def test_repository_issue_and_pr_assets_are_exact_canonical_projection(self) -> None:
        """Agent_Skills 根 Issue/PR 文件都只是 canonical assets 的原字节 projection。"""
        self.assertEqual(CONTRACT.validate_governance_projection(ROOT), [])
        for source in sorted(CANONICAL_FORMS.glob("*.yml")):
            self.assertEqual((ROOT_FORMS / source.name).read_bytes(), source.read_bytes())
        self.assertEqual(ROOT_PR.read_bytes(), CANONICAL_PR.read_bytes())

    def test_source_repository_sync_repairs_markerless_drift_and_removes_stale_issue_form(self) -> None:
        """源仓库根 .github ownership 来自 canonical mapping，不依赖文件 marker。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".agents/skills/coding/assets/issue-templates"
            source.mkdir(parents=True)
            for canonical in CANONICAL_FORMS.glob("*.yml"):
                shutil.copy2(canonical, source / canonical.name)
            pr = root / ".agents/skills/coding/assets/PULL_REQUEST_TEMPLATE.md"
            pr.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(CANONICAL_PR, pr)

            target = root / ".github/ISSUE_TEMPLATE"
            target.mkdir(parents=True)
            (target / "01-requirement.yml").write_text("drift\n", encoding="utf-8")
            (target / "stale.yml").write_text("stale\n", encoding="utf-8")
            root_pr = root / ".github/PULL_REQUEST_TEMPLATE.md"
            root_pr.write_text("old\n", encoding="utf-8")

            self.assertIn(".github/PULL_REQUEST_TEMPLATE.md", SYNC.projection_drift(root))
            changed = SYNC.sync_projection(root)
            self.assertIn(".github/PULL_REQUEST_TEMPLATE.md", changed)
            self.assertIn(".github/ISSUE_TEMPLATE/stale.yml", changed)
            self.assertFalse((target / "stale.yml").exists())
            self.assertEqual(SYNC.projection_drift(root), [])

    def test_source_sync_rejects_non_directory_projection_parent(self) -> None:
        """源仓库 sync 也必须在写入前拒绝 .github 等非目录祖先。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".agents/skills/coding/assets/issue-templates"
            source.mkdir(parents=True)
            for canonical in CANONICAL_FORMS.glob("*.yml"):
                shutil.copy2(canonical, source / canonical.name)
            pr = root / ".agents/skills/coding/assets/PULL_REQUEST_TEMPLATE.md"
            pr.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(CANONICAL_PR, pr)
            (root / ".github").write_text("project-owned-file\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "父路径必须是目录"):
                SYNC.projection_drift(root)

            self.assertEqual((root / ".github").read_text(encoding="utf-8"), "project-owned-file\n")

    def test_legacy_marker_sync_script_is_removed(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        self.assertFalse(LEGACY_SYNC_PATH.exists())

    def test_project_payload_contains_canonical_issue_and_pr_assets(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        expected = {
            f"coding/assets/issue-templates/{path.name}"
            for path in CANONICAL_FORMS.glob("*.yml")
        }
        expected.add("coding/assets/PULL_REQUEST_TEMPLATE.md")
        self.assertTrue(expected.issubset(self.payload_files))
        self.assertEqual(
            self.payload_files["coding/assets/PULL_REQUEST_TEMPLATE.md"],
            CANONICAL_PR.read_bytes(),
        )

    def test_validator_profile_changes_with_canonical_form_without_hardcoded_heading_table(self) -> None:
        """Issue Profile 必须从 Form 顺序恢复 required checkbox + textarea。"""
        with tempfile.TemporaryDirectory() as directory:
            forms = Path(directory) / "forms"
            shutil.copytree(CANONICAL_FORMS, forms)
            requirement = forms / "01-requirement.yml"
            text = requirement.read_text(encoding="utf-8")
            text = text.replace('title: "[需求] "', 'title: "[产品需求] "')
            text = text.replace("label: 目标\n", "label: 业务目标\n", 1)
            requirement.write_text(text, encoding="utf-8")
            profile = CONTRACT.resolve_issue_profile("[产品需求] 动态 Profile", forms_dir=forms)
            self.assertEqual(profile.required_headings[0], "重复检查")
            self.assertIn("业务目标", profile.required_headings)

    def test_pr_profile_is_read_from_canonical_template(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        profile = CONTRACT.load_pr_profile()
        self.assertEqual(profile.required_headings[0], "Requirement Source")
        self.assertEqual(profile.required_headings[-1], "Git / 发布")
        changed = CANONICAL_PR.read_text(encoding="utf-8").replace(
            "## 目标",
            "## 交付目标",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            template = Path(directory) / "PULL_REQUEST_TEMPLATE.md"
            template.write_text(changed, encoding="utf-8")
            self.assertIn("交付目标", CONTRACT.load_pr_profile(template).required_headings)

    def test_first_install_projects_issue_and_pr_assets_via_installer(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-v1")
            result = install_project(target, self.payload, artifact, release_version="9.9.9")
            self.assertTrue((target / ".github/ISSUE_TEMPLATE/01-requirement.yml").is_file())
            self.assertEqual(
                (target / ".github/PULL_REQUEST_TEMPLATE.md").read_bytes(),
                CANONICAL_PR.read_bytes(),
            )
            self.assertIn(".github/PULL_REQUEST_TEMPLATE.md", result["governance_projections"])

    def test_first_install_equal_projection_is_safe_adoption(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            target_issue = target / ".github/ISSUE_TEMPLATE"
            target_issue.mkdir(parents=True)
            for source in CANONICAL_FORMS.glob("*.yml"):
                shutil.copy2(source, target_issue / source.name)
            target_pr = target / ".github/PULL_REQUEST_TEMPLATE.md"
            shutil.copy2(CANONICAL_PR, target_pr)
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-v1")

            result = install_project(target, self.payload, artifact, release_version="9.9.9")

            self.assertEqual(result["ownership_source"], "first-install")
            self.assertEqual(result["governance_projections"], [])
            self.assertEqual(target_pr.read_bytes(), CANONICAL_PR.read_bytes())

    def test_projection_parent_file_conflict_fails_before_installer_writes(self) -> None:
        """root projection 的非目录祖先必须在任何 managed/Runtime 写入前完成 preflight fail-closed。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            (target / ".github").write_text("project-owned-file\n", encoding="utf-8")
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-v1")

            with patch.object(INSTALLER, "_atomic_write", wraps=INSTALLER._atomic_write) as writer:
                with self.assertRaisesRegex(ValueError, "父路径必须是目录"):
                    install_project(target, self.payload, artifact, release_version="9.9.9")

            writer.assert_not_called()
            self.assertFalse((target / ".agents").exists())
            self.assertEqual((target / ".github").read_text(encoding="utf-8"), "project-owned-file\n")

    def test_first_install_rejects_different_existing_pr_before_mutation(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            conflict = target / ".github/PULL_REQUEST_TEMPLATE.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("project-owned\n", encoding="utf-8")
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-v1")

            with self.assertRaisesRegex(ValueError, "GOVERNANCE_PROJECTION_COLLISION"):
                install_project(target, self.payload, artifact, release_version="9.9.9")

            self.assertEqual(conflict.read_text(encoding="utf-8"), "project-owned\n")
            self.assertFalse((target / "AGENTS.md").exists())
            self.assertFalse((target / ".agents/runtime").exists())

    def test_marker_based_previous_issue_upgrades_to_markerless_by_previous_bytes(self) -> None:
        """旧 marker 只是 previous bytes 内容，不参与 ownership 判定。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            source = PurePosixPath("coding/assets/issue-templates/01-requirement.yml")
            incoming = self.payload_files[source.as_posix()]
            old = b"# agent-skills:governance-issue-form:v1\n" + incoming
            self._write_previous_source_and_projection(target, source, old)
            previous_state = {"managed_files": [source.as_posix()]}

            plan = build_governance_projection_plan(target, self.payload, previous_state)
            apply_governance_projection_plan(target, plan)

            self.assertEqual(
                (target / ".github/ISSUE_TEMPLATE/01-requirement.yml").read_bytes(),
                incoming,
            )

    def test_managed_projection_drift_fails_closed_and_keeps_project_bytes(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            source = PurePosixPath("coding/assets/issue-templates/01-requirement.yml")
            old = b"previous-canonical\n"
            self._write_previous_source_and_projection(target, source, old)
            projection = target / ".github/ISSUE_TEMPLATE/01-requirement.yml"
            projection.write_bytes(b"project-drift\n")
            previous_state = {"managed_files": [source.as_posix()]}

            with self.assertRaisesRegex(ValueError, PROJECT_SIDE_PROJECTION_DRIFT):
                build_governance_projection_plan(target, self.payload, previous_state)

            self.assertEqual(projection.read_bytes(), b"project-drift\n")

    def test_new_pr_projection_on_existing_install_create_adopt_or_fail_closed(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        issue_sources = self._current_issue_sources()
        previous_state = {"managed_files": [source.as_posix() for source in issue_sources]}

        def prepare_target(root: Path) -> None:
            """为新 PR projection 场景准备旧版本只认领 Issue Forms 的目标项目。"""
            for source in issue_sources:
                content = self.payload_files[source.as_posix()]
                self._write_previous_source_and_projection(root, source, content)

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            prepare_target(target)
            plan = build_governance_projection_plan(target, self.payload, previous_state)
            self.assertTrue(any(op.target == PurePosixPath(".github/PULL_REQUEST_TEMPLATE.md") for op in plan))

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            prepare_target(target)
            pr = target / ".github/PULL_REQUEST_TEMPLATE.md"
            pr.write_bytes(CANONICAL_PR.read_bytes())
            plan = build_governance_projection_plan(target, self.payload, previous_state)
            self.assertFalse(any(op.target == PurePosixPath(".github/PULL_REQUEST_TEMPLATE.md") for op in plan))

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            prepare_target(target)
            pr = target / ".github/PULL_REQUEST_TEMPLATE.md"
            pr.write_text("project-owned\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "GOVERNANCE_PROJECTION_COLLISION"):
                build_governance_projection_plan(target, self.payload, previous_state)
            self.assertEqual(pr.read_text(encoding="utf-8"), "project-owned\n")

    def test_removed_previous_projection_deletes_equal_target_but_rejects_drift(self) -> None:
        """验证 governance canonical source、projection ownership 或 rollback 的对应契约。"""
        source = PurePosixPath("coding/assets/PULL_REQUEST_TEMPLATE.md")
        old = b"previous-pr\n"
        previous_state = {"managed_files": [source.as_posix()]}

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self._write_previous_source_and_projection(target, source, old)
            with patch.object(PROJECTION, "_incoming_governance_sources", return_value={}):
                plan = build_governance_projection_plan(target, self.payload, previous_state)
            self.assertEqual([op.action for op in plan], ["delete"])
            apply_governance_projection_plan(target, plan)
            self.assertFalse((target / ".github/PULL_REQUEST_TEMPLATE.md").exists())

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self._write_previous_source_and_projection(target, source, old)
            projection = target / ".github/PULL_REQUEST_TEMPLATE.md"
            projection.write_bytes(b"project-drift\n")
            with patch.object(PROJECTION, "_incoming_governance_sources", return_value={}):
                with self.assertRaisesRegex(ValueError, PROJECT_SIDE_PROJECTION_DRIFT):
                    build_governance_projection_plan(target, self.payload, previous_state)
            self.assertEqual(projection.read_bytes(), b"project-drift\n")

    def test_installer_failure_preserves_preexisting_empty_governance_directories(self) -> None:
        """回滚只能删除本事务新建的目录，不能删除安装前已经存在的空 .github 目录。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            preexisting_issue_dir = target / ".github/ISSUE_TEMPLATE"
            preexisting_issue_dir.mkdir(parents=True)
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-v1")
            agents_path = (target / "AGENTS.md").resolve()
            original_atomic_write = INSTALLER._atomic_write
            failed = False

            def controlled_atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
                """在 governance projection 已应用后制造 Host 写失败，随后允许正常 rollback。"""
                nonlocal failed
                if Path(path).resolve() == agents_path and not failed:
                    failed = True
                    raise OSError("fixture host write failure with preexisting directories")
                original_atomic_write(path, content, mode)

            with patch.object(INSTALLER, "_atomic_write", side_effect=controlled_atomic_write):
                with self.assertRaisesRegex(OSError, "preexisting directories"):
                    install_project(target, self.payload, artifact, release_version="9.9.9")

            self.assertTrue((target / ".github").is_dir())
            self.assertTrue(preexisting_issue_dir.is_dir())
            self.assertEqual(list(preexisting_issue_dir.iterdir()), [])

    def test_installer_failure_after_governance_apply_rolls_back_all_projection_bytes(self) -> None:
        """后续 Host 配置写失败时，root governance、managed files 与 Runtime 都回滚。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            artifact = root / "agent-skills"
            artifact.write_bytes(b"runtime-v1")
            agents_path = (target / "AGENTS.md").resolve()
            original_atomic_write = INSTALLER._atomic_write
            failed = False

            def controlled_atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
                """在指定 Host 写入点制造失败并允许后续 rollback 正常恢复。"""
                nonlocal failed
                if Path(path).resolve() == agents_path and not failed:
                    failed = True
                    raise OSError("fixture host write failure after governance projection")
                original_atomic_write(path, content, mode)

            with patch.object(INSTALLER, "_atomic_write", side_effect=controlled_atomic_write):
                with self.assertRaisesRegex(OSError, "host write failure"):
                    install_project(target, self.payload, artifact, release_version="9.9.9")

            self.assertFalse((target / ".github/PULL_REQUEST_TEMPLATE.md").exists())
            self.assertFalse((target / ".github/ISSUE_TEMPLATE/01-requirement.yml").exists())
            self.assertFalse((target / ".agents/runtime/agent-skills").exists())
            self.assertFalse((target / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
