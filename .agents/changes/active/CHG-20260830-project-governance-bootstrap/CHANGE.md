---
schema: coding-change/v1
id: "CHG-20260830-project-governance-bootstrap"
title: "建立目标项目治理 Bootstrap 与首次接入用法"
level: L3
status: ready_for_review
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
  - ".agents/skills/coding/tests/test_project_governance_bootstrap.py"
contracts:
  - "目标项目 Project Governance Bootstrap 工作流"
  - "目标项目 AGENTS Overlay 内容边界"
data_changes: []
---

# 目标

把目标项目首次使用 Agent_Skills 的流程从“安装后直接开发”明确升级为两阶段：Runtime Installation Bootstrap 只做机械安全安装；首次研发会话或发现治理事实漂移时，由当前项目使用的宿主大模型在任何实质性生产代码修改前执行 Project Governance Bootstrap，基于目标仓库当前真实实现创建或校准项目自己的 `AGENTS.md` Overlay，完成后重新读取最终 `AGENTS.md` 并继续原始研发任务。

# 用户要求

1. 使用 Agent_Skills 帮助其他项目开发时，应先生成或修改项目 `AGENTS.md`。
2. `AGENTS.md` 不能由模板猜测，需要大模型调查目标仓库真实实现、规则、代码、Contract、Schema/Migration、测试、CI、部署和正式文档后再写。
3. 已有 `AGENTS.md` 应结合现有内容和代码现实安全修正，而不是覆盖或机械重写。
4. 应固定一个通用结构模板，但固定的是结构与判断规则，不是具体技术栈或项目事实。
5. Runtime binary 不替代大模型做语义调查；用户通过自然语言研发任务触发当前项目所用宿主大模型完成调查、AGENTS 校准并继续原始任务。
6. `USAGE.md` 必须告诉最终用户如何使用本地 MCP/Agent_Skills 完成首次治理 Bootstrap 和后续代码修改，并提供可直接使用的自然语言示例。

# 成功标准

- [x] Coding Core 明确首次接入 / AGENTS 缺失或初始模板 / 长期治理事实疑似漂移时，生产代码修改前先执行 Project Governance Bootstrap。
- [x] 项目发现规则明确先做有界事实调查，并输出“规范性规则 / 描述性事实 / 未确认事项”三类判断依据。
- [x] AGENTS Bootstrap Reference 明确区分 Runtime Installation Bootstrap 与 Project Governance Bootstrap。
- [x] 已有 AGENTS 校准时保留仍有效规范性规则；实现违反规则时报告实现问题，不能通过改 AGENTS 让错误实现合法化。
- [x] 已有 AGENTS 中可证伪的描述性事实与当前仓库事实冲突时允许修正；无法确认的内容不猜。
- [x] 只允许 Agent 修改目标项目自有 Overlay；Agent Skills managed block 仍由安装器维护，不手工改写。
- [x] `AGENTS.template.md` 固定长期结构骨架，但不写死语言、框架、数据库、CI、部署等项目事实。
- [x] managed block 先读取唯一 Router，再让普通自然语言研发任务在首次接入/待校准/治理漂移时命中 Project Governance Bootstrap，不复制第二套完整 Router。
- [x] 只读首次任务不写项目规则，但完成会话内最少充分治理调查后继续原始只读任务。
- [x] `USAGE.md` 明确“安装 ≠ 已完成项目治理”，给出首次接入、日常开发、治理事实变化后的可复制自然语言用法。
- [x] Source Bootstrap 与 Runtime Project Installer 仍保持 existing AGENTS managed marker 外字节保护、fail-closed 和幂等性。
- [x] Routing metadata、Stable Reference ID、Project Payload schema、install manifest schema、MCP Tool Contract、依赖均不改变。

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
| R1 | 首次使用 Skill 开发其他项目时先建立/校准项目 AGENTS | user:first-governance-bootstrap | satisfied | Coding Core 硬触发 + ref12 两阶段 Bootstrap + managed block 首次/待校准触发；永久治理回归通过 |
| R2 | 大模型调查仓库现实后才能写项目 AGENTS | user:investigate-before-agents | satisfied | ref01 新增有界事实调查；ref12 明确由宿主大模型执行，不由 Runtime binary 猜架构 |
| R3 | 已有 AGENTS 结合现有内容和代码现实修正，区分规则与事实 | user:reconcile-existing-agents | satisfied | ref01/ref12 明确规范性规则、描述性事实、未确认事项；禁止通过改 AGENTS 合法化错误实现 |
| R4 | 固定通用结构模板，但不固定具体技术栈 | user:agents-template | satisfied | `AGENTS.template.md` 新增治理状态、工程基线、架构、Contract、验证、CI/Release/部署等结构骨架；明确无证据不填、不发明技术栈 |
| R5 | 自然语言触发当前项目宿主大模型治理后继续原任务 | user:host-llm-natural-language-bootstrap | satisfied | managed block 先 Router 后治理；Coding/ref12 明确普通自然语言任务可触发，并在校准/重读 AGENTS 后继续原始研发任务；只读边界也覆盖 |
| R6 | USAGE 告诉使用者如何通过 MCP/Agent_Skills 修改代码 | user:usage-mcp-development | satisfied | USAGE 新增首次接入与日常开发章节、可复制 Project Governance Bootstrap 提示词以及“直接自然语言开发任务也会自动触发”说明 |
| R7 | 保持 Runtime/Project Payload/安装安全与兼容边界 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | 未改 Runtime Python/protocol；run `33299971593` 的 180 tests、Linux onefile/MCP/project install、Windows/macOS package/install 产品链全部 Green |
| R8 | 按 Agent_Skills L3 门禁完成 Review、CI、PR、main fresh CI 与 Change 清理 | .agents/MAINTENANCE.md | explicitly_deferred | Final Ready run `33300086948` 三个 Job 全绿；Draft PR #54 因连接器 `Repository.fullDatabaseId` GraphQL 缺陷关闭且未合并；非 Draft PR #55 使用同一 feature branch 接棒，仍需其最终 HEAD 永久 CI、正常 merge、main fresh CI 和独立 Active Change 清理 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Initial Red `33299105196`：178 tests 中仅新增 5 条治理回归失败；Review Red `33299634725`：179 tests 中仅 3 条 Review 语义断言 + 1 条既有 Core 大小门禁失败；Router-order Red `33299930033`：180 tests 中仅新顺序回归失败；pre-Ready `33299971593` 180 tests 全 Green |
| 接口 / Contract | required | managed block / template / existing AGENTS ownership 语义守恒；Routing metadata/Stable ID 未改；Router 仍唯一跨 Skill Owner |
| 集成 / Runtime Dependency | required | 永久测试用 canonical Bundle + Project Payload + `install_project()` 在临时项目验证真实生成 AGENTS 含待校准状态、结构骨架和自然语言入口 |
| 用户 / Workflow Acceptance | required | USAGE 明确首次接入任意项目先由当前大模型治理，提供纯治理和“治理后继续原开发任务”两种可复制自然语言示例 |
| 跨组件 Golden Path | required | run `33299971593`：180 tests → Linux onefile → real stdio MCP → project-only install；Windows/macOS package/install 同步 Green |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider、网络 Contract 或在线服务行为变化 |
| Build / Package / Runtime | required | run `33299971593`：Windows/macOS package/install success；Linux onefile/status/self-test/project install success |
| Docs / Governance / Other | required | 独立 Review 三轮发现均先建 Red 再修复；最终 re-review `NO_FINDINGS_WITHIN_SCOPE`；pre-Ready 唯一 Job 失败为 Change `proposed` 的预期 Ready Gate |

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取用户要求、当前 feature 根 AGENTS、Maintenance、Router、Coding、ref01/ref12/ref13/ref15、USAGE、永久治理测试和最终 PR diff。
- [x] change_coverage：首次接入、Greenfield/已有项目、已有 AGENTS 校准、只读权限、模板结构、Runtime 边界、自然语言触发、Router 顺序和最终用户用法均有正式 Owner。
- [x] reverse_audit：从“安装后二次打开开发工具并直接要求改代码”反查为 AGENTS managed block → Router → Coding/ref01/ref12 → Governance Bootstrap → 重读最终 AGENTS → 原任务；普通后续任务只有长期治理漂移时 targeted 更新，不无意义重写 AGENTS。
- [x] unresolved_cleared：R1–R7 satisfied；R8 仅保留必须发生在 Ready 之后的正式交付生命周期 `explicitly_deferred`；无 `not_satisfied`。

# 任务

- [x] 读取当前 main/feature 的 AGENTS、Maintenance、Router、Coding、项目发现、AGENTS Bootstrap、Runtime 分发、规则内容守恒、USAGE、安装实现与相关测试。
- [x] 新增 Project Governance Bootstrap preservation/behavior Red，并验证 Red 精确。
- [x] 更新 Coding Core、项目发现、AGENTS Bootstrap、managed/template assets 和 USAGE。
- [x] 保持 Runtime binary 为机械安装器，不新增语义扫描实现；canonical Project Payload 安装行为由永久测试覆盖。
- [x] 完成独立 Review、Review Red/Green、Progressive Disclosure 修复、Router→Governance 顺序修复与最终 re-review。
- [x] pre-Ready run `33299971593` 完成 180 tests、三平台 Runtime 和真实 project install；唯一失败为 `proposed` Ready Gate。
- [x] Final Ready run `33300086948` 三个 Job 全部 Green；Draft PR #54 因连接器 GraphQL schema 缺陷关闭且未合并，已创建非 Draft PR #55。
- [ ] 非 Draft PR #55 最终 HEAD 永久 CI 全绿后正常合并；main fresh CI 后删除 Active Change。

# 独立 Review

Review Target：`main@e9eb57451629cf1f2cf767e3229f1601c31585b3 → feat/project-governance-bootstrap`。

模式：review-and-fix。

重点风险：

- Runtime binary 是否被错误扩展成第二个 Coding Agent；
- 自然语言首次任务能否稳定进入宿主大模型治理，而不是要求用户记内部命令；
- 已有 AGENTS 的规范性规则是否会被当前错误实现反向覆盖；
- 只读任务是否会因首次治理而被错误阻断或越权写文件；
- fixed template 是否变成固定技术栈模板或强制已有 AGENTS 重排；
- project governance 状态是否错误放入 installer managed ownership；
- managed block 是否先进入唯一 Router，再由 Coding 加载 ref12；
- Core 是否因详细规则膨胀，破坏 Progressive Disclosure；
- USAGE 是否是最终用户操作说明而不是泄漏内部维护 Contract。

Review 修复证据：

1. Review Red `33299634725`：179 tests 中只有 4 个失败，分别是只读继续、USAGE 强度/Greenfield 范围和既有 Coding Core `<=680` 行门禁；其他回归通过。
2. 修复后把详细规则继续留在 ref12，Coding Core 只保留硬触发；只读首次任务继续原始只读任务；USAGE 改为首次接入任意项目均应先治理。
3. re-review 发现 managed block 的 Router/治理顺序自引用，新增顺序回归；Router-order Red `33299930033` 为 180 tests 中唯一失败。
4. 修复为“项目规则 → 唯一 Router → Project Governance Bootstrap → Skill/Reference 路由”，不改变 Runtime Contract。
5. pre-Ready `33299971593` 自包含测试和产品链全部 Green。

最终结论：`NO_FINDINGS_WITHIN_SCOPE`。

# 文档影响

- `USAGE.md` 是本次最终用户主要说明：明确安装与项目治理是两个阶段，并给出首次接入、直接自然语言开发和日常开发的操作方式。
- 不新增第二份用户手册；根 README / runtime README 职责不变。

# Contract / Schema / Migration / 依赖

- Routing metadata / Stable Reference ID：不变；ref12 继续使用 `coding.reference.13` 与现有 `项目 Bootstrap` 路由意图。
- Runtime / Project Payload / install manifest / MCP Tool Contract：schema 与实现不变；canonical Skill/asset 正文变化会自然改变下一次构建 digest。
- Schema / Migration / 数据：无。
- 依赖：无。

# 交付

- Branch：`feat/project-governance-bootstrap`
- Draft PR #54：关闭且未合并；Draft → Ready 因已连接 GitHub 工具 GraphQL schema 缺陷失败。
- 非 Draft PR：#55，当前正式交付入口。
- Release：本任务不创建正式 Release
