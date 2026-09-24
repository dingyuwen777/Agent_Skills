---
schema: coding-change/v1
id: CHG-20260924-110218-final-release-behavior-qualification
title: 发版前 Agent 行为治理与 Release Qualification 最终收口
level: L3
status: ready_for_review
owner: dingyuwen777
branch: tech/final-release-behavior-qualification
created: 2026-09-24
updated: 2026-09-24
completion_gate: required
depends_on: []
affected_areas:
  - router
  - review
  - coding
  - testing
  - docs
  - figma
  - outcome-eval
  - runtime-project-payload
  - release
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/review/
  - .agents/skills/coding/
  - .agents/skills/testing/
  - .agents/skills/docs/
  - .agents/skills/figma/
  - evals/
  - .github/workflows/release.yml
  - .github/workflows/behavior-qualification.yml
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - scripts/runtime_platform_smoke.py
  - README.md
  - USAGE.md
contracts:
  - Cross-Skill Follow-up Lifecycle
  - Exact and Allowed Routing Context
  - High Value Outcome Eval Registry
  - Release Behavioral Qualification
data_changes: []
---

# 变更摘要

- **要解决的问题**：Issue #310 已确认四类发版前高价值缺口：Follow-up 生命周期 Owner、Routing over-disclosure、九个高价值 Outcome Eval、Release behavioral qualification。
- **拟议修改**：只修改这四类机制及其必要 Runtime/project-facing/CI/test/docs 投影，不继续增加无关治理规则。
- **预期结果**：Agent_Skills 在简单任务、复杂任务、跨 Skill、多 Agent 和发版前资格检查上都具有可验证、可收敛且低歧义的行为。

# 背景、现状与问题

## 背景

用户明确把本轮定义为发版前最后一次系统性治理改造，并要求不能为了发版降低实际使用效果。GitHub Issue #310 是当前稳定 Requirement Source。

## 当前现状

- Analysis、Review convergence、多 Agent hardening、Follow-up 非递归、Source/Runtime parity、context absolute budget、三平台 Runtime package smoke 已存在。
- Follow-up 完整 candidate→persistence→backlog→STOP 语义仍主要位于 Review Finding Reference。
- Routing Conformance 主要使用 expected subset + 局部 forbidden references。
- HIGH_VALUE_CONVERGENCE_CASES 已登记九类 failure family，但 evals/cases 未完整落地。
- Release workflow 已证明构建/安装/完整性，但没有 model-neutral behavioral qualification machine contract。

## 问题、根因或约束

根因不是缺少更多规则，而是已有规则在跨 Skill Ownership、最小 Context、真实 Outcome Evidence 和 Release qualification 四个层面还没有形成同一闭环。继续增加同义 Markdown 不能解决这些结构性缺口。

## 不修改的后果

- 跨 Skill 产生 Follow-up 时可能只有 terminal name 而缺完整持久化/停止语义；
- Route 可持续多载 Context 而不触发 under-disclosure 测试；
- registry 名称存在不能证明真实 Outcome case 存在；
- Release Green 仍主要证明 Runtime 产品面，而不是关键 Agent 行为资格。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前 main 为 e4bcebb03a1ca25f3b9db37cf1a35b3128ea6d48 | GitHub main fresh read | 本轮基线 |
| E2 | Follow-up lifecycle 完整链路位于 Review Finding Reference | current canonical read | AC1-AC2 |
| E3 | routing conformance 使用 expected subset 作为核心断言 | current test read | AC3-AC5 |
| E4 | HIGH_VALUE_CONVERGENCE_CASES 有九项，evals/cases 未完整存在 | current tree/evaluator read | AC6-AC8 |
| E5 | release preflight 已跑 full tests + ready_check，三平台 package 保持独立 | current release.yml read | AC9-AC10 |
| E6 | 当前宿主没有 Codex/Claude/Cursor/DeepSeek Harness 的真实外部模型执行接口 | 当前可用宿主能力 | actual cross-host qualification 不能伪造 |

## 推断与待确认

- **待确认**：最终 Release Qualification 要求的跨模型/跨宿主 actual run artifact 尚未取得；本轮先实现机器 Contract 和 fail-closed gate，只有取得真实 run 后才能把对应 Release qualification 标成 satisfied。
- 该未知不阻塞 canonical 规则、Routing、Eval case、Runtime 与 Release gate 的实现，但会阻塞“当前 revision 已完成跨宿主 actual qualification”的强结论。

# 目标、成功标准与非目标

## 目标

形成“规则 → Routing → Runtime → Agent Outcome → Release qualification”的发版前闭环，并保持简单任务低负担、复杂任务充分、跨 Skill/多 Agent 收敛。

## 成功标准

- [x] #310 AC1-AC12 已由当前实现、永久回归和 pre-Ready Green Evidence 覆盖。
- [ ] #310 AC13 的 final-head PR CI / Review / merge / main-fresh / archive / closure / cleanup 由下游 Delivery Gate 完成，不在 pre-merge Change 中自证未来动作。
- [x] #310 AC14 保持：本轮不执行 Release/Deploy；actual qualification 必须在 implementation merge 后绑定 final main SHA，缺失时 Release fail closed。

## 范围

- Cross-Skill Follow-up lifecycle；
- exact/allowed routing 与 context delta；
- 九个 Outcome Eval cases 和 registry validator；
- Release qualification machine contract / preflight；
- 必要 project-facing projection、tests、USAGE 同步。

## 非目标

- 不新增 Planner/Scheduler/Task Queue/Follow-up DB/持久 Ledger；
- 不建立模型专属 Skill；
- 不改 public Runtime CLI/MCP/License/Project Payload schema；
- 不提高 context budget；
- 不执行 Release/Deploy；
- 不修改其他仓库。

## 必须保持不变

- 当前 Source/Runtime 同源和 private execution parity；
- public Runtime 产品面、License、安装/升级 ownership、三平台 ZIP；
- Review/Testing/Figma 专业 Owner 边界；
- 现有安全、权限、Git/CI/Release 门禁；
- 现有 absolute context budget 不放宽。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Router 只拥有跨 Skill terminal/lifecycle；专业分类仍归专业 Owner | E2 / #310 AC1 | 防止第二专业 Owner |
| 接口与契约 | 不改变 public Runtime protocol；新增内部 eval/release evidence contract | E4-E5 | 需要 contract tests |
| 数据与迁移 | 不适用；无业务数据或 Schema | #310 | 无 Migration |
| 错误与失败语义 | qualification/registry 缺失必须 fail closed；actual Evidence 不可伪造 | E4-E6 | Release gate |
| 兼容性 | 当前版本 clean install / 当前版本内 projection 为基线 | Maintenance | 不新增历史兼容 |
| 部署与回滚 | 不执行 Release/Deploy；失败通过 revert PR 回滚 | #310 | 可逆 |

# 修改方案与决策依据

## 最小充分方案

1. 先新增 contract Red：Follow-up Owner、exact/allowed routing、九 case registry、Release qualification/preflight。
2. 将通用 Follow-up lifecycle 上移 Router，Review 只保留 Finding classification 与 Router terminal 引用；同步 project-facing 边界。
3. Routing conformance 对 facts-complete 代表 case 使用 exact，对 unknown/complex 使用 bounded allowed；context budget 增加非阻塞 delta observation，不改 absolute threshold。
4. 新增九个 model-neutral Outcome Eval case，并让 evaluator 强制 registry↔case 完整性。
5. 新增 release qualification machine contract，校验 required actual run、revision、grader、host/model coverage；Release preflight 只调用该 validator，不重写现有三平台流水线。
6. 同步 USAGE/managed projection 与必要 Runtime tests；取得 Green、Review、CI 和交付 Evidence。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 Cross-Skill lifecycle 上移 | E2 | Follow-up 可由多个 Skill 产生，生命周期必须唯一 Owner |
| D2 exact/allowed routing | E3 | 同时控制 under/over disclosure，不靠提高 budget |
| D3 九 case 真正落地 | E4 | registry 名称本身不是行为 Evidence |
| D4 Release qualification 单独 machine contract | E5-E6 | 保留现有 Runtime release owner，同时禁止 fixture/静态 Green 冒充 actual |

## 备选方案与取舍

- 继续只补 Markdown：不能证明真实行为，拒绝。
- Router 复制 Review/Testing/Figma 细节：形成第二专业 Owner，拒绝。
- 全部 route 一律 exact：unknown/complex 合法 dependency closure 会被误伤，拒绝。
- 让 fixture 冒充 actual qualification：违反现有 Outcome Eval 真值边界，拒绝。
- 为本轮新增模型 Provider/Secret：超出范围并引入新运行/安全面，拒绝。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Follow-up lifecycle 跨 Skill 唯一 Owner | #310 / AC1 | satisfied | Router thin lifecycle + Review classification-only + cross-Skill regression |
| R2 | Candidate persistence/backlog/STOP 与新 Task readmission | #310 / AC2 | satisfied | Router / managed AGENTS / Runtime project-facing Router / USAGE |
| R3 | facts-complete exact / unknown bounded routing | #310 / AC3 | satisfied | test_routing_conformance exact/allowed cases Green |
| R4 | routing 关键负例 | #310 / AC4 | satisfied | Testing-only / Analysis-only / Figma review-only / L1 / Mutation Audit conformance Green |
| R5 | absolute budget 保留 + delta observation | #310 / AC5 | satisfied | 现有 absolute threshold 未修改；run 35951626548 全部 budget Green + Context Delta 输出 |
| R6 | 九个 Outcome Eval case | #310 / AC6 | satisfied | evals/cases 九个同名 case + registry test Green |
| R7 | registry↔case fail-closed | #310 / AC7 | satisfied | validate_high_value_case_registry + CLI validate-registry + negative contract tests |
| R8 | 文本 + Contract + Outcome Evidence 分层 | #310 / AC8 | satisfied | preservation + routing/contract + case/grader machine contract；actual 结果留给 exact-main Release qualification |
| R9 | Release Qualification Contract | #310 / AC9 | satisfied | evals/release_qualification.py + fixture/stale/host/model fail-closed unit tests + Behavior Qualification workflow |
| R10 | Release preflight 接线且保留三平台流程 | #310 / AC10 | satisfied | release.yml 仅新增 registry/qualification preflight；Linux/Windows/macOS jobs 未删除 |
| R11 | 不增加禁止机制/不放宽预算 | #310 / AC11 | satisfied | 无 Planner/Scheduler/DB/模型专属 Skill；absolute budgets 未提高；Workflow Responsibility Audit 完成 |
| R12 | project-facing/plaintext + private parity | #310 / AC12 | satisfied | Runtime Router projection + project payload/source-runtime tests Green；package smoke 待 PR Ready current-head |
| R13 | final-head CI/Review/merge/main/archive/closure/cleanup | #310 / AC13 | not_applicable | pre-merge Change 不自证下游 Delivery Gate；由 PR Ready / merge 后流程完成 |
| R14 | 不执行 Release/Deploy | #310 / AC14 | satisfied | 本任务只建立 release gate；未创建 tag/Release/Deploy |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| router/review/specialist cores | Follow-up lifecycle Ownership 收口 | 跨 Skill 一致 | R1-R2 |
| routing conformance/context budget | exact/allowed + delta | 控制 over-disclosure | R3-R5 |
| evals/cases + evaluator | 九 case + registry validation | Outcome Evidence | R6-R8 |
| evals/release qualification + release.yml | behavioral qualification | Release Evidence | R9-R10 |
| managed/Runtime projection/USAGE/tests | project-facing 与守恒同步 | 不丢规则/不泄露内部身份 | R11-R12 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 当前证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red run 35950071178；pre-Ready head e33e7cdf 的 run 35951626548：693 tests OK |
| 接口 / 契约 | required | exact/allowed routing、qualification schema、registry、Source/Runtime parity 全部 Green |
| 集成 / 持久化 / 运行依赖 | required | Project Payload / Runtime projection 自包含回归 Green；三平台 package/install/MCP 在 PR Ready current-head 由 package gate 执行 |
| 用户 / 工作流验收 | not_applicable | **当前 implementation PR** 无法产生绑定未来 final main SHA 的真实宿主 run；actual Codex/Claude Code/Cursor/DeepSeek Harness Evidence 是 implementation merge 后的 Release qualification gate，fixture 不替代 |
| 跨组件关键路径 | required | canonical→routing→bundle/context→Release/Behavior Qualification workflow wiring Green |
| 外部依赖 / 供应方探测 | not_applicable | 本 PR 不新增 Provider/API；真实模型宿主 run 由外部宿主在 final main SHA 上产生 |
| 构建 / 打包 / 运行 | required | compile/CLI smoke Green；PR Ready 后要求 Linux/Windows/macOS package smoke |
| 文档 / 治理 / 其他 | required | Issue #310、Change、README、USAGE、managed projection、Workflow Responsibility Audit 已同步 |

## 验证计划

- 目标测试：final release behavior contract、Outcome Eval registry/qualification、routing exact/allowed；
- 相关回归：全量 self-contained semantic suite；
- 静态/CLI：maintained entrypoints compile + CLI smoke；
- Runtime：Project Payload / project-facing projection；PR Ready 后三平台 runtime_platform_smoke；
- Release：Behavior Qualification artifact exact-main gate + 既有三平台 Release 构建；
- 就绪：ready_check + current-head required CI +独立 Review。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | exact route 误伤、qualification 过度阻塞、Router Owner 膨胀 | 正负例 + bounded unknown + project-facing audit |
| 兼容性 | 保持 public Runtime/Release Contract | 不改 protocol/schema/Stable ID |
| 数据 / Migration | 不适用 | 无业务数据变化 |
| 部署 / 运行 | Runtime project-facing 投影可能受影响 | package/install/MCP smoke |
| 回滚 / 恢复 | revert PR | 无不可逆操作 |

# 文档、依赖、部署与发布影响

- **长期文档**：USAGE 只同步最终用户需要理解的 Follow-up/qualification 使用语义。
- **依赖 / Runtime**：不新增/升级依赖；Runtime 只在 project-facing 投影受影响时重新验证。
- **配置 / Secret**：不新增 Provider Secret；actual run artifact 不允许包含 Secret/私有原始 payload。
- **部署 / Release**：不执行 Release；release.yml 仅增加 preflight evidence gate。
- **回滚**：revert 本 PR。

# 完成审计

- [x] upstream_re_read：已重读 #310、当前 main 基线、最终 implementation Owner 与 Release/Runtime/CI 事实。
- [x] change_coverage：#310 AC1-AC12 已逐条映射；AC13 明确属于下游 Delivery Gate；AC14 保持不执行 Release/Deploy。
- [x] reverse_audit：已反查 Router/Review/Multi-Agent/Runtime Project Payload/Outcome Eval/Behavior Qualification/Release/README/USAGE/Context；新增 Workflow 完成 Responsibility Audit。
- [x] unresolved_cleared：当前 implementation Ready 范围不存在 not_satisfied；真实 external actual run 不属于 pre-merge implementation Evidence，且 Release gate 会在缺失时 fail closed。

# 完成证据与状态

## 新鲜证据

| 证据 | revision / run | 结果 | 证明 |
| --- | --- | --- | --- |
| V1 | main e4bcebb03a1ca25f3b9db37cf1a35b3128ea6d48 / Issue #310 | confirmed | canonical 基线与 Requirement Source |
| V2 | run 35950071178 @ b9d87725 | Red：新 contract tests 按预期失败 | 四类缺口在旧实现上可被机器捕获 |
| V3 | 多轮中间 CI | over-disclosure、Workflow owner、Context budget 分别被回归捕获 | 未通过放宽预算/删测试制造 Green |
| V4 | run 35951626548 @ e33e7cdf | compile/CLI Green；693 tests OK；absolute context budgets Green；仅 Change status=in_progress 门禁阻塞 | pre-Ready implementation semantic Green |
| V5 | Context Delta @ e33e7cdf | testing/general/research/figma +359B；coding/docs +1771B；review +3263B，均仍在 absolute budget 内 | 新跨 Skill Contract 保持薄，增长可观测 |
| V6 | Workflow Responsibility Audit | 四个独立 Owner：Skill Tests / Change Archive / Behavior Qualification / Release | 新 workflow 不是重复 CI/Release owner |

## 未验证内容与剩余风险

- 当前宿主没有 Codex / Claude Code / Cursor / DeepSeek Harness 的真实模型执行接口，**尚未取得 final-main actual Release qualification**。这不会由 fixture/静态 CI 冒充；implementation merge 后若仍缺少该 artifact，正式 Release 会 fail closed。
- 当前 commit 将 Change 置为 `ready_for_review`，会形成新的 PR head；必须重新取得该 head 的 required CI、三平台 package Evidence 与独立 Review。
- 本任务不执行 Release / Deploy。

## 交付状态

- Requirement Source：#310 open
- 分支：tech/final-release-behavior-qualification
- Change：ready_for_review
- PR：#311 Draft；本 commit 后待转 Ready
- Red：35950071178
- pre-Ready Green：35951626548（693 tests OK；Change status gate 是唯一阻塞）
- PR Ready current-head CI/package：待本 commit 后重新取得
- 独立 Review：待 final head
- merge/main-fresh/archive/Issue Closure/cleanup：待 Delivery Gate
- Behavior Qualification actual artifact：implementation merge 后对 final main SHA 取得
- Release/Deploy：not_applicable

## 备注

本轮范围继续冻结为 #310 四类机制。后续只处理 current-head CI/Review/Delivery/actual qualification 暴露的 blocker，不继续凭理论可能增加新优化项。
