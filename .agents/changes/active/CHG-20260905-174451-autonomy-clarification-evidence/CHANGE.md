---
schema: coding-change/v1
id: CHG-20260905-174451-autonomy-clarification-evidence
title: 进一步收敛自主执行、澄清与验证边界
level: L2
status: ready_for_review
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
  - .agents/skills/coding/references/02_跨项目研发任务路由.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/25_Testing专业职责与Handoff.md
  - .agents/skills/coding/references/28_SkillMutation影响面一致性审计.md
  - .agents/skills/testing/SKILL.md
  - .agents/skills/coding/tests/test_autonomy_clarification_evidence.py
  - .agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py
  - .agents/skills/coding/tests/test_skill_router_single_source.py
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

- [x] Mutation Audit/Proposal 与 Apply 在 required Context 上真实分离。
- [x] “充分验证 / 完整命令”统一解释为完整执行已选择的风险匹配 Evidence，不再等价为全仓、全层或全平台测试。
- [x] Fresh Evidence 可按 revision/environment/Contract/Scope 有界复用，不因执行主体不同重复运行。
- [x] 非重大歧义有确定性的自主默认动作，不阻塞也不提请用户逐项确认。
- [x] 同目标/同范围/同副作用等级授权跨 Handoff 连续有效，但绝不升级权限等级。
- [x] L3 独立重大决策可一次有界提请，避免人为串行逐项确认。
- [x] Testing Workflow/User Journey 只在真实独立风险或结论需要时叠加。
- [x] Requested Outcome 明确决定 Completion Scope，能力存在不自动扩大终点。
- [x] Mutation Audit 只要求 canonical read；Apply 才要求写入/Change/PR/CI/delivery 能力；Maintenance L2/L3 Change 明确为本仓库 Overlay。
- [x] Task Route 示例只使用正式 machine vocabulary；现有 Owner/Handoff/Source-Runtime parity 不回归。
- [x] targeted 回归与仓库 required Skill Tests Green，scope 保持 content/routing，不触发三平台 binary package。

# 范围

- 收敛 Router/Coding 的自主默认、授权连续性和 Completion Scope。
- 建立 Fresh Evidence 的唯一跨 Skill 解释，并让专业验证方法继续留在既有 Owner。
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
- Fresh Evidence 的“新鲜”按受验证 revision/environment/Contract/Scope 是否仍有效判断，不按“是否由当前 Agent 刚运行”判断。
- Authorization Continuity 只在同目标、同范围、同副作用等级内成立；更高副作用动作必须已经存在对应授权。
- `Skill Mutation + 只读分析` 保持 Audit-compatible；显式 `Skill Mutation Apply`、具体写入意图，以及兼容旧调用的 `Skill Mutation + 执行模式=实现` 进入 Apply 完整门禁。
- Router 的新增跨模型语义保持为短硬规则；Testing、Planning、Mutation 的专业方法继续由各自既有 Owner 承担，不建立新 Skill/Reference。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Mutation Audit/Apply required Context 真分离 | #218 / AC1 | satisfied | `test_mutation_audit_does_not_preload_apply_only_governance` 与 `test_mutation_apply_restores_full_change_validation_review_and_impact_context` 在 PR head `6cb9fa304efdb9f6ffc7ad7123740a1bddf760aa` 的 Skill Tests #1258 通过；宽泛 Mutation + 实现继续兼容 Apply 重门禁。 |
| R2 | 充分验证/完整命令语义消歧 | #218 / AC2 | satisfied | Router 明确“完整验证证据 / 完整命令 / 完整输出”只指完整执行已选风险匹配 Evidence，不代表全仓/全层/全平台；对应新回归与 #1258 全量 Skill Tests Green。 |
| R3 | Fresh Evidence Contract | #218 / AC3 | satisfied | Router 明确 revision/environment/Contract/Scope 与失效条件，明确“不是当前 Agent 启动”不构成重跑理由；新回归与 #1258 通过。 |
| R4 | Non-material Ambiguity Default | #218 / AC4 | satisfied | Router 固化“项目既有模式 → 最小范围 → 最小副作用 → 最可逆 → 最少新机制”；新回归与 #1258 通过。 |
| R5 | Authorization Continuity 不升级权限 | #218 / AC5 | satisfied | Router 固化同目标/同范围/同副作用等级连续性和副作用等级梯度；Testing/Handoff 同步引用；新回归与 #1258 通过。 |
| R6 | L3 Decision Package | #218 / AC6 | satisfied | `05_设计实施与根因调试.md` 固化最上游问题优先、独立重大决策有界 Decision Package 和事实源排除；Planning 历史回归与新回归在 #1258 通过。 |
| R7 | Testing Workflow 条件式叠加 | #218 / AC7 | satisfied | Testing Core 与 Coding→Testing Handoff 明确独立 Workflow 风险/当前结论驱动、现有有效公开入口 Evidence 可复用且不机械重复 Journey；#1258 通过既有 Testing 与新增回归。 |
| R8 | Requested Outcome = Completion Scope | #218 / AC8 | satisfied | Router 固化 review-only/test-only/develop-and-submit/develop-and-deliver/Mutation Audit 的终点；既有 Delivery endpoint 回归与新回归在 #1258 通过。 |
| R9 | Mutation read/apply capability 与 Maintenance Overlay 消歧 | #218 / AC9 | satisfied | 根 AGENTS 明确 Audit 只需 canonical read、Apply 才需 write/Change/PR/CI/delivery；Maintenance 明确 Agent_Skills 专属 L2/L3 Change Overlay；#1258 通过。 |
| R10 | machine vocabulary 统一且路由不回归 | #218 / AC10 | satisfied | `02_跨项目研发任务路由.md` 路由卡使用 `审查/发布` 正式协议值；Routing Conformance、Source/Runtime context parity、Router preservation 在 #1258 全部 Green。 |
| R11 | targeted + required Skill Tests Green，scope 不扩大 | #218 / AC11 | satisfied | Verify Red：head `fec8f66e8792fe01b2dd3ae3bf29fd49de722a0e` / #1255 的新增 Contract 回归真实失败；Green：head `6cb9fa304efdb9f6ffc7ad7123740a1bddf760aa` / #1258 `Ran 482 tests in 6.017s` / `OK`；classifier=`content` 并明确 binary package evidence 不适用，Windows/macOS package skipped；未改 Runtime/Workflow/依赖/package 路径。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 依据 | 当前证据 |
| --- | --- | --- | --- |
| 行为 / 单元 / 组件 | required | autonomy/mutation/testing/completion targeted regression | #1255 Verify Red；#1258 482/482 Green |
| 接口 / 契约 | required | `Agent Skills Skill路由/v1` 的 Mutation Audit/Apply required Context、Source/Runtime parity、machine vocabulary | #1258 routing/metadata/conformance/parity 全绿 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改 Runtime executable、数据库、文件协议或外部 runtime dependency | PR changed-file 反查无相关路径 |
| 用户 / Workflow Acceptance | required | 代表性 Task Route 证明不同请求终点/授权/Testing Handoff 的可观察路由行为 | 新增回归 + 既有 Testing/Owner 路由回归 #1258 Green |
| 跨组件 Golden Path | not_applicable | 不改多组件产品运行链 | 无对应边界 |
| 外部依赖 Probe | not_applicable | 不需要第三方当前事实 | 无外部事实依赖 |
| Build / Package / Runtime | not_applicable | 不改 executable/package/platform | #1258 classifier=`content`；binary package evidence not applicable；平台 package jobs skipped |
| Docs / Governance / Other | required | Change/Requirement/Review/CI/Archive/Closure 与内容守恒审计 | 当前 Completion Audit；独立 Review/merge/post-merge/Closure 仍作为后续交付门禁 |

# Completion Audit

- [x] upstream_re_read：2026-09-05 在进入 Ready 前重新读取 live Requirement Source #218；AC1–AC11 未漂移，当前 main 仍为 `9b02f35042a277d09ec207d9f65f046fb68fec65`。
- [x] change_coverage：AC1–AC11 分别映射 R1–R11；实际 changed files 仅为本 Change、9 个 canonical 治理/专业规则文件与 3 个直接回归文件，没有额外业务/Runtime/Workflow/依赖范围。
- [x] reverse_audit：从当前 diff 反查 Rule → routing metadata/dependency → permanent tests → Source/Runtime parity/context budget/CI classifier；未提高 context budget，未修改 Runtime evaluator/Workflow/package，也未降低审批、权限、Review、CI、Completion 或交付门禁。历史 Router 守恒失败均恢复仍有效硬语义；旧 `Skill Mutation + 实现` 保留 Apply-compatible，不以放宽 benchmark 制造 Green。
- [x] unresolved_cleared：R1–R11 均有当前实现与 #1258 直接/回归证据；Validation Matrix 的 N/A 项均有实际 diff 边界依据。独立 Review、最终 current-head CI、merge/main-fresh、Change Archive 与 Issue Closure 属于 Ready 后交付门禁，不冒充当前 Completion Audit 已完成的证据。

# Docs Impact

`not_applicable`：本次修改的是 Agent/治理 canonical 规则与其永久回归，没有改变最终用户 Runtime 获取、安装、升级、CLI/MCP 使用方式，也没有改变 `README.md` / `USAGE.md` / `runtime/README.md` 面向维护者或最终用户的事实；不为产生文档 diff 修改这三个人类入口。
