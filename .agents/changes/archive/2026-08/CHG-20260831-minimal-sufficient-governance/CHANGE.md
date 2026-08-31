---
schema: coding-change/v1
id: CHG-20260831-minimal-sufficient-governance
title: 最小充分治理与渐进式 Protected 协作规则
level: L2
status: done
owner: dingyuwen777
branch: change/minimal-sufficient-governance
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - review-skill
  - routing
  - change-governance
  - collaboration-governance
  - issue-pr-traceability
  - git-delivery
  - tests
affected_paths:
  - .agents/skills/ROUTER.md
  - .agents/skills/coding/references/04_轻量变更管理.md
  - .agents/skills/coding/references/10_完成定义追溯门禁.md
  - .agents/skills/coding/references/18_最小充分治理与升级门禁.md
  - .agents/skills/review/references/04_审查深度选择.md
  - .agents/skills/coding/tests/test_minimal_sufficient_governance.py
  - .agents/skills/coding/tests/test_reference_numbering.py
contracts: []
data_changes: []
---

# 目标

把 Agent Skills 的默认研发治理收敛为“最小充分治理”：Issue、Change、PR、Review、Branch Protection/Ruleset 等能力继续完整存在，但任何单一信号都不能机械触发整套重流程。技术风险决定验证深度，Branch Protection 决定 Git 交付方式，当前跨 Owner 交接决定协作治理，真实持久追溯价值决定 Issue/独立 Change；这些维度彼此独立并按事实逐级升级。

# 成功标准

- [x] Coding 的正常研发路由自动加载最小充分治理升级门禁；能力存在不等于本次任务必须启用，不为了流程完整性机械创建 Issue、Change、PR、Review 阶段或归档记录。
- [x] L2 默认只要求最小充分任务契约，不再固定要求独立 `CHANGE.md`；已有用户确认事实、Issue/Spec/OpenSpec/RFC/PR body/项目载体均可承载，只有持久治理价值或项目规则要求时才升级独立 Change。
- [x] L3 继续要求稳定 Requirement Source、持久施工契约、兼容/Migration/回滚和 Deep Review，不因减负而降级。
- [x] Completion/Traceability 对轻量 L2 采用最小完成核对，不机械生成 Traceability 表或 Completion Audit 文件；持久 gated L2/L3 继续执行完整门禁。
- [x] 多人协作按当前任务的跨 Owner/开发者/Agent/PR 交接判断；Protected Branch、contributors、CODEOWNERS、历史 PR 不能单独证明当前任务 shared，`unknown != shared`。
- [x] Issue 具备 Necessity Gate；L2、PR、Protected Branch 均不能单独触发 Issue，只有跨 Owner、多个 PR、跨会话长期开发、独立审核/审计、项目规则/用户明确要求或缺少其他稳定 Requirement Source 且确有持久价值时才创建/复用。
- [x] Git 交付前读取真实 Branch Protection/Ruleset；未保护与受保护仓库走不同 Git 路径，但保护状态不反向触发 Issue/多人/Change/Deep Review。
- [x] GitHub protected profile 采用渐进式建议：轻量 PR/check 基线 → 并发提高再 strict up-to-date → 高流量且平台支持再 Merge Queue；bypass 只给已确认 actor，优先 `For pull requests only`。
- [x] Review 通过独立深度选择 Owner 支持 Quick / Standard / Deep，小 PR 不机械执行 L3 全审查。
- [x] Router 的普通 L2 Feature 示例不再预设存在活动 Change/Completion Gate；只有真实治理事实出现时再追加。
- [x] 不修改 Runtime evaluator、MCP、Bundle、Project Payload schema 或既有 Stable Reference ID。

# 范围

- 新增单一 canonical “最小充分治理与升级门禁”，只负责判断何时升级，不复制 Change/Issue/Git/Review 的执行细节。
- 调整现有轻量 Change 与完成定义规则，使普通 L2 保留语义核对但不固定生成持久 Change/表格。
- 新增 Review 深度选择 Owner，只决定 Quick/Standard/Deep，不复制 Findings 或测试方法。
- 调整 Router L2 示例，避免示例本身把普通开发路由回重流程。
- 新增 self-contained preservation/routing 回归，锁住最小充分治理与高风险不降级。

# 非目标

- 不删除现有三类 GitHub Issue Forms；它们继续作为“需要 Issue 时”的高质量工具箱。
- 不降低 Agent_Skills 源仓库自身 Maintenance Overlay：本仓库 Skill Mutation 仍按 Maintenance 要求完成 Change、TDD、Review、PR、CI 与独立归档。
- 不直接修改任何目标项目的 Branch Protection/Ruleset。
- 不新增 Runtime 路由维度或硬编码 `protected` 状态；Git 交付时从目标仓库当前平台事实读取。
- 不降低 public Contract、Schema/Migration、安全、权限、数据、部署等 L3 门禁。
- 不把同一最小治理原则复制进多人协作、Issue/PR、Git 或 Review Core。

# 必须保持不变

- 当前 Change 仍不是自身 Requirement Source。
- 项目 Overlay 优先，项目已有正式治理时继续复用。
- CI 绿色不能替代需求完整性或 Review。
- `Requirement-Source` 与 `Closes/Fixes/Resolves` 语义分离。
- PR Review 的 base/head revision 绑定、current-base freshness 和 `expected_head_sha` 继续保留。
- GitHub 只是一个平台 profile；非 GitHub 平台使用真实等价机制。
- Source/Runtime 两种模式继续共享 canonical metadata，既有 Stable Reference ID 不漂移。

# 关键决策

不新增“单人项目/多人项目”永久标签，也不增加 `protected=true/false` 的 Runtime route value。同一仓库可以同时存在 Owner 自己的轻量修改与外部协作者 PR；Agent 只依据当前任务真实跨 Owner 交接追加多人协作治理，Git 交付时再独立读取当前平台保护规则。

L2 从“必须独立 Change”改为“必须有最小充分任务契约”。任务契约要求目标、范围/非目标、成功标准/验收、关键不变项、风险和验证入口足够清楚，但载体可以是当前会话确认事实、PR body、Issue、Spec/OpenSpec/RFC 或项目既有正式记录。只有跨会话/跨 PR/跨 Owner 长期持久化、项目明确要求、复杂依赖/审计或 Completion Gate 等真实价值时才升级为独立持久 Change。L3 始终保留持久施工契约。

实现使用 `coding.reference.19` 作为唯一“何时升级”Owner；既有 Change/Issue/Git/Review 继续负责“升级后怎样执行”。`review.reference.04` 只负责 Quick/Standard/Deep 深度选择。完整 Completion Reference 仍对 L2 可达，但轻量 L2 只做目标/验收/不变项/证据/未验证项核对，不创建形式化表格。

GitHub Protected Profile 使用当前官方术语：初始小团队可开启 Require PR、required status checks、conversation resolution、Block force pushes、Restrict deletions；需要 Owner/受控 Agent 自己创建并合并 PR 时，`Required approvals=0` 与 loose up-to-date 可作为轻量起点。独立审批价值、并发和队列压力升高后，再逐级提高 approvals、启用 strict up-to-date、最后考虑 Merge Queue。`Restrict updates` 与 bypass 必须先验证真实 actor 权限模型。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 默认治理必须轻量，能力存在不等于每次任务都启用 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | `coding.reference.19` 自动参与正常 Coding 路由并定义 Minimal Sufficient Governance。 |
| R2 | L2 不再固定要求独立 Change，L3 继续严格 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | ref04 定义最小充分任务契约与 `L2 ≠ always CHANGE.md`；ref10 区分轻量 L2 和持久 gated 单元；L3 Migration/回滚/完整门禁保留。 |
| R3 | 当前任务而非仓库历史决定多人协作，unknown 不升级 shared | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | governance Owner 明确跨 Owner 交接才构成 shared，Protected/contributors/CODEOWNERS/历史 PR 不能单独证明，`unknown != shared`。 |
| R4 | Issue 只在真实持久追溯价值时创建，L2/PR/protected 不能单独触发 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | Issue Necessity Gate 锁住三个非触发条件与跨 Owner/多个 PR/跨会话/长期审计/用户或项目规则等升级条件。 |
| R5 | Protected Branch 与后续 Ruleset 设置独立管理并渐进升级 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | governance Owner 区分未保护/受保护并给出初始 Profile、loose→strict→Merge Queue、Required approvals 和 actor/bypass 边界；术语已对照 GitHub 官方文档。 |
| R6 | Review 按风险选择最小充分深度 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | `review.reference.04` 定义 Quick/Standard/Deep，正式 Review 路由可达且不复制 Findings/测试方法。 |
| R7 | Runtime/Stable ID/高风险门禁不回归 | AGENTS.md | satisfied | 未修改 Runtime evaluator/MCP/Bundle/Project Payload；既有 Stable ID 不变；final PR 和 merge 后 main Skill Tests 均成功。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red run `33346388713`；Green run `33347134128`；Ready run `33347279095`；最终 exact-head run `33347416514` 全绿。 |
| 接口 / 契约 | required | numbering 回归锁住新 `coding.reference.19` 和既有 Stable ID；真实 Runtime evaluator 验证 Coding/Review/L3 路由可达。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改运行时服务、数据库或业务数据。 |
| 用户 / 工作流验收 | required | 反向核对 solo/unprotected、solo/protected、external/shared handoff、multi-PR/长期追溯、普通 L2 与 L3，四个维度不会错误连锁。 |
| 跨组件关键路径 | required | Risk × Git protection × collaboration handoff × traceability value 由单一 governance Owner 决定升级，既有 Owner 承接执行。 |
| 外部依赖 / 供应方探测 | required | 2026-08-31 对照 GitHub 官方 Rulesets / Merge Queue 文档确认 Require PR、Restrict deletions、Block force pushes、loose/strict required checks、PR-only bypass 与 `merge_group` 边界。 |
| 构建 / 打包 / 运行 | not_applicable | 纯 Skill/Reference 变化，未修改 Runtime/Builder/MCP/Installer/Release，不触发三平台 Runtime Package Tests。 |
| 文档 / 治理 / 其他 | required | Router、ref04/ref10、governance Owner、Review depth Owner、Issue #90、Change 与回归语义一致。 |

# 完成审计

- [x] upstream_re_read：最终重新读取 Issue #90 和本轮用户确认的“默认轻、按事实升级、Protected 独立”目标，Issue 已同步最终 Owner 设计。
- [x] change_coverage：R1–R7 均有唯一 Owner 和证据；Issue Forms、既有 Git/Issue/Review execution rules 保留，不重复复制。
- [x] reverse_audit：从 `solo+unprotected`、`solo+protected`、external PR、multi-PR/跨会话、L3 反向检查，分别只触发真实需要的 Git/协作/追溯/审查深度；L3 不降级。
- [x] unresolved_cleared：A1/A2、内容守恒与 exact-head Review 未发现 BLOCKER/HIGH/MEDIUM 未解决项；GitHub 术语和初始 Protected Profile 已在最终 Review 前修正。

# 任务

- [x] 读取基线 main 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、Change、Completion、Collaboration、Issue/PR、Git 与 Review 规则。
- [x] 基线 main `182a79dd9e870033b0d0e1487ab7fbf819cdca36`，Skill Tests `33344829021` success。
- [x] 创建 Requirement Source Issue #90 和实现 PR #91。
- [x] Red run `33346388713`。
- [x] 实现单一治理升级 Owner、轻量 L2 Change/Completion 语义、Router 示例与 Review depth，不修改 Runtime evaluator。
- [x] Green run `33347134128`；Ready run `33347279095`；final exact-head run `33347416514`。
- [x] Deep Review `5062484263` 锚定 base `182a79dd9e870033b0d0e1487ab7fbf819cdca36` / head `3ca27a1e318a2425f45e007df540d80aa24ed1fc`，无 BLOCKER/HIGH/MEDIUM Finding。
- [x] PR #91 使用 `expected_head_sha=3ca27a1e318a2425f45e007df540d80aa24ed1fc` 合并，merge commit `7811dc6e4331593590879a8bb8dda8aaf885720f`。
- [x] Issue #90 由 `Closes #90` 自动关闭为 completed；merge 后 main Skill Tests run `33347550196` success。
- [x] 创建独立归档分支，准备 active→archive 移动。
- [ ] 归档 PR fresh CI / exact-head Review / merge，并验证归档后 main fresh CI。

# 验证

## 新鲜证据

- baseline main：`182a79dd9e870033b0d0e1487ab7fbf819cdca36`；Skill Tests `33344829021` success。
- Red：PR #91 run `33346388713`；新治理回归在旧规则下失败，compile/CLI 保持成功。
- 中间调试：run `33346907225` 暴露测试 API/旧 Conformance 取舍问题，未通过恢复重流程解决。
- Green：run `33347134128`；compile、CLI smoke、self-contained tests success，仅当时 `in_progress` Change gate 阻塞。
- Ready：run `33347279095` success。
- final exact head：`3ca27a1e318a2425f45e007df540d80aa24ed1fc`；Skill Tests run `33347416514` success。
- final Review：`5062484263`，reviewed/current base `182a79dd9e870033b0d0e1487ab7fbf819cdca36`，reviewed head `3ca27a1e318a2425f45e007df540d80aa24ed1fc`，无未解决中高风险 Finding。
- implementation merge：PR #91 → `7811dc6e4331593590879a8bb8dda8aaf885720f`。
- Requirement Source：Issue #90 = `closed/completed`。
- implementation main fresh CI：Skill Tests `33347550196` = success。

# 文档影响

属于通用 Agent/研发治理规则修改；不增加最终用户手册章节。普通用户继续只用自然语言描述开发或 Review 任务，内部按当前事实选择最小充分流程。

# Git / PR 状态

- feature branch: `change/minimal-sufficient-governance`
- Requirement Source: https://github.com/dingyuwen777/Agent_Skills/issues/90，closed/completed
- implementation PR: #91，merged
- implementation reviewed base: `182a79dd9e870033b0d0e1487ab7fbf819cdca36`
- implementation reviewed head: `3ca27a1e318a2425f45e007df540d80aa24ed1fc`
- implementation review: `5062484263`
- implementation merge: `7811dc6e4331593590879a8bb8dda8aaf885720f`
- implementation main fresh CI: `33347550196`，success
- archive branch: `archive/minimal-sufficient-governance`
- archive PR: 待创建
- final archive merge/main fresh CI: 待执行
