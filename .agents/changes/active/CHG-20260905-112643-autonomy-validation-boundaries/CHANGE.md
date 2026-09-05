---
schema: coding-change/v1
id: CHG-20260905-112643-autonomy-validation-boundaries
title: 收敛自主执行、审批与验证边界
level: L2
status: in_progress
owner: dingyuwen777
branch: agent/autonomy-validation-boundaries-216
created: 2026-09-05
updated: 2026-09-05
completion_gate: required
depends_on: []
affected_areas:
  - skill-routing
  - coding-governance
  - validation-strategy
  - skill-mutation
  - review-and-figma-routing
  - delivery-reporting
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/02_跨项目研发任务路由.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/21_系统级分析与代码整洁收口.md
  - .agents/skills/coding/references/22_根因调试.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/review/SKILL.md
  - .agents/skills/figma/SKILL.md
  - .agents/skills/coding/tests/
contracts:
  - Agent Skills Skill路由/v1
  - Minimal Sufficient Governance
  - Skill Mutation Impact Audit Contract
  - End-to-end Delivery Completion Contract
data_changes: []
---

# 目标

在不降低审批、安全、Completion、Review、CI、PR、Release 和交付门禁的前提下，收敛 Agent_Skills 中可能导致模型无必要停止、重复确认、机械叠加 Skill、扩大验证或顺手重构的含糊/重叠语义，使不同能力模型都能按确定性的“默认动作 + 最低要求 + 默认上限 + 升级条件 + 停止扩大条件”稳定执行。

# 成功标准

- [ ] 专业 Owner 只由真实专业对象/意图稳定命中，不由通用执行模式、阶段、审查/验证/capability 机械叠加无关 Skill。
- [x] “事实恢复/核验”与“提请用户/Owner 决策”语义明确，已确认决定不重复询问，审批要求与权限边界不降低。
- [x] 阻塞只沿真实依赖传播；三次失败假设触发回到诊断而不是无条件停止整个任务。
- [x] 小改动验证有明确下限、上限和单调升级条件；未知先有界调查；无关重构和邻近技术债不进入当前 Scope。
- [x] Skill Mutation 区分只读 Audit/Proposal 与 canonical Apply，并按影响类型选择开发侧 Evidence；正式仓库 CI 门禁保持。
- [x] 受影响规则不再使用与 Stable ID 混淆的裸 `refNN` 表述。
- [x] Figma 普通设计审查与正式 baseline-ready 意图分离，现有写权限/Design-to-Code 门禁保持。
- [x] 端到端交付增加分轴状态表达，但整体完成硬门禁保持不变。
- [ ] 当前 head 的 routing/preservation/minimal-governance/Figma/Review/Mutation 相关回归与完整 Skill Tests 通过；实际 diff 保持 `content` scope，不触发三平台 package。

# 范围

- 收敛 Router/Coding 的专业 Owner、事实核验、阻塞和升级语义。
- 调整 Review/Figma Core trigger 与普通审查默认模式，避免能力或通用执行模式机械叠加。
- 调整 Validation、Mutation、系统分析/清理、根因调试和端到端交付的范围/完成表达。
- 复用并扩展现有 routing、minimal-governance、Figma、Review、Mutation/preservation 回归。

# 非目标

- 不修改 Runtime Python、Bundle、Installer、MCP Tool Contract、Project Payload、加密、Release identity 或三平台 binary package 机制。
- 不修改 CI Workflow 或为了本 Change 降低/删除 required check。
- 不新增平行“模型兼容”Skill/Reference，不复制第二套 Router/Validation/Mutation 规则。
- 不升级依赖/Runtime，不修改 public API、Schema、数据或生产环境。
- 不扩大 merge、Release、Deploy、生产 Migration/数据写删等权限。

# 必须保持不变

- 用户/Owner 对 public Contract、Schema/数据语义、Migration、重大架构、核心路线、高成本/难逆决策的审批要求继续生效。
- Review-only、Testing、Figma review-only 不因流程优化获得生产修改或 Git/merge/release/deploy 权限。
- Requested Action 不提升 Effective Authorization；Branch Protection/Ruleset/CI/Review/Completion Gate 不绕过。
- Source/Runtime 使用同一 canonical routing metadata、Stable ID、依赖和风险下限；任何 routing metadata 修改必须由现有 Routing Conformance 证明没有意外欠披露。
- Agent_Skills canonical content 仍按当前仓库 `content` scope 执行正式 Skill Tests；开发侧 targeted-first 不等于删除正式 CI 门禁。
- repository-native Change Archive 和 Requirement Closure Owner 不改变。

# 关键决策

- 不新增“不同模型能力适配”平行规则层；把确定性语义写回现有唯一 Owner。
- 统一术语：事实恢复/核验默认由 Agent 自行从当前请求、仓库、工具和正式事实源完成；只有条款明确要求“提请用户/Owner 决策/批准”且答案会实质改变关键边界时才询问。
- 统一 Blocked Scope：缺失事实/能力/权限只阻塞依赖它的动作和完成声明；无依赖且已授权的工作继续，整体 end-to-end 完成状态仍受全部 required gate 约束。
- 验证采用 targeted-first：低影响可逆变更先复用最相关现有测试；只有失败、新行为/Contract/依赖、新独立失败边界、正式门禁或具体剩余风险才逐层扩大。
- 本次修改 routing/core governance content，属于 Contract/Routing 影响；Runtime executable/package/platform boundary 不受影响，因此开发侧不运行三平台 package，仓库既有 content CI 保持。
- #216 / AC9 的验收范围是“当前 head 相关测试 + 仓库 Skill Tests + package scope 不扩大”；Ready、独立 Review、merge、main-fresh、Change Archive 和 Closure 继续作为 Maintenance 的后续交付门禁，不混入 Ready 前的 Requirement Traceability 形成循环前置条件。
- Owner 隔离按专业意图统一收口：Testing-only、Figma-only、独立 `文档审查/编写/更新/同步` 出现时，Coding 的通用内容动作与阶段只能作为任务事实，不能反向制造 Coding Owner；`Git/发布/运维` 仍属于 Coding 的真实交付/运行职责，Review 专业意图继续组合 Coding，`Docs targeted/full` 继续表示 Coding→Docs Handoff，`设计转代码/代码实现/技术方案` 等显式 Coding 意图继续稳定命中 Coding。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 专业 Owner 不被通用执行模式、阶段、审查/验证/capability 机械叠加 | #216 / AC1 | not_satisfied | 首轮 Review 已证明 Figma-only `方案/实现` 误叠加并完成一次 Red→Fix→Green；独立 re-review 进一步发现同构绕过：Runtime evaluator 的 Owner refinement 不包含 `阶段`，Coding Core 又直接以研发阶段和 `只读分析/诊断/方案/实现` 等通用内容动作选择 Owner，因此 Figma-only 携带阶段、Testing-only 的测试方案/测试实现、独立 Docs 分析/编写仍会反向增加 Coding。当前提交只新增系统矩阵回归并退回开发态，待取得精确 Red 后统一修复。 |
| R2 | 核验/决策分离，审批保持且无权限扩大 | #216 / AC2 | satisfied | Router/Coding/Review/Figma 已明确事实核验默认自行完成、只有重大未决边界才提请决策且不重复确认；run #1238 的完整 Skill Tests 与授权/Review/Figma 回归通过，PR diff 未新增 Git/merge/release/deploy 权限。 |
| R3 | blocked 依赖传播；三次失败返回诊断 | #216 / AC3 | satisfied | Router/Coding/Diagnosis/Delivery 明确 blocker 只沿依赖传播，三次失败只停止同类补丁并返回事实恢复/根因诊断；run #1238 的相关回归通过。 |
| R4 | 小改动 targeted-first，按具体风险逐层扩大且禁止无关重构 | #216 / AC4 | satisfied | Validation 定义验证下限/默认上限/单调升级，Cleanup 明确旧技术债默认只记录 Finding；run #1238 的 validation/minimal-governance/context-budget 回归通过。 |
| R5 | Mutation Audit/Apply + 影响分档，不降低正式 CI | #216 / AC5 | satisfied | Mutation Reference 明确 `Mutation Audit / Proposal`、`Mutation Apply`、`Semantic Local`、`Contract / Routing`、`Runtime / Package`，正式 CI 不被 targeted-first 替代；run #1238 的 preservation/Mutation 回归通过。 |
| R6 | 受影响规则消除裸 refNN 歧义 | #216 / AC6 | satisfied | 受影响 Router/Coding/route/Mutation 使用明确文件链接和 Stable ID；run #1238 的 ambiguous-ref、Reference numbering 与 runtime handoff preservation 回归通过。 |
| R7 | Figma 普通审查与 baseline-ready 意图分离 | #216 / AC7 | satisfied | Figma Core 仅由专业意图触发；普通“全面检查/审查/找问题”默认 review-only，明确开发交付/READY 才 baseline-ready；run #1238 的 Figma 模式回归通过。当前 R1 的系统 Owner Finding 不改变该模式 Contract，只说明 Coding fallback 仍可旁路误叠加。 |
| R8 | 端到端分轴状态 + overall completion gate 不降低 | #216 / AC8 | satisfied | Delivery 已增加分轴状态并保持所有 required 轴完成后才能 `end_to_end: complete`；run #1238 的 delivery governance 回归通过。 |
| R9 | 当前 head 相关回归与完整 Skill Tests 通过且不触发 package | #216 / AC9 | not_satisfied | Review 前 head `ee4c7ae6cb7edc3641432c12c14d6244f9dabd3a` / run #1238 为 469/469 Green、Ready/Runtime Package Gate PASS、classifier=`content`、Windows/macOS package skipped；但 re-review 发现 R1 新漏测。本次新增系统矩阵回归后必须先取得新的 Red，再修复并由新的 current-head 完整 Skill Tests 重新证明。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 已有初始 Red、首轮 Figma Finding Red→Green 与 run #1238 469/469 Green；本轮新增 Testing/Figma/Standalone Docs 通用内容动作+阶段 Owner 隔离反例，并保留 Design-to-Code、Docs targeted、Code Review 正例，待 CI 取得精确 Red。 |
| 接口 / 契约 | required | `Agent Skills Skill路由/v1` Core trigger/Owner 语义继续调整；修复后必须通过 metadata compiler、Routing Conformance、Source/Runtime manifest 同值、dependency closure、owner-gated routing 与 exact-context。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变数据库、文件运行语义、MCP 执行机制或 Runtime service；不修改 Runtime Python/Installer/Bundle executable 实现。 |
| 用户 / 工作流验收 | required | 必须证明 Testing-only、Figma-only、Standalone Docs 在真实内容动作/阶段 facts 下仍只命中专业 Owner；Design-to-Code、Docs targeted/full、Code Review 等真实 Coding Handoff 仍命中 Coding。 |
| 跨组件关键路径 | not_applicable | 不改变 Runtime/Installer/Project Payload/Release 接线；Source/Runtime 路由一致性继续由平台无关 Skill Tests 证明。 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要第三方服务、生产环境或外部 Provider 当前事实。 |
| 构建 / 打包 / 运行 | not_applicable | 计划仍只改 canonical content/metadata/tests；未触及 executable/package/platform boundary，正式 scope 应保持 `content`。 |
| 文档 / 治理 / 其他 | required | Router/Coding/测试/Change 的 Owner 语义与内容守恒必须同步；不修改预算阈值、CI Workflow 或 Runtime evaluator 来制造 Green。 |

# 完成审计

- [x] upstream_re_read：独立 re-review 后已重新读取 live #216、当前 main `3135d58e1fe2b011ebfcf4c1a40845e66e54d235`、当前分支根 `AGENTS.md`、Maintenance、ENTRY、Router、Coding 与完整 Mutation Reference；上游 AC1-AC9 未漂移。
- [x] change_coverage：#216 / AC1-AC9 仍映射 R1-R9；第二轮 Review Finding 已并入 R1 和系统 Owner 矩阵，而不是新建平行规则或留作未追踪 Finding。
- [x] reverse_audit：从 Coding 的所有通用 Owner 入口反查 Testing/Figma/Docs/Review 专业 Core 后，确认 `阶段` 与内容动作 fallback 存在同类旁路；Review、Docs targeted/full、Design-to-Code 等真实 Coding Handoff 被列为必须保持的正例。
- [ ] unresolved_cleared：R1、R9 当前未满足；必须先取得新增回归 Red、完成系统性最小修复、current-head Green，再重新 Completion Audit 与 re-review。

# 任务

- [x] 恢复当前 main、Maintenance、ENTRY、Router、Coding 与命中 References。
- [x] 建立并 live re-read Requirement Source #216、专用分支与本 Change。
- [x] 初始回归先行 commit `bc59363ab2840fb0f3e453612ef47581d288661f` / run #1214 取得 Red。
- [x] 完成首轮 Router/Coding/Review/Figma/Validation/Mutation/Diagnosis/Delivery 收敛并取得 run #1235 468/468 Green。
- [x] 首轮独立 Review 发现 Figma-only `方案/实现` HIGH Finding；commit `362a7675712a9dba8e98fe358fa189b455a757bb` / run #1236 精确 Red。
- [x] commit `56165527f9767e8387c64ad8989e6612356ef0bc` 修复首轮 Finding，run #1237 取得 469/469 Green；carrier-only Ready 后 run #1238 取得 469/469、Ready 与 Runtime Package Gate 全绿。
- [x] 第二轮独立 re-review 系统审计发现 `阶段` 与 Testing/Standalone Docs 内容动作仍可绕过 Owner 隔离，Review 继续 `CHANGES_REQUIRED`。
- [ ] 新增系统 Owner 矩阵回归，取得精确 Red；本提交不修改生产 metadata。
- [ ] 统一修复 Coding 通用内容动作/阶段 fallback，同时保持普通 Coding、Design-to-Code、Docs targeted/full、Code Review 正例。
- [ ] 取得 current-head 完整 Skill Tests Green、预算/conformance/parity Green，并保持 `content` scope。
- [ ] 重新完成 Completion Audit、恢复 `ready_for_review` 并执行独立 re-review。
- [ ] re-review PASS 后更新 PR 真实状态，merge 前重新核对 live Requirement Source/head/base/权限/Ruleset。
- [ ] guarded merge 后取得 implementation main-fresh CI、repository-native Change Archive、Closure Audit、Issue Acceptance 写回/关闭与分支清理。

# 验证

## 计划

- Targeted routing：`test_autonomy_validation_boundaries.py`、`test_skill_owner_isolation.py`、`test_owner_gated_routing.py`、`test_routing_conformance.py`、`test_runtime_routing.py`、`test_source_runtime_context_conformance.py`。
- Targeted owner matrix：Testing-only + `方案/实现/阶段`、Figma-only + `方案/实现/阶段`、Standalone Docs + `只读分析/实现/阶段`；正例覆盖 `设计转代码`、`Docs targeted`、`代码审查`。
- 正式 PR/main：仓库当前 `content` scope 的完整 Skill Tests + Changed Change Ready Gate；不运行 package scope，除非实际 diff 扩大。

## 新鲜证据

- 当前 `main` HEAD：`3135d58e1fe2b011ebfcf4c1a40845e66e54d235`。
- 初始 Red：commit `bc59363ab2840fb0f3e453612ef47581d288661f` / run #1214。
- 首轮 Finding Red：commit `362a7675712a9dba8e98fe358fa189b455a757bb` / run #1236。
- 首轮 Finding Fix：commit `56165527f9767e8387c64ad8989e6612356ef0bc`；run #1237 为 `Ran 469 tests` / `OK`。
- Review 前 Ready Green：head `ee4c7ae6cb7edc3641432c12c14d6244f9dabd3a` / run #1238，469/469、Changed Change Ready、Runtime Package Gate 全部 PASS；classifier=`content`；Windows/macOS package skipped。
- 第二轮 re-review 证据：`runtime/agent_skills_runtime/routing.py` 的 `_OWNER_REFINEMENT_DIMENSIONS` 仅含项目形态/风险/工具链/范围/治理/授权，不含 `阶段`；Coding Core 仍以阶段和多个通用内容动作直接触发 Owner。Testing/Docs/Figma Core 均由专业 `意图` 触发，因此专业任务附带阶段/内容动作时存在可触发的 Coding 误叠加路径。

# 文档影响

本次仍只修改 Agent_Skills canonical governance/Skill/回归与 Change，不改变 README/USAGE/runtime README 面向人类说明；Docs Impact 由 canonical Owner 本身承载。

# 交付

- Requirement Source：#216。
- 分支：`agent/autonomy-validation-boundaries-216`。
- PR：#217。
- 当前独立 Review：`CHANGES_REQUIRED`；不得合并。
- merge：仅在系统 Owner Finding 修复、re-review PASS、Review 后 current-head CI、live Requirement Source、当前 main/base、Ruleset/权限和 expected head guard 满足后执行。
- post-merge：repository-native Change Archive + implementation main-fresh + Closure Audit；Agent 不手工归档 Change，也不把 archive/done 冒充 Issue Closure。
