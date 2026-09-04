---
schema: coding-change/v1
id: CHG-20260904-124835-issue-live-contract-gates
title: 强化 live Issue Contract 与 Requirement Source 生命周期门禁
level: L3
status: ready_for_review
owner: dingyuwen777
branch: chg/issue-live-contract-gates
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas:
  - issue-governance
  - requirement-traceability
  - delivery-finalization
  - skill-mutation
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/tests/test_issue_acceptance_closure_contract.py
  - .agents/changes/active/CHG-20260904-124835-issue-live-contract-gates/CHANGE.md
contracts:
  - Agent Skills Issue Acceptance Contract
  - Agent Skills Requirement Source Live Validation Contract
  - Agent Skills Requirement Closure Contract
data_changes: []
---

# 目标

把现有 Issue Acceptance / Evidence Sufficiency / Closure Contract 收口为不可跳过的 live Requirement Source 生命周期：create/update 后读取真实平台对象并验证；PR、正式 Review、Ready/可合并与 merge preflight 前重新读取；关闭前逐 AC 建立直接 Evidence、回写 Acceptance 状态并重读确认。

本变更只修改 `dingyuwen777/Agent_Skills` canonical 通用治理，不修改 AIMA_UGC 或其他目标项目，也不复制第二套 live Issue checker。

# 成功标准

- [x] GitHub Issue create/update 后执行 `re-read live → validate → normalize or block → re-read`，不能只信写 API 成功返回。
- [x] GitHub 默认 Acceptance 使用稳定 `AC1/AC2/...` 可回写 task list；普通编号列表或 comment-only Evidence 不能冒充最终状态 Owner。
- [x] PR / Review / Ready / merge preflight 重新读取当前 Requirement Source，正文/AC 漂移会使旧 `resolved` 结论失效。
- [x] open legacy/current Issue 仅在保持原需求语义和原验收顺序时规范化；无法安全恢复、无写权限、写失败或并发漂移时 fail closed；closed 历史不批量迁移。
- [x] Closure 继续强制 Evidence Sufficiency、body 状态写回、写后重读、close、close 后重读；comment 只能承载详细 Evidence Mapping。
- [x] 永久回归覆盖上述行为，并保持 project-owner、跨平台、路由、Runtime required Context 与内容守恒语义。

# 范围与非目标

范围仅包含 `coding.reference.18`、`coding.reference.24`、Issue Acceptance/Closure 自包含回归和本 Change 的交付生命周期。

明确不做：修改 AIMA_UGC/其他业务仓库；复制目标仓库 checker/Workflow；修改 Branch Protection/Ruleset；宣称 Agent_Skills 能平台级阻止绕过它的人工/管理员/第三方 API；批量迁移 closed 历史 Issue；修改 Runtime/MCP 协议、Task Route schema、Bundle、Project Payload、Installer、Release 产品面或依赖；把自然语言 Acceptance 重写成第二套机器 parser。

# 必须保持不变

- 项目已有更强 Issue/Ticket/Requirement Owner 时优先；非 GitHub 平台继续使用真实等价 Acceptance/Closure 状态。
- Acceptance Criteria 仍是 Requirement Source 最终完成状态 Owner；Change/PR 不创建第二套成功标准。
- Evidence Sufficiency 仍要求同一对象、行为、条件、revision/必要环境的直接证据；CI Green、merge、Change done、Review 无 Finding 本身不能机械满足自然语言 AC。
- GitHub Closure 顺序保持 `Evidence → body [x] → re-read → close → re-read`。
- `coding.reference.18` / `coding.reference.24` Stable ID、trigger、dependency 不变；只加强已命中场景内的执行 Contract。

# 关键决策

采用“加强 canonical 行为 Contract + 永久回归”，不新增通用 live Issue parser，也不向业务仓库复制 checker。原因：自然语言 Requirement 完整性、项目更强 Owner 与跨平台状态不能可靠交给第二套 parser；Agent_Skills 应统一约束经过其治理的流程，但不能冒充 GitHub 平台权限系统。

兼容策略：同一 open Requirement 保留原 Issue ID、AC 语义和原顺序；只有结构规范化可被证明时才补稳定 AC/task-list。无法安全恢复、缺写权限、写失败或并发漂移时保持 blocked/unresolved。closed 历史默认不批量改写。回滚只需撤回本次 canonical 文本与回归，无数据/Schema/依赖/Runtime/部署迁移。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：create/update 后 live re-read 与 Contract Validation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC1 | satisfied | `coding.reference.18` 新增 `Issue Creation / Update Live Validation Gate`；最终候选 head `8e38482e80ca51ff8eaf4af2adea3a7d393f74d4` 的 Skill Tests #1104 / run `33839272357` 中对应 live create/update regression 通过。 |
| R2 | AC2：稳定 AC task list，拒绝 numbered-list/comment-only 冒充状态 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC2 | satisfied | `coding.reference.18` 明确 `- [ ] AC1`、普通 `1. 2. 3.` 与 comment-only 边界；#1104 对应 regression 通过。 |
| R3 | AC3：只在保持原需求语义时规范化并重读，否则 fail closed | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC3 | satisfied | `coding.reference.18` 明确原语义/原顺序、再次重读、无写权限/并发漂移 → `blocked/unresolved`；#1104 safe-normalize/fail-closed regression 通过。 |
| R4 | AC4：PR、Review、Ready/可合并、merge preflight live revalidation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC4 | satisfied | `Delivery Live Requirement Source Validation` 覆盖四个 checkpoint；`coding.reference.24` 在 develop/review-and-deliver 编排 live validation；#1104 delivery regression 通过。 |
| R5 | AC5：open legacy/current 有界规范化；closed 历史不批量迁移 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC5 | satisfied | `coding.reference.18` 明确 open/current + 原有验收顺序与 closed history no-bulk-migration；#1104 legacy regression 通过。 |
| R6 | AC6：Closure comment 不替代 body，Evidence Sufficiency 后才 `[x]`，写后/关闭后均重读 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC6 | satisfied | `coding.reference.18` 保留 Evidence Sufficiency 与标准 Closure 顺序并新增 comment-only 显式禁止；#1104 Closure order/comment regression 通过。 |
| R7 | AC7：永久回归覆盖 live gate、漂移、fail-closed 且不破坏既有 profile | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC7 | satisfied | Red head `c51c041ab5314dea727195aea7f31867923fef71` 的 Skill Tests #1079 / run `33838379790` 420 项中仅新增 7 项按预期失败；最终候选 #1104 420/420 self-contained `OK`，现有 Issue Form、Closure、routing、project-owner/cross-platform 回归均通过。 |
| R8 | AC8：不修改 AIMA/Runtime 产品面/依赖，内容守恒与路由保持 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC8 | satisfied | PR #197 changed-files 仅本 Change、两份 canonical Reference、一个 contract test；Runtime Package #394 / run `33839272392` content scope success；三平台 binary jobs 未被触发。#1104 的 routing、context budget、Bundle exact-text、Project Payload/required Context 回归全部通过；上下文预算未抬阈值。 |
| R9 | AC9：Review、final-head CI、guarded merge、main-fresh、archive、archive-main fresh、最终 Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC9 | explicitly_deferred | Review 与最终 PR-head Green 将在本 Change Ready 后执行；merge/main-fresh/archive/archive-main/Issue Closure 只能在后续生命周期取得真实证据，由 #196 AC9 与 `coding.reference.24` 持续拥有，当前不得提前伪造 satisfied。 |

# Red / Green 证据

Red：head `c51c041ab5314dea727195aea7f31867923fef71`，Skill Tests #1079 / run `33838379790`。420 项中仅新增的 7 个 live-contract 回归失败，直接暴露 create/update 重读、numbered-list、safe-normalize/fail-closed、delivery preflight、comment-only Closure 与 develop-and-deliver 前置校验缺口。

Green：final semantic candidate `8e38482e80ca51ff8eaf4af2adea3a7d393f74d4`，Skill Tests #1104 / run `33839272357` 的 self-contained 阶段 `Ran 420 tests ... OK`，compile/smoke 与 route-context-budget 同样通过；workflow 最终仅因本 Change 当时仍为 `proposed` 被 changed-change Ready Check 阻止。Runtime Package #394 / run `33839272392` 为 `success`。

中间候选曾触发 Git Delivery context budget：`248943 > 244832`，随后 `246031 > 244832`。没有提高阈值，而是等价合并 ref17/ref23 重复说明；最终 #1104 的 context-budget regression 已通过。

# 验证矩阵

| 验证层 | 结论 |
| --- | --- |
| 行为 / 单元 / 组件 | required；Red 精确失败，最终 420/420 self-contained Green |
| 接口 / 契约 | required；ref18/ref24 Stable ID、trigger/dependency 不变，routing/metadata/required Context 回归 Green |
| 集成 / 持久化 / 运行依赖 | not_applicable；无数据库、文件持久化、Runtime service 实现变化 |
| 用户 / 工作流验收 | required；#196 create 后已真实 re-read；PR #197 创建后已重读并确认 `Requirement-Source: #196`，后续 Review/merge/Closure 继续取得 live evidence |
| 跨组件关键路径 | not_applicable；无新产品接线，content exact-text/required Context 由永久回归证明 |
| 外部依赖 / Provider Probe | not_applicable；GitHub 写入仅属正常交付，不新增供应方能力假设 |
| 构建 / 打包 / 运行 | required；Runtime Package #394 content scope success；package-scope 三平台 binary 正确不适用 |
| 文档 / 治理 / 其他 | required；Change Ready、独立 Review、PR/main/archive fresh CI 与 Closure lifecycle 分阶段取得 |

# 完成审计

- [x] upstream_re_read：已重新读取 live #196，并从 AC1–AC9 独立重建目标；当前 Issue open、AC1–AC9 均仍为 `[ ]`，未用 Change checklist 反推需求。
- [x] change_coverage：R1–R9 逐项映射 #196 AC1–AC9；AIMA #335/#337 只作为失败样例，没有进入 canonical 项目特例或第二套 Requirement Owner。
- [x] reverse_audit：已从 create/update、PR、Review、Ready、merge preflight、post-merge Closure 反查 checkpoint、失败边界、project-owner/cross-platform、Closure ordering、metadata、Runtime exact-text/required Context 与 Context Budget。
- [x] unresolved_cleared：实现范围 AC1–AC8 已有直接实现/回归证据；AC9 只有 post-merge 生命周期尚未发生，已用上游 #196 + finalization Owner 明确 `explicitly_deferred`，没有伪造完成。

# 任务状态

- [x] 当前 Maintenance / Router / Coding / required References 已读取。
- [x] Requirement Source #196 创建后 live re-read 成功。
- [x] 永久回归形成有效 Red：#1079 仅 7 个新增回归失败。
- [x] 最小修改 ref17/ref23 建立 live lifecycle gate。
- [x] final candidate 自包含 420/420 Green、Context Budget Green、Runtime Package content scope Green。
- [ ] 独立 L3 A1/A2 + 内容守恒 Review。
- [ ] Review 后 final-head fresh CI、Ready、guarded merge、main fresh。
- [ ] Change archive + archive-main fresh。
- [ ] #196 Closure Evidence、body `[x]` 写回、重读、close、再重读。

# 文档影响

`README.md` / `USAGE.md` / `runtime/README.md` 不拥有内部 Requirement Source/Closure canonical 细节，`Docs Impact: not_applicable`。本变更直接修改 canonical Reference Owner，不向人类说明、Runtime product docs 或目标项目 Overlay 复制规则。

# 交付边界

- PR：#197，当前保持 Draft，直到独立 Review 与 final-head fresh CI 完成。
- Release/Deploy：not_applicable；未请求且产品面未修改。
