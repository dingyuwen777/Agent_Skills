from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
import unittest
from collections.abc import Iterable


_SCOPE_RANK = {
    "change_only": 0,
    "governance": 1,
    "content": 2,
    "package": 3,
}

_PACKAGE_EXACT_PATHS = {
    ".gitattributes",
    ".github/scripts/runtime_package_scope.py",
    ".github/workflows/skill-tests.yml",
    # 保留已删除旧 Workflow 的路径；若意外恢复/删除发生变化，仍按 CI/package 控制面 fail-closed。
    ".github/workflows/runtime-package-tests.yml",
    ".github/workflows/release.yml",
    "scripts/build_runtime.py",
    "scripts/runtime_mcp_smoke.py",
}

_ARCHIVE_CONTROL_PATHS = {
    ".github/scripts/archive_change_after_merge.py",
    ".github/workflows/change-archive.yml",
}

_GOVERNANCE_EXACT_PATHS = {
    "AGENTS.md",
    ".agents/MAINTENANCE.md",
    ".gitignore",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/scripts/check_pr_requirement_source.py",
}

_HUMAN_DOC_PATHS = {
    "README.md",
    "runtime/README.md",
}

_CONTENT_EXACT_PATHS = {
    "USAGE.md",
}

_CHANGE_ONLY_PREFIX = ".agents/changes/"
_TEST_PREFIX = ".agents/skills/coding/tests/"
_ISSUE_TEMPLATE_PREFIX = ".github/ISSUE_TEMPLATE/"

_CI_SELF_TESTS = {
    "test_archive_ci_runtime_lifecycle.py",
    "test_ci_ready_evidence_order.py",
    "test_ci_workflow_minimal_sufficiency.py",
    "test_network_and_workflow_governance.py",
    "test_repository_change_archive_automation.py",
    "test_runtime_package_scope.py",
}

_GROUP_TEST_FILES: dict[str, tuple[str, ...]] = {
    "governance": (
        "test_archive_ci_runtime_lifecycle.py",
        "test_change_repository_ownership.py",
        "test_change_template_chinese_yaml.py",
        "test_ci_ready_evidence_order.py",
        "test_delivery_archive_governance.py",
        "test_issue_acceptance_closure_contract.py",
        "test_issue_forms_contract.py",
        "test_minimal_sufficient_governance.py",
        "test_network_and_workflow_governance.py",
        "test_planning_contract.py",
        "test_pr_requirement_source.py",
        "test_pr_requirement_traceability.py",
        "test_ready_check.py",
        "test_repository_change_archive_automation.py",
        "test_repository_l1_fast_path.py",
    ),
    "human_docs": (
        "test_bootstrap_fact_sources.py",
        "test_docs_ci_fast_path.py",
        "test_markdown_navigation_links.py",
        "test_project_governance_bootstrap.py",
        "test_repository_structure.py",
    ),
    "release_surface": (
        "test_archive_ci_runtime_lifecycle.py",
        "test_project_governance_bootstrap.py",
        "test_release_only_repository_surface.py",
        "test_release_platform_zips.py",
    ),
    "router": (
        "test_coding_progressive_disclosure.py",
        "test_dynamic_skill_distribution.py",
        "test_owner_gated_routing.py",
        "test_reference_numbering.py",
        "test_route_context_budget.py",
        "test_router_skill_migration.py",
        "test_routing_conformance.py",
        "test_shared_root_router_contract.py",
        "test_skill_owner_isolation.py",
        "test_skill_router_single_source.py",
        "test_source_runtime_context_conformance.py",
    ),
    "docs_skill": (
        "test_docs_ci_fast_path.py",
        "test_docs_skill.py",
    ),
    "figma_skill": (
        "test_figma_capability_gap_review.py",
        "test_figma_skill.py",
        "test_frontend_design_to_code.py",
    ),
    "testing_skill": (
        "test_review_test_adequacy_owner_reachability.py",
        "test_testing_runtime_projection.py",
        "test_testing_skill.py",
    ),
    "review_skill": (
        "test_review_skill.py",
        "test_review_test_adequacy_owner_reachability.py",
    ),
    "ci_self": tuple(sorted(_CI_SELF_TESTS)),
}


@dataclass(frozen=True)
class EvidenceSelection:
    """描述一次 changed scope 需要的最小充分 CI Evidence。"""

    runtime_scope: str
    semantic_profile: str
    semantic_groups: tuple[str, ...]
    test_files: tuple[str, ...]
    runtime_dependencies_required: bool
    compile_required: bool
    cli_smoke_required: bool
    semantic_tests_required: bool
    full_required: bool


class _SelectionBuilder:
    """累积多个 changed path 的 Evidence，并保证只向更强责任单调扩大。"""

    def __init__(self) -> None:
        self.runtime_scope = "change_only"
        self.groups: set[str] = set()
        self.direct_tests: set[str] = set()
        self.runtime_dependencies_required = False
        self.compile_required = False
        self.cli_smoke_required = False
        self.full_required = False
        self.found_path = False

    def promote_scope(self, scope: str) -> None:
        """把 Runtime scope 提升到当前路径要求的最高档位。"""
        if _SCOPE_RANK[scope] > _SCOPE_RANK[self.runtime_scope]:
            self.runtime_scope = scope

    def add_groups(self, *groups: str) -> None:
        """加入语义测试组并保持集合去重。"""
        self.groups.update(groups)

    def require_full(self, *, package: bool) -> None:
        """对共享或未知边界启用完整 semantic；仅 package 自动增加 Runtime compile/smoke。"""
        self.full_required = True
        self.runtime_dependencies_required = True
        self.promote_scope("package" if package else "content")
        if package:
            self.compile_required = True
            self.cli_smoke_required = True

    def add_path(self, path: str) -> None:
        """根据单个仓库路径把对应 Evidence 责任并入当前选择。"""
        normalized = path.strip()
        if not normalized:
            return
        self.found_path = True

        if normalized in _PACKAGE_EXACT_PATHS:
            self.require_full(package=True)
            return

        if normalized.startswith("runtime/") and normalized != "runtime/README.md":
            self.require_full(package=True)
            return

        if normalized.startswith("scripts/"):
            self.require_full(package=True)
            return

        if normalized.startswith(".github/workflows/"):
            if normalized in _ARCHIVE_CONTROL_PATHS:
                self.promote_scope("governance")
                self.add_groups("governance", "ci_self")
                return
            self.require_full(package=True)
            return

        if normalized.startswith(".github/scripts/"):
            if normalized in _ARCHIVE_CONTROL_PATHS:
                self.promote_scope("governance")
                self.add_groups("governance", "ci_self")
                self.compile_required = True
                return
            if normalized == ".github/scripts/check_pr_requirement_source.py":
                self.promote_scope("governance")
                self.add_groups("governance")
                self.compile_required = True
                self.cli_smoke_required = True
                return
            self.require_full(package=True)
            return

        if normalized.startswith(_CHANGE_ONLY_PREFIX):
            return

        if normalized in _HUMAN_DOC_PATHS:
            self.promote_scope("governance")
            self.add_groups("human_docs")
            return

        if normalized in _CONTENT_EXACT_PATHS:
            self.promote_scope("content")
            self.add_groups("human_docs", "release_surface")
            return

        if normalized in _GOVERNANCE_EXACT_PATHS or normalized.startswith(_ISSUE_TEMPLATE_PREFIX):
            self.promote_scope("governance")
            self.add_groups("governance")
            return

        if normalized == ".agents/skills/ENTRY.md" or normalized.startswith(
            ".agents/skills/router/"
        ):
            self.require_full(package=False)
            return

        if normalized == ".agents/skills/coding/scripts/ready_check.py":
            self.require_full(package=False)
            self.compile_required = True
            self.cli_smoke_required = True
            return

        if normalized == ".agents/skills/coding/scripts/coding.py":
            self.require_full(package=False)
            self.compile_required = True
            self.cli_smoke_required = True
            return

        if normalized.startswith(".agents/skills/coding/") and not normalized.startswith(
            _TEST_PREFIX
        ):
            self.require_full(package=False)
            return

        professional_groups = {
            ".agents/skills/docs/": "docs_skill",
            ".agents/skills/figma/": "figma_skill",
            ".agents/skills/testing/": "testing_skill",
            ".agents/skills/review/": "review_skill",
        }
        for prefix, group in professional_groups.items():
            if normalized.startswith(prefix):
                self.promote_scope("content")
                self.add_groups("router", group)
                self.runtime_dependencies_required = True
                return

        if normalized.startswith(".agents/skills/"):
            self.require_full(package=False)
            return

        if normalized.startswith(_TEST_PREFIX):
            name = Path(normalized).name
            if normalized.startswith(f"{_TEST_PREFIX}fixtures/"):
                self.require_full(package=False)
                return
            if name in _CI_SELF_TESTS:
                self.require_full(package=True)
                return
            if name.startswith("test_") and name.endswith(".py"):
                self.promote_scope("content")
                self.direct_tests.add(name)
                self.runtime_dependencies_required = True
                return
            self.require_full(package=False)
            return

        if normalized.endswith(".md"):
            self.promote_scope("governance")
            self.add_groups("human_docs")
            return

        # 未识别机器/仓库路径不能因为优化成本静默变轻。
        self.require_full(package=True)

    def build(self) -> EvidenceSelection:
        """生成稳定、可序列化的最终 EvidenceSelection。"""
        if not self.found_path:
            self.require_full(package=True)

        if self.full_required:
            test_files = ("*",)
            semantic_groups = ("full",)
            semantic_profile = "full"
        else:
            selected: set[str] = set(self.direct_tests)
            for group in self.groups:
                selected.update(_GROUP_TEST_FILES[group])
            test_files = tuple(sorted(selected))
            semantic_groups = tuple(sorted(self.groups))
            if self.runtime_scope == "change_only" and not test_files:
                semantic_profile = "change_only"
            elif self.direct_tests and not self.groups:
                semantic_profile = "test_only"
            elif self.groups <= {"human_docs", "release_surface"}:
                semantic_profile = "human_docs"
            elif self.groups <= {"governance", "ci_self"}:
                semantic_profile = "governance"
            else:
                semantic_profile = "content_targeted"

        semantic_tests_required = bool(test_files)
        if self.runtime_scope != "change_only" and not semantic_tests_required:
            raise ValueError("non-change-only scope selected no semantic Evidence")

        return EvidenceSelection(
            runtime_scope=self.runtime_scope,
            semantic_profile=semantic_profile,
            semantic_groups=semantic_groups,
            test_files=test_files,
            runtime_dependencies_required=self.runtime_dependencies_required,
            compile_required=self.compile_required,
            cli_smoke_required=self.cli_smoke_required,
            semantic_tests_required=semantic_tests_required,
            full_required=self.full_required,
        )


def select_evidence(paths: Iterable[str]) -> EvidenceSelection:
    """根据 changed paths 返回风险驱动、fail-closed 的多轴 CI Evidence。"""
    builder = _SelectionBuilder()
    for path in paths:
        builder.add_path(path)
    return builder.build()


def classify_path(path: str) -> str:
    """兼容旧调用：返回单个路径的 Runtime package scope。"""
    return select_evidence([path]).runtime_scope


def classify_paths(paths: Iterable[str]) -> str:
    """兼容旧调用：返回多个路径合并后的 Runtime package scope。"""
    return select_evidence(paths).runtime_scope


def _run_selected_tests(*, root: Path, selection_path: Path) -> int:
    """按 selector 输出加载已有 unittest 文件，不创建第二套测试框架。"""
    payload = json.loads(selection_path.read_text(encoding="utf-8"))
    test_files = payload.get("test_files")
    if not isinstance(test_files, list) or not test_files:
        raise SystemExit("selection 没有可执行 test_files")

    test_dir = root / ".agents/skills/coding/tests"
    loader = unittest.TestLoader()
    if test_files == ["*"]:
        suite = loader.discover(str(test_dir), pattern="test_*.py")
    else:
        suite = unittest.TestSuite()
        for name in test_files:
            if not isinstance(name, str) or Path(name).name != name:
                raise SystemExit(f"非法测试文件名：{name!r}")
            path = test_dir / name
            if not path.is_file():
                raise SystemExit(f"selector 选择了不存在的测试：{name}")
            suite.addTests(loader.discover(str(test_dir), pattern=name))

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def _build_parser() -> argparse.ArgumentParser:
    """创建 selector / targeted-test runner 的命令行解析器。"""
    parser = argparse.ArgumentParser(
        description="按 changed paths 选择 Agent_Skills 最小充分 CI Evidence。"
    )
    parser.add_argument("--json", action="store_true", help="输出完整 Evidence Selection JSON")
    parser.add_argument("--run-selected-tests", type=Path, help="执行指定 selection JSON 中的测试")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="仓库根目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    """默认兼容输出 runtime_scope；--json 输出多轴 Evidence；也可执行 selected tests。"""
    args = _build_parser().parse_args(argv)
    if args.run_selected_tests is not None:
        return _run_selected_tests(root=args.root.resolve(), selection_path=args.run_selected_tests)

    selection = select_evidence(line.rstrip("\n") for line in sys.stdin)
    if args.json:
        print(json.dumps(asdict(selection), ensure_ascii=False, sort_keys=True))
    else:
        print(selection.runtime_scope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
