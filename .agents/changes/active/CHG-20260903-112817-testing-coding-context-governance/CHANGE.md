---
schema: coding-change/v1
id: CHG-20260903-112817-testing-coding-context-governance
title: 收口 Testing Coding 职责并加固路由上下文治理
level: L3
status: ready_for_review
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

完成 Testing 从 Coding 中的职责收口，并把渐进式披露从“单文件不太大”提升为真实 Task Route 的可回归上下文约束：纯 Testing 任务不再因项目形态、风险、工具链、范围、治理或授权等 refinement facts 反向激活 Coding；Coding 只保留开发期 TDD、验证证据治理与 Testing Handoff；后端实现获得独立的 Coding 专项 profile，但不新增 Backend Skill。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/178

# 成功标准

- [x] Testing-only + 已知项目形态/风险/范围不会命中 Coding，也不会加载 Coding 测试专项/Handoff Reference。
- [x] Skill Owner 先于 Reference refinement：直接 Reference 不能反向激活未命中 Owner；显式 dependency 仍可跨 Skill 扩展 Owner。
- [x] Coding + 独立测试意图仍组合 Coding + Testing，并保持生产修复、Regression、Review 的既有 Handoff。
- [x] Coding 分层测试专项只保留证据边界/Testing Handoff，不复制 Test Strategy、Black-box、User Journey、Integration、Golden Path、Probe、Regression 的详细方法。
- [x] 代表性 Route 有永久 Context Budget 回归，并直接按真实 Skill Core + required Reference 计算预算。
- [x] Source evaluator 与 RuntimeStore 对 facts-complete route 返回完全一致的 required canonical Context。
- [x] Runtime Projection 显式保留 Testing 的 Owner/Handoff/Black-box/Regression 核心语义，并继续隐藏 Reference identity。
- [x] 新增 Backend/Service Coding Reference，覆盖服务端实现/运行边界，不新增 Backend Skill、不复制 Testing/Review/Git/CI 细则。
- [x] 动态 Skill Catalog、公共 Task Route 词汇、Project Payload no-Reference、防披露和现有 Runtime/MCP 协议保持不变。
- [ ] 独立 Review、PR CI、guarded merge、main fresh CI 和 Change archive 闭环完成；独立 Review 已完成，剩余 merge/main-fresh/archive 必须按仓库生命周期在合并后继续。

# 范围

- 调整单一 canonical routing evaluator：Owner 选择时投影掉 refinement dimensions；Reference 只在已命中 Owner 内直接匹配；显式 dependency 保持跨 Skill 能力。
- 收口 Coding 分层测试专项 Reference 与 Testing Owner 的边界。
- 新增 Backend/Service Coding 专项 Reference。
- 增加职责隔离、Owner-gated evaluator、Route Context Budget、Source/Runtime required Context、Testing Runtime Projection 永久回归。
- 仅同步受影响的 canonical Router/Reference 与测试；不扩大到无关 Skill Core/README/USAGE。

# 非目标

- 不新增 Frontend/Backend/Git/CI/Release 正式 Skill。
- 不改变 `Agent Skills Skill路由/v1`、`Agent Skills Reference路由/v1`、`Agent Skills 任务路由/v1`、Runtime Bundle、Project Payload 或 MCP Tool Contract 的 schema/version。
- 不升级 Python、依赖、GitHub Actions、Runtime 或包管理工具。
- 不修改仓库可见性。
- 不发布新 Release。
- 不把所有 Coding 实现机械升级为独立 Testing；普通开发期最小 TDD 仍由 Coding 完成。
- 不要求 Source/Runtime 最终 LLM 自然语言逐字相同；只保证相同 canonical routing 与 required Context。

# 必须保持不变

- Coding 的 `Red → Verify Red → Green → Refactor → Re-verify`、Requirement Traceability、Validation Matrix、Completion Audit、Git/CI/Release 门禁继续有效。
- Testing 是 Test Strategy、Scenario-based Black-box、User Journey、Exploratory、Integration/Contract/Golden Path/Probe、Regression 与测试资产方法的唯一专业 Owner。
- Review 保留独立需求/实现审查、测试充分性与 Evidence 判断，不复制 Testing 方法。
- Source Mode / Runtime Mode 继续使用同一 canonical metadata、Stable ID、依赖和 required Context 语义。
- 现有 Skill/Reference routing protocol、Stable ID 和公共 Task Route 取值继续可用；refinement 维度不会因 Owner gate 从 public contract 消失。
- Reference Stable ID 不因文件内容收口而重写；已有 `coding.reference.08` 与 `coding.reference.26` 保持身份稳定，新 Backend profile 使用 `coding.reference.27`。
- Runtime Project Payload 不安装 canonical Reference/Stub；公共 MCP 返回不公开 Reference identity。
- Router 仍是始终命中的控制面；授权信号只表示已确认事实，不产生权限。

# 方案比较与关键决策

## 方案 A：逐个修改所有 Coding Reference trigger

给每一个 Coding Reference 都补 `执行模式`/Coding anchor，使 risk/project-shape/scope 等 trigger 不再独立命中。

缺点：需要大面积重写现有 metadata；新增 Reference 仍可能再次忘记 anchor；重复表达 Owner 语义，维护成本高，容易造成 Source/Runtime 规则漂移。

## 方案 B：Owner-gated evaluator + Owner 内 Reference refinement（采用）

由单一 evaluator 明确两阶段语义：

```text
Task facts
→ Skill Core Owner projection
→ matched Owners
→ direct Reference match only inside matched Owner
→ dependency closure（允许跨 Skill）
→ owner/risk fixed-point
```

Owner 选择时，`项目形态 / 风险 / 工具链 / 范围 / 治理 / 授权` 作为 refinement dimensions 被投影掉；它们仍保留在 canonical metadata/public route vocabulary，并在 Owner 已命中后用于 Reference refinement。`执行模式 / 阶段 / 意图 / 能力` 可以表达专业 Owner 意图。Router 始终作为控制面命中。

优点：单一语义、动态 Skill Catalog 不需要静态 allowlist、不会要求每个 Reference 复制 Owner anchor；显式 dependency 仍能表达真正的跨 Skill Handoff。

风险：这是中央路由求值语义变化，因此本 Change 从 L2 升级为 L3，必须用现有 routing conformance + 新 owner isolation + Source/Runtime exact-context 回归证明没有欠披露。

## 方案 C：只瘦身 `coding.reference.08`

只解决 Testing 方法文本重复，不修改 owner/refinement 语义。

拒绝原因：Testing-only + `risk=L2` 仍会通过其他 Coding Reference 反向激活 Coding，无法解决根因。

## 其他决策

- 不修改接近 51 KiB 固定预算上限的 Coding Core；Owner/refinement 语义由跨 Skill Router + canonical evaluator 维护，避免为了职责收口反而让 Coding Core 膨胀。
- 不删除 `coding.reference.08`，把它收口为小型“分层证据边界 / Testing Handoff profile”，保持 Stable ID 和 live link；详细测试方法继续唯一存在于 Testing。
- Backend/Service 作为 Coding Reference 而不是新 Skill：它解决 transaction/idempotency/concurrency/async/resource lifecycle 等服务端实现责任，但 Testing/Review/Git/CI 继续由现有 Owner 负责。
- Context Budget 使用代表性真实 Task Route 的 Core + required Reference bytes 建永久回归；阈值固定在本次收口后的合理上界，不允许后续为让测试变绿随意抬高。
- Source/Runtime 一致性验证同一 route 的 required canonical Reference exact text，不要求 LLM 输出逐字一致。
- unknown 防导出仍失败关闭，但候选域收敛到当前 matched Owner 域；它不会因为未知 refinement facts 把不相关 Skill 全库带入上下文。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | refinement facts 不再单独触发 Coding/其他专业 Owner | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | Red：PR #179 head `c4ed0fef...` 的 Skill Tests run #1026 在 self-contained tests 失败；Green：head `ffbe921c...` 的 Skill Tests run #1029 中 `Run self-contained tests` 为 success |
| R2 | direct Reference 受 Owner gate，显式 dependency 仍可跨 Skill | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_owner_gated_routing.py` 已进入 run #1029 的 self-contained suite 并整体 success |
| R3 | Testing 成为独立测试工程方法唯一 Owner，Coding 旧专项方法收口 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | ref08 已收口为 Evidence Profile；ref25 明确 Owner/Handoff；Testing 既有专项回归与 run #1029 self-contained suite success |
| R4 | Coding + Testing 组合 Handoff 与开发期 TDD 不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_testing_skill.py`、`test_skill_owner_isolation.py`、`test_routing_conformance.py` 均在 run #1029 self-contained suite success |
| R5 | 增加 Route-level Context Budget 永久回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_route_context_budget.py` 在 run #1029 self-contained suite success；未提高既定预算阈值 |
| R6 | 增加 Source/Runtime required Context exact-text conformance | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_source_runtime_context_conformance.py` 在 run #1029 self-contained suite success |
| R7 | Testing Runtime Projection 核心语义显式受保护且不泄露 Reference identity | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | `test_testing_runtime_projection.py` 在 run #1029 self-contained suite success；Runtime Package Tests #319 三平台 package/MCP/install 全部 success |
| R8 | 新增 Backend/Service Coding 专项 Reference，不新增 Backend Skill | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | 新 `coding.reference.27` + `test_backend_service_profile.py` 在 run #1029 self-contained suite success；动态 Skill Catalog 未新增 backend |
| R9 | 动态分发、公共词汇、防披露、协议与既有高价值治理语义不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | satisfied | Skill Tests #1029 的 compile/CLI smoke/self-contained tests success；Runtime Package Tests #319 / run `33713866669` 的 Scope、Windows/macOS/Linux Package、Package Gate 全部 success |
| R10 | PR/Review/merge/main-fresh/archive 闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | explicitly_deferred | 独立 Review 已完成；guarded merge、main-fresh CI、Change archive 只有在 Ready/final-head CI 通过并实际合并后才能取得，按 Maintenance 生命周期继续执行，不在 pre-merge 阶段伪造完成 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Owner isolation、direct ref gate、cross-skill dependency、Backend profile 与 Context Budget 的永久 `unittest` 回归；run #1029 self-contained suite success |
| 接口 / 契约 | required | `agent-routing:v1` metadata compiler、Stable ID/dependency、公共 Task Route 词汇、Source/Runtime required Context 同源；run #1029 compile/CLI smoke/self-contained success |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改业务数据库、文件、队列或外部 Runtime Dependency 语义 |
| 用户 / 工作流验收 | required | 以 Task Route 作为治理调用者输入，Testing-only、Coding+Testing、Review/Docs/Figma 代表性路由由 routing conformance/context tests 覆盖并在 run #1029 success |
| 跨组件关键路径 | not_applicable | 不改变业务应用真实组件接线；Runtime 构建/投影由 Build/Package 层验证 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖任何第三方业务 Provider 当前事实 |
| 构建 / 打包 / 运行 | required | Runtime Package Tests #319 / run `33713866669`：Runtime Package Scope、Windows/macOS/Linux onefile build+self-test、真实 stdio MCP contract、project-only install、Package Gate 全部 success |
| 文档 / 治理 / 其他 | required | Requirement Source #178 success；Router/ref08/ref25 targeted 同步；独立 A1/A2 Review 无 blocker；Ready Check 将由本次 `ready_for_review` 提交重新执行 |

# Red 证据

- 分支从 `main@eb2ca179c7284497b054bf531ec1f6cc5d54ec7f` 创建。
- Red commit：`c4ed0fef6867afb390b526be7b647f5e45862fba`（只包含 Change + owner-isolation failure tests）。
- PR #179 已创建，`Requirement-Source: #178` 校验成功。
- PR head `c4ed0fef...`：
  - Skill Tests run #1026 / run id `33711679686`：**failure**，失败阶段 `Run self-contained tests`；
  - Runtime Package Tests run #316 / run id `33711679588`：**success**；
  - Requirement Source step：success；Agent Skills Gate 因 Skill Tests failure 被阻塞。
- 该 Red 证明旧 evaluator 会让 Testing-only + Web/Backend/L2 refinement facts 反向拉入 Coding；尚未用规则修改掩盖失败。

# Green 与失败处置证据

- Implementation commit：`e5cbbca5c4efee49b802d5af7ca06749a16221e2`（Owner-gated evaluator、职责收口、Backend profile、永久回归）。
- Follow-up commit：`2c407df882c5212fe618097cb9193e76ce82ef61`（保留 unknown fail-close、收窄 Backend trigger、修正已批准 Owner 语义）。
- Cleanup commit：`ffbe921c622c8bfa11d5def00ba5cb30807e3c59`（恢复误带入的无关 routing fixture 改写，只保留 Design-only Figma 的有依据 Owner 期望变化）。
- `e5cbbca...` 的 Skill Tests #1027 暴露 3 个真实兼容点：旧 unknown 期望、Design-only Figma 旧 Owner 期望、Backend profile 对 unknown project shape 过度加载；逐项区分“实现缺陷 vs 本次批准语义”，未通过删除断言/抬高预算制造 Green。
- `ffbe921c...` 的 Skill Tests #1029 / run `33713866714`：
  - Compile changed Python files：success；
  - CLI direct smoke：success；
  - Run self-contained tests：success；
  - Verify changed Coding Change：failure，仅因为 Change 当时仍是 `in_progress`；这正是 Completion Gate 的预期阻塞，不是代码/测试失败。
- `ffbe921c...` 的 Runtime Package Tests #319 / run `33713866669`：完整 success；Windows/macOS/Linux onefile Runtime、real stdio MCP contract、project-only single-binary install 与 gate 均成功。
- 本轮没有本地完整仓库执行证据：当前会话沙箱无法解析 `github.com` 完成 clone，因此不把本地环境冒充 Green；GitHub Actions 的真实 checkout/跨平台构建是本轮权威执行证据。

# 独立 Review

Review Target：PR #179，base `eb2ca179c7284497b054bf531ec1f6cc5d54ec7f`，review head `ffbe921c622c8bfa11d5def00ba5cb30807e3c59`。

模式：独立 review-only / Completion Audit；实现修改已经结束，本轮 Review 不以作者 checklist 或 CI 全绿替代上游重建。

## A1：上游要求 → Change / 实现

重新读取 Issue #178、`main` 根 `AGENTS.md`、`.agents/MAINTENANCE.md`、Router、Coding/Testing/Review canonical Owner 后独立重建：

- 必须解决 Testing-only 被 refinement facts 反向拉入 Coding 的根因，而不是只改文案；
- Testing 专业测试方法必须唯一归 Testing；Coding 保留开发期 TDD、证据需求与生产修复；Review 保留充分性/Evidence；
- 必须保留动态 Skill Catalog、Stable ID、公共 Task Route 词汇、Runtime no-Reference、防披露与 Source/Runtime 同源；
- 需要长期可回归的 Route Context Budget 与 Source/Runtime exact-context；
- 后端能力应作为 Coding profile 而非新 Backend Skill；
- 不能通过放宽测试、提高预算、升级依赖/协议或扩大无关重构实现。

对照最终 diff，A1 未发现 Requirement omission。

## A2：Change / 实现 → 测试 / 文档 / 运行证据

- evaluator 根因由 owner-isolation Red 证明，最终 owner-gated/direct-ref/dependency/unknown 行为进入永久测试；
- Context Budget、Source/Runtime exact-context、Testing Runtime Projection、Backend profile 都有新增永久回归；
- 既有 routing conformance 只对 Design-only Figma 的 Owner 期望做了本次需求明确支持的修改；其余误带入历史 fixture 已恢复；
- Runtime Package #319 真实构建三平台 onefile，验证 stdio MCP contract 和 project-only install；
- Router/ref08/ref25 已 targeted 同步；README/USAGE 的安装、MCP tool、Release artifact、用户命令均未改变，因此没有制造无关用户文档 diff；
- 无数据/依赖/Runtime/schema/protocol/migration 变化需要额外部署或迁移证据。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。没有 BLOCKER/HIGH/MEDIUM 需要返回 Coding/Testing；剩余未完成项只是按仓库生命周期必须在当前 Ready 提交之后取得的 final-head CI、guarded merge、main-fresh CI 和 post-merge archive。

# 完成审计

- [x] upstream_re_read：重新读取 Issue #178、当前 `main` 根规则、Maintenance、Router、Coding/Testing/Review canonical Owner，从上游独立重建完成定义。
- [x] change_coverage：确认 R1-R10 全部被当前 Change 覆盖，未把 Change 自身当作需求全集；R10 按生命周期显式 deferred 到 post-merge，不伪造完成。
- [x] reverse_audit：从 Testing-only、Coding+Testing、Backend Coding、Review/Docs/Figma、Runtime Projection 反向检查 Owner 与 required Context，并复核验证矩阵。
- [x] unresolved_cleared：当前无 `not_satisfied`；R1-R9 satisfied，R10 有正式 Maintenance 生命周期依据记录为 `explicitly_deferred`。

# 任务

- [x] 调查当前实现、Router、Coding/Testing/Review Owner、Runtime Projection、现有永久测试与 CI。
- [x] 建立 Requirement Source Issue #178 与 gated Change。
- [x] 提交能在旧实现上稳定失败的 Testing Owner isolation Red，并取得 PR CI Red。
- [x] 根因升级：确认全局 direct Reference match 会反向激活 Owner，本 Change 升为 L3。
- [x] 实现 Owner-gated evaluator，并保持显式 cross-Skill dependency。
- [x] 收口 `coding.reference.08` 为证据边界/Handoff profile，保持 Stable ID。
- [x] 新增 Backend/Service Coding Reference 与路由回归。
- [x] 增加 Route Context Budget、Source/Runtime Context Conformance、Testing Runtime Projection 永久测试。
- [x] 执行 implementation-head PR CI；self-contained tests 与 Runtime package 真实 Green，Change Gate 在 `in_progress` 阶段按预期阻塞。
- [x] 完成 A1/A2 独立 Review、Completion Audit，并将 Change 进入 `ready_for_review`。
- [ ] 取得当前 Ready 提交对应的 final-head PR CI，guarded merge，main fresh CI，归档 Change并关闭 Issue。

# 验证

## 计划

- Red：已由 PR #179 head `c4ed0fef...` 的 Skill Tests run #1026 证明。
- Targeted/Full：Owner isolation、owner-gated evaluator、Testing ownership、routing metadata、Context Budget、Source/Runtime Context、Runtime Projection、Backend profile 与现有 self-contained suite 已由 GitHub Actions 真实 checkout 执行。
- 就绪：本次提交把 Change 切到 `ready_for_review`，随后 `python .agents/skills/coding/scripts/ready_check.py --root . --changed-since "$BASE_SHA"` 必须在新的 final-head CI 真实通过。
- CI：Skill Tests + Agent Skills Gate + Runtime Package Tests/Gate，全部必须绑定 Ready 提交的新 head SHA。

## 新鲜证据

- pre-Ready implementation review head：`ffbe921c622c8bfa11d5def00ba5cb30807e3c59`。
- Skill Tests #1029 / run `33713866714`：compile、CLI smoke、self-contained tests success；Change Gate 因旧 status=`in_progress` 预期失败。
- Runtime Package Tests #319 / run `33713866669`：success。
- Requirement Source：success。
- 独立 Review：`NO_FINDINGS_WITHIN_SCOPE`。
- 当前 `main` 仍为 `eb2ca179c7284497b054bf531ec1f6cc5d54ec7f`，没有 base 漂移。
- Ready 提交后的 final-head CI 尚未执行；因此此处只标记 `ready_for_review`，不能宣称 PR 已可合并，必须等待下一轮新鲜 CI。

# 文档影响

- `targeted`：canonical Router 与 Coding/Testing Handoff Reference 本身属于治理文档并直接被 Source/Runtime/LLM 消费，已同步。
- Docs targeted re-review：README/USAGE 的安装方式、MCP tool contract、用户命令、Release 文件结构均不改变；没有长期用户文档事实需要同步，因此不制造 README/USAGE diff。
- Review 没有发现“文档为了迎合实现而合法化错误”的情况；Router 与 Reference 描述与最终 evaluator 语义一致。

# 兼容、迁移、部署与回滚

- API/schema：Task Route、Skill/Reference metadata、MCP/Bundle/Payload schema/version 均保持不变。
- Stable ID：现有 ID 不改；新增 Backend profile 使用 `coding.reference.27`。
- 数据迁移：not_applicable，无业务数据变化。
- 依赖/Runtime：不升级依赖和 Runtime。
- 部署/Release：本任务不发布 Release；合并后现有后续 Release 会自然从 canonical source 构建新 routing evaluator。
- 回滚：若 owner-gated routing 产生不可接受兼容回归，可回退本 Change 的 evaluator/Router/Reference 提交；不需要数据回滚。

# 交付

- Issue：https://github.com/dingyuwen777/Agent_Skills/issues/178
- 分支：`chg/testing-coding-context-governance`
- Red 提交：`c4ed0fef6867afb390b526be7b647f5e45862fba`
- Implementation 提交：`e5cbbca5c4efee49b802d5af7ca06749a16221e2`
- 修正提交：`2c407df882c5212fe618097cb9193e76ce82ef61`
- 清理提交：`ffbe921c622c8bfa11d5def00ba5cb30807e3c59`
- Ready 提交：由本次 Change 状态更新生成，等待 final-head CI。
- PR：https://github.com/dingyuwen777/Agent_Skills/pull/179
- Release：not_applicable；本任务明确不发布 Release
