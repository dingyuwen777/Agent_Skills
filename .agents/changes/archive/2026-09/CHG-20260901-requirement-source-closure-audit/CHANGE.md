---
schema: coding-change/v1
id: CHG-20260901-requirement-source-closure-audit
title: Requirement Source 关闭前执行 Closure Audit
level: L2
status: done
owner: dingyuwen777
branch: chore/requirement-source-closure-audit
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - requirement-traceability
  - issue-lifecycle
  - tests
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
contracts: []
data_changes: []
---

# 目标

在通用 Requirement Source 治理中补齐关闭阶段：Agent 负责把 Issue/工单关闭为 completed/resolved 前，必须重新读取当前来源、逐条执行 Closure Audit，只回写实际证据支持的完成状态；未满足或未验证且无正式延期的适用要求不得关闭为完成。

# 最终结果

- [x] completed/resolved closure 前明确要求 Closure Audit。
- [x] Closure Audit 重新读取当前 Requirement Source 并逐条核对验收标准。
- [x] 只有证据支持的 checklist/状态才允许完成；CI Green / merge / Change checklist 不批量证明自然语言要求。
- [x] 未满足、未验证且无正式延期的适用项阻止 completed/resolved closure。
- [x] 有写权限时先回写并重读确认，再关闭；无写权限/写失败时不得声称已同步。
- [x] closing keyword 不得绕过 post-merge Closure Audit。
- [x] 非 GitHub 平台使用等价 ticket/work-item 状态语义。
- [x] Runtime、Routing metadata/Stable ID、MCP、Bundle、Project Payload、Release 和安装行为不变。
- [x] PR Required Checks、独立 Review、正常 merge 与 implementation-main fresh CI 已完成。

# 非目标与不变项

- 未新增自动理解自然语言验收标准的 Workflow，也未给目标项目安装 Issue-close Workflow。
- 未要求所有 Requirement Source 都使用 GitHub Issue，也未要求历史已关闭 Issue 全量回写。
- Requirement Source 继续是上游事实，PR/CI/Change 不能成为自己的需求全集。
- `coding.reference.18` Stable ID 与 routing metadata 未改；Runtime/Release/installer 实现未改。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | completed closure 前执行 Closure Audit | user:requirement-source-closure-audit | satisfied | canonical ref17 新增 `Requirement Source 关闭前 Closure Audit` |
| R2 | 重新读取当前来源并逐条核对验收标准 | user:requirement-source-closure-audit | satisfied | ref17 固定 re-read → per-item audit → writeback → close 链；preservation test Green |
| R3 | 只回写证据支持的完成项，CI Green 不批量证明自然语言要求 | user:requirement-source-closure-audit | satisfied | ref17 明确 `只有实际证据支持`，并保留 `CI 全绿` 不能证明自然语言要求 |
| R4 | 未满足/未验证且未正式延期时阻止 completed/resolved | user:requirement-source-closure-audit | satisfied | ref17 明确 `不得以 completed / resolved 关闭` |
| R5 | 有写权限先同步再关闭；无权限/写失败报告未同步 | user:requirement-source-closure-audit | satisfied | ref17 要求先回写并重读确认，且无写权限不得声称完成 |
| R6 | closing keyword 不得绕过 Closure Audit | user:requirement-source-closure-audit | satisfied | 需要 post-merge evidence 时禁止提前 `Closes/Fixes/Resolves` |
| R7 | 非 GitHub 平台保持等价语义 | user:requirement-source-closure-audit | satisfied | ref17 明确非 GitHub 使用等价字段/状态 |
| R8 | Runtime/路由协议/Release/安装行为不变 | user:requirement-source-closure-audit | satisfied | changed files 仅 ref17、既有 preservation test 与 Change；metadata/Runtime 实现未改 |
| R9 | regression、Review、PR CI 与 implementation-main fresh CI 通过 | user:requirement-source-closure-audit | satisfied | Red `33521293667`；current-base PR runs `33524513232` / `33524513235` success；reviews `5079789356`、`5079832617` 无 blocker；PR #142 merge `a469b6eeb06da7f777bd14f22f284cb2972f2dd9`；main fresh `33525067104` / `33525067370` success |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 有效 Red `33521293667`；最终 preservation、旧追溯与 context-budget 回归均 Green |
| 接口 / Contract | not_applicable | 不修改 Runtime/public protocol/route schema |
| 集成 / Persistence / Runtime Dependency | not_applicable | 无运行依赖或持久化实现变化 |
| 用户 / Workflow Acceptance | required | canonical 规则覆盖 post-merge evidence → re-read → per-item audit → writeback → close；Issue #141 将在本归档 merge 后实际 dogfood |
| 跨组件 Golden Path | not_applicable | 无跨组件运行接线变化 |
| 外部依赖 Probe | not_applicable | 无外部 Provider 事实需要确认 |
| Build / Package / Runtime | not_applicable / regression passed | current-base Runtime Package `33524513235` 与 implementation-main fresh `33525067370` success |
| Docs / Governance / Other | required | Skill Tests、Requirement Source、Change Ready、Agent Skills Gate、Review 与 main fresh CI 均通过 |

# Completion Audit

- [x] upstream_re_read：重新读取用户要求、Issue #141、canonical ref17、Maintenance/Coding/Review 与 current-base 交付事实。
- [x] change_coverage：source re-read、逐项证据、写回顺序、阻止 completed、closing keyword、跨平台与 Runtime 不变项均进入 canonical Owner 与回归。
- [x] reverse_audit：从 close 动作反向确认 post-merge evidence → source re-read → per-item audit → persisted writeback → close 均有 Owner；CI 不承担自然语言批量判断。
- [x] unresolved_cleared：Requirement Traceability 无 not_satisfied；最终 current-base PR checks、Review、implementation merge 与 main fresh 均无 blocker。

# Red / Green 与 Review

- 有效行为 Red：Skill Tests `33521293667`，306 个 self-contained tests 中仅新增 Closure Audit preservation 用例失败。
- 实现后曾触发 common-route Context budget 回归；未放宽阈值，通过压缩重复语义恢复预算。
- 最终 PR head `1c61bb487ccd31af13c07fa1a85bf581b71e52d6` 对 current base `42d279f15d64b84b4031e6b6c5d1310886b86e50`：Skill Tests `33524513232` 与 Runtime Package Tests `33524513235` 全部 success。
- 独立 Review：`5079789356` 与 base-drift re-review `5079832617`，均 `NO_FINDINGS_WITHIN_SCOPE`；review threads 为空。

# Git / 交付

- Requirement Source：Issue #141。
- 实现 PR：#142 `治理：Requirement Source 关闭前执行 Closure Audit`。
- 最终实现 head：`1c61bb487ccd31af13c07fa1a85bf581b71e52d6`。
- 实现 merge commit：`a469b6eeb06da7f777bd14f22f284cb2972f2dd9`。
- implementation merge 后 main fresh：Skill Tests `33525067104` success；Runtime Package Tests `33525067370` success。
- 本文件在上述实现交付事实成立后移入 `archive/2026-09/` 并标记 `done`。归档 PR 只承担 Change 历史收口；归档 merge + archive-main fresh 完成后，对 Issue #141 执行本次新增的 Closure Audit、回写 checklist 并关闭 completed。
