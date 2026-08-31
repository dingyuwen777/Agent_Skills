"""对正式 canonical metadata 执行永久 Routing Conformance Benchmark。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, deserialize_routing_manifest, evaluate_route, serialize_routing_manifest

ROOT = Path(__file__).resolve().parents[4]


def _case(name: str, signals: dict[str, list[str]], references: list[str], skills: list[str], risk: str, *, unknown: list[str] | None = None, forbidden_references: list[str] | None = None) -> dict[str, object]:
    """构造一条可审查的 conformance fixture。"""
    return {"名称": name, "信号": signals, "未知项": list(unknown or []), "预期Skill": skills, "最低必需Reference": references, "禁止Reference": list(forbidden_references or []), "最低风险": risk}


LIGHT_L2_CORE = ["coding.reference.02", "coding.reference.07", "coding.reference.19"]
GATED_L2_CORE = LIGHT_L2_CORE + ["coding.reference.04", "coding.reference.10"]
REVIEW_CORE = GATED_L2_CORE + ["coding.reference.11", "review.reference.01"]
RUNTIME_CORE = ["coding.reference.02", "coding.reference.03", "coding.reference.04", "coding.reference.06", "coding.reference.07", "coding.reference.10", "coding.reference.13", "coding.reference.14", "coding.reference.19"]

CASES = [
    _case("Ad-hoc snippet", {"执行模式": ["实现"], "风险": ["L1"]}, ["coding.reference.02", "coding.reference.19"], ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "docs.reference.01", "review.reference.01"]),
    _case("Greenfield", {"执行模式": ["方案"], "项目形态": ["Greenfield"], "阶段": ["仓库初始化"], "风险": ["L2"]}, ["coding.reference.01"] + GATED_L2_CORE, ["coding"], "L2"),
    _case("Fact Recovery", {"执行模式": ["只读分析"], "阶段": ["事实恢复"], "风险": ["L1"]}, ["coding.reference.01", "coding.reference.02", "coding.reference.19"], ["coding"], "L1"),
    _case("L1 mechanical", {"执行模式": ["实现"], "风险": ["L1"]}, ["coding.reference.02", "coding.reference.19"], ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11"]),
    _case("L2 Feature", {"执行模式": ["实现"], "阶段": ["功能开发"], "风险": ["L2"], "能力": ["测试"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11"]),
    _case("Light L2 targeted validation", {"执行模式": ["验证"], "风险": ["L2"]}, LIGHT_L2_CORE, ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11"]),
    _case("Gated L2", {"执行模式": ["实现"], "风险": ["L2"], "治理": ["要求完成门禁"]}, GATED_L2_CORE, ["coding"], "L2", forbidden_references=["coding.reference.11"]),
    _case("L3 public API", {"执行模式": ["方案", "实现"], "阶段": ["需求设计", "功能开发"], "风险": ["L3"], "范围": ["公共契约", "API"]}, GATED_L2_CORE + ["coding.reference.05", "coding.reference.06"], ["coding"], "L3"),
    _case("Bug", {"执行模式": ["诊断", "实现"], "阶段": ["缺陷修复"], "风险": ["L2"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11"]),
    _case("Failure / Incident", {"执行模式": ["诊断", "运维"], "阶段": ["故障处置"], "风险": ["L3"]}, GATED_L2_CORE + ["coding.reference.05"], ["coding"], "L3"),
    _case("Refactor", {"执行模式": ["实现"], "阶段": ["重构"], "风险": ["L2"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11"]),
    _case("Performance", {"执行模式": ["诊断", "实现"], "阶段": ["性能优化"], "风险": ["L2"]}, LIGHT_L2_CORE + ["coding.reference.05"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11"]),
    _case("Schema Migration", {"执行模式": ["方案", "实现"], "阶段": ["需求设计"], "风险": ["L3"], "范围": ["Schema", "Migration"]}, GATED_L2_CORE + ["coding.reference.05", "coding.reference.06"], ["coding"], "L3"),
    _case("Frontend", {"执行模式": ["实现"], "项目形态": ["前端Web"], "阶段": ["功能开发"], "风险": ["L2"], "范围": ["前端"]}, LIGHT_L2_CORE + ["coding.reference.05", "coding.reference.08", "coding.reference.17"], ["coding"], "L2", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "figma.reference.00"]),
    _case("Figma review-only", {"执行模式": ["审查"], "风险": ["L2"], "意图": ["Figma review-only"], "能力": ["Figma"]}, REVIEW_CORE + ["figma.reference.00", "figma.reference.01", "figma.reference.06", "figma.reference.07"], ["coding", "figma", "review"], "L2"),
    _case("Figma review-and-fix", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Figma review-and-fix"], "能力": ["Figma"]}, LIGHT_L2_CORE + ["figma.reference.00", "figma.reference.01", "figma.reference.06", "figma.reference.07"], ["coding", "figma"], "L2"),
    _case("Figma baseline-ready", {"执行模式": ["方案"], "风险": ["L2"], "意图": ["Figma baseline-ready"], "能力": ["Figma"]}, LIGHT_L2_CORE + ["figma.reference.00", "figma.reference.01", "figma.reference.02", "figma.reference.03", "figma.reference.04", "figma.reference.05", "figma.reference.07"], ["coding", "figma"], "L2"),
    _case("Figma → Code", {"执行模式": ["实现"], "项目形态": ["前端Web"], "阶段": ["功能开发"], "风险": ["L2"], "范围": ["前端"], "意图": ["设计转代码"], "能力": ["Figma"]}, LIGHT_L2_CORE + ["coding.reference.05", "coding.reference.08", "coding.reference.17", "figma.reference.00", "figma.reference.01", "figma.reference.02", "figma.reference.03", "figma.reference.05"], ["coding", "figma"], "L2"),
    _case("Docs not_applicable", {"执行模式": ["实现"], "阶段": ["功能开发"], "风险": ["L1"]}, ["coding.reference.02", "coding.reference.05", "coding.reference.19"], ["coding"], "L1", forbidden_references=["coding.reference.04", "coding.reference.10", "coding.reference.11", "docs.reference.01"]),
    _case("Docs targeted", {"执行模式": ["实现"], "风险": ["L1"], "意图": ["Docs targeted"]}, ["coding.reference.02", "coding.reference.19", "docs.reference.01", "docs.reference.03"], ["coding", "docs"], "L1"),
    _case("Docs full", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Docs full"]}, LIGHT_L2_CORE + ["docs.reference.01", "docs.reference.02", "docs.reference.03"], ["coding", "docs"], "L2"),
    _case("Review-only", {"执行模式": ["审查"], "风险": ["L2"], "意图": ["Review-only"]}, REVIEW_CORE + ["review.reference.02"], ["coding", "review"], "L2", forbidden_references=["docs.reference.01"]),
    _case("Review-and-test", {"执行模式": ["审查", "验证"], "风险": ["L2"], "意图": ["Review-and-test"]}, REVIEW_CORE + ["review.reference.02", "review.reference.03"], ["coding", "review"], "L2"),
    _case("Review-and-fix", {"执行模式": ["审查", "实现"], "风险": ["L2"], "意图": ["Review-and-fix"]}, REVIEW_CORE + ["review.reference.02", "review.reference.03"], ["coding", "review"], "L2"),
    _case("Multi-Agent", {"执行模式": ["实现"], "风险": ["L2"], "治理": ["多 Agent"], "能力": ["多 Agent"]}, LIGHT_L2_CORE + ["coding.reference.09"], ["coding"], "L2"),
    _case("Multiple Active Changes", {"执行模式": ["实现"], "风险": ["L2"], "治理": ["多个活动变更"]}, LIGHT_L2_CORE + ["coding.reference.04", "coding.reference.09"], ["coding"], "L2"),
    _case("Dependency Upgrade", {"执行模式": ["实现"], "风险": ["L2"], "工具链": ["已确认"], "意图": ["依赖升级"]}, LIGHT_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L2"),
    _case("CI Workflow Change", {"执行模式": ["实现", "验证"], "风险": ["L3"], "治理": ["CI 变更"]}, GATED_L2_CORE, ["coding"], "L3"),
    _case("Git Delivery", {"执行模式": ["Git"], "阶段": ["交付"], "风险": ["L2"], "意图": ["Git 交付"], "能力": ["Git"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L2"),
    _case("PR Ready", {"执行模式": ["Git", "验证"], "阶段": ["交付"], "风险": ["L2"], "意图": ["PR Ready"], "能力": ["Git"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L2"),
    _case("Release", {"执行模式": ["发布"], "阶段": ["交付"], "风险": ["L3"], "意图": ["Release"], "能力": ["Git"], "授权": ["允许发布"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L3"),
    _case("Runtime Install", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Runtime 安装"]}, LIGHT_L2_CORE + ["coding.reference.13"], ["coding"], "L2"),
    _case("Runtime Upgrade", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Runtime 升级"]}, LIGHT_L2_CORE + ["coding.reference.13"], ["coding"], "L2"),
    _case("Runtime Bundle", {"执行模式": ["实现"], "风险": ["L3"], "工具链": ["已确认"], "范围": ["Runtime", "Runtime Bundle", "MCP"], "意图": ["Runtime Bundle"]}, RUNTIME_CORE, ["coding"], "L3"),
    _case("Project Payload", {"执行模式": ["实现"], "风险": ["L3"], "工具链": ["已确认"], "范围": ["Runtime", "Project Payload"], "意图": ["Project Payload"]}, RUNTIME_CORE, ["coding"], "L3"),
    _case("Skill Mutation", {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Skill Mutation"]}, GATED_L2_CORE + ["coding.reference.11", "coding.reference.16"], ["coding"], "L2"),
    _case("Security / Permission", {"执行模式": ["方案"], "风险": ["L3"], "意图": ["安全与权限"], "授权": ["允许只读"]}, GATED_L2_CORE + ["coding.reference.03", "coding.reference.11", "coding.reference.15"], ["coding"], "L3"),
    _case("CLI package manifest 不推断 Browser/PostgreSQL", {"执行模式": ["只读分析"], "项目形态": ["CLI"], "风险": ["L1"], "工具链": ["JavaScript"]}, ["coding.reference.02", "coding.reference.03", "coding.reference.19"], ["coding"], "L1", forbidden_references=["coding.reference.08", "coding.reference.17", "figma.reference.00"]),
    _case("Backend Python 不推断 FastAPI/PostgreSQL", {"执行模式": ["只读分析"], "项目形态": ["后端服务"], "风险": ["L1"], "工具链": ["Python"]}, ["coding.reference.02", "coding.reference.03", "coding.reference.07", "coding.reference.08", "coding.reference.19"], ["coding"], "L1", forbidden_references=["coding.reference.17", "figma.reference.00"]),
    _case("Design-only Figma 不伪造 API/代码事实", {"风险": ["L1"], "意图": ["Figma review-only"], "能力": ["Figma"], "授权": ["允许只读"]}, ["figma.reference.00", "figma.reference.01", "figma.reference.06", "figma.reference.07"], ["coding", "figma"], "L1", forbidden_references=["coding.reference.06", "coding.reference.08", "coding.reference.17"]),
    _case("Unknown facts", {"执行模式": ["方案"], "风险": ["L2"]}, [], ["coding", "docs", "figma", "review"