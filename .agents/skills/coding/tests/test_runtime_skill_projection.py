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
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
_ROUTING_BLOCK = re.compile(r"<!--\s*agent-routing:v1\s*\r?\n.*?\r?\n\s*-->", re.DOTALL)


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


def _frontmatter_name(text: str) -> str:
    """提取 Runtime Skill frontmatter 中宿主发现所需的唯一 name。"""
    match = _FRONTMATTER.match(text)
    if match is None:
        raise AssertionError("受测 SKILL.md 缺少 frontmatter")
    names = [line for line in match.group(1).splitlines() if line.strip().startswith("name:")]
    if len(names) != 1:
        raise AssertionError("受测 SKILL.md 没有唯一 name")
    return names[0]


def _without_machine_name(text: str) -> str:
    """忽略宿主发现必须保留的 name 行后返回其余 Runtime 明文。"""
    match = _FRONTMATTER.match(text)
    if match is None:
        return text
    frontmatter = "\n".join(
        line for line in match.group(1).splitlines() if not line.strip().startswith("name:")
    )
    return frontmatter + text[match.end() :]


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
    """验证 Runtime project-facing 投影不暴露内部组织，同时保持专业工程语义。"""

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

    def test_runtime_projection_preserves_project_facing_core_semantics(self) -> None:
        """去内部组织不能把 Runtime Core 变成空壳，真实工程语义必须保留。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        texts = _payload_texts(payload)
        required_by_skill = {
            "router/SKILL.md": ("name: router", "当前项目", "L1", "L2", "L3", "Fresh Evidence Contract"),
            "coding/SKILL.md": ("name: coding", "Red", "Completion Audit", "Git", "CI"),
            "docs/SKILL.md": ("name: docs", "Docs Impact", "targeted", "full"),
            "review/SKILL.md": ("name: review", "Findings", "review-only", "re-review"),
            "figma/SKILL.md": ("name: figma", "READY", "NOT_READY", "Canvas"),
            "testing/SKILL.md": ("name: testing", "测试", "回归", "User Journey", "test-only"),
        }
        for path, markers in required_by_skill.items():
            text = texts[path]
            for marker in markers:
                with self.subTest(path=path, marker=marker):
                    self.assertIn(marker, text)

    def test_runtime_projection_keeps_only_host_name_not_routing_metadata(self) -> None:
        """Runtime frontmatter 仅保留宿主发现所需 name；机器路由 metadata 留在私有清单。"""
        bundle = build_bundle(ROOT)
        texts = _payload_texts(build_project_payload(ROOT, bundle))
        for skill in bundle["skills"]:
            source = (SKILLS_ROOT / str(skill) / "SKILL.md").read_text(encoding="utf-8")
            runtime = texts[f"{skill}/SKILL.md"]
            with self.subTest(skill=skill):
                self.assertEqual(_frontmatter_name(runtime), _frontmatter_name(source))
                self.assertEqual(len(_ROUTING_BLOCK.findall(source)), 1)
                self.assertEqual(len(_ROUTING_BLOCK.findall(runtime)), 0)

    def test_every_runtime_skill_core_avoids_disclosure_self_description(self) -> None:
        """所有动态发现的 Runtime Skill Core 都不得重新写入防披露说明或内部组织身份。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        texts = _payload_texts(payload)
        self.assertGreaterEqual(len(texts), 2)
        forbidden = (
            "Router",
            "Skill",
            "Reference",
            "Handoff",
            "Source Mode",
            "Runtime Mode",
            "Agent_Skills",
            ".agents/skills/",
            "agent_skills_",
            "Coding",
            "内部能力",
            "内部控制面",
            "用户可见表达边界",
            "防披露",
        )
        for path, text in texts.items():
            checked = _without_machine_name(text)
            for marker in forbidden:
                with self.subTest(path=path, marker=marker):
                    self.assertNotIn(marker, checked)

    def test_runtime_projection_is_deterministic(self) -> None:
        """同一 canonical 输入重复构建必须得到完全相同的 Project Payload Core bytes 和 digest。"""
        bundle = build_bundle(ROOT)
        first = build_project_payload(ROOT, bundle)
        second = build_project_payload(ROOT, bundle)
        self.assertEqual(first["payload_digest"], second["payload_digest"])
        self.assertEqual(_payload_texts(first), _payload_texts(second))

    def test_runtime_agent_prompts_keep_high_value_project_execution_semantics(self) -> None:
        """agent prompt 去内部组织后仍保留激活所需项目事实、验证与失败边界。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        required_by_path = {
            "coding/agents/openai.yaml": (
                "project shape",
                "L1-L3",
                "current repository facts",
                "Asia/Shanghai",
                "Git",
                "CI",
                "validation",
            ),
            "docs/agents/openai.yaml": (
                "current repository facts",
                "not_applicable",
                "targeted",
                "full",
                "code_issue_detected",
                "validation",
            ),
            "review/agents/openai.yaml": (
                "review target",
                "review-only",
                "review-and-test",
                "review-and-fix",
                "Never claim boundaries that were not actually run",
                "validation",
            ),
            "figma/agents/openai.yaml": (
                "Figma",
                "review-and-fix",
                "NOT_READY",
                "current",
                "validation",
            ),
        }
        forbidden = ("Use $", "Router", " Skill", "Reference", "Handoff", ".agents/skills/", "Coding")
        for path, markers in required_by_path.items():
            source = (SKILLS_ROOT / path).read_text(encoding="utf-8")
            runtime = _payload_file_text(payload, path)
            with self.subTest(path=path, check="runtime-is-derived"):
                self.assertNotEqual(runtime, source)
            for marker in markers:
                with self.subTest(path=path, marker=marker):
                    self.assertIn(marker, runtime)
            for marker in forbidden:
                with self.subTest(path=path, forbidden=marker):
                    self.assertNotIn(marker, runtime)

    def test_new_skill_and_reference_are_projected_without_static_allowlist(self) -> None:
        """新增合法 Skill 自动隐藏内部身份，同时保留自己的专业语义与宿主 prompt。"""
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
            self.assertNotIn("agent-routing:v1", text)
            self.assertIn("fixture security workflow", text)
            self.assertIn("失败时必须停止发布", text)
            self.assertIn("完整约束", text)

            runtime_prompt = _payload_file_text(payload, "security/agents/openai.yaml")
            self.assertNotEqual(runtime_prompt, native_prompt)
            self.assertNotIn("Use $security", runtime_prompt)
            self.assertIn("security checks", runtime_prompt)
            self.assertIn("validation", runtime_prompt.lower())

    def test_reference_identity_inside_frontmatter_is_sanitized_without_changing_name(self) -> None:
        """frontmatter description 暴露 Reference 身份时必须投影掉，同时保留宿主 name。"""
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

            payload = build_project_payload(root, build_bundle(root))
            text = _payload_texts(payload)["security/SKILL.md"]
            self.assertIn("name: security", text)
            self.assertNotIn(reference_name, text)
            self.assertNotIn("security.reference.secret-policy", text)
            self.assertIn("完整约束", text)


if __name__ == "__main__":
    unittest.main()
