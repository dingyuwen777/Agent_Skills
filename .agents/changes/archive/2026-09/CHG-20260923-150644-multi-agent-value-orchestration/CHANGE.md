---
schema: coding-change/v1
id: CHG-20260923-150644-multi-agent-value-orchestration
title: 多 Agent 价值驱动编排与跨宿主适配
level: L3
status: done
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

- **要解决的问题**：当前多 Agent 规则只覆盖“已并行后的安全协作”，缺少价值驱动的拆分判定、MUST_SPLIT/单 Agent 降级语义、四宿主适配和用户可见编排。
- **拟议修改**：在 Coding Core 建立轻量决策入口，扩展既有 Reference 09 为唯一 Multi-Agent Orchestration Owner，并同步 Runtime projection、USAGE 和必要回归；保持 Router 不承担调度。
- **预期结果**：简单任务继续单 Agent；真正有独立价值的复杂任务按 NO_SPLIT/MAY_SPLIT/MUST_SPLIT 决策，支持的宿主真实委派，不支持时明确降级为单 Agent 正常执行，用户能看到 Agent 分工和状态。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #298。用户明确要求按已讨论方案修改 Agent_Skills，并在全部门禁满足后合并主分支。当前任务不授权 Runtime Release、Deploy，也不修改 AIMA_UGC。

## 当前现状

- Router canonical 明确 Anti-Agent Boundary：不创建子 Agent、不拆分/调度任务。
- Coding Reference 09 已规定纵向切片、DAG/frontier、Delegation Contract、并行写隔离、授权边界和父 Agent 集成验证。
- Coding Core 尚未要求在实质性工程任务开始时先判断多 Agent 的独立价值，因此普通任务不会稳定触发 Reference 09，也没有宿主能力不足时的统一单 Agent 降级语义。
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

复杂任务可能错失并行、上下文隔离和独立复核收益；简单任务也可能被过度拆分，增加 token、延迟和协调成本。不同宿主会出现不同的拆分行为和可见性；宿主无真实 subagent 能力时如果没有明确规则，也可能静默降级或错误阻塞。

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

- 已确认：本次没有新增 Host 配置、Provider、Runtime protocol/schema 或依赖；Project Payload/Runtime projection 回归已证明更新后的 Coding Core 能进入项目侧 Runtime Core。
- 已确认：当前 CI classifier 要求 Runtime Package Gate；Change Ready 后由 current-head CI 执行三平台 package evidence。

# 目标、成功标准与非目标

## 目标

建立跨 Codex、Claude Code、Cursor、DeepSeek Harness 一致的价值驱动 Multi-Agent Orchestration Contract，使复杂工程任务在真实有收益时拆分，并保持专业 Skill、授权、证据和交付治理同源。

## 成功标准

- [x] #298 AC1-AC11 已由当前实现、永久回归、文档与 Review Evidence 覆盖；current-head required CI 在 Ready 后继续执行。
- [x] #298 AC12 的 pre-merge治理已建立；merge/main-fresh/archive/closure/cleanup 由 post-merge Delivery Gate 持有。
- [x] Router Anti-Agent Boundary 保持，没有新增 Planner/Queue/长期 Worker 机制。
- [x] 简单任务明确保持单 Agent，不以“多 Agent”本身作为收益。

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
| 错误与失败语义 | MUST_SPLIT 在宿主支持时必须拆；宿主缺少 subagent 能力时显式降级为单 Agent 并继续执行；其他既有硬门禁不受影响 | #298 / AC2/AC6 | 不允许假多 Agent，也不因编排能力缺失误阻塞 |
| 兼容性 | 简单任务继续单 Agent；现有专业 Skill/Router 保持 | #298 / AC1/AC3/AC7 | 降低协调成本和漂移风险 |
| 部署与回滚 | 只合并 main，不 Release/Deploy；失败可 revert PR | 用户授权、#298 非目标 | 无不可逆运行数据 |

# 修改方案与决策依据

## 最小充分方案

1. 在 Coding Core 增加“Multi-Agent Value Gate”薄入口：先判 NO/MAY/MUST；只有 MAY/MUST/用户显式要求时加载 Reference 09。
2. 扩展 Reference 09，形成完整唯一 Orchestration Contract：独立价值判定、MUST_SPLIT、宿主不支持时的单 Agent 自动降级、五角色职责、权限、并发、Visibility、Handoff、Host Adapter、失败边界。
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
- 为 DSH 安装 subagent provider：会新增外部依赖和具体 provider 决策，超出本次“通用 Adapter”范围；改为能力检测，无 provider 时明确降级为单 Agent。
- 所有 L2/L3 自动固定启动 5 个 Agent：直接违背价值驱动目标，成本高且会制造写冲突；不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | NO/MAY/MUST 价值判定 | #298 / AC1 | satisfied | Coding Core §5 + Reference 09 Value Gate；run #1820 的 645 tests Green |
| R2 | MUST_SPLIT 条件与宿主无能力时的单 Agent 降级 | #298 / AC2 | satisfied | Reference 09 Value Gate + USAGE §4.1；Runtime projection 回归 Green |
| R3 | 五角色且不复制专业 Skill | #298 / AC3 | satisfied | Reference 09 角色段：Explorer/Researcher/Worker/Tester/Reviewer，只定义职责/权限并回到专业 Skill |
| R4 | 用户可见 Visibility Contract | #298 / AC4 | satisfied | Reference 09 Multi-Agent Visibility Contract + USAGE §4.1 |
| R5 | 并行写隔离/单 Writer | #298 / AC5 | satisfied | Reference 09：独立 frontier、共享 Contract/Schema 单 Writer、Writer 隔离/串行边界 |
| R6 | 四 Host native adapter | #298 / AC6 | satisfied | Reference 09 Host Adapter Contract：Codex/Claude Code/Cursor/DeepSeek Harness capability detect + native delegation + fallback |
| R7 | Router Anti-Agent 保持 | #298 / AC7 | satisfied | Router 未修改；永久回归断言“不创建子 Agent / 不拆分或调度开发任务” |
| R8 | Source/Runtime 同源触发 | #298 / AC8 | satisfied | Coding Core 写入 `能力=多 Agent`；`test_multi_agent_value_gate_survives_runtime_projection` 同时验证 canonical/Runtime Core |
| R9 | USAGE 用户说明 | #298 / AC9 | satisfied | USAGE §4.1 已说明自动判定、可见状态与无能力单 Agent 降级 |
| R10 | tests/Review/CI | #298 / AC10 | satisfied | Red run #1807 锁定旧实现缺口；Green run #1820/#1822：compile/CLI smoke/645 tests 与 Ready Check Green；Review 的 NO_SPLIT 可见性与 Value Gate 循环/用户要求绕过两项缺口均已修复并补永久回归；最终 package/current-head gate 继续 |
| R11 | 依赖/MCP/License/Release/Schema 保持 | #298 / AC11 | satisfied | PR changed files 仅 Coding rule/test/USAGE/Change；无 Manifest/lock/Runtime protocol/License/Release/Schema 文件变化 |
| R12 | merge/main-fresh/archive/closure/cleanup | #298 / AC12 | not_applicable | pre-merge Change 不能自证未来 merge/main-fresh/archive/closure/cleanup；由已授权 Delivery Gate 在 merge 后完成 |

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
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red run #1807 精确证明旧实现缺失；Green run #1820 的 645 tests 覆盖 Value Gate/roles/visibility/adapter 与上下文预算 |
| 接口 / 契约 | required | Router Anti-Agent 未改；Source/Runtime Coding Core projection 回归 Green；#298 AC1-AC12 已逐项映射 |
| 集成 / 持久化 / 运行依赖 | required | Project Payload / Runtime Skill Core 投影、sidecarless install 与既有 Runtime 回归均在 645 tests 中 Green |
| 用户 / 工作流验收 | required | USAGE §4.1 明确自动拆分、状态可见与无能力降级；本轮宿主真实无 subagent 时按该规则继续单 Agent |
| 跨组件关键路径 | required | canonical Coding Core → Project Payload → Runtime Core → `能力=多 Agent` → Reference 09 路由由永久回归覆盖 |
| 外部依赖 / 供应方探测 | not_applicable | 宿主能力依据当前官方 source owner 文档核验；本任务不调用真实外部 Provider/生产数据 |
| 构建 / 打包 / 运行 | required | compile + CLI smoke 已 Green；Change Ready 后 current-head CI 执行 required 三平台 Runtime package gate |
| 文档 / 治理 / 其他 | required | #298、当前 Change、PR #299、USAGE 与正式 Review；post-merge Archive/Closure 由 Delivery Gate继续 |

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

- [x] upstream_re_read：已重新读取 live #298、当前 head Coding Core、Reference 09、Runtime projection 回归与 USAGE。
- [x] change_coverage：已从 #298 AC1-AC12 独立重建完成定义并逐项映射；没有把本 Change 自身当需求全集。
- [x] reverse_audit：已反查任务判定 → `能力=多 Agent` → Reference 09 → host capability/fallback → Delegation/Handoff → 父 Agent 集成 → 用户可见结果，并核对 Runtime Projection。
- [x] unresolved_cleared：R1-R11 均有当前实现/测试/文档/Review Evidence；R12 的 post-merge 动作明确由 Delivery Gate 持有。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 0cb0cc2385 | GitHub canonical readback + official host docs | 已确认基线 | 当前规则/Runtime/宿主能力事实 |
| V2 | Issue #298 | create + live reread | 已建立并按用户纠正更新 | Requirement Source 与 AC1-AC12 |
| V3 | abdae298 / Skill Tests #1807 | selected self-contained tests | FAIL：新回归因旧 Core 缺少 NO_SPLIT 精确失败 | 有效 Red Evidence |
| V4 | 44e12fa4 / Skill Tests #1820 | compile selected entrypoints + CLI smoke + 645 self-contained tests | 全部 Green；645 tests OK | 实现、Runtime projection、内容守恒与 context budget 当前均通过 |
| V5 | PR #299 Review：44e12fa4 → c37c5358/1d16ba5a → ad15416f/ac18f737/ec85dfed | 独立重建 #298 AC1-AC12，审查 Coding Core / Reference 09 / Runtime projection / USAGE | Finding 1：NO_SPLIT 不加载详细 Reference 时可能缺少用户可见判定，已把“先报判定”放回 Core 并补回归；Finding 2：Core 先判 MAY/MUST 再加载详细定义存在循环，且“用户明确要求”不能单独绕过独立价值门槛，已在 Core 补极简自包含定义、Reference 09 收紧 MUST，并补永久回归；re-review 未发现新的阻塞 Finding | 两个需求/可维护性 Finding 均已修复并由 Source/Runtime 回归保护 |
| V6 | PR #299 changed-files readback | 5 files：Change、Coding Core、Reference 09、projection test、USAGE | 无 Manifest/lock/MCP/License/Release/Schema 变更 | R11 非目标保持 |
| V7 | 4368a7fd / Skill Tests #1822 | compile + CLI smoke + 645 self-contained tests + changed Change Ready Check | Agent Skills Gate success；645 tests OK；Ready Check 通过 | 当前实现/治理与 context budget 在 Change Ready 状态继续 Green；Draft 状态按设计尚未执行三平台 package |

## 未验证内容与剩余风险

- 当前聊天宿主没有可调用 subagent 执行接口；按 AC2 已降级为单 Agent 正常执行，本轮没有冒充实际拆分。
- 三平台 Runtime package、merge、main-fresh、Change Archive、Issue Closure 和 cleanup 尚未完成；PR 已转 Ready，当前最新 head 正在重新取得 required semantic/package Evidence。

## 交付状态

- 提交：实现/测试/文档已在 `tech/multi-agent-value-orchestration`；本次提交把 Change 切到 `ready_for_review`。
- 拉取请求：PR #299 已创建，当前仍 Draft；本提交后等待 final current-head CI 再转 Ready。
- CI：Red #1807 已确认；semantic Green #1820/#1822 与 Ready Check 已确认；PR 已转 Ready，最新 head 的三平台 Runtime package/current-head Evidence 正在执行，未完成前不合并。
- 合并：未执行；需 current-head Review/required CI 后 guarded merge。
- Change 归档：未执行；由 repository-native post-merge automation 负责。
- 发布 / 部署：不适用，本任务明确不创建 Runtime Release/Deploy。

## 备注

无。
