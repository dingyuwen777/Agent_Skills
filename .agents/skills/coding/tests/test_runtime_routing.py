"""验证中文 canonical 路由元数据、单一求值器与公共契约。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from runtime.agent_skills_runtime.routing import (
    REFERENCE_ROUTE_PROTOCOL,
    ROUTING_MANIFEST_PROTOCOL,
    SKILL_ROUTE_PROTOCOL,
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    deserialize_routing_manifest,
    evaluate_route,
    public_route_contract,
    serialize_routing_manifest,
    validate_task_route,
)


def _routing_block(payload: dict[str, object]) -> str:
    """把测试路由对象编码成 canonical Markdown 注释块。"""
    return (
        "<!-- agent-routing:v1\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n-->\n"
    )


def _contains(dimension: str, *values: str) -> dict[str, object]:
    """构造最小“包含”触发表达式。"""
    return {"包含": {"维度": dimension, "取值": list(values)}}


def _write_skill(
    root: Path,
    name: str,
    skill_trigger: dict[str, object],
    references: list[dict[str, object]],
) -> None:
    """写入一个带中文路由元数据的最小正式 Skill 与 References。"""
    skill_root = root / ".agents" / "skills" / name
    references_root = skill_root / "references"
    references_root.mkdir(parents=True)
    skill_metadata = {
        "协议": SKILL_ROUTE_PROTOCOL,
        "Skill": name,
        "触发": skill_trigger,
    }
    (skill_root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test\n---\n\n"
        + _routing_block(skill_metadata)
        + f"# {name}\n",
        encoding="utf-8",
    )
    for index, reference in enumerate(references, start=1):
        filename = str(reference.pop("文件名", f"{index:02d}_规则.md"))
        (references_root / filename).write_text(
            _routing_block(reference) + f"# 规则 {index}\n",
            encoding="utf-8",
        )


def _reference(
    reference_id: str,
    trigger: dict[str, object],
    *,
    dependencies: list[str] | None = None,
    minimum_risk: str | None = None,
) -> dict[str, object]:
    """构造最小 Reference 路由元数据。"""
    payload: dict[str, object] = {
        "协议": REFERENCE_ROUTE_PROTOCOL,
        "标识": reference_id,
        "触发": trigger,
        "依赖": list(dependencies or []),
    }
    if minimum_risk is not None:
        payload["最低风险"] = minimum_risk
    return payload


def _task_route(**signals: list[str]) -> dict[str, object]:
    """构造中文 Task Route。"""
    return {
        "协议": TASK_ROUTE_PROTOCOL,
        "信号": signals,
        "未知项": [],
        "依据": ["测试事实"],
    }


class RoutingMetadataTest(unittest.TestCase):
    """覆盖 metadata parser/validator/compiler 的失败关闭边界。"""

    def test_valid_chinese_metadata_compiles_deterministically(self) -> None:
        """合法中文 metadata 应生成稳定摘要并保持序列化 roundtrip 精确一致。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    _reference("coding.reference.01", _contains("阶段", "事实恢复")),
                    _reference(
                        "coding.reference.02",
                        _contains("阶段", "功能开发"),
                        dependencies=["coding.reference.01"],
                    ),
                ],
            )
            first = compile_routing(root)
            second = compile_routing(root)
            self.assertEqual(first, second)
            self.assertEqual(first["协议"], ROUTING_MANIFEST_PROTOCOL)
            self.assertEqual(
                deserialize_routing_manifest(serialize_routing_manifest(first)),
                first,
            )
            self.assertRegex(str(first["路由摘要"]), r"^[0-9a-f]{64}$")

    def test_explicit_reference_id_survives_filename_rename(self) -> None:
        """文件 rename 不应自动改变显式 Stable Reference ID。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = _reference("coding.reference.01", _contains("阶段", "事实恢复"))
            reference["文件名"] = "01_旧名称.md"
            _write_skill(root, "coding", _contains("执行模式", "实现"), [reference])
            before = compile_routing(root)
            old_path = root / ".agents" / "skills" / "coding" / "references" / "01_旧名称.md"
            old_path.rename(old_path.with_name("99_新名称.md"))
            after = compile_routing(root)
            self.assertEqual(before["引用"][0]["标识"], "coding.reference.01")
            self.assertEqual(after["引用"][0]["标识"], "coding.reference.01")

    def test_invalid_metadata_fails_closed(self) -> None:
        """非法 JSON、协议、维度、重复 ID、悬空依赖和循环依赖都必须失败关闭。"""
        cases: list[tuple[str, callable]] = []

        def invalid_json(root: Path) -> None:
            skill = root / ".agents" / "skills" / "coding"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: coding\ndescription: test\n---\n"
                "<!-- agent-routing:v1\n{bad json}\n-->\n",
                encoding="utf-8",
            )

        def invalid_protocol(root: Path) -> None:
            _write_skill(root, "coding", _contains("执行模式", "实现"), [])
            path = root / ".agents" / "skills" / "coding" / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8").replace(SKILL_ROUTE_PROTOCOL, "错误协议"), encoding="utf-8")

        def invalid_dimension(root: Path) -> None:
            _write_skill(root, "coding", _contains("不存在维度", "实现"), [])

        def duplicate_id(root: Path) -> None:
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    _reference("coding.reference.01", _contains("阶段", "事实恢复")),
                    _reference("coding.reference.01", _contains("阶段", "功能开发")),
                ],
            )

        def mismatched_owner(root: Path) -> None:
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [_reference("review.reference.01", _contains("阶段", "事实恢复"))],
            )

        def malformed_stable_id(root: Path) -> None:
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [_reference("coding.reference.01.", _contains("阶段", "事实恢复"))],
            )

        def unknown_dependency(root: Path) -> None:
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    _reference(
                        "coding.reference.01",
                        _contains("阶段", "事实恢复"),
                        dependencies=["coding.reference.99"],
                    )
                ],
            )

        def cycle(root: Path) -> None:
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    _reference(
                        "coding.reference.01",
                        _contains("阶段", "事实恢复"),
                        dependencies=["coding.reference.02"],
                    ),
                    _reference(
                        "coding.reference.02",
                        _contains("阶段", "功能开发"),
                        dependencies=["coding.reference.01"],
                    ),
                ],
            )

        cases.extend(
            [
                ("invalid_json", invalid_json),
                ("invalid_protocol", invalid_protocol),
                ("invalid_dimension", invalid_dimension),
                ("duplicate_id", duplicate_id),
                ("mismatched_owner", mismatched_owner),
                ("malformed_stable_id", malformed_stable_id),
                ("unknown_dependency", unknown_dependency),
                ("cycle", cycle),
            ]
        )
        for label, prepare in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                prepare(root)
                with self.assertRaises(ValueError):
                    compile_routing(root)

    def test_deserialized_manifest_revalidates_skill_and_reference_structure(self) -> None:
        """解密边界后的清单仍须拒绝非法 Skill 触发、Stable ID 与非稳定顺序。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    _reference("coding.reference.01", _contains("阶段", "事实恢复")),
                    _reference("coding.reference.02", _contains("阶段", "功能开发")),
                ],
            )
            manifest = compile_routing(root)
            cases = []

            invalid_skill = json.loads(json.dumps(manifest, ensure_ascii=False))
            invalid_skill["技能"][0]["触发"] = {"执行任意代码": "danger"}
            cases.append(invalid_skill)

            invalid_id = json.loads(json.dumps(manifest, ensure_ascii=False))
            invalid_id["引用"][0]["标识"] = "../escape"
            cases.append(invalid_id)

            unstable_order = json.loads(json.dumps(manifest, ensure_ascii=False))
            unstable_order["引用"].reverse()
            cases.append(unstable_order)

            for candidate in cases:
                material = {
                    "协议": candidate["协议"],
                    "技能": candidate["技能"],
                    "引用": candidate["引用"],
                }
                candidate["路由摘要"] = hashlib.sha256(
                    json.dumps(
                        material,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                    deserialize_routing_manifest(
                        json.dumps(candidate, ensure_ascii=False).encode("utf-8")
                    )


class RoutingEvaluatorTest(unittest.TestCase):
    """覆盖并集、依赖、风险、三值未知项与公共词汇边界。"""

    def setUp(self) -> None:
        """建立两个动态 Skill 和四个 References 的规范化测试路由。"""
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        _write_skill(
            self.root,
            "coding",
            {"任一": [_contains("执行模式", "实现", "审查"), _contains("风险", "L1", "L2", "L3")]},
            [
                _reference("coding.reference.01", _contains("阶段", "事实恢复")),
                _reference(
                    "coding.reference.02",
                    _contains("阶段", "功能开发"),
                    dependencies=["coding.reference.01"],
                ),
                _reference(
                    "coding.reference.03",
                    _contains("范围", "公共契约"),
                    dependencies=["coding.reference.02"],
                    minimum_risk="L3",
                ),
            ],
        )
        _write_skill(
            self.root,
            "review",
            _contains("执行模式", "审查"),
            [
                _reference(
                    "review.reference.01",
                    _contains("意图", "代码审查"),
                    dependencies=["coding.reference.02"],
                )
            ],
        )
        self.manifest = compile_routing(self.root)

    def tearDown(self) -> None:
        """释放隔离仓库。"""
        self.temporary.cleanup()

    def test_multiple_signals_union_and_dependency_closure(self) -> None:
        """多条件必须取并集，并展开跨 Skill 依赖闭包。"""
        route = _task_route(
            执行模式=["实现", "审查"],
            阶段=["功能开发"],
            风险=["L2"],
            范围=["公共契约"],
            意图=["代码审查"],
        )
        actual = evaluate_route(self.manifest, route)
        self.assertEqual(actual["命中Skill"], ["coding", "review"])
        self.assertEqual(
            actual["必需Reference"],
            [
                "coding.reference.01",
                "coding.reference.02",
                "coding.reference.03",
                "review.reference.01",
            ],
        )
        self.assertEqual(actual["最低风险"], "L3")

    def test_unknown_facts_expand_only_related_candidate_context(self) -> None:
        """未知阶段只保守加入阶段相关候选，不得再无条件扩大到全部 canonical Context。"""
        route = _task_route(执行模式=["实现"], 风险=["L1"])
        route["未知项"] = ["阶段"]
        actual = evaluate_route(self.manifest, route)
        self.assertEqual(actual["命中Skill"], ["coding"])
        self.assertEqual(
            actual["必需Reference"],
            ["coding.reference.01", "coding.reference.02"],
        )
        self.assertEqual(actual["最低风险"], "L1")
        self.assertTrue(actual["存在未知项"])

    def test_unknown_induced_full_corpus_fails_closed(self) -> None:
        """只有未知事实才把 candidate 扩张到全库时，必须要求恢复更多事实而不是导出全库。"""
        route = _task_route(执行模式=["实现"], 风险=["L1"])
        route["未知项"] = ["阶段", "范围", "意图"]

        with self.assertRaisesRegex(ValueError, "事实不足"):
            evaluate_route(self.manifest, route)

    def test_tristate_any_all_and_not_keep_unknown_without_false_positive(self) -> None:
        """ANY/ALL/NOT 的 UNKNOWN 传播必须保守，但未命中的无关第四条规则不能被带入。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_skill(
                root,
                "coding",
                _contains("执行模式", "实现"),
                [
                    _reference(
                        "coding.reference.01",
                        {"全部": [_contains("阶段", "功能开发"), _contains("范围", "API")]},
                    ),
                    _reference(
                        "coding.reference.02",
                        {"任一": [_contains("阶段", "事实恢复"), _contains("意图", "诊断")]},
                    ),
                    _reference(
                        "coding.reference.03",
                        {"非": _contains("范围", "公共契约")},
                    ),
                    _reference(
                        "coding.reference.04",
                        _contains("能力", "Git"),
                    ),
                ],
            )
            manifest = compile_routing(root)
            route = _task_route(执行模式=["实现"], 范围=["API"])
            route["未知项"] = ["阶段"]
            actual = evaluate_route(manifest, route)

            self.assertEqual(
                actual["必需Reference"],
                ["coding.reference.01", "coding.reference.02", "coding.reference.03"],
            )
            self.assertNotIn("coding.reference.04", actual["必需Reference"])

    def test_public_contract_is_dynamic_without_private_mapping(self) -> None:
        """公共契约应汇总中文词汇和 Skill，但不泄露 Reference mapping。"""
        contract = public_route_contract(self.manifest)
        serialized = json.dumps(contract, ensure_ascii=False)
        self.assertEqual(contract["任务路由协议"], TASK_ROUTE_PROTOCOL)
        self.assertEqual(contract["Skill"], ["coding", "review"])
        self.assertIn("功能开发", contract["维度"]["阶段"])
        for forbidden in ("coding.reference", "文件名", "source_path", "依赖图", "引用数量"):
            self.assertNotIn(forbidden, serialized)

    def test_task_route_rejects_unknown_values_and_authorization_is_data_only(self) -> None:
        """未知取值必须明确失败，授权信号只能参与路由而不能成为权限授予。"""
        contract = public_route_contract(self.manifest)
        with self.assertRaises(ValueError):
            validate_task_route(
                _task_route(执行模式=["不存在动作"]),
                contract,
            )
        route = _task_route(执行模式=["实现"], 授权=["允许修改项目"])
        contract["维度"]["授权"] = ["允许修改项目"]
        normalized = validate_task_route(route, contract)
        self.assertEqual(normalized["信号"]["授权"], ["允许修改项目"])
        self.assertNotIn("权限已授予", normalized)


if __name__ == "__main__":
    unittest.main()
