---
schema: coding-change/v1
id: CHG-20260903-112817-testing-coding-context-governance
title: 收口 Testing Coding 职责并加固路由上下文治理
level: L3
status: done
owner: dingyuwen777
branch: chg/testing-coding-context-governance
created: 2026-09-03
updated: 2026-09-03
completion_gate: required
depends_on: []
affected_areas:
  - skill-routing
  - coding-governance
  - testing-governance
  - progressive-disclosure
  - runtime-conformance
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/references/08_分层测试与验收策略.md
  - .agents/skills/coding/references/25_Testing专业职责与Handoff.md
  - .agents/skills/coding/references/26_后端服务实施与运行边界.md
  - runtime/agent_skills_runtime/routing.py
  - .agents/skills/coding/tests/test_skill_owner_isolation.py
  - .agents/skills/coding/tests/test_owner_gated_routing.py
  - .agents/skills/coding/tests/test_route_context_budget.py
  - .agents/skills/coding/tests/test_source_runtime_context_conformance.py
  - .agents/skills/coding/tests/test_testing_runtime_projection.py
  - .agents/skills/coding/tests/test_backend_service_profile.py
  - .agents/skills/coding/tests/test_routing_conformance.py
contracts:
  - Agent Skills Skill路由/v1
  - Agent Skills Reference路由/v1
  - Agent Skills 任务路由/v1
data_changes: []
---

# 目标

完成 Testing 与 Coding 的专业职责收口，并把渐进式披露从单文件约束提升为真实 Task Route 的上下文治理：纯 Testing 任务不再因项目形态、风险、工具链、范围、治理或授权等 refinement facts 反向激活 Coding；Coding 保留开发期 TDD、Requirement Traceability、Validation Matrix、Completion Audit、生产实现/修复与 Git/CI/Release 门禁；Testing 唯一拥有系统性测试工程方法；后端实现作为 Coding profile 存在，不新增 Backend Skill。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/178

实现 PR：https://github.com/dingyuwen777/Agent_Skills/pull/179

归档 PR：https://github.com/dingyuwen777/Agent_Skills/pull/180

# 根因

旧 `runtime/agent_skills_runtime/routing.py::evaluate_route()` 会对全库 References 直接执行 trigger match。即使任务只具备 Testing 专业意图，`风险=L2`、`项目形态=前端Web/后端服务`、`范围=API/持久化`、工具链、治理或授权等普通任务事实仍可能命中 Coding Reference，再把 Coding Owner 反向加入上下文。

只收窄 Coding Skill Core 或只瘦身旧测试 Reference 不能解决根因，因为其他 Coding References 仍可能通过 refinement facts 反向激活 Coding。

# 采用方案

采用 Owner-gated evaluator：

```text
Task facts
→ Skill Core Owner projection
→ matched professional Owners
→ direct Reference match only inside matched Owner
→ explicit dependency closure（允许跨 Skill）
→ dependency Owner / risk fixed-point
```

Owner 选择阶段把以下维度作为 refinement 投影掉：

```text
项目形态 / 风险 / 工具链 / 范围 / 治理 / 授权
```

这些维度仍保留在 canonical metadata 和公共 Task Route vocabulary 中，并继续用于 Owner 已命中后的 Reference refinement。`执行模式 / 阶段 / 意图 / 能力` 可表达专业 Owner 意图。Router 作为控制面始终存在。

unknown facts 继续采用三值保守语义并保持 fail-close；防导出的候选域收敛到当前 matched Owner domain，避免 unknown refinement facts 把无关专业 Skill 全库带入。

未采用“给所有 Coding References 逐个补 Owner anchor”：该方案需要大面积重写 metadata，新增 Reference 仍可能忘记 anchor，并重复表达 Owner 语义。也未采用“只瘦身旧 Coding 测试方法”：它不能解决全局 direct Reference match 的根因。

# 职责边界

## Coding

继续拥有：

- `Red → Verify Red → Green → Refactor → Re-verify` 开发闭环；
- Requirement Traceability / Validation Matrix / Completion Audit；
- 决定一次交付必须证明哪些独立失败边界；
- 与实现紧耦合的最小 Unit/Component Regression；
- 生产代码实现、根因诊断与修复；
- Contract/Schema/Migration、兼容、Git/CI/PR/Release 等已有研发治理。

## Testing

唯一拥有：

- Test Strategy / Test Gap；
- Scenario-based Black-box Acceptance；
- User Journey / Workflow Acceptance；
- Exploratory Testing；
- 系统性 Integration / Contract / Golden Path / External Probe；
- Regression / Bug reproduction / retest；
- Fixture / Fake / Mock / Harness 的测试工程方法；
- 测试执行 Evidence 与证据等级表述。

## Review

继续拥有独立上游要求重建、实现审查、测试充分性/Evidence 判断、Findings 与 re-review；不维护第二套 Coding 或 Testing 方法。

# 后端 Coding Profile

新增 `coding.reference.27`，只在真实 Coding 执行模式 + Backend/Full-stack 或 API/Persistence 范围命中，不新增 Backend Skill。它覆盖 public service/API/event/command 入口、server-side validation/error contract、transaction/atomicity/data owner、idempotency/concurrency、async job/worker/retry/timeout/backpressure、resource lifecycle/graceful shutdown、observability/error categorization，并显式不拥有 Testing、Review、Git/CI/Release 的专业方法。

# 永久回归

新增：

- `test_skill_owner_isolation.py`：Testing-only + 已知项目 facts 不激活 Coding；project shape/risk/auth 单独不制造 Coding Owner。
- `test_owner_gated_routing.py`：direct Reference 不能跨 Owner gate；显式 dependency 可以跨 Skill。
- `test_route_context_budget.py`：真实 Route 的治理 Context bytes 预算与 full-corpus 防退化。
- `test_source_runtime_context_conformance.py`：Testing-only、Backend Coding、Coding+Testing、Review+Testing 的 Source/Runtime exact canonical text 同源。
- `test_testing_runtime_projection.py`：Testing Runtime Projection 核心语义守恒 + Reference identity 防披露。
- `test_backend_service_profile.py`：Backend profile 正确命中、Frontend 不误命中、正式 Skill Catalog 不新增 backend。

既有 `test_routing_conformance.py` 最终只对 Design-only Figma 的 Owner 期望做了本次职责语义明确支持的更新；实现过程中误带入的其他历史 fixture 改写已经恢复。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | refinement facts 不单独触发 Coding/其他专业 Owner | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | Red Skill #1026 → final-head Skill #1030 success → implementation main-fresh Skill #1031 success |
| R2 | direct Reference 受 Owner gate，显式 dependency 仍可跨 Skill | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_owner_gated_routing.py` 已进入 final-head/main-fresh self-contained suites 并通过 |
| R3 | Testing 成为唯一专业测试方法 Owner，Coding 旧专项方法收口 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | ref08/ref25 收口 + Testing ownership regressions 通过 |
| R4 | Coding + Testing 组合 Handoff 与开发期 TDD 不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | Testing/routing conformance suites #1030/#1031 通过 |
| R5 | 增加 Route-level Context Budget 永久回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_route_context_budget.py` 通过；预算未因失败而抬高 |
| R6 | 增加 Source/Runtime required Context exact-text conformance | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_source_runtime_context_conformance.py` + Runtime package CI 通过 |
| R7 | Testing Runtime Projection 核心语义受保护且不泄露 Reference identity | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_testing_runtime_projection.py` + 三平台 Runtime package/MCP/install 通过 |
| R8 | 新增 Backend/Service Coding 专项 Reference，不新增 Backend Skill | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `coding.reference.27` + `test_backend_service_profile.py` 通过 |
| R9 | 动态分发、公共词汇、防披露、协议与既有高价值治理语义不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | Skill #1030/#1031 + Runtime #320/#321 通过 |
| R10 | Review / final-head CI / guarded merge / implementation main-fresh / archive lifecycle | https://github.com/dingyuwen777/Agent_Skills/issues/178 | explicitly_deferred | 实现部分已满足；归档 PR 自身的 merge/final-main-fresh 由 post-merge finalization 自身记录，避免 archived Change 自引用 |

# Red 与实现证据

分支从 `main@eb2ca179c7284497b054bf531ec1f6cc5d54ec7f` 创建。

Red commit：`c4ed0fef6867afb390b526be7b647f5e45862fba`，只包含 Change + owner-isolation failure tests。PR #179 在该 head 上：Skill Tests #1026 / run `33711679686` 在 self-contained tests 失败；Runtime Package Tests #316 / run `33711679588` 成功；Requirement Source 成功。该 Red 直接证明旧 evaluator 会让 Testing-only + Web/Backend/L2 refinement facts 反向拉入 Coding。

实现与修正：

- `e5cbbca5c4efee49b802d5af7ca06749a16221e2`：Owner-gated evaluator、职责收口、Backend profile、永久回归；
- `2c407df882c5212fe618097cb9193e76ce82ef61`：保留 unknown fail-close、收窄 Backend trigger、修正已批准 Owner 语义；
- `ffbe921c622c8bfa11d5def00ba5cb30807e3c59`：恢复误带入的无关 routing fixture 改写，只保留 Design-only Figma 的有依据 Owner 变化；
- `2128db6a2e5804d2a61401fcabc01f9b43b9db74`：Completion Audit / 独立 Review 完成并进入 `ready_for_review`。

中间 implementation head `e5cbbca...` 的 Skill Tests #1027 暴露旧 unknown 期望、Design-only Figma 旧 Owner 期望、Backend profile 对 unknown project shape 过度加载三个兼容点；三项分别按根因处理，没有删除断言、放宽 Owner gate 或提高 Context Budget 制造 Green。

# 独立 Review

Review Target：PR #179，base `eb2ca179c7284497b054bf531ec1f6cc5d54ec7f`，review head `ffbe921c622c8bfa11d5def00ba5cb30807e3c59`。

A1 重新读取 Issue #178、根规则、Maintenance、Router、Coding/Testing/Review canonical Owner，从上游要求反查 Change/实现；未发现 Requirement omission。A2 从最终 diff 反查永久测试、Runtime package、Docs targeted 同步与兼容边界；未发现证据夸大或未覆盖的高风险实现边界。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`，无 BLOCKER/HIGH/MEDIUM 需要返回 Coding/Testing。

# PR Final-head 验证

Ready head：`2128db6a2e5804d2a61401fcabc01f9b43b9db74`。

- Skill Tests #1030 / run `33714542861`：success；Requirement Source、changed Python compile、CLI smoke、self-contained tests、changed Coding Change Ready Check、Agent Skills Gate 全部成功。
- Runtime Package Tests #320 / run `33714542862`：success；Scope、Windows/macOS/Linux onefile build+self-test、real stdio MCP contract、project-only single-binary install、Package Gate 全部成功。

合并前重新确认 PR head 未漂移、main 未漂移、无 unresolved review thread/comment。

# 实现合并与 Main-fresh 验证

PR #179 使用 `expected_head_sha=2128db6a2e5804d2a61401fcabc01f9b43b9db74` guarded squash merge。

实现 merge SHA：`4d0b015358ff3aa675275768a6ad47bdb05f638c`。

`main@4d0b0153...` fresh CI：

- Skill Tests #1031 / run `33714728234`：success；self-contained suite、Active Change Ready Check、Agent Skills Gate 全部通过。
- Runtime Package Tests #321 / run `33714728302`：success；Windows/macOS/Linux onefile/self-test、real stdio MCP、project-only install、Package Gate 全部通过。

只有取得以上 implementation main-fresh evidence 后才开始归档 Change。

# 验证矩阵最终状态

| 验证层 | 结论 |
| --- | --- |
| 行为 / Unit / Component | required，已由 owner isolation、routing、Backend、Context Budget 等 self-contained tests 证明 |
| 接口 / Contract | required，routing metadata/Stable ID/public vocabulary/Source-Runtime conformance 已证明 |
| 集成 / Persistence / Runtime Dependency | not_applicable；不修改业务数据库、文件、queue 或外部 Runtime Dependency 语义 |
| 用户 / Workflow Acceptance | required；Task Route 代表性工作流由 routing conformance/context tests 覆盖 |
| Real Cross-component business path | not_applicable；没有改变业务系统组件接线 |
| External Dependency Probe | not_applicable；不依赖第三方业务 Provider 当前事实 |
| Build / Package / Runtime | required；PR final-head 与 implementation main-fresh 的三平台 onefile/MCP/install 全部通过 |
| Docs / Governance | required；Requirement Source、Completion Audit、独立 Review、Ready Check、Router/Reference targeted sync 完成 |

# 文档影响

`targeted`。已同步直接承载治理语义的 Router 与 Coding/Testing Handoff References。README/USAGE 的安装方式、MCP tool contract、用户命令、Release artifact 结构均未改变，因此没有制造无关用户文档 diff。

# 兼容、依赖、迁移、部署和回滚

- Task Route、Skill/Reference metadata、Runtime Bundle、Project Payload、MCP Tool Contract 的 schema/version 均未变化；
- 现有 Reference Stable ID 未改；新增 Backend profile 使用 `coding.reference.27`；
- 没有依赖/Runtime 升级；
- 没有数据库/Schema/Migration/业务数据变化；
- 本任务不发布 Release；
- 后续正式 Release 会自然从当前 canonical main 构建新 evaluator；
- 若未来发现 Owner-gated routing 存在不可接受兼容回归，可回退实现 merge `4d0b0153...` 的相关 evaluator/Router/Reference 变化；不需要数据回滚。

# 环境与证据边界

当前会话本地沙箱无法解析 `github.com` 完成 clone，因此本任务没有伪造“本地完整仓库测试通过”。权威执行证据来自 GitHub Actions 的真实仓库 checkout 和 Windows/macOS/Linux 构建环境。

# 完成审计

- [x] upstream_re_read：已重新读取 Issue #178、根 `AGENTS.md`、Maintenance、Router、Coding/Testing/Review canonical Owner，并独立重建完成定义。
- [x] change_coverage：R1-R10 全部覆盖；R1-R9 satisfied，R10 仅将归档 PR 自身 merge/final-main-fresh 按生命周期 explicitly_deferred，没有把 Change 自身当 Requirement Source。
- [x] reverse_audit：已从 Testing-only、Coding+Testing、Backend Coding、Review/Docs/Figma、Runtime Projection 和三平台 Runtime package 反向检查 Owner、required Context 与 Evidence boundary。
- [x] unresolved_cleared：当前无 not_satisfied；没有未处理 BLOCKER/HIGH/MEDIUM；R10 的 deferred 有 Maintenance post-merge finalization 依据。

# 归档与交付

- Requirement Issue：#178
- 实现 PR：#179
- 实现 merge SHA：`4d0b015358ff3aa675275768a6ad47bdb05f638c`
- implementation main-fresh Skill Tests：#1031 / run `33714728234` success
- implementation main-fresh Runtime Package Tests：#321 / run `33714728302` success
- Change 归档路径：`.agents/changes/archive/2026-09/CHG-20260903-112817-testing-coding-context-governance/CHANGE.md`
- 归档 PR：#180
- Release：not_applicable，本任务未发布新版本

本历史记录在实现 main-fresh 通过后归档。归档 PR 自身的 guarded merge、最终 main-fresh CI、Issue 关闭与分支清理由仓库 post-merge finalization 继续执行；这些动作不会通过再次改写 archived Change 来制造循环依赖证据。
