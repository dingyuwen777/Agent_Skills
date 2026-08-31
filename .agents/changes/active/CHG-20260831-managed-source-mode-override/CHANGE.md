---
schema: coding-change/v1
id: CHG-20260831-managed-source-mode-override
title: Runtime managed block 支持高优先级 Source Mode 覆盖
level: L3
status: ready_for_review
owner: dingyuwen777
branch: change/managed-source-mode-override
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - project-bootstrap
  - runtime-distribution
  - information-disclosure
  - governance
  - tests
affected_paths:
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/tests/test_project_governance_bootstrap.py
  - .agents/skills/coding/tests/test_runtime_disclosure_boundary.py
contracts:
  - agent-skills-managed-mode-override
  - project-bootstrap
data_changes: []
---

# 目标

让正式 Runtime 安装到目标项目的 `AGENTS.md` managed block 保持 **Runtime Mode 默认行为**，同时明确服从系统、开发者或用户级更高优先级指令中已经明确选择的其他 Agent_Skills 执行模式（当前主要场景为维护者 Source Mode）。

当更高优先级指令明确选择 Source Mode 时，只停止执行与该模式冲突的本地 Runtime/MCP 规则取得路径和 Runtime 用户可见披露限制；目标项目自己的 Overlay、项目事实、Contract、Schema、CI、部署、验收和 managed block 中不冲突的项目治理边界继续有效。

# 成功标准

- [x] 没有更高优先级 Agent_Skills 模式覆盖时，managed block 仍默认要求通过当前项目已配置的治理 MCP 取得完整约束，普通 Release 用户行为不变。
- [x] 存在更高优先级明确 Agent_Skills 执行模式时，managed block 明确服从该模式，而不是继续强制 Runtime/MCP 获取路径。
- [x] 模式覆盖只影响 Agent_Skills 规则取得路径和与该模式冲突的 Runtime 控制面披露要求，不得让 Agent 忽略目标项目自己的 Overlay、事实、Contract、Schema、CI、部署或验收规则。
- [x] managed block 不复制 Source Mode 的 canonical 仓库地址、Entry/Router/Reference 路径、Stable ID、Maintenance 细节或第二套 Router；普通 Runtime 用户仍不需要知道内部治理导航。
- [x] Source Mode 失败边界仍由更高优先级 Source Mode 指令和 canonical Agent_Skills 规则负责；managed block 不新增网页搜索、旧 Runtime 或缓存等兜底路径。
- [x] Bootstrap canonical Reference 与 managed block 唯一模板语义同步，现有 Runtime/Source Mode Ownership 不发生漂移。
- [x] targeted preservation/behavior tests 先在旧实现上失败，再在实现后通过；完整 Skill Tests 通过。
- [x] 独立 Requirement / 内容守恒 / Runtime 披露边界 Review 无未解决 BLOCKER/HIGH/MEDIUM Finding。

# 方案比较与选择

## 方案 A：只强化维护者 Custom Instructions

优点：不改 Runtime Release 资产。

缺点：目标项目 managed block 仍重复要求本地 Runtime/MCP，模型需要在同一项目中自行解析两套互斥入口；网页端尤其容易退化为“知道应该 Source Mode，但项目根规则仍要求 Runtime”。无法从 canonical 分发边界消除冲突。

结论：不采用。

## 方案 B：managed block 增加高优先级执行模式覆盖契约（采用）

在 managed block 最前部明确：它定义的是默认 Runtime Mode；若系统/开发者/用户级更高优先级指令已明确选择其他 Agent_Skills 执行模式，则仅对冲突的 Runtime/MCP 取得路径与 Runtime 披露限制让位，项目 Overlay 始终保留。

优点：保持普通用户默认 Runtime；维护者 Source Mode 不再和项目根受管入口对打；不需要 Runtime 识别用户身份；不复制 canonical Source 细节。

风险：如果边界写得过宽，可能错误跳过项目规则；如果写得过窄，仍会强制 Runtime。通过正反向测试明确“只覆盖 Runtime acquisition/disclosure，不覆盖 project Overlay”。

结论：采用。

## 方案 C：由 Runtime/Installer 自动识别维护者身份并切换 Source Mode

缺点：身份与宿主权限不属于本地 Runtime 可可靠判断的事实，会把 GitHub 账号、ChatGPT/Codex 宿主能力和本地安装耦合，增加隐私、兼容和维护成本，也违背 Source Mode 应由高优先级宿主指令选择的边界。

结论：不采用。

# 范围

- 修改 managed block 唯一模板，使 Runtime 为默认模式而非不可覆盖模式。
- 同步 Bootstrap canonical Reference 对 managed block 的职责和验证要求。
- 增加 targeted tests，验证默认 Runtime、Source Mode override、Overlay 保留和披露边界。

# 非目标

- 不修改 MCP Tool Contract、Task Route、Routing Manifest、Bundle、加密、Runtime Python server 或 Installer ownership schema。
- 不改变 Source Mode canonical 仓库入口、Router、Skill/Reference 路由语义。
- 不在 managed block 中硬编码 `dingyuwen777/Agent_Skills`、GitHub App、Source Mode 文件路径或维护流程。
- 不修改当前目标项目 AIMA_UGC 的安装副本；该项目需在未来安装/升级包含本变更的 Release 后获得新的 managed block。
- 本任务不创建正式 Release/tag。

# 必须保持不变

- 普通用户没有更高优先级模式覆盖时继续使用项目级 Runtime/MCP。
- 项目事实和项目 Overlay 始终优先于通用 Agent_Skills 示例。
- Runtime Mode 内部治理控制面仍保持静默，工程过程仍可正常显示。
- Source Mode 仍直接读取 canonical 源仓库，不调用目标项目本地 Runtime/MCP。
- Runtime Project Payload、install manifest v3、受管 marker、项目用户文本保护和 fail-closed ownership 不变。
- canonical References、routing metadata、Stable ID、source/routing digest 语义不变。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 维护者网页/Codex Source Mode 不应被目标项目 Runtime managed block 强制切回本地 MCP | https://github.com/dingyuwen777/Agent_Skills/issues/113 | satisfied | `AGENTS.managed.md` 明确 Runtime 为默认模式，并让位于更高优先级显式 Agent_Skills 模式；`test_managed_bootstrap_defaults_runtime_but_allows_higher_priority_mode_override` 通过。 |
| R2 | 普通 Release 用户仍默认使用 Runtime/MCP | https://github.com/dingyuwen777/Agent_Skills/issues/113 | satisfied | managed block 首段、模式声明、步骤 2/8 都限定默认 Runtime；原 Runtime MCP 流程与项目安装回归继续通过。 |
| R3 | Source Mode 覆盖不得跳过项目自身 Overlay 与真实项目事实 | https://github.com/dingyuwen777/Agent_Skills/issues/113 | satisfied | managed block 显式保留项目规则、事实、Contract、Schema、CI、部署和验收边界；Bootstrap 与真实 Project Payload 安装测试均断言该语义。 |
| R4 | 不复制 Source Mode canonical 仓库/内部导航到普通 Runtime managed block | .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md | satisfied | disclosure regression 禁止 `dingyuwen777/Agent_Skills`、GitHub App、Maintenance、内部路径进入 managed/安装后的根 AGENTS；本轮 263 个测试通过。 |
| R5 | Source/Runtime 两种模式继续共享同一 canonical 规则语义，只改变取得通路与披露层 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | 未修改 MCP/Bundle/Router/Runtime Python；Source navigation、Runtime projection、exact-text、routing conformance、context footprint 和 disclosure 回归全部通过。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | GitHub Actions run `33379066539`：self-contained suite `Ran 263 tests`，`OK`；覆盖默认 Runtime、higher-priority override、Overlay 保留。 |
| 接口 / Contract | required | `AGENTS.managed.md` 与 ref12 同步；当前非 Draft PR #116 diff 只新增薄模式契约，不改变 MCP Tool Contract、Stable ID 或 schema。 |
| 集成 / Persistence / Runtime Dependency | required | `test_canonical_runtime_install_creates_pending_governance_agents` 与 `test_real_project_install_keeps_internal_runtime_assets_out_of_root_guidance` 使用 canonical Bundle/Project Payload/Installer 生成真实临时项目并通过。 |
| 用户 / Workflow Acceptance | required | 普通 Runtime 路径与维护者 Source Mode 两条入口反向审查通过；首段 Runtime 职责歧义在 Review 中发现后增加回归并修复。 |
| 跨组件 Golden Path | not_applicable | 未修改 MCP/Runtime 执行链；本次只改变安装到项目的 Bootstrap 规则文本及其 canonical 说明。 |
| 外部依赖 Probe | not_applicable | 不依赖第三方 Provider 或现时网络事实。 |
| Build / Package / Runtime | not_applicable | 未修改 `runtime/`、Builder、package/release workflow；按当前 path-scoped 门禁不要求三平台 onefile。Skill Tests 中 Python compile、CLI smoke、Project Payload/Installer integration 均通过。 |
| Docs / Governance / Other | required | ref12 同步；context footprint migration 继续通过；A1/A2 Deep Review 完成；Change `ready_for_review` 后 Ready Check 已在 run `33379223979` 通过。 |

# TDD / 验证证据

- 初始 Red：已关闭 Draft PR #111 run `33377500225`，旧 managed block 上 `263` 个测试中新增断言造成 `10` 个失败，均为缺少模式覆盖语义。
- Green 收敛：实现后曾触发 required-context 8 KiB 历史预算，未提高阈值，改为压缩 ref12 重复说明；预算最终通过。
- Review 回归 Red：run `33379005282`，新加“首段 Runtime 职责必须限定默认模式”断言后 `263` 个测试中仅 `1` 个失败，原因与 Review Finding 一致。
- Review 修复 Green：run `33379066539`，compile 与 CLI smoke 通过，self-contained suite `Ran 263 tests in 4.310s`，`OK`；workflow 唯一失败为 Change 当时仍是 `in_progress`，Ready Check 明确报告这一项。
- Change Ready Green：run `33379223979` 完整成功，changed Change Ready Check 通过。
- 最新 main 同步 Green：分支通过中文 merge commit `8fac06553f6602764da71775fac4a3b3b2bd2da4` 合并 `main` `0fc35ac54d7b1c2f9ed5095303f75f066b4f1965`；run `33379485410` 完整成功，比较结果 `behind_by=0`，diff 仍为预期 5 个文件。

# 实施任务

1. [x] 在旧实现上补 managed block 模式覆盖回归测试并取得正确原因的 Red。
2. [x] 最小修改 `AGENTS.managed.md`：声明默认 Runtime + higher-priority mode override + Overlay 保留边界。
3. [x] 同步 ref12 managed block 职责，不修改 ref13 Runtime 分发正文。
4. [x] 收敛 required-context 增量，不提高历史预算门禁。
5. [x] 执行独立 Deep Review；发现并修复首段无条件 Runtime 职责这一 MEDIUM Finding，并以单独 Red → Green 回归证明。
6. [x] 更新本 Change 到 `ready_for_review`，Ready Check 已通过；因 GitHub 连接器 Draft→Ready GraphQL schema 错误关闭 Draft PR #111，并从同一已验证分支创建非 Draft PR #116，不绕过 Ready 门禁。
7. [ ] PR #116 取得本次治理状态同步后的新鲜 CI，全绿后合并；merge 后验证 main fresh CI，再独立归档 Change。

# Migration / 部署 / 回滚

- 迁移：无需数据或 schema migration。新 managed block 只会随未来包含本变更的 Runtime Release 安装/升级到目标项目；现有已安装旧 Release 不会被当前 main 源码自动改写。
- 部署：本任务只交付 Agent_Skills main，不创建 Release。后续正式 Release 仍按现有三平台 Release 门禁构建。
- 回滚：回退本次 canonical 变更或安装上一正式 Release，即可恢复旧 managed block；不得手工改目标项目中受 manifest 认领的安装副本冒充 canonical 回滚。

# 安全与兼容性

- 不新增 Secret、账号身份识别、远端鉴权或网络调用。
- 更高优先级模式选择来自宿主指令优先级，不由目标项目 Runtime 推断用户身份。
- 不降低项目规则、权限、CI、Git、Contract、Schema、部署和验收约束。
- 不把 Prompt/managed block 描述成安全隔离；Runtime 控制面静默仍只是用户可见披露边界。
- 私有仓库/GitHub App 是否可访问仍属于 Source Mode 宿主能力门禁，本次 managed block 不复制或发明该能力；读取失败继续由更高优先级 Source Mode 指令与 canonical 规则 fail closed。

# Completion Audit

- [x] upstream_re_read：在进入 Ready 前重新读取 Issue #113、当前 main 根 `AGENTS.md`、`.agents/MAINTENANCE.md`、分支 managed/ref12、当前 ref13/ref15 与受影响测试/PR diff。
- [x] change_coverage：逐项比较 Issue #113 与实现，默认 Runtime、Source override、Overlay 保留、内部身份不泄露均有实现和测试；私有仓库访问能力保持在 Source Mode Owner，本次不错误复制到 Runtime managed block。
- [x] reverse_audit：从普通 Runtime 和维护者 Source Mode 两条入口反向检查最终 managed block；首段 Runtime 职责也已限定默认模式，不再残留无条件 Runtime 强制路径。
- [x] unresolved_cleared：R1–R5 全部 `satisfied`；无待决策项。三平台 onefile 未运行是按 path-scope 明确判定 `not_applicable`，不是漏测。

# Review

- Review 深度：L3 Deep Review；目标为 Issue #113 + 当前 main + 当前非 Draft PR #116（历史 TDD Red 来自已关闭 Draft PR #111）。
- A1 Requirement Review：PASS。Issue 中默认 Runtime、显式高优先级模式覆盖、Overlay 保留、不泄露 Source 内部导航、非目标/回滚均已映射到实现和测试。
- A2 Implementation / Test Review：PASS after fix。首次审查发现 1 个 MEDIUM：managed block 第一段仍无条件声明 Runtime 负责完整约束；已增加回归测试，在 run `33379005282` 正确失败后修正为“在默认 Runtime Mode 下”，run `33379066539` 的 263 个测试全部通过。
- 内容守恒：PASS。只改变 Runtime Bootstrap 模式优先级契约；Router/Skill/Reference、MCP/Bundle/Runtime Python、Project Payload ownership 与 Source Mode 明文导航均未弱化。
- 披露边界：PASS。Runtime managed/真实安装根 AGENTS 不出现 canonical 仓库地址、GitHub App、Maintenance、内部 Reference 导航；默认 Runtime 的静默规则仍受原测试覆盖。
- 当前开放 Findings：无 BLOCKER / HIGH / MEDIUM；无需要阻止 Ready 的 LOW。

# Git / PR / Release 状态

- Branch：`change/managed-source-mode-override`
- 主分支同步提交：`8fac06553f6602764da71775fac4a3b3b2bd2da4`，合并基线 `main` `0fc35ac54d7b1c2f9ed5095303f75f066b4f1965`，比较结果 `behind_by=0`。
- Requirement Source：Issue #113 `https://github.com/dingyuwen777/Agent_Skills/issues/113`
- PR：#116（非 Draft，当前正式交付 PR）。#111 已关闭且未合并，仅保留历史 TDD/CI 证据；关闭原因是 Draft→Ready 连接器 GraphQL schema 错误。
- Merge：待 PR #116 当前 head 新鲜 CI 全绿后执行。
- Main fresh CI：待 merge 后执行。
- Release：本任务不创建正式 Release；AIMA_UGC 当前已安装旧 Release 不会自动获得该 managed block。
