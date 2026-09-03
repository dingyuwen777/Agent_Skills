---
schema: coding-change/v1
id: CHG-20260903-144449-issue-acceptance-closure-contract
title: 统一 Issue 验收标准与 Closure Audit 回写契约
level: L3
status: in_progress
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
  - Agent Skills Issue Acceptance Contract
  - Agent Skills Requirement Closure Contract
data_changes: []
---

# 目标

统一 Agent_Skills 自身和被 Agent_Skills 帮助开发的项目在 Requirement Source / Issue 关闭阶段的 Acceptance Criteria 与 Closure Audit：Issue/Ticket 的 Acceptance Criteria 是最终完成状态 Owner；Change 负责 Evidence Ledger，PR 负责交付，Closure Audit 负责把直接 Evidence 回写到 Requirement Source。GitHub profile 使用稳定 `AC1/AC2/...` task list，并在关闭前真实完成 `[ ] → [x] → write → re-read → close → re-read`；其他平台使用项目现有的等价状态，不强制复制 GitHub YAML。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/184

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | canonical Issue Contract 明确 Acceptance Criteria 最终状态 Owner、稳定 AC ID 与状态语义 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC1 | not_satisfied | Red/Green closure contract 回归 |
| R2 | GitHub Closure Audit 强制 checklist 写回、重读、close 后再读；未完成项阻止关闭 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC2 | not_satisfied | canonical rule + closure regressions + 本 Issue dogfood |
| R3 | Change 直接追踪上游 AC 与 direct Evidence，不建立第二套需求 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC3 | not_satisfied | traceability rule/test |
| R4 | 三类 Issue Form 统一 acceptance_criteria / AC 示例 / validation_requirements，同时保留专项字段 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC4 | not_satisfied | Issue Form contract tests |
| R5 | PR Template 在 post-merge evidence 场景禁止 auto-close keyword 抢先关闭 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC5 | not_satisfied | PR template regression |
| R6 | Post-Merge Finalization 固定 checklist sync → re-read → close → re-read → cleanup 顺序 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC6 | not_satisfied | finalization regression |
| R7 | 公共 Contract / 类型 Profile / 平台 Profile 分层，项目现有 Owner 优先 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC7 | not_satisfied | canonical cross-platform regression |
| R8 | 永久回归完整覆盖并保持现有高价值 Issue/PR/Closure 语义 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC8 | not_satisfied | full Skill Tests + diff review |
| R9 | Review、PR/main/archive CI、guarded merge、归档以及本 Issue checklist 回写关闭闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/184#AC9 | not_satisfied | final-head/main/archive/closure evidence |

# Validation Matrix

| 层级 | Scope | 状态 | 证据 |
| --- | --- | --- | --- |
| Red | 当前 main 缺少统一 AC/Closure 写回契约 | pending | 新增 Red regression |
| Static contract | canonical rules / Issue Forms / PR Template / Finalization | pending | self-contained tests |
| Routing / preservation | Issue/PR/端到端交付既有路由与高价值语义不回归 | pending | existing + updated regressions |
| Runtime package scope | 本次治理/Skill 内容变化按真实 scope 分类，不机械要求 binary package | pending | Runtime Package Gate |
| Review | A1 Requirement→Implementation + A2 Implementation→Evidence | pending | independent Review |
| Closure dogfood | Issue #184 AC1-AC9 回写 `[x]`、重读、关闭、再读 | pending | final Closure Audit |

# 完成审计

- [ ] upstream_re_read: 合并前重新读取 Issue #184、当前 main 规则与最终 diff。
- [ ] change_coverage: AC1-AC9 均有直接实现或验证证据。
- [ ] reverse_audit: 从最终 diff 反查公共 Contract、类型/平台边界、auto-close 时序和未授权范围扩大。
- [ ] unresolved_cleared: 无未解决 blocker、CI failure、未验证适用 AC 或未回写 Issue 状态。
