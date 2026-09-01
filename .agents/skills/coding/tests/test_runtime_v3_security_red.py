from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import BUNDLE_SCHEMA, build_bundle
from runtime.agent_skills_runtime.routing import (
    REFERENCE_ROUTE_PROTOCOL,
    SKILL_ROUTE_PROTOCOL,
    TASK_ROUTE_PROTOCOL,
    evaluate_route,
)
from runtime.agent_skills_runtime.runtime import RuntimeStore


def _routing_block(payload: dict[str, object]) -> str:
    """把测试路由对象编码为 canonical Markdown metadata。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _task_route(*, intent: str, unknown: list[str] | None = None) -> dict[str, object]:
    """构造覆盖 unknown-route 风险的最小 Task Route。"""
    return {
        "协议": TASK_ROUTE_PROTOCOL,
        "信号": {"意图": [intent]},
        "未知项": list(unknown or []),
        "依据": ["Runtime v3 Red 基线"],
    }


class RuntimeV3SecurityRedTest(unittest.TestCase):
    """锁定 Bundle v3、unknown routing 与 plaintext-store 的旧实现失败事实。"""

    def setUp(self) -> None:
        """为每个用例创建隔离 canonical fixture。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        route_values = {"coding": "功能开发", "review": "代码审查", "docs": "文档更新"}
        for skill, route_value in route_values.items():
            skill_root = self.root / ".agents" / "skills" / skill
            references = skill_root / "references"
            references.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(
                f"---\nname: {skill}\ndescription: fixture\n---\n\n"
                + _routing_block(
                    {
                        "协议": SKILL_ROUTE_PROTOCOL,
                        "Skill": skill,
                        "触发": {"包含": {"维度": "意图", "取值": [route_value]}},
                    }
                )
                + f"# {skill}\n",
                encoding="utf-8",
                newline="",
            )
            (references / "01_规则.md").write_text(
                _routing_block(
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": f"{skill}.reference.01",
                        "触发": {"包含": {"维度": "意图", "取值": [route_value]}},
                        "依赖": [],
                    }
                )
                + f"# {skill}\n\n仅用于 Runtime v3 安全回归。\n",
                encoding="utf-8",
                newline="",
            )

    def tearDown(self) -> None:
        """清理隔离 fixture。"""
        self.temp_directory.cleanup()

    def test_runtime_bundle_schema_is_v3(self) -> None:
        """新 Runtime 必须使用独立 record 的 Bundle v3 内部协议。"""
        self.assertEqual(BUNDLE_SCHEMA, "agent-skills-runtime-bundle/v3")

    def test_unknown_irrelevant_dimension_does_not_expand_to_full_corpus(self) -> None:
        """未知维度与当前 trigger 无关时，不得把全部 Reference 作为 required。"""
        bundle = build_bundle(self.root)
        result = evaluate_route(
            bundle["路由清单"],
            _task_route(intent="功能开发", unknown=["阶段"]),
        )

        self.assertEqual(result["必需Reference"], ["coding.reference.01"])
        self.assertTrue(result["存在未知项"])

    def test_runtime_store_does_not_keep_all_reference_plaintext_entries(self) -> None:
        """RuntimeStore 不得持有包含 canonical `content` 的全库 Reference Map。"""
        store = RuntimeStore(build_bundle(self.root))
        entries = getattr(store, "_entries", None)
        if entries is None:
            return
        self.assertTrue(isinstance(entries, dict))
        self.assertTrue(all("content" not in entry for entry in entries.values()))


if __name__ == "__main__":
    unittest.main()
