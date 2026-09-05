---
schema: coding-change/v1
id: CHG-20260905-112643-autonomy-validation-boundaries
title: 收敛自主执行、审批与验证边界
level: L2
status: ready_for_review
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

- [x] 专业 Owner 只由真实专业对象/意图稳定命中，不由通用执行模式、阶段、审查/验证/capability 机械叠加无关 Skill。
- [x] “事实恢复/核验”与“提请用户/Owner 决策”语义明确，已确认决定不重复询问，审批要求与权限边界不降低。
- [x] 阻塞只沿真实依赖传播；三次失败假设触发回到诊断而不是无条件停止整个任务。
- [x] 小改动验证有明确下限、上限和单调升级条件；未知先有界调查；无关重构和邻近技术债不进入当前 Scope。
- [x] Skill Mutation 区分只读 Audit/Proposal 与 canonical Apply，并按影响类型选择开发侧 Evidence；正式仓库 CI 门禁保持。
- [x] 受影响规则不再使用与 Stable ID 混淆的裸 `refNN` 表述。
- [x] Figma 普通设计审查与正式 baseline-ready 意图分离，现有写权限/Design-to-Code 门禁保持。
- [x] 端到端交付增加分轴状态表达，但整体完成硬门禁保持不变。
- [x] 当前实现 head 的 routing/preservation/minimal-governance/Figma/Review/Mutation 相关回归与完整 Skill Tests 通过；实际 diff 保持 `content` scope，不触发三平台 package。

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
- Owner 隔离按专业意图统一收口：Testing-only、Figma-only、独立 `文档审查/编写/更新/同步` 出现时，Coding 的通用内容动作与阶段不能反向制造 Coding Owner；真实 `诊断` 与 `实现 + 测试专业意图` 继续按 Testing Handoff 组合 Coding+Testing；`Git/发布/运维` 仍属于 Coding 的真实交付/运行职责，Review 专业意图继续组合 Coding，`Docs targeted/full` 继续表示 Coding→Docs Handoff，`设计转代码/代码实现/技术方案` 等显式 Coding 意图继续稳定命中 Coding。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 专业 Owner 不被通用执行模式、阶段、审查/验证/capability 机械叠加 | #216 / AC1 | satisfied | 首轮 Review 的 Figma-only Finding 由 commit `362a7675712a9dba8e98fe358fa189b455a757bb` / run #1236 精确 Red；第二轮系统矩阵 commit `e66cc6fbd462721c0a57cf740719480a71fa1702` / run #1239 取得 5 个专业 Owner 隔离失败。系统修复后 run #1242 只剩 2 个 Coding+Testing Handoff 误伤，commit `6f8c45314f6db0fe5a1ab4bb5084e5ec8c4a7a6c` 恢复 canonical 条件式 Handoff；最终 head `09fad9d55894c9ccdad7731d8ec70fdde5c7b44c` / run #1244 中 `test_testing_and_standalone_docs_intents_block_generic_coding_fallbacks`、`test_figma_only_plan_and_fix_modes_do_not_create_coding_owner`、`test_explicit_coding_handoffs_survive_specialized_owner_isolation`、Owner isolation、Routing Conformance 与 Source/Runtime parity 全部通过。 |
| R2 | 核验/决策分离，审批保持且无权限扩大 | #216 / AC2 | satisfied | Router/Coding/Review/Figma 已明确事实核验默认自行完成、只有重大未决边界才提请决策且不重复确认；run #1244 的完整 Skill Tests 与 authorization/Review/Figma 回归通过，PR diff 未新增 Git/merge/release/deploy 权限。 |
| R3 | blocked 依赖传播；三次失败返回诊断 | #216 / AC3 | satisfied | Router/Coding/Diagnosis/Delivery 明确 blocker 只沿依赖传播，三次失败只停止同类补丁并返回事实恢复/根因诊断；run #1244 的 diagnosis/delivery/fail-closed 回归通过。 |
| R4 | 小改动 targeted-first，按具体风险逐层扩大且禁止无关重构 | #216 / AC4 | satisfied | Validation 定义验证下限/默认上限/单调升级，Cleanup 明确旧技术债默认只记录 Finding；run #1244 的 validation/minimal-governance/context-budget 回归通过。预算修复未提高阈值，只对共享 ENTRY 做等价去重。 |
| R5 | Mutation Audit/Apply + 影响分档，不降低正式 CI | #216 / AC5 | satisfied | Mutation Reference 明确 `Mutation Audit / Proposal`、`Mutation Apply`、`Semantic Local`、`Contract / Routing`、`Runtime / Package`，正式 CI 不被 targeted-first 替代；run #1244 的 preservation/Mutation/Runtime parity 回归通过。 |
| R6 | 受影响规则消除裸 refNN 歧义 | #216 / AC6 | satisfied | 受影响 Router/Coding/route/Mutation 使用明确文件链接和 Stable ID；run #1244 的 ambiguous-ref、Reference numbering 与 runtime handoff preservation 回归通过。 |
| R7 | Figma 普通审查与 baseline-ready 意图分离 | #216 / AC7 | satisfied | Figma Core 仅由专业意图触发；普通“全面检查/审查/找问题”默认 review-only，明确开发交付/READY 才 baseline-ready；run #1244 的 Figma review-only、baseline-ready、Design-to-Code 与 Owner 隔离回归通过。 |
| R8 | 端到端分轴状态 + overall completion gate 不降低 | #216 / AC8 | satisfied | Delivery 已增加分轴状态并保持所有 required 轴完成后才能 `end_to_end: complete`；run #1244 的 delivery governance 回归通过。 |
| R9 | 当前 head 相关回归与完整 Skill Tests 通过且不触发 package | #216 / AC9 | satisfied | 实现 head `09fad9d55894c9ccdad7731d8ec70fdde5c7b44c` / run #1244：Requirement Source、编译、CLI smoke 通过；`Ran 471 tests in 6.628s` / `OK`；Routing Conformance、Source/Runtime exact-context、minimal-governance、Figma、Review、Mutation、context-budget 全部 Green。classifier=`content`，Linux onefile/MCP/install steps skipped，Windows/macOS package jobs skipped；run 唯一失败是 Changed Change 仍为 `in_progress`，不属于 AC9 行为/内容证据。当前 carrier-only Ready 提交后仍必须取得新的 current-head CI。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 初始 run #1214 Red；首轮 Figma Finding run #1236 Red；第二轮系统 Owner run #1239 为 5 failures；run #1242 收敛到 2 个合法 Handoff 误伤；run #1243 语义矩阵全绿但暴露 100 B / 7 B 预算超限；run #1244 最终 471/471 Green。 |
| 接口 / 契约 | required | `Agent Skills Skill路由/v1` Core trigger/Owner 语义改变；run #1244 的 metadata compiler、Routing Conformance、Source/Runtime manifest 同值、dependency closure、owner-gated routing 与 exact-context 全部通过。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变数据库、文件运行语义、MCP 执行机制或 Runtime service；未修改 Runtime Python/Installer/Bundle executable 实现。 |
| 用户 / 工作流验收 | required | run #1244 证明 Testing-only、Figma-only、Standalone Docs 在内容动作/阶段 facts 下不误叠加 Coding，同时真实诊断/实现+Testing、Design-to-Code、Docs targeted/full、Code Review Handoff 保持。 |
| 跨组件关键路径 | not_applicable | 不改变 Runtime/Installer/Project Payload/Release 接线；Source/Runtime 路由一致性由 run #1244 平台无关 Skill Tests 证明。 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要第三方服务、生产环境或外部 Provider 当前事实。 |
| 构建 / 打包 / 运行 | not_applicable | diff 未触及 executable/package/platform boundary；run #1244 classifier=`content`，Linux binary steps及 Windows/macOS package jobs 均 skipped。 |
| 文档 / 治理 / 其他 | required | canonical Rule/trigger/Stable ID/引用、内容守恒与 context budget 已由 run #1244 证明；Ready、独立 re-review、merge/main-fresh/Archive/Closure 继续作为后续交付门禁。 |

# 完成审计

- [x] upstream_re_read：最终 Green 后重新读取 live #216、current main `3135d58e1fe2b011ebfcf4c1a40845e66e54d235`、当前 head 根 `AGENTS.md` 与 ENTRY；此前已按当前 Mutation 链完整读取 Maintenance、Router、Coding、Validation、Review、Runtime 与 Mutation Owner，上游 AC1-AC9 未漂移。
- [x] change_coverage：#216 / AC1-AC9 全部映射 R1-R9；两轮独立 Review Finding 均并入 R1 并由失败→修复→Green Evidence 闭环，没有新建平行规则或未追踪延期。
- [x] reverse_audit：从 Coding 通用 Owner 入口反查 Testing/Figma/Docs/Review 专业 Core 与 Handoff，确认专业-only 不再被内容动作/阶段旁路激活，同时诊断、实现+Testing、Design-to-Code、Docs targeted/full、Code Review 等合法组合继续可达；没有权限扩大、Runtime evaluator/CI/阈值放宽或无关重构。
- [x] unresolved_cleared：R1-R9 全部为 `satisfied` 且有直接 Evidence；Validation Matrix required 项已有 run #1244 当前实现证据，N/A 与实际 diff 边界一致，无 `not_satisfied`。

# 任务

- [x] 恢复当前 main、Maintenance、ENTRY、Router、Coding 与命中 References。
- [x] 建立并 live re-read Requirement Source #216、专用分支与本 Change。
- [x] 初始回归先行 commit `bc59363ab2840fb0f3e453612ef47581d288661f` / run #1214 取得 Red。
- [x] 完成首轮 Router/Coding/Review/Figma/Validation/Mutation/Diagnosis/Delivery 收敛并取得 run #1235 468/468 Green。
- [x] 首轮独立 Review 发现 Figma-only `方案/实现` HIGH Finding；commit `362a7675712a9dba8e98fe358fa189b455a757bb` / run #1236 精确 Red。
- [x] commit `56165527f9767e8387c64ad8989e6612356ef0bc` 修复首轮 Finding，run #1237 取得 469/469 Green；carrier-only Ready 后 run #1238 取得 469/469、Ready 与 Runtime Package Gate 全绿。
- [x] 第二轮独立 re-review 系统审计发现 `阶段` 与 Testing/Standalone Docs 内容动作仍可绕过 Owner 隔离，Review 继续 `CHANGES_REQUIRED`。
- [x] commit `e66cc6fbd462721c0a57cf740719480a71fa1702` 新增系统 Owner 矩阵，run #1239 取得 5 个精确 Red。
- [x] 系统修复后 run #1242 将问题收敛为 2 个 Coding+Testing Handoff 误伤；commit `6f8c45314f6db0fe5a1ab4bb5084e5ec8c4a7a6c` 恢复条件式 Handoff。
- [x] run #1243 语义回归 Green 后只剩 backend-l2-feature 超 100 B、Skill Mutation 超 7 B；未提高阈值，commit `09fad9d55894c9ccdad7731d8ec70fdde5c7b44c` 等价压缩共享 ENTRY，run #1244 取得 471/471 Green。
- [x] 完成最终 Completion Audit，并将 Change 恢复为 `ready_for_review`。
- [ ] 取得 carrier-only Ready 提交的 current-head CI，确认 Changed Change Ready 与 Runtime Package Gate Green。
- [ ] 执行独立 re-review；只有 PASS 才进入 merge preflight。
- [ ] re-review PASS 后更新 PR 真实状态，merge 前重新核对 live Requirement Source/head/base/权限/Ruleset。
- [ ] guarded merge 后取得 implementation main-fresh CI、repository-native Change Archive、Closure Audit、Issue Acceptance 写回/关闭与分支清理。

# 验证

## 计划

- Targeted routing：`test_autonomy_validation_boundaries.py`、`test_skill_owner_isolation.py`、`test_owner_gated_routing.py`、`test_routing_conformance.py`、`test_runtime_routing.py`、`test_source_runtime_context_conformance.py`。
- Targeted owner matrix：Testing-only / Figma-only / Standalone Docs 反例；`诊断 + Testing`、`实现 + 用户场景验收`、Design-to-Code、Docs targeted/full、Code Review 正例。
- 正式 PR/main：仓库当前 `content` scope 的完整 Skill Tests + Changed Change Ready Gate；不运行 package scope，除非实际 diff 扩大。

## 新鲜证据

- 当前 `main` HEAD：`3135d58e1fe2b011ebfcf4c1a40845e66e54d235`。
- 初始 Red：commit `bc59363ab2840fb0f3e453612ef47581d288661f` / run #1214。
- 首轮 Finding Red：commit `362a7675712a9dba8e98fe358fa189b455a757bb` / run #1236。
- 首轮 Finding Fix：commit `56165527f9767e8387c64ad8989e6612356ef0bc`；run #1237 为 469/469 Green；run #1238 Ready 亦 Green。
- 系统 Owner Red：commit `e66cc6fbd462721c0a57cf740719480a71fa1702` / run #1239，新增矩阵暴露 5 failures。
- 系统中间态：head `93ea3bcfbca545814e494e32b31d6c94e579f6a4` / run #1242，专业-only 反例已 Green，但两个合法 Coding+Testing Handoff 被误伤。
- 条件式 Handoff 修复：commit `6f8c45314f6db0fe5a1ab4bb5084e5ec8c4a7a6c`；run #1243 语义矩阵全部 Green，只剩 context budget：backend-l2-feature 195100 > 195000、Skill Mutation 213247 > 213240。
- 最终实现 Green：head `09fad9d55894c9ccdad7731d8ec70fdde5c7b44c` / run #1244；Requirement Source、编译、CLI smoke 通过；`Ran 471 tests in 6.628s` / `OK`；context budget、Routing Conformance、Source/Runtime parity、Owner/Handoff 全绿；classifier=`content`，Linux binary steps和 Windows/macOS package skipped。唯一失败是 Changed Change 当时仍为 `in_progress`。
- 预算修复没有调整阈值：只等价压缩共享 ENTRY 的重复描述；永久隐私、Source/Runtime、宿主 UI、required Context 守恒测试在 run #1244 全部通过。

# 文档影响

本次仍只修改 Agent_Skills canonical governance/Skill/回归与 Change，不改变 README/USAGE/runtime README 面向人类说明；Docs Impact 由 canonical Owner 本身承载。

# 交付

- Requirement Source：#216。
- 分支：`agent/autonomy-validation-boundaries-216`。
- PR：#217。
- 当前阶段：实现与 Completion Audit 已 Green，Change=`ready_for_review`；独立 re-review 待执行，尚不得合并。
- merge：仅在 re-review PASS、Review 后 current-head CI、live Requirement Source、当前 main/base、Ruleset/权限和 expected head guard 满足后执行。
- post-merge：repository-native Change Archive + implementation main-fresh + Closure Audit；Agent 不手工归档 Change，也不把 archive/done 冒充 Issue Closure。
