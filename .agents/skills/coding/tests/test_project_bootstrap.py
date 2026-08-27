from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CODING_PATH = ROOT / ".agents/skills/coding/scripts/coding.py"
INSTALL_PATH = ROOT / "scripts/install.py"


def _load_module(name: str, path: Path):
    """从指定路径加载模块，便于在测试中直接调用公开安装与 Bootstrap 行为。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODING = _load_module("coding_project_bootstrap", CODING_PATH)


class ProjectBootstrapTest(unittest.TestCase):
    """验证目标项目 AGENTS Overlay 与本地缓存忽略规则的安全、幂等行为。"""

    def test_bootstrap_creates_agents_for_greenfield_without_inventing_stack(self) -> None:
        """空项目应创建可用 AGENTS 初版，并明确禁止把技术示例反推成项目事实。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / ".agents/skills/coding"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Coding\n", encoding="utf-8")

            result = CODING.bootstrap_project(root)

            content = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(result["agents"], "created")
            self.assertIn("<!-- agent-skills:managed:start -->", content)
            self.assertIn(".agents/skills/coding/SKILL.md", content)
            self.assertIn(".agents/skills/review/SKILL.md", content)
            self.assertIn(".agents/skills/docs/SKILL.md", content)
            self.assertIn("不能单凭文件名推出 React、FastAPI、PostgreSQL", content)
            self.assertNotIn("本项目使用 FastAPI", content)
            self.assertNotIn("数据库：PostgreSQL", content)
            self.assertNotIn("前端框架：React", content)
            self.assertNotIn("前端框架：Vue", content)
            self.assertIn("初始化扫描未发现可稳定列出的项目规则", content)
            self.assertIn(".agents/project-context.json", (root / ".gitignore").read_text(encoding="utf-8"))

    def test_bootstrap_preserves_existing_agents_bytes_outside_managed_block(self) -> None:
        """已有 AGENTS 原文必须逐字保留，只允许在末尾追加 Agent Skills 自管区。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / ".agents/skills/coding"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Coding\n", encoding="utf-8")
            original = b"# Existing Rules\r\n\r\n- Keep this exact.  \r\n"
            (root / "AGENTS.md").write_bytes(original)

            result = CODING.bootstrap_project(root)
            updated = (root / "AGENTS.md").read_bytes()

            self.assertEqual(result["agents"], "updated")
            self.assertTrue(updated.startswith(original))
            self.assertIn(b"<!-- agent-skills:managed:start -->", updated)
            self.assertIn(b"<!-- agent-skills:managed:end -->", updated)
            self.assertNotIn(b"\n", updated.replace(b"\r\n", b""))

    def test_bootstrap_updates_only_existing_managed_block(self) -> None:
        """已有完整 managed block 时只替换自管区，marker 前后用户文本必须保持原样。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / ".agents/skills/coding"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Coding\n", encoding="utf-8")
            prefix = b"# Existing\n\nuser-before\n"
            suffix = b"\nuser-after\n"
            existing = (
                prefix
                + b"<!-- agent-skills:managed:start -->\nOLD BLOCK\n<!-- agent-skills:managed:end -->"
                + suffix
            )
            (root / "AGENTS.md").write_bytes(existing)

            CODING.bootstrap_project(root)
            updated = (root / "AGENTS.md").read_bytes()

            self.assertTrue(updated.startswith(prefix))
            self.assertTrue(updated.endswith(suffix))
            self.assertNotIn(b"OLD BLOCK", updated)
            self.assertEqual(updated.count(b"<!-- agent-skills:managed:start -->"), 1)
            self.assertEqual(updated.count(b"<!-- agent-skills:managed:end -->"), 1)

    def test_bootstrap_is_idempotent(self) -> None:
        """连续执行 Bootstrap 不得重复追加 AGENTS managed block 或缓存 ignore。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / ".agents/skills/coding"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Coding\n", encoding="utf-8")

            CODING.bootstrap_project(root)
            first_agents = (root / "AGENTS.md").read_bytes()
            first_ignore = (root / ".gitignore").read_bytes()
            result = CODING.bootstrap_project(root)

            self.assertEqual(result["agents"], "unchanged")
            self.assertEqual(result["gitignore"], "unchanged")
            self.assertEqual((root / "AGENTS.md").read_bytes(), first_agents)
            self.assertEqual((root / ".gitignore").read_bytes(), first_ignore)

    def test_bootstrap_rejects_broken_or_duplicate_managed_markers(self) -> None:
        """managed marker 缺失、逆序或重复时必须拒绝猜测性覆盖。"""
        invalid_documents = [
            b"# Rules\n<!-- agent-skills:managed:start -->\n",
            b"# Rules\n<!-- agent-skills:managed:end -->\n",
            b"<!-- agent-skills:managed:end -->\n<!-- agent-skills:managed:start -->\n",
            (
                b"<!-- agent-skills:managed:start -->\n"
                b"<!-- agent-skills:managed:end -->\n"
                b"<!-- agent-skills:managed:start -->\n"
                b"<!-- agent-skills:managed:end -->\n"
            ),
        ]
        for content in invalid_documents:
            with self.subTest(content=content):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    skill = root / ".agents/skills/coding"
                    skill.mkdir(parents=True)
                    (skill / "SKILL.md").write_text("# Coding\n", encoding="utf-8")
                    agents = root / "AGENTS.md"
                    agents.write_bytes(content)

                    with self.assertRaisesRegex(ValueError, "managed marker"):
                        CODING.bootstrap_project(root)
                    self.assertEqual(agents.read_bytes(), content)

    def test_bootstrap_preserves_existing_gitignore_and_does_not_duplicate_rule(self) -> None:
        """已有 .gitignore 其他规则必须保留，已有缓存忽略规则时不得重复写入。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / ".agents/skills/coding"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Coding\n", encoding="utf-8")
            original = "node_modules/\n/.agents/project-context.json\n*.log\n"
            (root / ".gitignore").write_text(original, encoding="utf-8")

            CODING.bootstrap_project(root)
            updated = (root / ".gitignore").read_text(encoding="utf-8")

            self.assertEqual(updated, original)
            self.assertEqual(updated.count("project-context.json"), 1)

    def test_bootstrap_requires_installed_coding_skill(self) -> None:
        """目标项目没有 Coding Skill 时不得生成一个会指向不存在入口的 AGENTS。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(FileNotFoundError, "coding/SKILL.md"):
                CODING.bootstrap_project(root)
            self.assertFalse((root / "AGENTS.md").exists())


class InstallerTest(unittest.TestCase):
    """验证安装器动态管理全部正式 Skill，并与目标项目 Bootstrap 形成真实文件系统链路。"""

    @classmethod
    def setUpClass(cls) -> None:
        """在安装器文件已实现后加载模块，避免测试导入时隐藏缺失文件错误。"""
        cls.install = _load_module("agent_skills_installer", INSTALL_PATH)

    def test_install_copies_all_formal_skills_and_bootstraps_target(self) -> None:
        """首次安装应复制全部动态正式 Skill、建立 AGENTS，同时保留目标 `.agents` 自有内容。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            custom = target / ".agents/custom.txt"
            change = target / ".agents/changes/active/keep.txt"
            custom.parent.mkdir(parents=True)
            change.parent.mkdir(parents=True)
            custom.write_text("keep custom\n", encoding="utf-8")
            change.write_text("keep change\n", encoding="utf-8")

            result = self.install.install_skills(ROOT, target)
            expected_skills = self.install._discover_managed_skills(ROOT)

            self.assertEqual(result["skills"], expected_skills)
            for skill in result["skills"]:
                self.assertTrue((target / ".agents/skills" / skill / "SKILL.md").is_file())
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertIn(".agents/skills/coding/SKILL.md", (target / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertEqual(custom.read_text(encoding="utf-8"), "keep custom\n")
            self.assertEqual(change.read_text(encoding="utf-8"), "keep change\n")
            self.assertFalse((target / ".agents/changes/archive").exists())
            self.assertFalse((target / ".agents/project-context.json").exists())

    def test_install_upgrade_is_idempotent_and_keeps_existing_agents_text(self) -> None:
        """重复安装用于升级时不得重复 managed block，也不得覆盖 AGENTS 中用户维护的原文。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            original = "# My Project\n\n- user-owned-rule\n"
            (target / "AGENTS.md").write_text(original, encoding="utf-8")

            self.install.install_skills(ROOT, target)
            first = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.install.install_skills(ROOT, target)
            second = (target / "AGENTS.md").read_text(encoding="utf-8")

            self.assertTrue(first.startswith(original))
            self.assertEqual(second, first)
            self.assertEqual(second.count("<!-- agent-skills:managed:start -->"), 1)
            self.assertEqual(second.count("<!-- agent-skills:managed:end -->"), 1)

    def test_install_replaces_managed_skill_without_deleting_other_skill_directories(self) -> None:
        """升级正式 Skill 可以替换旧内容，但不得清理目标项目其他 `.agents/skills` 目录。"""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            old_coding = target / ".agents/skills/coding/obsolete.txt"
            custom_skill = target / ".agents/skills/project-custom/SKILL.md"
            old_coding.parent.mkdir(parents=True)
            custom_skill.parent.mkdir(parents=True)
            old_coding.write_text("old\n", encoding="utf-8")
            custom_skill.write_text("custom\n", encoding="utf-8")

            self.install.install_skills(ROOT, target)

            self.assertFalse(old_coding.exists())
            self.assertEqual(custom_skill.read_text(encoding="utf-8"), "custom\n")


if __name__ == "__main__":
    unittest.main()
