---
schema: coding-change/v1
id: CHG-20260928-142125-review-root-mechanism-closure
title: Review 根机制投影闭环与首轮覆盖门禁
level: L3
status: done
owner: dingyuwen777
branch: tech/319-review-root-mechanism-closure
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - review
  - testing
  - outcome-eval
  - docs
  - governance
affected_paths:
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/review/references/03_测试专家审查方法.md
  - .agents/skills/coding/tests/test_review_root_mechanism_closure.py
  - evals/cases/review-root-mechanism-projection.json
  - USAGE.md
contracts:
  - Root-Mechanism Projection Closure Gate
  - First-pass Coverage Miss
  - Invariant Projection Regression Matrix
data_changes: []
---

# 变更摘要

复杂 Code Review 在确认复合高风险机制后，不再以首个局部 Finding 作为机制闭环；先在当前 Scope 内完成 Invariant、Lifecycle、Failure Boundary、Projection、Evidence 与 Omission/Coverage Audit，再统一形成 Findings。简单局部 Review 保持轻量。需要 Systemic 深度时复用现有 `执行模式=诊断 → coding.reference.23` 路由，不新增 Router vocabulary、不复制第二套 RCA。

# 背景、现状与问题

Requirement Source：GitHub Issue #319。原有 Review risk-first、Systemic RCA、Testing Handoff 与 Review Convergence Guard 各自成立，但没有首轮根机制投影闭环，因此同一 invariant 的兄弟 failure projection 可能在后续 re-review 才逐个出现。

最终实现没有修改 Router、Coding ref11 或 ref22；中间曾尝试新增“机制完整性审查” routing vocabulary，但上下文预算和 Owner 审计证明没有必要，最终改为复用既有 `执行模式=诊断`。这使方案更小，同时保留相同可达性和失败边界。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 运行 | 支撑约束或决策 |
| --- | --- | --- | --- |
| E1 | 普通 Code Review 既有 Owner 是 Coding + Review | canonical Router current main | 简单 Review 不应新增重型上下文 |
| E2 | Systemic RCA 已由 `coding.reference.23` 通过 `执行模式=诊断` 可达 | canonical ref22 + routing evaluator | 复用现有路由，不增加 vocabulary |
| E3 | 旧规则缺少 Root-Mechanism Gate、Projection states、Regression Matrix 和 First-pass Coverage Miss | Red run #2134 | 新 Contract 在旧规则上真实失败 |
| E4 | 最终 branch 的新 Review 回归、既有路由/Source-Runtime parity/context budget 均通过 | run #2144 selected self-contained tests：109 tests / OK | R1-R7 当前实现 Green |
| E5 | PR #320 最终 diff 只有 Change、Review Core/ref01/ref03、永久回归、Outcome Eval、USAGE | current PR patch reread | Router/ref11/ref22 无最终 diff，唯一 Owner 未复制 |
| E6 | #319 仍 open，AC8 明确要求 post-merge finalization | live Requirement reread | merge 前 R8 必须 deferred |

# 目标、成功标准与非目标

## 目标 / 成功标准

- AC1：复杂 Review 具有 Root-Mechanism Projection Closure Gate。
- AC2：简单、局部、单因果 Review 保持 lightweight。
- AC3：Systemic 复杂度条件式复用现有 Coding RCA，不复制第二套 Owner。
- AC4：同一 invariant 的主要 blocking projections 进入最小 Regression Matrix。
- AC5：re-review 能标记 First-pass Coverage Miss，且不误标新事实。
- AC6：机制内完整、任务外有界，不把 Review 变成无限审计。
- AC7：永久回归与 Outcome Eval 保护上述正反例且 context budget 不提高。
- AC8：独立 Review、required CI、merge、main-fresh、Change Archive、Issue Closure 后才端到端完成。

## 非目标

- 不承诺一次 Review 找到任何 PR 的所有潜在 Bug。
- 不让所有 Review 自动进入诊断/Systemic RCA。
- 不新增 Skill、Agent、Router vocabulary、队列或第二套 RCA。
- 不修改 Runtime MCP public surface、依赖、License、数据/Schema。
- 不创建 Release/Deploy，不自动 rollout 到业务仓库。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| Review Gate Owner | Review Core 保留不可延迟首轮闭环 Gate | E3/E4 | 复杂 Review 不能首个 Finding 即闭合 |
| Projection 细节 Owner | review ref01 | E4 | Core 保持薄；状态/停止边界集中一处 |
| RCA Owner | 继续由 coding ref22 唯一拥有 | E2/E5 | 不复制诊断链，不增加 routing metadata |
| Testing | review ref03 只定义 adequacy matrix；专业测试仍交 Testing | E4/E5 | 不产生第二套 Testing 方法 |
| Scope | 机制内完整、任务外有界 | #319 AC2/AC6 | 防止“全面”演变为无限扫描 |
| Eval | 新增 review-root-mechanism-projection case | #319 AC7 | 可长期比较首轮覆盖与返修 churn |

# 修改方案与决策依据

1. Review Core 增加薄 Root-Mechanism Projection Closure Gate，保留 Invariant/Lifecycle/Failure Boundary/Projection/Omission Audit 与 First-pass Coverage Miss 的不可延迟 Contract。
2. review ref01 作为详细执行 Owner：定义五种 projection 状态、Systemic unknown 的诊断升级、Coverage Audit 与 bounded closure。
3. review ref03 定义 Invariant Projection Regression Matrix；已有证据不要求重复执行，测试缺口继续 Handoff Testing。
4. Systemic RCA 不新增路由词表；Reviewer 确认需要 Systemic 深度时，将任务事实追加为 `执行模式=诊断`，由既有 routing evaluator 自动加载 coding.reference.23。
5. 新永久回归同时证明复杂正例与简单 Review 负例，并用 Outcome Eval case 保护 sibling-projection churn。
6. USAGE 告诉使用者无需知道内部 Gate/RCA 名称，普通“审查 PR”即可由 Reviewer 按事实自主升级。

## 备选方案与取舍

- 所有 Review 无条件加载 Analysis/Systemic RCA：上下文与认知成本过高，不采用。
- 新增 `意图=机制完整性审查` routing vocabulary：可以工作，但会增加路由 Contract 与复杂路由上下文；既有 `执行模式=诊断` 已能表达该事实，最终撤销。
- 在 Coding ref11/ref22 再写一套 Review Handoff：会形成跨 Owner 重复，最终撤销。
- 新建 Mechanism Review Skill/Agent：职责与 Review/Coding 重叠，不采用。
- 提高 context budget：会掩盖规则膨胀，不采用；通过去重使旧预算继续通过。

# 需求追溯

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Root-Mechanism Projection Closure Gate | #319 / AC1 | satisfied | Review #5334950366 已修：Core 显式 Evidence；run #2149 regression Green |
| R2 | 简单 Review lightweight | #319 / AC2 | satisfied | `test_simple_review_does_not_load_systemic_rca` Green；Router 无 diff |
| R3 | 条件式 Systemic RCA reachability / single Owner | #319 / AC3 | satisfied | Review #5334950366 已修：达到 Systemic 条件即 diagnosis；route/ref01 tests Green |
| R4 | Invariant Projection Regression Matrix | #319 / AC4 | satisfied | review ref03 + targeted regression Green |
| R5 | First-pass Coverage Miss | #319 / AC5 | satisfied | Review Core/ref01 + Outcome Eval case |
| R6 | bounded convergence | #319 / AC6 | satisfied | “机制内完整、任务外有界” + 既有 Convergence Guard 保持 |
| R7 | permanent regression / Outcome Eval / budget | #319 / AC7 | satisfied | run #2149：109 tests / OK；Evidence/Systemic/false-positive 断言 Green；旧 budget 未提高 |
| R8 | full delivery | #319 / AC8 | explicitly_deferred | 依赖 Ready 后 independent Review/required CI/merge/main-fresh/archive/closure |

# 计划改动

| 文件 / 模块 / 资产 | 实际修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| review/SKILL.md | 薄 Root-Mechanism Gate + First-pass Coverage Miss | 首轮先闭合同根机制 | R1/R2/R5/R6 |
| review/ref01 | projection 状态、Systemic diagnosis handoff、Coverage Audit | 唯一详细执行 Owner | R1/R3/R5/R6 |
| review/ref03 | Invariant Projection Regression Matrix | 测试覆盖主要 blocking projections | R4 |
| test_review_root_mechanism_closure.py | 复杂正例、简单负例、Owner 链与 Outcome Eval 回归 | 防止规则未来退化 | R1-R7 |
| review-root-mechanism-projection.json | 跨模型 Outcome Eval case | 量化首轮覆盖与 sibling churn | R5/R7 |
| USAGE.md | 普通代码审查使用说明 | 用户无需记内部实现术语 | R1-R6 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Rule Contract | required | Review Core/ref01/ref03 + 新永久回归 |
| Routing / Context | required | complex=`审查+诊断` loads coding.reference.23；simple review 不加载 |
| Outcome Eval | required | review-root-mechanism-projection case 通过 schema/eval contract |
| Source / Runtime parity | required | 现有 routing/source-runtime conformance 回归 Green |
| Context budget | required | 历史复杂路由预算保持；未提高阈值 |
| Runtime package | conditional/current CI owner | Ready 后由 changed-scope classifier 决定并执行 required package gate |
| Docs / Governance | required | #319、Active Change、USAGE、PR #320 |
| External Provider / 数据 Migration | not_applicable | 无外部 Provider、Schema、数据变化 |

# 验证计划

- 已完成 Red：run #2134 在旧规则上出现 18 failures + 1 routing error；简单 Review 负例仍通过。
- 已完成 Green：run #2144 selected self-contained tests `Ran 109 tests` / `OK`，新 Review tests 全 Green，历史 context budget 通过；该 run 最终 fail-closed 的唯一原因是 Change 尚为 `in_progress`。
- 本提交把 Change 切到 `ready_for_review`，随后要求 current-head required CI / package gate（如 classifier 要求）与 independent Requirement-first Review。
- merge 后执行 main-fresh、repository-native Change Archive 与 #319 Closure Audit。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理 |
| --- | --- | --- |
| 主要风险 | 简单 Review 过度升级、RCA 双 Owner、无边界扩审 | simple negative regression + ref22 唯一 Owner + bounded closure |
| 兼容性 | 现有 Review Finding classification、Testing Handoff、Convergence 保持 | additive Review contract；Router 无最终 diff |
| 数据 / Schema / Migration | 不适用 | 无数据或 Schema 改动 |
| Runtime/Public Contract | 不变 | 无 Router vocabulary/MCP/public protocol diff |
| 依赖 | 不变 | 无 Manifest/lock 改动 |
| 部署 / Release | 不适用 | 本任务不 Release/Deploy |
| 回滚 | revert PR #320 | 无不可逆状态 |

# 文档、依赖、部署与发布影响

- USAGE 同步 Code Review 行为：用户不需要显式要求 Analysis/Systemic RCA。
- README/runtime README 无长期事实变化，不更新。
- 无依赖、配置、数据、Schema、Migration、部署或 Release 影响。
- 业务项目需要后续安装/升级到包含本变更的 Source/Runtime 版本后才获得新规则；本任务不自动 rollout。

# 完成审计

- [x] upstream_re_read：Ready 前已重读 live #319 与最终 Review Core/ref01/ref03、RCA Owner、PR diff。
- [x] change_coverage：Review #5334950366 的 R1/R3 blocker 已修复，R1-R7 均有当前 revision Evidence。
- [x] reverse_audit：复杂 Review、简单 Review、Systemic route、Testing adequacy、re-review、Source/Runtime parity、context budget 均反查。
- [x] unresolved_cleared：Review #5334950366 blocker 已修复；仅 R8 按 post-merge 生命周期 deferred。

# 完成证据与状态

## 新鲜证据

| Evidence | Revision / Run | Result | 证明内容 |
| --- | --- | --- | --- |
| V1 Red | PR #320 run #2134 | 63 tests；新 Contract 18 failures + 1 routing error；simple review negative Green | 旧规则不能满足首轮机制闭环 |
| V2 Green | HEAD 7f741e11 / run #2144 | selected `Ran 109 tests` / `OK`；Ready Check success；context budget through | 最终语义、正反例、routing/parity/budget Green |
| V3 Diff audit | PR #320 current patch | 7 files；Router/ref11/ref22 无 final diff | 没有第二 Routing/RCA Owner |
| V4 Review fix | HEAD e0c198f1 / run #2149 | selected `Ran 109 tests` / `OK`；budget Green | Review #5334950366 两个 blocker 已修复 |

## 未验证内容与剩余风险

- current-head ready revision 仍需 required CI；如果 classifier 要求 Runtime package，则三平台 package evidence 仍待本提交后的 CI。
- independent Requirement-first Review #5334950366 的两个 blocker 已修复；最终 re-review 待 ready-head CI 后确认。
- main-fresh、Change Archive、Issue Closure 属于 merge 后 Evidence，当前不能提前宣称。

## 交付状态

- implementation: complete
- delivery: PR #320 ready_for_review，尚未 merge
- validation: review-fix Green（run #2149）；ready-head CI 待本提交
- main_fresh: not yet applicable before merge
- change_archive: not yet applicable before merge
- requirement_closure: #319 open
- cleanup: pending post-merge
- end_to_end: incomplete（按 #319 / AC8）
