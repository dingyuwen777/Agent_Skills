from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.routing import REFERENCE_ROUTE_PROTOCOL, SKILL_ROUTE_PROTOCOL


ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = ROOT / ".agents" / "skills"


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


class RuntimeSkillProjectionTest(unittest.TestCase):
    """验证 Source Core 保持完整，而 Runtime Core 自动去除 canonical Reference 身份导航。"""

    def test_source_mode_keeps_canonical_reference_navigation(self) -> None:
        """构建 Runtime Projection 不能要求维护者删除 canonical SKILL 中的源码导航。"""
        coding = (SKILLS_ROOT / "coding" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/02_跨项目研发任务路由.md", coding)
        self.assertIn("02_跨项目研发任务路由.md", coding)
        self.assertIn("references/07_通用验证与证据策略.md", coding)

    def test_project_payload_skill_cores_hide_all_canonical_reference_identities(self) -> None:
        """安装明文面不得包含任一 canonical Reference 文件名、路径、Stable ID 或 references 目录导航。"""
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

    def test_runtime_projection_is_deterministic(self) -> None:
        """同一 canonical 输入重复构建必须得到完全相同的 Project Payload Core bytes 和 digest。"""
        bundle = build_bundle(ROOT)
        first = build_project_payload(ROOT, bundle)
        second = build_project_payload(ROOT, bundle)
        self.assertEqual(first["payload_digest"], second["payload_digest"])
        self.assertEqual(_payload_texts(first), _payload_texts(second))

    def test_new_skill_and_reference_are_sanitized_without_static_allowlist(self) -> None:
        """新增合法 Skill/Reference 后 Projection 必须自动识别其身份，不要求修改固定名称列表。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = root / ".agents" / "skills"
            skills.mkdir(parents=True)
            (skills / "ENTRY.md").write_text("# Entry\n", encoding="utf-8")

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

            bundle = build_bundle(root)
            payload = build_project_payload(root, bundle)
            text = _payload_texts(payload)["security/SKILL.md"]
            self.assertNotIn(reference_name, text)
            self.assertNotIn(reference_id, text)
            self.assertNotIn("references/", text)
            self.assertIn("fixture security workflow", text)
            self.assertIn("失败时必须停止发布", text)
            self.assertIn("完整约束", text)


if __name__ == "__main__":
    unittest.main()
