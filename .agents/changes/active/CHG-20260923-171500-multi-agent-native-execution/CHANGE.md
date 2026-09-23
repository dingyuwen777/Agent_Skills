---
schema: coding-change/v1
id: CHG-20260923-171500-multi-agent-native-execution
title: 安装多 Agent 原生执行层与项目 Bootstrap
level: L3
status: ready_for_review
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
  - scripts/runtime_platform_smoke.py
  - USAGE.md
  - runtime/README.md
contracts:
  - target-project AGENTS managed bootstrap
  - Multi-Agent Role Manifest
  - Codex project custom agents
  - Claude Code project subagents
  - Cursor project subagents
  - DeepSeek Harness native role tools
  - agent-skills-project-payload/v2
data_changes: []
---

# 变更摘要

- **要解决的问题**：#298/#299 已建立多 Agent Policy，但 onefile binary 安装到目标项目后只配置治理/MCP，没有把根 AGENTS → stable ENTRY → Value Gate 与四宿主 native delegation execution surface 确定性接通。
- **拟议修改**：新增唯一五角色 Role Manifest；installer 由它确定性生成 Codex / Claude Code / Cursor project agents，并在 DeepSeek Harness 当前 base-owned subagent runtime 上增加 namespaced role tools；根 AGENTS managed block 显式导航稳定 ENTRY 并执行 NO_SPLIT/MAY_SPLIT/MUST_SPLIT。
- **预期结果**：运行 binary 后，目标项目自动具备宿主原生可发现的五角色执行层；只在有真实独立价值时拆 Agent；宿主没有可用 delegation 时明确降级为单 Agent 正常执行。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #302。用户要求运行 Agent_Skills 二进制后自动完成目标项目 AGENTS 改造与 Codex / Claude Code / Cursor / DeepSeek Harness 多 Agent execution layer 安装，并在验证、Review、CI 与 post-merge 门禁满足后合并 main。

## 当前现状

本 Change 建立时 main 为 `cf258a69e66a334bf39660e17e73a4b6f65d9233`：

- Runtime installer 已安装 Project Payload、根 AGENTS managed block、四宿主 MCP、CLAUDE.md bridge、DeepSeek Harness MCP overlay 和 Windows launcher。
- 根 AGENTS managed block 未显式导航 `.agents/skills/ENTRY.md`。
- 没有 `.codex/agents/agent-skills-*.toml`、`.claude/agents/agent-skills-*.md`、`.cursor/agents/agent-skills-*.md`。
- DeepSeek overlay 没有 Agent_Skills namespaced role tools。
- #298/#299 的 Policy 已能判断 NO_SPLIT/MAY_SPLIT/MUST_SPLIT，但“应该委派”与“宿主已安装可调用角色”之间仍缺执行桥。

当前 PR #303 已完成上述 execution gap 的实现和永久回归；当前 reviewed implementation head 为 `f71ec867cdd4da8d77aaa03f3cbd499e214bbf12`。

## 问题、根因或约束

根因是上一 Change 的完成边界停在 **Policy**，没有把 **Host Execution Adapter** 作为独立安装 Contract。

必须同时满足：

1. 角色职责不能在四宿主形成四套人工事实源；
2. root AGENTS 必须能确定到达 stable ENTRY / Value Gate，但不能恢复 Router/Reference 全内部导航；
3. native role files 必须有 ownership/collision 保护；
4. installer 任一步失败必须恢复 Runtime、Project Payload、AGENTS/MCP、role projections 与 DSH overlay；
5. read-only roles 与 Worker 的并发默认必须与写冲突风险相称；
6. 宿主没有 subagent 能力时，多 Agent Contract 本身不能阻塞原任务。

## 不修改的后果

MUST_SPLIT 可能仍依赖模型临场发现宿主能力；Claude/Cursor/Codex 无固定项目级角色，DSH 无 Agent_Skills namespaced role tools；不同宿主执行效果不稳定，且以前的 CI 只能证明规则文本/Runtime Core 存在，不能证明 onefile install 后 native execution assets 真正落地。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | main 基线 `cf258a69` 缺 root AGENTS→ENTRY 明确导航和 native role projections | main canonical readback + Red regression | 必须补 Bootstrap + execution layer |
| E2 | Codex 当前支持项目 `.codex/agents/*.toml`；`name/description/developer_instructions` required，`sandbox_mode` 支持 | OpenAI current official Subagents docs，2026-09-23 复核 | Codex renderer schema |
| E3 | Claude Code 当前支持 `.claude/agents/*.md`；`permissionMode=plan`、`disallowedTools`、`background` 均为合法 frontmatter；首次创建 agents 目录时旧会话可能需重启 | Anthropic current official Subagents docs，2026-09-23 复核 | Claude renderer + USAGE discovery note |
| E4 | Cursor 当前支持 `.cursor/agents/*.md`，字段包括 `model/readonly/is_background`，并可自动/并行 delegation | Cursor current official Subagents docs，2026-09-23 复核 | Cursor renderer schema |
| E5 | DeepSeek Harness current base 已挂载 subagent service、spawn/fork、control/list 与 generic delegation tool；`dsh-tool-subagent` 支持 `provider/toolName/backgroundMode/enableRunInBackground/persona` | DeepSeek Harness current official source/package README，2026-09-23 复核 | DSH 只增加 role tools，不重复注册 base runtime |
| E6 | #1839 在 Requirement Source 合法后真正运行新增 4 个 installer tests，并因旧实现缺 Bootstrap/native files/collision/rollback execution assets 失败 | Skill Tests run `35843007636` | 有效 Red Evidence |
| E7 | #1869 在 head `f71ec867` 上 compile/CLI smoke/649 tests 全部 Green；Gate 仅因 Change 尚未 Ready 被 fail-closed | Skill Tests run `35846311845` | 当前实现与永久回归 Green |
| E8 | PR Review `5291913091` 基于 #302 重建预期并审查最新 implementation head，结果 NO_BLOCKING_FINDINGS_WITHIN_SCOPE | PR #303 current-head Review | 独立 Review 证据 |
| E9 | PR changed surface 无 Manifest/lock/License/MCP Tool/Release schema/业务 Schema 变更 | PR #303 changed-files/diff readback | 非目标保持 |

## 推断与待确认

- 已确认：current implementation 不需要新增 Python/Node 依赖，也不在线安装外部宿主或 DSH package。
- 已确认：Project Payload v2 会分发 `coding/assets/multi-agent-roles.json`，installer 从该 payload 生成 host projections。
- 待 Delivery Gate：Change Ready 后，当前 final head 仍需重新取得 Linux / Windows / macOS onefile package evidence；pre-Ready semantic Green 不能替代 final package。
- 不在 CI 启动需要真实账号/模型的 Codex、Claude Code、Cursor 或 DSH 会话，因此最终 Evidence 只证明“execution surface 按当前官方 schema 安装并可由宿主原生发现/调用”，不宣称真实付费模型已经 spawn child。

# 目标、成功标准与非目标

## 目标

运行 Agent_Skills onefile binary 后自动建立目标项目 Multi-Agent Bootstrap 和四宿主 native execution surface，并把这些资产纳入安全安装/升级/回滚事务；保持价值驱动拆分和无能力单 Agent fallback。

## 成功标准

- [x] #302 AC1–AC12 已由 current implementation、永久回归和文档直接覆盖。
- [x] #302 AC13 的独立 Review 已完成；final-head required CI 与三平台 package 属于 Ready 后 Delivery Gate，不由 pre-Ready Change 自证。
- [x] #302 AC14 明确由 guarded merge 后的 main-fresh / Archive / Issue Closure / cleanup 门禁持有。
- [x] 当前实现没有新增 Planner/Scheduler/常驻 Worker Queue，也没有固定模型或并发数。

## 范围

AGENTS managed Bootstrap、single Role Manifest、Codex/Claude/Cursor role projections、DeepSeek namespaced role tools、installer transaction、onefile smoke、相关回归、USAGE/runtime docs 和本次交付治理。

## 非目标

- 不固定每个任务启动五个 Agent；
- 不固定模型 ID、reasoning effort 或最大并发；
- 不新增 MCP Tool；
- 不在线下载 Codex / Claude Code / Cursor / DSH package；
- 不建立长期 Planner/Queue/Worker 控制面；
- 不修改 AIMA_UGC；
- 不创建 Runtime Release 或 Deploy；
- 不用 CI 冒充真实外部模型会话已经成功 spawn。

## 必须保持不变

- Router Anti-Agent Boundary；
- Coding/Testing/Review/Research/Figma 专业 Skill ownership；
- 六个 MCP Tool Contract；
- License Contract；
- Release ZIP schema；
- `agent-skills-project-payload/v2`；
- marker 外目标项目 AGENTS/CLAUDE/MCP/用户文件；
- 用户无法证明 Agent_Skills ownership 的同名 native role file；
- sidecarless previous ownership 与原子 rollback 基础语义。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 角色事实源 | `multi-agent-roles.json` 是五角色唯一人工事实源；Host renderer 只投影 | #302 AC2 | 防止四宿主 prompt 漂移 |
| 根 Bootstrap | root AGENTS 只公开稳定 `.agents/skills/ENTRY.md`，其余 Router/Skill/Reference 导航继续隐藏 | #302 AC1 + Runtime disclosure Contract | 保证可达性且不恢复完整内部导航 |
| Codex/Claude/Cursor | 生成 namespaced project-native agent files，不固定模型 | E2-E4 | 宿主可发现、继承 parent model |
| DeepSeek | 复用 current `@deepseek-ai/dsh-base` 已有 subagent runtime，只增加五个 role tools | E5 | 避免重复 provider/service 注册 |
| 并发默认 | read-only roles 可 background；Worker 在 Claude/Cursor/DSH 默认不后台写，DSH 强制 one-shot + background disabled | #302 AC5/AC6 + current host semantics | 降低共享工作区写冲突 |
| ownership | role file 只有不存在或含精确 `agent-skills:multi-agent-role:v1 role=<id>` marker 才可写 | #302 AC8 | 用户同名文件 fail closed |
| rollback | host projections 与 DSH overlay 加入 installer snapshot/restore 与新目录 cleanup | #302 AC9 | 不留半安装 |
| fallback | 宿主无 delegation/被禁用时明确降级单 Agent，不阻塞任务 | #302 AC7 | 多 Agent 是收益增强而非兼容性硬依赖 |

# 修改方案与决策依据

## 最小充分方案

1. canonical `multi-agent-roles.json` 固定 Explorer / Researcher / Worker / Tester / Reviewer 的 ID、description、mode、background、instructions。
2. `host_agent_projection.py` 严格校验 Manifest，并从同一输入生成 Codex TOML、Claude Markdown、Cursor Markdown、DSH role-tool rows。
3. `AGENTS.managed.md` 在计划前明确读取 stable ENTRY、执行 NO/MAY/MUST、报告实际分工，并规定无能力 fallback。
4. `project_installer.py` 在任何 mutation 前构建 Host plan 并检查 symlink/collision/ownership；写入纳入现有安装事务、snapshot 与 rollback。
5. DSH overlay保留已有 Agent_Skills MCP，复用 base-owned `ctx.subagents/spawn/control/list`，只增加 namespaced role tools；Worker one-shot foreground。
6. onefile smoke 直接验证 target tree 中 15 个 Codex/Claude/Cursor native role files、DSH role rows、root AGENTS 唯一 ENTRY 及权限默认。
7. USAGE 只说明开发者可观察行为：binary 自动安装四宿主多 Agent adapters、首次新增 agent 目录后必要时新建宿主会话、无能力正常单 Agent。
8. Ready 后取得 current-head 三平台 package，再 guarded merge 和 post-merge closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用 |
| --- | --- | --- |
| D1 single manifest | #302 AC2；四宿主角色职责相同 | 一个 Owner 比四套手写规则稳定 |
| D2 root ENTRY | Red E6 + 用户明确质疑 AGENTS 可达性 | Policy 文件存在不等于宿主必然读到 |
| D3 native project agents | E2-E4 | 利用宿主当前官方发现面，不发明私有 API |
| D4 DSH base reuse | E5 | current base 已挂载 runtime；重复注册有冲突风险 |
| D5 Worker foreground | 当前宿主共享 checkout/DSH in-process语义 + #302 写冲突要求 | 不为了“并行”制造共享写状态竞争 |
| D6 installer transaction | 现有 installer 已拥有原子写/rollback | 比第二安装器或运行时临时生成更安全 |

## 备选方案与取舍

- **继续只有 Markdown Policy**：无法证明 native execution surface，拒绝。
- **四宿主各手写五套 canonical prompt**：会形成规则漂移，拒绝。
- **DSH 重复安装 subagent service/provider/control**：current base 已拥有，可能重复注册，拒绝；只加 role tools。
- **DSH/Claude/Cursor Worker 默认 background**：共享工作区写冲突收益差，拒绝；保持 foreground。
- **安装时联网装 Host/package**：破坏离线/确定性，拒绝。
- **所有复杂任务固定启动五角色**：违背 Value Gate，拒绝。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AGENTS Bootstrap | #302 / AC1 | satisfied | AGENTS.managed 明确 stable ENTRY + NO/MAY/MUST；project bootstrap/disclosure tests 与 #1869 Green |
| R2 | 单一 Role Manifest | #302 / AC2 | satisfied | `multi-agent-roles.json` + strict loader；固定五角色顺序/mode/background |
| R3 | Codex execution projection | #302 / AC3 | satisfied | `.codex/agents/agent-skills-*.toml` renderer；read-only/workspace-write；current Codex schema 复核；installer test Green |
| R4 | Claude Code execution projection | #302 / AC4 | satisfied | `.claude/agents/agent-skills-*.md` renderer；plan + disallowedTools for read-only；background=false Worker；current Claude schema 复核 |
| R5 | Cursor execution projection | #302 / AC5 | satisfied | `.cursor/agents/agent-skills-*.md` renderer；readonly/is_background；current Cursor schema 复核 |
| R6 | DSH execution overlay | #302 / AC6 | satisfied | current base ownership 复核；overlay 仅五 namespaced role tools；四 read-only continuable，Worker one-shot + no background；tests/smoke 断言 |
| R7 | Value Gate → native execution / fallback | #302 / AC7 | satisfied | root AGENTS Bootstrap + #298 canonical Orchestration Contract；无能力明确单 Agent fallback |
| R8 | ownership / idempotency / collision | #302 / AC8 | satisfied | 精确 role marker；Codex/Claude/Cursor 三类 collision tests；same-binary reinstall byte-stable test |
| R9 | installation rollback | #302 / AC9 | satisfied | host projection snapshots + directory cleanup；升级 reviewer 内容变化后注入 Cursor write failure，验证 reviewer projections/manifest/AGENTS/Runtime/DSH 恢复 |
| R10 | Runtime/MCP/License/schema compatibility | #302 / AC10 | satisfied | 无 MCP Tool/License/Project Payload schema/依赖变更；649-test closure Green |
| R11 | permanent regression | #302 / AC11 | satisfied | Red #1839；new installer regression；正式 `runtime_platform_smoke.py` 验证 onefile target tree/native projections |
| R12 | USAGE / discovery / fallback docs | #302 / AC12 | satisfied | USAGE §4.1：binary 自动安装四宿主 adapters、首次新目录会话发现、无能力单 Agent；runtime README/canonical References 同步 |
| R13 | Review / final-head CI / three-platform package | #302 / AC13 | not_applicable | independent Review `5291913091` 已完成且无阻塞 Finding；final-head required CI/package 只有 Change Ready 后才能作为 Delivery Evidence，不能由 pre-Ready Change 自证 |
| R14 | merge / main-fresh / archive / closure / cleanup | #302 / AC14 | not_applicable | pre-merge Change 不能自证未来动作；由已授权 Delivery Gate 在 guarded merge 后完成 |

# 计划改动

| 文件 / 模块 / 资产 | 实际修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| `coding/assets/AGENTS.managed.md` | stable ENTRY + Value Gate + visibility/fallback | 目标项目确定可达 | R1/R7 |
| `coding/assets/multi-agent-roles.json` | 五角色 canonical manifest | 唯一角色 Owner | R2 |
| `runtime/.../host_agent_projection.py` | manifest validator + Codex/Claude/Cursor/DSH renderers | native execution layer | R2-R8 |
| `runtime/.../project_installer.py` | preflight/write/snapshot/rollback host projections + DSH rows | binary 自动安装执行层 | R3-R10 |
| `coding/scripts/coding.py` | disclosure validator 只白名单 stable ENTRY | root AGENTS 可达但不泄漏其余内部导航 | R1/R10 |
| `coding/tests/test_multi_agent_execution_install.py` | Red→Green、first install、三宿主 collision、reinstall、upgrade rollback | 安装行为直接证明 | R1-R11 |
| 既有 Bootstrap/disclosure tests | 迁移为“只允许 stable ENTRY” Contract | 同步规范性行为变化 | R1/R10/R11 |
| `scripts/runtime_platform_smoke.py` | 正式 artifact target tree/15 role files/DSH/root AGENTS 检查 | 三平台 onefile evidence | R11/R13 |
| `USAGE.md` / `runtime/README.md` / Ref12/Ref13 / Maintenance | targeted 同步执行层与边界 | 长期事实一致 | R12 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立有效 Red Evidence
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档
- [x] 取得仍覆盖 current implementation head 的 semantic/installer 新鲜验证
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Role Manifest strict validator；Codex/Claude/Cursor/DSH renderers；new tests |
| 接口 / 契约 | required | current official host schemas；root stable ENTRY disclosure boundary；role ownership marker |
| 集成 / 持久化 / 运行依赖 | required | first install / same binary reinstall / changed-manifest upgrade / three-host collision / write-failure rollback |
| 用户 / 工作流验收 | required | onefile target tree、AGENTS Value Gate、USAGE auto-install/session discovery/fallback |
| 跨组件关键路径 | required | canonical manifest → Project Payload → installer → host-native files/DSH rows → parent Value Gate |
| 外部依赖 / 供应方探测 | not_applicable | current source-owner docs/source 已核验；无真实付费模型/account Probe |
| 构建 / 打包 / 运行 | required | compile + CLI smoke + 649 tests Green；Ready 后 final-head Linux/Windows/macOS onefile package |
| 文档 / 治理 / 其他 | required | #302、Change、PR #303、Review 5291913091、USAGE/runtime docs；post-merge closure |

## 验证计划

- 已完成 Red：#1839 / `35843007636`。
- 已完成 current implementation semantic：#1869 / `35846311845`，649 tests Green。
- Ready 后必须重新跑 final-head Agent Skills Gate 和 Linux/Windows/macOS Runtime Package。
- final package smoke 将真实运行 onefile install，验证 root AGENTS、15 native role files、DSH role rows、MCP/status/self-test 等。
- 不执行外部付费模型 child-run Probe；完成报告明确该边界。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | host schema 漂移、user-owned role collision、DSH duplicate provider、并行 Writer、半安装 | current docs/schema 核验；marker/preflight；DSH base reuse；Worker foreground；transaction rollback |
| 兼容性 | Project Payload v2、MCP/License/Release ZIP schema 保持；新增 target-side execution assets | #302 AC8-AC10 + 649-test closure |
| 数据 / Migration | 不适用 | 无数据库/业务数据/Schema |
| 配置 / 部署 | 下一次正式 Runtime Release/升级才向外部目标项目分发；本任务本身不 Release/Deploy | 用户授权 |
| 升级 | 同 binary 重装幂等；旧 binary previous ownership 继续走 install-state；新 role files 自身 marker 证明后续 ownership | tests + installer |
| 回滚 / 恢复 | 任一写失败恢复 host projections/AGENTS/MCP/Runtime/managed files/DSH，清理本事务新建空目录；源码可 revert PR | #302 AC9 |

# 文档、依赖、部署与发布影响

- **长期文档**：USAGE、runtime README、Bootstrap/Runtime References、Maintenance 已 targeted 更新。
- **依赖 / Runtime**：无 dependency/lock 更新；DeepSeek 只引用当前 base 已提供 package。
- **配置 / Secret**：新增项目级 native role files 与 DSH role rows；无 Secret。
- **部署 / Release**：不创建 Release/Deploy。
- **消费者影响**：后续发布的新 binary 安装/升级后会生成 native role adapters；首次创建 agent 目录后，宿主若未即时发现需新建/重启会话；无 delegation 时任务正常单 Agent。

# 完成审计

- [x] upstream_re_read：Ready 前已重新读取 live #302、current head AGENTS/manifest/renderer/installer/tests/USAGE/runtime docs，并重新核验 Codex/Claude/Cursor/DSH current source-owner schema。
- [x] change_coverage：从 #302 AC1–AC14 独立重建完成定义并逐项映射；R13/R14 的 downstream Delivery 不由本 Change 反推完成。
- [x] reverse_audit：已从 binary install → Project Payload role manifest → collision preflight → AGENTS stable ENTRY → host projections/DSH role tools → Value Gate/delegation/fallback → parent integration → rollback 反向审计。
- [x] unresolved_cleared：R1–R12 均有 direct implementation/test/doc Evidence；R13/R14 的 Ready 后动作明确标为 Delivery Gate，当前无 `not_satisfied` 或占位 Evidence。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main `cf258a69` | canonical installer/assets + current host official docs | confirmed | 起始 execution gap |
| V2 | #1837/#1838 | Requirement/Change machine contract | failed before behavior tests | 非 Red；促使 Requirement Source 按 current form 补齐 |
| V3 | PR head `b4b30cef` / Skill Tests #1839 / run `35843007636` | new installer regression | 4 tests executed: 3 fail + 1 error，均指向旧实现缺 Bootstrap/native files/collision/rollback assets | 有效 Red Evidence |
| V4 | PR #303 iterative Green | compile/CLI smoke/full self-contained suite | 旧 disclosure Contract、context budget、rollback fixture 等真实回归逐项修复；未抬预算/删断言 | 修复过程保持测试意图 |
| V5 | PR head `f71ec867` / Skill Tests #1869 / run `35846311845` | compile + CLI smoke + 649 self-contained tests | tests 全部 Green；Ready enforcement 仅因 Change 当时仍 `in_progress` 失败 | current implementation 功能/语义/预算 closure Green |
| V6 | current official Host docs/source | Codex/Claude/Cursor docs + DSH base cordis/tool-subagent README | renderer 字段均为 current supported schema；DSH base-owned runtime 已确认 | Host schema / base reuse |
| V7 | PR #303 review `5291913091` @ `f71ec867` | requirement-first current-head review | NO_BLOCKING_FINDINGS_WITHIN_SCOPE | 独立 Review 无阻塞 Finding |
| V8 | PR #303 changed-files/diff | implementation surface readback | 无 Manifest/lock/MCP Tool/License/Release schema/业务 Schema 变更 | 非目标保持 |

## 未验证内容与剩余风险

- 当前聊天宿主本身没有可调用 subagent execution interface；本次开发按已定义 fallback 由单 Agent 完成，没有伪造真实 child run。
- CI/onefile smoke 不使用外部 Codex/Claude/Cursor/DSH 账号与真实模型，因此不宣称四宿主真实模型已成功 spawn；证明边界是 native execution surface 已安装且 schema/发现面符合 current official contract。
- final-head 三平台 package、merge、main-fresh、Archive、Issue Closure 和 branch cleanup 尚未发生；这些必须在本 Ready commit 之后取得 fresh Evidence。

## 交付状态

- 分支：`tech/multi-agent-native-execution`。
- PR：#303，当前仍 Draft；本提交将 Change 置为 `ready_for_review`。
- Review：`5291913091`，implementation head `f71ec867`，无阻塞 Finding；本 Ready commit 只更新 Change Evidence，需做增量 re-review。
- CI：Red #1839；current implementation semantic Green #1869；Ready commit 后必须重新取得 final-head required CI/package。
- 合并：未执行；只有 final reviewed head required CI Green 后才允许 `expected_head_sha` guarded merge。
- Change 归档：未执行；Implementation merge 后由 repository-native automation 持有。
- Release / Deploy：不适用，本任务未授权且明确非目标。

## 备注

无。
