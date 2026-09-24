---
schema: coding-change/v1
id: CHG-20260924-110218-final-release-behavior-qualification
title: 发版前 Agent 行为治理与 Release Qualification 最终收口
level: L3
status: in_progress
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

- [ ] #310 AC1-AC12 全部由当前实现与永久回归覆盖。
- [ ] #310 AC13 的 PR/merge/main-fresh/archive/closure/cleanup 由交付阶段新鲜 Evidence 覆盖。
- [ ] #310 AC14 保持：本轮不执行 Release/Deploy，只把 main 准备到可发版条件；若 actual qualification Evidence 缺失则如实报告剩余 blocker。

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
| R1 | Follow-up lifecycle 跨 Skill 唯一 Owner | #310 / AC1 | not_satisfied | 待实现 |
| R2 | Candidate persistence/backlog/STOP 与新 Task readmission | #310 / AC2 | not_satisfied | 待实现 |
| R3 | facts-complete exact / unknown bounded routing | #310 / AC3 | not_satisfied | 待实现 |
| R4 | routing 关键负例 | #310 / AC4 | not_satisfied | 待实现 |
| R5 | absolute budget 保留 + delta observation | #310 / AC5 | not_satisfied | 待实现 |
| R6 | 九个 Outcome Eval case | #310 / AC6 | not_satisfied | 待实现 |
| R7 | registry↔case fail-closed | #310 / AC7 | not_satisfied | 待实现 |
| R8 | 文本 + Contract + Outcome Evidence | #310 / AC8 | not_satisfied | 待实现 |
| R9 | Release Qualification Contract | #310 / AC9 | not_satisfied | 待实现；actual 外部 runs 待取得 |
| R10 | Release preflight 接线且保留三平台流程 | #310 / AC10 | not_satisfied | 待实现 |
| R11 | 不增加禁止机制/不放宽预算 | #310 / AC11 | satisfied | 当前计划与 Red test 不新增禁止项 |
| R12 | project-facing/plaintext + private parity | #310 / AC12 | not_satisfied | 待回归 |
| R13 | final-head CI/Review/merge/main/archive/closure/cleanup | #310 / AC13 | not_satisfied | 待交付 |
| R14 | 不执行 Release/Deploy | #310 / AC14 | satisfied | 本轮授权边界 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| router/review/specialist cores | Follow-up lifecycle Ownership 收口 | 跨 Skill 一致 | R1-R2 |
| routing conformance/context budget | exact/allowed + delta | 控制 over-disclosure | R3-R5 |
| evals/cases + evaluator | 九 case + registry validation | Outcome Evidence | R6-R8 |
| evals/release qualification + release.yml | behavioral qualification | Release Evidence | R9-R10 |
| managed/Runtime projection/USAGE/tests | project-facing 与守恒同步 | 不丢规则/不泄露内部身份 | R11-R12 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Outcome Eval registry/case/grader、Follow-up/repair/delegation contract |
| 接口 / 契约 | required | routing exact/allowed、qualification schema、Source/Runtime parity |
| 集成 / 持久化 / 运行依赖 | required | Runtime project payload/install/MCP/self-test |
| 用户 / 工作流验收 | required | simple-fp 与跨 Skill/多 Agent behavioral case 的 actual Evidence；无法运行的宿主明确 blocked |
| 跨组件关键路径 | required | canonical→routing→bundle/context→release preflight |
| 外部依赖 / 供应方探测 | not_applicable | 不新增 Provider/API；真实模型宿主 runs 作为外部 Evidence，不由本 PR 发明 Provider |
| 构建 / 打包 / 运行 | required | 现有 Linux/Windows/macOS package smoke 与 Release preflight |
| 文档 / 治理 / 其他 | required | Change/Issue/USAGE/managed projection/Review/CI |

## 验证计划

- 目标测试：新增 final release behavior contract、Outcome Eval registry/qualification、routing exact/allowed。
- 相关回归：现有 coding tests 全量。
- 静态检查或构建：现有 Release preflight / package selector。
- 专项真实边界：Runtime package smoke；actual host/model runs 只接受真实 artifact。
- 就绪检查：ready_check + current-head CI。

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

- [ ] upstream_re_read：最终 Ready 前重新读取 #310 与当前 main。
- [ ] change_coverage：逐条 #310 AC1-AC14 映射。
- [ ] reverse_audit：反查 Router/Review/Runtime/Eval/Release/USAGE 和 Context。
- [ ] unresolved_cleared：Ready 前清除所有 required not_satisfied；真实 external actual run 若不可得则不得伪造 satisfied。

# 完成证据与状态

## 新鲜证据

当前先建立 Red contract；Green、Review、CI、main-fresh 在后续填写。

## 未验证内容与剩余风险

- 当前宿主不能真实运行 Codex/Claude/Cursor/DeepSeek Harness 的模型任务，因此跨宿主 actual qualification 尚无 Evidence。
- 不会用 fixture、静态测试或当前 ChatGPT 会话冒充这些宿主 actual run。

## 交付状态

- Requirement Source：#310 open
- 分支：tech/final-release-behavior-qualification
- Change：in_progress
- PR：尚未创建
- CI/Review：待 Red commit 后建立
- merge/main-fresh/archive/closure/cleanup：待交付
- Release/Deploy：not_applicable

## 备注

本轮实施范围冻结为 #310 四类机制；除非实施中发现会直接使这四类机制错误或不可验证的 blocker，不新增其他优化项。
