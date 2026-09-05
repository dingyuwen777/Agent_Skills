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

- [x] 专业 Owner 只由真实专业对象/意图稳定命中，不由通用执行模式/审查/验证/capability 机械叠加无关 Skill。
- [x] “事实恢复/核验”与“提请用户/Owner 决策”语义明确，已确认决定不重复询问，审批要求与权限边界不降低。
- [x] 阻塞只沿真实依赖传播；三次失败假设触发回到诊断而不是无条件停止整个任务。
- [x] 小改动验证有明确下限、上限和单调升级条件；未知先有界调查；无关重构和邻近技术债不进入当前 Scope。
- [x] Skill Mutation 区分只读 Audit/Proposal 与 canonical Apply，并按影响类型选择开发侧 Evidence；正式仓库 CI 门禁保持。
- [x] 受影响规则不再使用与 Stable ID 混淆的裸 `refNN` 表述。
- [x] Figma 普通设计审查与正式 baseline-ready 意图分离，现有写权限/Design-to-Code 门禁保持。
- [x] 端到端交付增加分轴状态表达，但整体完成硬门禁保持不变。
- [x] 当前实现 head 的 routing/preservation/minimal-governance/Figma/Review/Mutation 回归与完整 Skill Tests 通过；实际 diff 保持 `content` scope，不触发三平台 package。

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
- Figma-only `review-and-fix / baseline-ready` 的 `方案/实现` 只是 Figma 专业动作，不得单独制造 Coding Owner；普通非 Figma `方案/实现` 继续作为 Coding 默认入口，真实 `代码实现/技术方案/设计转代码` 等专业 Coding 意图仍能稳定命中 Coding。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 专业 Owner 不被通用执行模式/审查/验证/capability 机械叠加 | #216 / AC1 | satisfied | 首轮独立 Review 在 head `f02a00e28c420eb52283e092fc79985b2712fcbe` 发现 HIGH：Figma-only baseline/fix 的 `方案/实现` 会机械增加 Coding。回归提交 `362a7675712a9dba8e98fe358fa189b455a757bb` 对应 run #1236 精确 Red：`test_figma_only_plan_and_fix_modes_do_not_create_coding_owner` 显示 baseline actual 多出 `coding`。修复 commit `56165527f9767e8387c64ad8989e6612356ef0bc` 将 Coding 的通用 `方案/实现` 入口条件化排除 `Figma review-and-fix / Figma baseline-ready`，但保留显式 Coding 意图；run #1237 中该回归、Figma→Code 正例、Ad-hoc/L1 Coding 正例、Owner isolation、Routing Conformance 全部通过。 |
| R2 | 核验/决策分离，审批保持且无权限扩大 | #216 / AC2 | satisfied | Router/Coding/Review/Figma 明确事实核验默认自行完成、只有重大未决边界才提请决策且不重复确认；run #1237 的 `test_router_and_coding_distinguish_self_verification_decision_and_blocked_scope` 及既有 authorization/review/Figma 权限回归通过；PR diff 未新增任何 Git/merge/release/deploy 权限。 |
| R3 | blocked 依赖传播；三次失败返回诊断 | #216 / AC3 | satisfied | Router/Coding/Diagnosis/Delivery 明确 blocker 只沿依赖传播，三次失败只停止同类补丁并返回事实恢复/根因诊断；run #1237 的 `test_three_failed_fix_hypotheses_return_to_diagnosis_not_whole_task_stop`、delivery axis 回归及现有 fail-closed 回归通过。 |
| R4 | 小改动 targeted-first，按具体风险逐层扩大且禁止无关重构 | #216 / AC4 | satisfied | Validation 定义验证下限/默认上限/单调升级，Cleanup 明确旧技术债默认只记录 Finding；run #1237 的 `test_validation_has_lower_upper_bound_and_monotonic_escalation`、`test_cleanup_does_not_absorb_preexisting_adjacent_technical_debt`、minimal-governance 与 context-budget 回归全部通过。 |
| R5 | Mutation Audit/Apply + 影响分档，不降低正式 CI | #216 / AC5 | satisfied | Mutation Reference 明确 `Mutation Audit / Proposal`、`Mutation Apply`、`Semantic Local`、`Contract / Routing`、`Runtime / Package`，并声明开发侧 profile 不替代正式 CI；run #1237 的 Mutation canonical ownership/preservation/delivery governance 回归全部通过。 |
| R6 | 受影响规则消除裸 refNN 歧义 | #216 / AC6 | satisfied | 受影响 Router/Coding/route/Mutation 使用明确文件链接和 Stable ID；run #1237 的 `test_affected_rules_do_not_use_ambiguous_bare_ref_numbers`、Reference numbering 与 runtime handoff preservation 回归通过。 |
| R7 | Figma 普通审查与 baseline-ready 意图分离 | #216 / AC7 | satisfied | Figma Core 仅由专业意图触发；普通“全面检查/审查/找问题”默认 review-only，明确开发交付/READY 才 baseline-ready；run #1237 的 `test_figma_plain_audit_defaults_to_review_only_not_baseline_ready`、Figma-only `review-and-fix/baseline-ready` Owner 隔离、Figma→Code 正例与完整 Figma Skill 回归全部通过。 |
| R8 | 端到端分轴状态 + overall completion gate 不降低 | #216 / AC8 | satisfied | Delivery 增加 implementation/validation/delivery/main_fresh/change_archive/requirement_closure/cleanup/end_to_end 分轴，同时规定所有 applicable + required 轴完成后才能 `end_to_end: complete`；run #1237 的 `test_delivery_reports_axis_status_without_weakening_overall_completion` 及现有 delivery governance 回归通过。 |
| R9 | 当前 head 相关回归与完整 Skill Tests 通过且不触发 package | #216 / AC9 | satisfied | 初始需求回归先行 commit `bc59363ab2840fb0f3e453612ef47581d288661f` / run #1214 为真实 Red；首轮 Review Finding 回归 commit `362a7675712a9dba8e98fe358fa189b455a757bb` / run #1236 为精确 Red；修复 head `56165527f9767e8387c64ad8989e6612356ef0bc` 的 run #1237 执行 469 项 self-contained tests，结果 `OK`，Requirement Source、编译、CLI smoke 通过，context budget、legacy preservation、Routing Conformance、Source/Runtime manifest 同值全部 Green；scope classifier=`content`，Windows/macOS package jobs skipped。当前 Change-only Ready 写入后由新一轮 PR CI 再验证 Ready Gate。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 初始 run #1214 为 Red；Review Finding run #1236 为精确 Red；fix run #1237 为 469/469 Green，包含新增 Figma-only Owner 隔离、已有 Coding/Figma 正例、minimal governance、Review、Mutation、diagnosis、delivery 与 context budget。 |
| 接口 / 契约 | required | `Agent Skills Skill路由/v1` Core trigger/Owner 语义改变；run #1237 的 metadata compiler、Routing Conformance、Source/Runtime manifest 同值、dependency closure、owner-gated routing 与 exact-context 回归通过。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变数据库、文件运行语义、MCP 执行机制或 Runtime service；changed files 无 Runtime Python/Installer/Bundle executable 实现。 |
| 用户 / 工作流验收 | required | 典型路由证明 Figma/Docs/Testing/Review 不机械叠加无关 Owner；Figma review-only/review-and-fix/baseline-ready 与 Router 表一致，真实 Figma→Code 仍命中 Coding+Figma。 |
| 跨组件关键路径 | not_applicable | 不改变 Runtime/Installer/Project Payload/Release 接线；Source/Runtime 路由一致性由 run #1237 的平台无关 Skill Tests 证明。 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要第三方服务、生产环境或外部 Provider 当前事实。 |
| 构建 / 打包 / 运行 | not_applicable | diff 未触及 executable/package/platform boundary；run #1237 classifier 为 `content`，三平台 package 不应执行且 Windows/macOS jobs skipped。 |
| 文档 / 治理 / 其他 | required | canonical Rule/trigger/Stable ID/引用、内容守恒、context budget 与路由迁移守恒已由 run #1237 的 469 项 Skill Tests 证明；Change-only Ready 写入后继续由 Changed Change Ready Gate 验证。 |

# 完成审计

- [x] upstream_re_read：已重新读取 live #216、当前 main `3135d58e1fe2b011ebfcf4c1a40845e66e54d235` 的根治理/Maintenance 事实以及当前分支 ENTRY；上游 AC1-AC9 与 main 均未发生影响本 Change 的漂移。
- [x] change_coverage：#216 / AC1-AC9 均绑定为 R1-R9；首轮独立 Review 发现的 Figma-only `方案/实现` Owner 漏测已纳入 R1、Regression 与当前 conformance，而不是留作未追踪 Finding。
- [x] reverse_audit：已从 Router 表、Coding Core metadata、Runtime evaluator、Figma Core、Validation、Mutation、Cleanup、Diagnosis、Delivery、Review 和测试反向审计；首轮 HIGH Finding 已通过 Red→Fix→Green 闭环，未发现权限扩大、CI/预算阈值放宽、无关 Runtime/package 变更或第二套 Owner/规则体系。
- [x] unresolved_cleared：R1-R9 全部为 `satisfied` 且有直接 Evidence；Validation Matrix required 项已有新鲜实现 head 证据，N/A 项与实际 diff 职责一致，无 `not_satisfied`。独立 re-review 属于 Ready 后交付门禁，不作为 Requirement Traceability 的循环前置条件。

# 任务

- [x] 恢复当前 main、Maintenance、ENTRY、Router、Coding 与命中 References。
- [x] 确认当前无 Active Change，建立并 live re-read Requirement Source #216。
- [x] 建立专用分支与本 Change。
- [x] 先扩展最小现有回归，取得初始 Red/current-old-behavior 证据：commit `bc59363ab2840fb0f3e453612ef47581d288661f` / run #1214 self-contained tests failure。
- [x] 最小修改 Router/Coding/Review/Figma 与直接 Owner References。
- [x] 执行 targeted-first 开发验证并按实际失败收敛；首轮 Ready 前 run #1235 为 468/468 Green。
- [x] 完成 Rule→metadata/tests/runtime parity 影响审计与裸 refNN 检查。
- [x] 首轮 Completion Audit 与 Ready 已完成。
- [x] 首轮独立 Review 发现 HIGH Finding：Figma-only `方案/实现` 会机械增加 Coding Owner，并返回开发态。
- [x] 为 Review Finding 取得 run #1236 精确 Red，使用 commit `56165527f9767e8387c64ad8989e6612356ef0bc` 最小修复 Coding Owner trigger，并由 run #1237 取得 469/469 Green、预算与 conformance Green。
- [x] 重新完成 Completion Audit，并恢复 `ready_for_review`。
- [ ] 对新的 Ready head 执行独立 re-review；如再有 Finding，继续修复→验证→re-review。
- [ ] 取得 re-review 后 current-head PR CI，merge 前重新核对 live Requirement Source/head/base/权限/Ruleset。
- [ ] guarded merge 后取得 implementation main-fresh CI、repository-native archive、Closure Audit、Issue Acceptance 写回/关闭与分支清理。

# 验证

## 计划

- Targeted routing：`test_autonomy_validation_boundaries.py`、`test_owner_gated_routing.py`、`test_routing_conformance.py`、`test_runtime_routing.py`、`test_source_runtime_context_conformance.py`。
- Targeted governance：`test_minimal_sufficient_governance.py`、`test_skill_mutation_canonical_ownership.py`、`test_skill_owner_isolation.py`、`test_reference_numbering.py`。
- Targeted owner behavior：`test_figma_skill.py`、`test_review_skill.py`、`test_systemic_diagnosis.py` 及 delivery governance 现有回归。
- 正式 PR/main：仓库当前 `content` scope 的完整 Skill Tests + Changed Change Ready Gate；不运行 package scope，除非实际 diff 扩大。

## 新鲜证据

- 当前 `main` HEAD：`3135d58e1fe2b011ebfcf4c1a40845e66e54d235`；该变化来自其他已归档 Change，不属于本 PR 范围。
- 初始 Red：回归先行 commit `bc59363ab2840fb0f3e453612ef47581d288661f` / run #1214 self-contained tests failure。
- Review 前 Green：head `f02a00e28c420eb52283e092fc79985b2712fcbe` / run #1235 为 468/468 Green 且 Changed Change Ready PASS。
- 首轮独立 Review HIGH Finding：Figma-only baseline/fix 的 `执行模式=方案/实现` 会通过 Coding Core 的通用模式 trigger 机械增加 Coding Owner。
- Finding Red：commit `362a7675712a9dba8e98fe358fa189b455a757bb` / run #1236，469 tests 中仅新增 `test_figma_only_plan_and_fix_modes_do_not_create_coding_owner` 失败；baseline actual 多出 `coding`，context budget 等既有回归保持通过。
- Finding Fix：commit `56165527f9767e8387c64ad8989e6612356ef0bc`；Coding 通用 `方案/实现` trigger 只在不存在 `Figma review-and-fix / Figma baseline-ready` 专业意图时生效；显式 `代码实现/技术方案/设计转代码` 等 Coding intent 保持。
- Finding Green：run #1237 / merge ref `c88d447abbf0ad15f6e12af1beb68c8f8ac797e8`，Requirement Source、编译、CLI smoke 通过；`Ran 469 tests in 5.810s`、`OK`；新增 Figma-only 回归、Figma→Code、Ad-hoc/L1 Coding、context budget、legacy route preservation、Routing Conformance、Source/Runtime manifest 同值全部通过。
- Scope：run #1237 classifier=`content`；Windows/macOS Runtime Package jobs skipped；本 PR 未改变 executable/package/platform boundary。
- run #1237 Agent Skills Gate 的唯一失败来自 Change 故意保持 `in_progress`，Ready Check 报“状态必须为 ready_for_review”；本次 carrier-only 提交即用于解除该预期门禁，并由下一轮 current-head CI 重新证明。

# 文档影响

本次修改的是 Agent_Skills canonical governance/Skill 文本，不改变 README/USAGE/runtime README 面向人类说明；文档影响由 canonical Owner 自身承载，Docs Skill 不需要额外用户文档 diff。

# 交付

- Requirement Source：#216。
- 分支：`agent/autonomy-validation-boundaries-216`。
- PR：#217。
- 首轮独立 Review：`CHANGES_REQUIRED`；HIGH Finding 已修复并有 Red→Green Evidence，当前等待独立 re-review。
- merge：仅在 re-review PASS、re-review 后 current-head CI、live Requirement Source、当前 main/base、Ruleset/权限和 expected head guard 满足后执行。
- post-merge：repository-native Change Archive + implementation main-fresh + Closure Audit；Agent 不手工归档 Change，也不把 archive/done 冒充 Issue Closure。
