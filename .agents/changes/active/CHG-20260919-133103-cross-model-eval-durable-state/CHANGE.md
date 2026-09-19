---
schema: coding-change/v1
id: CHG-20260919-133103-cross-model-eval-durable-state
title: 提升跨模型一致性、真实效果评测与长任务连续性
level: L3
status: ready_for_review
owner: dingyuwen777
branch: feature/cross-model-eval-durable-state
created: 2026-09-19
updated: 2026-09-19
completion_gate: required
depends_on: []
affected_areas:
  - cross-model-behavior
  - agent-outcome-eval
  - durable-task-state
  - progressive-disclosure
  - multi-agent-delegation
  - runtime-mcp
  - figma-governance
  - ci
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/
  - .agents/skills/figma/
  - runtime/agent_skills_runtime/
  - evals/
  - .agents/skills/coding/tests/
  - .github/scripts/runtime_package_scope.py
  - .github/workflows/skill-tests.yml
  - README.md
  - USAGE.md
  - runtime/README.md
contracts:
  - Agent Skills canonical routing
  - Agent Skills MCP工具契约/v3
  - Agent Skills Task State
  - Agent Skills Outcome Eval
data_changes: []
---

# 变更摘要

- 要解决的问题：当前 Agent_Skills 已能稳定约束路由、治理、验证和交付，但还缺少跨模型统一的真实 Outcome Eval、可恢复的长任务语义状态，并且部分 Skill Core 已开始膨胀，可能降低不同模型下的渐进披露效果。
- 拟议修改：保持现有 Router/Coding/Testing/Review/Docs/Figma Owner，不新增 Research/Analysis 或 Planner；增加 model-neutral Outcome Eval/Trace、Durable Task State、Rule Effectiveness Gate、Delegation Contract，并把过大的 Figma Core 以内容守恒方式迁移到按需 Reference。
- 预期结果：GPT、DeepSeek、GLM 或其他模型可以采用不同推理过程，但同一任务使用同一 canonical Contract、同一 required Context、同一完成/Evidence 标准，并能用同一 Eval 判断真实任务效果；长任务可以恢复必要语义状态，渐进披露保持有效。

# 背景、现状与问题

## 背景

Requirement Source 为 #266。维护者明确要求全面系统修改 Agent_Skills，使不同能力模型对同一套 Agent_Skills 的使用效果尽可能一致，同时保持渐进式披露，并明确禁止为了缩短文本而总结、弱化或丢失规则效果；本次还明确排除 SEP-2640 Compatibility 与 Research/Analysis Skill。

## 当前现状

- canonical Router 已使用中文 machine routing metadata、Stable ID、dependency closure、risk floor 和 Source/Runtime parity。
- Runtime 已有六个 MCP Tool、task capability、required-context lazy load、Context Budget 和 exact canonical text。
- Coding 已有 Planning Contract、Vertical Slice、DAG/frontier、Completion/Evidence/Git 交付。
- 当前永久测试主要证明文本/路由/Runtime Contract，而没有统一真实 Agent Outcome Eval Contract。
- Runtime checkpoint 主要证明 required Context 是否已加载以及当前阶段，不承载目标、决定、切片、Evidence、blocker 等问题求解状态。
- Figma Skill Core 明显大于其他 Core，需要继续渐进披露，但所有原规则必须保持完整可达。

## 问题、根因或约束

1. 跨模型一致性缺少可测结果层：只要求模型遵守同一规则不足以证明真实任务结果一致。
2. Runtime 只持有治理加载状态：长任务语义进度仍主要依赖模型上下文。
3. Skill Core 增长会侵蚀渐进披露，但简单删减会破坏内容守恒。
4. 长期 invariant/policy 与为弥补模型弱点而增加的 heuristic/technique 目前缺少显式生命周期与 Eval 门禁。

## 不修改的后果

- 不同模型都读到规则，但真实任务成功率、越权率、重复工具调用、用户纠正次数和最终交付质量无法横向比较。
- 超长任务可能在上下文压缩后重复调查、忘记已经否定的方案或错误扩大范围。
- Figma/Coding Core 继续增长，让强弱模型都承担不必要上下文。
- 历史模型补丁型规则只能累积，难以用数据证明可以降级或删除。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | #266 明确 AC1-AC10、排除 SEP-2640 和 Research/Analysis | live GitHub Issue #266 | 本 Change 的 Requirement Source |
| E2 | Runtime 稳定公开 Tool 当前恰好六个，checkpoint 仅返回 task/pass/phase/progress | current main Runtime/server canonical | Task State 在现有 Tool 内扩展 |
| E3 | Runtime 使用 capability + required-context lazy load + Source/Runtime parity | current main Runtime/canonical Reference | 新状态不能绕过 route token |
| E4 | Router/Coding 已有 owner-gated routing、Fresh Evidence、Authorization Continuity | current main Router/Coding | 模型差异不能成为第二套治理分支 |
| E5 | Figma Core 明显大于其他 Skill Core，且已有多个专项 References | current main canonical Figma | 通过迁移做渐进披露 |
| E6 | 当前 tests 覆盖 routing/context budget/planning/runtime parity，但没有 Outcome Eval contract | current main test inventory | Eval/Trace 是独立能力 |

## 推断与待确认

无阻塞待确认。具体文件拆分在实现前继续从当前 canonical Figma/Runtime/CI 事实收敛，不需要用户再次决策。

# 目标、成功标准与非目标

## 目标

建立一套模型无关、结果可测、状态可恢复、上下文按需加载的 Agent_Skills 执行体系，并保证当前详细治理语义不因拆分或模型能力差异而降低。

## 成功标准

- [x] 同一任务不因模型品牌改变 canonical 路由、风险、权限、Evidence 或完成 Contract。
- [x] Outcome Eval 能以同一 case/grader 比较多个模型/宿主的真实运行结果，未实际运行的模型明确为未验证。
- [x] Trace/Run Artifact 能保存可用的过程与结果证据，缺失数据显式 unavailable，不编造。
- [x] Runtime Task State 可创建、更新、读取、恢复，并保持六 Tool、capability 和 required-context 安全边界。
- [x] Figma Core 显著收窄，但移出的规则逐段完整迁移且代表场景仍可达。
- [x] Rule Effectiveness Gate 能区分 invariant/policy/heuristic/technique，并将 heuristic 的变更与真实失败或 Eval Evidence 关联。
- [x] Multi-Agent Delegation Contract 明确子任务输入/边界/输出/Evidence，父 Agent 保留最终集成责任。
- [x] README/USAGE/runtime 文档同步，明确不包含 SEP-2640 和 Research/Analysis。
- [x] 开发侧实现、文档与独立 Review 已达到 PR Ready 候选；三平台 package、merge、main-fresh、Archive 与 Requirement Closure 由下游交付门禁继续 fail-closed 持有。

## 范围

- canonical Router/Coding/Figma 规则与相关 References；
- Runtime Task State 与 MCP 参数/响应兼容扩展；
- Outcome Eval/Trace 机器 Contract、fixture、grader/compare 和测试；
- Context Budget/preservation/routing/parity/CI selector；
- README、USAGE、runtime README。

## 非目标

- SEP-2640 Compatibility；
- 通用 Research/Analysis Skill；
- 按模型品牌复制 Skill/Reference；
- 新 Planner/Task Manager/Worker Queue 控制面；
- 静默升级依赖、Runtime、Python 或 MCP SDK；
- 改变外部业务仓库的项目特定事实；
- 用摘要替代现有详细规则。

## 必须保持不变

- Source Mode canonical Ownership 与 Runtime private execution parity；
- Router/Coding/Testing/Review/Docs/Figma 现有 Owner；
- L1/L2/L3、Authorization Continuity、Fresh Evidence、Requirement Traceability、Completion Audit；
- Runtime encrypted Bundle、project-facing Projection、six-tool MCP、Installer ownership、三平台 Release 资产形态；
- 现有详细规则中的触发、例外、失败/停止、验证、安全、兼容和 Handoff 语义。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 保持现有顶层 Skill Owner；新增能力进入现有 Coding/Runtime/Figma Owner 和 evals 机器资产 | #266 AC1/AC6/AC8 | 不新增 Planner/Research Skill |
| 接口与契约 | 保持六 MCP Tool；允许 start/checkpoint 参数/响应向后兼容扩展 Task State | #266 AC4/AC5 + E2/E3 | MCP Contract 需新永久测试与 smoke |
| 数据与迁移 | Task State 默认进程内，显式 resume payload 由宿主提供；不新增磁盘隐式 sidecar | 当前 Runtime 边界 | 无项目数据 Migration |
| 错误与失败语义 | 非法/超限 Task State fail closed；缺失 Eval telemetry 标记 unavailable；未真实运行模型不得声明兼容 | #266 AC2-AC5 | 避免伪造状态或评测 |
| 兼容性 | 旧 start_task(id, phase) / checkpoint(token, phase) 调用保持合法；新增字段可选 | 当前版本内行为保持 | 不做历史跨版本迁移 |
| 部署与回滚 | 无生产部署；回滚为 revert Implementation PR | 源仓库变更 | 无外部数据恢复 |

# 修改方案与决策依据

## 最小充分方案

1. Cross-model Outcome Contract：在 Coding canonical 增加模型无关行为、Eval、Rule Effectiveness 规则；模型标签只属于 Eval，不进入 Router trigger。
2. Eval/Trace executable contract：新增 evals 目录的 stdlib schema/validator/grader/compare、cases/fixtures；不绑定特定 Provider SDK。
3. Durable Task State：Runtime 新增有界 schema validator；start_task 支持可选恢复状态，checkpoint 支持可选状态 patch 并返回当前状态；六 Tool 名称不变。
4. Progressive Disclosure：逐段迁移 Figma Core 详细正文到正确 Reference Owner；Core 保留模式、不可延迟不变量、路由/停止/Ready/Handoff 与明确 Reference 入口，不摘要原规则。
5. Delegation Contract：在现有多人/多 Agent Reference 增加最小 delegation fields，不建立调度系统。
6. CI/Evidence：增加 deterministic tests、routing/context-budget/preservation/runtime smoke 与文档同步。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1/E4 | 同一工程 Contract 比模型专属规则更稳定 |
| D2 | E6 | Outcome Eval 是现有路由/文本测试无法证明的独立层 |
| D3 | E2/E3 | 在六 Tool 内扩展 state 可复用 capability/fail-closed |
| D4 | E5 | Figma 应通过迁移降低常驻 Context，而不是压缩语义 |
| D5 | 当前 Multi-Agent Owner | Delegation 机器化现有边界，不需要 Planner/Worker |

## 备选方案与取舍

- 按模型维护 GPT/DeepSeek/GLM 专属 Skill：不采用，会形成多套规则和漂移。
- 只加更长提示词而不做 Eval：不采用，无法证明真实任务结果。
- 新增第七个 Runtime Tool 管 Task State：不采用，会扩大公共控制面。
- 通过摘要 Figma Core 快速减行：不采用，违反内容守恒。
- 引入 SEP-2640：明确非目标，不实施。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 模型身份不成为治理路由分叉，同一任务使用同一 Contract | #266 / AC1 | satisfied | Router Cross-model Behavior Contract + ROUTE_DIMENSIONS 无模型维度 + routing conformance |
| R2 | model-neutral Outcome Eval + 正负例 + 跨模型同标准比较 | #266 / AC2 | satisfied | evals/agent_outcome_eval.py + 7 类 case + actual/fixture verified 边界 + test_cross_model_outcome_eval |
| R3 | Trace/Run Artifact contract，缺失项显式 unavailable | #266 / AC3 | satisfied | Outcome Eval run schema 覆盖 model/host/revision/route/context/trace/process/Evidence/outcome/telemetry；缺失 telemetry=unavailable |
| R4 | 六 Tool 内支持结构化可恢复 Task State | #266 / AC4 | satisfied | RuntimeStore Task State + server 仍恰好六 Tool + MCP smoke |
| R5 | start/checkpoint resume/update + schema/size/fail-closed | #266 / AC5 | satisfied | test_runtime_task_state 覆盖恢复、patch、旧调用、首次补录、非法字段/权限、64 KiB、capability 不旋转 |
| R6 | Figma/Coding 渐进披露且规则内容守恒 | #266 / AC6 | satisfied | Figma Core 421 行；详细规则迁入 References；Figma progressive disclosure/skill/context budget 回归通过，未抬预算 |
| R7 | Rule Effectiveness Gate 区分四类规则并由 Eval 管 heuristic | #266 / AC7 | satisfied | coding.reference.32 明确 invariant/policy/heuristic/technique 与 Outcome Eval 生命周期 |
| R8 | Multi-Agent Delegation Contract，不新增 Planner/Worker | #266 / AC8 | satisfied | Ref09 Delegation Contract + test_multi_agent_delegation_contract；保留 Vertical Slice/DAG/frontier 与父 Agent 集成责任 |
| R9 | README/USAGE/runtime docs 同步且排除 SEP-2640/Research | #266 / AC9 | satisfied | README/runtime README 明确非目标；USAGE 仅保留最终用户跨模型/长任务用法且 release surface tests 通过 |
| R10 | 永久测试、PR CI、merge、main-fresh、Archive、Closure | #266 / AC10 | not_applicable | pre-Ready Change 不自证未来平台交付；current-head 583 tests/compile/smoke 与 Review 已取得，package→merge→main-fresh→Archive→#266 Closure 由下游 Delivery 生命周期持有 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Coding canonical References | 跨模型行为、Eval、Rule Effectiveness、Delegation 规则 | 统一 Contract | R1/R2/R3/R7/R8 |
| evals/ | schema/validator/grader/compare/cases/fixtures | Outcome Eval 机器 Contract | R2/R3 |
| Runtime runtime.py / server.py | Task State schema、resume/checkpoint | 长任务连续性 | R4/R5 |
| Figma SKILL.md + references | 逐段原文迁移，降低 Core 常驻 Context | 渐进披露 | R6 |
| tests / CI selector/workflow | deterministic regression | 防止行为漂移 | R1-R10 |
| README/USAGE/runtime README | 使用方式、边界与证据说明 | 人类可用性 | R9 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外：PR run #1526/#1535 暴露真实失败；候选实现接管过程未伪造不存在的先行 TDD
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Eval validator/grader、Task State normalize/patch/resume、内容守恒辅助逻辑 |
| 接口 / 契约 | required | MCP six-tool、可选参数/响应、Eval/Trace schema、routing vocabulary 不引入模型维度 |
| 集成 / 持久化 / 运行依赖 | required | RuntimeStore lifecycle + required-context capability + state resume/update |
| 用户 / 工作流验收 | required | route→context→state→checkpoint；Eval fixture→grade→compare |
| 跨组件关键路径 | required | Skill/Reference→Bundle/Runtime→MCP；Figma Router→Reference→Coding handoff |
| 外部依赖 / 供应方探测 | not_applicable | 本次不真实调用外部模型 Provider；未运行模型不标记已验证 |
| 构建 / 打包 / 运行 | required | changed-scope 选择的 compile/smoke/package |
| 文档 / 治理 / 其他 | required | #266、Change、内容守恒、context budget、文档、Review/CI/Archive/Closure |

## 验证计划

- 目标测试：Outcome Eval、Task State、Figma progressive disclosure、Rule Effectiveness、Delegation。
- 相关回归：routing conformance、context budget、Source/Runtime parity、runtime routing/bundle/project projection、Figma skill、planning/multi-agent。
- 静态检查或构建：按 runtime_package_scope.py 当前 classifier 选择，不降低 required CI。
- 专项真实边界：不调用外部模型 Provider；model label fixture 不冒充真实模型兼容证据。
- 就绪检查：ready_check + Requirement Source live validation + 独立 Review。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 规则迁移漏语义、Runtime state 扩展破坏现有 Tool、Eval 被误当真实模型验证 | old→new 内容守恒、兼容参数、明确 unverified |
| 兼容性 | 当前版本内保持旧 start/checkpoint 调用合法，Router 不加模型维度 | R1/R5 |
| 数据 / Migration | 不适用：不新增目标项目数据库/Schema，Task State 为显式 Runtime 状态 | 无外部持久数据 |
| 部署 / 运行 | Runtime artifact 行为变化，需平台 build/smoke | Runtime changed scope |
| 回滚 / 恢复 | revert PR；无外部不可逆数据 | 源码/治理变更 |

# 文档、依赖、部署与发布影响

- 长期文档：README、USAGE、runtime README 同步跨模型一致性、Outcome Eval、Task State、渐进披露和未验证模型边界。
- 依赖 / Runtime：不新增第三方依赖；继续 stdlib + 当前 MCP/Runtime 依赖，禁止静默升级。
- 配置 / Secret：Eval 不要求把 Provider Secret 写入仓库；真实 run artifact 必须由 runner/宿主脱敏。
- 部署 / Release：不创建正式 Release，但 Runtime 代码变化必须完成当前仓库要求的平台 package evidence。
- 兼容 / 消费方通知：Runtime MCP 参数新增可选字段时保持当前调用方式。

# 完成审计

- [x] upstream_re_read：已重新读取 live #266、current main/base 7d252cd5 与 head 3424c0dc，AC1-AC10 和非目标无漂移。
- [x] change_coverage：AC1-AC9 均映射到 canonical 实现、永久测试/文档和 current-head Evidence；AC10 的 post-Ready 部分继续由 Delivery 生命周期持有。
- [x] reverse_audit：已从跨模型同任务、actual/fixture Eval、长任务恢复、旧调用首次补状态、Figma baseline、Multi-Agent delegation、Runtime MCP、最终用户文档反向检查；确定 Finding 均已修复。
- [x] unresolved_cleared：开发侧 R1-R9 satisfied；R10 pre-Ready 不适用未来证据自证。未真实运行的 GPT/DeepSeek/GLM 版本保持 unverified。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 7d252cd5 | GitHub canonical reread + live #266 | 已确认 | 写入前 Ownership/Requirement Source 新鲜 |
| V2 | PR #269 head 3424c0dc / GitHub Actions run #1537 | compile selected maintained entrypoints + CLI smoke + selected self-contained tests | 583 tests，OK；compile/smoke success | 当前实现、路由、Context Budget、Figma 内容守恒、Outcome Eval、Task State、CI selector 等开发侧回归通过 |
| V3 | PR #269 base 7d252cd5 / head 3424c0dc | Independent Review #5254861137 | NO_FINDINGS_WITHIN_SCOPE | 从 live #266 独立 A1/A2 重建后，无当前实现阻塞 Finding；明确保留 package/main/Archive/Closure 未验证边界 |

## 未验证内容与剩余风险

- 当前未验证的是 Ready 后三平台 Runtime package/self-test/real MCP/install、guarded merge、main-fresh CI、repository-native Change Archive 与 #266 Closure；这些仍阻塞最终交付结论。
- 本需求不要求调用外部模型 Provider，因此不能在没有真实 `actual` run artifact 时宣称某个 GPT/DeepSeek/GLM 版本已经通过 Outcome Eval；本次建立同标准评测与机器 Contract，具体模型保持 unverified。

## 交付状态

- 提交：开发分支 head 3424c0dcc6391d52ad5e5f571ef5d5cef9b89013。
- 拉取请求：#269，当前 Draft；本 Change 更新后进入 Ready 流程。
- CI：run #1537 开发侧 583 tests/compile/smoke 已通过；Change status 之前为 in_progress，因此 package gate 按设计 fail-closed。
- 合并：未合并；等待 Ready 后 required package/current-head CI。
- Change 归档：未归档；merge 后由 repository-native Change Archive 处理。
- 发布 / 部署：不适用；本需求不发布正式 Release。

# 备注

- 用户已明确授权本任务完成后合并到 main。
- SEP-2640 Compatibility 与 Research/Analysis Skill 明确不在本 Change。
