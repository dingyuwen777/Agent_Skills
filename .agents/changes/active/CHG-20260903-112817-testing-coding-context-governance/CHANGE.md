---
schema: coding-change/v1
id: CHG-20260903-112817-testing-coding-context-governance
title: 收口 Testing Coding 职责并加固路由上下文治理
level: L2
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
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/08_分层测试与验收策略.md
  - .agents/skills/coding/references/25_Testing专业职责与Handoff.md
  - .agents/skills/coding/references/26_后端服务实施与运行边界.md
  - .agents/skills/testing/SKILL.md
  - .agents/skills/testing/references/01_测试策略与分层证据.md
  - .agents/skills/coding/tests/test_testing_skill.py
  - .agents/skills/coding/tests/test_skill_owner_isolation.py
  - .agents/skills/coding/tests/test_route_context_budget.py
  - .agents/skills/coding/tests/test_source_runtime_context_conformance.py
  - .agents/skills/coding/tests/test_testing_runtime_projection.py
contracts:
  - Agent Skills Skill路由/v1
  - Agent Skills Reference路由/v1
  - Agent Skills 任务路由/v1
data_changes: []
---

# 目标

完成 Testing 从 Coding 中的职责收口，并把渐进式披露从“单文件不太大”升级为可回归的真实 Route 上下文约束：纯 Testing 任务不再因项目形态、风险或授权事实附带加载 Coding Core；Coding 只保留开发期 TDD、验证证据治理与 Testing Handoff；后端实现获得独立的 Coding 专项 profile，但不新增 Backend Skill。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/178

# 成功标准

- [ ] Testing-only + 已知项目形态/风险不会命中 Coding，也不会加载 Coding 测试专项/Handoff Reference。
- [ ] Coding + 独立测试意图仍组合 Coding + Testing，并保持生产修复、Regression、Review 的既有 Handoff。
- [ ] Coding 分层测试专项只保留证据边界/Testing Handoff，不复制 Test Strategy、Black-box、User Journey、Integration、Golden Path、Probe、Regression 的详细方法。
- [ ] 代表性 Route 有永久 Context Budget 回归，并直接按真实 Skill Core + required Reference 计算预算。
- [ ] Source evaluator 与 RuntimeStore 对 facts-complete route 返回完全一致的 required canonical Context。
- [ ] Runtime Projection 显式保留 Testing 的 Owner/Handoff/Black-box/Regression 核心语义，并继续隐藏 Reference identity。
- [ ] 新增 Backend/Service Coding Reference，覆盖服务端实现/运行边界，不新增 Backend Skill、不复制 Testing/Review/Git/CI 细则。
- [ ] 动态 Skill Catalog、Project Payload no-Reference、防披露和现有 Runtime/MCP 协议保持不变。
- [ ] 独立 Review、PR CI、REST guarded merge、main fresh CI 和 Change archive 闭环完成。

# 范围

- 收窄 Coding Skill 级 Owner trigger。
- 收口 Coding 分层测试专项 Reference 与 Testing Owner 的边界。
- 新增 Backend/Service Coding 专项 Reference。
- 增加职责隔离、Route Context Budget、Source/Runtime required Context、Testing Runtime Projection 永久回归。
- 仅同步受影响的 canonical Skill/Reference 与测试；没有独立用户文档事实变化时不制造 README/USAGE diff。

# 非目标

- 不新增 Frontend/Backend/Git/CI/Release 正式 Skill。
- 不改变 Runtime Bundle、Project Payload、MCP Tool Contract、Task Route 顶层 schema/version。
- 不升级 Python、依赖、GitHub Actions、Runtime 或包管理工具。
- 不修改仓库可见性。
- 不发布新 Release。
- 不把所有 Coding 实现机械升级为独立 Testing；普通开发期最小 TDD 仍由 Coding 完成。

# 必须保持不变

- Coding 的 Red → Verify Red → Green → Refactor → Re-verify、Requirement Traceability、Validation Matrix、Completion Audit、Git/CI/Release 门禁继续有效。
- Testing 是 Test Strategy、Scenario-based Black-box、User Journey、Exploratory、Integration/Contract/Golden Path/Probe、Regression 与测试资产方法的唯一专业 Owner。
- Review 保留独立需求/实现审查、测试充分性与 Evidence 判断，不复制 Testing 方法。
- Source Mode / Runtime Mode 继续使用同一 canonical metadata、Stable ID、依赖和 required Context 语义。
- Reference Stable ID 不因文件内容收口而重写；已有 `coding.reference.08` 与 `coding.reference.26` 保持身份稳定。
- Runtime Project Payload 不安装 canonical Reference/Stub；公共 MCP 返回不公开 Reference identity。
- 项目形态、风险、能力、授权可以细化已命中 Skill，但不能凭自身制造不相关专业 Owner。

# 关键决策

- 不删除 `coding.reference.08`，而把它收口为小型“分层证据边界 / Testing Handoff profile”，保留已有 Stable ID 和 live link，避免为职责迁移制造不必要 Contract/链接破坏；详细测试工程方法继续唯一存在于 Testing。
- Coding Skill Owner 选择只依赖真正的 Coding `执行模式`；项目形态、风险和授权继续作为 Reference refinement/task facts，不再单独把 Coding Core 拉入纯 Testing 任务。
- Backend/Service 作为 Coding Reference 而不是新 Skill：它解决服务端实现特有的 transaction/idempotency/concurrency/async/resource lifecycle 等实现责任，但 Testing/Review/Git/CI 继续由现有 Owner 负责。
- Context Budget 使用代表性真实 Task Route 的 Core + required Reference bytes 建永久回归；阈值以本次收口后的实际基线加小幅维护余量建立，禁止为了让回归变绿随意抬高。
- Source/Runtime 一致性验证 required canonical Context，而不要求 LLM 最终自然语言逐字一致。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 项目形态/风险/授权不再单独触发 Coding Owner | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 初始 Red 回归待执行 |
| R2 | Testing 成为独立测试工程方法唯一 Owner，Coding 旧专项方法收口 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 初始 Red 与内容守恒复核待执行 |
| R3 | Coding + Testing 组合 Handoff 与开发期 TDD 不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | targeted routing regression 待执行 |
| R4 | 增加 Route-level Context Budget 永久回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 新永久测试待实现 |
| R5 | 增加 Source/Runtime required Context exact-text conformance | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 新永久测试待实现 |
| R6 | Testing Runtime Projection 核心语义显式受保护且不泄露 Reference identity | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 新永久测试待实现 |
| R7 | 新增 Backend/Service Coding 专项 Reference，不新增 Backend Skill | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | canonical Reference 与 routing 回归待实现 |
| R8 | 动态分发、防披露、协议与既有高价值治理语义不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | full self-contained/Runtime scope CI 待执行 |
| R9 | PR/Review/merge/main-fresh/archive 闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/178 | not_satisfied | 交付阶段取得新鲜证据后更新 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Routing owner isolation、组合 Handoff、Backend profile 与 Context Budget 的永久 `unittest` 回归 |
| 接口 / 契约 | required | `agent-routing:v1` metadata compiler、Stable ID/dependency、Source/Runtime required Context 同源 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改业务数据库、文件、队列或外部 Runtime Dependency 语义 |
| 用户 / 工作流验收 | required | 以 Task Route 作为治理调用者公开输入，验证 Testing-only、Coding+Testing、Review/Docs/Figma 代表性路由的可观察 required Context |
| 跨组件关键路径 | not_applicable | 不改变业务应用真实组件接线；Runtime 构建/投影由 Build/Package 层验证 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖任何第三方业务 Provider 当前事实 |
| 构建 / 打包 / 运行 | required | Runtime Project Payload/Projection/content scope 与当前 CI gate，必要时由 Runtime Package Scope 证明 |
| 文档 / 治理 / 其他 | required | Change/Requirement Source/Ready Check、canonical Skill/Reference 内容守恒、独立 Review、PR/main fresh CI |

# 完成审计

- [ ] upstream_re_read：重新读取 Issue #178、当前 `main` 根规则、Maintenance、Router 与受影响 canonical Owner，从上游独立重建完成定义。
- [ ] change_coverage：确认 R1-R9 全部被当前 Change 覆盖，未把 Change 自身当作需求全集。
- [ ] reverse_audit：从 Testing-only、Coding+Testing、Backend Coding、Review/Runtime Projection 反向检查 Owner 与 required Context，并复核验证矩阵。
- [ ] unresolved_cleared：所有 `not_satisfied` 已清零，任何不适用/延期均有正式依据。

# 任务

- [x] 调查当前实现、Router、Coding/Testing/Review Owner、Runtime Projection、现有永久测试与 CI。
- [x] 建立 Requirement Source Issue #178 与 L2 gated Change。
- [ ] 提交能在当前实现上稳定失败的 Testing Owner isolation Red。
- [ ] 收窄 Coding Skill Owner trigger。
- [ ] 收口 `coding.reference.08` 为证据边界/Handoff profile，并保持 Stable ID。
- [ ] 新增 Backend/Service Coding Reference 与路由回归。
- [ ] 增加 Route Context Budget、Source/Runtime Context Conformance、Testing Runtime Projection 永久测试。
- [ ] 执行 targeted 与 full self-contained 测试，修复根因且不降低断言/抬高预算逃避失败。
- [ ] 完成 A1/A2 独立 Review、Ready Check 与 Change `ready_for_review`。
- [ ] 取得 PR CI，guarded merge，main fresh CI，归档 Change 并关闭 Issue。

# 验证

## 计划

- Red：`python -m unittest .agents.skills.coding.tests.test_skill_owner_isolation -v` 或 self-contained discovery 中等价用例必须在旧实现失败。
- Targeted：Testing ownership、routing metadata、Context Budget、Source/Runtime Context、Runtime Projection、Backend profile。
- Full：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- 就绪：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready` 或 PR changed-since 等价 gate。
- CI：Skill Tests + Agent Skills Gate + Runtime Package Scope/Gate。

## 新鲜证据

- 尚未执行 Red/Green；本 Change 当前处于 `in_progress`。

# 文档影响

- `targeted`：canonical Coding/Testing 规则本身属于治理文档且会被 Runtime/LLM 消费，必须同步；当前没有发现 README/USAGE 对外使用方式需要改变，完成前再复核。

# 交付

- Issue：https://github.com/dingyuwen777/Agent_Skills/issues/178
- 分支：`chg/testing-coding-context-governance`
- 提交：待生成
- 拉取请求：待创建
- 发布：not_applicable；本任务明确不发布 Release
