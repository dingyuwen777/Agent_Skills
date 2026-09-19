---
schema: coding-change/v1
id: CHG-20260919-151144-general-analysis-research-skills
title: 增加通用 Analysis 与 Research Skills
level: L3
status: proposed
owner: dingyuwen777
branch: feature/general-analysis-research-skills
created: 2026-09-19
updated: 2026-09-19
completion_gate: required
depends_on: []
affected_areas: [router, analysis, research, evals, docs, runtime-distribution]
affected_paths: [.agents/skills, evals, README.md, USAGE.md]
contracts: [agent-routing-v1, project-payload-v2, outcome-eval-v1]
data_changes: none
---

# 变更摘要

- **要解决的问题**：通用分析、外部研究和长期回答原则仍依赖宿主侧长全局指令，Agent_Skills 没有对应 canonical Owner。
- **拟议修改**：新增 analysis / research 两个正式能力域，补 Router、通用回答不变量、Outcome Eval、文档与 Runtime 动态发现回归；不新增控制面、MCP Tool 或模型专属分支。
- **预期结果**：复杂分析与研究可从同一仓库按需加载规则，简单问答保持 fast path，网页端全局指令缩成薄 Bootstrap。

# 背景、现状与问题

## 背景

用户要求把现有网页端全局指令中可跨项目复用的分析、研究与回答原则收敛到 Agent_Skills，并最终合并 main，使后续 ChatGPT/Codex/DeepSeek/GLM 等宿主只需要一个薄入口。

## 当前现状

当前 main 为 `42d6e150a1abc86f6957bb6659f3b5a4ce244a06`。正式能力域包含 router、coding、testing、review、docs、figma；Runtime 从根一级 Skill 目录动态发现，公开 MCP Tool 保持六个；Outcome Eval 已有工程任务族，但没有通用 Analysis / Research case。

## 问题、根因或约束

缺口不是工程治理规则不足，而是通用问题求解没有 canonical Owner。若把现有长全局指令整体塞进入口，会破坏渐进式披露；若把普通“分析/方案”继续交给 Coding，则非工程问题会误入工程流程。

## 不修改的后果

不同宿主继续重复维护长全局提示词；研究时效、一手来源、第一性原理、阶段化方案等长期规则无法统一验证，且模型升级后难用同一 Outcome Eval 判断效果。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前正式能力域没有 analysis / research | 当前 main 动态 Skill Catalog / Router | 需要新增独立 Owner |
| E2 | Runtime 按 `.agents/skills/<name>/SKILL.md` 动态发现 | coding.reference.14 | 不新增静态白名单或第七 MCP Tool |
| E3 | Coding Owner 会对“只读分析/方案”宽匹配 | coding/SKILL.md agent-routing:v1 | 新通用意图必须从 Coding 默认 Owner 排除 |
| E4 | Outcome Eval 已支持 model-neutral case/run/compare | evals/agent_outcome_eval.py | 新任务族应复用现有评测 Contract |
| E5 | 用户明确要求第一性原理、简洁、项目实际、阶段化方案、默认最新资料 | #270 / AC1-AC4 | 形成 Analysis/Research 核心行为 Contract |

## 推断与待确认

无。当前范围、交付终点与非目标已由 #270 明确。

# 目标、成功标准与非目标

## 目标

让通用分析与外部研究成为可路由、可按需披露、可评测的正式能力，同时让全局指令只承担 Bootstrap。

## 成功标准

- [ ] #270 / AC1-AC10 均有实现或交付证据。
- [ ] 简单问答不加载 Analysis/Research/Coding；通用分析、研究、组合场景分别命中正确 Owner。
- [ ] 新能力可由现有动态 Runtime/Project Payload 发现，现有工程任务回归不退化。

## 范围

- 新增 analysis / research Core、References、agent metadata。
- 调整 Router 与 Coding 路由，增加通用回答不变量。
- 增加 Outcome Eval cases、routing/preservation/runtime projection 回归。
- 更新 README / USAGE 的薄全局 Bootstrap。

## 非目标

- SEP-2640、Planner/Worker、数据库/向量记忆、模型专属规则。
- 把简单日常问答强制进入复杂流程。
- 重写现有工程专业规则或提高 Context Budget。

## 必须保持不变

- Runtime 六个公开 Tool。
- Source/Runtime 同源路由与 exact required Context。
- L1/L2/L3、权限、Evidence、Review、CI、Git 安全边界。
- 项目自身事实优先于通用方法。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Analysis 负责推理/方案；Research 负责外部取证；工程 Owner 保持现状 | E1/E3/#270 | Router/Handoff |
| 接口与契约 | 复用现有 agent-routing/v1 与公开 Task Route 维度，不新增顶层协议 | E2 | Runtime 路由清单会新增动态 Skill/词汇 |
| 数据与迁移 | 不适用：无业务 Schema/持久化数据 | #270 非目标 | 无 Migration |
| 错误与失败语义 | 必需来源不可得时只限制依赖该来源的结论；不得编造 | #270 / AC3-AC4 | Research fail-closed |
| 兼容性 | 现有工程路由必须不退化；简单问答保留 fast path | #270 / AC5-AC8 | 新增正反例 |
| 部署与回滚 | 通过普通 PR/Release 动态发现；回滚为回退本变更 | E2 | 无独立部署步骤 |

# 修改方案与决策依据

## 最小充分方案

1. 新增两个薄 Core 与按需 References；验证：metadata compiler + 内容 marker + Core 体积回归。
2. Router 增加通用回答 Contract 和 Owner/Handoff；Coding 排除纯 Analysis/Research 意图；验证：routing conformance 正反例。
3. Outcome Eval 增加 Analysis/Research/simple-answer cases；验证：现有 grader/schema tests。
4. 更新 README/USAGE；验证：文档链接与用户面回归。
5. 依赖现有动态 Catalog/Project Payload 自动分发；验证：Source/Runtime parity 与 package gate。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1/E3 | 独立 Owner 比继续扩 Coding 更能避免非工程任务误路由 |
| D2 | E2 | 动态发现已存在，不应新增第二套 Catalog/Tool |
| D3 | E4 | 复用 Outcome Eval 避免新建分析/研究评测框架 |
| D4 | E5 | 把用户长期稳定原则放 canonical，宿主仅保留薄 Bootstrap |

## 备选方案与取舍

- 单一 Research/Analysis 大 Skill：职责混合、触发过宽，不采用。
- 把全部规则放根 AGENTS/Router：会让所有任务预付上下文，不采用。
- 新增“任务域”顶层路由维度：当前 intent + Owner projection 已足够表达，会扩大 Runtime Contract，不采用。
- 为不同模型维护专属规则：违背跨模型同一 Contract，不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Analysis 第一性原理/前提/事实分层 | #270 / AC1 | not_satisfied | 尚未实现 |
| R2 | 最小充分与阶段化方案 | #270 / AC2 | not_satisfied | 尚未实现 |
| R3 | Research 默认最新适用资料 | #270 / AC3 | not_satisfied | 尚未实现 |
| R4 | Research 来源/冲突/引用/停止规则 | #270 / AC4 | not_satisfied | 尚未实现 |
| R5 | Router 正确区分与组合 | #270 / AC5 | not_satisfied | 尚未实现 |
| R6 | 渐进披露与薄通用入口 | #270 / AC6 | not_satisfied | 尚未实现 |
| R7 | Runtime 动态发现且六 Tool 不变 | #270 / AC7 | not_satisfied | 尚未验证 |
| R8 | Eval 与正反例回归 | #270 / AC8 | not_satisfied | 尚未实现 |
| R9 | README/USAGE 与薄 Bootstrap | #270 / AC9 | not_satisfied | 尚未实现 |
| R10 | 完整 PR/main 交付闭环 | #270 / AC10 | not_satisfied | 尚未完成 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| .agents/skills/analysis | 新增 Core/Refs/agent metadata | 通用分析 Owner | R1/R2/R6 |
| .agents/skills/research | 新增 Core/Refs/agent metadata | 外部研究 Owner | R3/R4/R6 |
| Router/Coding metadata | Owner 选择与排除误命中 | 组合路由 | R5 |
| evals + tests | 新 case 与永久正反例 | 可验证效果 | R7/R8 |
| README/USAGE | 使用说明与薄 Bootstrap | 用户入口 | R9 |

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
| 行为 / 单元 / 组件 | required | Analysis/Research 内容与 Outcome Eval case contract |
| 接口 / 契约 | required | agent-routing metadata、Owner selection、六 MCP Tool 不变 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无业务持久化；Runtime 分发由构建/运行层验证 |
| 用户 / 工作流验收 | required | 简单问答/分析/研究/组合路由与薄 Bootstrap |
| 跨组件关键路径 | required | Source metadata → Runtime manifest → Project Payload |
| 外部依赖 / 供应方探测 | not_applicable | 本变更不需要真实付费 Provider 调用 |
| 构建 / 打包 / 运行 | required | classifier 要求的 Runtime package/platform gate |
| 文档 / 治理 / 其他 | required | README/USAGE、Change、Review、Issue closure |

## 验证计划

- 目标测试：新增 Analysis/Research routing + content + Outcome Eval tests。
- 相关回归：完整 self-contained Agent Skills tests。
- 静态检查或构建：metadata/compiler、Python compile、CLI smoke（按 CI selector）。
- 专项真实边界：Runtime dynamic discovery / Project Payload / real MCP / platform package（按 required CI）。
- 就绪检查：ready_check + Requirement/Completion Audit。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | Owner 重叠导致上下文膨胀或普通问答误路由 | 正反例和 Coding exclusion 回归 |
| 兼容性 | 保持现有工程语义；只新增通用能力 | 不改顶层 Task Route 协议和 Runtime Tool |
| 数据 / Migration | 不适用 | 无持久化数据变化 |
| 部署 / 运行 | 正式 Release 后动态发现新能力 | 现有 Project Payload v2 |
| 回滚 / 恢复 | 回退本 PR 即可 | 无不可逆数据/外部副作用 |

# 文档、依赖、部署与发布影响

- **长期文档**：README / USAGE 需要同步新能力和薄 Bootstrap。
- **依赖 / Runtime**：不新增依赖、不升级 Runtime。
- **配置 / Secret**：不改变。
- **部署 / Release**：无需新增发布步骤；现有三平台包动态包含正式能力。
- **兼容 / 消费方通知**：最终用户只需按新版 USAGE 使用；旧工程能力不改变。

# 完成审计

- [ ] upstream_re_read：完成前重新读取 #270 与当前 main/PR 事实。
- [ ] change_coverage：确认 AC1-AC10 全覆盖。
- [ ] reverse_audit：从简单问答/Analysis/Research/工程组合反向核对路由、Runtime 与文档。
- [ ] unresolved_cleared：所有 not_satisfied 清零。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | 待填写 | 待填写 | 待填写 | 待填写 |

## 未验证内容与剩余风险

尚未实施和验证。

## 交付状态

- 提交：待完成
- 拉取请求：待创建
- CI：待运行
- 合并：待完成
- Change 归档：待完成
- 发布 / 部署：不适用；本任务不创建正式 Release。

## 备注

无。
