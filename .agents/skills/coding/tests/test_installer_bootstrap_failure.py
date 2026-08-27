from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTALL_PATH = ROOT / "scripts/install.py"


def _load_installer():
    """加载根安装器模块，以真实子进程 Bootstrap 失败验证升级回滚。"""
    spec = importlib.util.spec_from_file_location("agent_skills_installer_bootstrap_failure", INSTALL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 scripts/install.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALL = _load_installer()


class InstallerBootstrapFailureTest(unittest.TestCase):
    """验证全部动态正式 Skill 已切换后若目标 AGENTS 校验失败，安装器恢复原受管目录。"""

    def test_install_restores_all_managed_skills_when_bootstrap_fails(self) -> None:
        """坏 managed marker 导致 Bootstrap 失败时，全部动态正式 Skill 都应恢复到安装前内容。"""
        managed_skills = INSTALL._discover_managed_skills(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for skill in managed_skills:
                skill_root = target / ".agents/skills" / skill
                skill_root.mkdir(parents=True)
                (skill_root / "old.txt").write_text(f"old {skill}\n", encoding="utf-8")
            agents = target / "AGENTS.md"
            original_agents = b"# Existing\n<!-- agent-skills:managed:start -->\n"
            agents.write_bytes(original_agents)

            with self.assertRaisesRegex(RuntimeError, "Bootstrap 失败"):
                INSTALL.install_skills(ROOT, target)

            for skill in managed_skills:
                skill_root = target / ".agents/skills" / skill
                self.assertEqual(
                    (skill_root / "old.txt").read_text(encoding="utf-8"),
                    f"old {skill}\n",
                )
                self.assertFalse((skill_root / "SKILL.md").exists())
            self.assertEqual(agents.read_bytes(), original_agents)
            self.assertFalse((target / ".gitignore").exists())


if __name__ == "__main__":
    unittest.main()
