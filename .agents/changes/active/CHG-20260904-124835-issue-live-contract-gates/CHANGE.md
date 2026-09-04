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
| R1 | AC1：create/update 后 live re-read 与 Contract Validation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC1 | satisfied | `Issue Creation / Update Live Validation Gate` + live create/update regression 在 final semantic head `0ffaaaa137b4c4637d2df1f873921f5c5610062f` 的 Skill Tests #1109 / run `33839797760` 通过。 |
| R2 | AC2：稳定 AC task list，拒绝 numbered-list/comment-only 冒充状态 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC2 | satisfied | ref17 明确 GitHub task-list/numbered-list/comment-only 边界；#1109 对应 regression 通过。 |
| R3 | AC3：仅保持原需求语义时规范化并重读，否则 fail closed | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC3 | satisfied | ref17 明确原语义/原顺序、再次重读、无写权限/并发漂移 → blocked/unresolved；#1109 对应 regression 通过。 |
| R4 | AC4：PR、Review、Ready/可合并、merge preflight live revalidation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC4 | satisfied | `Delivery Live Requirement Source Validation` + ref23 develop/review-and-deliver 编排；#1109 delivery regressions 通过。 |
| R5 | AC5：open legacy/current 有界规范化；closed 历史不批量迁移 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC5 | satisfied | ref17 明确 open/current 原有验收顺序、closed history no-bulk-migration；#1109 legacy regression 通过。 |
| R6 | AC6：Closure comment 不替代 body；Evidence Sufficiency 后才 `[x]` 并双重重读 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC6 | satisfied | ref17 保留 Evidence Sufficiency、标准 Closure 顺序和 comment-only 显式禁止；#1109 Closure regressions 通过。 |
| R7 | AC7：永久回归且既有 profile/治理语义不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC7 | satisfied | 初次 Review HIGH 后新增内容守恒回归；Review-fix Red head `0ab371fa38813d385432dd131797524bf94565de` 的 Skill Tests #1106 / run `33839557881` 精确暴露旧语义缺失；恢复语义后的 #1109 共 422 项 self-contained `OK`，包括两项内容守恒回归、既有 Issue Form/Closure/project-owner/cross-platform/routing 回归。 |
| R8 | AC8：不改 AIMA/Runtime 产品面/依赖；canonical 内容守恒/路由通过 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC8 | satisfied | PR #197 changed-files 仅本 Change、两份 canonical Reference、一个 contract test；Runtime Package #399 / run `33839797751` content scope success，三平台 binary jobs 未触发；#1109 compile/smoke、routing、Context Budget、Bundle exact-text、Project Payload/required Context 全部通过，预算阈值未提高。 |
| R9 | AC9：Review、final-head CI、guarded merge、main-fresh、archive、archive-main、最终 Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC9 | explicitly_deferred | 独立 final-head re-review、Ready/merge/main-fresh/archive/archive-main/Issue Closure 只能在后续生命周期取得；由 #196 AC9 与 ref23 持续拥有，当前不提前伪造 satisfied。 |

# Red / Green / Review 证据

- 初始 Red：head `c51c041ab5314dea727195aea7f31867923fef71`，Skill Tests #1079 / run `33838379790`，420 项中仅新增 7 个 live-contract 回归按预期失败。
- 初始语义 Green：head `8e38482e80ca51ff8eaf4af2adea3a7d393f74d4`，Skill Tests #1104 / run `33839272357` self-contained `420/420 OK`；Runtime Package #394 / run `33839272392` success。
- Context Budget 中间候选曾为 `248943 > 244832`、`246031 > 244832`；没有提高阈值，而是等价收敛重复说明。
- 独立 L3 Review（head `6c6cbaa8655e73e6f3b711bc21a053c2d18ada6a`）发现 HIGH：过度压缩删掉若干既有 Issue/PR/Review/Closure 条件，违反 Skill Mutation 内容守恒；Change 随即回退 `proposed`。
- Review 修复 Red：head `0ab371fa38813d385432dd131797524bf94565de`，Skill Tests #1106 / run `33839557881` 的新增内容守恒回归在旧压缩版上失败，精确对应 Review Finding。
- Review 修复 Green：head `0ffaaaa137b4c4637d2df1f873921f5c5610062f`，Skill Tests #1109 / run `33839797760`：compile/smoke 成功，422/422 self-contained `OK`，route Context Budget 成功；该 run 最终仅因本 Change 当时仍为 `proposed` 被 changed-Change Ready Check 阻止。Runtime Package #399 / run `33839797751` success。

# 验证矩阵

| 验证层 | 状态 |
| --- | --- |
| 行为 / 单元 | required；初始 live-gate Red→Green + Review-fix content-preservation Red→Green，final 422/422 Green |
| 接口 / 契约 | required；ref18/ref24 Stable ID、trigger/dependency 不变，routing/metadata/exact-text/required Context Green |
| Integration/Persistence | not_applicable；无数据库、文件持久化、Runtime service 实现变化 |
| Workflow Acceptance | required；#196 create 后 live re-read，PR #197 create/update 后 live source 重新读取；后续 Ready/merge/Closure 继续取得真实证据 |
| Build/Package | required；Runtime Package #399 `content` scope success；三平台 binary 构建按真实 scope 不适用 |
| Docs/Governance | required；内容守恒 HIGH 已修复并由永久回归保护；Completion Audit 完成；正式 final-head re-review、PR/main/archive/Closure 尚待后续阶段 |

# 完成审计

- [x] upstream_re_read：已重新读取 live #196，并从 AC1–AC9 独立重建目标；未用 Change checklist 反推需求。
- [x] change_coverage：R1–R9 直接映射 #196；AIMA #335/#337 只作为失败样例，没有进入 canonical 项目特例或第二套 Requirement Owner。
- [x] reverse_audit：从 create/update、Issue 类型/未知项、PR split、Review/Ready/merge preflight、授权、post-merge Closure、project-owner/cross-platform、Stable ID、Runtime exact-text/required Context 和 Context Budget 反查；首次 HIGH 已通过 Review-fix Red→Green 清理。
- [x] unresolved_cleared：R1–R8 已有直接实现/回归证据；R9 仅包含尚未发生的 post-merge 生命周期，已有上游 #196 + finalization Owner 的 `explicitly_deferred`，没有伪造完成。

# 任务状态

- [x] Maintenance / Router / Coding / required References 已读取。
- [x] #196 创建后 live re-read。
- [x] 初始 live-contract Red → Green。
- [x] 独立 Review 暴露内容守恒 HIGH，Change 回退 proposed。
- [x] Review 修复 content-preservation Red → Green；422/422 与原 Context Budget Green。
- [x] Completion Audit 完成，Change 恢复 `ready_for_review`。
- [ ] 精确 final-head 独立 L3 A1/A2 + 内容守恒 re-review。
- [ ] re-review 后 final-head fresh CI、PR Ready、guarded merge、main fresh。
- [ ] Change archive + archive-main fresh。
- [ ] #196 Closure Evidence、body `[x]`、重读、close、再重读。

# 文档影响

`README.md` / `USAGE.md` / `runtime/README.md` 不拥有内部 Requirement Source/Closure canonical 细节，`Docs Impact: not_applicable`；规则只留在 canonical Owner。

# 交付边界

PR #197 继续保持 Draft，直到精确 final-head re-review 与 fresh CI 完成。Release/Deploy not_applicable。
