---
schema: coding-change/v1
id: CHG-20260928-171100-review-rule-effectiveness
title: Review首轮闭环与关键规则可达性
level: L2
status: done
owner: dingyuwen777
branch: tech/323-review-rule-effectiveness
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - review
  - routing
  - outcome-eval
  - governance
affected_paths:
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/review/references/02_Findings与严重度.md
  - .agents/skills/review/references/04_审查深度选择.md
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/references/31_跨模型效果评测与规则有效性.md
  - .agents/skills/coding/assets/multi-agent-roles.json
  - .agents/skills/coding/tests/test_cross_model_outcome_eval.py
  - .agents/skills/coding/tests/test_hard_rule_reachability.py
  - .agents/skills/coding/tests/test_review_convergence_contract.py
  - .agents/skills/coding/tests/test_review_root_mechanism_closure.py
  - evals/agent_outcome_eval.py
  - evals/cases/review-root-mechanism-projection.json
contracts:
  - Review Assembly and Finding Admission
  - Repair Batch and delta re-review convergence
  - hard-rule route reachability
  - high-value Outcome Eval registry
data_changes: []
---

# 变更摘要

按 Issue #323 建立 `Review Assembly → Finding Admission → Repair Batch → Delta Re-review` 的端到端收敛链：Reviewer 首轮先在冻结 Head 上以固定、非递归 Assembly 独立收敛，再一次发布有效 blocking Findings；作者按稳定 Finding batch 一次性修复、复用原 PR/MR 并一次 re-request；返修后只做 reviewed_head→repair_head delta re-review。同步补关键 hard rule 条件式可达性和高价值 Outcome Eval，不新增 Runtime 协议或 Agent 角色。

# 背景、现状与问题

Requirement Source：GitHub Issue #323。原规则已有 Root-Mechanism Projection Closure、First-pass Coverage Miss 和 repair convergence，但仍可能把 Reviewer 探索过程暴露给作者，形成“首轮报一批→作者修→再从旧基线报一批”的循环；同时作者侧缺少稳定 Repair Batch，容易 per-Finding push / re-request / 新 PR。另有 Issue/PR platform write 治理 Contract 需要在写动作前可靠可达，但不能常驻加载抬高普通交付上下文。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 | 影响 |
| --- | --- | --- | --- |
| E1 | current main 已有 Root-Mechanism Projection Closure / First-pass Coverage Miss / Net Delivery Convergence | Review Core/References | 复用既有 Owner，不另建 Review 框架 |
| E2 | 初始 Red regression 能稳定暴露首轮闭环、high-value registry、hard-rule reachability 缺口 | PR #324 early CI | 先测试后实现 |
| E3 | delivery→governance 常驻 dependency 会把轻量 route 风险抬高到 L2 并放大 Context | PR #324 Red CI | 改为 platform write 前条件式 route refresh |
| E4 | `review-root-mechanism-projection` case 原本存在但未进入 HIGH_VALUE_CONVERGENCE_CASES | eval registry | 纳入高价值 qualification registry |
| E5 | pre-ready head `e3d50267bef5cfab04ffbdadeaa4685376593dd5` 的 selected self-contained suite 742/742 PASS；CI 唯一失败是 Change 仍为 `in_progress` | Skill Tests run 36406508582 | 实现/语义回归已 Green，可进入 Ready |

# 目标、成功标准与非目标

## 目标 / 成功标准

- [x] AC1：First Review Assembly Gate 使用固定 fan-out + single synthesis；synthesis 后不递归开启 Full Review，也不向作者发布部分 Findings。
- [x] AC2：Second-pass Repair Verification 只审原 Findings、reviewed_head→repair_head delta、直接相邻回归与 Acceptance；first-review escape 只允许一次 fresh blind assembly。
- [x] AC3：Finding Admission Gate 只允许有稳定 Finding ID、直接 Evidence、触发/影响、classification、收口方向和验证方式的 blocker 进入 Repair；同根/重复/冲突先合并或裁决。
- [x] AC4：Repair Batch Gate 一次性处理 blocking Finding batch，复用原 PR/MR 并一次 re-request review；禁止 per-Finding push/request-review/新 PR 循环。
- [x] AC5：同一 Finding 连续两次修复仍失败或同类 repair regression 再现时，先 root-cause reanalysis / repair-plan reset；实质 Requirement/Scope 变化才重建 Review baseline。
- [x] AC6：Issue/PR platform write 前 Governance Contract 条件式可达；普通交付不常驻加载重治理 Context。
- [x] AC7：`review-root-mechanism-projection` 已进入 HIGH_VALUE_CONVERGENCE_CASES，并覆盖 Assembly/Finding/Repair/delta 失败模式。
- [x] AC8：Runtime MCP/Task Route 协议、Stable IDs、五角色集合未改变；Quick Review 不机械多 Agent 化。
- [ ] AC9：current-head required CI、独立 Review、guarded merge、main-fresh、Change Archive、Issue Closure 与 cleanup；其中 merge 后步骤正式 deferred 到 post-merge lifecycle。

## 非目标

- 不新增 Runtime action-state-machine / MCP 方法 / Pre-Action 通用协议。
- 不新增 Reviewer/Compliance/Preflight 角色；继续复用现有 Reviewer/Tester/Explorer/Researcher。
- 不创建 Release/Deploy，不修改依赖、数据、Schema/Migration。
- 不追求“理论上永远发现所有问题”；目标是当前事实/范围下高价值问题首轮充分覆盖，并让 review/repair 链有界收敛。

## 必须保持不变

- Source/Runtime Task Route 协议与 Stable Reference IDs。
- 简单/低风险 Review 保持最小充分，不因存在 Assembly 规则自动拆 Agent。
- fixture/静态测试不能冒充真实跨模型 actual qualification。
- Branch Protection、required CI、独立 Review、Change Archive 与 Closure 门禁不降低。

# 约束与意图决策

| 决策 | 结论 | 依据 |
| --- | --- | --- |
| Review 内部收敛 | 固定 Review Assembly + blind perspectives + Parent 单次 synthesis，不循环 full review | #323 + Red/Green evidence |
| Finding 有效性 | blocking Finding 先过 Finding Admission Gate | 避免 speculative blocker 进入作者返修 |
| 作者返修 | 一个 blocking Finding batch → 一个 Repair Batch → 原 PR/MR 一次 re-request | 避免 per-Finding 往返 |
| 二次 Review | reviewed_head→repair_head delta-first | 避免机械重审未改旧代码 |
| 重复失败 | root-cause reanalysis / repair-plan reset | 避免叠加同类补丁 |
| PR/Issue governance | platform write 前 route refresh 到 PR治理/Issue治理 | 保证可达且不常驻放大 Context |
| Runtime | 不改 protocol / stable IDs / 角色集合 | 当前 fixed-point/context loader 已足够 |

# 修改方案与决策依据

1. Review Core/执行流程：First Review Assembly Gate、Coverage Map、Systemic Projection closure、single synthesis、delta re-review、one-shot first-review escape correction。
2. Findings：Finding Admission Gate，稳定 ID、直接 Evidence、触发/影响、classification、修复/验证边界，先去重/裁决再发布。
3. 审查深度：Quick/Standard/Deep 分别映射不同固定 Assembly；Deep 仍受 active child budget=3/no nested delegation。
4. 多 Agent/协作：Repair Batch Gate，统一修当前 blocker、Finding→修改→Evidence 映射、复用原 PR/MR、一次 re-request；重复失败先重诊断。
5. Delivery：Issue/PR platform write 前条件式 route refresh 到治理 Contract，不用常驻 dependency。
6. Eval：把 review-root-mechanism-projection 加入 HIGH_VALUE_CONVERGENCE_CASES，并覆盖 partial Finding publication、speculative blocker repair、per-Finding re-request、duplicate PR、recursive assembly 等负例。

# 需求追溯

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 固定非递归 Review Assembly + single synthesis | #323 / AC1 | satisfied | Review Core/ref04 + `test_review_assembly_is_fixed_and_non_recursive` |
| R2 | delta-scoped second pass + one-shot escape correction | #323 / AC2 | satisfied | review ref01 + root-mechanism/convergence tests |
| R3 | Finding Admission Gate | #323 / AC3 | satisfied | review ref02 + `test_finding_admission_requires_actionable_evidence_before_repair` |
| R4 | Repair Batch + existing PR + single re-request | #323 / AC4 | satisfied | coding ref09 + `test_repair_batch_updates_existing_pr_once_before_rereview` |
| R5 | repeated repair root-cause / repair-plan reset | #323 / AC5 | satisfied | coding ref09/ref01 + convergence tests |
| R6 | platform-write Governance Contract 条件式可达 | #323 / AC6 | satisfied | coding ref23 + `test_hard_rule_reachability.py` positive/negative routes |
| R7 | high-value Outcome Eval registry | #323 / AC7 | satisfied | eval registry/case + cross-model/root-mechanism tests |
| R8 | Runtime/Stable IDs/roles/Quick path compatibility | #323 / AC8 | satisfied | 742/742 selected tests PASS on pre-ready head; routing/runtime conformance included |
| R9 | end-to-end delivery lifecycle | #323 / AC9 | explicitly_deferred | current-head CI + independent Review 仍需在 ready revision 完成；merge/main-fresh/archive/closure/cleanup 属 post-merge lifecycle |

# 计划改动

| 资产 | 实际变化 | 目的 |
| --- | --- | --- |
| Review Core + refs 01/02/04 | Assembly、Finding Admission、depth、delta re-review | 首轮问题集更完整/有效，并避免 Reviewer 内部递归 |
| multi-agent reviewer role | blind draft Findings + Parent synthesis + repair delta | 保证宿主子 Agent 继承新语义 |
| Coding ref09 | Repair Batch、single re-request、repeat-failure reanalysis | 收敛作者/Reviewer 往返 |
| Coding ref23 | platform write route refresh | hard rule 可达但保持普通交付轻量 |
| Coding ref31 + eval registry/case | high-value review convergence case | 防行为回归 |
| targeted tests | Review Assembly/Finding/Repair/reachability/registry | 永久 Red/Green 保护 |

- [x] 调查当前实现和事实源。
- [x] 建立与风险相称的任务路由和验证矩阵。
- [x] 行为变化先建立 Red evidence，再实现 Green。
- [x] 完成最小实现，没有新增 Runtime 协议或 Agent 角色。
- [x] 同步受影响 canonical Owner；README/USAGE 不变，因为用户调用方式未改变。
- [x] 取得覆盖当前实现的 pre-ready Green Evidence。
- [x] 完成需求追溯、完成审计和适用复核；post-merge lifecycle 正式 deferred。

# 验证矩阵

| 验证层 | 是否要求 | Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Review Assembly、Finding Admission、Repair Batch、delta re-review、Outcome Eval tests |
| 接口 / Contract | required | routing metadata/conditional route、Source/Runtime conformance、Stable IDs |
| 用户 / Workflow | required | 真实 Task Route witness：Systemic Review、PR治理 write refresh、多人协作 Repair Batch |
| Integration / Persistence | not_applicable | 无数据/外部 runtime 行为变化 |
| Build / Package / Runtime | not_applicable | Runtime package/protocol 未修改 |
| Docs / Governance | required | #323、Change、PR current-head CI、独立 Review、post-merge archive/closure |

## 新鲜验证

- Red：PR #324 early CI 明确失败于首轮 Review 时序、high-value registry、hard-rule reachability，以及后续的循环/上下文副作用；测试先于最终实现。
- Green：Skill Tests run `36406508582`，head `e3d50267bef5cfab04ffbdadeaa4685376593dd5`，selected self-contained suite `Ran 742 tests ... OK`。
- 同一 run 的唯一失败：Ready Check 要求 Active Change 为 `ready_for_review`，当前当时仍为 `in_progress`；没有测试失败。
- Context budget：未提高现有预算；经过语义守恒压缩后由现有 routing migration/context budget tests 继续约束。

# 风险、兼容性、迁移与回滚

- 主要风险：Review 过度多 Agent 化、Finding 数量导向、作者返修被机械 batching、context 膨胀。
- 缓解：Quick 单 Reviewer；Standard/Deep 才按风险增加 blind/specialist；Finding Admission 不以数量为目标；existing budget tests 不放宽。
- 兼容：Runtime protocol、Stable IDs、角色集合、公共 Task Route vocabulary 均未迁移。
- 数据 / Schema / Migration / 依赖 / Deploy：不适用。
- 回滚：revert PR #324；无外部数据状态需要恢复。

# 文档、依赖、部署与发布影响

- Canonical Review/Coding References 是本次长期事实源；不另在 README/USAGE 复制第二套规则。
- 无依赖升级、Runtime 协议、Schema/Migration、Release/Deploy 影响。

# 完成审计

- [x] upstream_re_read：已重读 #323 和当前受影响 Review/Coding/Router/Eval canonical Source；用户补充目标已纳入。
- [x] change_coverage：R1-R8 均由当前实现和测试覆盖；R9 按正式 post-merge lifecycle deferred。
- [x] reverse_audit：已从“Reviewer 首轮 → Finding → 作者返修 → re-review → PR/Issue platform write”用户路径反查 route、Context、Evidence 与停止条件。
- [x] unresolved_cleared：实现范围内无 `not_satisfied`；只剩 R9 的 current-head delivery/post-merge lifecycle。

# 完成证据与状态

## 未验证内容与剩余风险

- 当前 ready revision 尚需重新跑 required CI；pre-ready head 已证明实现测试 Green。
- 独立 final Review、guarded merge、main-fresh、repository-native Change Archive、Issue #323 Closure 与 branch cleanup 尚未完成。
- 本任务未运行真实跨宿主 actual Outcome Eval；因此不能声称新的行为已经跨所有模型/宿主实际 qualification，仍按 current rule 记 unverified，不阻塞普通源码交付。

## 交付状态

- implementation: complete
- validation: pre-ready semantic suite green; current-head required CI pending
- PR: #324 draft/ready transition pending
- independent_review: pending
- merge: pending
- main_fresh: pending
- change_archive: pending
- requirement_closure: #323 open
- cleanup: pending
- release/deploy: not_applicable
