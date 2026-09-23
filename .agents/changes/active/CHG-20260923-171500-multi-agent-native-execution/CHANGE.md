---
schema: coding-change/v1
id: CHG-20260923-171500-multi-agent-native-execution
title: 安装多 Agent 原生执行层与项目 Bootstrap
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/multi-agent-native-execution
created: 2026-09-23
updated: 2026-09-23
completion_gate: required
depends_on: []
affected_areas:
  - governance
  - coding
  - runtime
  - project-payload
  - project-installer
  - host-adapters
  - tests
  - docs
affected_paths:
  - .agents/skills/coding/assets/
  - runtime/agent_skills_runtime/
  - .agents/skills/coding/tests/
  - USAGE.md
  - runtime/README.md
contracts:
  - target-project AGENTS managed bootstrap
  - Multi-Agent Role Manifest
  - Codex project custom agents
  - Claude Code project subagents
  - Cursor project subagents
  - DeepSeek Harness ctx.subagents execution overlay
  - agent-skills-project-payload/v2
data_changes: []
---

# 变更摘要

- 要解决的问题：#298/#299 已建立多 Agent Policy，但目标项目安装后二进制只配置 MCP，没有把 AGENTS → ENTRY → Value Gate 与四宿主 native delegation execution surface 确定性接通。
- 拟议修改：增加唯一 Role Manifest，由 installer 自动投影 Codex/Claude/Cursor custom agents 与 DSH subagent tools，并强化目标项目 AGENTS Bootstrap；保持 Router 不调度、专业 Skill 不复制。
- 预期结果：运行 binary 后目标项目直接具备宿主可发现的五角色多 Agent 执行层；值得拆且宿主支持时可以真实 delegation，不支持时正常单 Agent。

# 背景、现状与问题

Requirement Source：GitHub Issue #302。

当前已确认：
- installer 已安装 Runtime Project Payload、MCP 配置、目标 AGENTS managed block、CLAUDE.md bridge 和 DSH launcher；
- 目标 AGENTS managed block 未显式导航 .agents/skills/ENTRY.md；
- 当前没有 .codex/agents/agent-skills-*、.claude/agents/agent-skills-*、.cursor/agents/agent-skills-* projection；
- DSH overlay 当前只有 dsh-mcp-client，没有 ctx.subagents service/provider/model-facing tool；
- 当前 Codex / Claude Code / Cursor / DSH 官方实现都存在原生 subagent surface，且 DSH base bundle 已含本次需要的 subagent packages。

真正问题是 Policy 与 Execution Adapter 被错误等同。仅安装 Value Gate 文本不能证明宿主具有可调用的角色 agent/provider。

# 事实与证据

| 证据 | 已确认事实 | 来源 |
| --- | --- | --- |
| E1 | main 基线 cf258a69e66a334bf39660e17e73a4b6f65d9233 | main readback |
| E2 | installer 只生成 MCP / CLAUDE.md / DSH MCP overlay | project_installer.py |
| E3 | AGENTS.managed.md 不含 .agents/skills/ENTRY.md | current main |
| E4 | Codex 支持 AGENTS/Skill delegation 与 .codex/agents/*.toml | OpenAI official |
| E5 | Claude Code 支持 .claude/agents/*.md，child 不继承主 system prompt | Anthropic official |
| E6 | Cursor 支持 .cursor/agents/*.md、readonly/background/parallel | Cursor official |
| E7 | DSH base 含 subagent service/spawn/tool/control，spawn 支持 continuable | DeepSeek Harness official |

# 目标与非目标

目标：
- binary 安装自动建立 AGENTS Bootstrap + 四宿主原生多 Agent execution layer；
- 五角色只有一个 canonical role source；
- Host 支持时 MAY/MUST 可实际委派，MUST 必须委派；无能力时明确单 Agent fallback；
- installation ownership/collision/rollback 保持安全。

非目标：
- 不创建 Planner/Queue；
- 不固定每个任务启动五个 Agent；
- 不固定模型或并发数；
- 不联网安装 Codex/Claude/Cursor 或 DSH npm package；
- 不新增 MCP Tool；
- 不修改 AIMA_UGC；
- 不 Release/Deploy。

必须保持：
- Router Anti-Agent Boundary；
- Coding/Testing/Review/Research/Figma ownership；
- MCP/License/Project Payload schema；
- marker 外用户项目规则和用户自有同名文件。

# 方案

1. 新增 JSON Role Manifest，stdlib 校验 Explorer / Researcher / Worker / Tester / Reviewer。
2. 新增 host_agent_projection.py，从单一 manifest 渲染 Codex/Claude/Cursor 角色文件和 DSH role tool 配置。
3. AGENTS managed block增加 ENTRY + Multi-Agent Bootstrap；角色 prompt也要求重读 AGENTS/ENTRY。
4. installer 在任何写入前 preflight host projection ownership/collision，纳入 snapshot、写入、rollback、空目录 cleanup。
5. DSH overlay增加 service、spawn provider、五个 continuable role tools、control 和 list-agents。
6. Red→Green 覆盖 first install/reinstall/upgrade/collision/rollback/Project Payload/三平台 package。
7. targeted 更新 USAGE/runtime README。
8. Review → Ready → current-head CI → guarded merge → main-fresh → archive/closure/cleanup。

# 需求追溯

| 编号 | 来源 | 状态 |
| --- | --- | --- |
| R1 AGENTS Bootstrap | #302 / AC1 | not_satisfied |
| R2 Role Manifest | #302 / AC2 | not_satisfied |
| R3 Codex projection | #302 / AC3 | not_satisfied |
| R4 Claude projection | #302 / AC4 | not_satisfied |
| R5 Cursor projection | #302 / AC5 | not_satisfied |
| R6 DSH execution | #302 / AC6 | not_satisfied |
| R7 Value Gate → execution/fallback | #302 / AC7 | not_satisfied |
| R8 ownership/idempotency/collision | #302 / AC8 | not_satisfied |
| R9 rollback | #302 / AC9 | not_satisfied |
| R10 protocol compatibility | #302 / AC10 | not_satisfied |
| R11 permanent regression | #302 / AC11 | not_satisfied |
| R12 docs | #302 / AC12 | not_satisfied |
| R13 Review/CI/package | #302 / AC13 | not_satisfied |
| R14 merge/post-merge | #302 / AC14 | not_satisfied |

# 验证矩阵

| 层 | 要求 |
| --- | --- |
| 行为/单元 | required：manifest validator / renderers |
| 接口/契约 | required：host schema / markers / AGENTS bootstrap |
| 集成 | required：installer first/reinstall/upgrade/rollback |
| 用户工作流 | required：binary install 后 target tree |
| 跨组件 | required：role → payload → installer → four hosts |
| 外部真实模型 | not_applicable：不在 CI 启动付费宿主模型 |
| 构建/打包 | required：Runtime + Linux/Windows/macOS onefile |
| 治理 | required：#302/Change/Review/CI |

# 风险与回滚

主要风险：host schema 漂移、同名 user file collision、rollback 半安装。
处理：官方 schema 校准、namespaced marker、preflight fail closed、transaction snapshot。
回滚：revert PR；项目安装失败恢复 snapshots。

# 执行状态

- [x] 当前事实和官方宿主能力已核验
- [x] Requirement Source 已建立
- [x] 任务分支已建立
- [ ] Red Evidence
- [ ] 实现
- [ ] 文档
- [ ] Review / CI
- [ ] merge / main-fresh / archive / closure / cleanup

# 新鲜证据

| 证据 | 结果 |
| --- | --- |
| V1 main cf258a69 | 当前缺口与四宿主官方 schema 已确认 |

当前聊天宿主没有 subagent execution interface，本次开发实际按单 Agent fallback 执行，不冒充已拆分。
