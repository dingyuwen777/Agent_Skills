---
schema: coding-change/v1
id: CHG-20260928-142125-review-root-mechanism-closure
title: Review 根机制投影闭环与首轮覆盖门禁
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/319-review-root-mechanism-closure
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - router
  - review
  - coding
  - testing
  - outcome-eval
  - docs
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/review/references/03_测试专家审查方法.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/references/22_根因调试.md
  - .agents/skills/coding/tests/test_review_root_mechanism_closure.py
  - evals/cases/review-root-mechanism-projection.json
  - USAGE.md
contracts:
  - Root-Mechanism Projection Closure Gate
  - First-pass Coverage Miss
  - Review Systemic RCA conditional escalation
data_changes: []
---

# 变更摘要

把复杂 Code Review 从“发现一个 Finding 就局部返修”收敛为“先对已命中的高风险根机制做有界投影闭环，再统一形成 Findings”。简单 Review 继续走轻量路径；只有当前事实确认并发、批处理、Lease/Fencing、Retry/Timeout、幂等、partial failure、外部副作用、事务、状态机、恢复或资源生命周期等复合机制时，才条件升级并复用既有 Systemic RCA。

# 背景、现状与问题

Requirement Source 为 GitHub Issue #319。当前 Review risk-first、Analysis Two-Pass、Coding Systemic RCA、主要复发路径和 Review Convergence Guard 分别存在，但高风险 Code Review 没有稳定形成“根机制 → 生命周期 → 主要失效投影 → 证据”的首轮闭环，因此同一 invariant 的兄弟问题可能在多轮 re-review 中逐个出现。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 | 支撑约束 |
| --- | --- | --- | --- |
| E1 | 普通 Code Review 默认路由 Coding + Review | canonical Router current main | 不能假设 Analysis/Systemic RCA 自动加载 |
| E2 | Review 已有 risk-first 和 Convergence Guard | review/SKILL.md + ref01 | 应增强首轮覆盖，不重做整个 Review |
| E3 | Systemic RCA 已覆盖并发/批处理/外部 I/O/retry/partial failure 等链路 | coding ref22 | 复用唯一 RCA Owner |
| E4 | Review Testing 已审 Evidence 边界，但未按 invariant projections 形成回归矩阵 | review ref03 | 需要最小补强 |
| E5 | Outcome Eval 已有 repair-churn/review-testing，但无首轮同根投影覆盖 case | evals/cases | 需要可度量回归 |

# 目标、成功标准与非目标

## 目标 / 成功标准

- AC1：Review Core 建立 Root-Mechanism Projection Closure Gate。
- AC2：简单局部 Review 保持 lightweight。
- AC3：复杂机制 Review 条件式复用 Coding Systemic RCA，routing 可达。
- AC4：Testing Handoff 从同一 invariant 的主要 blocking projections 建最小 Regression Matrix。
- AC5：re-review 能区分 First-pass Coverage Miss 与真正的新事实/新需求。
- AC6：Review Convergence Guard 保持“机制内完整、任务外有界”。
- AC7：永久回归覆盖复杂正例、简单负例、Systemic route、Coverage Miss 和 Outcome Eval。
- AC8：独立 Review、current-head CI、guarded merge、main-fresh、Change Archive 和 Issue Closure 后端到端完成。

## 非目标

- 不承诺一次 Review 找出任何 PR 的所有潜在 Bug。
- 不让所有 Review 无条件加载 Analysis/Systemic RCA。
- 不新增 Agent、队列或第二套 RCA Owner。
- 不改变 Runtime MCP public surface、依赖、License 或 Release ZIP surface。
- 不 rollout 到业务仓库，不执行 Release/Deploy。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| Review Owner | Review 拥有“何时需要机制闭环”的审查 Gate | E1/E2 | 不把完整 RCA 复制进 Review |
| RCA Owner | 复杂未知达到 Systemic 时复用 coding ref22 | E3 | 保持单一 Owner |
| Testing | 以 invariant blocking projections 形成最小矩阵 | E4 | 不按测试数量配额扩张 |
| Scope | 机制内完整、任务外有界 | #319 / AC2/AC6 | 防止全仓无限审计 |
| Eval | 增加首轮 coverage case | E5 | 可跨模型度量规则效果 |

# 修改方案与决策依据

1. Review Core 增加 Root-Mechanism Projection Closure Gate：确认复合机制后，局部 Finding 前先做 Invariant → Lifecycle → Failure Boundary → Projection → Evidence → Omission/Coverage Audit。
2. Router/Review 执行规则约定内部信号 `意图=机制完整性审查`；命中后由 routing metadata 条件加载 coding ref22。
3. ref01 定义 projection 状态：confirmed / ruled_out / covered_by_evidence / not_applicable / unknown，并规定首轮覆盖停止条件。
4. ref03 以同一 invariant 的 blocking projections 生成最小 Regression Matrix。
5. ref11 明确正式 Review 的复杂机制回程，继续引用 ref22，不建立第二套 RCA。
6. re-review 新 blocker 若与原 Finding 同一 invariant 且首轮当时事实足以推导，标记 First-pass Coverage Miss；真正由新代码/新 Requirement/新外部事实引入则不误标。
7. USAGE 提供无需用户记住内部术语的短指令；普通“审核 PR”即可触发 Review 自主判断。

# 备选方案与取舍

- 所有 Review 无条件加载 Analysis/Systemic RCA：上下文成本高且简单 Review 过度治理，不采用。
- 只在 re-review 增加更多检查：仍无法解决首轮漏检，不采用。
- 新建独立 Mechanism Review Skill/Agent：复制 Review/Coding Owner，增加路由复杂度，不采用。
- 把 Systemic RCA 全文复制到 Review：产生双 Owner 和未来漂移，不采用。

# 需求追溯

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Root-Mechanism Projection Closure Gate | #319 / AC1 | not_satisfied | Red regression first |
| R2 | 简单 Review lightweight | #319 / AC2 | not_satisfied | negative route regression |
| R3 | 条件式 Systemic RCA reachability | #319 / AC3 | not_satisfied | routing regression |
| R4 | invariant projection Regression Matrix | #319 / AC4 | not_satisfied | review testing contract regression |
| R5 | First-pass Coverage Miss | #319 / AC5 | not_satisfied | re-review contract regression |
| R6 | bounded convergence | #319 / AC6 | not_satisfied | convergence preservation review |
| R7 | permanent regression / Outcome Eval | #319 / AC7 | not_satisfied | new test + eval case |
| R8 | full delivery | #319 / AC8 | explicitly_deferred | post-merge lifecycle |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| Router | Review 条件式 Systemic reachability | 复杂机制动态升级而非全量加载 | R2/R3 |
| Review Core/ref01 | 根机制投影闭环、Coverage Miss | 防同根问题多轮打地鼠 | R1/R5/R6 |
| Review ref03 | Invariant Projection Regression Matrix | 测试覆盖机制而非首个 Finding | R4 |
| Coding ref11/ref22 metadata | 复用 Systemic RCA Owner | 保持 Owner 单一且 Runtime 可达 | R3 |
| tests/evals | 正反例与 Outcome Eval | 永久保护行为 | R7 |
| USAGE | 面向使用者的短 Review 指令 | 用户无需记内部术语 | R1-R6 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| Behavior / Rule Contract | required | Review/Router/Coding/Testing canonical markers and semantics |
| Routing / Context | required | complex review loads coding.reference.23; simple review does not |
| Outcome Eval | required | root-mechanism projection case validates |
| Runtime / Source parity | required | existing metadata compiler/routing conformance/project payload tests |
| Docs / Governance | required | Issue #319, Change, USAGE, ready gate |
| External Provider | not_applicable | no external provider behavior |

# 验证计划

- Red：新永久回归在旧 canonical 规则上因缺少 Gate/route/coverage markers 失败。
- Green：最小修改 canonical Owner 后同一回归通过。
- 相关回归：routing compiler/conformance、progressive disclosure、cross-model outcome eval、Review/Testing、context budget。
- current-head PR required CI；merge 后 main-fresh。
- 不提高 context budget，不删除既有断言。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 处理 |
| --- | --- | --- |
| 主要风险 | 简单 Review 过度路由、Review/Coding 双 Owner、无边界审计 | 简单负例 + 单一 Systemic RCA Owner + bounded scope |
| 兼容性 | Finding classification / Testing Handoff / Convergence 保持 | additive strengthening |
| 数据 / Migration | 不适用 | 无 Schema/数据变化 |
| Runtime | routing metadata 有条件扩展 | 走现有 compiler/parity 回归 |
| 回滚 | revert implementation PR | 无不可逆状态 |

# 文档、依赖、部署与发布影响

- USAGE 同步面向维护者的代码审查短指令。
- 无新依赖，无配置/Schema/Migration。
- 不 Release/Deploy；旧 Runtime 不热更新。
- 业务项目后续需独立安装/升级才获得新规则。

# 完成审计

- [ ] upstream_re_read：Ready 前重读 #319 与最终 canonical rules。
- [ ] change_coverage：AC1-AC8 映射最终实现/Evidence。
- [ ] reverse_audit：复杂 Review、简单 Review、Systemic route、Testing、re-review、Runtime parity 反向检查。
- [ ] unresolved_cleared：Ready 前 R1-R7 satisfied；R8 仅按 post-merge 生命周期保留正式延期。

# 完成证据与状态

## 新鲜证据

- Red PR #320 run #2131 首次失败仅证明 Change 机器 Contract 不完整，不能作为目标行为 Red。
- 下一 revision 只修 Change 结构，必须继续取得真正的目标测试失败后才能进入 Green。

## 未验证内容与剩余风险

- 尚未取得目标行为 Red。
- canonical 规则尚未修改。
- Runtime package/main-fresh/Archive/Closure 尚未执行。

## 交付状态

- Requirement Source：#319 open。
- 分支：tech/319-review-root-mechanism-closure。
- PR：#320 Draft。
- 当前阶段：修正 Change contract 后重新取得 Red。
- merge/main-fresh/archive/Issue Closure：未执行。
