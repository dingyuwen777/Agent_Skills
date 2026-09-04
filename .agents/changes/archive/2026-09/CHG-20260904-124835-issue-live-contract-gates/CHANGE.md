---
schema: coding-change/v1
id: CHG-20260904-124835-issue-live-contract-gates
title: 强化 live Issue Contract 与 Requirement Source 生命周期门禁
level: L3
status: done
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
  - .agents/changes/archive/2026-09/CHG-20260904-124835-issue-live-contract-gates/CHANGE.md
contracts:
  - Agent Skills Issue Acceptance Contract
  - Agent Skills Requirement Source Live Validation Contract
  - Agent Skills Requirement Closure Contract
data_changes: []
---

# 目标

把现有 Issue Acceptance / Evidence Sufficiency / Closure Contract 收口为不可跳过的 live Requirement Source 生命周期：create/update 后读取真实平台对象并验证；PR、正式 Review、Ready/可合并与 merge preflight 前重新读取；关闭前逐 AC 建立直接 Evidence、回写 Acceptance 状态并重读确认。

本变更只修改 `dingyuwen777/Agent_Skills` canonical 通用治理，没有修改 AIMA_UGC 或其他目标项目，也没有复制第二套 live Issue checker。

# 范围、非目标与不变量

- 只修改 `coding.reference.18`、`coding.reference.24`、Issue Acceptance/Closure 永久回归和本 Change。
- 不修改 AIMA_UGC、Runtime/MCP/Bundle/Project Payload/Installer/Release、依赖、Branch Protection/Ruleset；不新增第二套自然语言 parser；不批量迁移 closed 历史 Issue。
- 项目已有更强 Requirement/Issue/Ticket Owner 时优先；非 GitHub 平台继续使用等价 Acceptance/Closure 状态。
- Acceptance Criteria 仍是 Requirement Source 最终状态 Owner，Change/PR 不创建第二套完成定义。
- Evidence Sufficiency、GitHub `[ ] → [x] → write → re-read → close → re-read`、权限/fail-closed、原 Issue 创建条件/类型职责/multi-PR/Review/授权/Closure 例外与输出责任均保持。
- `coding.reference.18` / `coding.reference.24` Stable ID、trigger、dependency 不变；Context Budget 阈值没有提高。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：create/update 后 live re-read 与 Contract Validation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC1 | satisfied | `Issue Creation / Update Live Validation Gate` 已进入 `coding.reference.18`；final PR head `c290da75ec774778c66c6165d311b50d031b8b7e` 的 Skill Tests #1110 / run `33839934387` 对应回归通过。 |
| R2 | AC2：稳定 AC task list，拒绝 numbered-list/comment-only 冒充状态 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC2 | satisfied | ref18 明确 GitHub `- [ ] AC1`、普通编号列表和 comment-only Evidence 边界；#1110 回归通过。 |
| R3 | AC3：仅保持原需求语义时规范化并重读，否则 fail closed | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC3 | satisfied | ref18 明确原语义/原顺序、再次读取、无写权限/失败/并发漂移 → `blocked/unresolved`；#1110 回归通过。 |
| R4 | AC4：PR、Review、Ready/可合并、merge preflight live revalidation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC4 | satisfied | `Delivery Live Requirement Source Validation` 覆盖四个 checkpoint；ref24 在 develop/review-and-deliver 编排 live validation；#1110 对应回归通过。 |
| R5 | AC5：open legacy/current 有界规范化；closed 历史不批量迁移 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC5 | satisfied | ref18 保留 open/current 原有验收顺序与 closed history no-bulk-migration；#1110 regression 通过。 |
| R6 | AC6：Closure comment 不替代 body；Evidence Sufficiency 后才 `[x]` 并双重重读 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC6 | satisfied | ref18 保留 Evidence Sufficiency、body task-list writeback、write-after reread、close-after reread；#1110 Closure regressions 通过。 |
| R7 | AC7：永久回归覆盖新 live gate 且既有语义不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC7 | satisfied | 初始 Red #1079 / `33838379790` 精确失败 7 个新增 live-contract tests；第一次 Review 发现内容守恒 HIGH 后，Review-fix Red #1106 / `33839557881` 精确失败 2 个新增 preservation tests；最终 #1110 共 422/422 self-contained Green，并保持旧 Issue/PR/Closure/project-owner/cross-platform/routing 回归。 |
| R8 | AC8：不改 AIMA/Runtime 产品面/依赖；canonical 内容守恒/路由通过 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC8 | satisfied | PR #197 changed-files 仅本 Change、两份 canonical Reference、一个 contract test；final-head Runtime Package #400 / `33839934393` success，implementation main-fresh Runtime Package #401 / `33840083338` success；三平台 binary build 未触发。Skill Tests 的 routing、Context Budget、Bundle exact-text、Project Payload/required Context 全绿，预算阈值未提高。 |
| R9 | AC9：Review、PR final-head CI、guarded merge、main-fresh、Change archive、archive-main、最终 Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC9 | explicitly_deferred | final-head Review `NO_FINDINGS_WITHIN_SCOPE`（PR #197 review `5109446167`）；PR #197 expected-head guarded squash merge 为 `628b6729f59f542c09d86bd5e74d290576bb9157`；implementation main-fresh Skill Tests #1111 / `33840083333` 与 Runtime Package #401 / `33840083338` success。当前 archive PR/merge、archive-main fresh 与 #196 最终 Closure 由 post-merge finalization 继续承担，避免 archived Change 自引用。 |

# Red / Green 与 Review

- 初始 Red：head `c51c041ab5314dea727195aea7f31867923fef71`；Skill Tests #1079 / `33838379790`，420 项中仅新增 7 项按预期失败。
- 初始语义 Green：head `8e38482e80ca51ff8eaf4af2adea3a7d393f74d4`；Skill Tests #1104 / `33839272357` 的 420/420 self-contained Green，Runtime Package #394 / `33839272392` success。
- Context Budget 中间候选曾 `248943 > 244832`、`246031 > 244832`；没有抬阈值，而是等价收敛重复文本。
- 第一轮 L3 Review 在 head `6c6cbaa8655e73e6f3b711bc21a053c2d18ada6a` 发现 HIGH：压缩删除部分既有细粒度语义；Change 回退 proposed。
- Review-fix Red：head `0ab371fa38813d385432dd131797524bf94565de`；Skill Tests #1106 / `33839557881` 的 2 个内容守恒回归精确失败。
- Review-fix Green：head `0ffaaaa137b4c4637d2df1f873921f5c5610062f`；Skill Tests #1109 / `33839797760` 422/422 + 原 Context Budget Green，Runtime Package #399 / `33839797751` success。
- final PR head：`c290da75ec774778c66c6165d311b50d031b8b7e`；Skill Tests #1110 / `33839934387`、Runtime Package #400 / `33839934393` success。
- final-head L3 A1/A2 + 内容守恒 Review：`NO_FINDINGS_WITHIN_SCOPE`，review id `5109446167`。无 unresolved review thread。
- implementation merge：PR #197 guarded squash merge → `main@628b6729f59f542c09d86bd5e74d290576bb9157`。
- implementation main-fresh：Skill Tests #1111 / `33840083333` success（含 Agent Skills Gate）；Runtime Package #401 / `33840083338` success。

# 验证矩阵

| 验证层 | 结论 |
| --- | --- |
| 行为 / 单元 | required；live-gate Red→Green + content-preservation Review-fix Red→Green；final 422/422 Green |
| 接口 / 契约 | required；Stable ID/trigger/dependency 不变，routing/metadata/exact-text/required Context Green |
| Integration / Persistence | not_applicable；无数据库、文件持久化、Runtime service 实现变化 |
| Workflow Acceptance | required；#196 create 后 live re-read，PR #197 create/update/Ready/merge preflight 均重新读取；最终 Closure 仍由 #196 承担 |
| Build / Package | required；Runtime Package content scope PR/main fresh success；平台 binary build 正确不适用 |
| Docs / Governance | required；Completion Audit、L3 Review、final-head CI、guarded merge、implementation main-fresh 已完成；archive-main 与 final Closure 仍由 finalization 承担 |

# 完成审计

- [x] upstream_re_read：多次重新读取 live #196，并从 AC1–AC9 独立重建需求。
- [x] change_coverage：R1–R9 直接映射 #196；AIMA #335/#337 只作为失败样例，没有进入 canonical 项目特例。
- [x] reverse_audit：从 create/update、Issue 创建条件/类型/未知项、PR split、Review/Ready/merge、授权、Closure、project-owner/cross-platform、Stable ID、Runtime exact-text/required Context、Context Budget 全面反查；首次 HIGH 已通过专门 Red→Green 修复。
- [x] unresolved_cleared：R1–R8 satisfied；R9 的 archive/Closure 自引用生命周期有正式 Owner #196 和 ref24，按规则 explicitly_deferred。

# 文档影响

`README.md` / `USAGE.md` / `runtime/README.md` 不拥有内部 Requirement Source/Closure canonical 细节，`Docs Impact: not_applicable`；没有复制规则到人类说明或目标项目 Overlay。

# 归档生命周期

- [x] PR #197 final-head Review、fresh CI 和 expected-head guarded squash merge 完成。
- [x] implementation `main@628b6729f59f542c09d86bd5e74d290576bb9157` 的 Skill Tests #1111 / Runtime Package #401 fresh success。
- [ ] 当前 archive PR merge 并取得 archive-main fresh CI。
- [ ] #196 AC1–AC9 Closure Evidence、body checkbox writeback、重读、close、再次重读。
- [ ] 当前任务 implementation/archive 分支完成安全清理。

# 交付边界

Release/Deploy not_applicable；未修改 AIMA_UGC、Runtime/MCP/Bundle/Project Payload/Installer/Release 产品面或依赖。Agent_Skills 只保证经过其治理的流程，不能从 GitHub 平台层阻止完全绕过 Agent_Skills 的人工、管理员或第三方 API 操作。
