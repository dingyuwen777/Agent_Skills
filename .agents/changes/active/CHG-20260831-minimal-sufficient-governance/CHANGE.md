---
schema: coding-change/v1
id: CHG-20260831-minimal-sufficient-governance
title: 最小充分治理与渐进式 Protected 协作规则
level: L2
status: ready_for_review
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
- 不降低 Agent_Skills 源仓库自身 Maintenance Overlay：本仓库 Skill Mutation 继续按 Maintenance 要求走 Change、TDD、Review、PR、CI 与归档。
- 不直接修改任何目标项目的 Branch Protection/Ruleset。
- 不新增 Runtime 路由维度或硬编码 `protected` 状态；Git 交付时从目标仓库当前平台事实读取。
- 不降低 public Contract、Schema/Migration、安全、权限、数据、部署等 L3 门禁。
- 不为了满足早期施工设想而把同一最小治理规则复制进多人协作、Issue/PR、Git 或 Review Core。

# 必须保持不变

- 当前 Change 仍不是自身 Requirement Source。
- 项目 Overlay 优先，项目已有正式治理时继续复用。
- CI 绿色不能替代需求完整性或 Review。
- `Requirement-Source` 与 `Closes/Fixes/Resolves` 语义分离。
- PR Review 的 base/head revision 绑定、current-base freshness 和 `expected_head_sha` 继续保留。
- GitHub 只是一个平台 profile；非 GitHub 平台使用真实等价机制。
- Source/Runtime 两种模式继续共享 canonical metadata，既有 Stable Reference ID 不漂移。

# 关键决策

不新增“单人项目/多人项目”永久标签，也不增加 `protected=true/false` 的 Runtime route value。原因是这些都不是任务语义：同一仓库可以同时存在 Owner 自己的轻量修改与外部协作者 PR。Agent 只依据当前任务已经确认的跨 Owner 交接事实追加多人协作治理；Git 交付时再独立读取当前平台保护规则。

L2 的治理强度从“必须独立 Change”改为“必须有最小充分任务契约”。任务契约要求目标、范围/非目标、成功标准/验收、关键不变项、风险和验证入口足够清楚，但载体可以是当前会话确认事实、PR body、Issue、Spec/OpenSpec/RFC 或项目既有正式记录。只有需要跨会话/跨 PR/跨 Owner 长期持久化、项目明确要求、复杂依赖/审计或 Completion Gate 时，才升级为独立持久 Change。L3 始终保留持久施工契约。

实现没有把同一原则复制进 ref09/ref18/ref15/Review Core，而是新增 `coding.reference.19` 作为唯一“何时升级”Owner；既有 Change/Issue/Git/Review 继续负责“升级后怎样执行”。Review 只新增 `review.reference.04` 负责深度选择。这样减少规则漂移和上下文重复，符合本需求的减负目标。

完整 Completion Reference 仍对 L2 可达，但它现在明确区分轻量 L2 与持久 gated L2：轻量 L2 只做上游目标/验收/不变项/证据/未验证项核对，不创建形式化表格。保留这一可达性避免破坏现有 Routing Conformance，同时减掉实际流程动作。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 默认治理必须轻量，能力存在不等于每次任务都启用 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | 新增 `coding.reference.19`，正常 Coding 路由自动加载；正文明确 Minimal Sufficient Governance 与“不得为了流程完整性”机械创建 Issue/Change/PR/Review/归档。 |
| R2 | L2 不再固定要求独立 Change，L3 继续严格 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | ref04 改为“最小充分任务契约”，明确 `L2 ≠ always CHANGE.md`；L3 继续要求持久施工契约、Migration/回滚；ref10 保留完整 L3/持久 gated 门禁。 |
| R3 | 当前任务而非仓库历史决定多人协作，unknown 不升级 shared | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | `coding.reference.19` 明确当前跨 Owner 交接才构成 shared，Protected/contributors/CODEOWNERS/历史 PR 不能单独证明，`unknown != shared`；发现事实后再追加现有多人协作路由。 |
| R4 | Issue 只在真实持久追溯价值时创建，L2/PR/protected 不能单独触发 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | `coding.reference.19` 的 Issue Necessity Gate 明确三个非触发条件与跨 Owner/多个 PR/跨会话/长期审计/用户或项目规则等升级条件；需要后再进入既有 Issue/PR Owner。 |
| R5 | Protected Branch 与后续 Ruleset 设置独立管理并渐进升级 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | `coding.reference.19` 区分未保护/受保护，只影响 Git 交付；写入 PR + required checks + force-push/deletion + conversation resolution 基线，以及 loose→strict→Merge Queue、PR-only bypass/actor 身份边界。已对照 GitHub 当前官方 Rulesets/Merge Queue 文档。 |
| R6 | Review 按风险选择最小充分深度 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | satisfied | 新增 `review.reference.04`，定义 Quick/Standard/Deep 和升级规则；Review 路由真实命中该 Reference，原 Review Findings/测试方法不复制。 |
| R7 | Runtime/Stable ID/高风险门禁不回归 | AGENTS.md | satisfied | 未修改 Runtime evaluator/MCP/Bundle/Project Payload；新增 Coding Stable ID `coding.reference.19`，既有 ID 不改；run `33347134128` compile、CLI smoke、全部 self-contained tests 成功。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 初始 Red run `33346388713` 由新治理回归按预期失败；实现后 run `33347134128` 的全部 self-contained tests 成功。 |
| 接口 / 契约 | required | 新 Stable ID 由 numbering 回归锁住；真实 Runtime evaluator 验证正常 Coding 命中 `coding.reference.19`、Review 命中 `review.reference.04`、L3 继续命中完整 Completion Reference。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改运行时服务、数据库或业务数据。 |
| 用户 / 工作流验收 | required | 反向核对 solo/unprotected、solo/protected、external/shared handoff、multi-PR/长期追溯、普通 L2 与 L3：四个治理维度互不错误连锁，发现新事实后再升级。 |
| 跨组件关键路径 | required | Risk × Git protection × collaboration handoff × traceability value 组合由 `coding.reference.19` 统一选择；既有执行 Owner 继续承接升级后的 Change/Issue/Git/Review。 |
| 外部依赖 / 供应方探测 | required | 2026-08-31 对照 GitHub 官方 `Available rules for rulesets`、`Creating rulesets`、`Managing a merge queue`：确认 strict/loose required checks、PR-only bypass、Merge Queue 与 `merge_group` CI 边界。 |
| 构建 / 打包 / 运行 | not_applicable | 纯 Skill/Reference 变化，不修改 Runtime/Builder/MCP/Installer/Release；按 Maintenance 不触发三平台 Runtime Package Tests。 |
| 文档 / 治理 / 其他 | required | Router、ref04/ref10、新 governance Owner、新 Review depth Owner、Change 与回归语义一致；Issue #90 已按最终 Owner 决策同步。 |

# 完成审计

- [x] upstream_re_read：重新读取 Issue #90，并按本轮用户最终确认的“默认轻、按事实升级、Protected 独立”目标核对；Issue 已同步最终 Owner 设计，不把早期施工方案当需求本身。
- [x] change_coverage：R1–R7 均有唯一 Owner 和证据；Issue Forms、existing Git/Issue/Review execution rules 保留，不重复复制。
- [x] reverse_audit：从 `solo+unprotected`、`solo+protected`、external PR、multi-PR/跨会话、L3 反向检查，分别只触发真实需要的 Git/协作/追溯/深度审查；L3 仍完整。
- [x] unresolved_cleared：A1/A2 与内容守恒 Review 未发现 BLOCKER/HIGH；测试 API 错误和旧 Conformance 语义冲突已通过保留 ref10 可达性、验证轻量语义的方式修正；R1–R7 全部 satisfied。

# 任务

- [x] 读取基线 main 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、Change、Completion、Collaboration、Issue/PR、Git 与 Review 规则。
- [x] 确认基线 main `182a79dd9e870033b0d0e1487ab7fbf819cdca36` 未开启 branch protection，且 Skill Tests run `33344829021` success。
- [x] 搜索无等价 Issue 后创建 Requirement Source Issue #90，并创建 PR #91。
- [x] 新增失败回归并取得 Red：run `33346388713`。
- [x] 实现单一最小治理 Owner、轻量 L2 Change/Completion 语义、Router 示例与 Review depth；不修改 Runtime evaluator。
- [x] 修正测试调用与旧 Conformance 取舍；run `33347134128` compile/CLI/self-contained tests 全成功，workflow 只被本 Change 当时仍为 in_progress 的 changed Change gate 正确阻塞。
- [x] 完成 A1/A2、内容守恒 Review、GitHub 官方平台事实复核并更新 Issue #90/本 Change。
- [ ] 本 Ready head 跑完整 Skill Tests / changed Change gate 并取得 success。
- [ ] 检查最新 main/base drift，完成 exact base/head Review，正常合并 PR #91，验证 Issue #90 自动关闭与 main fresh CI。
- [ ] 将本 Change 更新为 `done` 并通过独立归档 PR 移入 `archive/2026-08/`，验证归档后 main fresh CI。

# 验证

## 新鲜证据

- baseline main：`182a79dd9e870033b0d0e1487ab7fbf819cdca36`；Skill Tests `33344829021` success。
- Red：PR #91 run `33346388713`；新治理回归在旧规则下失败，compile/CLI 保持成功。
- 中间 Green 调试：run `33346907225`；大部分新语义已通过，暴露两类测试基线问题：新测试误用 `build_bundle` key、旧 Conformance 仍固定要求普通 L2 的旧 Completion 语义。
- Green：run `33347134128`；compile、CLI smoke、全部 self-contained tests success；唯一 workflow failure 是 changed Change gate 看到本 Change 仍为 `in_progress/not_satisfied`。
- GitHub 官方事实：Rulesets 支持 PR、required checks、force-push 限制、bypass；required checks 区分 loose/strict；PR-only bypass 可要求 actor 仍通过 PR；Merge Queue 面向高流量 protected branch，并要求 GitHub Actions 配置 `merge_group` 事件。

# 文档影响

属于通用 Agent/研发治理规则修改；不增加最终用户手册章节。普通用户仍只用自然语言描述开发或 Review 任务，内部根据当前事实选择最小充分流程。

# Git / PR 状态

- branch: `change/minimal-sufficient-governance`
- baseline main: `182a79dd9e870033b0d0e1487ab7fbf819cdca36`
- Requirement Source: #90
- implementation PR: #91，open
- current head before Ready evidence: `e9147fd9d70aef1d24497b0eec8536a0b71c44a7`
- merge: 未执行
- main fresh CI: 未执行
- archive: 未执行
