---
schema: coding-change/v1
id: CHG-20260928-212500-route-outcome-effectiveness
title: 路由完整性与真实行为评测闭环
level: L3
status: ready_for_review
owner: dingyuwen777
branch: tech/327-route-outcome-effectiveness
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: none
affected_areas: routing,runtime,outcome-eval,qualification,context-effectiveness
affected_paths: router,coding,runtime,evals,tests,docs
contracts: task-route,outcome-eval,behavior-qualification
data_changes: none
---

# 变更摘要

- **要解决的问题**：规则已经能被确定性分发，但 mixed-route、Task Fact completeness、actual Evidence trust 与 Reasoning qualification 仍存在执行层缺口。
- **拟议修改**：收紧 Owner trigger、补 Task Route truth-state Contract、让 actual grader 从 host Evidence Receipt 推导结果、增加 reasoning-source qualification profile 与 context-effectiveness report。
- **预期结果**：同一自然语言任务在 Source/Runtime 中得到更可靠的 Owner/Context，真实行为资格不再依赖模型自报标签，并能比较 Context 成本与实际收敛效果。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #327。用户明确要求按系统审计方案修改 Agent_Skills，并在 required gate 满足后合并 main。

## 当前现状

当前 main 已有 Owner-gated routing、UNKNOWN evaluator、Source/Runtime exact-context、Review convergence、Outcome Eval actual/fixture 区分与 Behavior Qualification；Issue #325 已闭合上一轮规则可达性。

## 问题、根因或约束

根因集中在执行输入与行为 Evidence：Coding mixed trigger 对 Analysis/Research 模式边界不够精确；Task Route sparse signals 会把漏报维度规范成空；actual grader 直接信任 run 自报 result/evidence/violations；Reasoning case 尚未形成独立 qualification profile；Context budget 未与结果指标联动观察。

## 不修改的后果

模型可能合法地产生欠披露或过路由 Context；actual artifact 可以通过自报标签形成假阳性；“跨模型遵循规则”和“Context 更有效”缺少可核验的结果层证据。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Coding machine trigger 对只读分析/方案/验证较宽，Analysis/Research mixed-mode 负例不完整 | coding/SKILL.md + test_analysis_research_skills.py current main | 需要 AC1 |
| E2 | validate_task_route 对缺失 signal dimension 使用空列表补齐 | runtime/agent_skills_runtime/routing.py current main | 需要 AC2 |
| E3 | grade_run 直接用 run 的完成结果/证据/违规集合评分 | evals/agent_outcome_eval.py current main | 需要 AC3 |
| E4 | Analysis/Research cases 已存在，但 Engineering high-value registry/qualification 没有独立 reasoning-source profile | evals/cases + release_qualification.py current main | 需要 AC4 |
| E5 | context budget 只约束 bytes，没有结果效果联合报告 | test_route_context_budget.py + Outcome Eval current main | 需要 AC5 |
| E6 | Issue #327 已按 canonical Technical Change Form 创建 | GitHub Issue #327 | 当前 Requirement Source |

## 推断与待确认

- Runtime Project Payload/host projection 是否需要正文变化取决于 Router/Runtime projection 的自动派生与现有 parity tests；只有直接消费者受影响才修改。
- 本次 Task Route Contract 若触及 package classifier，将由 current selector 决定是否要求三平台 package，不能预先用风险等级替代 changed-scope 事实。

# 目标、成功标准与非目标

## 目标

让规则执行闭环从“正确规则可被加载”推进为“任务事实不静默漏报、专业 Owner 不误命中、actual Evidence 可验证、Reasoning 行为可独立 qualification、Context 成本能与结果质量共同观察”。

## 成功标准

- [ ] AC1–AC6 由当前实现与永久回归直接证明。
- [ ] AC7 由 current-head required CI、适用 package 与独立 Review 证明。
- [ ] AC8 由 guarded merge、main-fresh、repository-native archive、Issue closure 与 cleanup 证明。

## 范围

Router/Coding routing metadata、Runtime Task Route validator/evaluator、Outcome Eval/qualification、直接相关 tests 与长期说明。

## 非目标

不新增 Skill/Agent/daemon/Provider runner；不强制普通 Release 执行 actual qualification；不修改用户全局工程 policy；不升级依赖或改变 Release ZIP 资产面。

## 必须保持不变

项目事实优先、权限边界、L1-L3、Fresh Evidence、Review convergence、Follow-up lifecycle、现有四宿主工程 qualification 语义与用户自然语言入口均不得降低。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Router/Coding/Runtime/Eval 各自保持唯一 Owner | E1-E5 / #327 | 不新增第二控制面 |
| 接口与契约 | Task Route truth-state 与 actual run Evidence trust 允许升级机器 Contract | #327 / AC2-AC3 | 同步 Source/Runtime/tests |
| 数据与迁移 | 不适用，无业务 Schema/数据 | E1-E5 | 无 Migration |
| 错误与失败语义 | 漏维度/矛盾 UNKNOWN/缺 actual receipt fail closed | #327 AC2-AC3 | 阻止欠披露和假阳性 |
| 兼容性 | 不为未要求的历史 Runtime 双读协议 | Maintenance 当前策略 | 当前版本内同源迁移 |
| 部署与回滚 | 本 PR 不 Release；失败回退 PR | #327 | 无生产迁移 |

# 修改方案与决策依据

## 最小充分方案

1. 先补 mixed-route、Task Route completeness、actual self-report bypass、reasoning profile、context effectiveness Red 回归。
2. 收紧 Coding Owner trigger，同时保留工程实现/诊断 + Research 的组合路径。
3. 在现有 Task Route shape 上建立显式 tri-state：每个维度必须由 signal key 或 unknown 声明覆盖；KNOWN_EMPTY 与 UNKNOWN 互斥。
4. actual run 增加 host/tool/repository/user Evidence Receipt，grader 对 actual 只从 receipt 派生 result/evidence/violation；fixture 保留机器 contract 测试语义。
5. qualification validator 抽出共享 profile Contract；现有 Engineering 入口保持，新增 reasoning-source profile，不复制 grader。
6. 增加 context effectiveness report，仅联合呈现 bytes + first-pass miss/repair churn/retry/user intervention + grade，不把 context size 单独作为成功条件。
7. 同步受影响 Router/Reference/README/USAGE 与 Runtime parity；按 selector 运行 current-head gate，再独立 Review 和 guarded delivery。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 mixed trigger 精修 | E1 | 修真正 Owner 边界，不靠模型记忆 |
| D2 tri-state completeness | E2 | 解决漏报与 false 混同，不新增 Router |
| D3 receipt-derived actual grading | E3 | 切断模型自报 PASS 路径 |
| D4 profile 复用 grader | E4 | 扩展 Reasoning 验证而不复制第二套评测 |
| D5 effectiveness report | E5 | 防止只追求 Context 变小 |

## 备选方案与取舍

- 新增 Route Agent/后台守卫：增加控制面与宿主复杂度，不采用。
- 把完整规则复制进 managed block/host prompt：重新制造第二 Owner，不采用。
- 直接让 CI 调用各模型 Provider：引入 Secret、费用和宿主行为差异，当前不采用；actual run 仍由真实宿主产生。
- 仅增加更多 Markdown “必须”：不能解决 machine input/evidence trust 根因，不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | mixed Analysis/Research route 不误入 Coding，工程组合仍可达 | #327 / AC1 | satisfied | mixed-route 正负例与既有 Testing/Figma/Docs Handoff 回归在 run 36434077058 全部 Green |
| R2 | Task Route 显式区分 known/known-empty/unknown | #327 / AC2 | satisfied | Task Route 升级 v2；漏维度/UNKNOWN+值负例、Source/Runtime conformance、真实 MCP smoke 在 run 36434077058 Green |
| R3 | actual grader 不信任自报标签 | #327 / AC3 | satisfied | actual Evidence Receipt + forbidden clear receipt Contract；self-report bypass/qualification 回归在 run 36434077058 Green |
| R4 | reasoning-source qualification profile 复用同一 grader | #327 / AC4 | satisfied | reasoning-source profile 复用 grade_run；Analysis/Research registry/profile 回归 Green |
| R5 | Context Effectiveness 联合结果指标 | #327 / AC5 | satisfied | effectiveness report 联合 context bytes/首轮遗漏/返修/重试/用户干预/grader；无 size-only PASS |
| R6 | Mutation Impact / parity / budget 不回归 | #327 / AC6 | satisfied | compile/CLI smoke + 753 tests OK；routing/source-runtime/runtime/qualification/context budget 全部 Green，未提高预算 |
| R7 | current-head CI/package/review | #327 / AC7 | explicitly_deferred | 进入 ready_for_review 后取得 current-head required CI、三平台 package 与 final Review；235c920 实现语义已 Green |
| R8 | merge/main-fresh/archive/closure/cleanup | #327 / AC8 | explicitly_deferred | 仅能在 merge 后由 main-fresh、repository-native archive、Closure Audit 与 cleanup 完成 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| coding/SKILL.md + Router | mixed Owner trigger / completeness 入口 | 修路由边界 | R1-R2 |
| runtime/.../routing.py + Runtime consumers | truth-state validator/evaluator | 防漏报 | R2 |
| evals/agent_outcome_eval.py | Evidence Receipt + effectiveness | 可信 actual / 结果指标 | R3/R5 |
| evals/release_qualification.py | qualification profiles | Reasoning profile | R4 |
| existing tests | Red/Green regression | 永久保护 | R1-R6 |
| README/USAGE/canonical eval rule | 同步长期事实 | 使用/维护一致 | R3-R5 |

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
| 行为 / 单元 / 组件 | required | routing、Task Route validator、Outcome Eval receipt/profile/effectiveness |
| 接口 / 契约 | required | Task Route、Outcome Eval/qualification machine Contract |
| 集成 / 持久化 / 运行依赖 | required | Runtime evaluator/store/stdin MCP；无数据库 |
| 用户 / 工作流验收 | required | Analysis/Research、工程 Research、actual qualification artifact 路径 |
| 跨组件关键路径 | required | canonical metadata → evaluator → Runtime Context；host receipt → grader → qualification |
| 外部依赖 / 供应方探测 | not_applicable | 不调用真实 Provider；actual run 生产不属于本 PR required gate |
| 构建 / 打包 / 运行 | required | changed-scope selector 决定 Runtime package Evidence |
| 文档 / 治理 / 其他 | required | #327、Change、README/USAGE/Reference、CI/Review/Archive/Closure |

## 验证计划

- 目标测试：analysis/research routing、runtime routing、cross-model outcome eval、qualification。
- 相关回归：routing conformance、source-runtime conformance、context budget、runtime MCP/package、hard-rule reachability。
- 静态检查或构建：selector 选择的 compile/CLI smoke。
- 专项真实边界：真实 GitHub PR/CI/Review/main-fresh/archive/closure。
- 就绪检查：ready_check current-head。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | route 欠披露、Eval 过度复杂、Context 指标误导 | 正负回归 + 单一 grader + no-size-only PASS |
| 兼容性 | Task Route 升级为 v2 并收紧 truth-state | #327 明确允许；当前版本同源升级，不保留未要求历史双 reader |
| 数据 / Migration | 不适用 | 无数据库/业务数据 |
| 部署 / 运行 | 后续 Runtime Release 才分发到目标项目 | 本 PR 不发布 |
| 回滚 / 恢复 | 回退 PR | 无不可逆数据副作用 |

# 文档、依赖、部署与发布影响

- **长期文档**：README 与 canonical Runtime/Eval References 已同步；USAGE 无新增用户操作或调用方式，因此不复制内部 machine-contract 细节。
- **依赖 / Runtime**：无新依赖；Runtime routing 行为受影响。
- **配置 / Secret**：不新增 Secret/Provider 凭据。
- **部署 / Release**：本任务不创建 Release；未来正式 Release 使用现有三平台流程。
- **兼容 / 消费方通知**：目标项目升级到后续 Runtime 后获得新 Task Route 语义。

# 完成审计

- [x] upstream_re_read：已重读 #327、Router/Coding/Runtime/Outcome Eval/qualification 与当前 CI 事实。
- [x] change_coverage：AC1–AC6 已满足；AC7 Ready 后门禁、AC8 post-merge 门禁均显式 deferred，无遗漏要求。
- [x] reverse_audit：已从自然语言 → owner route → truth-state → Context → Evidence Receipt → grader → qualification → delivery 反查，并验证 Testing/Figma/Docs/Review 既有组合未回归。
- [x] unresolved_cleared：当前无 not_satisfied；仅 R7/R8 按正式生命周期 explicitly_deferred。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 0bda190c | canonical read + Issue #327 | confirmed | 起始事实与 Requirement Source |
| V2 | head 3e8e96980bfe435a74e35e70326c13df4fa8a2c7 / GitHub Actions run 36429308261 | selected self-contained tests | FAILED：48 tests 中 8 failures + 1 error；mixed-route、Task Route completeness、actual receipt、reasoning profile/effectiveness 均按预期 Red | 新回归在旧实现上真实暴露 #327 AC1–AC5 缺口 |
| V3 | head 235c9205e0b7c34769652c16d28a9f432a357a82 / GitHub Actions run 36434077058 | compile + CLI smoke + full selected semantic suite | compile/smoke PASS；Ran 753 tests → OK；既有 absolute/context migration budgets 均 Green | AC1–AC6 当前实现与内容守恒已闭合；唯一 CI failure 是 Change 尚为 in_progress 的预期 Ready Gate |

## 未验证内容与剩余风险

- Ready 后仍需 current-head required CI、适用三平台 Runtime Package 与 final Review；merge 后仍需 main-fresh/archive/closure/cleanup。
- 真实跨宿主 actual runs 不属于本次普通源码交付 required gate；本次建立可信 Evidence Receipt/qualification Contract，但不冒充已完成真实跨宿主 qualification。

## 交付状态

- 提交：Red + Green + compatibility/context closure 已提交，当前实现 head `235c9205e0b7c34769652c16d28a9f432a357a82`。
- 拉取请求：PR #328 Draft；本提交将 Change 切换为 ready_for_review，随后转 Ready。
- CI：run 36434077058 compile/smoke/753 semantic tests Green；整体 job 仅因 Change 当时 in_progress 按预期 fail-closed。
- 合并：待 Ready-head required CI/package + final Review。
- Change 归档：待 merge 后 repository-native automation。
- 发布 / 部署：不适用，本任务不创建 Release。

## 备注

无。
