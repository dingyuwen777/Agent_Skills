---
schema: coding-change/v1
id: CHG-20260903-144449-issue-acceptance-closure-contract
title: 统一 Issue 验收标准与 Closure Audit 回写契约
level: L3
status: ready_for_review
owner: dingyuwen777
branch: chg/issue-acceptance-closure-contract
created: 2026-09-03
updated: 2026-09-03
completion_gate: required
depends_on: []
affected_areas:
  - issue-governance
  - requirement-traceability
  - post-merge-finalization
  - issue-forms
  - issue-title-contract
  - pr-template
  - skill-mutation
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .github/ISSUE_TEMPLATE/01-requirement.yml
  - .github/ISSUE_TEMPLATE/02-bug.yml
  - .github/ISSUE_TEMPLATE/03-technical-change.yml
  - .github/PULL_REQUEST_TEMPLATE.md
  - .agents/skills/coding/tests/test_issue_forms_contract.py
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
  - .agents/skills/coding/tests/test_pr_requirement_source.py
  - .agents/skills/coding/tests/test_network_and_workflow_governance.py
  - .agents/skills/coding/tests/test_issue_acceptance_closure_contract.py
contracts:
  - Agent Skills Issue Title Contract
  - Agent Skills Issue Acceptance Contract
  - Agent Skills Requirement Closure Contract
data_changes: []
---

# 目标

统一 Agent_Skills 自身和被 Agent_Skills 治理项目在 Requirement Source / Issue 生命周期中的默认公共 Contract：Issue 类型/标题、Acceptance Criteria、验证要求与 Closure Audit 使用稳定语义。Acceptance Criteria 是最终完成状态 Owner；Change 只承担 Evidence Ledger，PR 只承担交付关系；Closure Audit 必须用充分、直接且匹配的 Evidence 逐项验收并回写 Requirement Source。

GitHub 默认使用稳定 `AC1/AC2/...` task list，并执行 `[ ] → [x] → write → re-read → close → re-read`。项目有更强 Issue/Ticket/Title/Closure Owner 时优先遵守；没有更强规则时，即使未复制 Agent_Skills GitHub Forms，Agent 行为仍执行同一默认 Contract。AIMA_UGC 作为真实业务仓库 Profile 验证，由其自身 #319 / Change / PR #320 独立承载。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/184

实现 PR：https://github.com/dingyuwen777/Agent_Skills/pull/185

AIMA 跨仓验证 Owner：https://github.com/dingyuwen777/AIMA_UGC/issues/319

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Acceptance Criteria 是最终完成状态 Owner，使用稳定 AC ID 与显式状态语义 | #184 / AC1 | satisfied | ref17 `Issue Acceptance Contract` 明确 final Owner、稳定 `AC1 / AC2 / ...` 与 `satisfied / not_applicable / deferred / unresolved`；`test_canonical_contract_owns_acceptance_state_and_evidence_mapping` 在 Green suite 通过。 |
| R2 | 每个 AC 只有在充分、直接且匹配的 Evidence 下才能 satisfied / 打勾 | #184 / AC2 | satisfied | ref17 `Evidence Sufficiency Gate` 明确同一对象/行为/条件、revision/commit、必要环境和实际证明内容；明确 CI Green、测试存在/数量、PR merge、Change done 不能单独证明 AC；Evidence Sufficiency regression 通过。 |
| R3 | GitHub Closure Audit 强制逐项 Evidence、checklist 写回、重读、close 后再读，未完成项阻止关闭 | #184 / AC3 | satisfied | ref17 固定逐条 Requirement→Evidence、`- [ ]`→`- [x]`、写回、重读、close、再读；`test_github_closure_requires_checkbox_writeback_reread_and_closed_confirmation` 通过。 |
| R4 | Change 直接追踪上游 AC 和 direct Evidence，不创建第二套需求 | #184 / AC4 | satisfied | ref17 明确 `Change 不创建第二套需求`；本 Change 直接使用 `#184 / ACx` 作为来源并逐项记录 Evidence。 |
| R5 | 三类 Issue Form 统一验收标准、稳定 AC 示例和验证要求，同时保留类型专项字段 | #184 / AC5 | satisfied | 三类 Form 均统一 `acceptance_criteria`、`label: 验收标准`、`AC1` task-list 示例、`validation_requirements / 验证要求` 且 required；Issue Form contract regressions 通过。 |
| R6 | 需要 post-merge evidence 时 PR 禁止提前 auto-close | #184 / AC6 | satisfied | PR Template 明确需要 post-merge evidence 时不得使用 `Closes / Fixes / Resolves`，只保留 `Requirement-Source`，由 Closure Audit 后关闭；PR-template regression 通过。 |
| R7 | Post-Merge Finalization 固定 Acceptance 同步、写后重读、close 后再读，再 cleanup/report | #184 / AC7 | satisfied | ref23 固定 `Closure Audit → Acceptance checklist 同步 → 写后重读 → close → close 后再读 → 分支清理 → 最终报告`；顺序 regression 通过，失败保持 `blocked/incomplete`。 |
| R8 | 通用 Contract 跨项目/跨平台，项目更强 Owner 优先，不强制安装 GitHub Form | #184 / AC8 | satisfied | ref17 明确 `公共 Contract + 类型 Profile + 平台 Profile`、项目已有 Owner 优先、非 GitHub 使用等价 Acceptance/Closure 状态、不强制复制 Forms；cross-platform regression 通过。 |
| R9 | Agent_Skills 三类 chooser/title 使用统一默认格式且标题不承载额外状态元数据 | #184 / AC9 | satisfied | 三类 Form 已统一为 `需求/[需求] `、`缺陷/[缺陷] `、`技术变更/[技术变更] `；ref17 Title Contract 明确标题不承载状态/优先级/Owner/分支/重复 Issue 编号；title regression 通过。 |
| R10 | 永久回归防止 Title/AC/Evidence/Closure/auto-close/Finalization 与 Context Budget 漂移 | #184 / AC10 | satisfied | PR head `dd907409...` 的 Skill Tests #1066 / run `33727965339` 中 399 项 self-contained tests 全部通过；一次 Git Delivery Context 超预算 515 bytes 被永久预算测试阻止后没有抬阈值，而是等价压缩重复 Profile 文本，route-context-budget 恢复 Green。Runtime Package #356 / run `33727965265` governance scope Gate success，三平台 binary jobs skipped。 |
| R11 | Review、PR final-head、guarded merge、main-fresh、Change archive、archive-main fresh 与最终 Issue Closure 完整闭环 | #184 / AC11 | explicitly_deferred | 独立 A1/A2 Review 已 `NO_FINDINGS_WITHIN_SCOPE`；其余 merge/main/archive/closure evidence 必须由后续真实 revision 取得，不能在 merge 前伪造。 |
| R12 | 无更强项目规则时目标仓库即使未复制 GitHub Forms 也使用默认 Contract，并由 AIMA 真实 Profile 验证 | #184 / AC12 | explicitly_deferred | 通用无-Form 默认行为已进入 ref17 并由 regression 保护；真实业务仓库 Profile 由 AIMA_UGC #319 / PR #320 / 独立 Change 承载，只有 AIMA 自身 final CI、merge、main-fresh、archive、#319 Closure Audit 完成后才能最终 satisfied。 |

# Red / Green 证据

Red head `a29e0b11694c32888f6e9eebb8f366029cbbd88f` 只包含 Change + 新 Closure Contract 回归。Skill Tests #1052 / run `33724854183` 在旧 canonical 实现上出现 8 个预期 failure，直接暴露 Acceptance final Owner、GitHub writeback/re-read、三 Form 公共 validation、PR auto-close、Finalization 与跨平台 Contract 缺口；Runtime Package #342 / run `33724854273` 对该治理范围 success。

用户随后补充 Issue 标题统一和 Evidence Sufficiency，本 Requirement Source 更新为 AC1–AC12；对应 Red/Green 回归继续加入同一测试文件。实现完成后，语义回归已全部通过。一次 Green 候选因 Git Delivery 路由上下文 245347 bytes 超过既有 244832 bytes 硬预算 515 bytes 被永久预算测试阻止；没有提高阈值，而是压缩重复 UI Profile 说明，保留全部行为边界。最终实现 head `dd90740997daf8d125b05fc1a2275f3d07a2fe26` 的 self-contained suite 全绿。

# 独立 Review

Review Target：PR #185，Requirement Source #184，review implementation head `dd90740997daf8d125b05fc1a2275f3d07a2fe26`。

A1 Requirement→Implementation：逐项从 AC1–AC12 反查 ref17/ref23、三类 Issue Forms、PR Template 与永久回归。AC1–AC10 均有直接实现；AC11 的 post-merge lifecycle、AC12 的 AIMA 独立仓库 lifecycle 保持 explicit deferred，没有用 CI Green、Review 或作者说明提前满足。

A2 Implementation→Evidence：从 PR changed-files 反查仅涉及 Requirement/Closure canonical rules、Agent_Skills GitHub Profiles、PR Template、Change 和相关永久回归；没有 Runtime/MCP/Bundle/Project Payload/Release 产品面变化。Evidence Sufficiency 本身明确拒绝 CI/merge/Change done 机械满足自然语言 AC。目标仓库没有安装 GitHub Form 时仍由 Agent 行为 Contract 生效；AIMA 实现不进入 canonical 特例，保持项目 Ownership。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`，无 BLOCKER/HIGH/需要阻塞交付的 MEDIUM。

# Validation Matrix

| 验证层 | 结论 |
| --- | --- |
| Red | required；#1052 明确证明旧实现不满足新增 Closure/AC Contract |
| Static / Contract | required；399 项 current self-contained suite 通过，覆盖 Title、Acceptance、Evidence Sufficiency、Forms、PR、Finalization、跨平台与无-Form 默认行为 |
| Routing / Context | required；既有 Issue/PR/Git Delivery 路由与 Context Budget 全部通过，预算未上调 |
| Runtime Package | governance scope；#356 Package Gate success，三平台 binary build not_applicable/skipped，未伪造 package evidence |
| 产品业务 / Persistence / Schema | not_applicable；未修改业务代码、数据库、Schema/Migration 或 Provider |
| Release / Deploy | not_applicable；未请求且未修改 Release/Deploy 产品行为 |
| Independent Review | required；A1/A2 `NO_FINDINGS_WITHIN_SCOPE` |
| PR final-ready / merge / main-fresh / archive | explicitly_deferred；只能由后续真实 revision/lifecycle 取得 |
| AIMA project profile | explicitly_deferred to `dingyuwen777/AIMA_UGC#319`；跨仓独立治理 |
| Final Requirement Closure | explicitly_deferred；只有 #184 AC1–AC12 均取得充分 Evidence 并真实回写后才可 close |

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #184（含用户追加的 AIMA 与 Evidence Sufficiency 要求）、Agent_Skills 当前 main baseline、最终 PR diff 和受影响 canonical Owners。
- [x] change_coverage: AC1–AC10 已有直接实现/Evidence；AC11 post-merge lifecycle 与 AC12 AIMA lifecycle 有明确正式 Owner 和 `explicitly_deferred`，没有伪造完成。
- [x] reverse_audit: 已从最终 diff 反查 Title/Acceptance/Evidence/Closure、类型/平台 Profile、auto-close、Finalization、无-Form 默认行为、上下文预算与非目标边界；未发现 Runtime/Release/业务范围扩大。
- [x] unresolved_cleared: 当前产品/规则实现与独立 Review 无阻塞 finding；唯一未完成项均是必须发生在后续真实 revision 的 lifecycle evidence，已显式 deferred，不把它们当成已完成。
