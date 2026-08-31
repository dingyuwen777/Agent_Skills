"""验证薄 ENTRY、正式 Router Skill、旧路由效果和非 Agent 化边界。"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import SKILL_ROUTE_PROTOCOL, TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route
from runtime.agent_skills_runtime.skill_catalog import discover_skills
from scripts.build_runtime import _context_budget

ROOT = Path(__file__).resolve().parents[4]
ENTRY_PATH = ROOT / ".agents/skills/ENTRY.md"
ROUTER_SKILL_PATH = ROOT / ".agents/skills/router/SKILL.md"
LEGACY_ROUTER_PATH = ROOT / ".agents/skills/ROUTER.md"
BASELINE_PATH = Path(__file__).with_name("fixtures") / "router_legacy_baseline.json"
CONTEXT_GROWTH_LIMIT = 16 * 1024
INTENTIONAL_REQUIRED_REMOVALS = {
    "L2 Feature": {"coding.reference.04", "coding.reference.10"},
    "Figma → Code": {"coding.reference.04", "coding.reference.10"},
}


def _routing_block(skill: str, intent: str) -> str:
    """生成最小 Skill 路由元数据，供控制面强制命中测试使用。"""
    payload = {"协议": SKILL_ROUTE_PROTOCOL, "Skill": skill, "触发": {"包含": {"维度": "意图", "取值": [intent]}}}
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _write_skill(root: Path, name: str, intent: str) -> None:
    """写入不含 Reference 的最小正式 Skill。"""
    skill_root = root / ".agents/skills" / name
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(f"---\nname: {name}\ndescription: fixture\n---\n\n" + _routing_block(name, intent) + f"# {name}\n", encoding="utf-8")


class RouterSkillMigrationTest(unittest.TestCase):
    """覆盖 Router Skill 迁移的架构、行为和体积契约。"""

    def test_entry_is_thin_and_router_is_the_only_formal_control_plane(self) -> None:
        """ENTRY 只能导航正式 Router，旧平级 Router 必须消失。"""
        self.assertTrue(ENTRY_PATH.is_file())
        self.assertTrue(ROUTER_SKILL_PATH.is_file())
        self.assertFalse(LEGACY_ROUTER_PATH.exists())
        entry = ENTRY_PATH.read_text(encoding="utf-8")
        self.assertLess(len(entry.encode("utf-8")), 5_000)
        self.assertIn(".agents/skills/router/SKILL.md", entry)
        self.assertIn("项目", entry)
        self.assertIn("无法读取", entry)
        for forbidden in ("agent_skills_route_contract", "agent_skills_submit_route", "agent_skills_load_required_context", "低歧义组合示例", "正式 Skill Catalog", "项目级执行计划"):
            self.assertNotIn(forbidden, entry)
        self.assertIn("router", {skill.name for skill in discover_skills(ROOT)})
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        self.assertEqual(payload["shared_files"], ["ENTRY.md"])
        paths = {str(item["path"]) for item in payload["files"]}
        self.assertIn("ENTRY.md", paths)
        self.assertIn("router/SKILL.md", paths)
        self.assertNotIn("ROUTER.md", paths)

    def test_router_is_forced_before_ordinary_skill_trigger_evaluation(self) -> None:
        """Router 是保留控制面；即使自身普通 trigger 不匹配也必须命中。"""
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            _write_skill(root, "router", "内部控制面")
            _write_skill(root, "coding", "实现功能")
            actual = evaluate_route(compile_routing(root), {"协议": TASK_ROUTE_PROTOCOL, "信号": {"意图": ["实现功能"]}, "未知项": [], "依据": ["控制面测试"]})
            self.assertEqual(actual["命中Skill"], ["coding", "router"])

    def test_legacy_routes_preserve_safety_except_explicit_lightweight_reductions(self) -> None:
        """历史基线继续防欠披露；只有本次明确批准的轻量 L2 重型 Context 可减少。"""
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        bundle = build_bundle(ROOT)
        manifest = bundle["路由清单"]
        budget = _context_budget(ROOT, bundle)
        reference_sizes = {str(entry["id"]): int(entry["size"]) for entry in bundle["references"]}
        for case in baseline["cases"]:
            with self.subTest(case=case["name"]):
                actual = evaluate_route(manifest, {"协议": TASK_ROUTE_PROTOCOL, "信号": case["signals"], "未知项": case["unknown"], "依据": [case["name"]]})
                actual_skills = set(actual["命中Skill"])
                actual_references = set(actual["必需Reference"])
                self.assertTrue(set(case["matched_skills"]).issubset(actual_skills))
                self.assertIn("router", actual_skills)
                expected = set(case["required_references"]) - INTENTIONAL_REQUIRED_REMOVALS.get(case["name"], set())
                self.assertTrue(expected.issubset(actual_references), expected - actual_references)
                self.assertFalse(set(case["forbidden_references"]) & actual_references)
                self.assertEqual(actual["最低风险"], case["minimum_risk"])
                current_bytes = int(budget["entry_bytes"]) + sum(int(budget["skill_core_bytes"][skill]) for skill in actual_skills) + sum(reference_sizes[reference] for reference in actual_references)
                self.assertLessEqual(current_bytes, int(case["context_bytes"]) + CONTEXT_GROWTH_LIMIT)

    def test_light_l2_reference_context_is_materially_smaller_than_legacy_baseline(self) -> None:
        """轻量 L2 必须通过少加载重型 Reference 获得净减负，而不是只放宽总体积预算。"""
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        case = next(item for item in baseline["cases"] if item["name"] == "L2 Feature")
        bundle = build_bundle(ROOT)
        actual = evaluate_route(bundle["路由清单"], {"协议": TASK_ROUTE_PROTOCOL, "信号": case["signals"], "未知项": [], "依据": ["light L2 context regression"]})
        reference_sizes = {str(entry["id"]): int(entry["size"]) for entry in bundle["references"]}
        current_reference_bytes = sum(reference_sizes[reference] for reference in actual["必需Reference"])
        legacy_reference_bytes = sum(reference_sizes[reference] for reference in case["required_references"] if reference in reference_sizes)
        self.assertLess(current_reference_bytes, legacy_reference_bytes)
        self.assertNotIn("coding.reference.10", actual["必需Reference"])

    def test_router_has_anti_agent_boundary_and_runtime_exposes_no_executor(self) -> None:
        """同时检查文字边界和 Python 公共表面，避免仅凭关键词宣称非 Agent 化。"""
        router = ROUTER_SKILL_PATH.read_text(encoding="utf-8")
        for marker in ("## Anti-Agent Boundary", "只输出", "不生成项目级执行计划", "不创建子 Agent", "不接管专业 Skill"):
            self.assertIn(marker, router)
        routing_path = ROOT / "runtime/agent_skills_runtime/routing.py"
        tree = ast.parse(routing_path.read_text(encoding="utf-8"))
        imported_modules = {alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names}
        public_functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")}
        self.assertFalse({"subprocess", "threading", "multiprocessing"} & imported_modules)
        self.assertFalse({name for name in public_functions if any(word in name for word in ("plan", "execute", "agent"))})
        result_keys = set(evaluate_route(build_bundle(ROOT)["路由清单"], {"协议": TASK_ROUTE_PROTOCOL, "信号": {"执行模式": ["实现"], "风险": ["L1"]}, "未知项": [], "依据": ["输出边界测试"]}))
        self.assertEqual(result_keys, {"路由摘要", "命中Skill", "必需Reference", "最低风险", "存在未知项"})

    def test_coding_no_longer_claims_cross_skill_router_ownership(self) -> None:
        """Coding 保留研发能力，但不得继续声明所有任务必经或跨 Skill 主流程 Owner。"""
        coding = (ROOT / ".agents/skills/coding/SKILL.md").read_text(encoding="utf-8")
        router = ROUTER_SKILL_PATH.read_text(encoding="utf-8")
        for forbidden in ("跨 Skill 主流程", "核心锚点", "每个研发任务的固定入口"):
            self.assertNotIn(forbidden, coding)
        self.assertIn("唯一的跨 Skill", router)
        for preserved in ("Red-Green-Refactor", "Validation Matrix", "Completion Audit", "Git"):
            self.assertIn(preserved, coding)

    def test_runtime_handoff_uses_current_reference_owners(self) -> None:
        """Router 的 Runtime Handoff 必须指向当前 ref12/ref13，不得保留已漂移的 ref14 编号。"""
        router = ROUTER_SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("Bootstrap/managed block 进入 Coding ref12", router)
        self.assertIn("Runtime/分发边界在此基础上进入 Coding ref13", router)
        self.assertIn("Coding ref12/ref13 + Runtime 实现", router)
        self.assertNotIn("Coding ref13/ref14", router)


if __name__ == "__main__":
    unittest.main()
