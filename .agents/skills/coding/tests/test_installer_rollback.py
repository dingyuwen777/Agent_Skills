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
    """验证受管 Skill 在切换中途失败时完整恢复当前项和此前已切换项。"""

    def test_swap_restores_all_changed_skills_when_staged_directory_is_missing(self) -> None:
        """第二项切换失败时，应同时恢复当前旧目录和第一项已经被新版本替换的旧目录。"""
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

            old_coding = target / "coding"
            old_coding.mkdir()
            (old_coding / "old.txt").write_text("old coding\n", encoding="utf-8")
            old_review = target / "review"
            old_review.mkdir()
            (old_review / "old.txt").write_text("old review\n", encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                INSTALL._swap_skills(staging, target, backup)

            restored_coding = target / "coding/old.txt"
            restored_review = target / "review/old.txt"
            self.assertTrue(restored_coding.is_file())
            self.assertEqual(restored_coding.read_text(encoding="utf-8"), "old coding\n")
            self.assertTrue(restored_review.is_file())
            self.assertEqual(restored_review.read_text(encoding="utf-8"), "old review\n")
            self.assertFalse((target / "coding/new.txt").exists())
            self.assertFalse((backup / "coding").exists())
            self.assertFalse((backup / "review").exists())


if __name__ == "__main__":
    unittest.main()
