from __future__ import annotations

from pathlib import Path
import unittest

from evals.agent_outcome_eval import HIGH_VALUE_CONVERGENCE_CASES, validate_high_value_case_registry
from evals.release_qualification import DEFAULT_HOST_CASES, SUPPORTED_HOSTS
from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.host_agent_projection import (
    load_multi_agent_roles,
    render_claude_agent,
    render_codex_agent,
    render_cursor_agent,
    render_deepseek_execution_rows,
)
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"


def _payload_files() -> dict[str, bytes]:
    """构建当前 Runtime Project Payload 并返回路径到原始字节。"""
    payload = build_project_payload(ROOT, build_bundle(ROOT))
    return {
        str(entry["path"]): decode_payload_file(entry)
        for entry in payload["files"]
        if isinstance(entry, dict)
    }


class DecisionAuthorityContractTest(unittest.TestCase):
    """锁定跨模型自主决策与 Human Input Admission Contract。"""

    def test_router_owns_ordered_decision_authority_contract(self) -> None:
        """规则、事实、惯例、默认和局部可逆选择必须先于人类决策。"""
        text = (SKILLS / "router" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "Decision Authority Contract",
            "Human Input Admission Gate",
            "RULE_RESOLVED",
            "FACT_RESOLVABLE",
            "CONVENTION_RESOLVED",
            "DEFAULT_RESOLVED",
            "SELF_DECIDE",
            "OWNER_DECISION",
            "AUTHORIZATION_REQUIRED",
            "REQUIRED_USER_INPUT",
            "CAPABILITY_BLOCKER",
            "No Choice-Prompt",
        ):
            self.assertIn(marker, text)

    def test_coding_keeps_self_decide_and_must_ask_boundary(self) -> None:
        """Coding 不得把普通实现细节升级成人工审批，也不能吞掉真正 Owner 决策。"""
        text = (SKILLS / "coding" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "SELF_DECIDE",
            "OWNER_DECISION",
            "AUTHORIZATION_REQUIRED",
            "REQUIRED_USER_INPUT",
            "No Choice-Prompt",
            "低风险",
            "可逆",
        ):
            self.assertIn(marker, text)

    def test_git_branch_name_has_deterministic_resolution_without_user_question(self) -> None:
        """分支名应按规则/惯例/fallback 自动解析，而不是询问用户。"""
        text = (
            SKILLS / "coding" / "references" / "14_Git交付依赖安全与宿主能力边界.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Branch Name Resolution",
            "项目显式规则",
            "稳定分支模式",
            "Requirement / Issue",
            "<type>/<short-task-slug>",
            "feature / fix / refactor / docs / test / tech",
            "不得向用户询问",
        ):
            self.assertIn(marker, text)

    def test_managed_agents_exposes_human_input_gate_to_every_main_model(self) -> None:
        """目标项目最前层必须直接给所有模型相同 Ask/No-Ask 硬边界。"""
        text = (
            SKILLS / "coding" / "assets" / "AGENTS.managed.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "自主决策与提问边界",
            "RULE_RESOLVED",
            "FACT_RESOLVABLE",
            "SELF_DECIDE",
            "OWNER_DECISION",
            "AUTHORIZATION_REQUIRED",
            "不得把已经可以自行解决的问题重新包装成多个方案让用户选择",
        ):
            self.assertIn(marker, text)

    def test_runtime_router_and_agent_prompt_preserve_decision_authority(self) -> None:
        """Runtime project-facing 明文必须保留自主决策，而不是只在 Source 中存在。"""
        files = _payload_files()
        router = files["router/SKILL.md"].decode("utf-8")
        for marker in (
            "决策权与用户提问",
            "RULE_RESOLVED",
            "FACT_RESOLVABLE",
            "SELF_DECIDE",
            "OWNER_DECISION",
            "No Choice-Prompt",
        ):
            self.assertIn(marker, router)

        prompts = [
            payload.decode("utf-8")
            for path, payload in files.items()
            if path.endswith("/agents/openai.yaml")
        ]
        self.assertTrue(prompts)
        for prompt in prompts:
            self.assertIn("Do not ask the user to choose ordinary implementation details", prompt)
            self.assertIn("material owner decision", prompt)

    def test_all_supported_child_host_prompts_return_material_decision_to_parent(self) -> None:
        """Child 不直接问用户；普通细节自行解决，真正决策只返回 Parent。"""
        files = _payload_files()
        roles = load_multi_agent_roles(files)
        self.assertTrue(roles)
        for role in roles:
            rendered = (
                render_codex_agent(role).decode("utf-8"),
                render_claude_agent(role).decode("utf-8"),
                render_cursor_agent(role).decode("utf-8"),
            )
            for text in rendered:
                self.assertIn("Do not ask the user to choose ordinary implementation details", text)
                self.assertIn("return it to the parent under PARENT_DECISION", text)
        deepseek = render_deepseek_execution_rows(roles)
        self.assertIn("Do not ask the user to choose ordinary implementation details", deepseek)
        self.assertIn("return it to the parent under PARENT_DECISION", deepseek)

    def test_permanent_contract_keeps_both_no_ask_and_must_ask_sides(self) -> None:
        """减少提问不能退化成永远不问。"""
        router = (SKILLS / "router" / "SKILL.md").read_text(encoding="utf-8")
        for no_ask in (
            "RULE_RESOLVED",
            "FACT_RESOLVABLE",
            "CONVENTION_RESOLVED",
            "DEFAULT_RESOLVED",
            "SELF_DECIDE",
        ):
            self.assertIn(no_ask, router)
        for must_ask in (
            "OWNER_DECISION",
            "AUTHORIZATION_REQUIRED",
            "REQUIRED_USER_INPUT",
            "CAPABILITY_BLOCKER",
        ):
            self.assertIn(must_ask, router)
        self.assertIn("业务", router)
        self.assertIn("Schema", router)
        self.assertIn("安全", router)

    def test_unnecessary_clarification_is_release_qualified_high_value_case(self) -> None:
        """真实多问问题必须进入现有 model-neutral registry 与 Release Qualification。"""
        self.assertIn("unnecessary-clarification", HIGH_VALUE_CONVERGENCE_CASES)
        case = ROOT / "evals" / "cases" / "unnecessary-clarification.json"
        self.assertTrue(case.is_file())
        report = validate_high_value_case_registry(ROOT / "evals" / "cases")
        self.assertIn("unnecessary-clarification", report["高价值用例"])
        for host in SUPPORTED_HOSTS:
            self.assertIn("unnecessary-clarification", DEFAULT_HOST_CASES[host])


if __name__ == "__main__":
    unittest.main()
