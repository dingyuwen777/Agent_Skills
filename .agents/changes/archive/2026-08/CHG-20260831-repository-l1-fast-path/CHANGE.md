---
schema: coding-change/v1
id: CHG-20260831-repository-l1-fast-path
title: 仓库内 L1 轻量实现与渐进式上下文加载
level: L2
status: done
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
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/02_跨项目研发任务路由.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/18_最小充分治理与升级门禁.md
  - .agents/skills/coding/references/20_L1轻量实现与验证路径.md
  - .agents/skills/coding/tests/test_coding_progressive_disclosure.py
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
- [x] Source Mode 与 Runtime 的轻量路由语义一致；新增 Reference 可被动态发现、Bundle exact-text 与 Routing Conformance 验证，不引入固定白名单或 Task Route schema 变化。
- [x] 为 Source Mode 明文路由增加的 Coding Core 固定成本受硬预算约束，且普通轻量 L2 的 Reference 上下文和总上下文都严格小于历史基线。

# 范围

只修改 Coding 的 L1 路由、Source Mode 人类可读入口、相关 Reference metadata、永久路由/上下文回归和本 Change。新增一份短小的 L1 实现/验证 Reference 作为 Repository Fast Path Owner；不把轻量规则复制进 Router 或新增顶层 Skill。

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
2. 新增短小 `L1轻量实现与验证路径` Reference，避免把 Repository Fast Path 重新膨胀成第二套完整研发流程。
3. 通过收窄 ref05/ref07/ref19 的触发条件降低 Context，而不是删除其完整专业内容。
4. 已确认根因的 L1 小修复与根因未知的诊断任务分流；后者通过 `执行模式=诊断` 单调升级到完整根因调试。
5. L1 仍必须有 targeted validation；减负只减少无关层，不取消验证。
6. `能力=测试` 继续保留在公开 Task Route 词汇中，但由 L1 Reference 的 `风险=L1 AND 能力=测试` 分支承载词汇；普通 L2/L3 仍按风险加载完整 Validation Reference，避免为了兼容公开词汇重新增加 L1 重上下文。
7. Source Mode Core 必须显式导航 Repository L1，避免 Runtime metadata 已轻量而明文模式仍被旧表述拉回重流程。
8. Coding Core 从历史基线 `48,012 B` 增至 `50,105 B`，固定增量 `2,093 B`；永久回归以 `51,000 B` / `760` 行作为硬上限，并在历史迁移基准只允许 `2,300 B` 的固定 Source Mode Fast Path 预算。与此同时，轻量 L2 必须额外证明 Reference bytes 与 total context bytes 均严格低于旧基线，不能用预算放宽掩盖净膨胀。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 简单仓库代码不应机械走编码、文档、审查全部流程 | user:current-request | satisfied | PR #123 最终 head `ce3314a1343d1df9149a970c9e771010f5f71697`；Skill Tests #747 全绿，Repository L1、已知根因 Bug、未知根因诊断升级、L1 validation、Source Mode Core 与上下文净减负回归均通过 |
| R2 | 按已讨论方案修改 Agent_Skills canonical 并最终合并 main | user:current-request | satisfied | PR #123 已合并；merge commit `060e81bec3a04328c3a87d2365e27d56c7fd22b2`；main Skill Tests #748 成功 |
| R3 | 不降低 L2/L3、安全、兼容、验证和真实项目门禁 | .agents/MAINTENANCE.md | satisfied | #747 / #748 覆盖 L2 Feature、Gated L2、L3 public API、Schema Migration、Incident、Review/Git/Release/CI/Runtime/unknown fail-safe 等升级反例，281/281 self-contained tests OK |
| R4 | Skill Mutation 保持内容守恒、Stable ID、metadata compiler、Source/Runtime parity | .agents/skills/coding/references/15_规则内容守恒与Skill维护.md | satisfied | #747 / #748 验证 metadata 合法性、Stable ID、Routing Conformance、Source/Runtime manifest 同值、历史安全 baseline、Runtime routing 与 Source Mode Core 反向检查 |
| R5 | 新 Reference 动态发现、canonical exact-text/hash、Bundle/Project Payload 不引入静态白名单 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | #747 / #748 验证 dynamic distribution、Bundle exact reference text/hash、Project Payload no-reference、Runtime projection 与 routing roundtrip |
| R6 | 源仓库 L2 Mutation 经正式 Change、独立 Review、PR/CI、main fresh CI、归档清理 | .agents/MAINTENANCE.md | satisfied | 正式 Change、独立 re-review、PR #123、最终 PR #747、merge `060e81be...` 与 main #748 均完成；本归档提交原子移动 Change 并清理 active，归档 PR/main 后续 fresh CI 由 GitHub PR/Actions 历史保存 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Skill Tests #747 与 main #748：Repository L1、已知根因 Bug、未知根因诊断升级、L1 validation、L2/L3 evaluator 回归通过 |
| 接口 / 契约 | required | `能力=测试` 公共词汇兼容、agent-routing metadata、Stable ID、依赖闭包、Task Route evaluator 与 Source/Runtime parity 在 #747/#748 通过 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 本次不改变业务 persistence/runtime dependency |
| 用户 / 工作流验收 | required | Routing Conformance 覆盖 Scratch、Repository L1、Bug、L2/L3、Docs、Review、Git/Release、Runtime、unknown 与复杂组合，在 #747/#748 通过 |
| 跨组件关键路径 | required | canonical metadata → compile/evaluate → Bundle/Runtime required Context exact-text/hash，以及 Source Mode Core → L1 Reference 可达性，在 #747/#748 通过 |
| 外部依赖 / 供应方探测 | not_applicable | 本次没有第三方 Provider 当前事实或生产写操作 |
| 构建 / 打包 / 运行 | required | #747/#748 maintained scripts/runtime `py_compile` 与 CLI smoke 成功；动态 Bundle/Project Payload/Runtime self-contained 回归成功；Runtime package workflow 按纯 Skill/Reference changed scope 不适用 |
| 文档 / 治理 / 其他 | required | changed Change Ready Check、独立 re-review、PR 合并、main fresh CI 均完成；本提交将 Change 更新为 done 并从 active 移入 archive |

# 完成审计

- [x] upstream_re_read：重新读取用户要求、目标分支根 AGENTS、Maintenance、Entry、Router、Coding、Skill Mutation、Runtime 分发、Review Skill 与本次 required Coding/Review References。
- [x] change_coverage：Repository L1 Fast Path、Source Mode Core、ref05/ref07/ref19 trigger 收窄、公开测试能力词汇兼容、Stable ID、历史迁移基准、上下文预算、升级反例和交付闭环均已覆盖。
- [x] reverse_audit：从 Scratch/Repository L1/已知与未知根因 Bug 反查到 L2 Feature/Gated L2/L3 Contract/Schema、Docs、Review、Git/Release、Runtime 与 unknown fail-safe；永久回归证明普通轻量 L2 的 Reference bytes 与 total context bytes 均严格低于历史基线。
- [x] unresolved_cleared：需求追溯无 `not_satisfied`；所有功能/治理实现、独立 Review、PR CI、merge 与 main fresh CI 均已有新鲜证据。

# 任务

- [x] 确认 main HEAD、当前维护规则、既有轻量治理 Change 和真实缺口
- [x] 建立专用分支与正式 L2 Change
- [x] 先补 Repository L1 路由失败回归并取得 Red 证据
- [x] 新增 L1 轻量实现与验证 Reference
- [x] 收窄根因调试、Validation、最小充分治理 metadata trigger
- [x] 同步跨项目路由正文与永久 Routing Conformance
- [x] 运行 targeted 与 full self-contained tests
- [x] 完成 Completion Audit 并进入 ready_for_review
- [x] 修复独立 Review 发现的 Source Mode / Runtime 路由不一致并补回归
- [x] 量化 Source Mode Core 固定成本，并用净上下文断言锁住轻量化收益
- [x] 最终独立 re-review 无 blocker / important finding
- [x] PR 最终 CI 全绿并合并 main
- [x] main fresh CI 全绿
- [x] 将 Change 更新为 done 并从 active 原子移动到 archive

# 验证

## Red 证据 1：Repository L1 缺口

PR #123 首轮 Skill Tests run `33392382064` / job `99488823100`：`Ran 279 tests`，`FAILED (failures=6)`。六个失败均来自本次新增的 Repository L1 回归，分别证明新 L1 Reference 缺失、L1 Bug/validation/治理过度加载和普通 L2 governance 预加载；旧有回归保持绿色。

## Red 证据 2：Source Mode 路由不一致

独立 Review 发现 Runtime metadata 已进入轻量路径，但 `coding/SKILL.md` 人类可读路由仍把 Bug/Feature/Refactor 机械导向完整实施/调试规则。新增 Source Mode 回归后，Skill Tests run `33394373981` / job `99495256148`：`Ran 281 tests in 4.548s`，仅新增的 Source Mode 一致性回归失败，其余 280 个测试保持绿色，证明 finding 可稳定复现。

## 上下文预算证据

Source Mode Core 修复后，Skill Tests #744 暴露旧静态预算：路由正确性已经绿色，但 Coding Core 因显式 Repository L1 导航从主分支历史基线 `48,012 B` 增至 `50,105 B`（`+2,093 B`）。最终没有删除高价值 Core 语义或无界放宽预算，而是：

- Core 永久硬上限：`51,000 B`、`760` 行；
- 历史迁移预算只增加固定 `2,300 B` Source Mode Fast Path 上限；
- `L2 Feature` 反向断言要求当前 Reference bytes 与 total context bytes 都严格小于历史 baseline。

## Green 证据 1：实现与预算回归

PR #123 Skill Tests #746 / run `33395303226` / job `99498286112`，目标 head `c5491031209fffafb909beeb8a92f078363ec8d8`：

- maintained scripts/runtime `py_compile`：成功；
- maintained CLI entrypoint smoke：成功；
- self-contained tests：`281/281`，`OK`；
- changed Coding Change Ready Check：成功。

## 最终独立 re-review

Review Target：PR #123，base `71039ce7c69908ef65b47df6d8c2fe987bfb5d51`，reviewed head `ce3314a1343d1df9149a970c9e771010f5f71697`。

结论：`NO_FINDINGS_WITHIN_SCOPE`，未发现 blocker / important finding。A1 重新核对用户要求和 Maintenance；A2 复核 Repository L1、L2/L3 升级、Source/Runtime 一致性、上下文预算、Stable ID、动态发现、exact-text/hash、Docs Impact 与测试充分性。Review 记录保存在 PR #123 discussion。

## 最终 PR Green

PR #123 Skill Tests #747 / run `33395567637` / job `99499143757`，head `ce3314a1343d1df9149a970c9e771010f5f71697`：

- workflow conclusion：`success`；
- maintained scripts/runtime `py_compile`：通过；
- CLI entrypoint smoke：通过；
- self-contained tests：`281/281`，`OK`；
- changed Coding Change Ready Check：通过。

## 合并与 main fresh CI

PR #123 已于 2026-08-31 合并到 `main`，merge commit：`060e81bec3a04328c3a87d2365e27d56c7fd22b2`。

main push Skill Tests #748 / run `33395835478`：`head_sha=060e81bec3a04328c3a87d2365e27d56c7fd22b2`，`conclusion=success`。这是真实 merge commit 的 main 新鲜 CI，不复用 PR CI 作为 main 证据。

# 文档影响

`targeted`：本次只改变 Agent_Skills canonical Coding 路由/治理语义、Source Mode Core 导航与对应永久测试。根 `README.md`、`USAGE.md`、`runtime/README.md` 的安装方式、最终用户操作、Runtime 产品接口、Release 资产和部署方式没有改变，因此不制造这些人类文档 diff。

# 交付

- 功能分支：`feat/repository-l1-fast-path`
- 功能 PR：#123 `增加仓库 L1 轻量实现与验证路径`
- 最终 reviewed head：`ce3314a1343d1df9149a970c9e771010f5f71697`
- 最终 PR CI：#747 / run `33395567637` / job `99499143757`，成功
- merge commit：`060e81bec3a04328c3a87d2365e27d56c7fd22b2`
- main fresh CI：#748 / run `33395835478`，成功
- 归档分支：`chore/archive-repository-l1-fast-path`
- Release：不涉及；Runtime schema、Installer、Release artifact 与依赖版本均未改变

归档 PR 只移动本 Change 历史，不修改 Skill、Runtime、Workflow、依赖或产品行为。归档 PR 合并后的 main fresh CI 仍按 Maintenance 执行，其结果由 GitHub PR/Actions 历史保存，不再改写本归档记录。