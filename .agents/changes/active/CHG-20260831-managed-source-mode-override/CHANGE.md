---
schema: coding-change/v1
id: CHG-20260831-managed-source-mode-override
title: Runtime managed block 支持高优先级 Source Mode 覆盖
level: L3
status: in_progress
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

- [ ] 没有更高优先级 Agent_Skills 模式覆盖时，managed block 仍默认要求通过当前项目已配置的治理 MCP 取得完整约束，普通 Release 用户行为不变。
- [ ] 存在更高优先级明确 Agent_Skills 执行模式时，managed block 明确服从该模式，而不是继续强制 Runtime/MCP 获取路径。
- [ ] 模式覆盖只影响 Agent_Skills 规则取得路径和与该模式冲突的 Runtime 控制面披露要求，不得让 Agent 忽略目标项目自己的 Overlay、事实、Contract、Schema、CI、部署或验收规则。
- [ ] managed block 不复制 Source Mode 的 canonical 仓库地址、Entry/Router/Reference 路径、Stable ID、Maintenance 细节或第二套 Router；普通 Runtime 用户仍不需要知道内部治理导航。
- [ ] Source Mode 失败边界仍由更高优先级 Source Mode 指令和 canonical Agent_Skills 规则负责；managed block 不新增网页搜索、旧 Runtime 或缓存等兜底路径。
- [ ] Bootstrap canonical Reference 与 managed block 唯一模板语义同步，现有 Runtime/Source Mode Ownership 不发生漂移。
- [ ] targeted preservation/behavior tests 先在旧实现上失败，再在实现后通过；完整 Skill Tests 与受影响 CI 通过。
- [ ] 独立 Requirement / 内容守恒 / Runtime 披露边界 Review 无 BLOCKER/HIGH/MEDIUM Finding。

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
| R1 | 维护者网页/Codex Source Mode 不应被目标项目 Runtime managed block 强制切回本地 MCP | user:managed-source-mode-override | not_satisfied | 待通过 managed block 模式覆盖契约和 targeted tests 证明。 |
| R2 | 普通 Release 用户仍默认使用 Runtime/MCP | user:managed-source-mode-override | not_satisfied | 待通过默认 Runtime 文案与回归测试证明。 |
| R3 | Source Mode 覆盖不得跳过项目自身 Overlay 与真实项目事实 | user:managed-source-mode-override | not_satisfied | 待通过 managed block 显式边界和正向断言证明。 |
| R4 | 不复制 Source Mode canonical 仓库/内部导航到普通 Runtime managed block | .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md | not_satisfied | 待通过 disclosure regression 证明。 |
| R5 | Source/Runtime 两种模式继续共享同一 canonical 规则语义，只改变取得通路与披露层 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待通过内容守恒 Review、targeted/full tests 证明。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | managed block 正反向语义测试：默认 Runtime、明确更高优先级模式覆盖、Overlay 保留。 |
| 接口 / Contract | required | `AGENTS.managed.md` 作为 Runtime/LLM 消费的 Bootstrap Contract；模板和 ref12 必须一致。 |
| 集成 / Persistence / Runtime Dependency | required | canonical Project Payload/Installer 生成的目标 `AGENTS.md` 必须包含新模式契约且保留原 marker/Runtime 行为。 |
| 用户 / Workflow Acceptance | required | 维护者 Source Mode 与普通 Runtime 两种入口从根规则得到无冲突、可执行的模式选择语义。 |
| 跨组件 Golden Path | not_applicable | 不修改 MCP/Runtime 执行链；本次只改变安装到项目的 Bootstrap 规则文本。 |
| 外部依赖 Probe | not_applicable | 不依赖第三方 Provider 或现时网络事实。 |
| Build / Package / Runtime | not_applicable | 不修改 Runtime Python、Builder、Package workflow 或 binary 构建边界；Project Payload/Installer 语义由 self-contained integration test 覆盖。 |
| Docs / Governance / Other | required | ref12、managed block、内容守恒、Ready Check、独立 Review 与 CI。 |

# 实施任务

1. 在现有实现上先补 managed block 模式覆盖回归测试，取得正确原因的 Red。
2. 最小修改 `AGENTS.managed.md`：声明默认 Runtime + higher-priority mode override + Overlay 保留边界。
3. 同步 ref12 managed block 职责、默认/覆盖语义和验证条目，不修改 ref13 Runtime 分发正文。
4. 运行 targeted tests、完整 self-contained Skill Tests、Ready Check。
5. 执行独立 Deep Review：A1 上游要求完整性、A2 实现/测试/文档、内容守恒、披露边界和兼容性。
6. 更新本 Change 到 `ready_for_review`，创建 PR，读取新鲜 CI；合并后验证 main fresh CI，再独立归档 Change。

# Migration / 部署 / 回滚

- 迁移：无需数据或 schema migration。新 managed block 只会随未来包含本变更的 Runtime Release 安装/升级到目标项目；现有已安装旧 Release 不会被当前 main 源码自动改写。
- 部署：本任务只交付 Agent_Skills main，不创建 Release。后续正式 Release 仍按现有三平台 Release 门禁构建。
- 回滚：回退本次 canonical 变更或安装上一正式 Release，即可恢复旧 managed block；不得手工改目标项目中受 manifest 认领的安装副本冒充 canonical 回滚。

# 安全与兼容性

- 不新增 Secret、账号身份识别、远端鉴权或网络调用。
- 更高优先级模式选择来自宿主指令优先级，不由目标项目 Runtime 推断用户身份。
- 不降低项目规则、权限、CI、Git、Contract、Schema、部署和验收约束。
- 不把 Prompt/managed block 描述成安全隔离；Runtime 控制面静默仍只是用户可见披露边界。

# Completion Audit

- [ ] upstream_re_read：完成前重新读取用户要求、根 AGENTS、Maintenance、ref12/ref13/ref15 与受影响测试。
- [ ] change_coverage：逐项比较用户目标与本 Change，确认没有遗漏“默认 Runtime / Source override / Overlay 保留 / 私有仓库能力边界”。
- [ ] reverse_audit：从普通 Runtime 和维护者 Source Mode 两条入口反向检查最终 managed block，不出现互斥强制路径。
- [ ] unresolved_cleared：所有 Requirement Traceability `not_satisfied` 清零，未验证项明确。

# Review

状态：待实现后执行独立 Deep Review。

# Git / PR / Release 状态

- Branch：`change/managed-source-mode-override`
- Commit：已创建 Change 初始化提交；实现提交待产生。
- PR：待创建。
- Merge：待 CI/Review 门禁完成后执行。
- Main fresh CI：待 merge 后执行。
- Release：本任务不创建正式 Release。
