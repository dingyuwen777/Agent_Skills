---
schema: coding-change/v1
id: CHG-20260920-105900-validation-asset-redundancy-gate
title: 把验证资产冗余清理升级为合并前完成门禁
level: L2
status: ready_for_review
owner: dingyuwen777
branch: feature/validation-asset-redundancy-gate
created: 2026-09-20
updated: 2026-09-20
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - validation
  - ci-cost
  - delivery
affected_paths:
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/tests/test_docs_ci_fast_path.py
contracts:
  - Validation Asset Redundancy Gate
  - PR Ready / merge completion gate
data_changes: []
---

# 变更摘要

- **要解决的问题**：现有规则会主动检查 CI/Test/Action 成本并减少无关执行，但没有明确要求把本次范围内已证明没有独立长期 Evidence 价值的验证资产在 PR Ready / merge 前删除、合并或职责重组。
- **拟议修改**：以 coding.reference.28 作为详细 Owner，新增 Validation Asset Redundancy Gate；Maintenance、Review/Completion、Delivery 只增加薄触发和完成边界；补永久回归。
- **预期结果**：以后每次准备 PR Ready / merge 时，如果本次改动新引入、扩大、直接触及或 CI 实际暴露冗余 test/job/workflow，且可证明清理不降低 Required Evidence，就必须主动收口，而不是只靠 selector/skip 隐藏。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #279。用户明确要求以后每次合并主分支时，若存在相关测试或 Run Job 冗余风险，AI 应主动删除或合并。

## 当前现状

- Maintenance 已要求每次维护执行 changed-scope Evidence Check。
- coding.reference.28 已要求每次实现默认检查 Cost / Evidence，并包含 CI 消重顺序。
- 永久回归已保护“不能等用户发现 Actions 消耗过高”“优先减少何时运行”“无关 test group / 重复 setup/build”等语义。
- 现有规则没有把“验证资产本身无独立长期证明价值时必须清理”显式定义为 PR Ready / merge 前门禁。

## 问题、根因或约束

缺口不是缺少 CI 成本意识，而是“执行成本优化”和“永久资产去冗余”没有形成闭环：selector 可以让重复资产少跑，但仍可能长期保留职责重复或职责混杂的 tests/jobs/workflows。

## 不修改的后果

- 新增或暴露的冗余验证资产可能长期留存，只是被 selector 隐藏。
- 同一 Contract 可能继续由多个 test/job 重复证明，增加维护同步成本。
- 职责混杂的测试文件可能再次把无关依赖/Runner 拉入 changed-scope。
- 用户仍需再次提醒“把冗余测试/Run Job 删掉或合并”。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 每次维护都必须 changed-scope Evidence Check | .agents/MAINTENANCE.md §9 | 现有机制应增强而非平行新建 |
| E2 | 每次实现默认加载 CI Cost/Evidence Check | coding.reference.28 + test_docs_ci_fast_path.py | 详细 Owner 已存在 |
| E3 | 现有规则强调优先减少“何时运行” | Maintenance / reference 27 | 必须保留该原则但补上永久资产清理 |
| E4 | 用户要求合并前主动删除/合并本次相关冗余 | #279 | PR Ready/merge 必须增加完成门禁 |

## 推断与待确认

无。规则 Owner、缺口和目标均已由当前 main 与 #279 确认。

# 目标、成功标准与非目标

## 目标

让验证资产去冗余成为每次实现/维护的默认责任，并在本次改动直接相关时成为 PR Ready / merge 前的完成门禁。

## 成功标准

- [ ] 详细 Owner 明确资产范围、判定标准、必须清理条件、保留边界和 Scope 边界。
- [ ] Maintenance/Review/Delivery 都能到达同一门禁但不复制第二套完整规则。
- [ ] 永久回归能阻止未来退回“只少跑、不清永久冗余”。
- [ ] required CI / Review / merge / main-fresh / archive / closure 完成。

## 范围

- 修改 Issue #279 指定的 4 个规则文件。
- 在既有 CI/Docs fast-path 测试中增加永久回归；如职责更清晰可新增单一专用测试，但不为形式新增测试文件。

## 非目标

- 本任务不顺手重组当前 87 个测试文件。
- 不改 skill-tests/release/change-archive Workflow 拓扑。
- 不实现 PR Evidence 复用 main-fresh package 的高风险优化。
- 不修改 Runtime/Router/MCP/Release 产品行为。

## 必须保持不变

- 仍有独立 Owner/Contract/failure boundary/Evidence level 的验证资产必须保留。
- unknown/shared/CI-self 继续 fail-closed。
- 不以文件数、测试数、Job 数、YAML 行数作为优化目标。
- 无直接因果关系的历史冗余不自动扩大当前 Scope。
- required check identity、平台独立性、权限/生命周期边界不得因表面相似被合并。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Reference 27 详细 Owner，其他位置只薄触发 | E1-E3 | 避免第二套规则 |
| 接口与契约 | 新增 Validation Asset Redundancy Gate 语义 | #279 AC1-AC8 | 影响 Completion/Delivery 判定 |
| 数据与迁移 | 不适用 | 无数据变化 | 无 |
| 错误与失败语义 | required 冗余未清理时不得 Ready/mergeable | #279 AC8 | completion fail-closed |
| 兼容性 | 保留现有 changed-scope/fail-closed/独立 Evidence | #279 必须保持不变 | 不降低验证强度 |
| 部署与回滚 | 纯规则/测试变化，可 revert PR | 当前范围 | 无部署影响 |

# 修改方案与决策依据

## 最小充分方案

1. Reference 27 增加 Validation Asset Redundancy Gate：资产范围、独立证明责任、触发条件、必须清理条件、保留边界、Scope 边界、状态 clean/not_applicable/blocked。
2. Maintenance 增加源仓库专属完成要求：每次维护收尾必须执行该 Gate，不能仅靠 selector 隐藏永久冗余。
3. Reference 11 在 Completion Audit / 第二阶段质量检查中增加薄检查：进入 Ready 前确认 Gate 已 clean/not_applicable。
4. Reference 23 在 develop-and-submit/deliver 的 PR Ready / merge 前链路增加薄触发；blocked 不得宣称 Ready/mergeable。
5. 永久回归在 test_docs_ci_fast_path.py 中验证 detailed Owner 与三处薄触发关键 marker。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1-E3 | 复用现有 Owner 和路由，避免新增平行 Skill/Reference |
| D2 | E4 | 用户目标是每次交付自动收口，因此必须接入 Completion/Delivery |
| D3 | #279 范围边界 | 只处理与当前改动有直接因果关系的冗余，避免 Scope creep |

## 备选方案与取舍

- 只强化 selector：不能解决永久资产继续冗余的问题，不采用。
- 每次全仓扫描并清所有历史冗余：会把普通任务升级为无边界重构，不采用。
- 新建独立 Skill：现有 coding.reference.28 已是正式 Owner，无需增加平行体系。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 定义 Validation Asset Redundancy Gate | #279 / AC1 | satisfied | coding.reference.28 已定义 Validation Asset Redundancy Gate 与资产范围 |
| R2 | 少跑不等于允许永久冗余 | #279 / AC2 | satisfied | reference 27 明确“少跑 ≠ 允许永久冗余”及 selector/skip 禁止隐藏永久冗余 |
| R3 | 以 Owner/Contract/failure boundary/Evidence level 判定 | #279 / AC3 | satisfied | reference 27 以 Owner / Contract / failure boundary / Evidence level 为判定单位 |
| R4 | 当前范围内可证明冗余必须在 Ready/merge 前清理 | #279 / AC4 | satisfied | reference 27 明确当前直接相关且可证等价的冗余必须在 PR Ready / merge 前清理 |
| R5 | 历史无关冗余不扩大 Scope | #279 / AC5 | satisfied | reference 27 明确历史无直接因果冗余只记 Finding、不扩大 Scope |
| R6 | 独立 Evidence 不因表面相似误删 | #279 / AC6 | satisfied | reference 27 明确平台/Evidence/权限生命周期/required-check 不同则保留 |
| R7 | Maintenance 源仓库完成门禁 | #279 / AC7 | satisfied | MAINTENANCE.md 要求每次维护收尾执行同一 Gate，并使用 clean/not_applicable/blocked |
| R8 | Review/Delivery Ready/merge 薄门禁 | #279 / AC8 | satisfied | reference 11 与 23 在 ready_for_review / PR Ready / guarded merge 前要求 Gate clean/not_applicable |
| R9 | 永久回归 | #279 / AC9 | satisfied | test_docs_ci_fast_path.py 新增 detailed Owner 与 completion/delivery 两个永久回归 |
| R10 | 完整交付且不改产品行为 | #279 / AC10 | not_applicable | pre-merge Change 不自证未来 merge/main-fresh/archive/Issue Closure；这些继续由 downstream delivery gate 持有 |ng/reference 27 | 新增详细 Redundancy Gate | 唯一详细 Owner | R1-R6 |
| MAINTENANCE.md | 源仓库专属强制完成要求 | 每次维护自动执行 | R7 |
| coding/reference 11 | Completion/Review 薄触发 | Ready 前关闭缺口 | R8 |
| coding/reference 23 | submit/deliver 薄触发 | merge 前关闭缺口 | R8 |
| test_docs_ci_fast_path.py | 增加永久回归 | 防规则回退 | R9 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| coding/reference 27 | Validation Asset Redundancy Gate 详细 Owner | 统一判定与 Scope 边界 | R1-R6 |
| MAINTENANCE.md | 源仓库完成门禁薄覆盖 | 每次维护自动收口 | R7 |
| coding/reference 11 | Completion/Review 薄触发 | Ready 前关闭缺口 | R8 |
| coding/reference 23 | Delivery 薄触发 | PR Ready / merge 前关闭缺口 | R8 |
| test_docs_ci_fast_path.py | 永久回归 | 防止“只少跑、不清冗余”回退 | R9 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 永久回归验证 detailed Owner 与薄触发 marker |
| 接口 / 契约 | required | Completion/Delivery 语义保持 fail-closed 且单一 Owner |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无运行依赖变化 |
| 用户 / 工作流验收 | required | “完成并合并 main”流程能自动触发冗余清理边界 |
| 跨组件关键路径 | required | Maintenance → Reference 27 → Completion/Delivery 可达 |
| 外部依赖 / 供应方探测 | not_applicable | 无外部依赖 |
| 构建 / 打包 / 运行 | not_applicable | 不改 Runtime/package 产品行为 |
| 文档 / 治理 / 其他 | required | Requirement/Change/Review/CI/Archive/Closure |

## 验证计划

- 目标测试：`test_docs_ci_fast_path.py` 新增/修改回归。
- 相关回归：changed-scope/Completion/Delivery/Skill routing 相关 selected tests。
- 静态检查或构建：current-head required Skill Tests。
- 专项真实边界：不适用。
- 就绪检查：仓库 PR CI / ready_check。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 误删独立 Evidence 或扩大 Scope | 明确独立证明边界与直接因果范围 |
| 兼容性 | 保持现有验证强度 | 不改 selector/fail-closed/平台 Evidence |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不适用 | 纯规则与回归 |
| 回滚 / 恢复 | 可直接 revert | 不涉及外部状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：Maintenance 与 Coding References 属正式治理规则，需同步。
- **依赖 / Runtime**：不适用；不新增/升级依赖。
- **配置 / Secret**：不适用。
- **部署 / Release**：不适用；本任务不创建 Release。
- **兼容 / 消费方通知**：Runtime Project Payload 详细行为不变；Source/Runtime 产品协议不变。

# 完成审计

- [x] upstream_re_read：已重读 #279、current main 与 current branch 规则；目标和非目标无漂移。
- [x] change_coverage：R1-R9 已映射到直接实现/回归；R10 downstream 交付由 post-merge gate 持有。
- [x] reverse_audit：已从实现任务 → coding.reference.28 → Maintenance/Completion/Delivery → PR Ready/merge 反向审计可达性。
- [x] unresolved_cleared：R1-R9 satisfied，独立 Review 无 blocker；Validation Asset Redundancy Gate=clean。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 7e2e5293 | canonical reread + #279 | 已确认 | 当前 Owner、缺口和目标 |
| V2 | Draft PR #280 / run #1587 rerun | 新增回归（规则实现前） | Red：2 个新增测试按预期失败；Requirement Source/Change Contract 通过 | 证明当前规则缺少 Validation Asset Redundancy Gate |
| V3 | branch current | Reference 27 / Maintenance / refs 11+23 静态反查 | 通过 | 详细 Owner、源仓库覆盖、Completion/Delivery 薄触发均可达 |
| V4 | runs #1591/#1592/#1594 | full semantic regression | 新 Gate 语义回归已转 Green；仅 context budget 超限 | 功能/治理语义正确，但首次实现过厚 |
| V5 | reviewed head 280cae5f | 独立 Review + Redundancy Gate audit | NO_FINDINGS_WITHIN_SCOPE；Gate=clean | 不抬预算，薄 Reference 已持续压缩；本任务未新增重复验证资产 |

## 未验证内容与剩余风险

- 最终 ready_for_review head 的 required CI 尚未完成；此前 Green 语义回归仅剩 context budget，现已进一步压薄。
- merge/main-fresh/archive/Issue Closure 尚未完成。
- 本任务不修改 Runtime/Router/MCP/Release 产品行为。

## 交付状态

- 提交：当前任务分支已有实现提交；最终 ready_for_review head 见 PR #280
- 拉取请求：#280（Draft，待最终 current-head CI 后转 Ready）
- CI：Red #1587 已确认；Green 语义回归 #1591/#1592/#1594 已通过新增门禁语义，最终 current-head CI 待运行
- 合并：未执行
- Change 归档：未执行（merge 后由 repository-native automation 负责）
- 发布 / 部署：不适用，本任务不修改产品发布行为。

## 备注

无。
