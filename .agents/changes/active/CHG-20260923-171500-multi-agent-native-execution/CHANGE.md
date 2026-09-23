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

- **要解决的问题**：#298/#299 已建立多 Agent Policy，但目标项目安装后二进制只配置治理/MCP，没有把目标项目 Bootstrap 与四宿主 native delegation execution surface 确定性接通。
- **拟议修改**：增加唯一 Role Manifest，由 installer 自动投影 Codex / Claude Code / Cursor custom agents 与 DeepSeek Harness subagent execution overlay，并强化目标项目 AGENTS Bootstrap；保持 Router 不调度、专业 Skill 不复制。
- **预期结果**：运行 binary 后，目标项目自动具备宿主可发现/可调用的五角色多 Agent 执行层；只有具备真实独立价值的工作才拆，宿主不支持时明确降级为单 Agent 正常执行。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #302。用户明确要求运行 Agent_Skills 二进制后自动完成目标项目 AGENTS 改造和多 Agent execution layer 安装，并在验证、Review、CI 与 post-merge 门禁全部满足后合并 main。

## 当前现状

- installer 已安装 Runtime Project Payload、目标项目 AGENTS managed block、Codex/Cursor/Claude Code MCP、CLAUDE.md bridge、DeepSeek Harness MCP overlay 和 Windows launcher。
- 目标 AGENTS managed block 未显式导航 `.agents/skills/ENTRY.md`。
- 当前没有 `.codex/agents/agent-skills-*.toml`、`.claude/agents/agent-skills-*.md`、`.cursor/agents/agent-skills-*.md` projection。
- DSH overlay 当前只有 `@deepseek-ai/dsh-mcp-client`，没有 `ctx.subagents` service/provider/model-facing delegation tool。
- Codex / Claude Code / Cursor / DSH 当前官方实现都存在原生 subagent surface；DSH base bundle 已包含本次需要的 subagent service/spawn/tool/control packages。

## 问题、根因或约束

根因是上一 Change 只完成了 **Policy**，但 Completion Evidence 没有把 **Host Execution Adapter** 作为独立边界。安装 Value Gate 文本只能告诉模型“应该拆”，不能证明宿主存在可发现、可调用的角色 agent/provider。

同时必须保持两个约束：
1. 角色语义不能在四个宿主复制成四套 canonical truth；
2. installer 不能为了执行层覆盖用户自有同名配置，也不能在失败时留下半安装状态。

## 不修改的后果

复杂任务即使命中 MUST_SPLIT，也可能因为宿主没有发现角色定义或 DSH 没有 provider/tool 而继续单 Agent。不同宿主能否拆分依赖临场能力，且测试最多证明 Markdown/Runtime Core 存在，不能证明 binary 安装后的 native execution surface。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | main 基线为 `cf258a69e66a334bf39660e17e73a4b6f65d9233` | GitHub main readback | 本 Change 从最新 main 建立 |
| E2 | installer 当前只生成 MCP / CLAUDE.md / DSH MCP overlay，没有 native role agent files | `runtime/agent_skills_runtime/project_installer.py` main | 必须新增 execution projection |
| E3 | `AGENTS.managed.md` 不含 `.agents/skills/ENTRY.md` | current main asset | 必须补稳定 Bootstrap |
| E4 | Codex 当前支持 AGENTS/Skill instruction 触发 delegation 与 project `.codex/agents/*.toml` | OpenAI official docs，2026-09-23 核验 | Codex 使用 native projection |
| E5 | Claude Code project subagents 位于 `.claude/agents/*.md`，child 不继承主会话 system prompt | Anthropic official docs，2026-09-23 核验 | child prompt 必须自带项目治理入口 |
| E6 | Cursor project subagents 位于 `.cursor/agents/*.md`，支持 readonly/background/parallel | Cursor official docs，2026-09-23 核验 | Cursor 使用 native projection |
| E7 | DSH base 当前已依赖 subagent service/spawn/tool/control，spawn provider 名为 `spawn` 且支持 continuable | DeepSeek Harness official source，2026-09-23 核验 | DSH 无需在线装包即可接 execution overlay |
| E8 | #302 已给出 AC1-AC14 | GitHub Issue #302 live readback | 本 Change Requirement Traceability Owner |

## 推断与待确认

- 待 CI 确认新增 projection 后，现有 Runtime Project Payload/install-state/three-platform onefile package 仍兼容。
- CI 不启动需要真实账号/模型的 Codex、Claude Code、Cursor 或 DSH 对话，因此最终验证边界是“宿主原生 execution surface 已按当前官方 schema 安装并可被宿主发现/调用”，不能夸大为真实模型已经成功生成 child run。

# 目标、成功标准与非目标

## 目标

运行当前 Agent_Skills onefile binary 后自动建立目标项目 Multi-Agent Bootstrap 和四宿主原生执行层，同时保持价值驱动拆分、权限边界、写入隔离、用户文件保护、幂等升级和安装事务回滚。

## 成功标准

- [ ] #302 AC1-AC12 由当前实现、永久回归和文档直接覆盖。
- [ ] #302 AC13 的独立 Review、final reviewed head required CI、Linux/Windows/macOS package 全绿。
- [ ] #302 AC14 的 guarded merge、main-fresh、Change Archive、Issue Closure 和任务分支 cleanup 全部完成。

## 范围

- 目标项目 AGENTS managed bootstrap。
- canonical Multi-Agent Role Manifest。
- Codex / Claude Code / Cursor / DeepSeek Harness execution projection。
- installer ownership/preflight/snapshot/write/rollback。
- Project Payload / Runtime package 相关回归。
- USAGE.md 与 runtime/README.md 的真实安装行为同步。
- 本次 GitHub Requirement / Change / Review / CI / Delivery 闭环。

## 非目标

- 不创建 Planner、Scheduler、常驻 Worker Queue。
- 不固定每个任务启动五个 Agent。
- 不固定模型 ID、reasoning effort 或并发数量。
- 不让角色文件复制 Coding / Testing / Review / Research / Figma 的完整专业方法。
- 不在安装时联网下载 Codex / Claude Code / Cursor。
- 不通过 pnpm/npm 在线安装 DSH subagent package；只使用当前 DSH base 已提供的 package。
- 不新增 MCP Tool。
- 不修改 AIMA_UGC。
- 不创建 Runtime Release / Deploy。

## 必须保持不变

- Router Anti-Agent Boundary。
- 专业 Skill ownership。
- 现有 MCP Tool Contract、License Contract、Release ZIP schema 和 `agent-skills-project-payload/v2`。
- marker 外目标项目 AGENTS/CLAUDE/host config 内容。
- 用户无法证明 ownership 的同名 custom agent 文件。
- installer 原有 sidecarless ownership、Project Payload integrity 和原子 rollback 语义。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Role Manifest 是五角色事实唯一 Owner；host renderer 只做投影 | #302 / AC2；E4-E7 | 防止四套角色规则漂移 |
| 接口与契约 | 新增 target-side host execution files / DSH rows，不新增 MCP Tool | #302 / AC3-AC10 | Project install observable surface 扩展 |
| 数据与迁移 | 无业务数据 / Schema / Migration | #302 范围 | 不适用数据迁移 |
| 错误与失败语义 | unowned same-name host file 在任何 mutation 前 fail closed；写入失败整体 rollback | #302 / AC8-AC9 | 保护用户资产，不留半安装 |
| 兼容性 | namespaced projection；旧 Runtime ownership 仍按现有 install-state 恢复 | E2；#302 / AC8-AC10 | 保持既有升级链 |
| 部署与回滚 | 本 PR 只合并源码；未来 binary install 使用同一事务回滚 | 用户授权；#302 | 无 Release/Deploy |

# 修改方案与决策依据

## 最小充分方案

1. 新增 JSON Role Manifest，stdlib 校验 Explorer / Researcher / Worker / Tester / Reviewer 的 ID、description、mode、background、instructions。
2. 新增 `host_agent_projection.py`，只从 Role Manifest 生成：
   - Codex namespaced TOML custom agents；
   - Claude Code namespaced Markdown subagents；
   - Cursor namespaced Markdown subagents；
   - DSH role-tool fragments。
3. `AGENTS.managed.md` 增加 ENTRY + Multi-Agent Bootstrap；每个 role prompt 也明确重新读取当前项目 `AGENTS.md` 和 `.agents/skills/ENTRY.md`。
4. installer 在 mutation 前对全部新 host projection 做 ownership/collision preflight，并纳入 snapshot/write/rollback/新建空目录 cleanup。
5. DSH overlay继续保留 Agent_Skills MCP，同时增加 subagent service、spawn provider、五个角色 delegation tool、control 和 list-agents；Worker 不默认后台并发写。
6. 先取得 Red：当前实现必须因 native execution files / bootstrap 缺失失败；再实现 Green。
7. targeted 更新 USAGE/runtime README，说明安装行为、宿主发现限制和 fallback。
8. 完成独立 Review、Ready、current-head CI、三平台 package、guarded merge 和 post-merge closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用 |
| --- | --- | --- |
| D1 | E3-E6 | 显式项目 Bootstrap + native project agents 是跨宿主最稳定、可审查入口 |
| D2 | E7 | DSH base 已提供全部 package，不需要破坏离线/确定性安装 |
| D3 | E2 | installer 已有 marker/collision/snapshot/rollback 基础，应扩展同一事务而非新增第二个安装器 |
| D4 | #302 / AC2 | 单一 Role Manifest 比四套手写 prompt 更能保证语义同源 |

## 备选方案与取舍

- **只继续加 Markdown Policy**：无法证明 execution surface，正是当前缺口，不采用。
- **四宿主分别手写五角色规则**：短期简单但必然形成语义漂移，不采用。
- **DSH 安装时执行 pnpm/npm add**：引入网络、版本和副作用，不必要，因为 E7 已确认 base 包含所需 package，不采用。
- **默认并行多个 Writer**：会放大共享文件/Contract 冲突，违背价值驱动拆分；Worker 仍受单 Writer / 隔离门禁约束。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AGENTS Bootstrap | #302 / AC1 | not_satisfied | 待实现与测试 |
| R2 | 单一 Role Manifest | #302 / AC2 | not_satisfied | 待实现与测试 |
| R3 | Codex execution projection | #302 / AC3 | not_satisfied | 待实现与测试 |
| R4 | Claude Code execution projection | #302 / AC4 | not_satisfied | 待实现与测试 |
| R5 | Cursor execution projection | #302 / AC5 | not_satisfied | 待实现与测试 |
| R6 | DSH execution overlay | #302 / AC6 | not_satisfied | 待实现与测试 |
| R7 | Value Gate → native execution / fallback | #302 / AC7 | not_satisfied | 待实现与测试 |
| R8 | ownership / idempotency / collision | #302 / AC8 | not_satisfied | 待实现与测试 |
| R9 | installation rollback | #302 / AC9 | not_satisfied | 待实现与测试 |
| R10 | Runtime/MCP/License/schema compatibility | #302 / AC10 | not_satisfied | 待回归 |
| R11 | permanent regression | #302 / AC11 | not_satisfied | Red 测试已提交但尚未真正执行 |
| R12 | USAGE / discovery / fallback docs | #302 / AC12 | not_satisfied | 待同步 |
| R13 | Review / current-head CI / three-platform package | #302 / AC13 | not_satisfied | Delivery Gate |
| R14 | merge / main-fresh / archive / closure / cleanup | #302 / AC14 | not_satisfied | Delivery Gate |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| `.agents/skills/coding/assets/AGENTS.managed.md` | 增加 ENTRY + Multi-Agent Bootstrap | 建立目标项目稳定入口 | R1/R7 |
| `.agents/skills/coding/assets/multi-agent-roles.json` | canonical 五角色 manifest | 单一事实源 | R2 |
| `runtime/agent_skills_runtime/host_agent_projection.py` | validator + four-host render | native execution adapters | R2-R8 |
| `runtime/agent_skills_runtime/project_installer.py` | preflight/install/rollback + DSH execution | 自动安装执行层 | R3-R10 |
| `.agents/skills/coding/tests/test_multi_agent_execution_install.py` | Red→Green end-to-end install regression | 证明安装产物而非文案 | R1-R11 |
| 现有 installer/DSH tests | 校准新行为与旧不变量 | 防回归 | R8-R11 |
| `USAGE.md` / `runtime/README.md` | targeted 同步安装/宿主发现事实 | 用户说明 | R12 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的验证矩阵
- [ ] 行为变化建立有效 Red Evidence
- [ ] 完成最小实现，不静默扩大范围
- [ ] 同步受影响长期文档
- [ ] 取得 current-head 新鲜验证
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Role Manifest validator、host renderers |
| 接口 / 契约 | required | Codex/Claude/Cursor schema、DSH rows、markers、AGENTS Bootstrap |
| 集成 / 持久化 / 运行依赖 | required | installer first/reinstall/upgrade/collision/rollback |
| 用户 / 工作流验收 | required | binary install 后 target tree、AGENTS 和四宿主配置 |
| 跨组件关键路径 | required | canonical role → Project Payload → installer → host-native execution assets |
| 外部依赖 / 供应方探测 | not_applicable | 官方 current schema 已核验；CI 不启动真实付费模型会话 |
| 构建 / 打包 / 运行 | required | Runtime build、onefile install smoke、Linux/Windows/macOS package |
| 文档 / 治理 / 其他 | required | #302、Change、USAGE/runtime README、Review、CI、post-merge closure |

## 验证计划

- 目标测试：`test_multi_agent_execution_install.py`。
- 相关回归：single-binary install、DeepSeek Harness host config、Runtime Project Payload/projection、install-state、rollback。
- 静态检查或构建：repository-native compile/semantic tests。
- 专项真实边界：不执行付费模型 Provider Probe；宿主 schema 以 2026-09-23 官方 owner 文档为证据。
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | host schema 漂移、user-owned same-name collision、rollback 半安装 | current official schema + namespaced markers + preflight + snapshot |
| 兼容性 | 保持现有 Project Payload v2、MCP Tool、License 和项目自有配置；新增 execution projections 是安装可见行为 | #302 / AC8-AC10 |
| 数据 / Migration | 不适用 | 无业务数据/Schema |
| 部署 / 运行 | 后续 Release binary 才向外部项目分发；本任务只源码 merge | 用户授权 |
| 回滚 / 恢复 | Source 可 revert Implementation PR；target install 写失败恢复全部 snapshots | #302 / AC9 |

# 文档、依赖、部署与发布影响

- **长期文档**：USAGE.md 与 runtime/README.md 需要 targeted 同步“binary 自动安装 execution adapters”和宿主发现限制。
- **依赖 / Runtime**：不新增 Python/Node dependency；DSH 只引用 base bundle 当前已内含 package。
- **配置 / Secret**：新增项目级 custom-agent 文件和 DSH overlay rows，不新增 Secret。
- **部署 / Release**：本任务不 Release/Deploy。
- **兼容 / 消费方通知**：下一次正常 Runtime Release/升级后，目标项目会获得新 execution projections；用户自有同名文件发生 collision 时 fail closed。

# 完成审计

- [ ] upstream_re_read：Ready 前重新读取 live #302、current head installer/assets/tests/docs 与当前官方宿主 schema。
- [ ] change_coverage：逐项映射 AC1-AC14，不能由本 Change 自证。
- [ ] reverse_audit：从 binary install → AGENTS/Role Manifest → host projection → native discovery/delegation → fallback → rollback 反向审计。
- [ ] unresolved_cleared：R1-R12 在 Ready 前清零；R13/R14 downstream Delivery Gate 有明确边界。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main `cf258a69` | canonical installer/assets + current official host docs readback | confirmed | 当前 execution gap 与 host schema |
| V2 | PR #303 head `392aabc5` / Skill Tests #1837 | Verify PR Requirement Source | failed before tests because Change headings were noncanonical | 不是 Red Evidence；仅证明 Change 文档需先符合机器 Contract |
| V3 | Issue #302 live contract | current Technical Change Form readback + Issue update | required `当前状态 / 兼容与迁移 / 风险与回滚 / 上游事实源` 已补齐 | Requirement Source 已满足当前机器语义段，下一 run 可以进入真实 Red tests |

## 未验证内容与剩余风险

- Red 测试尚未真正执行，因此不能把 #1837 当行为失败证据。
- 当前聊天宿主没有 subagent execution interface，本次开发按单 Agent fallback 执行，不冒充实际 delegation。

## 交付状态

- 提交：Change + Red test 已在 `tech/multi-agent-native-execution`。
- 拉取请求：Draft PR #303。
- CI：#1837/#1838 均在测试前暴露 Requirement/Change 机器契约缺口；当前 Issue/Change 已按正式模板补齐，下一 head 重新取得有效 Red。
- 合并：未执行。
- Change 归档：未执行。
- 发布 / 部署：不适用，本任务明确只合并源码 main。

## 备注

无。
