from __future__ import annotations

from pathlib import Path
import json
import unittest

from evals import agent_outcome_eval
from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"
HIGH_VALUE_CASES = {
    "follow-up-recursion",
    "oos-blocker",
    "repair-churn",
    "parent-reviewer",
    "stale-child",
    "single-writer",
    "must-split-fallback",
    "simple-fp",
    "cross-skill-finding",
}


class FinalReleaseBehaviorContractTest(unittest.TestCase):
    """锁定发版前最后四类高价值治理 Contract。"""

    def test_router_owns_cross_skill_followup_lifecycle(self) -> None:
        """Follow-up candidate 之后的通用生命周期必须由跨 Skill Contract 可达。"""
        router = (SKILLS / "router" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "Follow-up Lifecycle",
            "Persistence Authorization Gate",
            "BACKLOG_ITEM",
            "dedup",
            "新 Requirement / 新 Task",
            "当前任务不得继续执行",
        ):
            self.assertIn(marker, router)

    def test_high_value_registry_has_real_case_files(self) -> None:
        """高价值 failure family 不能只登记名称，必须存在合法 case。"""
        case_dir = ROOT / "evals" / "cases"
        found: set[str] = set()
        for path in sorted(case_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            normalized = agent_outcome_eval.validate_case(payload)
            found.add(str(normalized["用例标识"]))
        self.assertTrue(HIGH_VALUE_CASES.issubset(found), HIGH_VALUE_CASES - found)

    def test_high_value_registry_has_machine_consistency_validator(self) -> None:
        """registry↔case 的一致性必须由机器 Contract fail closed。"""
        self.assertTrue(hasattr(agent_outcome_eval, "validate_high_value_case_registry"))

    def test_release_qualification_contract_exists(self) -> None:
        """Release 必须有独立的 model-neutral behavioral qualification Contract。"""
        path = ROOT / "evals" / "release_qualification.py"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        for marker in (
            "Agent Skills Release Qualification/v1",
            "actual",
            "revision",
            "host",
            "model",
        ):
            self.assertIn(marker, text)

    def test_runtime_project_facing_router_keeps_followup_stop_semantics(self) -> None:
        """Runtime Project Payload 必须保留跨 Skill Follow-up 的项目侧停止语义。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        files = payload["files"]
        router_text = None
        for entry in files:
            if isinstance(entry, dict) and entry.get("path") == "router/SKILL.md":
                router_text = decode_payload_file(entry).decode("utf-8")
                break
        self.assertIsNotNone(router_text)
        for marker in (
            "FOLLOW_UP_CANDIDATE",
            "BACKLOG_ITEM",
            "新的 Requirement / Task",
            "不自动创建",
        ):
            self.assertIn(marker, router_text)

    def test_behavior_qualification_workflow_is_revision_bound(self) -> None:
        """actual Evidence 必须由独立 workflow 绑定 main SHA，不写回被验证 revision。"""
        path = ROOT / ".github" / "workflows" / "behavior-qualification.yml"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        for marker in (
            "Behavior Qualification",
            "workflow_dispatch",
            "bundle_base64",
            "refs/heads/main",
            "release-behavior-qualification",
            "--revision",
        ):
            self.assertIn(marker, text)

    def test_release_preflight_validates_behavioral_qualification(self) -> None:
        """现有 Release workflow 只增加资格门禁，不替换三平台产品验证。"""
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        self.assertIn("Validate Outcome Eval case registry", workflow)
        self.assertIn("Validate Release Qualification", workflow)
        for marker in ("runtime-linux:", "runtime-windows:", "runtime-macos:"):
            self.assertIn(marker, workflow)

    def test_routing_conformance_has_exact_and_allowed_contracts(self) -> None:
        """facts-complete 与 unknown/complex 必须分别限制 exact / bounded allowed Context。"""
        path = SKILLS / "coding" / "tests" / "test_routing_conformance.py"
        text = path.read_text(encoding="utf-8")
        self.assertIn("EXACT_CASE_NAMES", text)
        self.assertIn("ALLOWED_CONTEXT_CASE_NAMES", text)
        self.assertIn("assertEqual(actual_references, expected)", text)
        self.assertIn("issubset(allowed)", text)

    def test_context_budget_records_nonblocking_delta(self) -> None:
        """绝对预算继续硬失败，同时提供不改变门禁的 Context Delta 观测。"""
        path = SKILLS / "coding" / "tests" / "test_route_context_budget.py"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Context Delta", text)
        self.assertIn("non-blocking", text)


if __name__ == "__main__":
    unittest.main()
