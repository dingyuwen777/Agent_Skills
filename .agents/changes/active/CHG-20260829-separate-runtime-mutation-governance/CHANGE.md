---
schema: coding-change/v1
id: CHG-20260829-separate-runtime-mutation-governance
title: 收敛 Runtime 用户面与 Skill Mutation 源仓库治理边界
level: L2
status: in_progress
owner: ChatGPT
branch: fix/runtime-user-surface-mutation-boundary
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - project-payload
  - router
  - bootstrap
  - skill-governance
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/skills/ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/references/16_规则内容守恒与Skill维护.md"
  - ".agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py"
contracts:
  - "Runtime user-facing routing surface"
  - "Agent_Skills source-repository Skill Mutation ownership"
data_changes: []
---

# 目标

普通用户只拿 Release Runtime binary 安装到业务项目时，不再在项目 `AGENTS.md` managed block 或共享 `ROUTER.md` 中看到 `Skill Mutation`、canonical repository、`dingyuwen777/Agent_Skills`、源仓库 Maintenance 等维护者专用治理信息；同时保留普通项目真正需要的正常 Coding / Review / Docs / Figma / Reference 路由与最薄的受管运行资产保护。

Agent_Skills 源仓库自身仍必须完整保留 Skill / Reference 新增、修改、删除、重命名、拆分、合并、通用化和跨仓库同步的 canonical Ownership、内容守恒、Change、Review、CI、PR、main 验证与归档规则。源仓库根 `AGENTS.md` 负责 Mutation 意图升级入口，`ref16` 负责详细内容守恒；Custom Instructions 可以作为外部薄触发器，但不是 canonical 规则事实源。

# 成功标准

- [ ] Runtime Project Payload 中的 `ROUTER.md` 不包含 `Skill Mutation`、`dingyuwen777/Agent_Skills`、`.agents/MAINTENANCE.md` 或源仓库 Mutation 维护入口。
- [ ] Runtime Project Payload 中的 `coding/assets/AGENTS.managed.md` 不包含 `Skill Mutation`、canonical repository、源仓库 Maintenance / ref16 等维护者术语。
- [ ] managed block 仍保留项目事实优先、读取 `.agents/skills/ROUTER.md`、按需加载 Skill/Reference、失败停止以及“不要手工维护安装器认领的 `.agents` 运行资产”的最薄保护。
- [ ] `ROUTER.md` 继续完整承担普通目标项目的动态 Skill Catalog、Coding 锚点、Reference 两种加载方式、Figma/Review/Docs Handoff、失败/权限/CI 门禁；不为 Mutation 再创建第二个 Runtime Router。
- [ ] 源仓库根 `AGENTS.md` 独立承担完整 Mutation 触发与 canonical Owner 路由，并继续支持“只改当前项目规则 / 项目自有 Skill”例外。
- [ ] `ref16` 继续完整承担 Skill/Reference 新增删除重命名、跨仓库同步、项目特定事实隔离和内容守恒规则；其入口不再依赖 Runtime Router 的 Mutation 章节。
- [ ] ref13/ref14 明确普通 Runtime 分发面不承载源仓库 Mutation 治理，同时保持 Project Payload / Router / Stub / MCP / install Contract 不变。
- [ ] 新增/修改永久回归，实际构建 Project Payload 并证明安装明文面不再携带源仓库 Mutation 治理；源仓库 Mutation 规则仍完整可达。
- [ ] 完成 Red → Green → 独立 Review → Ready → 非 Draft PR CI → merge → main 新鲜 CI → 独立 Change 归档。

# 范围

- 收敛根 `AGENTS.md`、共享 `ROUTER.md` 与 `AGENTS.managed.md` 的 Mutation Ownership。
- 同步 ref13/ref14/ref16 的正式职责说明。
- 调整 Skill Mutation / Project Payload 永久回归。

# 非目标

- 不修改 Runtime binary 加密、Bundle schema、Project Payload schema、install manifest schema、MCP Tool Contract、Reference Stub 格式或 Reference ID。
- 不删除普通 Runtime 用户必须使用的 Coding / Review / Docs / Figma / Reference 路由。
- 不改变 `.agents/runtime/`、Host MCP 配置、安装/升级/rollback 行为。
- 不修改 ChatGPT 产品级 Custom Instructions；只保证仓库允许 Custom Instructions 作为薄触发器，而 canonical 维护规则继续来自源仓库当前文件。
- 不自动创建新 Release 或修改 `VERSION`。

# 必须保持不变

- `.agents/skills/ROUTER.md` 仍是目标项目唯一普通跨 Skill Router，并原样作为 shared runtime file 进入 Project Payload。
- 正式 Skill 继续从 `.agents/skills/*/SKILL.md` 动态发现，不新增静态白名单。
- canonical References 继续加密进入 Runtime，目标项目只保存同名 Stub，通过 `agent_skills_load_context` 取得并校验 `canonical_text`。
- 项目自身规则与真实事实优先；Router/Skill/Reference 缺失或无法验证时继续 fail closed。
- Source repository 的 Mutation canonical Owner、项目特定事实隔离、内容守恒、Change/Review/CI/PR/Release 安全门禁不得降低。

# 已确认关键决策

采用“**一个普通 Runtime Router + 源仓库专用 Mutation Bootstrap**”，不新增 runtime/source 两份 Router：

```text
普通目标项目
→ AGENTS.managed.md
→ .agents/skills/ROUTER.md
→ 普通研发路由

Agent_Skills 源仓库
→ 根 AGENTS.md 识别 Skill Mutation
→ .agents/MAINTENANCE.md + Coding + ref16
→ canonical 维护
```

这样既不把维护者专用信息分发给普通用户，也不重新制造两份 Router 事实源。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 普通 exe 用户不需要看到 Skill Mutation / canonical Owner / 源仓库维护说明 | user:2026-08-29-runtime-user-surface | not_satisfied | 待 Red/Green：当前 `AGENTS.managed.md` 与 `ROUTER.md` 仍包含这些内容。 |
| R2 | Mutation 更适合作为 Owner 侧 Custom Instructions 的薄触发，并由当前源仓库规则承担 canonical 维护 | user:2026-08-29-runtime-user-surface | not_satisfied | 待实现：根 `AGENTS.md` 保留/强化 Mutation 入口，Runtime 面移除维护细节。 |
| R3 | 普通 Runtime 的正常研发路由、Reference 加载和安装 Contract 不能因收敛而丢失 | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | not_satisfied | 待回归证明普通 Router / managed block 高价值语义保持。 |
| R4 | Runtime/Project Payload/Skill 规则重组必须保持内容守恒与三平台 artifact 验证 | `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md` | not_satisfied | 待永久 CI、Project Payload exact-content 与三平台 package/install 证据。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 修改 Mutation/Router/managed preservation tests，先证明旧 Runtime 用户面 Red，再证明新 Ownership Green。 |
| 接口 / Contract | required | 检查 root AGENTS / Runtime Router / managed block / ref16 的 Owner 与触发边界，保证普通路由语义不丢。 |
| 集成 / Persistence / Runtime Dependency | required | 真实调用 `build_bundle()` + `build_project_payload()`，检查最终 Project Payload 明文文件内容，而非只检查源文件。 |
| 用户 / Workflow Acceptance | required | onefile 项目安装后的 AGENTS/Router/Stub/MCP 链继续可用；普通安装面不出现源仓库 Mutation 治理。 |
| 跨组件 Golden Path | required | 永久 CI 的 onefile → status/self-test → real stdio MCP → project-only install / installed Runtime smoke。 |
| External Dependency / Provider Probe | not_applicable | 不依赖业务第三方 Provider；Custom Instructions 属宿主外部配置，本 Change 不修改产品设置。 |
| Build / Package / Runtime | required | Linux onefile/MCP/install、Windows/macOS package/install 全部使用最终 HEAD 验证。 |
| Docs / Governance / Other | required | 内容守恒、A1/A2、独立 Review、Completion Audit、Ready Gate、PR/main CI、独立 archive。 |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户目标、根 AGENTS、Maintenance、Router、Coding、ref13/ref14/ref16。
- [ ] change_coverage：逐项检查普通用户安装面、源仓库 Mutation、动态 Skill、Reference Stub/MCP、失败/权限边界。
- [ ] reverse_audit：按 `Owner Custom Instruction → source AGENTS → Maintenance/ref16` 与 `binary → Project Payload → managed → Router → Skill/Reference` 两条路径反向复核。
- [ ] unresolved_cleared：Requirement 全部 satisfied 或有正式延期/不适用依据，无开放 Review Finding。

# TDD / 实施与验证证据

待执行。

# 独立 Review

待执行。

# 文档影响

Docs Impact：`targeted`。本次属于规则 Ownership / Runtime 分发面调整，需要同步 root `AGENTS.md`、Router、managed template、ref13/ref14/ref16；`USAGE.md` 的最终用户操作步骤、文件名、安装命令、CLI 与 Release 资产均不变化，预计无需修改。

# Git / PR / Release 状态

- branch: `fix/runtime-user-surface-mutation-boundary`
- base: `main@9b0bd3df2575c2ca0db4ed9985dfb5af02d0b59b`
- PR: 未创建
- merge: 未执行
- main CI: 未执行
- Release: 不触发
