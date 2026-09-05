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

- [ ] 专业 Owner 只由真实专业对象/意图稳定命中，不由通用审查/验证/capability 机械叠加无关 Skill。
- [ ] “事实恢复/核验”与“提请用户/Owner 决策”语义明确，已确认决定不重复询问，审批要求与权限边界不降低。
- [ ] 阻塞只沿真实依赖传播；三次失败假设触发回到诊断而不是无条件停止整个任务。
- [ ] 小改动验证有明确下限、上限和单调升级条件；未知先有界调查；无关重构和邻近技术债不进入当前 Scope。
- [ ] Skill Mutation 区分只读 Audit/Proposal 与 canonical Apply，并按影响类型选择开发侧 Evidence；正式仓库 CI 门禁保持。
- [ ] 受影响规则不再使用与 Stable ID 混淆的裸 `refNN` 表述。
- [ ] Figma 普通设计审查与正式 baseline-ready 意图分离，现有写权限/Design-to-Code 门禁保持。
- [ ] 端到端交付增加分轴状态表达，但整体完成硬门禁保持不变。
- [ ] 当前 head 的相关 targeted tests、完整 Skill Tests、Ready/Review/PR/main-fresh 门禁全部满足；scope 不扩大到 package。

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

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 专业 Owner 不被通用审查/验证/capability 机械叠加 | #216 / AC1 | not_satisfied | 待实现并由 owner-gated routing/routing conformance 证明。 |
| R2 | 核验/决策分离，审批保持且无权限扩大 | #216 / AC2 | not_satisfied | 待实现并人工语义审计。 |
| R3 | blocked 依赖传播；三次失败返回诊断 | #216 / AC3 | not_satisfied | 待实现并由 governance/diagnosis 回归证明。 |
| R4 | 小改动 targeted-first，按具体风险逐层扩大且禁止无关重构 | #216 / AC4 | not_satisfied | 待实现并由 validation/minimal-governance 回归证明。 |
| R5 | Mutation Audit/Apply + 影响分档，不降低正式 CI | #216 / AC5 | not_satisfied | 待实现并由 mutation/preservation 回归证明。 |
| R6 | 受影响规则消除裸 refNN 歧义 | #216 / AC6 | not_satisfied | 待执行引用扫描/现有 numbering/preservation checks。 |
| R7 | Figma 普通审查与 baseline-ready 意图分离 | #216 / AC7 | not_satisfied | 待实现并由 Figma routing/skill tests 证明。 |
| R8 | 端到端分轴状态 + overall completion gate 不降低 | #216 / AC8 | not_satisfied | 待实现并由 delivery governance 回归证明。 |
| R9 | targeted + 完整 Skill Tests 通过且不触发 package | #216 / AC9 | not_satisfied | 待 current-head PR/main CI。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 复用 owner-gated routing、minimal governance、Figma、Review、Mutation、diagnosis、delivery 现有回归；只新增直接防止本次语义回退的断言。 |
| 接口 / 契约 | required | `Agent Skills Skill路由/v1` Core trigger/Owner 语义改变；必须验证 metadata 可解析、Source/Runtime routing conformance 与 dependency closure。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变数据库、文件运行语义、MCP 执行机制或 Runtime service。 |
| 用户 / 工作流验收 | required | 以典型任务路由证明普通文档/Figma/Testing/Review 不机械叠加无关 Owner，普通小改动/阻塞能按目标继续。 |
| 跨组件关键路径 | not_applicable | 不改变 Runtime/Installer/Project Payload/Release 接线；routing conformance 由现有平台无关 Skill Tests 承担。 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要第三方服务或生产环境当前事实。 |
| 构建 / 打包 / 运行 | not_applicable | executable/package/platform boundary 不变；按 Maintenance content scope 不运行三平台 onefile package。 |
| 文档 / 治理 / 其他 | required | canonical Rule/trigger/Stable ID/引用、Change/Ready、内容守恒、独立 Review、PR/main-fresh/Change Archive/Issue Closure。 |

# 完成审计

- [ ] upstream_re_read：合并前重新读取 #216、当前 main 适用规则和受影响 canonical Owner。
- [ ] change_coverage：逐项核对 #216 AC1-AC9 均映射到本 Change 与真实 Evidence。
- [ ] reverse_audit：从 Routing、Validation、Mutation、Review/Figma、Diagnosis、Delivery 反向确认没有欠披露/权限扩大/无关流程。
- [ ] unresolved_cleared：R1-R9 全部有直接 Evidence 或正式 N/A/deferred 依据，无 `not_satisfied`。

# 任务

- [x] 恢复当前 main、Maintenance、ENTRY、Router、Coding 与命中 References。
- [x] 确认当前无 Active Change，建立并 live re-read Requirement Source #216。
- [x] 建立专用分支与本 Change。
- [ ] 先扩展最小现有回归，取得 Red/current-old-behavior 证据。
- [ ] 最小修改 Router/Coding/Review/Figma 与直接 Owner References。
- [ ] 执行 targeted validation；只有失败/新风险才扩大开发侧验证。
- [ ] 完成 Rule→metadata/tests/runtime parity 影响审计与裸 refNN 检查。
- [ ] 将 Change 更新为 `ready_for_review`，完成 Completion Audit 与独立 Review。
- [ ] 取得 current-head PR CI，merge 前重新核对 Requirement Source/head/base/权限/Ruleset。
- [ ] guarded merge 后取得 main-fresh CI、repository-native archive、Closure Audit、Issue Acceptance 写回/关闭与分支清理。

# 验证

## 计划

- Targeted routing：`test_owner_gated_routing.py`、`test_routing_conformance.py`、`test_runtime_routing.py`、`test_source_runtime_context_conformance.py`。
- Targeted governance：`test_minimal_sufficient_governance.py`、`test_skill_mutation_canonical_ownership.py`、`test_skill_owner_isolation.py`、`test_reference_numbering.py`。
- Targeted owner behavior：`test_figma_skill.py`、`test_review_skill.py`、`test_systemic_diagnosis.py` 及 delivery governance 现有回归。
- 正式 PR/main：仓库当前 content scope 的完整 Skill Tests + Changed Change Ready Gate；不运行 package scope，除非实际 diff 扩大。

## 新鲜证据

- 当前 `main` 基线 HEAD：`7476de295924fd09866110ed715b11523741d14b`。
- GitHub live Requirement Source：#216 已创建并写后重读，AC1-AC9 保持 open/unresolved 等待实现 Evidence。
- 当前 main `.agents/changes` 无 active Change，本 Change 是唯一当前施工单元。
- 本地容器 `git clone` 因 `Could not resolve host: github.com` 失败；因此本地终端测试不可用，该能力缺口只影响本地执行，不阻塞 GitHub App 写入与 PR Actions 验证。

# 文档影响

本次修改的是 Agent_Skills canonical governance/Skill 文本，不改变 README/USAGE/runtime README 面向人类说明；文档影响由 canonical Owner 自身承载，Docs Skill 不需要额外用户文档 diff。

# 交付

- Requirement Source：#216
- 分支：`agent/autonomy-validation-boundaries-216`
- PR：待创建。
- merge：仅在 Change Ready、独立 Review、current-head CI、live Requirement Source、Ruleset/权限和 head guard 满足后执行。
- post-merge：repository-native Change Archive + main-fresh + Closure Audit；Agent 不手工归档 Change。