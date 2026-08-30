---
schema: coding-change/v1
id: "CHG-20260830-project-governance-bootstrap"
title: "建立目标项目治理 Bootstrap 与首次接入用法"
level: L3
status: proposed
owner: "dingyuwen777"
branch: "feat/project-governance-bootstrap"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "目标项目首次接入与事实恢复"
  - "项目 AGENTS Overlay 治理"
  - "Runtime Project Payload Bootstrap 资产"
  - "最终用户 MCP 使用说明"
affected_paths:
  - ".agents/skills/coding/SKILL.md"
  - ".agents/skills/coding/references/01_项目发现与可失效缓存.md"
  - ".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/assets/AGENTS.template.md"
  - "USAGE.md"
  - ".agents/skills/coding/tests/test_project_bootstrap.py"
  - ".agents/skills/coding/tests/test_project_governance_bootstrap.py"
contracts:
  - "目标项目 Project Governance Bootstrap 工作流"
  - "目标项目 AGENTS Overlay 内容边界"
data_changes: []
---

# 目标

把目标项目首次使用 Agent_Skills 的流程从“安装后直接开发”明确升级为两阶段：Runtime Installation Bootstrap 只做机械安全安装；首次研发会话或发现治理事实漂移时，由 Agent 在任何实质性生产代码修改前执行 Project Governance Bootstrap，基于目标仓库当前真实实现创建或校准项目自己的 `AGENTS.md` Overlay，完成后重新读取最终 `AGENTS.md` 再进入正常开发。

# 用户要求

1. 使用 Agent_Skills 帮助其他项目开发时，应先生成或修改项目 `AGENTS.md`。
2. `AGENTS.md` 不能由模板猜测，需要大模型调查目标仓库真实实现、规则、代码、Contract、Schema/Migration、测试、CI、部署和正式文档后再写。
3. 已有 `AGENTS.md` 应结合现有内容和代码现实安全修正，而不是覆盖或机械重写。
4. 应固定一个通用结构模板，但固定的是结构与判断规则，不是具体技术栈或项目事实。
5. `USAGE.md` 必须告诉最终用户如何使用本地 MCP/Agent_Skills 完成首次治理 Bootstrap 和后续代码修改，并提供可直接使用的自然语言示例。

# 成功标准

- [ ] Coding Core 明确首次接入 / AGENTS 缺失或初始模板 / 长期治理事实疑似漂移时，生产代码修改前先执行 Project Governance Bootstrap。
- [ ] 项目发现规则明确先做有界事实调查，并输出“规范性规则 / 描述性事实 / 未确认事项”三类判断依据。
- [ ] AGENTS Bootstrap Reference 明确区分 Runtime Installation Bootstrap 与 Project Governance Bootstrap。
- [ ] 已有 AGENTS 校准时保留仍有效规范性规则；实现违反规则时报告实现问题，不能通过改 AGENTS 让错误实现合法化。
- [ ] 已有 AGENTS 中可证伪的描述性事实与当前仓库事实冲突时允许修正；无法确认的内容不猜。
- [ ] 只允许 Agent 修改目标项目自有 Overlay；Agent Skills managed block 仍由安装器维护，不手工改写。
- [ ] `AGENTS.template.md` 固定长期结构骨架，但不写死语言、框架、数据库、CI、部署等项目事实。
- [ ] managed block 能让首次研发会话主动命中 Project Governance Bootstrap，而不复制第二套完整 Coding/Router 规则。
- [ ] `USAGE.md` 明确“安装 ≠ 已完成项目治理”，给出首次接入、日常开发、治理事实变化后的可复制自然语言用法。
- [ ] Source Bootstrap 与 Runtime Project Installer 仍保持 existing AGENTS managed marker 外字节保护、fail-closed 和幂等性。
- [ ] Routing metadata、Stable Reference ID、Project Payload schema、install manifest schema、MCP Tool Contract、依赖均不改变。

# 非目标

- 不让 Runtime binary 自己扫描整个仓库并充当 LLM/第二个 Coding Agent。
- 不让安装器自动语义重写已有 `AGENTS.md` managed block 外项目内容。
- 不为所有项目强制同一语言、框架、数据库、目录结构、CI 或部署方式。
- 不要求每个普通开发任务都重写 `AGENTS.md`；只有首次接入、明确治理漂移或长期工程事实变化时才更新。
- 不修改 Bundle / Project Payload / install / MCP schema，不增加新的网络服务或 Provider。

# 必须保持不变

- Runtime binary 只做机械、安全、可证明的项目安装与 managed block 管理，不执行 LLM 语义判断。
- 现有 `AGENTS.md` managed marker 外内容在 Runtime 安装/升级时继续逐字保护。
- marker 损坏、ownership 不明确、同名受管资产冲突继续 fail closed。
- Router 仍是唯一跨 Skill Router；Coding 仍是研发主流程 Owner。
- 精确项目事实仍以代码、Contract、Schema/Migration、CI、测试等当前事实源为准，AGENTS 不复制第二套机器事实。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 首次使用 Skill 开发其他项目时先建立/校准项目 AGENTS | user:first-governance-bootstrap | not_satisfied | 待 Coding/Bootstrap 规则与回归 |
| R2 | 大模型调查仓库现实后才能写项目 AGENTS | user:investigate-before-agents | not_satisfied | 待项目发现与治理 Bootstrap 规则 |
| R3 | 已有 AGENTS 结合现有内容和代码现实修正，区分规则与事实 | user:reconcile-existing-agents | not_satisfied | 待 reconciliation 规则与测试 |
| R4 | 固定通用结构模板，但不固定具体技术栈 | user:agents-template | not_satisfied | 待 AGENTS.template 更新 |
| R5 | USAGE 告诉使用者如何通过 MCP/Agent_Skills 修改代码 | user:usage-mcp-development | not_satisfied | 待 USAGE 首次接入和日常开发说明 |
| R6 | 保持 Runtime/Project Payload/安装安全与兼容边界 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待三平台 Runtime / install 回归 |
| R7 | 按 Agent_Skills L3 门禁完成 Review、CI、PR、main fresh CI 和 Change 清理 | .agents/MAINTENANCE.md | not_satisfied | 待交付闭环 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Project Governance Bootstrap preservation + AGENTS source bootstrap tests Red→Green |
| 接口 / Contract | required | managed block / template / existing AGENTS ownership 与兼容语义守恒 |
| 集成 / Runtime Dependency | required | Project Payload 中资产进入 onefile Runtime，真实 project install 生成目标 AGENTS |
| 用户 / Workflow Acceptance | required | USAGE 首次接入提示可自然触发治理 Bootstrap，再进入开发 |
| 跨组件 Golden Path | required | Release payload → onefile → project install → AGENTS/Router/MCP → Ready Check |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider 或网络行为变化 |
| Build / Package / Runtime | required | Linux/Windows/macOS 永久 Runtime CI |
| Docs / Governance / Other | required | Skill 内容守恒 Review、Docs review、Ready Check、PR/main fresh CI |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户要求、当前分支 AGENTS、Maintenance、Router、Coding、ref01/ref12/ref13/ref15、USAGE 和相关测试。
- [ ] change_coverage：首次接入、已有 AGENTS 校准、模板结构、Runtime 边界和最终用户用法均有正式 Owner。
- [ ] reverse_audit：从“安装后二次打开开发工具并直接要求改代码”反查是否会先触发治理 Bootstrap；从普通后续任务反查是否不会无意义重写 AGENTS。
- [ ] unresolved_cleared：所有 not_satisfied 清零；交付后置步骤仅保留明确 deferred 状态。

# 任务

- [x] 读取当前 main 的 AGENTS、Maintenance、Router、Coding、项目发现、AGENTS Bootstrap、Runtime 分发、USAGE、安装实现与现有 Bootstrap 测试。
- [ ] 新增 Project Governance Bootstrap preservation/behavior Red。
- [ ] 更新 Coding Core、项目发现、AGENTS Bootstrap、managed/template assets 和 USAGE。
- [ ] 必要时只做最小实现调整；不把语义调查塞进 Runtime binary。
- [ ] 跑全量测试、三平台 Runtime、真实项目安装、独立 Review 和 Ready Check。
- [ ] 非 Draft PR 正常合并；main fresh CI 后删除 Active Change。

# Contract / Schema / Migration / 依赖

- Routing metadata / Stable Reference ID：原则上不变；如确需增加已有 ref12 的触发同义词，只允许不改变 Stable ID/依赖/风险边界的兼容扩展并记录。
- Project Payload / install manifest / MCP：schema 不变。
- Schema / Migration / 数据：无。
- 依赖：无。

# 交付

- Branch：`feat/project-governance-bootstrap`
- PR：待创建
- Release：本任务不创建正式 Release
