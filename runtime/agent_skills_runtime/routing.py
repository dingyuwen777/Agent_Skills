"""编译、校验并求值 Agent Skills 的 canonical 中文路由元数据。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from .skill_catalog import discover_skills, iter_reference_files


SKILL_ROUTE_PROTOCOL = "Agent Skills Skill路由/v1"
REFERENCE_ROUTE_PROTOCOL = "Agent Skills Reference路由/v1"
TASK_ROUTE_PROTOCOL = "Agent Skills 任务路由/v1"
ROUTING_MANIFEST_PROTOCOL = "Agent Skills 路由清单/v1"
PUBLIC_ROUTE_CONTRACT_PROTOCOL = "Agent Skills 公共路由契约/v1"
CONTROL_PLANE_SKILL = "router"

ROUTE_DIMENSIONS = (
    "执行模式",
    "项目形态",
    "阶段",
    "风险",
    "工具链",
    "范围",
    "意图",
    "治理",
    "能力",
    "授权",
)
_OWNER_REFINEMENT_DIMENSIONS = frozenset(
    {"项目形态", "风险", "工具链", "范围", "治理", "授权"}
)
_RISK_ORDER = {"L1": 1, "L2": 2, "L3": 3}
_ROUTING_BLOCK = re.compile(r"<!--\s*agent-routing:v1\s*\n(.*?)\n\s*-->", re.DOTALL)
_SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_REFERENCE_ID = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*\.reference\.[a-z0-9]+(?:[.-][a-z0-9]+)*$"
)
_TRUE = 1
_UNKNOWN = 0
_FALSE = -1


def _canonical_json(value: Any) -> bytes:
    """把路由对象编码为确定性 UTF-8 JSON 字节。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: Any) -> str:
    """计算规范化路由对象的 SHA256。"""
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _parse_routing_block(path: Path) -> dict[str, Any]:
    """从 canonical Markdown 中读取唯一 agent-routing JSON 注释块。"""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"路由元数据文件不是合法 UTF-8：{path}") from error
    matches = _ROUTING_BLOCK.findall(text)
    if len(matches) != 1:
        raise ValueError(f"canonical Markdown 必须且只能包含一个 agent-routing:v1 block：{path}")
    try:
        payload = json.loads(matches[0])
    except json.JSONDecodeError as error:
        raise ValueError(f"路由元数据不是合法 JSON：{path}：{error.msg}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"路由元数据顶层必须是 object：{path}")
    return payload


def _normalize_values(raw: Any, *, label: str) -> list[str]:
    """校验路由取值列表并返回稳定去重结果。"""
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{label} 取值必须是非空列表")
    values = [str(item).strip() for item in raw]
    if any(not value for value in values):
        raise ValueError(f"{label} 取值不能为空")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} 取值不能重复")
    return sorted(values)


def _normalize_expression(raw: Any, *, label: str) -> dict[str, Any]:
    """校验有限触发表达式，拒绝任意代码或未知操作符。"""
    if not isinstance(raw, Mapping) or len(raw) != 1:
        raise ValueError(f"{label} 触发表达式必须是只含一个操作符的 object")
    operator = next(iter(raw))
    value = raw[operator]
    if operator == "包含":
        if not isinstance(value, Mapping) or set(value) != {"维度", "取值"}:
            raise ValueError(f"{label} 包含表达式必须只含维度和取值")
        dimension = str(value["维度"]).strip()
        if dimension not in ROUTE_DIMENSIONS:
            raise ValueError(f"{label} 使用非法路由维度：{dimension!r}")
        values = _normalize_values(value["取值"], label=f"{label}/{dimension}")
        if dimension == "风险" and any(item not in _RISK_ORDER for item in values):
            raise ValueError(f"{label} 风险取值只允许 L1/L2/L3")
        return {"包含": {"维度": dimension, "取值": values}}
    if operator in {"全部", "任一"}:
        if not isinstance(value, list) or not value:
            raise ValueError(f"{label} {operator} 必须是非空表达式列表")
        expressions = [
            _normalize_expression(item, label=f"{label}/{operator}[{index}]")
            for index, item in enumerate(value)
        ]
        expressions.sort(key=lambda item: _canonical_json(item))
        return {operator: expressions}
    if operator == "非":
        return {"非": _normalize_expression(value, label=f"{label}/非")}
    raise ValueError(f"{label} 使用不支持的路由操作符：{operator!r}")


def _normalize_skill_metadata(raw: Mapping[str, Any], *, skill: str, path: Path) -> dict[str, Any]:
    """校验 Skill 级路由元数据与动态 Catalog 身份。"""
    if set(raw) != {"协议", "Skill", "触发"}:
        raise ValueError(f"Skill 路由元数据字段不合法：{path}")
    if raw.get("协议") != SKILL_ROUTE_PROTOCOL:
        raise ValueError(f"Skill 路由协议不受支持：{path}")
    if str(raw.get("Skill")) != skill:
        raise ValueError(f"Skill 路由名称与动态 Catalog 不一致：{path}")
    return {
        "Skill": skill,
        "触发": _normalize_expression(raw["触发"], label=f"Skill {skill}"),
    }


def _normalize_dependencies(raw: Any, *, path: Path) -> list[str]:
    """校验 Reference 依赖列表和 Stable ID 语法。"""
    if not isinstance(raw, list):
        raise ValueError(f"Reference 依赖必须是列表：{path}")
    dependencies = [str(item).strip() for item in raw]
    if any(not _REFERENCE_ID.fullmatch(item) for item in dependencies):
        raise ValueError(f"Reference 依赖包含非法 Stable ID：{path}")
    if len(dependencies) != len(set(dependencies)):
        raise ValueError(f"Reference 依赖不能重复：{path}")
    return sorted(dependencies)


def _normalize_reference_metadata(
    raw: Mapping[str, Any],
    *,
    skill: str,
    path: Path,
    source_root: Path,
) -> dict[str, Any]:
    """校验 Reference 级元数据并保留加密边界内的 provenance。"""
    required = {"协议", "标识", "触发", "依赖"}
    allowed = required | {"最低风险"}
    if set(raw) - allowed or not required.issubset(raw):
        raise ValueError(f"Reference 路由元数据字段不合法：{path}")
    if raw.get("协议") != REFERENCE_ROUTE_PROTOCOL:
        raise ValueError(f"Reference 路由协议不受支持：{path}")
    reference_id = str(raw.get("标识", "")).strip()
    if not _REFERENCE_ID.fullmatch(reference_id):
        raise ValueError(f"Reference Stable ID 非法：{path}：{reference_id!r}")
    if reference_id.split(".reference.", 1)[0] != skill:
        raise ValueError(f"Reference Stable ID 与 Skill Owner 不一致：{path}：{reference_id!r}")
    minimum_risk = raw.get("最低风险")
    if minimum_risk is not None and str(minimum_risk) not in _RISK_ORDER:
        raise ValueError(f"Reference 最低风险只允许 L1/L2/L3：{path}")
    normalized = {
        "标识": reference_id,
        "Skill": skill,
        "文件名": path.name,
        "源路径": path.relative_to(source_root).as_posix(),
        "触发": _normalize_expression(raw["触发"], label=f"Reference {reference_id}"),
        "依赖": _normalize_dependencies(raw["依赖"], path=path),
    }
    if minimum_risk is not None:
        normalized["最低风险"] = str(minimum_risk)
    return normalized


def _assert_acyclic(references: Iterable[Mapping[str, Any]]) -> None:
    """验证 Reference 依赖图没有循环。"""
    graph = {str(entry["标识"]): [str(item) for item in entry["依赖"]] for entry in references}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(reference_id: str, trail: list[str]) -> None:
        """深度优先检查单个 Reference 的依赖路径。"""
        if reference_id in visiting:
            cycle = " -> ".join(trail + [reference_id])
            raise ValueError(f"Reference 路由依赖存在循环：{cycle}")
        if reference_id in visited:
            return
        visiting.add(reference_id)
        for dependency in graph[reference_id]:
            visit(dependency, trail + [reference_id])
        visiting.remove(reference_id)
        visited.add(reference_id)

    for reference_id in sorted(graph):
        visit(reference_id, [])


def _routing_material(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """提取 routing digest 覆盖的规范化私有清单字段。"""
    return {
        "协议": manifest["协议"],
        "技能": manifest["技能"],
        "引用": manifest["引用"],
    }


def compile_routing(source_root: str | Path) -> dict[str, Any]:
    """从动态 Skill Catalog 的 canonical Markdown 编译私有 Routing Manifest。"""
    root = Path(source_root).resolve()
    skills = discover_skills(root)
    normalized_skills = [
        _normalize_skill_metadata(
            _parse_routing_block(skill.root / "SKILL.md"),
            skill=skill.name,
            path=skill.root / "SKILL.md",
        )
        for skill in skills
    ]
    normalized_references: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for skill_name, path in iter_reference_files(skills):
        reference = _normalize_reference_metadata(
            _parse_routing_block(path),
            skill=skill_name,
            path=path,
            source_root=root,
        )
        reference_id = str(reference["标识"])
        if reference_id in seen_ids:
            raise ValueError(f"Reference Stable ID 全局重复：{reference_id}")
        seen_ids.add(reference_id)
        normalized_references.append(reference)
    normalized_skills.sort(key=lambda item: str(item["Skill"]))
    normalized_references.sort(key=lambda item: str(item["标识"]))
    for reference in normalized_references:
        unknown = sorted(set(reference["依赖"]) - seen_ids)
        if unknown:
            raise ValueError(f"Reference {reference['标识']} 存在悬空依赖：{', '.join(unknown)}")
    _assert_acyclic(normalized_references)
    manifest: dict[str, Any] = {
        "协议": ROUTING_MANIFEST_PROTOCOL,
        "技能": normalized_skills,
        "引用": normalized_references,
    }
    manifest["路由摘要"] = _sha256(_routing_material(manifest))
    validate_routing_manifest(manifest)
    return manifest


def validate_routing_manifest(manifest: Mapping[str, Any]) -> None:
    """验证私有 Routing Manifest 的协议、结构、依赖与摘要。"""
    if set(manifest) != {"协议", "技能", "引用", "路由摘要"}:
        raise ValueError("Routing Manifest 字段不合法")
    if manifest.get("协议") != ROUTING_MANIFEST_PROTOCOL:
        raise ValueError(f"Routing Manifest 协议不受支持：{manifest.get('协议')!r}")
    skills = manifest.get("技能")
    references = manifest.get("引用")
    if not isinstance(skills, list) or not skills:
        raise ValueError("Routing Manifest 技能必须是非空列表")
    if not isinstance(references, list):
        raise ValueError("Routing Manifest 引用必须是列表")
    normalized_skills: list[dict[str, Any]] = []
    for raw in skills:
        if not isinstance(raw, Mapping) or set(raw) != {"Skill", "触发"}:
            raise ValueError("Routing Manifest Skill 必须是只含 Skill 和触发的 object")
        skill_name = str(raw["Skill"])
        if not _SKILL_NAME.fullmatch(skill_name):
            raise ValueError(f"Routing Manifest Skill 名称非法：{skill_name!r}")
        normalized_skills.append(
            {
                "Skill": skill_name,
                "触发": _normalize_expression(raw["触发"], label=f"Skill {skill_name}"),
            }
        )
    skill_names = [str(entry["Skill"]) for entry in normalized_skills]
    if skill_names != sorted(set(skill_names)):
        raise ValueError("Routing Manifest Skill 必须唯一并稳定排序")
    seen_ids: set[str] = set()
    normalized_references: list[dict[str, Any]] = []
    for raw in references:
        if not isinstance(raw, Mapping):
            raise ValueError("Routing Manifest Reference 必须是 object")
        required = {"标识", "Skill", "文件名", "源路径", "触发", "依赖"}
        if set(raw) - (required | {"最低风险"}) or not required.issubset(raw):
            raise ValueError("Routing Manifest Reference 字段不合法")
        reference_id = str(raw["标识"])
        if not _REFERENCE_ID.fullmatch(reference_id):
            raise ValueError(f"Routing Manifest Reference Stable ID 非法：{reference_id!r}")
        if reference_id in seen_ids:
            raise ValueError(f"Routing Manifest Reference ID 重复：{reference_id}")
        seen_ids.add(reference_id)
        if str(raw["Skill"]) not in skill_names:
            raise ValueError(f"Routing Manifest Reference 指向未知 Skill：{raw['Skill']}")
        if reference_id.split(".reference.", 1)[0] != str(raw["Skill"]):
            raise ValueError(f"Routing Manifest Reference ID 与 Skill Owner 不一致：{reference_id}")
        _normalize_expression(raw["触发"], label=f"Reference {reference_id}")
        dependencies = _normalize_dependencies(raw["依赖"], path=Path(str(raw["源路径"])))
        minimum_risk = raw.get("最低风险")
        if minimum_risk is not None and str(minimum_risk) not in _RISK_ORDER:
            raise ValueError(f"Routing Manifest Reference 最低风险非法：{reference_id}")
        normalized_references.append({"标识": reference_id, "依赖": dependencies})
    reference_ids = [str(entry["标识"]) for entry in normalized_references]
    if reference_ids != sorted(reference_ids):
        raise ValueError("Routing Manifest Reference 必须按 Stable ID 稳定排序")
    for reference in normalized_references:
        unknown = sorted(set(reference["依赖"]) - seen_ids)
        if unknown:
            raise ValueError(f"Routing Manifest 存在悬空依赖：{', '.join(unknown)}")
    _assert_acyclic(normalized_references)
    expected = _sha256(_routing_material(manifest))
    if str(manifest.get("路由摘要")) != expected:
        raise ValueError("Routing Manifest 路由摘要不一致")


def serialize_routing_manifest(manifest: Mapping[str, Any]) -> bytes:
    """把已验证的私有 Routing Manifest 序列化为稳定 JSON。"""
    validate_routing_manifest(manifest)
    return _canonical_json(manifest)


def deserialize_routing_manifest(payload: bytes) -> dict[str, Any]:
    """恢复并验证私有 Routing Manifest JSON。"""
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Routing Manifest 不是合法 UTF-8 JSON") from error
    if not isinstance(decoded, dict):
        raise ValueError("Routing Manifest 顶层必须是 object")
    validate_routing_manifest(decoded)
    return decoded


def _collect_vocabulary(expression: Mapping[str, Any], target: dict[str, set[str]]) -> None:
    """从规范化表达式递归汇总公开维度取值。"""
    operator = next(iter(expression))
    value = expression[operator]
    if operator == "包含":
        target[str(value["维度"])].update(str(item) for item in value["取值"])
        return
    if operator in {"全部", "任一"}:
        for item in value:
            _collect_vocabulary(item, target)
        return
    _collect_vocabulary(value, target)


def public_route_contract(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """动态生成不包含 Reference mapping 的中文公共路由契约。"""
    validate_routing_manifest(manifest)
    vocabulary = {dimension: set() for dimension in ROUTE_DIMENSIONS}
    for skill in manifest["技能"]:
        _collect_vocabulary(skill["触发"], vocabulary)
    for reference in manifest["引用"]:
        _collect_vocabulary(reference["触发"], vocabulary)
    dimensions = {dimension: sorted(vocabulary[dimension]) for dimension in ROUTE_DIMENSIONS}
    return {
        "协议": PUBLIC_ROUTE_CONTRACT_PROTOCOL,
        "任务路由协议": TASK_ROUTE_PROTOCOL,
        "维度": dimensions,
        "维度说明": {
            dimension: f"记录任务事实中的“{dimension}”信号；取值只用于确定需要加载的规则。"
            for dimension in ROUTE_DIMENSIONS
        },
        "取值说明": {
            dimension: {value: f"表示当前任务包含“{value}”这一事实。" for value in values}
            for dimension, values in dimensions.items()
        },
        "Skill": [str(entry["Skill"]) for entry in manifest["技能"]],
    }


def validate_task_route(route: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    """依据当前公共契约校验并规范化宿主模型提交的中文 Task Route。"""
    required = {"协议", "信号", "未知项", "依据"}
    if set(route) != required:
        raise ValueError("Task Route 必须且只能包含协议、信号、未知项、依据")
    if route.get("协议") != TASK_ROUTE_PROTOCOL:
        raise ValueError(f"Task Route 协议不受支持：{route.get('协议')!r}")
    raw_dimensions = contract.get("维度")
    if not isinstance(raw_dimensions, Mapping):
        raise ValueError("公共路由契约缺少维度")
    signals = route.get("信号")
    if not isinstance(signals, Mapping):
        raise ValueError("Task Route 信号必须是 object")
    unknown_dimensions = sorted(set(str(item) for item in signals) - set(ROUTE_DIMENSIONS))
    if unknown_dimensions:
        raise ValueError(f"Task Route 使用未知维度：{', '.join(unknown_dimensions)}")
    normalized_signals: dict[str, list[str]] = {}
    for dimension in ROUTE_DIMENSIONS:
        raw_values = signals.get(dimension, [])
        if not isinstance(raw_values, list):
            raise ValueError(f"Task Route {dimension} 必须是列表")
        values = [str(item).strip() for item in raw_values]
        if any(not value for value in values) or len(values) != len(set(values)):
            raise ValueError(f"Task Route {dimension} 取值不能为空或重复")
        allowed = {str(item) for item in raw_dimensions.get(dimension, [])}
        invalid = sorted(set(values) - allowed)
        if invalid:
            raise ValueError(f"Task Route {dimension} 包含未公开取值：{', '.join(invalid)}")
        normalized_signals[dimension] = sorted(values)
    unknown = route.get("未知项")
    if not isinstance(unknown, list):
        raise ValueError("Task Route 未知项必须是列表")
    normalized_unknown = [str(item).strip() for item in unknown]
    if (
        any(item not in ROUTE_DIMENSIONS for item in normalized_unknown)
        or len(normalized_unknown) != len(set(normalized_unknown))
    ):
        raise ValueError("Task Route 未知项只能使用唯一的公开维度名")
    evidence = route.get("依据")
    if not isinstance(evidence, list):
        raise ValueError("Task Route 依据必须是列表")
    normalized_evidence = [str(item).strip() for item in evidence]
    if any(not item for item in normalized_evidence):
        raise ValueError("Task Route 依据不能为空字符串")
    return {
        "协议": TASK_ROUTE_PROTOCOL,
        "信号": normalized_signals,
        "未知项": sorted(normalized_unknown),
        "依据": normalized_evidence,
    }


def _matches(expression: Mapping[str, Any], signals: Mapping[str, set[str]]) -> bool:
    """使用原有二值求值语义判断事实充分的规范化触发表达式。"""
    operator = next(iter(expression))
    value = expression[operator]
    if operator == "包含":
        return bool(signals[str(value["维度"])] & {str(item) for item in value["取值"]})
    if operator == "全部":
        return all(_matches(item, signals) for item in value)
    if operator == "任一":
        return any(_matches(item, signals) for item in value)
    return not _matches(value, signals)


def _matches_tristate(
    expression: Mapping[str, Any],
    signals: Mapping[str, set[str]],
    unknown_dimensions: set[str],
) -> int:
    """对未知事实使用 TRUE/FALSE/UNKNOWN 三值逻辑，只扩大与未知维度真实相关的候选 Context。"""
    operator = next(iter(expression))
    value = expression[operator]
    if operator == "包含":
        dimension = str(value["维度"])
        if signals[dimension] & {str(item) for item in value["取值"]}:
            return _TRUE
        return _UNKNOWN if dimension in unknown_dimensions else _FALSE
    if operator == "全部":
        results = [_matches_tristate(item, signals, unknown_dimensions) for item in value]
        if any(result == _FALSE for result in results):
            return _FALSE
        if all(result == _TRUE for result in results):
            return _TRUE
        return _UNKNOWN
    if operator == "任一":
        results = [_matches_tristate(item, signals, unknown_dimensions) for item in value]
        if any(result == _TRUE for result in results):
            return _TRUE
        if all(result == _FALSE for result in results):
            return _FALSE
        return _UNKNOWN
    result = _matches_tristate(value, signals, unknown_dimensions)
    if result == _TRUE:
        return _FALSE
    if result == _FALSE:
        return _TRUE
    return _UNKNOWN


def _matches_owner_projection(
    expression: Mapping[str, Any],
    signals: Mapping[str, set[str]],
    unknown_dimensions: set[str],
) -> int | None:
    """只用 Owner 选择维度求值 Skill trigger；refinement 原子被投影掉但继续保留在公共词汇中。"""
    operator = next(iter(expression))
    value = expression[operator]
    if operator == "包含":
        dimension = str(value["维度"])
        if dimension in _OWNER_REFINEMENT_DIMENSIONS:
            return None
        if signals[dimension] & {str(item) for item in value["取值"]}:
            return _TRUE
        return _UNKNOWN if dimension in unknown_dimensions else _FALSE
    if operator in {"全部", "任一"}:
        results = [
            result
            for item in value
            if (result := _matches_owner_projection(item, signals, unknown_dimensions)) is not None
        ]
        if not results:
            return None
        if operator == "全部":
            if any(result == _FALSE for result in results):
                return _FALSE
            if all(result == _TRUE for result in results):
                return _TRUE
            return _UNKNOWN
        if any(result == _TRUE for result in results):
            return _TRUE
        if all(result == _FALSE for result in results):
            return _FALSE
        return _UNKNOWN
    result = _matches_owner_projection(value, signals, unknown_dimensions)
    if result is None:
        return None
    if result == _TRUE:
        return _FALSE
    if result == _FALSE:
        return _TRUE
    return _UNKNOWN


def _dependency_closure(required: set[str], references: Mapping[str, Mapping[str, Any]]) -> set[str]:
    """展开当前 required References 的传递依赖闭包。"""
    expanded = set(required)
    pending = list(sorted(required))
    while pending:
        current = pending.pop()
        for dependency in references[current]["依赖"]:
            dependency_id = str(dependency)
            if dependency_id not in expanded:
                expanded.add(dependency_id)
                pending.append(dependency_id)
    return expanded


def _minimum_risk(signals: Mapping[str, set[str]], required: Iterable[Mapping[str, Any]]) -> str:
    """计算输入风险与 required Context 风险下限的最高值。"""
    risks = [item for item in signals["风险"] if item in _RISK_ORDER]
    risks.extend(str(entry["最低风险"]) for entry in required if entry.get("最低风险") in _RISK_ORDER)
    return max(risks or ["L1"], key=lambda item: _RISK_ORDER[item])


def _evaluate_fixed_point(
    manifest: Mapping[str, Any],
    signals: dict[str, set[str]],
    *,
    unknown_dimensions: set[str] | None = None,
) -> tuple[set[str], set[str], str]:
    """执行 Owner-gated fixed-point：Skill 先按 Owner 投影选择，Reference 再在已命中 Owner 内细化。"""
    references = {str(entry["标识"]): entry for entry in manifest["引用"]}
    skill_names = {str(entry["Skill"]) for entry in manifest["技能"]}
    required_ids: set[str] = set()
    matched_skills: set[str] = (
        {CONTROL_PLANE_SKILL} if CONTROL_PLANE_SKILL in skill_names else set()
    )
    owner_unknown = unknown_dimensions or set()
    while True:
        before = (set(required_ids), set(matched_skills), set(signals["风险"]))
        for skill in manifest["技能"]:
            skill_name = str(skill["Skill"])
            if skill_name == CONTROL_PLANE_SKILL:
                continue
            owner_match = _matches_owner_projection(skill["触发"], signals, owner_unknown)
            if owner_match == _TRUE or (unknown_dimensions is not None and owner_match == _UNKNOWN):
                matched_skills.add(skill_name)
        for reference_id, reference in references.items():
            owner = str(reference["Skill"])
            if owner not in matched_skills:
                continue
            matched = (
                _matches(reference["触发"], signals)
                if unknown_dimensions is None
                else _matches_tristate(reference["触发"], signals, unknown_dimensions) != _FALSE
            )
            if matched:
                required_ids.add(reference_id)
        required_ids = _dependency_closure(required_ids, references)
        for reference_id in required_ids:
            matched_skills.add(str(references[reference_id]["Skill"]))
        minimum_risk = _minimum_risk(signals, (references[item] for item in required_ids))
        signals["风险"].add(minimum_risk)
        after = (set(required_ids), set(matched_skills), set(signals["风险"]))
        if after == before:
            break
    required_entries = [references[item] for item in sorted(required_ids)]
    return required_ids, matched_skills, _minimum_risk(signals, required_entries)


def evaluate_route(manifest: Mapping[str, Any], route: Mapping[str, Any]) -> dict[str, Any]:
    """求值 required Context；refinement facts 不直接选专业 Owner，显式 dependency 仍可跨 Skill。"""
    validate_routing_manifest(manifest)
    normalized = validate_task_route(route, public_route_contract(manifest))
    base_signals = {
        dimension: set(normalized["信号"][dimension])
        for dimension in ROUTE_DIMENSIONS
    }
    unknown_dimensions = set(normalized["未知项"])
    if not unknown_dimensions:
        required_ids, matched_skills, minimum_risk = _evaluate_fixed_point(
            manifest,
            {dimension: set(values) for dimension, values in base_signals.items()},
        )
    else:
        known_required, _, _ = _evaluate_fixed_point(
            manifest,
            {dimension: set(values) for dimension, values in base_signals.items()},
        )
        required_ids, matched_skills, minimum_risk = _evaluate_fixed_point(
            manifest,
            {dimension: set(values) for dimension, values in base_signals.items()},
            unknown_dimensions=unknown_dimensions,
        )
        all_reference_ids = {str(entry["标识"]) for entry in manifest["引用"]}
        if required_ids == all_reference_ids and known_required != all_reference_ids:
            raise ValueError(
                "当前任务事实不足以建立最小充分治理约束；请先恢复更多当前项目事实后重新建立任务约束"
            )
    return {
        "路由摘要": manifest["路由摘要"],
        "命中Skill": sorted(matched_skills),
        "必需Reference": sorted(required_ids),
        "最低风险": minimum_risk,
        "存在未知项": bool(unknown_dimensions),
    }
