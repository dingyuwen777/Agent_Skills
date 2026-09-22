"""验证 Issue/PR creation-time canonical Core、Appendix 与 Acceptance 边界。"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PATH = ROOT / ".agents/skills/coding/scripts/governance_contract.py"


def _load_module(path: Path, name: str):
    """从真实仓库路径加载治理 Contract 模块用于隔离回归。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = _load_module(CONTRACT_PATH, "governance_creation_strictness_subject")


def _issue_sections() -> list[tuple[str, str]]:
    """按当前 canonical Technical Change Profile 生成合法 Issue Core fixture。"""
    profile = CONTRACT.resolve_issue_profile("[技术变更] strict create")
    sections: list[tuple[str, str]] = []
    for heading in profile.required_headings:
        if heading == "重复检查":
            body = "- [x] 已搜索重复事项"
        elif heading == "验收标准":
            body = "- [ ] AC1：创建实例满足当前 canonical Contract\n- [ ] AC2：Core 后 Appendix 可保留"
        else:
            body = f"{heading} 的真实候选内容。"
        sections.append((heading, body))
    return sections


def _render_issue(sections: list[tuple[str, str]], appendix: str = "") -> str:
    """把 Issue Core sections 渲染成 GitHub Markdown body。"""
    body = "\n\n".join(f"## {heading}\n{content}" for heading, content in sections)
    if appendix:
        body += "\n\n" + appendix
    return body + "\n"


def _pr_sections() -> list[tuple[str, str]]:
    """按当前 canonical PR Profile 生成合法 PR Core fixture。"""
    profile = CONTRACT.load_pr_profile()
    sections: list[tuple[str, str]] = []
    for heading in profile.required_headings:
        if heading == "Requirement Source":
            body = "Requirement-Source: #292"
        else:
            body = f"{heading} 的当前事实。"
        sections.append((heading, body))
    return sections


def _render_pr(sections: list[tuple[str, str]], appendix: str = "") -> str:
    """把 PR Core sections 渲染成 GitHub Markdown body。"""
    body = "\n\n".join(f"## {heading}\n{content}" for heading, content in sections)
    if appendix:
        body += "\n\n" + appendix
    return body + "\n"


class GovernanceCreationStrictnessTests(unittest.TestCase):
    """锁定 create 模式强约束；历史 live 兼容不能降低 create。"""

    def test_issue_canonical_core_and_lifecycle_appendix_pass(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        body = _render_issue(
            _issue_sections(),
            "## Closure Audit\n当前仅作为 Core 后 lifecycle appendix fixture。",
        )
        self.assertEqual(
            CONTRACT.validate_issue_instance(
                "[技术变更] strict create",
                body,
                mode="create",
            ),
            [],
        )

    def test_issue_missing_required_section_fails(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = [(h, c) for h, c in _issue_sections() if h != "目标状态"]
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            _render_issue(sections),
            mode="create",
        )
        self.assertTrue(any("目标状态" in error for error in errors), errors)

    def test_issue_duplicate_required_section_fails(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = _issue_sections()
        sections.insert(3, ("当前状态", "重复 section"))
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            _render_issue(sections),
            mode="create",
        )
        self.assertTrue(any("重复" in error and "当前状态" in error for error in errors), errors)

    def test_issue_out_of_order_core_fails(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = _issue_sections()
        sections[2], sections[3] = sections[3], sections[2]
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            _render_issue(sections),
            mode="create",
        )
        self.assertTrue(any("strict" in error.lower() or "严格顺序" in error for error in errors), errors)

    def test_issue_custom_section_inside_core_fails(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = _issue_sections()
        sections.insert(4, ("Current Evidence", "不能插入 Core。"))
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            _render_issue(sections),
            mode="create",
        )
        self.assertTrue(any("Core" in error for error in errors), errors)

    def test_issue_free_structure_before_canonical_core_fails(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        body = "## 自由结构\n先写自己的模板。\n\n" + _render_issue(_issue_sections())
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            body,
            mode="create",
        )
        self.assertTrue(any("Core" in error for error in errors), errors)

    def test_issue_required_checkbox_must_be_checked_on_create(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = [
            (h, "- [ ] 未勾选" if h == "重复检查" else c)
            for h, c in _issue_sections()
        ]
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            _render_issue(sections),
            mode="create",
        )
        self.assertTrue(any("checkbox" in error for error in errors), errors)

    def test_issue_acceptance_outside_acceptance_section_cannot_satisfy_contract(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = [
            (h, "尚未提供 task list" if h == "验收标准" else c)
            for h, c in _issue_sections()
        ]
        body = _render_issue(
            sections,
            "## Closure Audit\n- [ ] AC1：Appendix 中的 AC 不能冒充验收标准。",
        )
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            body,
            mode="create",
        )
        self.assertTrue(any("验收标准 section" in error for error in errors), errors)

    def test_issue_acceptance_ids_must_be_continuous(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = [
            (h, "- [ ] AC1：第一项\n- [ ] AC3：第三项" if h == "验收标准" else c)
            for h, c in _issue_sections()
        ]
        errors = CONTRACT.validate_issue_instance(
            "[技术变更] strict create",
            _render_issue(sections),
            mode="create",
        )
        self.assertTrue(any("连续且唯一" in error for error in errors), errors)

    def test_live_mode_keeps_pre_creation_contract_checkbox_compatibility(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = [(h, c) for h, c in _issue_sections() if h != "重复检查"]
        self.assertEqual(
            CONTRACT.validate_issue_instance(
                "[技术变更] historical live",
                _render_issue(sections),
                mode="live",
            ),
            [],
        )

    def test_pr_canonical_core_and_lifecycle_appendix_pass(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        body = _render_pr(
            _pr_sections(),
            "## Final Review\nNO_FINDINGS_WITHIN_SCOPE",
        )
        self.assertEqual(CONTRACT.validate_pr_instance(body, mode="create"), [])

    def test_pr_missing_duplicate_out_of_order_and_interleaved_core_fail(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        cases: list[list[tuple[str, str]]] = []
        base = _pr_sections()
        cases.append([(h, c) for h, c in base if h != "目标"])
        duplicate = list(base)
        duplicate.insert(3, ("目标", "duplicate"))
        cases.append(duplicate)
        out_of_order = list(base)
        out_of_order[2], out_of_order[3] = out_of_order[3], out_of_order[2]
        cases.append(out_of_order)
        interleaved = list(base)
        interleaved.insert(4, ("Current Evidence", "不能插入 Core"))
        cases.append(interleaved)
        for sections in cases:
            with self.subTest(headings=[heading for heading, _ in sections]):
                self.assertTrue(CONTRACT.validate_pr_instance(_render_pr(sections), mode="create"))

    def test_pr_free_structure_before_core_fails(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        body = "## 自由结构\n先写自由模板。\n\n" + _render_pr(_pr_sections())
        errors = CONTRACT.validate_pr_instance(body, mode="create")
        self.assertTrue(any("Core" in error for error in errors), errors)

    def test_pr_requirement_source_placeholders_fail(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        for invalid in ("#<Issue>", "", "TBD", "TODO", "待确认", "无"):
            sections = [
                (
                    h,
                    f"Requirement-Source: {invalid}" if h == "Requirement Source" else c,
                )
                for h, c in _pr_sections()
            ]
            with self.subTest(invalid=invalid):
                errors = CONTRACT.validate_pr_instance(_render_pr(sections), mode="create")
                self.assertTrue(any("占位值" in error for error in errors), errors)

    def test_pr_multiple_stable_requirement_sources_pass(self) -> None:
        """验证 creation-time Governance Contract 的对应正反例。"""
        sections = [
            (
                h,
                "Requirement-Source: #292\nRequirement-Source: docs/spec.md"
                if h == "Requirement Source"
                else c,
            )
            for h, c in _pr_sections()
        ]
        self.assertEqual(CONTRACT.validate_pr_instance(_render_pr(sections), mode="create"), [])


if __name__ == "__main__":
    unittest.main()
