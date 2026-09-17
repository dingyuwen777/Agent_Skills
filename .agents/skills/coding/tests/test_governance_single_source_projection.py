"""验证治理模板单一 canonical source 与 Runtime first-install 投影。"""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.governance_projection import issue_form_projection_transaction
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PATH = ROOT / ".agents/skills/coding/scripts/governance_contract.py"
CANONICAL_FORMS = ROOT / ".agents/skills/coding/assets/issue-templates"
ROOT_FORMS = ROOT / ".github/ISSUE_TEMPLATE"
SERVER_PATH = ROOT / "runtime/agent_skills_runtime/server.py"
SYNC_PATH = ROOT / "scripts/sync_repository_issue_forms.py"


def _load_module(name: str, path: Path):
    """按真实路径加载治理模块，避免测试复制实现逻辑。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载治理模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = _load_module("single_source_governance_contract", CONTRACT_PATH)
SYNC = _load_module("single_source_governance_sync", SYNC_PATH)


class GovernanceSingleSourceProjectionTests(unittest.TestCase):
    """覆盖 canonical Form、机器 Profile 与 Runtime 首次安装投影的同源性。"""

    @classmethod
    def setUpClass(cls) -> None:
        """构建当前真实 Bundle/Payload，证明 canonical assets 自动进入现有 Project Payload。"""
        cls.bundle = build_bundle(ROOT)
        cls.payload = build_project_payload(ROOT, cls.bundle)
        cls.payload_files = {
            str(entry["path"]): decode_payload_file(entry)
            for entry in cls.payload["files"]
            if isinstance(entry, dict)
        }

    def test_repository_issue_forms_are_exact_canonical_projection(self) -> None:
        """Agent_Skills 自身根 Issue Forms 必须与 Coding canonical assets 原字节一致。"""
        self.assertEqual(CONTRACT.validate_issue_form_projection(ROOT), [])
        for source in sorted(CANONICAL_FORMS.glob("*.yml")):
            self.assertEqual((ROOT_FORMS / source.name).read_bytes(), source.read_bytes())


    def test_source_repository_renderer_is_deterministic_and_repairs_managed_drift(self) -> None:
        """源仓库 renderer 必须只从 canonical source 恢复根受管投影。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".agents/skills/coding/assets/issue-templates"
            shutil.copytree(CANONICAL_FORMS, source)
            target = root / ".github/ISSUE_TEMPLATE"
            target.mkdir(parents=True)
            stale = (CANONICAL_FORMS / "01-requirement.yml").read_text(encoding="utf-8").replace(
                "name: 需求",
                "name: 旧需求",
                1,
            )
            (target / "01-requirement.yml").write_text(stale, encoding="utf-8")

            self.assertIn(
                ".github/ISSUE_TEMPLATE/01-requirement.yml",
                SYNC.projection_drift(root),
            )
            changed = SYNC.sync_projection(root)
            self.assertIn(".github/ISSUE_TEMPLATE/01-requirement.yml", changed)
            self.assertEqual(SYNC.projection_drift(root), [])
            for canonical in sorted(CANONICAL_FORMS.glob("*.yml")):
                self.assertEqual(
                    (target / canonical.name).read_bytes(),
                    canonical.read_bytes(),
                )

    def test_source_repository_renderer_refuses_unmanaged_collision(self) -> None:
        """源仓库 renderer 不能把无受管 marker 的同名文件当生成物覆盖。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".agents/skills/coding/assets/issue-templates"
            shutil.copytree(CANONICAL_FORMS, source)
            target = root / ".github/ISSUE_TEMPLATE"
            target.mkdir(parents=True)
            collision = target / "01-requirement.yml"
            collision.write_text("project-owned\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "拒绝覆盖非受管"):
                SYNC.sync_projection(root)
            self.assertEqual(collision.read_text(encoding="utf-8"), "project-owned\n")

    def test_project_payload_contains_canonical_issue_form_assets(self) -> None:
        """不新增 Payload schema，现有 Coding assets 分发链必须自动携带 canonical Forms。"""
        expected = {
            f"coding/assets/issue-templates/{path.name}"
            for path in CANONICAL_FORMS.glob("*.yml")
        }
        self.assertTrue(expected)
        self.assertTrue(expected.issubset(self.payload_files))
        for relative in expected:
            self.assertEqual(
                self.payload_files[relative],
                (CANONICAL_FORMS / Path(relative).name).read_bytes(),
            )

    def test_validator_profile_changes_with_canonical_form_without_hardcoded_heading_table(self) -> None:
        """修改隔离 canonical Form 后 validator 应按新 title/heading 工作，证明 Profile 来自 Form。"""
        with tempfile.TemporaryDirectory() as directory:
            forms = Path(directory) / "forms"
            shutil.copytree(CANONICAL_FORMS, forms)
            requirement = forms / "01-requirement.yml"
            text = requirement.read_text(encoding="utf-8")
            text = text.replace('title: "[需求] "', 'title: "[产品需求] "')
            text = text.replace("label: 目标\n", "label: 业务目标\n", 1)
            requirement.write_text(text, encoding="utf-8")
            body = """## 问题背景
测试。

## 业务目标
测试。

## 用户 / 使用场景
测试。

## 范围
测试。

## 非目标
测试。

## 验收标准
- [ ] AC1：测试。

## 必须保持不变
测试。

## 上游事实源 / 相关资料
测试。

## 风险与依赖
测试。

## 验证要求
测试。
"""
            self.assertEqual(
                CONTRACT.validate_issue_instance(
                    "[产品需求] 动态 Profile",
                    body,
                    forms_dir=forms,
                ),
                [],
            )

    def test_l3_required_heading_is_read_from_template_marker(self) -> None:
        """L3 额外结构由 Change Template marker 定义，不再由 validator 复制标题文本。"""
        template = (ROOT / ".agents/skills/coding/assets/CHANGE.template.md").read_text(encoding="utf-8")
        self.assertEqual(
            CONTRACT.template_required_second_level_headings(template, "L3"),
            ("备选方案与取舍",),
        )
        changed = template.replace("## 备选方案与取舍", "## L3 决策取舍")
        self.assertEqual(
            CONTRACT.template_required_second_level_headings(changed, "L3"),
            ("L3 决策取舍",),
        )

    def test_first_install_projects_issue_forms_and_keeps_them_after_success(self) -> None:
        """干净首次安装事务成功后，目标仓库根应保留全部 canonical Issue Form 投影。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with issue_form_projection_transaction(target, self.payload) as projected:
                self.assertIn(".github/ISSUE_TEMPLATE/01-requirement.yml", projected)
                for source in CANONICAL_FORMS.glob("*.yml"):
                    self.assertEqual(
                        (target / ".github/ISSUE_TEMPLATE" / source.name).read_bytes(),
                        source.read_bytes(),
                    )
            self.assertTrue((target / ".github/ISSUE_TEMPLATE/config.yml").is_file())

    def test_first_install_refuses_conflicting_project_issue_form_before_writing_others(self) -> None:
        """首次安装不能覆盖项目自有同名 Form；collision 必须在任何新投影写入前失败。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            conflict = target / ".github/ISSUE_TEMPLATE/01-requirement.yml"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("project-owned\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "拒绝覆盖"):
                with issue_form_projection_transaction(target, self.payload):
                    pass
            self.assertEqual(conflict.read_text(encoding="utf-8"), "project-owned\n")
            self.assertFalse((target / ".github/ISSUE_TEMPLATE/02-bug.yml").exists())

    def test_projection_rolls_back_when_downstream_install_fails(self) -> None:
        """投影写入后若后续 install 失败，事务必须恢复首次安装前状态。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with self.assertRaisesRegex(RuntimeError, "downstream"):
                with issue_form_projection_transaction(target, self.payload):
                    self.assertTrue((target / ".github/ISSUE_TEMPLATE/01-requirement.yml").is_file())
                    raise RuntimeError("downstream install failed")
            self.assertFalse((target / ".github/ISSUE_TEMPLATE/01-requirement.yml").exists())

    def test_runtime_install_wraps_project_installer_in_projection_transaction(self) -> None:
        """真实 Runtime install 入口必须把 root projection 与现有 installer 放在同一异常边界中。"""
        server = SERVER_PATH.read_text(encoding="utf-8")
        transaction = server.index("with issue_form_projection_transaction(target, payload):")
        install = server.index("result = install_project(", transaction)
        self.assertLess(transaction, install)


if __name__ == "__main__":
    unittest.main()
