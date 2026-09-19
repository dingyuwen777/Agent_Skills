---
schema: coding-change/v1
id: CHG-20260919-145000-analysis-research-skills
title: 增加通用 Analysis / Research Skills 与薄全局 Bootstrap
level: L3
status: in_progress
owner: dingyuwen777
branch: feature/analysis-research-skills
created: 2026-09-19
updated: 2026-09-19
completion_gate: required
depends_on: []
affected_areas:
  - general-analysis
  - external-research
  - routing
  - progressive-disclosure
  - agent-outcome-eval
  - runtime-distribution
  - documentation
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/analysis/
  - .agents/skills/research/
  - .agents/skills/coding/tests/
  - evals/
  - README.md
  - USAGE.md
contracts:
  - Agent Skills canonical routing
  - Agent Skills Analysis
  - Agent Skills Research
  - Agent Skills Outcome Eval
data_changes: []
---

# 变更摘要

- **要解决的问题**：网页端全局指令仍承担大量通用分析、研究和回答原则，无法与 Agent_Skills 的渐进式披露、跨模型同源治理统一。
- **拟议修改**：新增独立的 Analysis 与 Research Owner；Router 只增加最小通用回答契约和组合路由；详细分析/研究方法进入按需 Reference；扩展 Outcome Eval、文档与动态分发回归。
- **预期结果**：网页端以后只保留薄 Bootstrap，复杂分析/研究从当前 canonical Agent_Skills 按需取得；简单问答不机械加载，工程任务不被通用 Analysis/Research 误接管。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #272。用户要求本次直接完成新增、验证并合并 main，同时要求两个新 Skill 符合当前全局工作原则：客观直接、纠错前提、事实/推断/建议/未知分离、第一性原理、现实方案优先、避免大而全、必要时按“当下方案 → 阶段演进 → 理想方案”表达；外部研究除明确历史/离线/限定资料外默认联网取得最新资料。

本轮还核对了 2026-09-19 当前资料：OpenAI 对新模型建议减少过度脚手架、缩短 Skill description；Anthropic Agent Skills 强调 progressive disclosure、按需 Context 和先评测再迭代；成熟社区 Research Skill 强调 claim 追到一手 source owner。只吸收可跨模型成立的原则，不复制供应商或仓库专属控制面。

## 当前现状

- 当前正式 Skill 为 router/coding/testing/review/docs/figma，动态 Catalog 可自动发现新增 Skill。
- Router 已有 Owner-gated routing、Fresh Evidence、Authorization Continuity、Cross-model Behavior Contract。
- Outcome Eval 已能以 model-neutral case/run/grader/compare 记录 actual/fixture，但当前 case 主要覆盖工程任务。
- Runtime/Project Payload 已有动态 Skill 分发与 project-facing projection，不要求新增静态白名单。
- 当前没有通用非工程 Analysis/Research Owner，因此网页端全局指令承担了本应长期复用的方法。

## 问题、根因或约束

1. 把全部通用原则继续写在网页端会形成第二套长期事实源，并让不同宿主难以共享。
2. 把这些原则全部塞进 Router/AGENTS 又会扩大每次任务的常驻 Context。
3. Analysis 与 Research 若不分 Owner，会把“已有事实上的推理”和“需要外部最新证据的研究”混在一起。
4. 新模型更强后，过度细化步骤可能限制模型；规则应保持硬不变量明确、方法按需加载。

## 不修改的后果

- 网页端仍需维护大篇幅全局指令；
- Research 容易停在二手摘要、旧资料或无边界搜索；
- 通用方案容易脱离真实场景给大而全架构；
- 不同宿主对通用回答原则的使用继续漂移。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | #272 明确 AC1-AC14 与用户补充要求 | GitHub Issue #272 | 本 Change Requirement Source |
| E2 | 正式 Skill/Reference 由动态 Catalog 发现 | current main runtime + test_dynamic_skill_distribution.py | 不增加静态白名单 |
| E3 | Router 已有 owner-gated routing 与模型无关 Contract | current main router/SKILL.md | 新 Skill 走现有固定点 |
| E4 | Anthropic Agent Skills 将 name/description、SKILL body、linked files作为逐级披露，并建议从 Eval 迭代 | Anthropic 2025-10-16 / 2025-12 update | Core 薄、References 按需、加入 Eval |
| E5 | OpenAI 2026-09-11 建议新模型下缩短 Skill description、减少过度提示脚手架 | OpenAI Developers | description 精准、不过度流程化 |
| E6 | 成熟社区 Research Skill 要求事实追到 primary source owner | mattpocock/skills current main research | 一手来源优先 |

## 推断与待确认

无阻塞待确认。具体 Reference 数量以最小充分为准，不为了“看起来完整”制造章节。

# 目标、成功标准与非目标

## 目标

让 Agent_Skills 同时成为工程研发、通用分析和外部研究的长期 canonical 方法源，并把网页端全局指令收缩为薄 Bootstrap。

## 成功标准

- [ ] Analysis 能按 #272 AC1-AC3、AC7-AC9 执行。
- [ ] Research 能按 #272 AC4-AC6、AC7-AC9 执行。
- [ ] Router 通用回答契约与 Owner 组合不污染简单问答/工程 Owner。
- [ ] Outcome Eval 覆盖新任务族与关键负例。
- [ ] 动态 Runtime/Project Payload 自动发现新 Skills。
- [ ] README/USAGE 与最终全局 Bootstrap 同步。
- [ ] required CI、Review、merge、main-fresh、Archive、Issue Closure 完整闭环。

## 范围

- 新增 analysis/research Skill Core、References、可选宿主 metadata；
- Router 最小回答契约与路由导航；
- Outcome Eval cases、routing/context/projection/preservation 测试；
- README/USAGE；
- 本仓库 Change/PR/CI/Git 生命周期。

## 非目标

- 不新增 Planner/Worker、后台研究控制面或万能 Provider Runner；
- 不改变 Runtime 六 Tool；
- 不引入 SEP-2640；
- 不把网页端产品特定 UI 指令写入通用 Skill；
- 不要求简单翻译、算术、短改写等日常问题加载专项 Skill；
- 不按 GPT/DeepSeek/GLM 分叉规则。

## 必须保持不变

- 现有工程 Skills 的 Ownership 与硬门禁；
- Source/Runtime 同源路由、动态 Catalog、private required Context；
- 项目事实和更高优先级指令优先；
- 权限、Fresh Evidence、Completion Scope 与模型无关行为 Contract。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 新增 Analysis / Research 独立 Owner，现有工程 Owner 不变 | #272 AC1-AC9 | 非工程分析不误入 Coding |
| 接口与契约 | 只扩展 canonical routing vocabulary / dynamic catalog，不改 Runtime 六 Tool | #272 AC7/AC11/AC13 | 保持 MCP 公共面 |
| 数据与迁移 | 不适用；无 Schema/持久数据变更 | 当前任务事实 | 无 Migration |
| 错误与失败语义 | 证据不足/无法联网/来源冲突时显式降级，不得编造确定性 | #272 AC4-AC6 | Research fail-closed |
| 兼容性 | 现有 Skill/Reference Stable ID、工程路由和用户项目事实优先级保持 | current main | 不破坏既有任务 |
| 部署与回滚 | merge 后进入现有 Runtime 动态分发；回滚为 revert PR | E2 | 无独立部署机制 |

# 修改方案与决策依据

## 最小充分方案

1. 先增加永久 Red 测试，证明当前缺少两个 Owner、路由和关键语义。
2. 新增 Analysis Core + 按需 References：问题/前提、第一性原理与因果、方案/阶段决策、复杂拆解与不确定性。
3. 新增 Research Core + 按需 References：研究问题/检索、来源层级、一手事实与时效、冲突/不确定性/引用与停止。
4. Router 只加入通用回答硬契约与 Analysis/Research Owner 触发、组合关系；不复制详细方法。
5. 扩展 Outcome Eval 与路由/Context/Runtime Projection 回归。
6. 同步 README/USAGE，最终给用户薄全局 Bootstrap。
7. 独立 Review、required CI、guarded merge、main-fresh、repository-native archive、关闭 #272。

## 备选方案与取舍

- 单个“大 Research+Analysis Skill”：拒绝，触发范围重叠且 Core 易膨胀。
- 把当前网页全局指令整段搬到 AGENTS/Router：拒绝，破坏渐进披露。
- 新增模型专属规则：拒绝，与 Cross-model Contract 冲突。
- 固定模板如 SWOT/MECE/三方案：拒绝，方法应服从真实问题，不让模型模板化。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Analysis 基础能力 | #272 / AC1 | not_satisfied | Red test 待实现 |
| R2 | 通用回答原则 | #272 / AC2 | not_satisfied | Red test 待实现 |
| R3 | 现实/阶段化方案 | #272 / AC3 | not_satisfied | Red test 待实现 |
| R4 | Research 最新资料默认 | #272 / AC4 | not_satisfied | Red test 待实现 |
| R5 | 一手来源/冲突/不可编造 | #272 / AC5 | not_satisfied | Red test 待实现 |
| R6 | Research Stop Rule | #272 / AC6 | not_satisfied | Red test 待实现 |
| R7 | Router 组合与简单问答边界 | #272 / AC7 | not_satisfied | Red test 待实现 |
| R8 | 渐进式披露与短 description | #272 / AC8 | not_satisfied | Red test 待实现 |
| R9 | 吸收当前最佳实践但不引入专属控制面 | #272 / AC9 | not_satisfied | E4-E6 + 待实现 |
| R10 | Outcome Eval 新任务族/负例 | #272 / AC10 | not_satisfied | 待实现 |
| R11 | 动态分发无静态白名单 | #272 / AC11 | not_satisfied | 待验证 |
| R12 | README/USAGE/薄 Bootstrap | #272 / AC12 | not_satisfied | 待实现 |
| R13 | 保持六 Tool/无 Planner/无 SEP-2640 | #272 / AC13 | not_satisfied | 待验证 |
| R14 | 完整交付闭环 | #272 / AC14 | not_satisfied | 待交付 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| analysis/ | Core、References、host metadata | 通用推理/决策 Owner | R1-R3/R7-R9 |
| research/ | Core、References、host metadata | 最新外部证据 Owner | R4-R9 |
| router/SKILL.md | 通用回答契约、Owner 选择与组合 | 防误路由 | R2/R7 |
| evals/ + tests | Analysis/Research cases、负例、routing/context/runtime projection | 可回归证明 | R8-R11 |
| README.md / USAGE.md | 使用方式与薄 Bootstrap 说明 | 最终用户可用 | R12 |

- [x] 调查当前实现和事实源
- [x] 建立 Change 与 Red 目标
- [ ] 建立可证明缺口的失败回归
- [ ] 完成最小实现
- [ ] 同步长期文档
- [ ] 取得 current-head 验证
- [ ] 完成独立 Review 与 Completion Audit

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 新 Skill 语义、trigger、Reference 可达性、Eval cases |
| 接口 / 契约 | required | routing metadata、动态 Catalog、公开 route contract |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不新增外部持久化/服务；Runtime 分发归构建/运行层 |
| 用户 / 工作流验收 | required | 通用分析、最新研究、组合研究+分析、简单问答负例 |
| 跨组件关键路径 | required | Source → Router → Skill/Reference → Runtime Project Payload |
| 外部依赖 / 供应方探测 | required | 本轮外部最佳实践仅作设计证据，使用当前官方/一手资料；不调用模型 Provider |
| 构建 / 打包 / 运行 | required | 当前 classifier/required CI 决定 package 证据 |
| 文档 / 治理 / 其他 | required | #272、Change、README/USAGE、Review、Archive/Closure |

# 风险、兼容性、迁移与回滚

- 主要风险：通用 Skill 误触发工程任务、Research 无边界联网、Core 变长。
- 兼容性：仅动态新增 Owner/路由词汇；不改变六 Tool、现有 Stable ID。
- 数据/Migration：不适用，无数据变更。
- 部署/运行：新增 Skill 会进入 Runtime Project Payload，需现有动态分发测试/required package gate。
- 回滚：revert Implementation PR；无外部不可逆数据。

# 文档、依赖、部署与发布影响

- **长期文档**：README/USAGE 需要同步新增通用 Analysis/Research 的使用方式和薄全局 Bootstrap；不建立第二套完整规则。
- **依赖 / Runtime**：不新增第三方依赖；Runtime 继续依赖动态 Catalog/Project Payload。
- **配置 / Secret**：不新增配置或 Secret；Research 不把 Provider 凭据写入规则/仓库。
- **部署 / Release**：不创建正式 Release；是否需要三平台 package evidence 由当前 changed-scope classifier/required gate 决定。
- **兼容 / 消费方通知**：现有工程任务自然语言和 Runtime 六 Tool 不变；新增通用任务路由词汇。

# 完成审计

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 42d6e150 | canonical reread + #272 | 已确认 | 写入前 Requirement/Ownership 新鲜 |
| V2 | 2026-09-19 web | OpenAI / Anthropic / Agent Skills / mattpocock research | 已核对 | 当前最佳实践约束 |

## 未验证内容与剩余风险

当前处于 Red / implementation 前阶段；实现、CI、Review、merge/main-fresh/archive 尚未完成。

## 交付状态

- 提交：Red commit 待创建。
- 拉取请求：待创建 Draft PR。
- CI：待运行。
- 合并：未合并。
- Change 归档：未归档。
- 发布 / 部署：不适用；本次不创建 Release。

# 备注

用户已明确授权本任务完成后合并 main。
