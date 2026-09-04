from __future__ import annotations

import json
from pathlib import Path
import re
import tempfile
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.routing import REFERENCE_ROUTE_PROTOCOL, SKILL_ROUTE_PROTOCOL


ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = ROOT / ".agents" / "skills"
_FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
_ROUTING_BLOCK = re.compile(r"<!--\s*agent-routing:v1\s*\r?\n.*?\r?\n\s*-->", re.DOTALL)
RUNTIME_OUTPUT_GUARD_MARKER = "对用户只描述项目实际动作、风险、证据和交付状态"


def _routing_block(payload: dict[str, object]) -> str:
    """把测试用路由元数据编码为 canonical Markdown 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _payload_texts(payload: dict[str, object]) -> dict[str, str]:
    """读取 Project Payload 中所有正式 Skill Core 的 UTF-8 文本。"""
    files = payload["files"]
    if not isinstance(files, list):
        raise AssertionError("Project Payload files 不是列表")
    result: dict[str, str] = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path = str(entry.get("path", ""))
        if path.count("/") == 1 and path.endswith("/SKILL.md"):
            result[path] = decode_payload_file(entry).decode("utf-8")
    return result


def _payload_file_text(payload: dict[str, object], relative_path: str) -> str:
    """读取 Project Payload 指定 UTF-8 文件，找不到时让测试直接失败。"""
    files = payload["files"]
    if not isinstance(files, list):
        raise AssertionError("Project Payload files 不是列表")
    for entry in files:
        if isinstance(entry, dict) and str(entry.get("path", "")) == relative_path:
            return decode_payload_file(entry).decode("utf-8")
    raise AssertionError(f"Project Payload 缺少文件：{relative_path}")


def _protected_metadata(text: str) -> tuple[str, str]:
    """提取 Skill frontmatter 与唯一 agent-routing metadata，供 Source/Runtime 逐字守恒断言。"""
    frontmatter_match = _FRONTMATTER.match(text)
    frontmatter = frontmatter_match.group(0) if frontmatter_match else ""
    routing_matches = _ROUTING_BLOCK.findall(text)
    if len(routing_matches) != 1:
        raise AssertionError("受测 SKILL.md 没有唯一 agent-routing metadata")
    return frontmatter, routing_matches[0]


def _write_fixture_router(skills: Path) -> None:
    """写入满足动态 Catalog Contract 的最小 Router Skill。"""
    router = skills / "router"
    router.mkdir()
    (router / "SKILL.md").write_text(
        "---\nname: router\ndescription: fixture\n---\n\n"
        + _routing_block(
            {
                "协议": SKILL_ROUTE_PROTOCOL,
                "Skill": "router",
                "触发": {"包含": {"维度": "风险", "取值": ["L1"]}},
            }
        )
        + "# Router\n",
        encoding="utf-8",
    )


class RuntimeSkillProjectionTest(unittest.TestCase):
    """验证 Runtime 隐藏 Reference 身份时不削弱 Source/native 专业执行能力。"""

    def test_source_mode_keeps_canonical_reference_navigation(self) -> None:
        """构建 Runtime Projection 不能要求维护者删除 canonical SKILL 中的源码导航。"""
        coding = (SKILLS_ROOT / "coding" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/02_跨项目研发任务路由.md", coding)
        self.assertIn("02_跨项目研发任务路由.md", coding)
        self.assertIn("references/07_通用验证与证据策略.md", coding)

    def test_project_payload_skill_cores_hide_all_canonical_reference_identities(self) -> None:
        """安装明文 Core 不得包含任一 canonical Reference 文件名、路径、Stable ID 或目录导航。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        texts = _payload_texts(payload)
        self.assertEqual(set(texts), {f"{skill}/SKILL.md" for skill in bundle["skills"]})

        for path, text in texts.items():
            with self.subTest(path=path):
                self.assertNotIn("references/", text)
                self.assertNotIn("/references/", text)
                for reference in bundle["references"]:
                    self.assertNotIn(str(reference["filename"]), text)
                    self.assertNotIn(str(reference["source_path"]), text)
                    self.assertNotIn(str(reference["id"]), text)

    def test_runtime_projection_preserves_native_skill_entry_and_core_semantics(self) -> None:
        """去身份化不能把 Runtime Core 变成空壳，frontmatter、路由元数据和核心执行语义必须保留。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        texts = _payload_texts(payload)
        required_by_skill = {
            "router/SKILL.md": ("name: router", "agent-routing:v1", "Anti-Agent Boundary", "Runtime Mode"),
            "coding/SKILL.md": ("name: coding", "agent-routing:v1", "Red", "Completion Audit", "Git", "CI"),
            "docs/SKILL.md": ("name: docs", "agent-routing:v1", "Docs Impact", "targeted", "full"),
            "review/SKILL.md": ("name: review", "agent-routing:v1", "Findings", "review-only", "re-review"),
            "figma/SKILL.md": ("name: figma", "agent-routing:v1", "READY", "NOT_READY", "Canvas"),
        }
        for path, markers in required_by_skill.items():
            text = texts[path]
            for marker in markers:
                with self.subTest(path=path, marker=marker):
                    self.assertIn(marker, text)
        for text in texts.values():
            self.assertIn("完整约束", text)

    def test_runtime_projection_preserves_frontmatter_and_skill_routing_metadata_exactly(self) -> None:
        """Runtime Projection 只能改正文；宿主发现 frontmatter 与 Skill 路由 metadata 必须逐字保持 canonical。"""
        bundle = build_bundle(ROOT)
        texts = _payload_texts(build_project_payload(ROOT, bundle))
        for skill in bundle["skills"]:
            source = (SKILLS_ROOT / str(skill) / "SKILL.md").read_text(encoding="utf-8")
            runtime = texts[f"{skill}/SKILL.md"]
            with self.subTest(skill=skill):
                self.assertEqual(_protected_metadata(runtime), _protected_metadata(source))

    def test_every_runtime_skill_core_gets_user_visible_output_guard(self) -> None:
        """所有动态发现的 Runtime Skill Core 都必须得到同一输出 guard，而不是硬编码当前 Skill 名单。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        texts = _payload_texts(payload)
        self.assertGreaterEqual(len(texts), 2)
        for path, text in texts.items():
            with self.subTest(path=path):
                self.assertIn(RUNTIME_OUTPUT_GUARD_MARKER, text)
                self.assertIn("内部能力身份继续用于路由、约束加载和专业执行", text)
                self.assertIn("不得把内部能力名称或标签转写成用户可见任务分工", text)

    def test_runtime_projection_is_deterministic(self) -> None:
        """同一 canonical 输入重复构建必须得到完全相同的 Project Payload Core bytes 和 digest。"""
        bundle = build_bundle(ROOT)
        first = build_project_payload(ROOT, bundle)
        second = build_project_payload(ROOT, bundle)
        self.assertEqual(first["payload_digest"], second["payload_digest"])
        self.assertEqual(_payload_texts(first), _payload_texts(second))

    def test_native_agent_prompts_keep_high_value_activation_and_handoff_semantics(self) -> None:
        """隐私改造不得删掉 canonical/native prompt 中有助于激活、Handoff 和失败边界的强提示。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        required_by_path = {
            "coding/agents/openai.yaml": (
                "Use $coding",
                "Read every triggered reference before acting",
                "Apply Docs Impact and Review routing",
                "Complete every applicable requirement, validation, review, Git, CI and fresh-evidence gate",
            ),
            "docs/agents/openai.yaml": (
                "Use $docs",
                ".agents/skills/coding/SKILL.md",
                "switch back to Coding's full development, validation, review, Git, and completion gates",
                "targeted Docs re-review",
            ),
            "review/agents/openai.yaml": (
                "Use $review",
                "read it before formal review",
                "review-and-test",
                "review-and-fix",
                "Never claim boundaries that were not actually run",
            ),
            "figma/agents/openai.yaml": (
                "Use $figma",
                "review-and-fix",
                "hands confirmed design facts to the target project's Coding workflow",
                "Coding workflow owns production changes, tests, review, CI, Git, PR, merge, and release",
            ),
        }
        for path, markers in required_by_path.items():
            source = (SKILLS_ROOT / path).read_text(encoding="utf-8")
            runtime = _payload_file_text(payload, path)
            with self.subTest(path=path, check="current-runtime-preserves-native-prompt"):
                self.assertEqual(runtime, source)
            for marker in markers:
                with self.subTest(path=path, marker=marker):
                    self.assertIn(marker, source)

    def test_new_skill_and_reference_are_sanitized_without_static_allowlist(self) -> None:
        """新增合法 Skill 自动隐藏 Reference 身份、获得输出 guard，同时保留自己的 native 激活提示。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = root / ".agents" / "skills"
            skills.mkdir(parents=True)
            (skills / "ENTRY.md").write_text("# Entry\n", encoding="utf-8")
            _write_fixture_router(skills)

            security = skills / "security"
            references = security / "references"
            references.mkdir(parents=True)
            reference_name = "91_秘密安全策略.md"
            reference_id = "security.reference.secret-policy"
            (references / reference_name).write_text(
                _routing_block(
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": reference_id,
                        "触发": {"包含": {"维度": "能力", "取值": ["安全审查"]}},
                        "依赖": [],
                    }
                )
                + "# Secret Policy\n\ncanonical-secret-policy\n",
                encoding="utf-8",
            )
            (security / "SKILL.md").write_text(
                "---\nname: security\ndescription: fixture security workflow\n---\n\n"
                + _routing_block(
                    {
                        "协议": SKILL_ROUTE_PROTOCOL,
                        "Skill": "security",
                        "触发": {"包含": {"维度": "能力", "取值": ["安全审查"]}},
                    }
                )
                + "# Security\n\n"
                + f"安全任务详见 [{reference_name}](references/{reference_name})。\n"
                + f"内部稳定身份：{reference_id}\n"
                + "失败时必须停止发布。\n",
                encoding="utf-8",
            )
            agents = security / "agents"
            agents.mkdir()
            native_prompt = (
                'interface:\n  display_name: "Security"\n  short_description: "fixture"\n'
                '  default_prompt: "Use $security. Preserve security checks and stop on unsafe release."\n'
            )
            (agents / "openai.yaml").write_text(native_prompt, encoding="utf-8")

            bundle = build_bundle(root)
            payload = build_project_payload(root, bundle)
            text = _payload_texts(payload)["security/SKILL.md"]
            self.assertNotIn(reference_name, text)
            self.assertNotIn(reference_id, text)
            self.assertNotIn("references/", text)
            self.assertIn("fixture security workflow", text)
            self.assertIn("失败时必须停止发布", text)
            self.assertIn("完整约束", text)
            self.assertIn(RUNTIME_OUTPUT_GUARD_MARKER, text)
            self.assertEqual(_payload_file_text(payload, "security/agents/openai.yaml"), native_prompt)

    def test_reference_identity_inside_protected_frontmatter_fails_closed(self) -> None:
        """若 canonical frontmatter 自身暴露 Reference 身份，Projection 不得静默改写宿主入口，只能拒绝构建。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = root / ".agents" / "skills"
            skills.mkdir(parents=True)
            (skills / "ENTRY.md").write_text("# Entry\n", encoding="utf-8")
            _write_fixture_router(skills)

            security = skills / "security"
            references = security / "references"
            references.mkdir(parents=True)
            reference_name = "91_秘密安全策略.md"
            (references / reference_name).write_text(
                _routing_block(
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": "security.reference.secret-policy",
                        "触发": {"包含": {"维度": "能力", "取值": ["安全审查"]}},
                        "依赖": [],
                    }
                )
                + "# Secret Policy\n\ncanonical-secret-policy\n",
                encoding="utf-8",
            )
            (security / "SKILL.md").write_text(
                f"---\nname: security\ndescription: 入口依赖 {reference_name}\n---\n\n"
                + _routing_block(
                    {
                        "协议": SKILL_ROUTE_PROTOCOL,
                        "Skill": "security",
                        "触发": {"包含": {"维度": "能力", "取值": ["安全审查"]}},
                    }
                )
                + "# Security\n\n失败时必须停止发布。\n",
                encoding="utf-8",
            )

            bundle = build_bundle(root)
            with self.assertRaisesRegex(ValueError, "仍残留 canonical Reference 身份"):
                build_project_payload(root, bundle)


if __name__ == "__main__":
    unittest.main()
