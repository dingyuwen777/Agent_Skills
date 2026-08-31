---
schema: coding-change/v1
id: CHG-20260831-runtime-silent-control-plane
title: Runtime 用户可见进度隐藏内部治理控制面
level: L3
status: in_progress
owner: dingyuwen777
branch: change/runtime-silent-control-plane
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - runtime-distribution
  - project-bootstrap
  - router
  - tests
affected_paths:
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/ENTRY.md
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/tests/test_runtime_progress_privacy.py
contracts:
  - runtime-user-visible-disclosure
data_changes: []
---

# 目标

强化 Runtime Mode 的用户可见信息披露边界：保留真实工程处理过程，但把 Skill 发现/选择/加载、Router 判断、Reference 解析/加载、Task Route、MCP required Context 加载等治理控制面变成静默内部过程，不再主动转写成用户可见进度。

# 成功标准

- [ ] Runtime 安装到目标项目后的最早 managed 入口，在任何内部路由/上下文加载前就明确建立“控制面静默”规则。
- [ ] progress update、commentary、tool preamble、intermediate summary、final response、error explanation 等所有 Agent 可控制的用户可见文本都受同一披露边界约束。
- [ ] 明确禁止“已读取/已加载/命中某 Skill”“Router 将任务路由为……”“正在加载某 Reference/治理文件/required Context”等模型生成播报。
- [ ] 继续允许展示项目调查、需求/风险判断、代码修改、测试、文档同步、Review、Git/CI、Release 与交付状态。
- [ ] Router 明确 Runtime Mode 的 Skill 选择、required Context 和 Handoff 输出只属于内部控制面，不等于用户可见进度；Source Mode 维护者仍可正常查看和讨论这些事实。
- [ ] Runtime canonical 规范明确模型可控文本与宿主 UI 自动活动标签的边界，不宣称 Prompt/Skill 能隐藏宿主自身 UI。
- [ ] Project Payload、Runtime Bundle、MCP Contract、安装 ownership、动态 Skill Catalog、canonical Reference exact-text/hash 语义不变。
- [ ] self-contained 回归测试与适用 CI 全绿。

# 范围

- 强化目标项目 managed block 中的 Runtime 用户可见过程规则，并确保其从读取该 block 起立即生效。
- 在共享 Entry 中增加 Runtime Mode 的静默控制面早期提醒，不扩张为第二套 Router。
- 在 Router 的 Anti-Agent Boundary 中澄清 Runtime Mode 的内部输出不能转写为用户进度播报。
- 同步 Runtime canonical 分发/信息披露规则，补充允许/禁止表达和宿主 UI 边界。
- 新增 preservation/behavior tests，验证分发到 Project Payload 的 managed block 与共享入口/Router/canonical 规则保持一致。

# 非目标

- 不改为 AGENTS + MCP 单入口架构。
- 不移除 Runtime Project Payload 中的 Entry、Router 或专业 Skill Core。
- 不修改 Runtime Python 实现、MCP Tool Contract、Task Route schema、Routing Manifest、Bundle 加密、Stable ID、source/routing/payload digest 或安装 manifest。
- 不隐藏目标项目自己的代码、测试、文档、配置、Git/CI 路径或真实工程过程。
- 不承诺隐藏 Codex/Cursor/Claude 等宿主 UI 自身自动生成的 Skill/Tool 活动标签；本 Change 只约束 Agent/Prompt/Skill/Runtime 能控制的用户可见文本。

# 必须保持不变

- Source Mode 维护者可以正常查看和讨论 Skill、Reference、路径、Stable ID、路由和加载事实。
- Runtime Mode 仍使用当前 Shared Entry + Native Router/专业 Core + Project-local MCP Runtime + Encrypted Canonical References 架构。
- 完整 canonical Context 不因用户可见保密而删改正文、routing metadata、Stable ID 或原始字节。
- 项目事实优先、required Context fail-closed、权限边界、Change/Review/CI/PR/Release 门禁保持不变。
- 用户可见过程仍可以解释真实工程步骤本身的原因和验证证据。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Runtime 用户可见过程不再主动播报 Skill 名称、文件/目录或内部路由/加载明细 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | not_satisfied | 待 Red/Green 实现验证。 |
| R2 | 控制面静默规则必须在第一次用户可见进度更新前生效 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | not_satisfied | 待强化最早 managed/Entry 入口并验证。 |
| R3 | Router 的内部选择/Handoff 不得被解释成用户可见进度 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | not_satisfied | 待 Router 边界修正并回归。 |
| R4 | 真实工程调查、修改、测试、文档、Review、Git/CI/交付过程继续可见 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | not_satisfied | 待规则与测试同时证明允许面未被误伤。 |
| R5 | Source Mode 可讨论内部事实，且不宣称能隐藏宿主 UI 自动活动标签 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | not_satisfied | 待 canonical 规范明确模式/宿主边界。 |
| R6 | Runtime/Project Payload/MCP/Bundle/安装语义不变 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | not_satisfied | 待完整回归与 changed-scope CI。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / 完成证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新增 self-contained 文本/Project Payload preservation 测试，先 Red 后 Green。 |
| 接口 / Contract | required | `runtime-user-visible-disclosure`：managed/Entry/Router/canonical 规则的 Runtime/Source Mode 边界一致。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改数据库、持久化或 Runtime Python 依赖交互；若 CI changed scope 触发安装/Runtime 包验证，则按现有 workflow 执行。 |
| 用户 / Workflow Acceptance | required | 从 Runtime 用户可见过程角度检查禁止与允许表达，确保工程过程仍可正常播报。 |
| 跨组件 Golden Path | required | canonical 规则 → Project Payload managed/shared Core → 目标项目最早入口的披露边界可达性。 |
| 外部依赖 Probe | not_applicable | 不依赖第三方 Provider 或外部系统事实。 |
| Build / Package / Runtime | required | Project Payload 构建/分发 preservation；若永久 CI 判定 Runtime Package Tests 适用，则接受三平台实际验证。 |
| Docs / Governance / Other | required | Change、内容守恒 Review、当前引用和正式 Runtime canonical 规则一致性检查。 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取 Issue #100 与当前 main 的实际披露/分发规则。
- [ ] change_coverage：R1–R6 全部有实现与新鲜证据。
- [ ] reverse_audit：从用户看到的进度反向追踪到最早入口、Router/Handoff、required Context 加载与允许工程播报，确认无泄露缺口。
- [ ] unresolved_cleared：没有 not_satisfied、TBD/TODO 或未解释的验证缺口。

# 任务

- [x] 读取当前 main 的 AGENTS、Maintenance、Entry、Router、Coding、Runtime 分发与内容守恒规则。
- [x] 创建 Requirement Source Issue #100 与 L3 Change。
- [ ] 新增 Runtime 进度披露目标测试并取得 Red。
- [ ] 最小修改 managed/Entry/Router/Runtime canonical 规则取得 Green。
- [ ] 执行完整 self-contained tests 与适用 changed-scope CI。
- [ ] 执行 Requirement Review、内容守恒/安全边界 Review 与 Completion Audit。
- [ ] 创建普通非 Draft PR，取得 final-head fresh CI 后用 expected_head_sha 合并。
- [ ] main fresh CI 成功后独立归档 Change。

# 文档影响

本 Change 修改的是 Agent/Runtime canonical 治理规则与安装到目标项目的 managed 入口，不新增独立人类手册。`USAGE.md` 不承担内部进度披露细则，本轮默认不修改；若实施中发现最终用户操作步骤发生变化，再按事实同步。

# Git / PR / 发布状态

- Requirement Source：Issue #100。
- 分支：`change/runtime-silent-control-plane`。
- PR：尚未创建。
- Merge：尚未执行。
- Release：本 Change 不创建新版本，只进入下一次正常 Release 的 Project Payload/canonical 内容。
