---
schema: coding-change/v1
id: CHG-20260831-project-facing-managed-bootstrap
title: 将 Runtime managed block 收敛为项目侧行为契约
level: L3
status: done
owner: dingyuwen777
branch: change/managed-block-project-facing-contract
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - project-bootstrap
  - runtime-disclosure
  - project-governance
  - tests
affected_paths:
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/assets/AGENTS.template.md
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/tests/
contracts:
  - project-managed-bootstrap
  - runtime-user-visible-disclosure
data_changes: []
---

# 目标

把安装到目标项目根 `AGENTS.md` 的 Agent_Skills managed block 从内部治理控制面说明，收敛为短、稳定的项目侧行为契约：任何通用治理执行方式都必须先读取并遵守目标项目规则和真实事实；更高优先级 Agent_Skills 模式只允许改变通用治理约束的取得和呈现方式，不能跳过、替代或降低项目 `AGENTS.md` / `CONTRIBUTING`、Contract、Schema/Migration、CI、正式设计、部署和验收边界。详细 Runtime 披露规则继续由内部唯一 Owner 承担。

# 成功标准

- [x] managed block 不再逐条枚举内部能力发现、选择、路由、上下文加载、内部文件/标识或 Agent 可见通道名称。
- [x] 项目规则与当前真实项目事实始终先于 Agent_Skills 模式覆盖读取。
- [x] 更高优先级模式覆盖只改变通用治理约束的取得/呈现方式，不使项目规则失效。
- [x] Runtime 详细披露约束仍由 shared Entry、canonical Runtime Reference 和 Runtime 公共进度规则承担。
- [x] Project Governance Bootstrap 只在 managed block 外用项目自身术语维护项目 Overlay。
- [x] Project Payload、MCP Tool Contract、Task Route、Routing Manifest、Bundle、Stable ID、安装 ownership 和 exact-text Context 语义未改变。
- [x] Red/Green、Deep Review、PR fresh CI、merge 和 main fresh CI 均取得新鲜证据。

# 范围与非目标

实施范围：

- 重写 `AGENTS.managed.md` 为项目侧行为契约；
- 在 `AGENTS.template.md` 增加项目化 Overlay 表达规则；
- 调整 Bootstrap canonical Reference 的 managed block Ownership；
- 新增并迁移 disclosure/bootstrap/Project Payload/Installer/内容守恒回归。

非目标：

- 不修改 `runtime.py`、MCP server、Builder、Workflow 或 Release 产品面；
- 不修改 AIMA_UGC 当前已安装副本；
- 不创建 Runtime Release/tag；
- 不把 Runtime 加密或 managed block 描述为机器 Owner 的安全隔离。

# 必须保持不变

- 无论 Source Mode、Runtime Mode 或其他明确模式，目标项目当前路径适用的项目规则始终先读并继续生效；
- 当前代码、Manifest/lock、Contract、Schema/Migration、测试、CI、正式文档和设计事实优先于通用示例；
- Runtime required Context 继续逐字来自 canonical Bundle 并保持 fail-closed；
- Source Mode 维护者继续可查看 canonical Skill/Reference/Router/路径和路由事实；
- Runtime 用户继续可见项目调查、需求/风险、代码、测试、文档、Review、Git/CI/Release 和交付状态；
- installer 只维护 managed marker 内文本，marker 外项目 Overlay 继续受保护。

# 关键决策

采用“managed block 只保留外部行为契约，详细内部规则留在 Runtime/Entry/canonical Runtime Owner，项目大模型只维护 block 外 Overlay”的方案。拒绝仅润色原内部清单，也拒绝让项目大模型自由修改 installer 认领的 managed block。

这是 L3 Bootstrap/披露契约调整，但不改 MCP/Bundle/Project Payload schema。未来 Runtime Release/升级只替换 installer 认领的 managed block；回滚到旧 commit/Release 即恢复旧文本，不涉及业务数据或 Schema 回滚。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | managed block 不应通过“禁止泄露”反向详细暴露内部治理实现 | user:managed-block-project-facing | satisfied | `AGENTS.managed.md` 已变为项目侧行为契约；新旧 disclosure 回归反向禁止 Runtime/Source/MCP/内部路由/required Context 清单回到根入口。 |
| R2 | 项目宿主大模型可以把治理结果写成项目自己的自然规范，但 managed block 仍由 installer 确定性维护 | user:managed-block-project-facing | satisfied | `AGENTS.template.md` 与 ref12 要求 marker 外 Overlay 使用项目自身模块/Contract/Schema/测试/CI/部署/业务/设计术语；marker ownership 回归通过。 |
| R3 | 更高优先级模式只能改变通用治理约束取得/呈现方式，不能跳过目标项目规则 | user:project-rules-always-read | satisfied | managed 第 1 条先读项目规则，第 2 条才允许模式覆盖；测试验证顺序及 Contract/Schema/Migration/CI/正式设计/部署/验收边界。 |
| R4 | Runtime 详细静默控制面约束继续有效，真实工程过程继续可见 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | ref13、Entry 与 `runtime.py` 未修改；Runtime 公共进度规则和 MCP disclosure 回归通过。 |
| R5 | managed block 只做 Bootstrap，不重新生长成第二套 Router/Runtime 实现说明 | .agents/MAINTENANCE.md | satisfied | ref12 明确详细 Runtime disclosure 不由 managed 承担，并禁止把内部控制面清单复制回目标项目根 `AGENTS.md`。 |

# 验证矩阵

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red：Skill Tests #751 在旧实现上按预期失败。Green：#766 self-contained 285/285 通过；PR #126 fresh Skill Tests #768 全绿。 |
| 接口 / Contract | required | managed bootstrap 外部行为契约迁移；MCP/Task Route/Bundle/Project Payload schema 与 Runtime Python 未改，既有 contract/routing/bundle/projection tests 通过。 |
| 集成 / Persistence / Runtime Dependency | required | canonical Bundle + Project Payload + Installer 构造真实临时项目并核对根 `AGENTS.md`、marker ownership、Entry/Router 与 no-Reference/sidecarless 边界。 |
| 用户 / Workflow Acceptance | required | 安装后的项目入口只表达项目规则先读、模式覆盖不跳过项目规则、工程过程可见，并反向禁止内部控制面清单。 |
| 跨组件 Golden Path | required | managed/template → Project Payload → Installer → target `AGENTS.md`；Entry/ref13/runtime progress rule 继续承担详细内部披露链。 |
| 外部依赖 / Provider Probe | not_applicable | 不依赖第三方服务、生产系统或实时外部数据。 |
| Build / Package / Runtime | not_applicable | 未修改 `runtime/**`、Builder、MCP smoke 或 package/release workflow；按仓库 path-scoped 门禁无需三平台 onefile。 |
| Docs / Governance / Other | required | ref12、managed、template、Change、live navigation、context budget、Routing Conformance 和 Ready gate 均由 Skill Tests 覆盖；没有提高 context budget 阈值。 |

# TDD / 验证证据

- Red：Skill Tests #751，run `33397855286`，head `26d244d077c325e690f018f4c7105790201c5401`；compile/CLI smoke 成功，新项目侧契约在旧 managed 上使 self-contained suite 正确失败。
- 中间 Green：Skill Tests #758，run `33398436673`；发现 8 个旧根入口字面契约和 3 个 context budget 回归。通过迁移旧断言与压缩 ref12 重复说明修复，没有恢复旧内部术语、没有提高预算阈值。
- Implementation Green：Skill Tests #766，run `33399612646`，head `40770fb62700910f25874b7c20e21dfacf6888d9`；`Ran 285 tests in 4.621s`，`OK`；唯一失败是 Change 当时仍为 `in_progress` 的预期 Ready gate。
- Final-head Ready Green：Skill Tests #767，run `33400049273`，head `b0d7371faea6a292b155625021f0f74df8ea5545`，完整成功。
- 新普通 PR Fresh Green：PR #126 Skill Tests #768，run `33400179361`，head `b0d7371faea6a292b155625021f0f74df8ea5545`，compile、CLI smoke、self-contained tests、changed Change Ready gate 全部成功。
- main Fresh Green：merge commit `124bc874c8d3396b7a5ffa4901fa384344389b37` 的 Skill Tests #769，run `33400253721`，compile、CLI smoke、self-contained tests、active Coding Change gate 全部成功。

# Review

L3 Deep Review 重新读取本轮用户要求、根 `AGENTS.md`、Maintenance、Entry、Router、Coding、ref12/ref13、Runtime progress rule、Review Skill/References，并检查实际 diff、Project Payload/Installer 路径和 CI。

重点反查：高优先级模式是否仍可能跳过项目规则；managed 变薄后详细 Runtime disclosure 是否不可达；项目大模型是否会把治理实现复制进 Overlay；是否破坏 ownership/Source Mode/exact-text Context；是否通过恢复旧词汇或放宽 context budget 取巧；是否误改 Runtime/Release 产品面。

结论：`NO_FINDINGS_WITHIN_SCOPE`，无 BLOCKER/HIGH/MEDIUM。详细内部披露仍由未修改的 Entry/ref13/runtime progress rule 承担；旧测试迁移为新契约反向保护；ref12 通过去重恢复历史 context budget；changed scope 不要求 Runtime Package Tests。

# 完成审计

- [x] upstream_re_read：完成前重新读取用户要求、根规则、Maintenance、Entry/Router、Coding、ref12/ref13、Runtime progress rule、Review 规则和真实 PR/CI 状态。
- [x] change_coverage：项目规则永远先读、managed 外部契约、内部 Owner 守恒、项目化 Overlay、不提高 context budget 均进入实现和测试。
- [x] reverse_audit：从真实 target `AGENTS.md` 反查 template/managed/Project Payload/Installer，再从 Runtime 用户可见输出反查 Entry/ref13/runtime progress rule；未发现缺口或第二 Owner。
- [x] unresolved_cleared：R1–R5 全部 satisfied，所有 not_applicable 有 changed-scope 依据。

# Git / PR / CI / 交付

- 功能分支：`change/managed-block-project-facing-contract`，从 `main@5789add905917ef28584cade3cf9f5ed9e648bd2` 创建；合并前 `behind_by=0`。
- Draft PR #125：final-head Skill Tests #767 成功；Draft → Ready mutation 返回 `Repository.fullDatabaseId` GraphQL 查询错误，重读后真实状态仍 `draft=true`，因此按零人工 PR 策略关闭，没有人工点击或重复重试。
- 普通 PR #126：使用同一 head/base 创建，`draft=false`；fresh Skill Tests #768 成功；合并前重新确认 `mergeable=true`、`behind_by=0`、head `b0d7371faea6a292b155625021f0f74df8ea5545`。
- Merge：REST merge 携带 `expected_head_sha=b0d7371faea6a292b155625021f0f74df8ea5545`，成功得到 main merge commit `124bc874c8d3396b7a5ffa4901fa384344389b37`。
- Main fresh CI：Skill Tests #769（run `33400253721`）完整成功。
- Release：未创建 tag 或正式 Release；新 managed block 将在未来正式 Runtime Release/升级时进入目标项目。

# 文档影响

- ref12 已同步为项目侧 managed contract 与项目化 Overlay 规则。
- ref13 重新读取并由回归验证继续承担详细 Runtime disclosure Owner，无需修改。
- `USAGE.md` 的下载、安装、升级、回退和日常使用步骤未变化，因此没有无关文档差异。
