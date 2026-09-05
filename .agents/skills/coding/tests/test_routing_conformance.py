"""对正式 canonical metadata 执行永久 Routing Conformance Benchmark。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import (
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    deserialize_routing_manifest,
    evaluate_route,
    serialize_routing_manifest,
)


ROOT = Path(__file__).resolve().parents[4]


def _case(
    name: str,
    signals: dict[str, list[str]],
    references: list[str],
    skills: list[str],
    risk: str,
    *,
    unknown: list[str] | None = None,
    forbidden_references: list[str] | None = None,
) -> dict[str, object]:
    """构造一条可审查的 conformance fixture。"""
    return {
        "名称": name,
        "信号": signals,
        "未知项": list(unknown or []),
        "预期Skill": skills,
        "最低必需Reference": references,
        "禁止Reference": list(forbidden_references or []),
        "最低风险": risk,
    }


L1_CORE = ["coding.reference.02", "coding.reference.21"]
LIGHT_L2_CORE = ["coding.reference.02", "coding.reference.07"]
GATED_L2_CORE = LIGHT_L2_CORE + ["coding.reference.04", "coding.reference.10", "coding.reference.19"]
REVIEW_CORE = GATED_L2_CORE + ["coding.reference.11", "review.reference.01"]
RUNTIME_CORE = [
    "coding.reference.02",
    "coding.reference.03",
    "coding.reference.04",
    "coding.reference.06",
    "coding.reference.07",
    "coding.reference.10",
    "coding.reference.13",
    "coding.reference.14",
    "coding.reference.19",
]
RUNTIME_V3_UNKNOWN_PROJECT_SHAPE = [
    "coding.reference.01",
    "coding.reference.02",
    "coding.reference.05",
    "coding.reference.07",
    "coding.reference.08",
    "coding.reference.17",
]


CASES = [
    _case("Ad-hoc snippet", {"执行模式": ["实现"], "风险": ["L1"]}, L1_CORE, ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.05", "coding.reference.07", "coding.reference.10", "coding.reference.11", "coding.reference.19", "docs.reference.01", "review.reference.01"]),
    _case("Greenfield", {"执行模式": ["方案"], "项目形态": ["Greenfield"], "阶段": ["仓库初始化"], "风险": ["L2"]}, ["coding.reference.01"] + GATED_L2_CORE, ["coding"], "L2"),
    _case("Fact Recovery", {"执行模式": ["只读分析"], "阶段": ["事实恢复"], "风险": ["L1"]}, ["coding.reference.01", "coding.reference.02"], ["coding"], "L1", forbidden_references=["coding.reference.19", "coding.reference.21"]),
    _case("L1 mechanical", {"执行模式": ["实现"], "风险": ["L1"]}, L1_CORE, ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.05", "coding.reference.07", "coding.reference.10", "coding.reference.11", "coding.reference.19"]),
    _case("L1 known-root Bug", {"执行模式": ["实现"], "阶段": ["缺陷修复"], "风险": ["L1"]}, L1_CORE, ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.05", "coding.reference.07", "coding.reference.10", "coding.reference.11", "coding.reference.19"]),
    _case("L1 unknown-root Bug", {"执行模式": ["诊断", "实现"], "阶段": ["缺陷修复"], "风险": ["L1"]}, L1_CORE + ["coding.reference.05"], ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.07", "coding.reference.10", "coding.reference.11", "coding.reference.19"]),
    _case("L2 Feature", {"执行模式": ["实现"], "阶段": ["功能开发"], "风险": ["L2"], "能力": ["测试"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "coding.reference.19", "coding.reference.21"]),
    _case("Light L2 targeted validation", {"执行模式": ["验证"], "风险": ["L2"]}, LIGHT_L2_CORE, ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "coding.reference.19", "coding.reference.21"]),
    _case("Gated L2", {"执行模式": ["实现"], "风险": ["L2"], "治理": ["要求完成门禁"]}, GATED_L2_CORE, ["coding"], "L2", forbidden_references=["coding.reference.11", "coding.reference.21"]),
    _case("L3 public API", {"执行模式": ["方案", "实现"], "阶段": ["需求设计", "功能开发"], "风险": ["L3"], "范围": ["公共契约", "API"]}, GATED_L2_CORE + ["coding.reference.05", "coding.reference.06"], ["coding"], "L3"),
    _case("Bug", {"执行模式": ["诊断", "实现"], "阶段": ["缺陷修复"], "风险": ["L2"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "coding.reference.19", "coding.reference.21"]),
    _case("Failure / Incident", {"执行模式": ["诊断", "运维"], "阶段": ["故障处置"], "风险": ["L3"]}, GATED_L2_CORE + ["coding.reference.05"], ["coding"], "L3"),
    _case("Refactor", {"执行模式": ["实现"], "阶段": ["重构"], "风险": ["L2"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "coding.reference.19", "coding.reference.21"]),
    _case("Performance", {"执行模式": ["诊断", "实现"], "阶段": ["性能优化"], "风险": ["L2"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "coding.reference.19", "coding.reference.21"]),
    _case("Schema Migration", {"执行模式": ["方案", "实现"], "阶段": ["需求设计"], "风险": ["L3"], "范围": ["Schema", "Migration"]}, GATED_L2_CORE + ["coding.reference.05", "coding.reference.06"], ["coding"], "L3"),
    _case("Frontend", {"执行模式": ["实现"], "项目形态": ["前端Web"], "阶段": ["功能开发"], "风险": ["L2"], "范围": ["前端"]}, LIGHT_L2_CORE + ["coding.reference.05", "coding.reference.08", "coding.reference.17"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "coding.reference.19", "coding.reference.21", "figma.reference.00"]),
    _case("Figma review-only", {"执行模式": ["审查"], "风险": ["L2"], "意图": ["Figma review-only"], "能力": ["Figma"]}, ["figma.reference.00", "figma.reference.01", "figma.reference.06", "figma.reference.07"], ["figma"], "L2", forbidden_references=REVIEW_CORE),
    _case("Figma review-and-fix", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Figma review-and-fix"], "能力": ["Figma"]}, ["figma.reference.00", "figma.reference.01", "figma.reference.06", "figma.reference.07"], ["figma"], "L2", forbidden_references=LIGHT_L2_CORE + ["coding.reference.19", "coding.reference.21"]),
    _case("Figma baseline-ready", {"执行模式": ["方案"], "风险": ["L2"], "意图": ["Figma baseline-ready"], "能力": ["Figma"]}, ["figma.reference.00", "figma.reference.01", "figma.reference.02", "figma.reference.03", "figma.reference.04", "figma.reference.05", "figma.reference.07"], ["figma"], "L2", forbidden_references=LIGHT_L2_CORE + ["coding.reference.19", "coding.reference.21"]),
    _case("Figma → Code", {"执行模式": ["实现"], "项目形态": ["前端Web"], "阶段": ["功能开发"], "风险": ["L2"], "范围": ["前端"], "意图": ["设计转代码"], "能力": ["Figma"]}, LIGHT_L2_CORE + ["coding.reference.05", "coding.reference.08", "coding.reference.17", "figma.reference.00", "figma.reference.01", "figma.reference.02", "figma.reference.03", "figma.reference.05"], ["coding", "figma"], "L2", forbidden_references=["coding.reference.19", "coding.reference.21"]),
    _case("Docs not_applicable", {"执行模式": ["实现"], "阶段": ["功能开发"], "风险": ["L1"]}, L1_CORE, ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.05", "coding.reference.07", "coding.reference.10", "coding.reference.11", "coding.reference.19", "docs.reference.01"]),
    _case("Docs targeted", {"执行模式": ["实现"], "风险": ["L1"], "意图": ["Docs targeted"]}, L1_CORE + ["docs.reference.01", "docs.reference.03"], ["coding", "docs"], "L1", forbidden_references=["coding.reference.19"]),
    _case("Docs full", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Docs full"]}, LIGHT_L2_CORE + ["docs.reference.01", "docs.reference.02", "docs.reference.03"], ["coding", "docs"], "L2", forbidden_references=["coding.reference.19", "coding.reference.21"]),
    _case("Review-only", {"执行模式": ["审查"], "风险": ["L2"], "意图": ["Review-only"]}, REVIEW_CORE + ["review.reference.02"], ["coding", "review"], "L2", forbidden_references=["docs.reference.01", "coding.reference.21"]),
    _case("Review-and-test", {"执行模式": ["审查", "验证"], "风险": ["L2"], "意图": ["Review-and-test"]}, REVIEW_CORE + ["review.reference.02", "review.reference.03"], ["coding", "review"], "L2"),
    _case("Review-and-fix", {"执行模式": ["审查", "实现"], "风险": ["L2"], "意图": ["Review-and-fix"]}, REVIEW_CORE + ["review.reference.02", "review.reference.03"], ["coding", "review"], "L2"),
    _case("Multi-Agent", {"执行模式": ["实现"], "风险": ["L2"], "治理": ["多 Agent"], "能力": ["多 Agent"]}, LIGHT_L2_CORE + ["coding.reference.09", "coding.reference.19"], ["coding"], "L2"),
    _case("Multiple Active Changes", {"执行模式": ["实现"], "风险": ["L2"], "治理": ["多个活动变更"]}, LIGHT_L2_CORE + ["coding.reference.04", "coding.reference.09", "coding.reference.19"], ["coding"], "L2"),
    _case("Dependency Upgrade", {"执行模式": ["实现"], "风险": ["L2"], "工具链": ["已确认"], "意图": ["依赖升级"]}, LIGHT_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L2"),
    _case("CI Workflow Change", {"执行模式": ["实现", "验证"], "风险": ["L3"], "治理": ["CI 变更"]}, GATED_L2_CORE + ["coding.reference.11"], ["coding"], "L3"),
    _case("Git Delivery", {"执行模式": ["Git"], "阶段": ["交付"], "风险": ["L2"], "意图": ["Git 交付"], "能力": ["Git"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L2"),
    _case("PR Ready", {"执行模式": ["Git", "验证"], "阶段": ["交付"], "风险": ["L2"], "意图": ["PR Ready"], "能力": ["Git"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L2"),
    _case("Release", {"执行模式": ["发布"], "阶段": ["交付"], "风险": ["L3"], "意图": ["Release"], "能力": ["Git"], "授权": ["允许发布"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L3"),
    _case("Runtime Install", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Runtime 安装"]}, LIGHT_L2_CORE + ["coding.reference.13"], ["coding"], "L2"),
    _case("Runtime Upgrade", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Runtime 升级"]}, LIGHT_L2_CORE + ["coding.reference.13"], ["coding"], "L2"),
    _case("Runtime Bundle", {"执行模式": ["实现"], "风险": ["L3"], "工具链": ["已确认"], "范围": ["Runtime", "Runtime Bundle", "MCP"], "意图": ["Runtime Bundle"]}, RUNTIME_CORE, ["coding"], "L3"),
    _case("Project Payload", {"执行模式": ["实现"], "风险": ["L3"], "工具链": ["已确认"], "范围": ["Runtime", "Project Payload"], "意图": ["Project Payload"]}, RUNTIME_CORE, ["coding"], "L3"),
    _case("Skill Mutation", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Skill Mutation"]}, GATED_L2_CORE + ["coding.reference.11", "coding.reference.16"], ["coding"], "L2"),
    _case("Security / Permission", {"执行模式": ["方案"], "风险": ["L3"], "意图": ["安全与权限"], "授权": ["允许只读"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L3"),
    _case("CLI package manifest 不推断 Browser/PostgreSQL", {"执行模式": ["只读分析"], "项目形态": ["CLI"], "风险": ["L1"], "工具链": ["JavaScript"]}, ["coding.reference.02", "coding.reference.03"], ["coding"], "L1", forbidden_references=["coding.reference.08", "coding.reference.17", "coding.reference.19", "coding.reference.21", "figma.reference.00"]),
    _case("Backend Python 不推断 FastAPI/PostgreSQL", {"执行模式": ["只读分析"], "项目形态": ["后端服务"], "风险": ["L1"], "工具链": ["Python"]}, ["coding.reference.02", "coding.reference.03", "coding.reference.07", "coding.reference.08"], ["coding"], "L1", forbidden_references=["coding.reference.17", "coding.reference.19", "coding.reference.21", "figma.reference.00"]),
    _case("Design-only Figma 不伪造 API/代码事实", {"风险": ["L1"], "意图": ["Figma review-only"], "能力": ["Figma"], "授权": ["允许只读"]}, ["figma.reference.00", "figma.reference.01", "figma.reference.06", "figma.reference.07"], ["figma"], "L1", forbidden_references=["coding.reference.06", "coding.reference.08", "coding.reference.17", "coding.reference.21"]),
    _case("Unknown facts", {"执行模式": ["方案"], "风险": ["L2"]}, RUNTIME_V3_UNKNOWN_PROJECT_SHAPE, ["coding"], "L2", unknown=["项目形态"], forbidden_references=["coding.reference.14", "docs.reference.01", "figma.reference.00", "review.reference.01"]),
    _case("复杂多条件叠加", {"执行模式": ["实现", "审查", "验证", "Git"], "项目形态": ["前端Web", "全栈应用"], "阶段": ["功能开发", "交付"], "风险": ["L3"], "工具链": ["TypeScript"], "范围": ["前端", "API", "公共契约", "Runtime Bundle"], "意图": ["设计转代码", "Docs full", "Review-and-fix", "Git 交付"], "治理": ["多个活动变更", "要求完成门禁"], "能力": ["Figma", "Git", "测试", "多 Agent"], "授权": ["允许修改项目"]}, RUNTIME_CORE + ["coding.reference.05", "coding.reference.08", "coding.reference.09", "coding.reference.11", "coding.reference.15", "coding.reference.17", "docs.reference.01", "docs.reference.02", "docs.reference.03", "figma.reference.00", "figma.reference.01", "figma.reference.02", "figma.reference.03", "figma.reference.05", "review.reference.01", "review.reference.02", "review.reference.03"], ["coding", "docs", "figma", "review"], "L3"),
]


class RoutingConformanceTest(unittest.TestCase):
    """验证永久任务矩阵没有 required Context 漏失或已知错误命中。"""

    @classmethod
    def setUpClass(cls) -> None:
        """只编译一次正式 canonical metadata，避免每个 case 重复读取。"""
        cls.manifest = build_bundle(ROOT)["路由清单"]

    def test_required_context_is_never_under_disclosed(self) -> None:
        """每个 case 至少满足 Expected Required ⊆ Actual Required，并验证风险、Skill 与 unknown anti-export。"""
        all_reference_ids = {str(entry["标识"]) for entry in self.manifest["引用"]}
        for case in CASES:
            with self.subTest(case=case["名称"]):
                route = {
                    "协议": TASK_ROUTE_PROTOCOL,
                    "信号": case["信号"],
                    "未知项": case["未知项"],
                    "依据": [str(case["名称"])],
                }
                actual = evaluate_route(self.manifest, route)
                actual_references = set(actual["必需Reference"])
                expected = set(case["最低必需Reference"])
                self.assertTrue(expected.issubset(actual_references), expected - actual_references)
                self.assertIn("router", actual["命中Skill"])
                self.assertTrue(set(case["预期Skill"]).issubset(actual["命中Skill"]))
                self.assertEqual(actual["最低风险"], case["最低风险"])
                self.assertFalse(set(case["禁止Reference"]) & actual_references)
                if case["未知项"]:
                    self.assertNotEqual(actual_references, all_reference_ids)

    def test_benchmark_covers_mandatory_task_families(self) -> None:
        """防止后续维护静默删掉任务书要求的 benchmark 家族。"""
        names = {str(case["名称"]) for case in CASES}
        mandatory = {
            "Ad-hoc snippet", "Greenfield", "Fact Recovery", "L1 mechanical", "L1 known-root Bug",
            "L1 unknown-root Bug", "L2 Feature", "Light L2 targeted validation", "Gated L2",
            "L3 public API", "Bug", "Failure / Incident", "Refactor", "Performance", "Schema Migration",
            "Frontend", "Figma review-only", "Figma review-and-fix", "Figma baseline-ready", "Figma → Code",
            "Docs not_applicable", "Docs targeted", "Docs full", "Review-only", "Review-and-test",
            "Review-and-fix", "Multi-Agent", "Multiple Active Changes", "Dependency Upgrade", "CI Workflow Change",
            "Git Delivery", "PR Ready", "Release", "Runtime Install", "Runtime Upgrade", "Runtime Bundle",
            "Project Payload", "Skill Mutation", "Security / Permission", "Unknown facts", "复杂多条件叠加",
        }
        self.assertTrue(mandatory.issubset(names), mandatory - names)

    def test_source_and_runtime_manifests_evaluate_identically(self) -> None:
        """同一 commit 的 Source 编译结果与 Runtime 序列化清单必须对全部 benchmark 同值。"""
        source_manifest = compile_routing(ROOT)
        runtime_manifest = deserialize_routing_manifest(serialize_routing_manifest(self.manifest))
        self.assertEqual(source_manifest, runtime_manifest)
        for case in CASES:
            with self.subTest(case=case["名称"]):
                route = {
                    "协议": TASK_ROUTE_PROTOCOL,
                    "信号": case["信号"],
                    "未知项": case["未知项"],
                    "依据": [str(case["名称"])],
                }
                self.assertEqual(
                    evaluate_route(source_manifest, route),
                    evaluate_route(runtime_manifest, route),
                )


if __name__ == "__main__":
    unittest.main()
