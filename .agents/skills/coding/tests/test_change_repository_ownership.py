"""验证 Coding Change 的仓库归属不会与 Agent_Skills 规则来源混淆。"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
CHANGE_REFERENCE = ROOT / ".agents/skills/coding/references/04_轻量变更管理.md"
MUTATION_REFERENCE = ROOT / ".agents/skills/coding/references/15_规则内容守恒与Skill维护.md"
CODING_SCRIPT = ROOT / ".agents/skills/coding/scripts/coding.py"


def _load_coding_module():
    """按真实脚本路径加载 Coding CLI，直接验证 carrier root 解析行为。"""
    spec = importlib.util.spec_from_file_location("agent_skills_coding_change_ownership", CODING_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 coding.py 测试模块")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChangeRepositoryOwnershipTest(unittest.TestCase):
    """锁定外部项目、自维护和跨仓 Skill Mutation 的 Change Ownership。"""

    def _read(self, path: Path) -> str:
        """读取当前 canonical Markdown 或脚本文本。"""
        return path.read_text(encoding="utf-8")

    def test_change_reference_owns_repository_scoped_change_semantics(self) -> None:
        """Change Owner 必须明确由被治理仓库决定，而不是由 Skill 来源决定。"""
        text = self._read(CHANGE_REFERENCE)
        for marker in (
            "Change Repository Ownership",
            "唯一被治理仓库",
            "规则从哪里加载",
            "谁被修改",
            "相对于该仓库根",
            "Agent_Skills 只是治理规则来源",
            "不得把外部项目 Change 写入 Agent_Skills",
            "不新增 `change_repository`",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_multi_repository_task_uses_separate_governance_units(self) -> None:
        """实际修改多个仓库时，各仓库分别治理，单个 Change 不跨仓承载实现。"""
        change = self._read(CHANGE_REFERENCE)
        mutation = self._read(MUTATION_REFERENCE)
        for marker in (
            "一次任务实际修改多个仓库",
            "每个需要持久施工契约的仓库",
            "不得用一个 Change 跨仓",
            "Issue / PR / Change ID",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, change)
        for marker in (
            "外部项目 Change 不承担 Agent_Skills canonical Skill Mutation",
            "Agent_Skills Change 也不承担外部项目业务实现",
            "分别进入各自仓库的治理闭环",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, mutation)

    def test_change_root_is_scoped_to_explicit_repository_root(self) -> None:
        """现有 Coding CLI 必须始终把默认 carrier 解析到显式传入的 repository root。"""
        coding = _load_coding_module()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            external_repo = base / "external-project"
            agent_skills_repo = base / "Agent_Skills"
            external_repo.mkdir()
            agent_skills_repo.mkdir()

            external_root = coding.resolve_change_root(external_repo, for_create=True)
            agent_skills_root = coding.resolve_change_root(agent_skills_repo, for_create=True)

            self.assertEqual(external_root, external_repo.resolve() / ".agents" / "changes")
            self.assertEqual(agent_skills_root, agent_skills_repo.resolve() / ".agents" / "changes")
            self.assertNotEqual(external_root, agent_skills_root)

    def test_change_schema_does_not_gain_repository_field(self) -> None:
        """本次只澄清 Ownership，不把语义扩大成 coding-change/v1 schema Migration。"""
        coding = _load_coding_module()
        self.assertEqual(coding.CHANGE_SCHEMA, "coding-change/v1")
        self.assertNotIn("change_repository", coding.CHANGE_SCALAR_FIELDS)
        self.assertNotIn("change_repository", coding.CHANGE_LIST_FIELDS)


if __name__ == "__main__":
    unittest.main()
