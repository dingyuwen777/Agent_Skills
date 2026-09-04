"""验证统一 Issue Title / Acceptance / Closure Contract 不因模板或收尾维护而漂移。"""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
TRACEABILITY = ROOT / ".agents/skills/coding/references/17_需求来源与PR追溯治理.md"
FINALIZATION = ROOT / ".agents/skills/coding/references/23_端到端交付与合并后收尾.md"
PR_TEMPLATE = ROOT / ".github/PULL_REQUEST_TEMPLATE.md"
FORM_DIR = ROOT / ".github/ISSUE_TEMPLATE"
FORM_PROFILES = {
    "01-requirement.yml": ("需求", '[需求] '),
    "02-bug.yml": ("缺陷", '[缺陷] '),
    "03-technical-change.yml": ("技术变更", '[技术变更] '),
}


class IssueAcceptanceClosureContractTest(unittest.TestCase):
    """锁定公共 Issue Title/Acceptance Contract、平台 Profile 和真实 Closure 时序。"""

    def _read(self, path: Path) -> str:
        """读取 UTF-8 正式文本。"""
        return path.read_text(encoding="utf-8")

    def _field_block(self, text: str, field_id: str) -> str:
        """返回 Issue Form 中指定字段块，字段缺失时直接失败。"""
        marker = f"id: {field_id}"
        self.assertIn(marker, text, field_id)
        tail = text.split(marker, 1)[1]
        next_field = tail.find("\n  - type:")
        return tail if next_field < 0 else tail[:next_field]

    def test_canonical_contract_owns_issue_title_format_without_overriding_project_owner(self) -> None:
        """Issue 标题需要统一默认 Contract，但目标项目已有更强规范时继续由项目 Owner 决定。"""
        text = self._read(TRACEABILITY)
        required = (
            "Issue Title Contract",
            "[需求] <简洁目标>",
            "[缺陷] <可观察问题>",
            "[技术变更] <工程目标>",
            "标题不承载状态、优先级、Owner、分支名或重复 Issue 编号",
            "项目已有更强 Issue 标题规范",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_agent_skills_issue_profiles_use_exact_chooser_names_and_title_prefixes(self) -> None:
        """Agent_Skills 自身三类 GitHub Form 的 chooser 名称与 title 前缀必须统一。"""
        for filename, (chooser_name, title_prefix) in FORM_PROFILES.items():
            with self.subTest(filename=filename):
                text = self._read(FORM_DIR / filename)
                first_lines = text.splitlines()[:4]
                self.assertIn(f"name: {chooser_name}", first_lines)
                self.assertIn(f'title: "{title_prefix}"', first_lines)

    def test_canonical_contract_owns_acceptance_state_and_evidence_mapping(self) -> None:
        """Acceptance Criteria 应是 Requirement Source 的最终状态 Owner，而不是 Change 的第二套需求。"""
        text = self._read(TRACEABILITY)
        required = (
            "Acceptance Criteria 是 Requirement Source 的最终完成状态 Owner",
            "AC1 / AC2 / ...",
            "Change 不创建第二套需求",
            "satisfied / not_applicable / deferred / unresolved",
            "直接 Evidence",
            "新的正式 Owner",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_satisfied_ac_requires_evidence_sufficiency_gate(self) -> None:
        """AC 只有在充分且匹配的直接 Evidence 下才能 satisfied/勾选。"""
        text = self._read(TRACEABILITY)
        required = (
            "Evidence Sufficiency Gate",
            "充分、直接且与该 AC 匹配",
            "同一对象、行为、条件",
            "revision/commit",
            "必要环境",
            "实际证明了什么",
            "CI Green",
            "PR merge",
            "Change `done`",
            "不得勾选",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_issue_create_or_update_requires_live_reread_and_contract_validation(self) -> None:
        """创建或实质更新 Requirement Source 后必须验证平台真实 live 对象。"""
        text = self._read(TRACEABILITY)
        required = (
            "Issue Creation / Update Live Validation Gate",
            "创建或实质更新 GitHub Requirement Source",
            "重新读取平台上的真实 live Requirement Source",
            "未完成这次写后重读",
            "不得把该 Requirement Source 视为 `resolved`",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_github_acceptance_rejects_numbered_list_and_comment_only_state(self) -> None:
        """GitHub 的普通编号列表或 comment-only Evidence 不能冒充可回写 Acceptance 状态。"""
        text = self._read(TRACEABILITY)
        required = (
            "GitHub 默认 Acceptance 状态必须使用可回写 task list",
            "`- [ ] AC1：...`",
            "普通 `1. 2. 3.` 编号列表",
            "不能冒充 Acceptance 状态 Owner",
            "comment-only Evidence",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_live_validation_normalizes_only_when_requirement_semantics_are_preserved(self) -> None:
        """live Issue 只有在保持原需求语义时才可规范化，否则必须失败关闭。"""
        text = self._read(TRACEABILITY)
        required = (
            "保持原 Requirement 语义",
            "再次重新读取",
            "`blocked/unresolved`",
            "无写权限",
            "并发漂移",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_delivery_checkpoints_revalidate_live_requirement_source_contract(self) -> None:
        """PR、Review、Ready 与 merge preflight 都必须重新验证 live Requirement Source。"""
        text = self._read(TRACEABILITY)
        required = (
            "Delivery Live Requirement Source Validation",
            "创建或更新 PR",
            "正式 Review",
            "PR Ready / 可合并",
            "merge preflight",
            "重新读取当前 live Requirement Source",
            "旧 `resolved` 结论失效",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_open_legacy_issue_can_be_normalized_without_bulk_rewriting_closed_history(self) -> None:
        """仍作为当前来源的 open Issue 可有界规范化，但 closed 历史不做猜测性批量迁移。"""
        text = self._read(TRACEABILITY)
        required = (
            "仍 open 且继续作为当前 Requirement Source",
            "原有验收顺序",
            "已关闭历史 Issue",
            "不批量迁移",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_live_hardening_preserves_existing_issue_creation_and_type_contracts(self) -> None:
        """新增 live gate 不能删掉原 Issue 建立条件、类型职责和未知项边界。"""
        text = self._read(TRACEABILITY)
        required = (
            "没有更强且已被正式采用的等价需求载体",
            "需要可追溯协作的 L2/L3",
            "创建 Issue 的 GitHub 写授权",
            "新增或改变用户、调用方或系统可以观察到的能力",
            "当前可观察行为偏离已经确认的期望行为",
            "主要目标是架构、重构、基础设施、CI、性能、安全、依赖、部署、维护性或工程质量",
            "关键未知项会影响范围",
            "不能因为表单提交成功就自动被视为 `resolved`",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_live_hardening_preserves_pr_split_and_delivery_authorization_semantics(self) -> None:
        """压缩上下文不能丢失多 PR 追溯、授权连续性和 Review PASS 的既有语义。"""
        traceability = self._read(TRACEABILITY)
        for marker in (
            "一个 Issue 拆成多个 PR",
            "每个 PR 都可以写同一个 `Requirement-Source`",
        ):
            self.assertIn(marker, traceability, marker)

        finalization = self._read(FINALIZATION)
        for marker in (
            "不把同一已确认交付范围机械拆成每一步重新询问",
            "Review PASS 表示 Review 当前结论没有阻塞交付",
        ):
            self.assertIn(marker, finalization, marker)

    def test_github_closure_requires_checkbox_writeback_reread_and_closed_confirmation(self) -> None:
        """GitHub Issue 必须真实同步 task list，再关闭并再次确认 closed。"""
        text = self._read(TRACEABILITY)
        ordered = (
            "逐条 Requirement → Evidence 审计",
            "`- [ ]` → `- [x]`",
            "写回 Issue body",
            "重新读取 Issue",
            "执行 close",
            "再次读取 Issue",
        )
        positions = []
        for marker in ordered:
            self.assertIn(marker, text, marker)
            positions.append(text.index(marker))
        self.assertEqual(positions, sorted(positions), "Closure 写回/重读/关闭顺序发生漂移")
        self.assertIn("仍适用的未勾选项", text)
        self.assertIn("不得关闭", text)
        self.assertIn("comment-only Evidence", text)
        self.assertIn("不能代替 Issue body Acceptance 状态", text)

    def test_three_issue_profiles_share_acceptance_and_validation_contract(self) -> None:
        """三类 GitHub Form 应共享验收标准、稳定 AC 示例和验证要求字段。"""
        for filename in FORM_PROFILES:
            with self.subTest(filename=filename):
                text = self._read(FORM_DIR / filename)
                acceptance = self._field_block(text, "acceptance_criteria")
                validation = self._field_block(text, "validation_requirements")
                self.assertIn("label: 验收标准", acceptance)
                self.assertIn("- [ ] AC1：", acceptance)
                self.assertIn("required: true", acceptance)
                self.assertIn("label: 验证要求", validation)
                self.assertIn("required: true", validation)

    def test_pr_template_delays_auto_close_until_post_merge_closure_audit(self) -> None:
        """需要 merge 后证据时 PR 不得用 closing keyword 抢先关闭 Requirement Source。"""
        text = self._read(PR_TEMPLATE)
        required = (
            "需要 post-merge evidence",
            "不得使用 `Closes` / `Fixes` / `Resolves`",
            "Closure Audit",
            "Requirement-Source:",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_develop_and_deliver_validates_live_source_before_branch_and_change(self) -> None:
        """端到端开发在建分支/Change 前必须先确认新建或复用 Requirement Source 的 live Contract。"""
        text = self._read(FINALIZATION)
        ordered = (
            "创建或复用 Requirement Source / Issue",
            "通过 live Requirement Source Contract Validation",
            "建立当前任务分支与 Change",
        )
        positions = []
        for marker in ordered:
            self.assertIn(marker, text, marker)
            positions.append(text.index(marker))
        self.assertEqual(positions, sorted(positions), "Requirement Source live validation 未位于分支/Change 前")

    def test_finalization_orders_acceptance_sync_before_close_and_cleanup(self) -> None:
        """端到端收尾必须先同步 Acceptance，再 close，最后 cleanup/report。"""
        text = self._read(FINALIZATION)
        ordered = (
            "Acceptance checklist 同步",
            "写后重新读取 Requirement Source",
            "关闭 Requirement Source",
            "close 后再次读取 Requirement Source",
            "分支清理",
            "最终交付报告",
        )
        positions = []
        for marker in ordered:
            self.assertIn(marker, text, marker)
            positions.append(text.index(marker))
        self.assertEqual(positions, sorted(positions), "Post-Merge Finalization 顺序发生漂移")
        self.assertIn("blocked/incomplete", text)

    def test_target_repository_default_contract_does_not_require_installed_github_forms(self) -> None:
        """目标仓库未复制 GitHub Form 时，Agent 默认 Issue lifecycle 仍必须生效。"""
        text = self._read(TRACEABILITY)
        required = (
            "GitHub Form 只是可选 UI Profile",
            "没有安装或复制 Agent_Skills GitHub Forms",
            "创建、规范、更新和关闭 Requirement Source",
            "仍执行本节默认 Contract",
            "落地 Issue Form 不是 Agent 行为 Contract 生效的前置条件",
            "每个仓库继续使用自己的 Requirement/Change/PR 生命周期",
        )
        for item in required:
            self.assertIn(item, text, item)

    def test_contract_is_cross_platform_without_forcing_github_forms(self) -> None:
        """统一的是语义 Contract，不是把 GitHub YAML 强制复制给所有项目。"""
        text = self._read(TRACEABILITY)
        required = (
            "公共 Contract + 类型 Profile + 平台 Profile",
            "项目已有更强 Issue/工单模板",
            "不强制复制 Agent_Skills 的 GitHub Issue Form",
            "等价 Acceptance/Closure 状态",
        )
        for marker in required:
            self.assertIn(marker, text, marker)


if __name__ == "__main__":
    unittest.main()
