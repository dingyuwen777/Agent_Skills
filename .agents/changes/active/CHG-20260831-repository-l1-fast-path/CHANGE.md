---
schema: coding-change/v1
id: CHG-20260831-repository-l1-fast-path
title: 仓库内 L1 轻量实现与渐进式上下文加载
level: L2
status: ready_for_review
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
  - .agents/skills/coding/tests/test_reference_numbering.py
  - .agents/skills/coding/tests/test_router_skill_migration.py
  - .agents/skills/coding/tests/test_routing_conformance.py
contracts:
  - Agent Skills Reference路由/v1
  - Agent Skills 任务路由/v1
data_changes: []
---

# 目标

在保留 L1/L2/L3、安全、兼容、验证和真实项目门禁的前提下，让已有仓库中的隔离 L1 小改使用真正轻量的实现/验证路径，并减少无真实价值的大型 Reference 预加载。

# 成功标准

- [x] 已有仓库中的行为不变机械修改或边界明确、影响隔离的极小修复，可以进入 Repository L1 Fast Path，不因“持久修改仓库”本身升级成完整 Feature/Bug 流程。
- [x] 已确认根因的 L1 小修复不会仅因 `阶段=缺陷修复` 自动加载完整设计/根因调试 Reference；根因未知或显式诊断仍加载完整调试规则。
- [x] L1 targeted validation 使用最便宜且直接的 parse/compile/typecheck/targeted test/regression 证据，不仅因 `能力=测试` 或 `执行模式=验证` 自动加载完整 Validation Matrix Reference。
- [x] 普通 L1/L2 不机械加载最小充分治理长 Reference；真实 Change/Completion/Review/Git/Release/多人协作/CI 治理事实仍可达并保持原强度。
- [x] Docs Impact 与独立 Review 保持条件式；L3、公共 Contract、Schema/Migration、安全、依赖/Runtime、CI/Release 等升级路径不降级。
- [x] Source Mode 与 Runtime 使用同一 canonical metadata 求值；新增 Reference 可被动态发现、Bundle exact-text 与 Routing Conformance 验证，不引入固定白名单或 Task Route schema 变化。

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
6. `能力=测试` 继续保留在公开 Task Route 词汇中，但由 L1 Reference 的 `风险=L1 AND 能力=测试` 分支承载词汇；普通 L2/L3 仍按风险加载完整 Validation Reference，避免为了兼容公开词汇重新增加 L1 重上下文。
7. 历史 Context 预算只为本次新增 ref21 与 ref02 导航增量做定点补偿，不扩大其他任务家族的欠披露容忍度。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 简单仓库代码不应机械走编码、文档、审查全部流程 | user:current-request | satisfied | PR #123 当前 head `c2e5c68b62fa151ae7c024a4a5616582f3f4fd52`；`test_repository_l1_fast_path`、最小充分治理与永久 conformance 在 Skill Tests #741 的 280/280 self-contained tests 中通过 |
| R2 | 按已讨论方案修改 Agent_Skills canonical 并最终合并 main | user:current-request | explicitly_deferred | canonical 修改已在 PR #123；用户已明确授权最终合并，按 Maintenance 顺序在独立 Review 与 PR 全绿后执行 main merge，再补 main fresh CI 证据 |
| R3 | 不降低 L2/L3、安全、兼容、验证和真实项目门禁 | .agents/MAINTENANCE.md | satisfied | Skill Tests #741 验证 L2 Feature、Gated L2、L3 public API、Schema Migration、Incident、Review/Git/Release/CI/Runtime 等升级反例；280/280 tests OK |
| R4 | Skill Mutation 保持内容守恒、Stable ID、metadata compiler、Source/Runtime parity | .agents/skills/coding/references/15_规则内容守恒与Skill维护.md | satisfied | Skill Tests #741：metadata 合法性、Stable ID、Routing Conformance、Source/Runtime manifest 同值、历史安全 baseline 与 Runtime routing tests 全部通过 |
| R5 | 新 Reference 动态发现、canonical exact-text/hash、Bundle/Project Payload 不引入静态白名单 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | Skill Tests #741：dynamic distribution、Bundle exact reference text/hash、Project Payload no-reference、Runtime projection 与 routing roundtrip 全部通过 |
| R6 | 源仓库 L2 Mutation 经正式 Change、独立 Review、PR/CI、main fresh CI、归档清理 | .agents/MAINTENANCE.md | explicitly_deferred | 正式 Change 与 PR #123 已建立，self-contained CI 已全绿；独立 Review、PR 最终绿色、main fresh CI 与归档是 Maintenance 规定的后续交付阶段 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Skill Tests #741：Repository L1、已知根因 Bug、未知根因诊断升级、L1 validation、L2/L3 evaluator 回归全部通过 |
| 接口 / 契约 | required | `能力=测试` 公共词汇兼容、agent-routing metadata、Stable ID、依赖闭包、Task Route evaluator 与 Source/Runtime parity 在 #741 通过 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 本次不改变业务 persistence/runtime dependency |
| 用户 / 工作流验收 | required | 永久 Routing Conformance 覆盖 Scratch、Repository L1、Bug、L2/L3、Docs、Review、Git/Release、Runtime 与复杂组合，#741 通过 |
| 跨组件关键路径 | required | canonical metadata → compile/evaluate → Bundle/Runtime required Context exact-text/hash，在 #741 通过 |
| 外部依赖 / 供应方探测 | not_applicable | 本次没有第三方 Provider 当前事实或生产写操作 |
| 构建 / 打包 / 运行 | required | #741 的 maintained scripts/runtime `py_compile` 与 CLI smoke 成功；动态 Bundle/Project Payload/Runtime self-contained 回归成功 |
| 文档 / 治理 / 其他 | required | Change 已完成语义审计并进入 ready_for_review；独立 Review、PR 最终门禁、main fresh CI 与归档按后续交付顺序执行 |

# 完成审计

- [x] upstream_re_read：已重新读取用户要求、当前分支根 AGENTS、Maintenance、Entry、Router、Coding、Skill Mutation、Runtime 分发以及 ref02/ref04/ref05/ref07/ref10/ref11/ref13/ref14/ref15/ref18 等受影响 canonical 事实。
- [x] change_coverage：Repository L1 Fast Path、ref05/ref07/ref19 trigger 收窄、公开测试能力词汇兼容、编号/历史迁移基准、升级反例、PR/main CI 和归档交付均已进入本 Change。
- [x] reverse_audit：永久回归从 Scratch/Repository L1/已知与未知根因 Bug 反查到 L2 Feature/Gated L2/L3 Contract/Schema、Docs、Review、Git/Release、Runtime 与 unknown fail-safe，280/280 tests 全绿。
- [x] unresolved_cleared：需求追溯当前无 `not_satisfied`；R2/R6 的 merge/main CI/archive 明确由 Maintenance 固定在 Ready/Review 后的交付阶段执行，并有用户授权。

# 任务

- [x] 确认 main HEAD、当前维护规则、既有轻量治理 Change 和真实缺口
- [x] 建立专用分支与正式 L2 Change
- [x] 先补 Repository L1 路由失败回归并取得 Red 证据
- [x] 新增 L1 轻量实现与验证 Reference
- [x] 收窄根因调试、Validation、最小充分治理 metadata trigger
- [x] 同步跨项目路由正文与永久 Routing Conformance
- [x] 运行 targeted 与 full self-contained tests
- [x] 完成 Completion Audit 并进入 ready_for_review
- [ ] 独立 Review 无 blocker
- [ ] PR CI 全绿并合并 main
- [ ] main fresh CI 全绿
- [ ] 归档 Change、清理 active，并验证归档后的 main fresh CI

# 验证

## Red 证据

PR #123 首轮 Skill Tests run `33392382064` / job `99488823100`：`Ran 279 tests`，`FAILED (failures=6)`。六个失败均来自本次新增的 Repository L1 回归，分别证明 ref21 缺失、L1 Bug/validation/ref19 过度加载和普通 L2 governance 预加载；旧有回归保持绿色。

## Green 证据

PR #123 Skill Tests run `33393892870` / job `99493713079`，测试目标为 head `c2e5c68b62fa151ae7c024a4a5616582f3f4fd52` 的 PR merge candidate：

- maintained scripts/runtime `py_compile`：成功；
- maintained CLI entrypoint smoke：成功；
- self-contained tests：`Ran 280 tests in 4.942s`，`OK`；
- `Verify changed Coding Change`：仅因当时 Change 仍为 `in_progress` 被 Ready Check 阻止，未发现实现测试失败。

这次 280 个测试已经覆盖 metadata compiler/roundtrip、Stable ID、routing conformance、历史迁移安全基线、Bundle exact-text/hash、dynamic Skill/Reference discovery、Project Payload、Runtime projection 与 Source/Runtime parity。

# 文档影响

`targeted`：本次只改变 Agent_Skills canonical Coding 路由/治理语义与对应永久测试。根 `README.md`、`USAGE.md`、`runtime/README.md` 的安装方式、最终用户操作、Runtime 产品接口、Release 资产和部署方式没有改变，因此不制造这些人类文档 diff。

# 交付

- 分支：`feat/repository-l1-fast-path`
- PR：#123 `增加仓库 L1 轻量实现与验证路径`
- CI：#741 self-contained 280/280 绿色；下一轮验证 `ready_for_review` 的 changed Change 门禁
- Review：按 Maintenance 在 Ready 后执行独立 Review
- main：feature merge 按独立 Review + PR CI 全绿后执行
- Release：不涉及；Runtime schema、Installer、Release artifact 与依赖版本均未改变
