---
schema: coding-change/v1
id: CHG-20260918-163300-architecture-planning-guidance
title: 强化架构设计、任务拆分与方案落地流程
level: L2
status: in_progress
owner: dingyuwen777
branch: tech/architecture-planning-guidance
created: 2026-09-18
updated: 2026-09-18
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - planning-design
  - multi-agent-collaboration
  - git-delivery
  - usage-documentation
affected_paths:
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/tests/test_development_guidance.py
  - USAGE.md
  - .agents/changes/active/CHG-20260918-163300-architecture-planning-guidance/CHANGE.md
contracts: []
data_changes: []
---

# 变更摘要

- **要解决的问题**：现有 Agent_Skills 的执行/验证/交付治理已经完整，但方案落地、代码结构设计、复杂任务纵向拆分、大型未知任务渐进规划和 Merge/Rebase 冲突意图恢复仍缺少集中、可执行的方法。
- **拟议修改**：只增强现有 Coding Owner 与最终用户说明，不新增顶层 Skill/Reference，不改变路由和 Runtime Contract。
- **预期结果**：开发者既可以先讨论方案，也可以把其他来源的方案安全映射到当前代码；复杂任务拆分反馈更快，大型任务不过早伪造完整计划，冲突按双方真实意图解决。

# 背景、现状与问题

## 背景

Requirement Source 为 #262。维护者明确排除“主动维护领域词汇”，并要求优先保证四项能力的实际使用效果，同时让 `USAGE.md` 提供可以直接复制的日常指令。

## 当前现状

- Coding 已有 Planning Contract、Plan Review Gate、第一性原理设计、TDD、Validation Matrix 和系统级分析。
- 多人/多 Agent 已有 affected paths/contracts/data/depends_on 与冲突检查，但没有明确 Vertical Slice + blocker DAG 拆分规则。
- Git 已有权限、工作区保护、PR/CI/merge 门禁，但没有完整的 intent-based conflict workflow。
- `USAGE.md` 没有系统说明“只讨论方案”“外部方案如何落地”“复杂/超大任务怎样规划”等入口。

## 问题、根因或约束

缺口不是需要更多顶层 Skill，而是既有 Owner 的专业方法不够显式。若新增平行 Planner/Architecture Skill，会增加路由、上下文和职责冲突；若只改 `USAGE.md`，又会让规则停留在示例层，不能稳定约束不同宿主/模型。

## 不修改的后果

Agent 仍可能机械照搬旧方案、按前后端水平切分造成长反馈链、在超大任务中提前编造完整计划，或在 Git 冲突中只按 ours/theirs 选择文本而忽略双方需求意图。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前正式 Owner 为 Router → Coding/Testing/Review/Docs/Figma，用户不希望增加领域词汇治理 | #262、当前 canonical Router/Coding | 不新增顶层 Skill |
| E2 | `05_设计实施与根因调试.md` 已拥有 Planning/Design/Re-plan | 当前 main canonical Source | 架构设计、方案落地、渐进规划进入现有设计 Owner |
| E3 | `09_多人和多智能体并行协作.md` 已拥有依赖/并行/冲突协作 | 当前 main canonical Source | Vertical Slice/DAG 进入现有协作 Owner |
| E4 | `14_Git交付依赖安全与宿主能力边界.md` 已拥有 Git 安全/授权/交付 | 当前 main canonical Source | Merge/Rebase conflict 进入现有 Git Owner |
| E5 | 当前 routing metadata、Stable ID、dependency、Runtime executable/Payload schema 不需要变化 | 本轮影响审计 | 使用 Semantic Local/Content 范围，不触发平行 Contract |

## 推断与待确认

无。修改范围和非目标已由 #262 明确。

# 目标、成功标准与非目标

## 目标

在不扩大顶层 Owner 的前提下，让“怎么设计、怎么拆、怎么逐步把大问题想清楚、怎么把已有方案映射到当前代码、怎么解决 Git 冲突”都成为现有流程中可直接执行的方法，并给普通开发者清晰入口。

## 成功标准

- [ ] Architecture / Codebase Design 方法进入现有设计 Owner，且不制造无关重构。
- [ ] Vertical Slice + blocker DAG / frontier 和 Wide Refactor 例外进入规划/协作 Owner。
- [ ] Large-task Progressive Planning 有明确条件和停止条件。
- [ ] 外部/既有方案按当前事实重新核验后实施，而不是盲信或全部推翻。
- [ ] Merge/Rebase 冲突按双方原始意图解决且不扩大 Git 授权。
- [ ] `USAGE.md` 提供全部关键场景的可复制指令。
- [ ] 路由、Stable ID、Runtime/MCP/Payload/install Contract 保持不变。
- [ ] PR/current-head、Review、main-fresh、Change Archive 和 Requirement Closure 按现有门禁完成。

## 范围

- 三个现有 Coding Reference。
- `USAGE.md`。
- 一个最小规则回归测试。
- 本 Change / Issue / PR 的治理与交付证据。

## 非目标

- 不维护领域词汇、CONTEXT.md 或 Ubiquitous Language。
- 不新增顶层 Skill/Reference、Planner、Task Manager 或 Ticket 系统。
- 不修改 routing metadata、Stable ID、Task Route schema、Runtime executable、MCP、Project Payload 或安装 Contract。
- 不强制所有任务拆 ticket、做架构重构或进入渐进式规划。
- 不改变任何业务 public API、Schema、数据、依赖或部署。

## 必须保持不变

- 项目事实和项目现有术语优先于通用分析词汇。
- 现有 L1/L2/L3、Plan Review Gate、Testing/Review/Docs/Figma Handoff、授权与 Git/CI/PR/Release 门禁强度不降低。
- 普通开发者默认仍止于 PR Ready，除非当前 Requested Outcome 和 Effective Authorization 明确更高交付终点。
- 用户工作保护、Branch Protection/Ruleset 和现有 fresh Evidence 规则保持。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 四项能力全部进入现有 Coding References，USAGE 只做人类入口 | E1-E4 | 不新增 Skill/Reference |
| 接口与契约 | routing/Stable ID/Task Route/Runtime Contract 不变 | E5 | Metadata 与 Runtime grouped N/A |
| 数据与迁移 | 不适用 | 无 Schema/数据变化 | 无 Migration |
| 错误与失败语义 | 方案冲突/大型未知/merge conflict 按既有 Decision/Authorization gate 处理 | #262 | 不发明平行 fail-close 体系 |
| 兼容性 | 现有普通 Planning/Git/协作路径继续有效，新规则条件式增强 | #262 | 无破坏性迁移 |
| 部署与回滚 | 无部署；revert 本 PR 即可回滚 | 纯治理/文档范围 | 无生产恢复 |

# 修改方案与决策依据

## 最小充分方案

1. 在现有设计 Reference 加入：外部/既有方案核验、Architecture/Codebase Design、Large-task Progressive Planning，并把复杂 Feature 拆分明确为 Vertical Slice。
2. 在多人协作 Reference 补 blocker DAG/frontier 与 expand → migrate batches → contract Wide Refactor 例外。
3. 在 Git Reference 补 intent-based Merge/Rebase conflict workflow，继续复用现有授权。
4. 在 `USAGE.md` 增加面向最终用户的讨论/实施/外部方案/切片/大型任务/架构审视/冲突解决提示词。
5. 增加最小规则回归，保护关键方法可达性；不为纯治理文字制造无关产品测试。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1-E4 | 现有 Owner 已正确，只需补方法，避免路由和职责膨胀 |
| D2 | E5 | 本次不改变 metadata/executable Contract，可保持 Semantic Local/Content Evidence |
| D3 | #262 AC6 | canonical 规则与 USAGE 同步，保证模型执行与用户易用同时成立 |
| D4 | #262 非目标 | 领域词汇、Wizard/Planner 等不进入本次范围 |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Architecture / Codebase Design 可执行且不强迫术语/无关重构 | #262 / AC1 | not_satisfied | 实现与 Review 后补证据 |
| R2 | Vertical Slice + blocker DAG/frontier + Wide Refactor 例外 | #262 / AC2 | not_satisfied | 实现与 Review 后补证据 |
| R3 | 条件式 Large-task Progressive Planning | #262 / AC3 | not_satisfied | 实现与 Review 后补证据 |
| R4 | 外部/既有方案先按当前事实核验再实施 | #262 / AC4 | not_satisfied | 实现与 Review 后补证据 |
| R5 | intent-based Merge/Rebase conflict 且不扩大授权 | #262 / AC5 | not_satisfied | 实现与 Review 后补证据 |
| R6 | USAGE 提供全部指定场景的可复制指令 | #262 / AC6 | not_satisfied | 实现与文档复核后补证据 |
| R7 | 不增加 Skill/Reference/路由/Runtime/Payload/install Contract 变化 | #262 / AC7 | not_satisfied | branch diff / Impact Audit |
| R8 | PR final head、Review、main fresh、archive、Closure 完整交付 | #262 / AC8 | not_satisfied | 下游 Delivery/Closure 证据 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `05_设计实施与根因调试.md` | 方案落地、架构设计、大型渐进规划、Vertical Slice | 当前 Planning/Design Owner | R1-R4 / E2 |
| `09_多人和多智能体并行协作.md` | blocker DAG/frontier、Wide Refactor | 当前并行/依赖 Owner | R2 / E3 |
| `14_Git交付依赖安全与宿主能力边界.md` | intent-based conflict workflow | 当前 Git Owner | R5 / E4 |
| `test_development_guidance.py` | 关键规则可达性回归 | 防止后续精简丢失 | R1-R7 |
| `USAGE.md` | 日常可复制使用说明 | 最终用户入口 | R6 |
| 本 Change / #262 / PR | 追溯与交付证据 | Maintenance L2 门禁 | R8 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外：本次为治理方法/文档增强，增加规则可达性回归，不伪造产品 Runtime Red
- [ ] 完成最小实现，不静默扩大范围
- [ ] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | not_applicable | 不改变业务/Runtime 可观察行为 |
| 接口 / 契约 | not_applicable | public API、Task Route、Stable ID、metadata/dependency 不变 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/服务/设备/OS 运行语义变化 |
| 用户 / 工作流验收 | not_applicable | 不新增业务工作流；USAGE 作为治理文档审查 |
| 跨组件关键路径 | not_applicable | 无产品组件接线变化 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方实时事实需要 Probe |
| 构建 / 打包 / 运行 | not_applicable | Runtime executable/package/install 边界不变 |
| 文档 / 治理 / 其他 | required | canonical 内容、USAGE、规则回归、Change/Issue gate、独立 Review、PR/main CI、archive/closure |

# 验证计划

- 目标测试：`test_development_guidance.py` 及 changed-scope selector 选择的治理/内容回归。
- 相关回归：Skill Mutation 内容守恒、Source/Runtime required Context parity（按 CI classifier 实际选择）。
- 静态检查或构建：仅仓库 CI selector 认为当前 content/governance scope 所需的 compile/check；不机械跑三平台 package。
- 专项真实边界：不适用；无外部 Provider/业务数据/运行环境变更。
- 就绪检查：PR Requirement Source + new Change machine Contract + `ready_check` + 独立 Review。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 普通任务过度规划、盲信/推翻外部方案、冲突解决越权 | 条件式触发 + 项目事实优先 + Authorization 不变 + Review |
| 兼容性 | 现有流程保持，新方法按真实场景加载 | 不改 Router/metadata/public Contract |
| 数据 / Migration | 不适用 | 无 Schema/数据 |
| 部署 / 运行 | 不适用 | 无 Runtime/部署 |
| 回滚 / 恢复 | revert Implementation PR | 无不可逆状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：更新唯一最终用户说明 `USAGE.md`；canonical 规则由三个现有 References 承载。
- **依赖 / Runtime**：不适用；不新增/删除/升级依赖，不修改 Runtime executable。
- **配置 / Secret**：不适用；无配置/Secret 变化。
- **部署 / Release**：不适用；不创建 Release/Deploy。
- **兼容 / 消费方通知**：既有提示词继续有效；新增方案/规划/冲突入口，不改变业务 consumer Contract。

# 完成审计

进入 `ready_for_review` 前重新读取 #262、当前 branch 的三个 canonical Owner、`USAGE.md`、实际 diff、测试与 Review Evidence，并从上游独立重建 AC1-AC8。

- [ ] upstream_re_read：重新读取上游正式事实源并独立重建完成定义。
- [ ] change_coverage：确认 R1-R8 覆盖全部 AC，没有让 Change 自证需求。
- [ ] reverse_audit：从用户场景 → USAGE → canonical Owner → 测试/Review/Delivery 反查，并复核 Validation Matrix。
- [ ] unresolved_cleared：R1-R7 满足；R8 的 post-Ready Delivery/Closure 事实按阶段正确处理，无未解释 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main `46a872cb` | canonical Source / Maintenance / affected Owner / Issue #262 回读 | 已完成 | 当前 Owner、范围、Requirement Source 与非目标已确认 |
| V2 | 当前任务分支 | GitHub readback + compare | 待执行 | 实际 diff 与预期范围一致 |
| V3 | 当前任务分支 | 独立 Review + changed-scope GitHub Actions | 待执行 | 需求、内容守恒、回归与机器门禁 |
| V4 | merge 后 main | main fresh CI + repository-native Change archive + Issue Closure Audit | 待执行 | 端到端交付完成 |

## 未验证内容与剩余风险

当前仍处于实现阶段；GitHub Actions、独立 Review、merge/main fresh、Change archive 与 Issue Closure 均未执行，不能宣称完成。

## 交付状态

- 提交：当前任务分支待写入。
- 拉取请求：未创建。
- CI：未运行当前任务 revision。
- 合并：未执行。
- Change 归档：未执行，由 repository-native automation 在 merge 后负责。
- 发布 / 部署：不适用；本次不涉及 Release/Deploy。

## 备注

当前执行环境本地 `git clone` 因 DNS 无法解析 GitHub，开发/交付使用已授权 GitHub App 路径；真实测试执行依赖仓库现有 GitHub Actions，不用代码阅读冒充测试结果。
