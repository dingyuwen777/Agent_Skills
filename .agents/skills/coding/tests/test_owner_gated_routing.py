from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import (
    REFERENCE_ROUTE_PROTOCOL,
    SKILL_ROUTE_PROTOCOL,
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    evaluate_route,
)


def _routing_block(payload: dict[str, object]) -> str:
    """把测试 routing metadata 编码为 canonical 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _contains(dimension: str, *values: str) -> dict[str, object]:
    """构造最小包含表达式。"""
    return {"包含": {"维度": dimension, "取值": list(values)}}


class OwnerGatedRoutingEvaluatorTest(unittest.TestCase):
    """用隔离 fixture 验证 direct Reference 受 Owner gate 限制，而显式 dependency 可以跨 Skill。"""

    def _write_skill(
        self,
        root: Path,
        name: str,
        skill_trigger: dict[str, object],
        references: list[dict[str, object]],
    ) -> None:
        """写入一个满足动态 Catalog 的最小 Skill。"""
        skill_root = root / ".agents" / "skills" / name
        refs = skill_root / "references"
        refs.mkdir(parents=True)
        (skill_root / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fixture\n---\n\n"
            + _routing_block({"协议": SKILL_ROUTE_PROTOCOL, "Skill": name, "触发": skill_trigger})
            + f"# {name}\n",
            encoding="utf-8",
        )
        for index, reference in enumerate(references, start=1):
            (refs / f"{index:02d}_规则.md").write_text(
                _routing_block(reference) + f"# {name} rule {index}\n",
                encoding="utf-8",
            )

    def _route(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """构造 facts-complete Task Route。"""
        return {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": signals,
            "未知项": [],
            "依据": ["owner-gated evaluator fixture"],
        }

    def test_direct_reference_cannot_activate_unmatched_owner(self) -> None:
        """Coding ref 即使 risk trigger 命中，也不能在 Testing-only route 中反向激活 Coding。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_skill(root, "router", _contains("风险", "L1", "L2", "L3"), [])
            self._write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": "coding.reference.01",
                        "触发": _contains("风险", "L2"),
                        "依赖": [],
                    }
                ],
            )
            self._write_skill(
                root,
                "testing",
                _contains("意图", "黑盒测试"),
                [
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": "testing.reference.01",
                        "触发": _contains("意图", "黑盒测试"),
                        "依赖": [],
                    }
                ],
            )

            result = evaluate_route(
                compile_routing(root),
                self._route({"风险": ["L2"], "意图": ["黑盒测试"]}),
            )
            self.assertEqual(result["命中Skill"], ["router", "testing"])
            self.assertEqual(result["必需Reference"], ["testing.reference.01"])

    def test_explicit_dependency_can_cross_owner_gate(self) -> None:
        """Testing ref 显式依赖 Coding ref 时，dependency closure 必须合法加入 Coding Owner。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_skill(root, "router", _contains("风险", "L1", "L2", "L3"), [])
            self._write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": "coding.reference.01",
                        "触发": _contains("风险", "L2"),
                        "依赖": [],
                    }
                ],
            )
            self._write_skill(
                root,
                "testing",
                _contains("意图", "独立验证"),
                [
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": "testing.reference.01",
                        "触发": _contains("意图", "独立验证"),
                        "依赖": ["coding.reference.01"],
                    }
                ],
            )

            result = evaluate_route(
                compile_routing(root),
                self._route({"风险": ["L2"], "意图": ["独立验证"]}),
            )
            self.assertEqual(result["命中Skill"], ["coding", "router", "testing"])
            self.assertEqual(
                result["必需Reference"],
                ["coding.reference.01", "testing.reference.01"],
            )


if __name__ == "__main__":
    unittest.main()
