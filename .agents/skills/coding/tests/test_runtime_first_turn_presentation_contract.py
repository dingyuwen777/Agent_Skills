from __future__ import annotations

import re
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.disclosure import (
    PROJECT_FACING_AGENT_PROMPT,
    PROJECT_FACING_USER_COMMUNICATION_RULE,
    USER_VISIBLE_PROGRESS_RULE,
)
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.runtime import RuntimeStore
from runtime.agent_skills_runtime.runtime_skill_projection import project_runtime_agent_prompt


ROOT = Path(__file__).resolve().parents[4]
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


class RuntimeFirstTurnPresentationContractTest(unittest.TestCase):
    """验证 Runtime 在宿主首次用户回复前已经具备 project-facing 沟通边界。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical Source 构建真实 Project Payload，覆盖实际安装明文而非手写镜像。"""
        cls.bundle = build_bundle(ROOT)
        cls.payload = build_project_payload(ROOT, cls.bundle)
        cls.files = {
            str(entry["path"]): decode_payload_file(entry).decode("utf-8")
            for entry in cls.payload["files"]
            if isinstance(entry, dict)
            and Path(str(entry.get("path", ""))).suffix.lower() in {".md", ".yaml", ".yml"}
        }

    def _text(self, path: str) -> str:
        """读取真实 Project Payload 中一个 UTF-8 用户前置可见文本资产。"""
        try:
            return self.files[path]
        except KeyError as error:
            raise AssertionError(f"Project Payload 缺少受测文件：{path}") from error

    def test_runtime_entry_has_first_turn_project_communication_contract(self) -> None:
        """Entry 必须在任何后续 MCP 返回之前阻止治理名称转写，并保留用户计划。"""
        entry = self._text("ENTRY.md")
        self.assertIn(PROJECT_FACING_USER_COMMUNICATION_RULE, entry)
        self.assertIn("治理能力或规则的内部名称", entry)
        self.assertIn("用户明确提供的项目术语、计划和决定照常保留", entry)

    def test_every_runtime_skill_keeps_machine_name_but_not_as_user_assignment(self) -> None:
        """宿主发现 name 可保留，但 description/body 都必须具备首轮项目表达 Contract。"""
        for skill in self.bundle["skills"]:
            path = f"{skill}/SKILL.md"
            text = self._text(path)
            match = _FRONTMATTER.match(text)
            self.assertIsNotNone(match, path)
            assert match is not None
            frontmatter = match.group(1)
            with self.subTest(path=path, area="machine-name"):
                self.assertIn(f"name: {skill}", frontmatter)
            with self.subTest(path=path, area="frontmatter-description"):
                description = next(
                    line for line in frontmatter.splitlines() if line.strip().startswith("description:")
                )
                self.assertIn("治理能力或规则的内部名称", description)
                self.assertIn("用户明确提供的项目术语、计划和决定", description)
            with self.subTest(path=path, area="body"):
                self.assertIn(PROJECT_FACING_USER_COMMUNICATION_RULE, text[match.end() :])
                self.assertIn("不把这些名称转写成用户可见的任务步骤、分工或计划", text[match.end() :])

    def test_runtime_agent_prompts_block_governance_name_narration(self) -> None:
        """宿主 agent prompt 必须覆盖治理名称转写这一真实失败模式。"""
        prompt_paths = sorted(path for path in self.files if path.endswith("/agents/openai.yaml"))
        self.assertTrue(prompt_paths)
        for path in prompt_paths:
            text = self._text(path)
            with self.subTest(path=path):
                self.assertIn(PROJECT_FACING_AGENT_PROMPT, text)
                self.assertIn("governance capability or rule names", text)
                self.assertIn("preserve user-provided project terms, plans, and decisions", text)
                self.assertNotIn("rule-selection", text)
                self.assertNotIn("rule-loading", text)
                self.assertNotIn("Do not pre-announce branch", text)
                self.assertNotIn("Use $", text)

    def test_user_provided_gold_set_plan_is_not_filtered_by_project_prompt_projection(self) -> None:
        """反向回归：用户明确写入的 Gold Set 决定属于项目计划，不应被新边界抑制。"""
        source = (
            'interface:\n  display_name: "Coding"\n  short_description: "fixture"\n'
            '  default_prompt: "Use $coding. Preserve the user-provided Gold Set decision and run validation."\n'
        ).encode("utf-8")
        runtime = project_runtime_agent_prompt(source, "coding").decode("utf-8")
        self.assertNotIn("Use $coding", runtime)
        self.assertIn("Gold Set", runtime)
        self.assertIn("preserve user-provided project terms, plans, and decisions", runtime)

    def test_new_contract_does_not_expand_into_process_or_delivery_restrictions(self) -> None:
        """反向回归：新增 Contract 只约束内部名称转写，不扩展到一般工程过程或交付表达。"""
        self.assertNotIn("规则选择", PROJECT_FACING_USER_COMMUNICATION_RULE)
        self.assertNotIn("取得/加载", PROJECT_FACING_USER_COMMUNICATION_RULE)
        self.assertNotIn("测试资产", PROJECT_FACING_USER_COMMUNICATION_RULE)
        self.assertNotIn("分支", PROJECT_FACING_USER_COMMUNICATION_RULE)
        self.assertNotIn("PR", PROJECT_FACING_USER_COMMUNICATION_RULE)
        self.assertNotIn("merge", PROJECT_FACING_AGENT_PROMPT.lower())
        self.assertNotIn("release", PROJECT_FACING_AGENT_PROMPT.lower())
        self.assertNotIn("deploy", PROJECT_FACING_AGENT_PROMPT.lower())

    def test_mcp_public_progress_uses_same_project_communication_semantics(self) -> None:
        """MCP 后续公共进度不能与首次回复前的 project-facing Contract 漂移。"""
        store = RuntimeStore(self.bundle, release_version="first-turn-test")
        payloads = [store.status(), store.route_contract(), store.start_task("T-first-turn")]
        for payload in payloads:
            rule = str(payload["用户可见进度规则"])
            with self.subTest(payload=payload.get("协议", payload.get("当前阶段"))):
                self.assertEqual(rule, USER_VISIBLE_PROGRESS_RULE)
                self.assertIn(PROJECT_FACING_USER_COMMUNICATION_RULE, rule)
                self.assertIn("用户明确提供的项目术语、计划和决定照常保留", rule)
                for marker in ("代码修改", "测试", "文档同步", "复核", "Git/CI", "交付状态", "真实阻塞原因"):
                    self.assertIn(marker, rule)
                self.assertNotIn("额外测试资产", rule)
                self.assertNotIn("未授权的分支", rule)


if __name__ == "__main__":
    unittest.main()
