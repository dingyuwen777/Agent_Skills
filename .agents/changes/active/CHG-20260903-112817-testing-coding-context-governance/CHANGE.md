---
schema: coding-change/v1
id: CHG-20260903-112817-testing-coding-context-governance
title: 收口 Testing Coding 职责并加固路由上下文治理
level: L3
status: in_progress
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

- [ ] Testing-only + 已知项目形态/风险/范围不会命中 Coding，也不会加载 Coding 测试专项/Handoff Reference。
- [ ] Skill Owner 先于 Reference refinement：直接 Reference 不能反向激活未命中 Owner；显式 dependency 仍可跨 Skill 扩展 Owner。
- [ ] Coding + 独立测试意图仍组合 Coding + Testing，并保持生产修复、Regression、Review 的既有 Handoff。
- [ ] Coding 分层测试专项只保留证据边界/Testing Handoff，不复制 Test Strategy、Black-box、User Journey、Integration、Golden Path、Probe、Regression 的详细方法。
- [ ] 代表性 Route 有永久 Context Budget 回归，并直接按真实 Skill Core + required Reference 计算预算。
- [ ] Source evaluator 与 RuntimeStore 对 facts-complete route 返回完全一致的 required canonical Context。
- [ ] Runtime Projection 显式保留 Testing 的 Owner/Handoff/Black-box/Regression 核心语义，并继续隐藏 Reference identity。
- [ ] 新增 Backend/Service Coding Reference，覆盖服务端实现/运行边界，不新增 Backend Skill、不复制 Testing/Review/Git/CI 细则。
- [ ] 动态 Skill Catalog、公共 Task Route 词汇、Project Payload no-Reference、防披露和现有 Runtime/MCP 协议保持不变。
- [ ] 独立 Review、PR CI、guarded merge、main fresh CI 和 Change archive 闭环完成。

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
- Reference Stable ID 不因文件内容收口而重写；已有 `coding.reference.08` 与 `coding.reference.26` 保持身份稳定，新 Backend profile 使用新 Stable ID。
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

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | refinement facts 不再单独触发 Coding/其他专业 Owner | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | Red：PR #179 head `c4ed0fef...`，Skill Tests run #1026 在 self-contained tests 失败 |
| R2 | direct Reference 受 Owner gate，显式 dependency 仍可跨 Skill | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 新 evaluator + isolation fixture 待 Green |
| R3 | Testing 成为独立测试工程方法唯一 Owner，Coding 旧专项方法收口 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | ref08/ref25 内容守恒与 Testing 回归待 Green |
| R4 | Coding + Testing 组合 Handoff 与开发期 TDD 不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | existing/new routing regression 待 Green |
| R5 | 增加 Route-level Context Budget 永久回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 新永久测试待 Green |
| R6 | 增加 Source/Runtime required Context exact-text conformance | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 新永久测试待 Green |
| R7 | Testing Runtime Projection 核心语义显式受保护且不泄露 Reference identity | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 新永久测试待 Green |
| R8 | 新增 Backend/Service Coding 专项 Reference，不新增 Backend Skill | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | canonical Reference 与 routing 回归待 Green |
| R9 | 动态分发、公共词汇、防披露、协议与既有高价值治理语义不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | full self-contained/Runtime scope CI 待执行 |
| R10 | PR/Review/merge/main-fresh/archive 闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 交付阶段取得新鲜证据后更新 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Owner isolation、direct ref gate、cross-skill dependency、Backend profile 与 Context Budget 的永久 `unittest` 回归 |
| 接口 / 契约 | required | `agent-routing:v1` metadata compiler、Stable ID/dependency、公共 Task Route 词汇、Source/Runtime required Context 同源 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改业务数据库、文件、队列或外部 Runtime Dependency 语义 |
| 用户 / 工作流验收 | required | 以 Task Route 作为治理调用者输入，验证 Testing-only、Coding+Testing、Review/Docs/Figma 代表性路由的可观察 required Context |
| 跨组件关键路径 | not_applicable | 不改变业务应用真实组件接线；Runtime 构建/投影由 Build/Package 层验证 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖任何第三方业务 Provider 当前事实 |
| 构建 / 打包 / 运行 | required | Runtime Project Payload/Projection/content scope 与当前 CI gate，必要时由 Runtime Package Scope 证明 |
| 文档 / 治理 / 其他 | required | Change/Requirement Source/Ready Check、canonical Router/Reference 内容守恒、独立 Review、PR/main fresh CI |

# Red 证据

- 分支从 `main@eb2ca179c7284497b054bf531ec1f6cc5d54ec7f` 创建。
- Red commit：`c4ed0fef6867afb390b526be7b647f5e45862fba`（只包含 Change + owner-isolation failure tests）。
- PR #179 已创建，`Requirement-Source: #178` 校验成功。
- PR head `c4ed0fef...`：
  - Skill Tests run #1026 / run id `33711679686`：**failure**，失败阶段 `Run self-contained tests`；
  - Runtime Package Tests run #316 / run id `33711679588`：**success**；
  - Requirement Source step：success；Agent Skills Gate 因 Skill Tests failure 被阻塞。
- 该 Red 证明当前旧 evaluator 会让 Testing-only + Web/Backend/L2 refinement facts 反向拉入 Coding；尚未用规则修改掩盖失败。

# 完成审计

- [ ] upstream_re_read：重新读取 Issue #178、当前 `main` 根规则、Maintenance、Router 与受影响 canonical Owner，从上游独立重建完成定义。
- [ ] change_coverage：确认 R1-R10 全部被当前 Change 覆盖，未把 Change 自身当作需求全集。
- [ ] reverse_audit：从 Testing-only、Coding+Testing、Backend Coding、Review/Docs/Figma、Runtime Projection 反向检查 Owner 与 required Context，并复核验证矩阵。
- [ ] unresolved_cleared：所有 `not_satisfied` 已清零，任何不适用/延期均有正式依据。

# 任务

- [x] 调查当前实现、Router、Coding/Testing/Review Owner、Runtime Projection、现有永久测试与 CI。
- [x] 建立 Requirement Source Issue #178 与 gated Change。
- [x] 提交能在旧实现上稳定失败的 Testing Owner isolation Red，并取得 PR CI Red。
- [x] 根因升级：确认全局 direct Reference match 会反向激活 Owner，本 Change 升为 L3。
- [ ] 实现 Owner-gated evaluator，并保持显式 cross-Skill dependency。
- [ ] 收口 `coding.reference.08` 为证据边界/Handoff profile，保持 Stable ID。
- [ ] 新增 Backend/Service Coding Reference 与路由回归。
- [ ] 增加 Route Context Budget、Source/Runtime Context Conformance、Testing Runtime Projection 永久测试。
- [ ] 执行 implementation-head PR CI，确认 self-contained/Runtime scope 真实 Green；不通过降低断言/抬高预算逃避失败。
- [ ] 完成 A1/A2 独立 Review、Ready Check 与 Change `ready_for_review`。
- [ ] 取得 final-head PR CI，guarded merge，main fresh CI，归档 Change 并关闭 Issue。

# 验证

## 计划

- Red：已由 PR #179 head `c4ed0fef...` 的 Skill Tests run #1026 证明。
- Targeted：Owner isolation、owner-gated evaluator、Testing ownership、routing metadata、Context Budget、Source/Runtime Context、Runtime Projection、Backend profile。
- Full：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`（由 GitHub Skill Tests 的真实 checkout 执行）。
- 就绪：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready` 或 PR changed-since 等价 gate。
- CI：Skill Tests + Agent Skills Gate + Runtime Package Scope/Gate。

## 新鲜证据

- 当前只有 Red 与 baseline Runtime scope Green；Implementation Green 尚未取得，不能宣称修复完成。

# 文档影响

- `targeted`：canonical Router 与 Coding/Testing Handoff Reference 本身属于治理文档并直接被 Source/Runtime/LLM 消费，必须同步。
- README/USAGE 的安装方式、MCP tool contract、用户命令、Release 文件结构均不改变；当前没有独立长期用户文档事实变化，不制造 README/USAGE diff。完成前再做 targeted re-review。

# 兼容、迁移、部署与回滚

- API/schema：Task Route、Skill/Reference metadata、MCP/Bundle/Payload schema/version 均保持不变。
- Stable ID：现有 ID 不改；新增 Backend profile 使用新 ID。
- 数据迁移：not_applicable，无业务数据变化。
- 依赖/Runtime：不升级依赖和 Runtime。
- 部署/Release：本任务不发布 Release；合并后现有后续 Release 会自然从 canonical source 构建新 routing evaluator。
- 回滚：若 owner-gated routing 产生不可接受兼容回归，可回退本 Change 的 evaluator/Router/Reference 提交；不需要数据回滚。

# 交付

- Issue：https://github.com/dingyuwen777/Agent_Skills/issues/178
- 分支：`chg/testing-coding-context-governance`
- Red 提交：`c4ed0fef6867afb390b526be7b647f5e45862fba`
- Implementation 提交：待生成
- PR：https://github.com/dingyuwen777/Agent_Skills/pull/179
- Release：not_applicable；本任务明确不发布 Release
