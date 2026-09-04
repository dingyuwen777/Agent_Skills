---
schema: coding-change/v1
id: CHG-20260904-124835-issue-live-contract-gates
title: 强化 live Issue Contract 与 Requirement Source 生命周期门禁
level: L3
status: proposed
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

# 范围与非目标

范围仅包含 `coding.reference.18`、`coding.reference.24`、Issue Acceptance/Closure 自包含回归和本 Change。明确不修改 AIMA_UGC、Runtime/MCP/Bundle/Project Payload/Installer/Release、依赖、Branch Protection/Ruleset；不新增第二套自然语言 parser，不批量迁移 closed 历史 Issue。

# 必须保持不变

- 项目已有更强 Requirement/Issue/Ticket Owner 时优先；非 GitHub 平台使用等价 Acceptance/Closure 状态。
- Acceptance Criteria 仍是 Requirement Source 最终状态 Owner，Change/PR 不创建第二套完成定义。
- Evidence Sufficiency、GitHub `[ ] → [x] → write → re-read → close → re-read` 与权限/fail-closed 边界保持。
- 原 ref17/ref23 的 Issue 建立条件、Issue 类型职责、PR 拆分追溯、Review/授权、Closure 例外和输出责任不得因 Context Budget 压缩丢失。
- `coding.reference.18` / `coding.reference.24` Stable ID、trigger、dependency 不变，不提高 Context Budget 阈值。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：create/update 后 live re-read 与 Contract Validation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC1 | satisfied | `Issue Creation / Update Live Validation Gate` + live create/update regression 已在 #1104 self-contained Green。 |
| R2 | AC2：稳定 AC task list，拒绝 numbered-list/comment-only 冒充状态 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC2 | satisfied | ref17 明确 GitHub task-list/numbered-list/comment-only 边界；对应 regression Green。 |
| R3 | AC3：仅保持原需求语义时规范化并重读，否则 fail closed | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC3 | satisfied | ref17 明确原语义/原顺序、再次重读、无写权限/并发漂移 → blocked/unresolved；对应 regression Green。 |
| R4 | AC4：PR、Review、Ready/可合并、merge preflight live revalidation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC4 | satisfied | `Delivery Live Requirement Source Validation` + ref23 编排；对应 regression Green。 |
| R5 | AC5：open legacy/current 有界规范化；closed 历史不批量迁移 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC5 | satisfied | ref17 + legacy regression Green。 |
| R6 | AC6：Closure comment 不替代 body；Evidence Sufficiency 后才 `[x]` 并双重重读 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC6 | satisfied | ref17 Closure 顺序/comment-only regression Green。 |
| R7 | AC7：永久回归且既有 profile/治理语义不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC7 | not_satisfied | 独立 Review 发现 HIGH：Context Budget 压缩删掉部分既有细粒度语义；已新增内容守恒回归，等待恢复后重新 Green。 |
| R8 | AC8：不改 AIMA/Runtime 产品面/依赖；canonical 内容守恒/路由通过 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC8 | not_satisfied | changed scope 未越界且 Runtime Package content scope 曾 Green；但内容守恒 HIGH 未清前不能判 satisfied。 |
| R9 | AC9：Review、final-head CI、guarded merge、main-fresh、archive、archive-main、最终 Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC9 | explicitly_deferred | 由 #196 AC9 与 ref23 持续拥有；只有清理 Review Finding 后才能进入后续生命周期。 |

# Red / Green / Review 证据

- 初始 Red：head `c51c041ab5314dea727195aea7f31867923fef71`，Skill Tests #1079 / run `33838379790`，420 项中仅新增 7 个 live-contract 回归按预期失败。
- 初始语义 Green：head `8e38482e80ca51ff8eaf4af2adea3a7d393f74d4`，Skill Tests #1104 / run `33839272357` self-contained `420/420 OK`；Runtime Package #394 / run `33839272392` success。Context Budget 曾从 `248943 > 244832` 降到 `246031 > 244832`，最终在未提高阈值下恢复 Green。
- 独立 L3 Review（head `6c6cbaa8655e73e6f3b711bc21a053c2d18ada6a`）发现 HIGH：为恢复预算进行的压缩删除了若干既有 Issue/PR/Review/Closure 细粒度条件，违反 Skill Mutation 内容守恒。当前状态回退为 `proposed`。
- Review 修复 Red：新增 `test_live_hardening_preserves_existing_issue_creation_and_type_contracts` 与 `test_live_hardening_preserves_pr_split_and_delivery_authorization_semantics`，用于锁住旧语义；待当前 CI 形成新鲜失败证据后再修规则。

# 验证矩阵

| 验证层 | 状态 |
| --- | --- |
| 行为 / 单元 | required；初始 Red/Green 已完成，Review 修复回归待 Red→Green |
| 接口 / 契约 | required；Stable ID/trigger/dependency 保持；需 final routing/exact-text/context Green |
| Integration/Persistence | not_applicable；无运行时持久化变化 |
| Workflow Acceptance | required；#196/PR #197 live lifecycle 分阶段取得 |
| Build/Package | required；content scope；三平台 binary 不适用 |
| Docs/Governance | required；内容守恒 Finding 清零、Completion Audit、Review、PR/main/archive/Closure |

# 完成审计

- [x] upstream_re_read：已重新读取 live #196 并独立重建 AC1–AC9。
- [x] change_coverage：R1–R9 直接映射 #196，AIMA #335/#337 仅为失败样例。
- [ ] reverse_audit：独立 Review 已发现内容守恒 HIGH，修复和 re-review 未完成。
- [ ] unresolved_cleared：R7/R8 与 Review Finding 尚未清理；AC9 生命周期未发生。

# 任务状态

- [x] Maintenance / Router / Coding / required References 已读取。
- [x] #196 创建后 live re-read。
- [x] 初始 live-contract Red → Green。
- [x] 独立 Review 暴露内容守恒 HIGH。
- [x] 已新增 Review 修复回归。
- [ ] 取得 Review 修复 Red，并恢复既有细粒度语义。
- [ ] final-head 全量 Green、Completion Audit、独立 re-review。
- [ ] PR Ready、guarded merge、main fresh。
- [ ] Change archive + archive-main fresh。
- [ ] #196 Closure Evidence、body `[x]`、重读、close、再重读。

# 文档影响

`README.md` / `USAGE.md` / `runtime/README.md` 不拥有内部 Requirement Source/Closure canonical 细节，`Docs Impact: not_applicable`；规则只留在 canonical Owner。

# 交付边界

PR #197 保持 Draft；Review HIGH 清零前不得 Ready/merge。Release/Deploy not_applicable。
