"""验证 Coding Change 的仓库归属不会与 Agent_Skills 规则来源混淆。"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
CHANGE_REFERENCE = ROOT / ".agents/skills/coding/references/04_轻量变更管理.md"
OWNERSHIP_REFERENCE = ROOT / ".agents/skills/coding/references/24_Change仓库归属与Carrier.md"
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

    def _required_references(self, signals: dict[str, list[str]]) -> set[str]:
        """使用真实 canonical metadata 计算给定任务事实的 required References。"""
        result = evaluate_route(
            build_bundle(ROOT)["路由清单"],
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["Change Repository Ownership 渐进披露回归"],
            },
        )
        return set(result["必需Reference"])

    def test_change_reference_routes_to_detailed_repository_owner(self) -> None:
        """ref04 保留 Change 入口，但详细仓库/Carrier 规则必须下沉到窄 Owner。"""
        change = self._read(CHANGE_REFERENCE)
        self.assertIn("24_Change仓库归属与Carrier.md", change)
        self.assertIn("唯一详细 Owner", change)
        self.assertNotIn("## Change Repository Ownership", change)

    def test_detailed_reference_owns_repository_scoped_change_semantics(self) -> None:
        """详细 Owner 必须明确由被治理仓库决定，而不是由 Skill 来源决定。"""
        text = self._read(OWNERSHIP_REFERENCE)
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

    def test_detailed_reference_owns_second_precision_id_and_legacy_compatibility(self) -> None:
        """Change ID 的新建格式与历史兼容策略只能由详细 Owner 定义。"""
        text = self._read(OWNERSHIP_REFERENCE)
        self.assertIn("CHG-YYYYMMDD-HHMMSS-kebab-case", text)
        self.assertIn("CHG-YYYYMMDD-kebab-case", text)
        self.assertIn("历史", text)
        self.assertIn("`--slug`", text)

    def test_multi_repository_task_uses_separate_governance_units(self) -> None:
        """实际修改多个仓库时，各仓库分别治理，单个 Change 不跨仓承载实现。"""
        ownership = self._read(OWNERSHIP_REFERENCE)
        mutation = self._read(MUTATION_REFERENCE)
        for marker in (
            "一次任务实际修改多个仓库",
            "每个需要持久施工契约的仓库",
            "不得用一个 Change 跨仓",
            "Issue / PR / Change ID",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, ownership)
        for marker in (
            "外部项目 Change 不承担 Agent_Skills canonical Skill Mutation",
            "Agent_Skills Change 也不承担外部项目业务实现",
            "分别进入各自仓库的治理闭环",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, mutation)

    def test_detailed_owner_loads_only_for_persistent_change_facts(self) -> None:
        """详细 carrier 规则只由 L3/持久治理事实加载，不重新膨胀普通 Review/Git 路由。"""
        for signals in (
            {"执行模式": ["实现"], "风险": ["L3"]},
            {"执行模式": ["实现"], "风险": ["L2"], "治理": ["要求变更记录"]},
        ):
            with self.subTest(signals=signals):
                self.assertIn("coding.reference.25", self._required_references(signals))

        for signals in (
            {"执行模式": ["审查"], "意图": ["Review-only"], "风险": ["L2"]},
            {
                "执行模式": ["Git"],
                "意图": ["Git 交付"],
                "能力": ["Git"],
                "阶段": ["交付"],
                "风险": ["L2"],
            },
        ):
            with self.subTest(signals=signals):
                self.assertNotIn("coding.reference.25", self._required_references(signals))

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
