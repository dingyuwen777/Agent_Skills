---
schema: coding-change/v1
id: CHG-20260918-163300-architecture-planning-guidance
title: 强化架构设计、任务拆分与方案落地流程
level: L2
status: ready_for_review
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
  - .agents/skills/coding/references/30_方案落地架构设计与渐进式规划.md
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/tests/test_development_guidance.py
  - .agents/skills/coding/tests/test_router_skill_migration.py
  - USAGE.md
  - .agents/changes/active/CHG-20260918-163300-architecture-planning-guidance/CHANGE.md
contracts: []
data_changes: []
---

# 变更摘要

- **要解决的问题**：现有 Agent_Skills 的执行/验证/交付治理已经完整，但方案落地、代码结构设计、复杂任务纵向拆分、大型未知任务渐进规划和 Merge/Rebase 冲突意图恢复仍缺少集中、可执行的方法。
- **拟议修改**：保持现有顶层 Skill/Owner；新增 1 个 Coding 方案专项 Reference，通过既有“方案/技术方案”词汇按需加载，避免普通 L2 上下文膨胀。
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

缺口不是需要更多顶层 Skill，而是既有 Owner 的专业方法不够显式。首轮实现把全部新方法写入普通 L2 必达 Reference，PR #263 Skill Tests #1462 证明这会让 backend L2 上下文达到 200,051B，超过 195,000B 预算，复杂历史组合也超过允许增长。不能通过抬高预算解决，因此改为新增 1 个 Coding 专项 Reference，按现有“方案/技术方案”信号渐进披露。

## 不修改的后果

Agent 仍可能机械照搬旧方案、按前后端水平切分造成长反馈链、在超大任务中提前编造完整计划，或在 Git 冲突中只按 ours/theirs 选择文本而忽略双方需求意图。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前正式 Owner 为 Router → Coding/Testing/Review/Docs/Figma，用户不希望增加领域词汇治理 | #262、当前 canonical Router/Coding | 不新增顶层 Skill |
| E2 | `05_设计实施与根因调试.md` 已拥有 Planning/Design/Re-plan | 当前 main canonical Source | 架构设计、方案落地、渐进规划进入现有设计 Owner |
| E3 | `09_多人和多智能体并行协作.md` 已拥有依赖/并行/冲突协作 | 当前 main canonical Source | Vertical Slice/DAG 进入现有协作 Owner |
| E4 | `14_Git交付依赖安全与宿主能力边界.md` 已拥有 Git 安全/授权/交付 | 当前 main canonical Source | Merge/Rebase conflict 进入现有 Git Owner |
| E5 | 既有 Reference metadata/Stable ID/dependency、Task Route schema/词汇与 Runtime executable/Payload/install Contract 不变；新增方案 Reference 自带新的唯一 Stable ID/trigger | 实际 diff + #1476 selected tests | 需要 routing/parity/context-budget Evidence，但不改变既有 Contract |

## 推断与待确认

无。修改范围和非目标已由 #262 明确。

# 目标、成功标准与非目标

## 目标

在不扩大顶层 Owner 的前提下，让“怎么设计、怎么拆、怎么逐步把大问题想清楚、怎么把已有方案映射到当前代码、怎么解决 Git 冲突”都成为现有流程中可直接执行的方法，并给普通开发者清晰入口。

## 成功标准

- [x] Architecture / Codebase Design 方法进入现有设计 Owner，且不制造无关重构。
- [x] Vertical Slice + blocker DAG / frontier 和 Wide Refactor 例外进入规划/协作 Owner。
- [x] Large-task Progressive Planning 有明确条件和停止条件。
- [x] 外部/既有方案按当前事实重新核验后实施，而不是盲信或全部推翻。
- [x] Merge/Rebase 冲突按双方原始意图解决且不扩大 Git 授权。
- [x] `USAGE.md` 提供全部关键场景的可复制指令。
- [x] 只新增 `coding.reference.31`；既有 Stable ID/dependency、Task Route schema/词汇与 Runtime executable/MCP/Payload/install Contract 保持不变。
- [x] 当前实现、文档与独立 Review 已达到 PR Ready 候选；PR/current-head、main-fresh、Change Archive 和 Requirement Closure 继续由下游交付门禁持有，当前 Change 不伪造未来平台事实。

## 范围

- 1 个新增 Coding 专项 Reference + 2 个现有 Coding References。
- `USAGE.md`。
- 2 个最小规则/路由回归文件。
- 本 Change / Issue / PR 的治理与交付证据。

## 非目标

- 不维护领域词汇、CONTEXT.md 或 Ubiquitous Language。
- 不新增顶层 Skill、Planner、Task Manager 或 Ticket 系统；只新增 1 个 Coding 专项 Reference。
- 不修改任何既有 Reference 的 Stable ID/dependency，不新增 Task Route 维度/词汇；新 Reference 使用新的唯一 Stable ID，并复用现有 `执行模式=方案` / `意图=技术方案`。
- 不修改 Runtime executable、MCP、Project Payload schema 或安装 Contract。
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
| 接口与契约 | 新增 `coding.reference.31`；既有 ID/dependency 与 Task Route/Runtime public Contract 不变 | E5 | routing/parity/context-budget 必须验证；executable/MCP/Payload/install 仍保持 |
| 数据与迁移 | 不适用 | 无 Schema/数据变化 | 无 Migration |
| 错误与失败语义 | 方案冲突/大型未知/merge conflict 按既有 Decision/Authorization gate 处理 | #262 | 不发明平行 fail-close 体系 |
| 兼容性 | 现有普通 Planning/Git/协作路径继续有效，新规则条件式增强 | #262 | 无破坏性迁移 |
| 部署与回滚 | 无部署；revert 本 PR 即可回滚 | 纯治理/文档范围 | 无生产恢复 |

# 修改方案与决策依据

## 最小充分方案

1. 新增 `30_方案落地架构设计与渐进式规划.md`：承载外部/既有方案核验、Architecture/Codebase Design、Large-task Progressive Planning，并只按现有“方案/技术方案”场景加载；现有设计 Reference 只保留薄入口和实施阶段 Vertical Slice 核心。
2. 在多人协作 Reference 补 blocker DAG/frontier 与 expand → migrate batches → contract Wide Refactor 例外。
3. 在 Git Reference 补 intent-based Merge/Rebase conflict workflow，继续复用现有授权。
4. 在 `USAGE.md` 增加面向最终用户的讨论/实施/外部方案/切片/大型任务/架构审视/冲突解决提示词。
5. 增加最小规则回归，保护关键方法可达性；不为纯治理文字制造无关产品测试。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1-E4 | 现有 Owner 已正确，只需补方法，避免路由和职责膨胀 |
| D2 | E5 | 新增 Reference identity/trigger 需要 routing/parity/context-budget Evidence，但无需改 Runtime executable/MCP/Payload schema |
| D3 | #262 AC6 | canonical 规则与 USAGE 同步，保证模型执行与用户易用同时成立 |
| D4 | #262 非目标 | 领域词汇、Wizard/Planner 等不进入本次范围 |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Architecture / Codebase Design 可执行且不强迫术语/无关重构 | #262 / AC1 | satisfied | `30_方案落地架构设计与渐进式规划.md` 覆盖职责集中、接口负担、pass-through、shotgun surgery、真实变化点、Locality/Leverage、design-it-twice，并明确项目术语优先、无关重构禁止 |
| R2 | Vertical Slice + blocker DAG/frontier + Wide Refactor 例外 | #262 / AC2 | satisfied | `30` 定义完整切片方法；`09_多人和多智能体并行协作.md` 保留默认 Vertical Slice、DAG/frontier 与 `expand → migrate batches → contract` 执行硬规则 |
| R3 | 条件式 Large-task Progressive Planning | #262 / AC3 | satisfied | `30` 仅在跨多会话/多阶段且路径不可见时启用 Destination / Decisions So Far / Current Frontier / Blocked / Not Yet Specifiable / Out of Scope，并在路径清晰后退出 |
| R4 | 外部/既有方案先按当前事实核验再实施 | #262 / AC4 | satisfied | `30` 将其他聊天/同事/文档/工具等方案定义为 Proposal，按仍成立/已过时/冲突/需 Owner 决策分类并映射当前实现；`USAGE.md` 提供用户入口 |
| R5 | intent-based Merge/Rebase conflict 且不扩大授权 | #262 / AC5 | satisfied | `14_Git交付依赖安全与宿主能力边界.md` 明确恢复操作状态、双方 Primary Requirement Source/Issue/PR/Change/commit 与 hunk，逐 hunk 合并兼容意图，真实语义冲突回决策门禁，保留安全 abort 与既有 Git 授权；独立 re-review #5246457257 无阻塞 Finding |
| R6 | USAGE 提供全部指定场景的可复制指令 | #262 / AC6 | satisfied | `USAGE.md` 已覆盖方案讨论、确认后实施、外部方案落地、纵向切片、大型任务、架构审视、Merge/Rebase 冲突及短指令 |
| R7 | 只新增 1 个 Coding 专项 Reference；既有 Stable ID/dependency、Task Route schema/词汇与 Runtime executable/MCP/Payload/install Contract 不变；Context Budget 不回归 | #262 / AC7 | satisfied | PR #263 run #1477 在 base `ba127180` / head `634356d0` 上 selected semantic tests 全部成功；覆盖方案路由正/反例、metadata/compiler、历史路由增长、Context Budget、Bundle exact-text 与 Source/Runtime parity |
| R8 | PR final head、Review、main fresh、archive、Closure 完整交付 | #262 / AC8 | not_applicable | pre-Ready 阶段平台交付证据由后续 Delivery 生命周期持有；不在 Change 内伪造未来状态 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `30_方案落地架构设计与渐进式规划.md` | 新增方案专项 Reference，承载方案核验、架构设计和大型渐进规划 | 保护普通 L2 Context Budget，同时保留 Coding Owner | R1/R3/R4 / #262 |
| `09_多人和多智能体并行协作.md` | blocker DAG/frontier、Wide Refactor | 当前并行/依赖 Owner | R2 / E3 |
| `14_Git交付依赖安全与宿主能力边界.md` | intent-based conflict workflow | 当前 Git Owner | R5 / E4 |
| `test_development_guidance.py` | 关键规则可达性回归 | 防止后续精简丢失 | R1-R7 |
| `USAGE.md` | 日常可复制使用说明 | 最终用户入口 | R6 |
| 本 Change / #262 / PR | 追溯与交付证据 | Maintenance L2 门禁 | R8 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外：本次为治理方法/文档增强，增加规则可达性回归，不伪造产品 Runtime Red
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | not_applicable | 不改变业务/Runtime 可观察行为 |
| 接口 / 契约 | required | 新增 Reference Stable ID `coding.reference.31` 与 routing metadata；必须证明只命中方案/技术方案，普通 backend L2 不命中，既有 Stable ID/dependency 与 Task Route schema/词汇不变 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/服务/设备/OS 运行语义变化 |
| 用户 / 工作流验收 | not_applicable | 不新增业务工作流；USAGE 作为治理文档审查 |
| 跨组件关键路径 | not_applicable | 无产品组件接线变化 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方实时事实需要 Probe |
| 构建 / 打包 / 运行 | required | 新增 canonical Reference 改变 Bundle/reference inventory；changed-scope classifier 已要求 Runtime package Evidence。Ready 后必须完成 Linux/Windows/macOS package/self-test/真实 MCP/安装证据；不因 executable 源码未改而手工跳过 |
| 文档 / 治理 / 其他 | required | canonical 内容、USAGE、规则回归、Change/Issue gate、独立 Review、PR/main CI、archive/closure |

# 验证计划

- 目标测试：`test_development_guidance.py` 新增方案 Reference 路由正/反例，以及 changed-scope selector 选择的治理/内容回归。
- 相关回归：metadata compiler/Stable ID/dependency、Context Budget、历史路由增长、Skill Mutation 内容守恒、Source/Runtime required Context parity（按 CI classifier 实际选择）。
- 静态检查或构建：classifier 已把新增 Reference 判定为需要 package Evidence；Ready 后执行仓库正式 Linux/Windows/macOS package gate，不新增临时 Workflow。
- 专项真实边界：不适用；无外部 Provider/业务数据/运行环境变更。
- 就绪检查：PR Requirement Source + new Change machine Contract + `ready_check` + 独立 Review。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 普通任务过度规划、盲信/推翻外部方案、冲突解决越权 | 条件式触发 + 项目事实优先 + Authorization 不变 + Review |
| 兼容性 | 现有流程保持，新专项只在方案场景加载 | 新增 Reference 使用新 Stable ID 和既有 route 词汇；不改 Task Route schema/public contract |
| 数据 / Migration | 不适用 | 无 Schema/数据 |
| 部署 / 运行 | 不适用 | 无 Runtime/部署 |
| 回滚 / 恢复 | revert Implementation PR | 无不可逆状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：更新唯一最终用户说明 `USAGE.md`；canonical 规则由三个现有 References 承载。
- **依赖 / Runtime**：不新增/删除/升级软件依赖，不修改 Runtime executable/MCP/Payload schema；新增 canonical Reference 会进入动态 Bundle/private routing manifest，因此必须通过现有 routing/parity/context-budget 回归。
- **配置 / Secret**：不适用；无配置/Secret 变化。
- **部署 / Release**：不适用；不创建 Release/Deploy。
- **兼容 / 消费方通知**：既有提示词继续有效；新增方案/规划/冲突入口，不改变业务 consumer Contract。

# 完成审计

进入 `ready_for_review` 前重新读取 #262、当前 branch 的三个 canonical Owner、`USAGE.md`、实际 diff、测试与 Review Evidence，并从上游独立重建 AC1-AC8。

- [x] upstream_re_read：已重新读取 live #262、base `ba127180`、current semantic head `634356d0`、Ref09/Ref14/Ref30、`USAGE.md`、实际 PR diff 与 #1477 Evidence，并从上游独立重建 AC1-AC8。
- [x] change_coverage：R1-R7 与 #262 AC1-AC7 一一满足；AC8 的 final PR/package/merge/main-fresh/archive/Closure 属 Ready 后 Delivery，不由 Change 自证。
- [x] reverse_audit：已从方案讨论/外部方案/纵向切片/大型任务/架构审视/Merge-Rebase 冲突用户场景反查 `USAGE.md` → Ref30/Ref09/Ref14 → routing/context-budget/parity tests → Delivery gate；无遗漏的新增顶层 Owner。
- [x] unresolved_cleared：R1-R7 均 satisfied；R8 仅按 pre-Ready 阶段记 `not_applicable`，无 `not_satisfied`；post-Ready Evidence 继续 fail-closed。

# 完成证据与状态

## 新鲜证据

**PR #263 run #1477（current semantic head）**：base `ba127180` / head `634356d0743a5ddddd48a5ac70df546b168a62c8` 的 Requirement Source、changed-scope selector、compile/smoke、selected semantic tests、current Coding Change structural readiness 均成功；selected tests 全部通过。最终 Agent Skills/Runtime Package Gate 仅因 Change 尚未切到 `ready_for_review` 而按设计 fail-closed，Windows/macOS package 未提前运行。

**Independent re-review #5246457257**：以 live #262 从 A1/A2 重建 AC，确认之前 AC5 与 Change 漂移 Finding 已修复，结果 `NO_FINDINGS_WITHIN_SCOPE`。仍未取得的证据仅为 Ready 后 final package CI、guarded merge、main-fresh、repository-native archive 与 Issue Closure。

**Review Finding（current-base）**：以 live #262 + base `ba127180` + head `d8b36a63` 独立重建 AC 后，发现 Ref14 压缩规则未明确保留“恢复 merge/rebase 状态”和“逐 hunk 合并兼容意图”，同时 Change 仍残留“Ref05/routing/Stable ID 全不变”的旧实现描述。当前 commit 只修正这两个证据/规则缺口，不改变方案架构；修复后必须重新取得 current-head semantic CI 再 re-review。

第七轮 PR #263 Skill Tests #1471 仅剩历史“复杂多条件叠加” Context Budget 超 646B；其余 selected tests，包括方案专项路由、metadata/compiler、Bundle exact-text、Source/Runtime parity、Planning/USAGE 回归均通过。当前不抬预算：删除前几轮残留的重复标题，并把 Vertical Slice/DAG 与 Merge/Rebase 冲突硬规则并回各自现有 Owner 段落。

第六轮 PR #263 Skill Tests #1469 已使 backend L2、方案路由、metadata/compiler、Bundle exact-text、Source/Runtime parity、Planning/USAGE 回归全部通过；仅复杂历史组合仍超预算 868B。当前只把 Ref09/Ref14 的重复解释收敛成执行硬规则，并恢复普通 Ref05 原有行为/能力工作分解，不改变四项能力或路由。

第五轮 PR #263 Skill Tests #1467 已将预算回归收敛到 backend L2 +154B、复杂组合 +1.3KB；新增 Reference 路由/metadata/Bundle/parity 继续通过。另有一个既有 Planning Contract 断言要求保留“工作分解”原词。当前删除普通 Ref05 的重复专项导航、压缩 Ref09/Ref14 的重复解释，并恢复原 Planning 关键词；详细方法仍由专项 Reference 与 USAGE 完整承载。

第四轮 PR #263 Skill Tests #1466 将失败继续收敛：新增 Reference 路由/metadata/Bundle/parity 与既有规划契约均通过；只剩 backend L2 +235B、复杂组合 +1.6KB，以及自有冲突规则措辞断言。当前最后去除 Ref09/Ref14 重复解释并恢复 `Primary Requirement Source` / `ours / theirs` 精确语义；仍不提高预算。

第三轮 PR #263 Skill Tests #1464 已证明新增 Reference 的 metadata/compiler、方案路由正反例、Bundle exact-text、Source/Runtime context conformance 等相关回归继续通过；剩余失败是普通 backend L2 仅超预算 477B、复杂历史组合超约 2.4KB，以及两条既有文本可达性断言因压缩改写失配。当前仅进一步去重复并恢复既有关键措辞，不提高预算、不削弱门禁。

第二轮 PR #263 Skill Tests #1463 证明专项 Reference 的显式方案/技术方案正反路由测试通过；剩余失败为 backend L2 仍超预算 743B、复杂历史组合超约 3.8KB，以及历史“方案 + unknown project shape”精确 expected-set 尚未加入新 Reference。当前修正通过进一步压薄普通 Ref05/Ref09/Ref14，并只对该历史方案用例加入 `coding.reference.31` 精确期望；不提高 Context Budget。

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | current base `ba127180` | live #262 + canonical Owner + PR diff readback | 完成 | 最终 Requirement、范围、Owner 与 main 新鲜基线一致 |
| V2 | head `634356d0` | PR #263 Skill Tests #1477 selected semantic phase | 全部成功 | 方案路由、metadata/compiler、历史路由、Context Budget、Bundle exact-text、Source/Runtime parity、USAGE/Planning 回归无失败 |
| V3 | head `634356d0` | Independent Review #5246457257 | `NO_FINDINGS_WITHIN_SCOPE` | AC1–AC7 实现与测试充分性通过独立 A1/A2 复核；AC5 修复已 re-review |
| V4 | Ready 后 Delivery | final required PR CI + 3-platform package + guarded merge + main fresh + repository-native archive + Closure Audit | 尚未执行 | 这些证据必须由真实 Actions/PR/main/archive Owner 取得，不能由 pre-Ready Change 预写 |

## 未验证内容与剩余风险

实现、routing/parity/context-budget 与独立 re-review 已完成；当前进入 `ready_for_review`。剩余风险仅是尚未执行 final required package CI、merge/main-fresh、repository-native archive 与 Issue Closure，在这些真实证据完成前不声明端到端完成。

## 交付状态

- 提交：semantic/review 候选 head 为 `634356d0743a5ddddd48a5ac70df546b168a62c8`；本次仅把已满足的 Change 门禁切到 `ready_for_review` 并固化 fresh Evidence。
- 拉取请求：PR #263 已存在，当前为普通 open PR；Change Ready 前逻辑上仍未就绪。
- CI：#1477 selected semantic phase 全部成功；final Agent Skills/Runtime Package Gate 将由本 Ready commit 的新 head 重新运行，旧 run 不冒充 final Evidence。
- 合并：未执行。
- Change 归档：未执行，由 repository-native automation 在 merge 后负责。
- 发布 / 部署：不适用；本次不涉及 Release/Deploy。

## 备注

当前执行环境本地 `git clone` 因 DNS 无法解析 GitHub，开发/交付使用已授权 GitHub App 路径；真实测试执行依赖仓库现有 GitHub Actions，不用代码阅读冒充测试结果。
