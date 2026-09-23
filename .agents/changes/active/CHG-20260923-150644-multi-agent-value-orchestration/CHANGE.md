---
schema: coding-change/v1
id: CHG-20260923-150644-multi-agent-value-orchestration
title: 多 Agent 价值驱动编排与跨宿主适配
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/multi-agent-value-orchestration
created: 2026-09-23
updated: 2026-09-23
completion_gate: required
depends_on: []
affected_areas:
  - governance
  - coding
  - runtime
  - project-payload
  - host-adapters
  - tests
  - docs
affected_paths:
  - .agents/skills/coding/
  - .agents/skills/router/SKILL.md
  - runtime/agent_skills_runtime/
  - .agents/skills/coding/tests/
  - USAGE.md
contracts:
  - Multi-Agent Orchestration Contract
  - coding.reference.09 collaboration contract
  - Agent Skills Router Anti-Agent Boundary
  - agent-skills-project-payload/v2
  - Runtime project-facing Skill projection
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前多 Agent 规则只覆盖“已并行后的安全协作”，缺少价值驱动的拆分判定、MUST_SPLIT 失败语义、四宿主适配和用户可见编排。
- **拟议修改**：在 Coding Core 建立轻量决策入口，扩展既有 Reference 09 为唯一 Multi-Agent Orchestration Owner，并同步 Runtime projection、USAGE 和必要回归；保持 Router 不承担调度。
- **预期结果**：简单任务继续单 Agent；真正有独立价值的复杂任务按 NO_SPLIT/MAY_SPLIT/MUST_SPLIT 决策，支持的宿主真实委派，不支持时如实 fail-closed，用户能看到 Agent 分工和状态。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #298。用户明确要求按已讨论方案修改 Agent_Skills，并在全部门禁满足后合并主分支。当前任务不授权 Runtime Release、Deploy，也不修改 AIMA_UGC。

## 当前现状

- Router canonical 明确 Anti-Agent Boundary：不创建子 Agent、不拆分/调度任务。
- Coding Reference 09 已规定纵向切片、DAG/frontier、Delegation Contract、并行写隔离、授权边界和父 Agent 集成验证。
- Coding Core 尚未要求在实质性工程任务开始时先判断多 Agent 的独立价值，因此普通任务不会稳定触发 Reference 09。
- Runtime 已支持 Codex、Cursor、Claude Code、DeepSeek Harness 四 Host 的 Agent_Skills 接入，但当前没有统一 multi-agent adapter 语义。
- 官方当前文档确认 Codex、Claude Code、Cursor 与 DeepSeek Harness 都存在原生 subagent/delegation 能力，但能力入口和配置面不同。

## 问题、根因或约束

根因不是“缺少更多 Agent 角色”，而是**决策层缺少统一价值门禁**：是否拆分、何时必须拆、宿主不能拆时如何报告，仍可能由模型临场决定。若直接给每个宿主复制一套完整角色 Prompt，又会形成第二套 Coding/Testing/Review/Research 规则源。

因此需要把职责分成：
- Coding Core：只负责轻量判定入口；
- Reference 09：唯一编排语义 Owner；
- 专业 Skills：继续决定“怎么做”；
- Host Adapter：只负责把已决定的 delegation 映射到宿主原生能力。

## 不修改的后果

复杂任务可能错失并行、上下文隔离和独立复核收益；简单任务也可能被过度拆分，增加 token、延迟和协调成本。不同宿主会出现不同的拆分行为和可见性，且 MUST_SPLIT 无真实能力时可能静默降级为单 Agent。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | main HEAD 基线为 0cb0cc23851e19b579bc8af5ed45ec83f7348391 | GitHub main commit readback | 本 Change 从当前 main 建立 |
| E2 | Router 明确不创建/调度子 Agent | .agents/skills/router/SKILL.md 当前 main | Orchestration 不进入 Router |
| E3 | Reference 09 已有安全并行与 Delegation Contract | .agents/skills/coding/references/09_多人和多智能体并行协作.md 当前 main | 扩展既有 Owner，不新建第二套规则 |
| E4 | Runtime Project Payload 会投影 Coding Skill Core，但排除 canonical references | runtime/agent_skills_runtime/project_payload.py 当前 main | Coding Core 必须包含触发 Reference 09 的最小入口 |
| E5 | Runtime installer 当前接入 codex/cursor/claude-code/deepseek-harness 四 Host | runtime/agent_skills_runtime/project_installer.py 当前 main | Adapter 只需覆盖现有四 Host |
| E6 | Codex 官方建议并行 read-heavy 任务、谨慎并行 write-heavy，并支持项目/Skill 指令触发 delegation | OpenAI Codex Subagents 官方文档，2026-09-23 核验 | 价值门禁与读写隔离有直接宿主依据 |
| E7 | Cursor 官方说明 simple task 的 subagent overhead 可为负，并支持 isolated worktree | Cursor Subagents 官方文档，2026-09-23 核验 | NO_SPLIT 与并行写隔离必须存在 |
| E8 | DeepSeek Harness 通过 ctx.subagents 注册多个 provider，能力是可选 seam | DeepSeek Harness 官方 subagent subsystem，2026-09-23 核验 | DSH 必须 capability-detect，不能假设 provider 存在 |
| E9 | #298 已按 current Technical Change Form 建立 AC1-AC12 | GitHub Issue #298 readback | 稳定 Requirement Source 已建立 |

## 推断与待确认

- 推断：若只修改 canonical Coding Core/Reference/USAGE，不新增 Host 配置文件，则 Runtime 安装代码本身不必改变；需要用 Project Payload/Runtime tests 证明新 Core 能自然进入目标项目。
- 待确认：当前 CI classifier 是否因 Skill/Runtime projection 变化要求三平台 package；最终以 PR head 的实际 required checks 为准，不预判。

# 目标、成功标准与非目标

## 目标

建立跨 Codex、Claude Code、Cursor、DeepSeek Harness 一致的价值驱动 Multi-Agent Orchestration Contract，使复杂工程任务在真实有收益时拆分，并保持专业 Skill、授权、证据和交付治理同源。

## 成功标准

- [ ] #298 AC1-AC11 在 PR head 有直接实现/测试/文档/Review Evidence。
- [ ] #298 AC12 的 pre-merge 部分通过，post-merge main-fresh/archive/closure/cleanup 由 Delivery Gate 完成。
- [ ] Router Anti-Agent Boundary 保持，没有新增 Planner/Queue/长期 Worker 机制。
- [ ] 简单任务明确保持单 Agent，不以“多 Agent”本身作为收益。

## 范围

Coding Core、Reference 09、必要 Router metadata/trigger 校准、Runtime project-facing projection 验证、USAGE 和本次交付治理。

## 非目标

AIMA_UGC rollout；Runtime Release/tag；Deploy；依赖升级；固定模型/并发配置；强制安装第三方 subagent provider；新建任务队列/调度服务；与当前目标无关的 Skill/Runtime 重构。

## 必须保持不变

六个 MCP Tool Contract、License Contract、Release ZIP surface、agent-skills-project-payload/v2 schema、现有四 Host MCP 接入、Router Anti-Agent Boundary、专业 Skill ownership、项目自身更高优先级规则和授权连续性。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Reference 09 是 Multi-Agent canonical Owner；Router 不调度 | E2/E3、#298 AC7 | 避免第二套 Orchestration |
| 接口与契约 | 新增 NO/MAY/MUST、角色/Handoff/Visibility/Adapter 语义；不增 MCP Tool | #298 AC1-AC8 | 规则 Contract 变化，Runtime protocol 不变 |
| 数据与迁移 | 不适用：无数据库/业务数据/Schema | #298 / AC11 | 无 Migration |
| 错误与失败语义 | MUST_SPLIT 缺能力/权限时 fail-closed；MAY_SPLIT 可回退单 Agent并说明 | #298 / AC2/AC6 | 不允许假多 Agent |
| 兼容性 | 简单任务继续单 Agent；现有专业 Skill/Router 保持 | #298 / AC1/AC3/AC7 | 降低协调成本和漂移风险 |
| 部署与回滚 | 只合并 main，不 Release/Deploy；失败可 revert PR | 用户授权、#298 非目标 | 无不可逆运行数据 |

# 修改方案与决策依据

## 最小充分方案

1. 在 Coding Core 增加“Multi-Agent Value Gate”薄入口：先判 NO/MAY/MUST；只有 MAY/MUST/用户显式要求时加载 Reference 09。
2. 扩展 Reference 09，形成完整唯一 Orchestration Contract：独立价值判定、MUST_SPLIT、五角色职责、权限、并发、Visibility、Handoff、Host Adapter、失败边界。
3. 保持 Router Anti-Agent Boundary，仅在必要时校准文字/metadata，不让 Router 执行调度。
4. 通过 Runtime Project Payload / Skill Projection 现有机制分发更新后的 Coding Core；除非证据证明必需，不增加新的宿主配置文件或 sidecar。
5. 更新 USAGE，告诉使用者无需手工分配 Agent；AI 会按价值判定并报告，宿主能力不足会显式说明。
6. 增加最小永久回归，锁定 Source/Runtime Core 中的决策入口与 Router Anti-Agent 不变量；复用现有 Runtime/package tests证明投影未回归。
7. 完成 Review、current-head CI、guarded merge、main-fresh、Change Archive、Issue Closure 和 cleanup。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E2/E3 | 既有 Reference 09 已是多 Agent 协作 Owner，扩展它比新增 Orchestration Skill 更少漂移 |
| D2 | E4 | Runtime 会分发 Skill Core，因此薄 Value Gate 可跨宿主触发详细 Reference，而不复制完整规则 |
| D3 | E6/E7 | 官方能力都强调独立/并行收益与协调成本，NO/MAY/MUST 比“复杂就拆”更稳 |
| D4 | E8 | DSH subagent 是可选 provider registry，Adapter 必须 capability-detect 而非强制假设 |
| D5 | #298 AC3/AC7 | 角色只表达职责和权限，专业执行继续进入既有 Skill |

## 备选方案与取舍

- 新建独立 Orchestration Skill：会与 Router/Coding 协作规则形成新 Owner，并要求所有工程任务额外路由；当前既有 Reference 09 已足以承担，暂不采用。
- 为 Codex/Claude/Cursor 各生成五套 native role 文件：可提高显式角色可发现性，但会复制同一角色语义并扩大 Runtime projection/ownership；当前宿主都可根据项目/Skill 指令创建原生 subagent，先采用薄 Adapter；未来若真实宿主 Evidence 证明需要固定文件，再另建 Change。
- 为 DSH 安装 subagent provider：会新增外部依赖和具体 provider 决策，超出本次“通用 Adapter”范围；改为能力检测，MUST_SPLIT 无 provider 时显式 blocker。
- 所有 L2/L3 自动固定启动 5 个 Agent：直接违背价值驱动目标，成本高且会制造写冲突；不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | NO/MAY/MUST 价值判定 | #298 / AC1 | not_satisfied | 待实现与验证 |
| R2 | MUST_SPLIT 条件与 capability fail-closed | #298 / AC2 | not_satisfied | 待实现与验证 |
| R3 | 五角色且不复制专业 Skill | #298 / AC3 | not_satisfied | 待实现与验证 |
| R4 | 用户可见 Visibility Contract | #298 / AC4 | not_satisfied | 待实现与验证 |
| R5 | 并行写隔离/单 Writer | #298 / AC5 | not_satisfied | 待实现与验证 |
| R6 | 四 Host native adapter | #298 / AC6 | not_satisfied | 待实现与验证 |
| R7 | Router Anti-Agent 保持 | #298 / AC7 | not_satisfied | 待 diff/test 证明 |
| R8 | Source/Runtime 同源触发 | #298 / AC8 | not_satisfied | 待 Project Payload projection 证明 |
| R9 | USAGE 用户说明 | #298 / AC9 | not_satisfied | 待文档同步 |
| R10 | tests/Review/CI | #298 / AC10 | not_satisfied | 待当前 head Evidence |
| R11 | 依赖/MCP/License/Release/Schema 保持 | #298 / AC11 | not_satisfied | 待 diff 与回归证明 |
| R12 | merge/main-fresh/archive/closure/cleanup | #298 / AC12 | not_satisfied | Delivery Gate 持有 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| .agents/skills/coding/SKILL.md | 增加薄 Multi-Agent Value Gate | 让 Source/Runtime 工程任务稳定做拆分判定 | R1/R2/R8 |
| .agents/skills/coding/references/09_多人和多智能体并行协作.md | 扩展 canonical Orchestration Contract | 唯一 Owner 承载角色、可见性、Host Adapter 和并发规则 | R1-R7 |
| .agents/skills/coding/tests/ | 增加最小语义/投影回归 | 锁定 Core/Router/Runtime 不变量 | R7/R8/R10/R11 |
| USAGE.md | 增加多 Agent 用户说明 | 用户知道自动拆分和运行时可见性 | R9 |
| 当前 Change / Issue / PR | 需求追溯与交付闭环 | L3/Runtime 变更门禁 | R10/R12 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 行为变化建立失败证据或说明测试例外
- [ ] 完成最小实现，不静默扩大范围
- [ ] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Coding Core Value Gate、Reference 09 classifier/roles/visibility/adapter 语义 |
| 接口 / 契约 | required | Router Anti-Agent、Source/Runtime project-facing Core parity、#298 Requirement Traceability |
| 集成 / 持久化 / 运行依赖 | required | Project Payload / Runtime install 后的 Skill Core 投影 |
| 用户 / 工作流验收 | required | USAGE + 复杂/简单/MUST capability 场景的规则正反例 |
| 跨组件关键路径 | required | canonical Coding Core → Project Payload → installed project Core → Host route/delegation Contract |
| 外部依赖 / 供应方探测 | not_applicable | 宿主能力已用官方当前文档核验；本任务不调用真实外部 Provider/生产数据 |
| 构建 / 打包 / 运行 | required | 以 CI classifier 实际 required scope 为准，至少覆盖 Runtime/Project Payload/install smoke |
| 文档 / 治理 / 其他 | required | Change/Issue/PR、USAGE、独立 Review、current-head CI、post-merge 收尾 |

## 验证计划

- 目标测试：新增 multi-agent orchestration source/runtime projection contract 测试。
- 相关回归：Project Payload、runtime skill projection、single-binary install、DeepSeek host config 等受影响现有测试。
- 静态检查或构建：仓库正式 semantic tests 与 CI classifier 要求的 checks。
- 专项真实边界：不进行外部模型付费 Probe；四宿主能力依据当前官方 source owner 文档核验。
- 就绪检查：python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 过度拆分、写冲突、宿主能力误判、规则第二 Owner | NO/MAY/MUST + Value Gate + 单 Writer + capability detect + Reference 09 单 Owner |
| 兼容性 | 保持现有 Router/专业 Skill/四 Host MCP 接入 | 只增加 Coding 编排语义，不改变 MCP/业务 Contract |
| 数据 / Migration | 不适用 | 无数据库、Schema 或业务数据变化 |
| 部署 / 运行 | Runtime project-facing Skill 文本会随未来安装/升级分发；本任务不 Release | Project Payload 回归证明 |
| 回滚 / 恢复 | revert Implementation PR | 仅源码/规则/测试/文档，可逆 |

# 文档、依赖、部署与发布影响

- **长期文档**：targeted 更新 USAGE；README 只有出现新的安装/运行事实才更新。
- **依赖 / Runtime**：Runtime Project Payload 内容会因 Coding Core 更新而变化，但不升级依赖、不改 protocol/schema。
- **配置 / Secret**：不改变配置/Secret/License。
- **部署 / Release**：不创建 Release/Deploy；正式 Runtime 包只有未来独立 Release 才分发。
- **兼容 / 消费方通知**：安装 Agent_Skills 的项目会在后续 Runtime 升级时获得新编排语义；不强制覆盖宿主自身多 Agent设置。

# 完成审计

- [ ] upstream_re_read：进入 Ready 前重新读取 live #298、当前 head Coding/Router/Runtime/USAGE。
- [ ] change_coverage：逐项映射 #298 AC1-AC12，不能从本 Change 反推完成。
- [ ] reverse_audit：从工程任务入口反查 classifier → Reference 09 → host capability → child Handoff → parent integration → visible result，并核对 Project Payload。
- [ ] unresolved_cleared：R1-R11 在 Ready 前全部取得 Evidence；R12 pre-merge 部分完成，post-merge 由 Delivery Gate继续。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 0cb0cc2385 | GitHub canonical readback + official host docs | 已确认基线 | 当前规则/Runtime/宿主能力事实 |
| V2 | Issue #298 | create + GitHub readback | 已建立 | Requirement Source 与 AC1-AC12 |

## 未验证内容与剩余风险

- 尚未实施，因此 R1-R12 仍未完成。
- 当前聊天宿主没有可调用 subagent 执行接口；本次开发不能把单 Agent 工作冒充多 Agent，这正是 AC2 要约束的 failure boundary。

## 交付状态

- 提交：仅待建立初始 Change commit。
- 拉取请求：待创建 Draft PR。
- CI：待 PR head。
- 合并：未执行。
- Change 归档：未执行。
- 发布 / 部署：不适用，本任务未授权且明确非目标。

## 备注

无。
