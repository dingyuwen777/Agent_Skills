---
schema: coding-change/v1
id: CHG-20260919-122500-cross-model-outcome-eval-task-state
title: 提升跨模型一致性、Agent效果评测与长任务连续性
level: L3
status: in_progress
owner: dingyuwen777
branch: feature/cross-model-outcome-eval-task-state
created: 2026-09-19
updated: 2026-09-19
completion_gate: required
depends_on: []
affected_areas:
  - router-governance
  - coding-governance
  - figma-progressive-disclosure
  - runtime-task-state
  - agent-outcome-eval
  - multi-agent-collaboration
  - ci-evidence-selection
  - user-documentation
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/references/
  - .agents/skills/figma/
  - .agents/evals/
  - runtime/agent_skills_runtime/
  - .agents/skills/coding/tests/
  - .github/scripts/runtime_package_scope.py
  - README.md
  - USAGE.md
  - runtime/README.md
  - .agents/changes/active/CHG-20260919-122500-cross-model-outcome-eval-task-state/CHANGE.md
contracts:
  - Agent Skills Task Route
  - Agent Skills Runtime MCP Tool Contract
  - Agent Skills Task State
  - Agent Skills Outcome Eval
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 Agent_Skills 已能可靠约束路由、治理、验证和交付，但缺少跨模型统一的真实 Outcome Eval、可恢复的长任务语义状态，以及对持续膨胀 Skill Core 的更严格渐进披露控制。
- **拟议修改**：保持现有 Router/Coding/Testing/Review/Docs/Figma Owner，不新增 Planner/Research Skill；增加 model-neutral Outcome Eval/Trace 契约、Runtime Task State、Rule Effectiveness Gate、Delegation Contract，并把 Figma Core 的详细规则按原意迁入按需 Reference。
- **预期结果**：GPT、DeepSeek、GLM 或其他模型可以使用不同内部推理方式，但同一任务必须满足同一事实、权限、Evidence 和完成 Contract；维护者可以用真实任务运行结果比较模型/规则效果；大型任务可以恢复必要语义状态；轻量任务不会因完整 Figma/Coding 规则常驻而额外消耗上下文。

# 背景、现状与问题

## 背景

Requirement Source 为 #266。维护者明确要求全面实施并最终合并到主分支，同时明确排除 SEP-2640 Compatibility，并计划后续另行增加通用 Research/Analysis Skill。

## 当前现状

- Router、Coding、Testing、Review、Docs、Figma 已分 Owner，并由 canonical metadata + Runtime evaluator 做 required Context 渐进披露。
- 现有永久测试已覆盖 Routing Conformance、Context Budget、Source/Runtime parity、Runtime Bundle/Installer/MCP、Planning、Testing、Review、Figma 与 Git/CI 治理。
- Runtime 当前六 Tool 为 status、route_contract、start_task、submit_route、load_required_context、checkpoint；checkpoint 只证明 required Context 是否加载完成并保存当前阶段。
- 真实模型效果目前主要靠规则与机器 Contract 的间接测试，缺少统一 run artifact、grader 和 model-neutral case corpus。
- Figma SKILL Core 明显偏大，详细设计规则与按需 Reference 的职责边界仍可继续收窄。

## 问题、根因或约束

根因不是缺少更多顶层 Skill，而是三层 Contract 尚未闭环：

1. 执行效果层：不同模型没有统一的真实任务结果评测 Contract，无法用同一标准比较是否真的解决问题；
2. 长任务状态层：治理 Context 可恢复，但目标、决定、切片、Evidence、blocker 等 problem-solving state 仍主要依赖会话上下文；
3. 渐进披露层：部分 Core 已承载过多详细方法，需要以 Owner/Reference 路由而不是摘要删规则来控制。

## 不修改的后果

- 模型升级或更换后只能凭主观感觉判断 Skill 是否有效，容易继续累积针对旧模型的补偿规则。
- 长任务经过上下文压缩或宿主重建后容易重复调查、遗漏已确认决定或重新走失败假设。
- Skill Core 持续增长会增加所有任务的固定上下文，并使不同模型对同一规则集合的利用差异扩大。
- Multi-Agent 虽有 DAG/frontier 原则，但子任务输入/输出/Evidence 仍缺稳定最小契约。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | main 当前基线为 7d252cd5dd1ad76d8577f0826201b5d3676cb89c | GitHub main live readback | 本 Change 从该 revision 建分支 |
| E2 | Runtime 六 Tool 已固定，checkpoint 只返回 task/pass/phase | runtime/agent_skills_runtime/server.py + runtime.py | Task State 必须扩展现有 Tool，不新增第七 Tool |
| E3 | 当前 Router 不以模型身份作为路由维度 | runtime/agent_skills_runtime/routing.py ROUTE_DIMENSIONS | 跨模型一致性应做同 Contract，不做 model-specific route |
| E4 | 已有 Context Budget 与 Routing Conformance 永久测试 | test_route_context_budget.py / test_routing_conformance.py | 渐进披露改造必须用既有预算与路由测试证明 |
| E5 | Figma SKILL Core 当前约 900 行，详细规则已有多个专业 References | .agents/skills/figma/SKILL.md + references | 适合做内容守恒迁移，不应摘要删除 |
| E6 | #266 明确排除 SEP-2640 与 Research/Analysis Skill | #266 / 非目标 | 本次不得引入这两项 |
| E7 | 用户明确要求完成后合并 main | 当前 Requirement Source / 用户授权 | Requested Outcome 为 develop-and-deliver |

## 推断与待确认

无会阻塞当前方案的待确认业务决策。具体文件拆分位置可按当前 Ownership 和 Context Budget 在实现中局部调整；若需要改变六 Tool 数量、Route 顶层 schema、Project Payload/Release 形态或依赖版本，必须重新进入 Plan Review Gate。

# 目标、成功标准与非目标

## 目标

建立跨模型同效、真实可评测、长任务可恢复且仍保持渐进披露的 Agent_Skills 执行体系。

## 成功标准

- [ ] 同一项目任务不因模型品牌改变 Router/Owner/Reference/权限/Evidence/Completion Contract。
- [ ] Outcome Eval 可以校验 case/run、评分单次 run、比较多个模型/宿主结果，并明确区分真实模型 Evidence 与 deterministic fixture。
- [ ] Runtime Task State 可由 start_task 恢复、checkpoint 更新/读取，且 schema/大小/fail-closed 完整。
- [ ] Figma Core 明显收窄但所有旧详细规则仍在明确 Reference Owner 中完整可达。
- [ ] Rule Effectiveness Gate 与 Delegation Contract 被 canonical 规则和永久测试保护。
- [ ] 文档、CI selector、Runtime smoke/永久测试/PR CI/merge/main-fresh/archive/Issue Closure 完整闭环。

## 范围

- canonical Router/Coding/Figma 与相关 References。
- RuntimeStore/server 的 Task State。
- .agents/evals model-neutral eval assets。
- 受影响测试、CI selector 和三个人类说明入口。

## 非目标

- SEP-2640 Compatibility。
- 通用 Research/Analysis Skill。
- Provider-specific model SDK/Secret 集成。
- 按模型品牌维护独立 Skill/Reference。
- 未经需求批准的依赖/Runtime 升级。
- 目标业务仓库的具体业务规则。

## 必须保持不变

- canonical Ownership、Source Mode 与 Runtime Mode 双通路。
- 六个 MCP Tool 数量。
- encrypted Reference Bundle、required-context lazy load、route capability fail-closed。
- L1/L2/L3、Authorization Continuity、Fresh Evidence、Completion/Review/CI/Git 安全门禁。
- Project Payload/Installer ownership 和 Release 资产形态。
- 现有详细规则的触发、例外、失败/停止、验证、安全与兼容强度。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 不新增顶层 Skill；跨模型/Eval 属 Coding Mutation 治理，Task State 属 Runtime，Figma 细则仍属 Figma | E2-E6 | 避免第二控制面 |
| 接口与契约 | 保持六 Tool；start_task/checkpoint 以可选参数扩展 Task State；新增独立 Eval machine contract | E2 | Runtime Tool schema 变化需 L3 回归 |
| 数据与迁移 | 不写持久 Task State sidecar；checkpoint 返回的 state 可由宿主保存并在新 Runtime start_task 恢复 | 安装 ownership 与隐私边界 | 无磁盘 Migration |
| 错误与失败语义 | Task State 非法/过大/字段未知 fail closed；未运行真实模型不得标记 verified | #266 AC2-AC5 | 防止伪造兼容性 |
| 兼容性 | 现有不传 Task State 的 start/checkpoint 调用保持可用；Route 顶层 schema 不因模型变化分叉 | E2-E3 | 当前版本内增量兼容 |
| 部署与回滚 | 无生产部署；revert Implementation PR 回滚 | 源仓治理/Runtime 代码 | 不改变 Release 流程 |

## 备选方案与取舍

1. 按模型维护 GPT/DeepSeek/GLM 专属规则：拒绝，会形成多套 canonical 语义。
2. 只增加更多自然语言规则，不做 Eval/State：拒绝，不能证明效果，也不能解决长任务恢复。
3. 增加新的 Planner/Task Manager Skill：拒绝，现有 Coding Planning/Router Owner 已足够。
4. Task State 落磁盘 sidecar：当前不采用，会引入新的 ownership、隐私、安装和迁移边界。
5. Figma 直接摘要压缩：拒绝，违反内容守恒；采用原意迁移到按需 Reference。

# 修改方案与决策依据

## 最小充分方案

1. 建立 model-neutral 跨模型执行与 Rule Effectiveness canonical Reference，并增加 deterministic Outcome Eval harness/cases/fixtures。
2. 扩展 Runtime start_task/checkpoint 的可选 Task State，保持 route capability 与 required Context 独立。
3. 把 Figma Core 中适合按模式加载的详细规则迁入现有/新增 Reference，Core 仅保留必须常驻的不变量、模式、路由与 Handoff。
4. 在 Multi-Agent Owner 增加 Delegation Contract；主 Agent 仍负责最终 diff/集成/Evidence。
5. 同步 README/USAGE/runtime README、CI selector 与永久回归；通过 PR CI 后 guarded merge。
6. 合并后取得 main-fresh Evidence，等待 repository-native Change Archive，再逐 AC 回写 #266 并关闭。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E3 | 模型身份不是项目事实/风险/授权，不应进入 Router 分叉 |
| D2 | E2 | Task State 可在六 Tool 内扩展，不需要新控制面 |
| D3 | E4-E5 | 用 Reference 路由和现有 Context Budget 证明渐进披露，不抬阈值 |
| D4 | #266 AC2/AC3 | Eval/Trace 必须是可执行机器 Contract，而不是建议以后评测 |
| D5 | #266 AC7 | heuristic 可随模型能力变化，但 invariant/policy 不能静默降级 |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 跨模型同一 canonical 行为 Contract，不按模型分叉治理 | #266 / AC1 | not_satisfied | 待实现与测试 |
| R2 | model-neutral Outcome Eval cases/grader/compare | #266 / AC2 | not_satisfied | 待实现与测试 |
| R3 | Trace/Run Artifact Contract | #266 / AC3 | not_satisfied | 待实现与测试 |
| R4 | Runtime 结构化 Task State | #266 / AC4 | not_satisfied | 待实现与测试 |
| R5 | start/checkpoint resume + schema/size/fail-closed | #266 / AC5 | not_satisfied | 待实现与测试 |
| R6 | Figma/Coding 渐进披露且内容守恒 | #266 / AC6 | not_satisfied | 待迁移与 Context Budget |
| R7 | Rule Effectiveness Gate | #266 / AC7 | not_satisfied | 待实现与回归 |
| R8 | Multi-Agent Delegation Contract | #266 / AC8 | not_satisfied | 待实现与回归 |
| R9 | README/USAGE/runtime 文档同步并保持非目标 | #266 / AC9 | not_satisfied | 待同步 |
| R10 | 永久测试、PR CI、merge、main-fresh、archive、Closure | #266 / AC10 | not_satisfied | 待交付 Evidence |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Router / Coding Mutation Reference | model-neutral Contract、Rule Effectiveness Gate、Eval 路由 | 保持跨模型唯一 Owner | R1/R7 |
| .agents/evals | case/run/trace/grader/compare contract + fixture | 真实效果可量化 | R2/R3 |
| RuntimeStore / server | Task State validate/start/checkpoint/restore | 长任务连续性 | R4/R5 |
| Figma SKILL + References | 按原意迁移详细规则，收窄 Core | 渐进披露 | R6 |
| Multi-Agent Reference | Delegation Contract | 子任务边界一致 | R8 |
| tests / CI selector | 永久保护上述 Contract | 防回归 | R1-R10 |
| README / USAGE / runtime README | 用户与维护边界 | 可使用、可验证 | R9 |

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
| 行为 / 单元 / 组件 | required | Eval validator/grader/compare；Task State validator/start/checkpoint；内容守恒辅助检查 |
| 接口 / 契约 | required | Task Route model-neutral、MCP six-tool schema、Task State v1、Outcome Eval v1 |
| 集成 / 持久化 / 运行依赖 | required | RuntimeStore + stdio MCP smoke；无 sidecar persistence |
| 用户 / 工作流验收 | required | deterministic eval fixture 覆盖主要任务家族；USAGE 长任务恢复/跨模型用法 |
| 跨组件关键路径 | required | canonical rule → route/context → Runtime state/eval → CI |
| 外部依赖 / 供应方探测 | not_applicable | 不调用真实模型 Provider；真实模型兼容性只能由后续 run artifact 证明 |
| 构建 / 打包 / 运行 | required | changed-scope selector 决定的 Runtime compile/smoke/package；不手工降低 |
| 文档 / 治理 / 其他 | required | #266、Change、内容守恒、独立 Review、PR/main CI、archive/closure |

## 验证计划

- 目标测试：新增 Outcome Eval、Cross-model Contract、Runtime Task State、Figma progressive disclosure、Delegation Contract 回归。
- 相关回归：routing conformance、context budget、Source/Runtime parity、Runtime routing/MCP/bundle/project-facing projection。
- 静态检查或构建：由当前 selector/CI 对 changed scope 选择；Runtime 合同变化预计触发 compile/smoke/package。
- 专项真实边界：不调用真实 GPT/DeepSeek/GLM Provider；只验证未运行不得标记已验证的机器 Contract。
- 就绪检查：governance contract + ready_check + independent Review + PR required CI。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 内容守恒失败、Task State 变成隐式权限/事实源、Eval 形成模型专属规则 | old→new Review、schema fail-closed、model-neutral case contract |
| 兼容性 | 保留六 Tool 和旧的无 Task State 参数调用 | 可选参数 + permanent tests |
| 数据 / Migration | 不适用 | 不新增持久数据库/sidecar；state 显式 round-trip |
| 部署 / 运行 | Runtime binary 行为变化 | current CI 三平台 Evidence 由 selector/Workflow 决定 |
| 回滚 / 恢复 | revert PR | 无不可逆外部状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：README、USAGE、runtime/README 同步跨模型、Eval、Task State 使用/维护边界。
- **依赖 / Runtime**：修改 Runtime 代码但不升级 Python/MCP/PyInstaller/第三方依赖。
- **配置 / Secret**：不把 Provider Secret 写入仓库；真实 Eval run artifact 只接受脱敏输入。
- **部署 / Release**：本次不创建正式 Release；merge 后只验证 main 当前构建/CI。
- **兼容 / 消费方通知**：现有六 Tool 名称不变；Tool schema 新增可选参数需要 Runtime 文档与 smoke 更新。

# 完成审计

进入 ready_for_review 前重新读取 #266、当前 branch canonical Owner、实际 diff、测试/CI 与独立 Review，并从上游独立重建 AC1-AC10。

- [ ] upstream_re_read：重新读取全部上游正式事实源并独立重建完成定义。
- [ ] change_coverage：确认 R1-R10 覆盖全部 AC，没有用 Change 替代 Requirement。
- [ ] reverse_audit：从不同模型执行、长任务恢复、Figma review/design-to-code、多 Agent、Git delivery 反查规则→实现→测试→文档。
- [ ] unresolved_cleared：所有 not_satisfied 清零；N/A/未验证有正式依据。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | branch 基线 | GitHub live readback main@7d252cd | 通过 | 当前分支基线已固定 |
| V2 | #266 live | GitHub live Issue readback | 通过 | AC1-AC10/非目标完整 |

## 未验证内容与剩余风险

- 当前尚未实现，因此 R1-R10 仍未满足。
- 本仓没有内置 GPT/DeepSeek/GLM Provider 凭据；本次只建立统一 Eval Contract，不会伪造真实模型兼容结论。

## 交付状态

- 提交：进行中
- 拉取请求：未创建
- CI：未运行当前分支
- 合并：未合并
- Change 归档：未归档
- 发布 / 部署：不适用；本次不创建正式 Release。

## 备注

用户已明确授权完成后合并到 main；merge 仍必须满足 current-head Review/CI、expected head guard、main-fresh、repository-native Change Archive 和 Requirement Closure。
