---
schema: coding-change/v1
id: CHG-20260831-repository-l1-fast-path
title: 仓库内 L1 轻量实现与渐进式上下文加载
level: L2
status: in_progress
owner: dingyuwen777
branch: feat/repository-l1-fast-path
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - coding
  - routing
  - governance
  - runtime-context
  - tests
affected_paths:
  - .agents/skills/coding/references/02_跨项目研发任务路由.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/18_最小充分治理与升级门禁.md
  - .agents/skills/coding/references/20_L1轻量实现与验证路径.md
  - .agents/skills/coding/tests/test_repository_l1_fast_path.py
  - .agents/skills/coding/tests/test_minimal_sufficient_governance.py
  - .agents/skills/coding/tests/test_routing_conformance.py
contracts:
  - Agent Skills Reference路由/v1
  - Agent Skills 任务路由/v1
data_changes: []
---

# 目标

在保留 L1/L2/L3、安全、兼容、验证和真实项目门禁的前提下，让已有仓库中的隔离 L1 小改使用真正轻量的实现/验证路径，并减少无真实价值的大型 Reference 预加载。

# 成功标准

- [ ] 已有仓库中的行为不变机械修改或边界明确、影响隔离的极小修复，可以进入 Repository L1 Fast Path，不因“持久修改仓库”本身升级成完整 Feature/Bug 流程。
- [ ] 已确认根因的 L1 小修复不会仅因 `阶段=缺陷修复` 自动加载完整设计/根因调试 Reference；根因未知或显式诊断仍加载完整调试规则。
- [ ] L1 targeted validation 使用最便宜且直接的 parse/compile/typecheck/targeted test/regression 证据，不仅因 `能力=测试` 或 `执行模式=验证` 自动加载完整 Validation Matrix Reference。
- [ ] 普通 L1/L2 不机械加载最小充分治理长 Reference；真实 Change/Completion/Review/Git/Release/多人协作/CI 治理事实仍可达并保持原强度。
- [ ] Docs Impact 与独立 Review 保持条件式；L3、公共 Contract、Schema/Migration、安全、依赖/Runtime、CI/Release 等升级路径不降级。
- [ ] Source Mode 与 Runtime 使用同一 canonical metadata 求值；新增 Reference 可被动态发现、Bundle exact-text 与 Routing Conformance 验证，不引入固定白名单或 Task Route schema 变化。

# 范围

只修改 Coding 的 L1 路由与相关 Reference metadata、永久路由回归和本 Change。新增一份短小的 L1 实现/验证 Reference 作为 Repository Fast Path Owner；不把轻量规则复制进 Router 或新增顶层 Skill。

# 非目标

不新增 L0；不改变 Runtime Task Route 顶层 schema、MCP Tool Contract、Bundle/Project Payload schema、Installer、Release 资产结构或依赖版本；不修改任何业务项目 Overlay；不降低 L2/L3 现有质量门禁。

# 必须保持不变

- 当前事实优先、用户工作保护、权限边界、不静默升级/扩大范围、新鲜证据门禁保持。
- 行数少不能作为 L1 依据；public API/ABI/CLI/config/serialization/Schema/Migration/数据语义、认证授权、安全、重大依赖/Runtime/部署/破坏性兼容仍按真实风险升级。
- 根因未知的 Bug、Incident、性能问题仍保留完整诊断/验证责任。
- Docs、Review、Git/PR/Release 由现有 Owner 和真实项目门禁决定，不因轻量化被删除。
- Reference Stable ID、依赖闭包、动态发现、Runtime exact-text/hash 和 fail-closed 语义保持。

# 关键决策

1. 不新增顶层 `simple-coding` Skill；L1 仍由 Coding Owner。
2. 新增短小 `L1轻量实现与验证路径` Reference，避免把 Repository Fast Path 重新膨胀进 Coding Core。
3. 通过收窄 ref05/ref07/ref19 的触发条件降低 Context，而不是删除其完整专业内容。
4. 已确认根因的 L1 小修复与根因未知的诊断任务分流；后者通过 `执行模式=诊断` 单调升级到完整根因调试。
5. L1 仍必须有 targeted validation；减负只减少无关层，不取消验证。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 简单仓库代码不应机械走编码、文档、审查全部流程 | user:current-request | not_satisfied | 待实现 Repository L1 Fast Path 与路由回归 |
| R2 | 按已讨论方案修改 Agent_Skills canonical 并最终合并 main | user:current-request | not_satisfied | 当前分支实施中，尚未合并 |
| R3 | 不降低 L2/L3、安全、兼容、验证和真实项目门禁 | .agents/MAINTENANCE.md | not_satisfied | 待 conformance 升级反例与独立 Review 验证 |
| R4 | Skill Mutation 保持内容守恒、Stable ID、metadata compiler、Source/Runtime parity | .agents/skills/coding/references/15_规则内容守恒与Skill维护.md | not_satisfied | 待 self-contained tests 与 Runtime routing roundtrip |
| R5 | 新 Reference 动态发现、canonical exact-text/hash、Bundle/Project Payload 不引入静态白名单 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待 Bundle/Runtime tests |
| R6 | 源仓库 L2 Mutation 经正式 Change、独立 Review、PR/CI、main fresh CI、归档清理 | .agents/MAINTENANCE.md | not_satisfied | 当前 Change in_progress |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | L1 实现、L1 已知根因 Bug、L1 诊断升级、L2/L3 保留的 evaluator 回归 |
| 接口 / 契约 | required | agent-routing metadata、Stable ID、依赖闭包、Task Route evaluator 与 Source/Runtime parity |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变业务 persistence/runtime dependency |
| 用户 / 工作流验收 | required | 自然任务信号 → required Context；轻量正例与升级反例 |
| 跨组件关键路径 | required | canonical metadata → compile/evaluate → Bundle/Runtime required Context exact-text |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方 Provider 当前事实 |
| 构建 / 打包 / 运行 | required | 新 Reference 动态进入 Bundle/Project Payload 构建与 Runtime package/self-contained 回归 |
| 文档 / 治理 / 其他 | required | Change Ready、内容守恒、独立 Review、PR/main CI 与归档 |

# 完成审计

- [ ] upstream_re_read：重新读取用户要求、根 AGENTS、Maintenance、Entry、Router、Coding、Skill Mutation、Runtime 分发与所有受影响 canonical References。
- [ ] change_coverage：确认 Repository L1 Fast Path、trigger 收窄、升级边界、测试、Review、PR/main CI 和归档全部进入本 Change。
- [ ] reverse_audit：从 scratch、Repository L1、已知/未知根因 Bug、L2 Feature、L3 Contract、Docs、Review、Git/Release 反向验证 required Context。
- [ ] unresolved_cleared：Requirement Traceability 无 not_satisfied。

# 任务

- [x] 确认 main HEAD、当前维护规则、既有轻量治理 Change 和真实缺口
- [x] 建立专用分支与正式 L2 Change
- [ ] 先补 Repository L1 路由失败回归并取得 Red 证据
- [ ] 新增 L1 轻量实现与验证 Reference
- [ ] 收窄根因调试、Validation、最小充分治理 metadata trigger
- [ ] 同步跨项目路由正文与永久 Routing Conformance
- [ ] 运行 targeted 与 full self-contained tests
- [ ] 完成 Completion Audit 并进入 ready_for_review
- [ ] 独立 Review 无 blocker
- [ ] PR CI 全绿并合并 main
- [ ] main fresh CI 全绿
- [ ] 归档 Change、清理 active，并验证归档后的 main fresh CI

# 验证

## 新鲜证据

当前仅完成源码调查与 Change 建立；尚未取得实现测试、PR CI 或 main fresh CI 证据。

# 文档影响

`targeted`：只影响 Agent_Skills canonical Coding/路由治理正文与对应测试。README、USAGE、runtime/README 的安装方式、产品接口和最终用户操作不变，除非实现中发现相反事实。

# 交付

- 分支：`feat/repository-l1-fast-path`
- PR：未创建
- CI：未运行
- Review：未执行
- main：尚未修改
- Release：不涉及
