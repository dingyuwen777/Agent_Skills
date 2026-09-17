"""验证 PR gate 会重新校验已有 current Active Change，且不扫描 archive 历史。"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[4]
CHECKER_PATH = ROOT / ".github/scripts/check_pr_requirement_source.py"
TEMPLATE_PATH = ROOT / ".agents/skills/coding/assets/CHANGE.template.md"


def _load_checker():
    """加载正式 PR gate，直接测试其 changed-scope 行为。"""
    spec = importlib.util.spec_from_file_location("governance_changed_active_gate", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 PR governance gate")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = _load_checker()


class GovernanceChangedActiveGateTests(unittest.TestCase):
    """锁定新增/修改 Active Change 与历史 archive 的边界。"""

    @staticmethod
    def _git(root: Path, *arguments: str) -> str:
        """执行临时仓库 Git 命令并返回 stdout。"""
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    @staticmethod
    def _write_change(root: Path, change_id: str) -> Path:
        """按当前 canonical 模板创建 L3 current Change fixture。"""
        target_template = root / ".agents/skills/coding/assets/CHANGE.template.md"
        target_template.parent.mkdir(parents=True, exist_ok=True)
        if not target_template.exists():
            shutil.copy2(TEMPLATE_PATH, target_template)
        content = Template(target_template.read_text(encoding="utf-8")).safe_substitute(
            change_id=change_id,
            title="治理复核 fixture",
            level="L3",
            owner="test",
            branch="test/governance-gate",
            created="2026-09-17T16:00:00+08:00",
            updated="2026-09-17T16:00:00+08:00",
            depends_on="[]",
            affected_areas="[governance]",
            affected_paths="[.github]",
            contracts="[coding-change/v1]",
            data_changes="[]",
        )
        path = root / "changes/active" / change_id / "CHANGE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_modified_existing_active_change_is_revalidated(self) -> None:
        """已有 current Active Change 被改坏时，不能利用非新增状态绕过 current Profile。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._git(root, "init", "-b", "main")
            self._git(root, "config", "user.name", "governance-gate")
            self._git(root, "config", "user.email", "governance-gate@example.invalid")
            path = self._write_change(root, "CHG-20260917-160000-existing-current")
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "建立当前Change基线")
            base = self._git(root, "rev-parse", "HEAD")

            path.write_text(
                path.read_text(encoding="utf-8").replace("# 完成审计", "# 其他审计"),
                encoding="utf-8",
            )
            self._git(root, "add", str(path.relative_to(root)))
            self._git(root, "commit", "-m", "模拟宿主破坏Change结构")
            head = self._git(root, "rev-parse", "HEAD")

            with self.assertRaisesRegex(CHECKER.RequirementSourceError, "完成审计"):
                CHECKER.validate_new_changes_since(root, base_sha=base, head_sha=head)

    def test_archive_history_is_not_scanned_by_current_profile(self) -> None:
        """历史 archive 不进入 Active current Profile 扫描，不触发批量迁移。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / ".agents/skills/coding/assets/CHANGE.template.md"
            template.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(TEMPLATE_PATH, template)
            self._git(root, "init", "-b", "main")
            self._git(root, "config", "user.name", "governance-gate")
            self._git(root, "config", "user.email", "governance-gate@example.invalid")
            archive = root / "changes/archive/2026-09/CHG-20260916-legacy/CHANGE.md"
            archive.parent.mkdir(parents=True, exist_ok=True)
            archive.write_text("immutable history\n", encoding="utf-8")
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "建立历史归档基线")
            base = self._git(root, "rev-parse", "HEAD")
            archive.write_text("immutable history fixture\n", encoding="utf-8")
            self._git(root, "add", str(archive.relative_to(root)))
            self._git(root, "commit", "-m", "模拟历史fixture变化")
            head = self._git(root, "rev-parse", "HEAD")

            self.assertEqual(
                CHECKER.validate_new_changes_since(root, base_sha=base, head_sha=head),
                (),
            )


if __name__ == "__main__":
    unittest.main()
