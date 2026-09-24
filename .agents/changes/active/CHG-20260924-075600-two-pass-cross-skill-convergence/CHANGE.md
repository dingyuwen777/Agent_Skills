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
  - docs
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

# 当前事实与根因

1. current main 已有 Closure ≠ Optimality / 独立失效模式审计，但没有显式 Two-Pass Independent Analysis + Bounded Closure。
2. Review Finding 当前使用 severity + disposition，`OUT_OF_SCOPE` 被放在 NON_BLOCKING 结束语言下，无法正交表达“超范围但阻塞交付”。
3. Parent 当前是 Repair Loop Owner / Finding Admission Gate，独立 Reviewer 的裁决边界未完整分离。
4. 当前单调收敛允许“原 Finding 关闭/根因边界收窄”形成进展，可能掩盖新 blocker，且混合诊断进展与交付收敛。
5. Follow-up 当前可进入 FOLLOW_UP_BACKLOG，但 candidate、持久化授权、carrier、新任务再准入没有完整状态链；当前任务 Git 权限与 OUT_OF_SCOPE 持久化权限存在潜在冲突。
6. Testing / Docs / Figma 都能发现跨域问题，但 Router 尚无统一 Cross-Skill terminal/handoff 终态语义。
7. NO/MAY/MUST_SPLIT 同时表达并行收益与独立复核，容易在无 delegation fallback 时概念混淆。
8. Skill Mutation 有内容守恒，但缺 Cross-Owner Semantic Conflict Audit。
9. Outcome Eval contract 已存在，但本轮没有真实外部 child-model execution interface，不能把静态测试写成 actual 模型效果。

# 目标与非目标

## 目标

1. 把“全面分析/系统性优化/是否遗漏”固化为跨领域通用 Two-Pass Independent Analysis，并同时固化 Bounded Closure。
2. Review Finding 改为 Scope / Delivery Effect / Action 三轴，允许 OUT_OF_SCOPE + BLOCKING。
3. Reviewer 保持 Finding 独立裁决；Parent 只编排返修。
4. Repair Loop 只认可净 Delivery Convergence，Diagnostic Progress 单独记录。
5. Follow-up 完整闭环 candidate → persistence gate → existing backlog → stop，并与当前任务写/Git 权限解耦。
6. Router 只拥有薄 Cross-Skill terminal/handoff contract；专业方法仍由各 Skill 唯一 Owner。
7. Delegation Value 与 Independence Requirement 正交。
8. Mutation 增加跨 Owner 语义冲突审计。
9. Outcome Eval 长期规则覆盖本轮发现的高价值失效模式，不伪造 actual run。

## 非目标

- 不新增永久 Agent Role、Planner、Scheduler、Agent Team、Task Queue。
- 不新增 Follow-up DB、持久 Orchestration Ledger 或新 Runtime protocol。
- 不自动创建/执行 Follow-up。
- 不把专业 Review/Testing/Docs/Figma 方法搬进 Router。
- 不修改 AIMA_UGC。
- 不创建 Runtime Release / Deploy。
- 不为了“全面”枚举所有理论可能。

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

# 方案与 Owner

| 语义 | Canonical Owner | 边界 |
| --- | --- | --- |
| 双遍分析 / 停止 | Analysis | 通用问题分析方法，不绑定 Agent_Skills |
| 跨 Skill terminal / Handoff | Router | 只定义终态与交接，不接管专业方法 |
| Finding 分类 | Review | severity + scope + delivery_effect + action |
| Repair scheduling | Main/Parent / Coding collaboration | 不改写 Reviewer classification |
| Follow-up candidate/persistence | Review finding + Router authorization boundary | candidate 不等于持久对象或任务 |
| Delegation / independence | Coding multi-agent | 分开并行收益与 required independence |
| Testing/Docs/Figma 跨域发现 | 各专业 Skill + Router terminal contract | current-scope 才直接 handoff |
| Skill Mutation conflict | Coding Mutation | 内容守恒之外检查跨 Owner 冲突 |
| Outcome Eval | Coding Eval | static/fixture 不冒充 actual |

# 实施计划

1. 建立永久 Red contract tests，证明 current main 缺失上述语义。
2. Analysis 实现 Two-Pass + Bounded Closure。
3. Router 增加薄 Cross-Skill terminal/handoff contract。
4. Review 迁移 Finding 三轴、Reviewer/Parent ownership、净收敛和 Follow-up 生命周期。
5. Coding multi-agent 解耦 Delegation Value / Independence，更新 Parent repair semantics。
6. Testing / Docs / Figma 对齐 Router terminal contract。
7. Mutation / Outcome Eval 增加 conflict/effectiveness 长期规则。
8. 同步 managed AGENTS / USAGE；更新旧 semantic tests，禁止保留冲突的 legacy canonical 术语。
9. 全量自包含测试、context budget、changed-scope package、独立 Review、CI、PR delivery。

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| Behavior / semantic contract | required | 新永久 contract tests；旧 contract tests |
| Routing / cross-skill semantics | required | Router/Skill canonical consistency |
| Runtime Project Payload | required | managed/project-facing projection 与 context budget |
| Build / Package / Runtime | required | classifier 命中时 current-head 三平台 package gate |
| Docs / Governance | required | USAGE、Change、canonical Owner 一致性 |
| Independent Review | required | Requirement-first Review of final head |
| External model actual run | not_applicable | 当前宿主无真实 child-model execution interface；不得伪造 |

# 风险、兼容、迁移与回滚

- Finding 内部治理模型从 disposition 迁移为三轴；旧术语只可出现在历史 Change，不在 current canonical 保留第二事实源。
- Router 只增加 terminal/handoff 薄语义，避免上下文膨胀。
- Analysis 双遍方法与停止门禁必须同提交落地，防止无界分析。
- Runtime public MCP / Bundle / License / Release ZIP protocol 不改变；managed/project-facing 文本变化由现有 Project Payload/Package 验证。
- 无数据/Schema/依赖 Migration；回滚为 revert Implementation PR。

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared
