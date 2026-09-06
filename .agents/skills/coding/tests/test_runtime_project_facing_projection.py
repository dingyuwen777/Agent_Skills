"""验证 Runtime 暴露给普通项目的明文只表达项目工程语义，不暴露内部组织与防披露实现。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.runtime import RuntimeStore


ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = ROOT / ".agents" / "skills"
MAINTENANCE = ROOT / ".agents" / "MAINTENANCE.md"
RUNTIME_REFERENCE = SKILLS_ROOT / "coding" / "references" / "13_本地MCP_Runtime分发与原文上下文加载.md"
MUTATION_REFERENCE = SKILLS_ROOT / "coding" / "references" / "15_规则内容守恒与Skill维护.md"
RUNTIME_README = ROOT / "runtime" / "README.md"
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
_TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".toml", ".txt"}


class RuntimeProjectFacingProjectionTest(unittest.TestCase):
    """覆盖真实 Project Payload 明文、Runtime 公共进度与关键工程语义守恒。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical Source 构建一次真实 Bundle 与 Project Payload。"""
        cls.bundle = build_bundle(ROOT)
        cls.payload = build_project_payload(ROOT, cls.bundle)
        cls.files = {
            str(entry["path"]): decode_payload_file(entry)
            for entry in cls.payload["files"]
            if isinstance(entry, dict)
        }

    def _text(self, path: str) -> str:
        """读取一个 Runtime Project Payload UTF-8 文本文件。"""
        return self.files[path].decode("utf-8")

    def _project_facing_texts(self) -> dict[str, str]:
        """收集普通项目可直接读取的文本运行资产，跳过脚本和二进制数据。"""
        result: dict[str, str] = {}
        for path, payload in self.files.items():
            if Path(path).suffix.lower() not in _TEXT_SUFFIXES:
                continue
            result[path] = payload.decode("utf-8")
        return result

    def _without_skill_machine_name(self, text: str) -> str:
        """仅忽略宿主发现必须保留的 frontmatter `name` 行，其余明文都纳入泄露检查。"""
        match = _FRONTMATTER.match(text)
        if match is None:
            return text
        frontmatter = "\n".join(
            line for line in match.group(1).splitlines() if not line.strip().startswith("name:")
        )
        return frontmatter + text[match.end() :]

    def test_runtime_entry_is_project_facing_projection_not_source_navigation_copy(self) -> None:
        """Runtime Entry 不得复制 Source 内部导航，但必须保留项目事实与最少充分约束入口。"""
        source = (SKILLS_ROOT / "ENTRY.md").read_text(encoding="utf-8")
        runtime = self._text("ENTRY.md")
        self.assertNotEqual(runtime, source)
        for marker in ("当前项目", "真实文件", "工程约束", "最少充分", "无法可靠取得"):
            self.assertIn(marker, runtime)
        for forbidden in (
            "Router",
            "Skill",
            "Reference",
            "Handoff",
            "Source Mode",
            "Runtime Mode",
            ".agents/skills/",
            "agent_skills_",
            "内部能力",
            "内部治理",
            "防披露",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, runtime)

    def test_runtime_skill_plaintext_does_not_expose_internal_navigation_or_disclosure_policy(self) -> None:
        """Runtime Skill Core 只保留宿主发现所需 name 与工程语义，不暴露自定义路由元数据/内部组织说明。"""
        skill_paths = [f"{skill}/SKILL.md" for skill in self.bundle["skills"]]
        for path in skill_paths:
            runtime = self._text(path)
            checked = self._without_skill_machine_name(runtime)
            with self.subTest(path=path):
                self.assertNotIn("agent-routing:v1", checked)
                for forbidden in (
                    "Router",
                    "Skill",
                    "Reference",
                    "Handoff",
                    "Source Mode",
                    "Runtime Mode",
                    "Agent_Skills",
                    ".agents/skills/",
                    "agent_skills_",
                    "内部能力",
                    "内部控制面",
                    "内部任务路由",
                    "用户可见表达边界",
                    "防披露",
                ):
                    self.assertNotIn(forbidden, checked)

    def test_runtime_agent_prompts_are_project_facing_without_named_internal_assignment(self) -> None:
        """分发给宿主的 agent prompt 不再要求 `Use $...` 或播报内部能力交接，但保留工程执行要求。"""
        prompt_paths = sorted(path for path in self.files if path.endswith("/agents/openai.yaml"))
        self.assertTrue(prompt_paths)
        for path in prompt_paths:
            text = self._text(path)
            with self.subTest(path=path):
                for forbidden in (
                    "Use $",
                    "Router",
                    " Skill",
                    "Reference",
                    "Handoff",
                    ".agents/skills/",
                    "Coding workflow",
                    "Skills exist",
                ):
                    self.assertNotIn(forbidden, text)
                for required in ("current", "validation"):
                    self.assertIn(required, text.lower())

    def test_runtime_progress_rule_describes_project_actions_without_internal_control_plane_vocabulary(self) -> None:
        """MCP 公共进度规则只描述项目动作，不枚举内部身份，也不解释防披露机制。"""
        store = RuntimeStore(self.bundle, release_version="project-facing-test")
        rule = str(store.status()["用户可见进度规则"])
        for required in ("项目", "代码", "测试", "文档", "Git/CI", "交付", "真实阻塞原因"):
            self.assertIn(required, rule)
        for forbidden in (
            "Router",
            "Skill",
            "Reference",
            "Handoff",
            "内部能力",
            "内部控制面",
            "内部 Owner",
            "内部任务路由",
            "内部规则解析",
            "必需上下文组织",
            "底层治理组织",
            "装配过程",
            "规则取得过程",
            "机器身份",
            "不要转述",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, rule)

    def test_project_facing_projection_preserves_high_value_engineering_semantics(self) -> None:
        """隐藏内部组织不能把 Runtime Core 变空壳；真实工程风险、验证与专业语义仍可直接触达。"""
        required_by_path = {
            "coding/SKILL.md": ("L1", "L2", "L3", "Red", "Completion Audit", "Git", "CI"),
            "testing/SKILL.md": ("测试", "回归", "用户", "验证"),
            "review/SKILL.md": ("Findings", "review-only", "re-review"),
            "docs/SKILL.md": ("Docs Impact", "targeted", "full"),
            "figma/SKILL.md": ("READY", "NOT_READY", "Canvas"),
            "router/SKILL.md": ("当前项目", "L1", "L2", "L3", "Fresh Evidence Contract"),
        }
        for path, markers in required_by_path.items():
            text = self._text(path)
            for marker in markers:
                with self.subTest(path=path, marker=marker):
                    self.assertIn(marker, text)

    def test_all_project_facing_text_assets_avoid_disclosure_self_description(self) -> None:
        """普通用户能直接打开的文本资产不出现“为了隐藏内部机制”这一类自我说明。"""
        for path, text in self._project_facing_texts().items():
            checked = self._without_skill_machine_name(text)
            with self.subTest(path=path):
                for forbidden in (
                    "用户可见表达边界",
                    "用户可见进度规则",
                    "防披露",
                    "内部能力身份",
                    "内部控制面不得",
                    "不得把内部能力",
                    "内部任务路由",
                ):
                    self.assertNotIn(forbidden, checked)

    def test_maintenance_rules_separate_plaintext_projection_from_private_execution_parity(self) -> None:
        """长期维护规则必须把 Runtime 明文项目化与私有执行同效作为两条独立证据轴。"""
        maintenance = MAINTENANCE.read_text(encoding="utf-8")
        runtime_reference = RUNTIME_REFERENCE.read_text(encoding="utf-8")
        mutation_reference = MUTATION_REFERENCE.read_text(encoding="utf-8")
        runtime_readme = RUNTIME_README.read_text(encoding="utf-8")

        for text in (maintenance, runtime_reference, mutation_reference, runtime_readme):
            self.assertIn("project-facing", text)
            self.assertIn("exact", text.lower())
        for marker in (
            "Project-facing Plaintext",
            "Private Execution Parity",
            "为了追求 Source/Runtime byte equality 把内部 metadata/output guard 重新塞回 Runtime 明文，也属于内容守恒失败",
        ):
            self.assertIn(marker, maintenance)
        self.assertIn("project-facing plaintext", mutation_reference)
        self.assertIn("private execution parity", mutation_reference)
        self.assertIn("不得用 Source/Runtime 明文逐字一致替代 parity", mutation_reference)
        self.assertIn("不要求 Runtime 明文与 Source Core 逐字一致", runtime_reference)
        self.assertIn("Source/Runtime 同效通过 routing/risk/dependency/context parity 证明", runtime_readme)


if __name__ == "__main__":
    unittest.main()