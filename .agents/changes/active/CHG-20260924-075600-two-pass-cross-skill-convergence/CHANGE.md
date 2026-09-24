---
schema: coding-change/v1
id: CHG-20260924-075600-two-pass-cross-skill-convergence
title: 统一双遍有界分析与跨 Skill 收敛语义
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/two-pass-cross-skill-convergence
created: 2026-09-24
updated: 2026-09-24
completion_gate: required
depends_on: []
affected_areas:
  - analysis
  - router
  - review
  - testing
  - docs
  - figma
  - coding
  - multi-agent
  - runtime-project-payload
  - eval
affected_paths:
  - .agents/skills/analysis/
  - .agents/skills/router/SKILL.md
  - .agents/skills/review/
  - .agents/skills/testing/
  - .agents/skills/docs/SKILL.md
  - .agents/skills/figma/SKILL.md
  - .agents/skills/coding/
  - USAGE.md
contracts:
  - Two-Pass Independent Analysis
  - Bounded Closure
  - Finding Three-Axis Contract
  - Cross-Skill Terminal Handoff Contract
  - Follow-up Lifecycle and Persistence Authorization
  - Delegation Value and Independence Requirement
  - Cross-Owner Semantic Conflict Audit
data_changes: []
---

# 变更摘要

- **Requirement Source**：GitHub Issue #308。
- **要解决的问题**：当前 main 已防止一阶自动扩张，但“全面分析”仍缺通用双遍 + 有界停止；Review 的 scope/blocking/action 混合；Parent/Reviewer Owner 边界、净收敛、Follow-up 持久化授权、跨 Skill 终态、多 Agent 独立性、Mutation 冲突审计仍有语义缝隙。
- **最小充分方案**：不新增 Planner/Scheduler/Task Queue/数据库；在现有 Analysis / Router / Review / Coding / Testing / Docs / Figma Owner 内建立一套正交语义，并用永久 contract regression 锁定。
- **预期结果**：既避免过早宣称“没问题”，也避免无限分析、无限返修和 Follow-up 任务树；跨 Skill、跨模型/宿主使用同一完成/阻塞/授权语义。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #308。用户要求把此前系统性审计形成的通用方法和跨 Skill 收敛语义真正写入 Agent_Skills，并完整交付到 main。

## 当前状态

- Analysis 已有 Closure ≠ Optimality / 独立失效模式审计，但尚未显式定义 Two-Pass Independent Analysis + Bounded Closure。
- Review Finding 当前使用 severity + disposition；`OUT_OF_SCOPE` 被放进 NON_BLOCKING 结束语言，无法正交表达“超范围但阻塞交付”。
- Parent 当前同时承担 Repair Loop Owner / Finding Admission Gate，Reviewer 的独立 Finding 裁决边界未完整分离。
- Repair Loop 当前允许“原 Finding 关闭/根因边界收窄”形成收敛信号，可能出现修掉 A 却引入同级/更高级 B 的假收敛。
- Follow-up 已禁止自动 Issue/Change/Branch/PR/Agent/执行/递归，但 candidate、持久化授权、既有 backlog carrier、新任务再准入未形成完整状态链。
- Testing / Docs / Figma 都能发现跨域问题，但 Router 尚无统一 Cross-Skill terminal/handoff 终态语义。
- NO/MAY/MUST_SPLIT 同时表达并行收益与独立复核，容易在无 delegation fallback 时概念混淆。
- Skill Mutation 有内容守恒，但缺 Cross-Owner Semantic Conflict Audit。
- Outcome Eval 机器契约已存在，但当前宿主没有真实外部 child-model execution interface，不能把静态 contract tests 当成 actual 模型效果。

## 根因

前一轮治理主要解决“自动机制继续扩张”的一阶问题，但同一语义仍跨 Analysis / Router / Review / Coding / Testing / Docs / Figma 分散表达，缺少正交状态模型和统一 Owner 边界；同时“全面”缺少与独立审计同等级的强停止条件，导致可能从过早收敛摆向无界分析。

# 事实与证据

| 证据 | 已确认事实 | 来源 | 影响 |
| --- | --- | --- | --- |
| E1 | current main 最新基线为 `095b2d80...`，前一轮 #307 已完整归档 | main fresh readback | 本 Change 从已交付基线继续 |
| E2 | Analysis 有 Closure ≠ Optimality / 独立失效模式审计，但无 Two-Pass / Bounded Closure 明确 Contract | current main canonical read | R1-R2 |
| E3 | Review Finding 仍使用 severity + disposition，OUT_OF_SCOPE 进入 NON_BLOCKING 结束语言 | current main review ref02 | R3-R4 |
| E4 | Parent 是 Repair Loop Owner / Finding Admission Gate | current main coding ref09 / review ref01 | R5 |
| E5 | 当前收敛定义允许“原 Finding 关闭/根因边界收窄”单独作为进展 | current main review ref01 | R6 |
| E6 | Follow-up 尚无 candidate→persistence→carrier→new task 完整生命周期 | current main review ref02 | R7-R8 |
| E7 | Testing/Docs/Figma 有跨域 Handoff，但无统一 Cross-Skill terminal contract | current main Router + specialist cores | R9 |
| E8 | 多 Agent 只有 NO/MAY/MUST_SPLIT 单轴 | current main coding core/ref09 | R10 |
| E9 | Mutation 有内容守恒，没有命名的 Cross-Owner Semantic Conflict Audit | current main coding ref15 | R11 |
| E10 | Outcome Eval 区分 actual/fixture；本会话无真实 child-model execution interface | current eval contract + host capability | R12 |
| E11 | 首轮 PR CI #35938404172 先被 Change schema 标题 gate 拦截，未运行到新 tests | GitHub Actions | 不是有效 Red，需先修 Change carrier |

# 目标、成功标准与非目标

## 目标

1. 把“全面分析/系统性优化/是否遗漏”固化为跨领域通用 Two-Pass Independent Analysis，并同时固化 Bounded Closure。
2. Review Finding 改为 Scope / Delivery Effect / Action 三轴，允许 `OUT_OF_SCOPE + BLOCKING`。
3. Reviewer 保持 Finding 独立裁决；Parent 只编排返修。
4. Repair Loop 只认可净 Delivery Convergence，Diagnostic Progress 单独记录。
5. Follow-up 完整闭环 candidate → persistence gate → existing backlog → stop，并与当前任务写/Git 权限解耦。
6. Router 只拥有薄 Cross-Skill terminal/handoff contract；专业方法仍由各 Skill 唯一 Owner。
7. Delegation Value 与 Independence Requirement 正交。
8. Mutation 增加跨 Owner 语义冲突审计。
9. Outcome Eval 长期规则覆盖本轮发现的高价值失效模式，不伪造 actual run。

## 成功标准

- #308 AC1–AC15 由 canonical rules / project-facing docs / 永久回归和 current-head CI 直接覆盖。
- #308 AC16 取得 final-head fresh Requirement-first Review + required CI/package。
- #308 AC17 完成 guarded merge、main-fresh、repository-native Change Archive、Issue Closure、branch cleanup。

## 非目标

- 不新增永久 Agent Role、Planner、Scheduler、Agent Team、Task Queue。
- 不新增 Follow-up DB、持久 Orchestration Ledger 或新 Runtime protocol。
- 不自动创建/执行 Follow-up。
- 不把专业 Review/Testing/Docs/Figma 方法搬进 Router。
- 不修改 AIMA_UGC。
- 不创建 Runtime Release / Deploy。
- 不为了“全面”枚举所有理论可能。

# 约束与意图决策

| 维度 | 决定 |
| --- | --- |
| Analysis | Two-Pass 与 Bounded Closure 必须同一变更落地；全面 ≠ 无界 |
| Review Finding | severity 保留；scope / delivery_effect / action 正交，不保留 disposition 作为第二 canonical 模型 |
| Reviewer / Parent | Reviewer owns Finding classification；Parent owns repair scheduling |
| Convergence | Net Delivery Convergence 与 Diagnostic Progress 分离 |
| Follow-up | candidate 不等于 backlog item；持久化是独立外部动作，需要明确/长期授权和既有 carrier |
| Cross-Skill | Router 只定义 terminal/handoff 薄语义，专业执行仍归各 Skill |
| Multi-Agent | Delegation Value 与 Independence Requirement 分离；fallback 只损失并行收益，不降低 required independence |
| Mutation | 内容守恒之外再做 Cross-Owner Semantic Conflict Audit |
| Eval | static/fixture 只证明 contract；actual 才能证明真实模型/宿主效果 |
| Context | 不提高既有 budget；超限只能内容守恒压缩或按需加载 |

# 修改方案与决策依据

## 最小充分方案

1. Analysis Core +复杂分析 Reference：加入 Two-Pass + Bounded Closure，保持通用、跨领域。
2. Router Core：增加短小 Cross-Skill Terminal / Handoff Contract。
3. Review Core/References：迁移 Finding 三轴、Reviewer/Parent Owner、净收敛、Follow-up 生命周期。
4. Coding Core/ref09：把 Delegation Value 与 Independence Requirement 正交，并对齐 Parent repair scheduling。
5. Testing / Docs / Figma Core：只增加“跨域发现映射 Router terminal contract”的薄边界，不复制 Review 分类细节。
6. Coding Mutation/ref15：增加 Cross-Owner Semantic Conflict Audit。
7. Coding Outcome Eval/ref31：补本轮高价值 case families 与 actual/fixture 边界。
8. managed AGENTS / USAGE：同步 project-facing 高价值边界，不复制内部专业方法。
9. 永久 tests 先 Red 后 Green；更新旧 contract tests 迁移旧术语。

## 决策依据

- Finding 的范围、交付影响和动作是三个独立问题，用单个 disposition 会产生语义耦合。
- Parent 需要编排权但不能同时拥有独立 Reviewer 的事实裁决权，否则独立复核可被作者侧覆盖。
- “根因更清楚”是诊断进展，不代表交付 blocker 减少。
- Follow-up candidate 属于发现结果；创建 Issue/Change 是新的持久副作用，不能从当前范围授权自动继承。
- Router 是唯一跨 Skill Handoff Owner，适合拥有薄终态语义，但不适合复制各专业规则。
- MUST_SPLIT 表达“值得委派”与“必须独立复核”是不同维度，解耦后才能正确处理无 subagent 宿主。
- 规则内容仍在不代表规则彼此一致，因此 Mutation 必须同时审计冲突。

# 备选方案与取舍

- **只在 Review ref02 增加一个 OUT_OF_SCOPE_BLOCKER 枚举**：局部改动小，但继续把 scope/blocking/action 混在一个枚举里，拒绝。
- **新增中央 Workflow/Task Manager**：可统一状态，但引入永久控制面、存储和维护成本，明显超出当前需要，拒绝。
- **把 Cross-Skill 全部细节复制进 Router**：容易形成第二专业 Owner 和 context 膨胀，拒绝；只保留 terminal/handoff。
- **所有 OUT_OF_SCOPE 自动建 Issue**：会制造任务树并突破授权，拒绝。
- **无 delegation 时把 required Review 也降级为自审**：破坏独立性，拒绝。
- **为保证全面而增加固定更多审计轮次**：会导致无界分析，拒绝；使用 Decision Relevance / Information Gain stop gate。

# 需求追溯

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 通用 Two-Pass Independent Analysis | #308 AC1 | not_satisfied | 待实现 |
| R2 | Bounded Closure / Decision Relevance / bounded counterexample / information gain / reopen guard | #308 AC2 | not_satisfied | 待实现 |
| R3 | Finding Scope / Delivery Effect / Action 三轴 | #308 AC3 | not_satisfied | 待实现 |
| R4 | 自动返修只接受 IN_SCOPE + BLOCKING + AUTO_REPAIR + Evidence | #308 AC4 | not_satisfied | 待实现 |
| R5 | Reviewer classification / Parent scheduling Owner 分离 | #308 AC5 | not_satisfied | 待实现 |
| R6 | Net Delivery Convergence + Diagnostic Progress 分离 | #308 AC6 | not_satisfied | 待实现 |
| R7 | Follow-up candidate → persistence authorization → backlog → new-task readmission | #308 AC7 | not_satisfied | 待实现 |
| R8 | 当前任务写/Git 权限不自动授权 OUT_OF_SCOPE 持久化 | #308 AC8 | not_satisfied | 待实现 |
| R9 | Router Cross-Skill terminal/handoff + Testing/Docs/Figma/Review 对齐 | #308 AC9 | not_satisfied | 待实现 |
| R10 | Delegation Value 与 Independence Requirement 解耦 | #308 AC10 | not_satisfied | 待实现 |
| R11 | Cross-Owner Semantic Conflict Audit | #308 AC11 | not_satisfied | 待实现 |
| R12 | Outcome Eval 新 failure families + actual/fixture 边界 | #308 AC12 | not_satisfied | 待实现 |
| R13 | managed AGENTS / USAGE 同步且不形成第二专业 Owner | #308 AC13 | not_satisfied | 待实现 |
| R14 | 永久 contract tests Red→Green 且旧回归不削弱 | #308 AC14 | not_satisfied | 待实现 |
| R15 | context budget 不提高 | #308 AC15 | not_satisfied | 待验证 |
| R16 | fresh Requirement-first Review + final-head required CI/package | #308 AC16 | not_satisfied | 待交付 |
| R17 | guarded merge/main-fresh/archive/closure/cleanup | #308 AC17 | not_satisfied | 待交付 |

# 计划改动

| 资产 | 计划 |
| --- | --- |
| analysis/SKILL + ref04 | Two-Pass Independent Analysis + Bounded Closure |
| router/SKILL | Cross-Skill Terminal / Handoff Contract |
| review/SKILL + ref01/ref02 | Finding 三轴、Reviewer/Parent Owner、Net Convergence、Follow-up lifecycle |
| coding/SKILL + ref09 | Delegation Value / Independence Requirement + Parent scheduling |
| testing/docs/figma Core | 对齐 Router terminal contract |
| coding/ref15 | Cross-Owner Semantic Conflict Audit |
| coding/ref31 | 新 Outcome Eval failure families + actual/fixture 边界 |
| AGENTS.managed.md | project-facing independence / follow-up persistence boundary |
| USAGE.md | 双遍有界分析、Review/Follow-up/独立性用户说明 |
| semantic tests | 新 Red→Green；迁移旧 disposition contract |

# 验证矩阵

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| Behavior / semantic contract | required | 新永久 contract tests；旧 contract tests |
| Routing / cross-skill semantics | required | Router/Skill canonical consistency |
| Runtime Project Payload | required | managed/project-facing projection 与 context budget |
| Build / Package / Runtime | required | classifier 命中时 current-head 三平台 package gate |
| Docs / Governance | required | USAGE、Change、canonical Owner 一致性 |
| Independent Review | required | Requirement-first Review of final head |
| External model actual run | not_applicable | 当前宿主无真实 child-model execution interface；不得伪造 |

# 风险、兼容性、迁移与回滚

- Finding 内部治理模型从 disposition 迁移为三轴；旧术语只可出现在历史 Change，不在 current canonical 保留第二事实源。
- Router 只增加 terminal/handoff 薄语义，避免上下文膨胀。
- Analysis 双遍方法与停止门禁必须同提交落地，防止无界分析。
- Runtime public MCP / Bundle / License / Release ZIP protocol 不改变；managed/project-facing 文本变化由现有 Project Payload/Package 验证。
- 无数据/Schema/依赖 Migration。
- 回滚为 revert Implementation PR；无不可逆数据操作。

# 文档、依赖、部署与发布影响

- **文档**：USAGE 与 project-facing managed AGENTS 需要同步；Runtime README 只有 Runtime/host adapter 真实变化才修改，本次原则上不需要。
- **依赖**：无新增/升级依赖。
- **Schema / 数据 / Contract**：无业务 Schema/Data 变化；仅 Agent governance semantic contract 变化。
- **部署 / Migration**：不适用。
- **Release**：本任务不创建 Runtime Release；如 Project Payload classifier 要求，则只取得三平台 package Evidence。
- **回滚**：revert PR。

# 完成审计

- [ ] upstream_re_read：Ready 前重读 #308 与 final-head canonical owners。
- [ ] change_coverage：逐 AC 映射到 canonical/测试/文档。
- [ ] reverse_audit：反查 Analysis stop、Review 三轴、Follow-up、cross-skill、independence、Mutation/Eval 和 project-facing projection。
- [ ] unresolved_cleared：R1-R15 清零；R16-R17 由 Delivery Gate 完成。

# 完成证据与状态

## 当前证据

- Branch：`tech/two-pass-cross-skill-convergence`
- PR：#309，普通 PR 但逻辑未就绪。
- 首轮 CI：Skill Tests run `35938404172` failure；失败原因是 Change 缺 current schema 必需标题，尚未到新 tests，因此**不计有效 Red**。
- 新永久 test 文件已进入分支，待 Change carrier 合法后取得真实 semantic Red。

## 当前状态

- implementation: in_progress
- validation: Red 尚未有效取得
- review: not_started
- delivery: PR open / logical not-ready
- merge/main-fresh/archive/closure/cleanup: not_started
- Release / Deploy: not_applicable
