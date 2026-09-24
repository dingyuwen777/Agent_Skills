---
schema: coding-change/v1
id: CHG-20260924-075600-two-pass-cross-skill-convergence
title: 统一双遍有界分析与跨 Skill 收敛语义
level: L3
status: done
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
  - evals/agent_outcome_eval.py
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
- **根因**：既有规则分别解决了独立优化审计、Review 收敛和多 Agent 二阶扩张，但“全面分析”的停止边界、Finding 的 Scope/Delivery/Action、Reviewer/Parent Owner、Follow-up 持久化授权、跨专业终态和 required independence 仍存在跨 Owner 语义缝隙。
- **方案**：不新增 Planner/Scheduler/Task Queue/Follow-up DB；在既有 Analysis/Router/Review/Coding/Testing/Docs/Figma/Eval Owner 中建立正交状态和授权语义，并用永久回归与 unchanged context budget 约束。
- **结果**：既避免过早宣称“没有优化”，也避免无限分析、无限返修、超范围自动修复和 Follow-up 任务树。

# 背景、现状与问题

## 背景

#308 要求把本轮系统审计结论落入 Agent_Skills canonical Source，并完整交付到 main。起始 main 为 `095b2d80fbdb00473872010c32adcf0560754d28`。

## 当前状态

实现已完成并通过 Ready 前 semantic/contract/context 验证：
- Analysis 已具备通用 Two-Pass Independent Analysis + Bounded Closure；
- Review 已迁移到 Scope / Delivery Effect / Action 三轴；
- Reviewer owns Finding classification，Parent owns repair scheduling；
- Review Repair 使用 Net Delivery Convergence，Diagnostic Progress 不等价于交付收敛；
- Follow-up 已形成 candidate → persistence authorization → existing backlog → STOP 的生命周期；
- Router 只保留薄 Cross-Skill terminal/handoff；
- Delegation Value 与 Independence Requirement 已解耦；
- Mutation 已增加 Cross-Owner Semantic Conflict Audit；
- Outcome Eval 的具体高价值 case-family 由机器契约承载，actual/fixture 真值边界保持不变；
- project-facing managed AGENTS / USAGE 已同步；
- current live Owner 已无 `IN_SCOPE_BLOCKING / IN_SCOPE_NON_BLOCKING / FOLLOW_UP_BACKLOG / disposition` 第二套模型。

## 根因

先前各局部门禁本身成立，但同一“范围 / 阻塞 / 权限 / 后续 / 停止”语义分散在多个 Owner，缺少正交状态模型；同时“全面审计”缺少与独立失效模式审计同等级的强停止规则，可能从过早收敛摆向无界分析。

# 事实与证据

| 证据 | 已确认事实 | 来源 | 影响 |
| --- | --- | --- | --- |
| E1 | 起始 main 为 `095b2d80...`，#306/#307 已完整归档 | main fresh readback | 基线 |
| E2 | current main 旧 Analysis 无完整 Two-Pass + Bounded Closure | canonical read | R1-R2 |
| E3 | 旧 Review 使用 severity + disposition，无法正交表达 OUT_OF_SCOPE + BLOCKING | canonical read | R3-R4 |
| E4 | 旧 Parent 同时承担 Repair Loop/Finding Admission，独立 Reviewer 裁决边界不完整 | canonical read | R5 |
| E5 | 旧收敛可因“原 Finding 关闭/诊断变清楚”被视为进展 | canonical read | R6 |
| E6 | 旧 Follow-up 无 candidate→persistence authorization→carrier→new-task 完整状态链 | canonical read | R7-R8 |
| E7 | Testing/Docs/Figma 有跨域回程但无统一 terminal/handoff | canonical read | R9 |
| E8 | 旧 NO/MAY/MUST_SPLIT 混合 delegation value 与 independence | canonical read | R10 |
| E9 | Mutation 有内容守恒但无 Cross-Owner Semantic Conflict Audit | canonical read | R11 |
| E10 | Outcome Eval 已有 actual/fixture；本宿主无真实外部 child-model execution interface | canonical + host capability | R12 |
| E11 | 有效 Red：run `35938644999` 在治理载体合法后，11 个新 contract tests 因旧语义缺失失败 | GitHub Actions | R14 |
| E12 | exact-head `5a634230...` / run `35943593916`：compile、CLI smoke、selected self-contained tests、context budget、Change readiness 结构检查均 Green；唯一 Agent Skills Gate failure 是 status=in_progress enforcement | GitHub Actions | R1-R15 |
| E13 | Requirement-first Review `5298706847` @ `5a634230...`：NO_BLOCKING_FINDINGS_WITHIN_SCOPE | PR #309 | R1-R15 |

# 目标、成功标准与非目标

## 目标

1. 全面类问题使用通用 Two-Pass Independent Analysis，并通过 Bounded Closure 强制停止。
2. Finding 使用 Scope / Delivery Effect / Action 三轴，允许 `OUT_OF_SCOPE + BLOCKING`。
3. Reviewer 独立裁决 Finding；Parent 只编排返修。
4. Repair Loop 只认可 Net Delivery Convergence。
5. Follow-up candidate 与持久化/执行授权彻底分离。
6. Router 只拥有薄跨专业终态，不复制专业方法。
7. Delegation Value 与 Independence Requirement 正交。
8. Mutation 同时做内容守恒和 Cross-Owner Semantic Conflict Audit。
9. Outcome Eval 不用 static/fixture 冒充真实模型效果。

## 成功标准

- #308 AC1–AC15 由 canonical rules、project-facing docs、永久回归和 Ready 前 Green 证据覆盖。
- #308 AC16 在 Ready HEAD 上重新取得 fresh Review + required CI/package。
- #308 AC17 由 merge 后 Delivery Gate 完成，不在 pre-merge Change 中自证未来动作。

## 非目标

- 不新增 Planner/Scheduler/Agent Team/Task Queue/Follow-up DB。
- 不新增持久 Orchestration Ledger 或 Runtime protocol。
- 不自动创建/执行/递归 Follow-up。
- 不把 Review/Testing/Docs/Figma 专业方法复制进 Router。
- 不修改 AIMA_UGC。
- 不创建 Runtime Release / Deploy。
- 不提高 context budget 或放宽永久测试。

# 约束与意图决策

| 维度 | 决定 |
| --- | --- |
| Analysis | Two-Pass 与 Bounded Closure 必须同变更落地；Comprehensiveness ≠ Unbounded Exploration |
| Review Finding | severity 保留；Scope / Delivery Effect / Action 正交 |
| Reviewer / Parent | Reviewer owns classification；Parent owns repair scheduling |
| Convergence | Net Delivery Convergence 与 Diagnostic Progress 分离 |
| Follow-up | candidate 不等于 backlog item；持久化需要独立授权与既有 carrier |
| Cross-Skill | Router 只定义 terminal/handoff |
| Multi-Agent | Delegation Value 与 Independence Requirement 分离 |
| Mutation | 内容守恒 + Cross-Owner Semantic Conflict Audit |
| Eval | static/fixture 不能证明 actual model behavior |
| Context | 不提高 budget；超限通过 Owner 去重 / 渐进披露修复 |

# 修改方案与决策依据

## 最小充分方案

- Analysis Core/ref04：Two-Pass + Bounded Closure。
- Router Core：薄 terminal/handoff set。
- Review Core/ref01/ref02：三轴 Finding、Owner 分离、Net Convergence、Follow-up 生命周期。
- Coding Core/ref09：Delegation Value / Independence Requirement 与 repair scheduling。
- Testing/Docs/Figma Core：仅 project-facing current-scope/跨域收口边界，不复制 Review 分类细节。
- Coding ref15：Cross-Owner Semantic Conflict Audit，同时保留既有 Mutation 授权/CI/内容守恒硬锚点。
- Eval：高价值 failure-family 机器事实与 actual/fixture 真值边界。
- managed AGENTS / USAGE：同步用户/项目侧规则。
- tests：新增永久回归，并把旧 disposition tests 迁到新模型。

## 备选方案与取舍

- 单加 `OUT_OF_SCOPE_BLOCKER`：继续耦合 scope/blocking/action，拒绝。
- 新增中央 Workflow/Task Manager：过度控制面，拒绝。
- Router 复制全部专业细节：第二 Owner + context 膨胀，拒绝。
- OUT_OF_SCOPE 自动建 Issue：突破授权并制造任务树，拒绝。
- 无 delegation 时降级 required Review：破坏独立性，拒绝。
- 为“全面”固定增加更多轮分析：会无界循环，拒绝。

# 需求追溯

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 通用 Two-Pass Independent Analysis | #308 / AC1 | satisfied | analysis Core + ref04 |
| R2 | Bounded Closure / Decision Relevance / bounded counterexample / information gain / reopen guard | #308 / AC2 | satisfied | analysis ref04 + USAGE |
| R3 | Finding Scope / Delivery Effect / Action 三轴 | #308 / AC3 | satisfied | review Core + ref02 |
| R4 | 自动返修只接受 IN_SCOPE + BLOCKING + AUTO_REPAIR + Evidence | #308 / AC4 | satisfied | review Core/ref01/ref02 |
| R5 | Reviewer classification / Parent scheduling Owner 分离 | #308 / AC5 | satisfied | review ref01 + coding ref09 |
| R6 | Net Delivery Convergence + Diagnostic Progress 分离 | #308 / AC6 | satisfied | review ref01 + USAGE |
| R7 | Follow-up candidate → persistence authorization → backlog → new-task readmission | #308 / AC7 | satisfied | review ref02 + managed AGENTS + USAGE |
| R8 | 当前任务写/Git 权限不自动授权 OUT_OF_SCOPE 持久化 | #308 / AC8 | satisfied | review ref02 + Router + managed AGENTS |
| R9 | Router terminal/handoff + Testing/Docs/Figma/Review 同语义 | #308 / AC9 | satisfied | Router + specialist Cores |
| R10 | Delegation Value 与 Independence Requirement 解耦 | #308 / AC10 | satisfied | coding Core/ref09 + managed AGENTS + USAGE |
| R11 | Cross-Owner Semantic Conflict Audit | #308 / AC11 | satisfied | coding ref15 |
| R12 | Outcome Eval 高价值 failure families + actual/fixture 边界 | #308 / AC12 | satisfied | evals/agent_outcome_eval.py + coding ref31 |
| R13 | managed AGENTS / USAGE 同步且无第二专业 Owner | #308 / AC13 | satisfied | project-facing projection tests + USAGE |
| R14 | 永久 contract Red→Green 且旧回归不削弱 | #308 / AC14 | satisfied | Red 35938644999；Green 35943593916 |
| R15 | context budget 不提高 | #308 / AC15 | satisfied | 多轮 over-budget 被 contract 捕获；最终 35943593916 无 budget failure，阈值未修改 |
| R16 | fresh Review + final-head required CI/package | #308 / AC16 | not_applicable | Review 5298706847 已完成；Ready commit 后重新取得 exact-head CI/package 与增量 Review |
| R17 | guarded merge/main-fresh/archive/closure/cleanup | #308 / AC17 | not_applicable | pre-merge Change 不自证未来交付动作；由 Delivery Gate 完成 |

# 计划改动

| 资产 | 实际修改 |
| --- | --- |
| analysis/SKILL + ref04 | Two-Pass Independent Analysis + Bounded Closure |
| router/SKILL | Cross-Skill terminal/handoff 薄契约 |
| review/SKILL + ref01/ref02 | Finding 三轴、Reviewer/Parent Owner、Net Convergence、Follow-up lifecycle |
| coding/SKILL + ref09 | Delegation Value / Independence Requirement + repair scheduling |
| testing/docs/figma Core | project-facing 跨域终态/授权边界 |
| coding/ref15 | Cross-Owner Semantic Conflict Audit + 原 Mutation 硬锚点保持 |
| coding/ref31 + evals/agent_outcome_eval.py | actual/fixture 边界 + high-value case registry |
| AGENTS.managed.md | independence / follow-up persistence boundary |
| USAGE.md | 双遍有界分析、Review/Follow-up、多 Agent 使用语义 |
| semantic tests | 新 contract tests + 旧模型迁移 |

# 验证矩阵

| Layer | Required | 当前证据 |
| --- | --- | --- |
| Behavior / semantic contract | required | Red 35938644999；Green 35943593916 |
| Routing / cross-skill | required | Router/specialist contract tests Green |
| Context budget | required | 35943593916 Green；未提高预算 |
| Runtime Project Payload | required | project-facing projection tests Green |
| Build / CLI | required | 35943593916 compile/CLI smoke Green |
| Package | required | Ready 后 current-head Runtime Package Gate |
| Docs / Governance | required | USAGE + Change + managed AGENTS + preservation tests |
| Independent Review | required | review 5298706847 @ 5a634230；Ready commit 后增量 re-review |
| External model actual run | not_applicable | 无真实 child-model execution interface，不伪造 benchmark |

# 风险、兼容性、迁移与回滚

- Finding current canonical 由 disposition 迁到三轴；历史记录保留历史事实。
- Runtime public MCP / License / Release ZIP protocol、Role ID、业务 API/ABI/Schema/Data 均不变。
- 无依赖升级、无 Migration、无生产数据操作。
- Project-facing managed AGENTS 需后续正常 Release/upgrade 才进入旧安装实例；本任务不创建 Release。
- actual 外部模型效果仍 unverified；static/fixture/CI 不冒充真实模型 benchmark。
- 回滚为 revert PR，无不可逆操作。

# 文档、依赖、部署与发布影响

- **文档**：canonical rules、managed AGENTS、USAGE 已同步。
- **依赖**：无新增/升级。
- **Schema / 数据**：无变化。
- **Runtime public protocol**：无变化。
- **Release / Deploy**：不执行；只取得本 Change classifier 要求的 package Evidence。
- **回滚**：revert PR。

# 完成审计

- [x] upstream_re_read：已重读 #308、current main `095b2d80...`、final implementation head canonical owners。
- [x] change_coverage：已从 #308 AC1–AC17 独立映射；R1–R15 satisfied，R16–R17 明确交给 downstream Delivery Gate。
- [x] reverse_audit：已反查 Analysis stop、Review 三轴/净收敛、Follow-up persistence、cross-skill、independence、Mutation/Eval、managed/USAGE，并确认 current live Owner 无旧 disposition 第二模型。
- [x] unresolved_cleared：Ready 前 required 实现/验证问题已清零；不存在 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | revision / run | 结果 | 证明 |
| --- | --- | --- | --- |
| V1 | main `095b2d80...` + #308 | confirmed | 起始事实 / Requirement Source |
| V2 | run `35938644999` | 新 11 个 contract tests 在旧语义上失败 | 有效 Red |
| V3 | 多轮中间 CI | projection/legacy anchors/context budget 回归被持续捕获 | 未通过删测试/抬预算造 Green |
| V4 | head `5a634230...` / run `35943593916` | compile、CLI smoke、selected self-contained tests、context budget、ready structure Green；唯一 failure=status in_progress enforcement | Ready 前 semantic Green |
| V5 | PR #309 review `5298706847` @ `5a634230...` | NO_BLOCKING_FINDINGS_WITHIN_SCOPE | Requirement-first Review |

## 未验证内容与剩余风险

- 本提交只把 Change 置为 Ready，会形成新 HEAD；必须取得该 HEAD 的 required CI/package 和增量 Review。
- 未运行真实 GPT/Claude/Cursor/DeepSeek child-model actual benchmark；仍标记 unverified。
- 不创建 Runtime Release；旧发布 binary 不自动获得本次新 project-facing rules。

## 交付状态

- 分支：`tech/two-pass-cross-skill-convergence`
- PR：#309，open / non-draft
- Change：本提交置为 `ready_for_review`
- Review：5298706847 @ 5a634230，无阻塞 Finding；Ready commit 后需增量 re-review
- CI：Red 已取得；Ready 前 semantic Green 已取得；Ready 后 final-head required CI/package 待执行
- merge/main-fresh/archive/Issue Closure/branch cleanup：待 Delivery Gate
- Release / Deploy：not_applicable
