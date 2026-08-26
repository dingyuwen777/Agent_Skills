from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTALL_PATH = ROOT / "scripts/install.py"


def _load_installer():
    """加载根安装器模块，以真实临时文件系统验证内部切换失败边界。"""
    spec = importlib.util.spec_from_file_location("agent_skills_installer_rollback", INSTALL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 scripts/install.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALL = _load_installer()


class InstallerRollbackTest(unittest.TestCase):
    """验证受管 Skill 在切换中途失败时不会丢失当前正在替换的旧目录。"""

    def test_swap_restores_current_skill_when_staged_directory_is_missing(self) -> None:
        """旧目录已移到 backup 后若新目录切换失败，应立即恢复该旧目录再向上抛错。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staging = root / "staging"
            target = root / "target"
            backup = root / "backup"
            staging.mkdir()
            target.mkdir()
            backup.mkdir()

            staged_coding = staging / "coding"
            staged_coding.mkdir()
            (staged_coding / "new.txt").write_text("new coding\n", encoding="utf-8")

            old_review = target / "review"
            old_review.mkdir()
            (old_review / "old.txt").write_text("old review\n", encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                INSTALL._swap_skills(staging, target, backup)

            restored = target / "review/old.txt"
            self.assertTrue(restored.is_file())
            self.assertEqual(restored.read_text(encoding="utf-8"), "old review\n")
            self.assertFalse((backup / "review").exists())


if __name__ == "__main__":
    unittest.main()
