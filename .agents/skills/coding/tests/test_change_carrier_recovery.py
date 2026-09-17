"""验证 Agent_Skills resolved Change carrier 与误放 Change 的原生归档恢复。"""

from __future__ import annotations

import importlib.util
import runpy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[4]
CHECKER_PATH = ROOT / ".github/scripts/check_pr_requirement_source.py"
ARCHIVER_PATH = ROOT / ".github/scripts/archive_change_after_merge.py"
TEMPLATE_PATH = ROOT / ".agents/skills/coding/assets/CHANGE.template.md"
WORKFLOW_PATH = ROOT / ".github/workflows/change-archive.yml"


def _load_checker():
    """加载正式 PR Requirement Source gate。"""
    spec = importlib.util.spec_from_file_location("change_carrier_recovery_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 PR governance gate")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_archiver():
    """加载 repository-native Change Archivist 脚本。"""
    return runpy.run_path(str(ARCHIVER_PATH))


CHECKER = _load_checker()


class ChangeCarrierRecoveryTests(unittest.TestCase):
    """锁定 resolved carrier fail-closed 与 misplaced recovery 边界。"""

    @staticmethod
    def _git(root: Path, *arguments: str) -> str:
        """在临时仓库执行 Git 命令并返回 stdout。"""
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    @staticmethod
    def _change_text(root: Path, change_id: str) -> str:
        """按当前 canonical 模板生成可通过 current Profile 的 L3 Change。"""
        template = root / ".agents/skills/coding/assets/CHANGE.template.md"
        template.parent.mkdir(parents=True, exist_ok=True)
        if not template.exists():
            shutil.copy2(TEMPLATE_PATH, template)
        return Template(template.read_text(encoding="utf-8")).safe_substitute(
            change_id=change_id,
            title="carrier recovery fixture",
            level="L3",
            owner="test",
            branch="test/change-carrier-recovery",
            created="2026-09-17T16:10:47+08:00",
            updated="2026-09-17T16:10:47+08:00",
            depends_on="[]",
            affected_areas="[governance]",
            affected_paths="[.github]",
            contracts="[coding-change/v1]",
            data_changes="[]",
        )

    @staticmethod
    def _write(path: Path, content: str) -> None:
        """创建父目录后写入 UTF-8 fixture。"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_pr_gate_rejects_changed_active_outside_resolved_carrier(self) -> None:
        """仓库已经采用 .agents/changes 时，新增 top-level Active Change 必须 fail closed。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._git(root, "init", "-b", "main")
            self._git(root, "config", "user.name", "carrier-recovery")
            self._git(root, "config", "user.email", "carrier-recovery@example.invalid")

            canonical_id = "CHG-20260917-161100-canonical-baseline"
            canonical = root / ".agents/changes/active" / canonical_id / "CHANGE.md"
            self._write(canonical, self._change_text(root, canonical_id))
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "建立 canonical carrier 基线")
            base = self._git(root, "rev-parse", "HEAD")

            misplaced_id = "CHG-20260917-161101-misplaced-current"
            misplaced = root / "changes/active" / misplaced_id / "CHANGE.md"
            self._write(misplaced, self._change_text(root, misplaced_id))
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "模拟误放 top-level Change")
            head = self._git(root, "rev-parse", "HEAD")

            with self.assertRaisesRegex(CHECKER.RequirementSourceError, "carrier|Carrier"):
                CHECKER.validate_new_changes_since(root, base_sha=base, head_sha=head)

    def test_pr_gate_accepts_active_in_resolved_top_level_target_project_carrier(self) -> None:
        """目标项目只有正式 top-level carrier 时，通用 carrier 能力仍可被 resolver 识别。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._git(root, "init", "-b", "main")
            self._git(root, "config", "user.name", "carrier-recovery")
            self._git(root, "config", "user.email", "carrier-recovery@example.invalid")

            change_id = "CHG-20260917-161102-top-level-project"
            change = root / "changes/active" / change_id / "CHANGE.md"
            self._write(change, self._change_text(root, change_id))
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "建立 top-level carrier 基线")
            base = self._git(root, "rev-parse", "HEAD")

            change.write_text(
                change.read_text(encoding="utf-8").replace(
                    "carrier recovery fixture", "carrier recovery fixture updated"
                ),
                encoding="utf-8",
            )
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "更新 top-level Change")
            head = self._git(root, "rev-parse", "HEAD")

            self.assertEqual(
                CHECKER.validate_new_changes_since(root, base_sha=base, head_sha=head),
                ("changes/active/CHG-20260917-161102-top-level-project/CHANGE.md",),
            )

    def test_archiver_recovers_misplaced_change_into_canonical_archive(self) -> None:
        """已合并误放 Change 必须由同一 Archivist 恢复到 .agents/changes/archive。"""
        module = _load_archiver()
        change_id = "CHG-20260917-161103-misplaced-archive"
        source = f"changes/active/{change_id}/CHANGE.md"
        original = self._change_text(Path(tempfile.gettempdir()), change_id).replace(
            "status: proposed", "status: ready_for_review"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write(root / source, original)

            result = module["archive_change"](
                root,
                changed_paths=[source],
                merged_at="2026-09-17T08:15:00Z",
                expected_source=original,
            )

            target = root / f".agents/changes/archive/2026-09/{change_id}/CHANGE.md"
            self.assertTrue(result.changed)
            self.assertFalse((root / source).exists())
            self.assertTrue(target.is_file())
            archived = target.read_text(encoding="utf-8")
            self.assertIn("status: done", archived)
            self.assertIn("updated: 2026-09-17", archived)
            self.assertEqual(
                archived.replace("status: done", "status: ready_for_review").replace(
                    "updated: 2026-09-17", "updated: 2026-09-17T16:10:47+08:00"
                ),
                original,
            )

    def test_archiver_fails_when_canonical_and_misplaced_changes_are_both_selected(self) -> None:
        """同一 merged PR 同时携带 canonical 与 recovery source 时必须拒绝歧义归档。"""
        module = _load_archiver()
        error = module["ArchiveError"]
        with self.assertRaisesRegex(error, "exactly one"):
            module["select_change"](
                [
                    ".agents/changes/active/CHG-20260917-161104-canonical/CHANGE.md",
                    "changes/active/CHG-20260917-161105-misplaced/CHANGE.md",
                ]
            )

    def test_workflow_keeps_canonical_auto_trigger_and_explicit_recovery_allowlist(self) -> None:
        """自动触发仍只服务 canonical carrier，手工 recovery 只能写 canonical archive。"""
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn('paths: [".agents/changes/active/**"]', workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("changes/active/", workflow)
        self.assertIn(".agents/changes/archive/", workflow)
        self.assertIn("归档 staged diff 超出单一 Change allowlist", workflow)
        self.assertIn("归档 source/target carrier 不满足允许边界", workflow)


if __name__ == "__main__":
    unittest.main()
