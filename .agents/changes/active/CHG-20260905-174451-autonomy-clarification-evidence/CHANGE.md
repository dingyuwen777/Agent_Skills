---
schema: coding-change/v1
id: CHG-20260905-174451-autonomy-clarification-evidence
title: 进一步收敛自主执行、澄清与验证边界
level: L2
status: in_progress
owner: dingyuwen777
branch: agent/autonomy-clarification-evidence-218
created: 2026-09-05
updated: 2026-09-05
completion_gate: required
depends_on: []
affected_areas:
  - autonomy-and-clarification
  - validation-evidence
  - authorization-handoff
  - skill-mutation-routing
  - testing-handoff
  - completion-scope
  - maintenance-overlay
affected_paths:
  - AGENTS.md
  - .agents/MAINTENANCE.md
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/02_跨项目研发任务路由.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/references/25_Testing专业职责与Handoff.md
  - .agents/skills/testing/SKILL.md
  - .agents/skills/review/SKILL.md
  - .agents/skills/figma/SKILL.md
  - .agents/skills/coding/tests/
contracts:
  - Agent Skills Skill路由/v1
  - Fresh Evidence Contract
  - Authorization Continuity Contract
  - Mutation Audit Apply Routing Contract
  - Requested Outcome Completion Contract
data_changes: []
---

# 目标

在不降低任何既有审批、安全、Review、CI、PR、merge、Release、Deploy、生产操作或 Completion Gate 的前提下，继续消除会让不同能力模型无必要停住、重复询问、重复跑验证或自动追求最大闭环的剩余二义性。

# 成功标准

- [ ] Mutation Audit/Proposal 与 Apply 在 required Context 上真实分离。
- [ ] “充分验证 / 完整命令”不再被误读为全仓、全层或全平台测试。
- [ ] Fresh Evidence 可按 revision/environment/contract/scope 有界复用，不因执行主体不同重复运行。
- [ ] 非重大歧义有确定性的自主默认动作，不阻塞也不提请用户逐项确认。
- [ ] 同目标/同范围/同副作用等级授权跨 Handoff 连续有效，但绝不升级权限等级。
- [ ] L3 独立重大决策可一次有界提请，避免人为串行逐项确认。
- [ ] Testing Workflow/User Journey 只在真实独立风险或结论需要时叠加。
- [ ] Requested Outcome 明确决定 Completion Scope，能力存在不自动扩大终点。
- [ ] Mutation Audit 只要求 canonical read；Apply 才要求写入/Change/PR/CI/delivery 能力；Maintenance L2/L3 Change 明确为本仓库 Overlay。
- [ ] Task Route 示例只使用正式 machine vocabulary；现有 Owner/Handoff/Source-Runtime parity 不回归。
- [ ] targeted 回归与仓库 required Skill Tests Green，scope 保持 content/routing，不触发三平台 binary package。

# 范围

- 收敛 Router/Coding 的自主默认、授权连续性和 Completion Scope。
- 建立 Fresh Evidence 的唯一语义 Owner，其他 Skill 只引用该语义。
- 把 Mutation Audit/Apply 从“正文分离”推进到正式 required Context 分离。
- 对 Testing 用户工作流、L3 Decision Package、Maintenance Overlay 与 machine vocabulary 做最小一致性修正。
- 只增加直接保护上述 Contract 的最小回归。

# 非目标

- 不做 routing schema v2 / `Owner触发` 与 `细化条件` 字段级重构。
- 不修改 Runtime evaluator/executable、Bundle、Installer、MCP、Project Payload、Release 或 CI Workflow。
- 不提高 context budget，不削弱 required CI，不增加无关测试框架或无关重构。
- 不扩大生产代码写入、Git、merge、Release、Deploy、生产 Migration/数据写删权限。

# 必须保持不变

- public Contract、Schema/数据、Migration、重大架构、核心技术路线、高成本/难逆决策仍受现有 Plan Review Gate / Owner 审批约束。
- Review-only、test-only、Figma review-only 不获得生产写入或 Git/merge/release/deploy 权限。
- Requested Action 不提升 Effective Authorization；Branch Protection/Ruleset/required CI/Review/Completion Gate 不绕过。
- Agent_Skills 源仓库本身 L2/L3 继续要求正式 Change、独立 Review、PR/main CI、main-fresh、repository-native Change Archive 与 Requirement Closure。
- 正式 `content` scope CI 不因开发侧 targeted-first 被删除或跳过。

# 关键决策

- 本次不执行 routing schema v2；该改动会扩大到 Runtime executable/package，不符合本次最小充分范围。
- Fresh Evidence 的“新鲜”按受验证 revision/environment/contract/scope 是否仍有效判断，不按“是否由当前 Agent 刚运行”判断。
- Authorization Continuity 只在同目标、同范围、同副作用等级内成立；更高副作用动作必须已经存在对应授权。
- Mutation Audit/Apply 使用现有 Task Route vocabulary/metadata 能力完成分路由，不建立平行 Skill 或第二套 Router。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Mutation Audit/Apply required Context 真分离 | #218 / AC1 | not_satisfied | 待实现与 routing conformance |
| R2 | 充分验证/完整命令语义消歧 | #218 / AC2 | not_satisfied | 待规则与 targeted 回归 |
| R3 | Fresh Evidence Contract | #218 / AC3 | not_satisfied | 待规则与复用条件回归 |
| R4 | Non-material Ambiguity Default | #218 / AC4 | not_satisfied | 待 Router/Coding 规则 |
| R5 | Authorization Continuity 不升级权限 | #218 / AC5 | not_satisfied | 待 Router/Handoff 回归 |
| R6 | L3 Decision Package | #218 / AC6 | not_satisfied | 待 Planning 规则 |
| R7 | Testing Workflow 条件式叠加 | #218 / AC7 | not_satisfied | 待 Testing/Handoff 回归 |
| R8 | Requested Outcome = Completion Scope | #218 / AC8 | not_satisfied | 待 Router/Delivery/专业模式规则 |
| R9 | Mutation read/apply capability 与 Maintenance Overlay 消歧 | #218 / AC9 | not_satisfied | 待 AGENTS/Maintenance 规则 |
| R10 | machine vocabulary 统一且路由不回归 | #218 / AC10 | not_satisfied | 待 route 文本与 Source/Runtime parity |
| R11 | targeted + required Skill Tests Green，scope 不扩大 | #218 / AC11 | not_satisfied | 待 current-head CI |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 依据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | autonomy/mutation/testing/completion targeted regression |
| 接口 / 契约 | required | `Agent Skills Skill路由/v1` 的 Mutation Audit/Apply required Context、Source/Runtime parity、machine vocabulary |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改 Runtime executable、数据库、文件协议或外部 runtime dependency |
| 用户 / Workflow Acceptance | required | 通过代表性 Task Route 证明不同请求终点/授权/Testing Handoff 的可观察路由行为 |
| 跨组件 Golden Path | not_applicable | 不改多组件产品运行链 |
| 外部依赖 Probe | not_applicable | 不需要第三方当前事实 |
| Build / Package / Runtime | not_applicable | 不改 executable/package/platform；正式 CI classifier 若发现相反事实则升级 |
| Docs / Governance / Other | required | Change/Requirement/Review/CI/Archive/Closure 与内容守恒审计 |

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared
