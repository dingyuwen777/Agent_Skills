---
schema: coding-change/v1
id: CHG-20260906-141857-user-doc-boundary
title: 重划 README 与 USAGE 的受众和使用说明边界
level: L2
status: active
owner: dingyuwen777
branch: docs/reorganize-readme-usage-227
created: 2026-09-06
updated: 2026-09-06
completion_gate: required
depends_on: []
affected_areas:
  - documentation
  - release-user-guide
affected_paths:
  - README.md
  - USAGE.md
contracts:
  - README.md 继续作为维护者源码仓库入口
  - USAGE.md 继续作为 Release 随包人类说明，但只面向已完成接入后的普通开发者日常使用
  - Release ZIP 成员结构、Runtime/MCP/路由协议与专业 Skill 语义保持不变
data_changes: []
---

# 目标

把维护/接入知识与普通开发者日常使用说明彻底分开：README 承担维护者需要的分发、安装、首次治理、升级/回退、自检与网页 Source Mode；USAGE 假设目标项目已经完成接入和首次治理，只告诉普通开发者如何在 Codex、Cursor、Claude Code 等桌面 AI Agent 中完成典型研发任务。

# 成功标准

- [ ] README 明确维护者受众，并承接 USAGE 中仍有效的安装、首次治理、状态/自检、升级/回退和网页端说明。
- [ ] USAGE 不再暴露 binary、Runtime、MCP、Source Mode、网页端、首次治理/AGENTS 校准、安装升级回退等内部接入信息。
- [ ] USAGE 给出功能开发、Bug、重构、测试/黑盒、Review、Review+Fix、文档、Figma/Design-to-Code、PR Ready、完整交付等典型桌面 Agent 使用示例。
- [ ] 不修改 Runtime/Release/Skill/Reference/CI 产品语义；文档链接和当前事实保持正确。
- [ ] PR required checks、两阶段 Review、main fresh、原生 Change Archive、Issue 验收与关闭全部按仓库现有门禁完成。

# 范围

仅修改根 README.md、USAGE.md 和本 Change 载体。对现有内容做职责迁移、去内部披露和读者任务重组；不改业务执行代码或 Runtime 协议。

# 非目标

不发布 Release/tag；不改变 Release ZIP 成员；不修改 Runtime、MCP Tool、Router、Skill、Reference、CI 或安装器实现；不修改任何目标业务项目。

# 必须保持不变

项目事实优先、权限与授权边界、Review/Testing/Docs/Figma/Coding 的现有专业语义、PR/CI/guarded merge/main-fresh/Change Archive/Requirement Closure 责任保持不变。普通开发者文档只隐藏治理实现细节，不隐藏真实项目调查、修改、测试、文档、Review、Git/CI 和交付结果。

# 关键决策

- `README.md` 是维护者/管理员入口，可以描述 Agent_Skills 源仓库、Release、binary、Runtime、首次治理和 Source Mode。
- `USAGE.md` 的前提是项目已经配置完成；不要求普通开发者知道或维护 Agent_Skills 本身，只提供面向桌面 AI Agent 的自然语言研发用法。
- 安装/首次接入等知识从 USAGE 移除前必须在 README 有等价或更清晰承载，避免知识丢失。
- 本次是文档职责调整，按当前 classifier 预期为 content scope；不因 USAGE 随 Release 分发就修改 package/runtime 机制。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | README 承担 binary 安装与首次治理等维护/接入说明 | #227 / AC1 | not_satisfied | 待修改 README 并验证内容覆盖 |
| R2 | USAGE 仅面向已接入项目的普通桌面 Agent 开发者，不暴露内部接入实现 | #227 / AC2 | not_satisfied | 待重写 USAGE 并做敏感主题反查 |
| R3 | USAGE 覆盖典型开发场景与可直接复制的自然语言示例 | #227 / AC3 | not_satisfied | 待重写并做读者任务审查 |
| R4 | 不制造第二套工程规则，不改变现有治理/Runtime/Release 产品语义 | #227 / AC4 | not_satisfied | 待 diff、Docs Review 与 CI 证明 |
| R5 | 完成文档验证、required CI、Review、merge 与 post-merge closure | #227 / AC5 | not_satisfied | 由 PR/main/Archive/Issue 平台证据完成 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 预期证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 当前 content scope 的自包含 Skill/文档回归，证明导航和内容契约未破坏 |
| 接口 / 契约 | required | Release/Runtime/路由协议与文件结构无 diff；USAGE/README 职责语义人工对照 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改 Runtime 执行或业务持久化 |
| 用户 / 工作流验收 | required | 从普通开发者视角检查典型场景是否可直接在桌面 Agent 使用，且无需内部知识 |
| 跨组件关键路径 | not_applicable | 无生产组件接线变化 |
| 外部依赖 / 供应方探测 | not_applicable | 不调用外部 Provider 或在线模型 |
| 构建 / 打包 / 运行 | not_applicable | 无 package/runtime 机制变化；正式 required CI 仍按 classifier 决定实际 scope |
| 文档 / 治理 / 其他 | required | README/USAGE 链接、读者职责、知识迁移、内部披露反查、Completion Gate 与两阶段 Review |

# 完成审计

- [ ] upstream_re_read：Ready 前重新读取 #227 与当前 README/USAGE，独立重建 AC。
- [ ] change_coverage：逐条证明安装/治理知识已迁入 README，普通使用知识完整留在 USAGE。
- [ ] reverse_audit：从维护者任务反查 README，从普通开发者典型任务反查 USAGE，不出现职责串位。
- [ ] unresolved_cleared：没有残留内部披露、断链、占位或未解决文档冲突。

# 两阶段复核

阶段 A：Ready 前从 Issue #227 和用户本轮要求独立重建文档职责与验收，不把当前 Change/草稿当需求全集。

阶段 B：复核最终 diff、文档事实/链接、Source-of-truth 边界、Release/Runtime 不变项、普通开发者信息披露边界和维护成本；阻塞 Finding 清零后才进入 Ready。

# 验证

当前处于施工阶段。最终只记录本轮实际执行并读取结果的验证、PR CI、main fresh、原生归档和 Issue closure 证据；不提前伪造 Green。