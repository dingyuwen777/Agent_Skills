---
schema: coding-change/v1
id: CHG-20260902-change-repository-ownership
title: 明确 Change 仓库归属与跨仓库治理边界
level: L2
status: ready_for_review
owner: dingyuwen777
branch: chore/163-change-repository-ownership
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - change-ownership
  - skill-mutation
affected_paths:
  - .agents/skills/coding/references/04_轻量变更管理.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/24_Change仓库归属与Carrier.md
  - .agents/skills/coding/tests/test_change_repository_ownership.py
contracts: []
data_changes: []
---

# 目标

把 Change 的 Repository Ownership 固化为可执行、可回归的 canonical 规则：Change 永远属于本次被修改/治理的仓库，而不是提供 Agent_Skills 规则的仓库；一次任务实际修改多个仓库时，各仓库在自己确实达到持久施工契约条件时分别治理，不允许一个 Change 跨仓承载实现范围。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/163

# 成功标准

- [x] canonical 规则明确唯一被治理仓库、carrier 与仓库相对影响边界。
- [x] 外部项目使用 Agent_Skills 时，外部项目 Change 不进入 Agent_Skills carrier；Agent_Skills 自维护时仍使用自身 carrier。
- [x] 外部项目实现与 Agent_Skills Skill Mutation 同时发生时，各自进入各仓库治理闭环，不共用跨仓 Change。
- [x] 保持 `coding-change/v1`、既有 Stable Reference ID、Runtime/Bundle/Project Payload/安装协议不变，不新增 `change_repository` frontmatter 字段。
- [x] 永久回归锁定 Ownership、现有 `coding.py --root` carrier 与渐进披露语义，且不放宽既有上下文预算。
- [x] 独立 Standard Review 对当前语义实现无 blocker；进入 Ready 前完整 Skill Tests 与 Runtime Package scope 证据已取得。

# 范围

- ref04 继续负责“何时需要 Change”、Traceability、Validation、Completion、状态和归档，并保留 detailed Owner 的硬入口。
- 新增窄触发 Reference，作为 Repository Ownership、carrier、ID 与元数据的唯一详细 Owner；只在 L3 或真实持久 Change 治理事实出现时加载。
- ref15 只补 Skill Mutation 跨仓 Ownership 边界并引用详细 Owner，不复制第二套 carrier/schema 规则。
- 新增永久回归，覆盖外部项目、Agent_Skills 自维护、多仓 Mutation、repository-root carrier、schema 不变和渐进披露。
- 完成 Issue → Change → PR → Review/CI → merge → main fresh → archive → Issue Closure Audit → 分支清理闭环。

# 非目标

- 不新增 Skill，也不建立平行的第二套 Change Ownership Reference。
- 不改变 Coding Change schema、模板必需字段或 carrier 目录结构。
- 不重写 `coding.py` 已正确存在的 repository-root carrier 机制。
- 不修改 Runtime evaluator、MCP、Bundle、Project Payload、Installer、Release 或三平台二进制。
- 不把所有 L2 变成必须创建 Change；是否需要持久施工契约继续由最小充分治理决定。
- 不修改 README / USAGE 等人类用户文档；当前调查没有发现其中存在需要同步的 Change Ownership 用户契约。

# 必须保持不变

- `coding-change/v1` 是当前唯一 Coding Change schema。
- Change carrier 继续由目标 repository root 与项目既有治理决定，不引入全局共享 Change 目录。
- Skill Mutation canonical 写入目标仍是 `dingyuwen777/Agent_Skills`。
- Runtime Mode 不增加维护者专用路径/文件名披露。
- L1 / 普通轻量 L2 的最小充分治理语义保持不变。
- 既有路由上下文预算不通过提高阈值或弱化回归来制造 Green。

# 关键决策

- 方案 A（最终采用）：ref04 保留 Change 生命周期与硬入口，把 Repository Ownership / Carrier 机械细节拆到一个窄触发、唯一详细 Owner；ref15 只引用并补 Mutation 专属跨仓边界。优点是职责单一、真实持久治理可达，同时普通 Review/Git/轻量 L2 不预付目录/schema 上下文。
- 初始方案（已由验证否决）：直接把详细 Ownership 全部补进 ref04。新增语义本身通过，但完整路由回归出现 4 个既有 context-budget failure；继续该方案只能扩大不必要上下文或提高预算阈值，因此按事实重规划。
- 方案 B（拒绝）：新增 `change_repository` frontmatter 字段。会把语义澄清升级为 schema/工具 Migration，当前没有必要。
- 方案 C（拒绝）：新增 Skill 或第二套平行 Ownership Reference。会产生重复 Owner 并扩大控制面。
- 方案 D（拒绝）：只把说明写进本 Change。Change 最终会归档，不是长期 canonical 规则 Owner，无法保证未来任务加载。

## Active Change 协调

任务开始时 `main` 仍有 `CHG-20260902-work-initialization-gate` 留在 active，且其 `affected_paths` 包含 Skill Mutation Reference；其实现 PR #157 已经合并进 `main`。本 Change 从包含该实现的最新 `main` 开始，因此不是两个实现分支同时修改旧版本 ref15，而是“已合并旧 Change 生命周期尚未归档”与新任务的历史范围重叠。当前任务没有修改旧 Change，也没有把旧任务证据混入本 Change。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Change 必须归属于唯一被修改/治理仓库，而非 Skill 来源仓库 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | ref24 `Change Repository Ownership` 明确“谁被修改/治理”与唯一被治理仓库；新增回归 `test_detailed_reference_owns_repository_scoped_change_semantics` 通过 |
| R2 | carrier 和仓库相对影响边界必须以该 Change 所属 repository root 为边界 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | ref24 明确 carrier/affected_paths/contracts/data_changes/Evidence 相对仓库根；`test_change_root_is_scoped_to_explicit_repository_root` 使用真实 `coding.py.resolve_change_root` 验证两个 repo root 隔离 |
| R3 | 外部项目与 Agent_Skills 自维护的 Change Ownership 必须明确分离 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | ref24 明确外部项目不得写 Agent_Skills carrier，自维护才使用 Agent_Skills carrier；Ownership 回归通过 |
| R4 | 外部项目实现 + Skill Mutation 的多仓任务必须分别治理，不得用一个 Change 跨仓承载实现 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | ref24 多仓规则 + ref15 `Skill Mutation 与外部项目 Change Ownership`；`test_multi_repository_task_uses_separate_governance_units` 通过 |
| R5 | 不改变 Change schema、既有 Stable ID、Runtime/Bundle/Project Payload/安装协议；详细 Owner 必须渐进披露 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | `test_change_schema_does_not_gain_repository_field`、metadata/bundle/projection/full suite 通过；`test_detailed_owner_loads_only_for_persistent_change_facts` 证明 L3/持久治理加载而 Review/Git 不加载；既有 context-budget 回归最终通过 |
| R6 | merge 后取得 main fresh CI，并完成 Change archive、Closure Audit、Issue close 和分支清理 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | explicitly_deferred | Issue #163 明确该阶段只能在实现 PR merge 后执行；当前仍处于 pre-merge，按端到端交付顺序保留为 Post-Merge 必做项，merge 后必须改为 satisfied 才能归档 done |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新增 6 个 Change Repository Ownership/渐进披露回归；最新完整 self-contained tests 全绿 |
| 接口 / Contract | not_applicable | 不改变 public API、Change schema、Runtime/MCP protocol；schema/metadata/bundle 回归证明边界保持 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改变数据库、文件持久化或 Runtime 依赖 |
| 用户 / Workflow Acceptance | required | 外部项目 / Agent_Skills 自维护 / 多仓 Mutation 三种治理场景由 canonical 文本 + routing regressions 直接覆盖 |
| 跨组件 Golden Path | not_applicable | 不改变产品组件接线 |
| 外部依赖 / Provider Probe | not_applicable | 不依赖第三方运行时事实 |
| Build / Package / Runtime | not_applicable | Runtime Package Scope/Gate success；Linux/Windows/macOS package jobs 按 content scope 全部 skipped，未把治理文本误升为 package 变更 |
| Docs / Governance / Other | required | Requirement Source success；完整 Skill Tests 353/353 通过；Standard Review 无 blocker；当前 Ready HEAD CI 将作为 merge gate 新鲜重跑 |

# 完成审计

- [x] upstream_re_read：重新读取 Issue #163 并按真实 context-budget 证据同步 Requirement Source；重新核对受影响 ref04/ref15/ref24、当前 PR diff 与现有 `coding.py` carrier 行为。
- [x] change_coverage：Issue #163 的 Ownership、外部/自维护、多仓、schema/Runtime 不变、渐进披露和交付阶段均已映射到当前 Change；没有把 Post-Merge 阶段伪装成 pre-merge 已完成。
- [x] reverse_audit：从外部项目、自维护、多仓 Mutation、Review/Git 轻量路由和 `coding.py --root` 反查；详细 Owner 只在 L3/真实持久治理加载，未发现跨仓 carrier 泄漏或轻量路由重新膨胀。
- [x] unresolved_cleared：R1–R5 已由当前实现与新鲜自动化证据满足；R6 依据上游明确的 merge 后顺序标记 `explicitly_deferred`，不存在无依据的 `not_satisfied`。

# 任务

- [x] 读取最新 `main` 的 Source Mode canonical 入口、Maintenance、Router、Coding 与命中 References。
- [x] 搜索重复 Requirement Source；确认没有同范围开放 Issue。
- [x] 创建并在验证重规划后同步 Issue #163。
- [x] 检查现有 `coding.py` carrier：由传入 repository root 解析，不需要 schema/脚本重写。
- [x] 识别旧 active Change 对 ref15 的历史范围重叠并明确顺序边界。
- [x] 建立本 Change、分支 `chore/163-change-repository-ownership` 与早期 PR #164。
- [x] 先增加失败回归并取得 Red。
- [x] 初始 Green 发现 context-budget 根因后重规划为窄 Reference 渐进披露；未提高预算阈值。
- [x] 完成 ref04/ref15/ref24 canonical Owner 与永久回归。
- [x] 运行完整 Skill Tests；语义实现 HEAD `67b5d53982a0a517b4bf6759078016c3ee460c86` 的 self-contained tests 为 353/353 通过。
- [x] Runtime Package Scope/Gate 通过；三平台 package jobs 按 content scope skipped。
- [x] Standard Review：base `d6bd9361d9f786907d86c66255e2415532b21b0c`、reviewed head `f28ec7ddae7af369bcf8c20bb3909523dd973cee`；A1/A2 无 blocker，PR review #5085595149。
- [ ] 对本 Ready 状态提交执行 current-head re-review，并取得全部 required PR CI Green。
- [ ] guarded merge 到 `main`。
- [ ] 取得 `main` fresh CI，独立归档本 Change。
- [ ] 对 Issue #163 执行 Closure Audit、关闭 Issue并清理当前已合并分支。

# 验证

## Red → Green 证据

- Red commit `316e03dffc2e01989599e214017ce1ef8c86de24`：只新增 Ownership 回归；Skill Tests run `33589999080` 的 self-contained tests 失败，compile/smoke/Requirement Source 正常，证明缺口来自 canonical 语义而不是环境。
- 初始规则 Green attempt：新增 Ownership 测试本身通过，但 run `33590281806` 暴露 4 个历史 context-budget failure（Review-only、Git Delivery、Skill Mutation、Figma review）；按规则禁止提高预算阈值，转为渐进披露设计。
- 拆分窄详细 Owner 后，第二轮只剩 L3 public API 比既有预算多 766 bytes；继续消除等价重复，而不是弱化测试。
- 语义实现 HEAD `67b5d53982a0a517b4bf6759078016c3ee460c86`，Skill Tests run `33590986588`：
  - `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v` → `Ran 353 tests in 5.551s`，`OK`；
  - 新增 6 个 `test_change_repository_ownership` 测试全部通过；
  - `test_legacy_routes_preserve_safety_except_explicit_progressive_disclosure_changes`、Reference 连号、metadata、Bundle、Project Payload、Runtime disclosure 等既有守恒回归全部通过；
  - 当时 Changed Coding Change Ready 唯一失败原因为本 Change 仍是 `in_progress`，不是实现/测试失败。
- Runtime Package Tests run `33590986661`：Scope success、Gate success；Linux/Windows/macOS package jobs 均 skipped，符合 content scope。
- Standard Review：reviewed head `f28ec7ddae7af369bcf8c20bb3909523dd973cee`，A1 Requirement Review 与 A2 Code/Rule Quality Review 均无 blocker；下一提交只改变 Change 的 Ready 状态/证据，仍需 re-review current head。

## 当前剩余验证

- 本提交把 Change 提升为 `ready_for_review`；必须等待其 current-head Skill Tests / Ready Check 与 Runtime Package Gate 新鲜完成。
- 对该 Ready HEAD 执行 re-review，确认从 reviewed head 到 merge head 只存在预期 Change 状态/证据变化或重新审查任何新增差异。
- merge 后必须取得 `main` fresh CI；该证据当前不可能提前产生。

# 文档影响

Docs Impact：`not_applicable`。README / USAGE 面向维护者入口或最终用户，不描述内部 Change Repository Ownership/Carrier；本次 canonical Reference 本身就是治理实现。当前 diff 未发现相反的人类用户契约，因此不新增 README/USAGE 文本。

# 兼容、依赖、迁移、部署与回滚

- public API / ABI：无变化。
- `coding-change/v1` schema / 必需字段：无变化；不新增 `change_repository`。
- 既有 Stable Reference ID：无变化；新增窄 Reference 使用独立 Stable ID `coding.reference.25`，由动态发现/metadata compiler 承载。
- Runtime / MCP / Bundle / Project Payload / Installer / Release：无协议或实现变化。
- 依赖 / Python / Runtime 版本：无变化。
- 数据 / Schema / Migration / 部署：不适用。
- 回滚：撤销本次 ref04/ref15/ref24 与回归测试提交即可；无数据或 Runtime 迁移需要反向操作。

# 交付

- Requirement Source：Issue #163（open，已按验证重规划同步）
- 分支：`chore/163-change-repository-ownership`
- PR：#164 `治理：明确 Change 仓库归属与跨仓库边界`
- 当前语义实现 HEAD：`67b5d53982a0a517b4bf6759078016c3ee460c86`
- Standard Review：#5085595149（reviewed head `f28ec7ddae7af369bcf8c20bb3909523dd973cee`）
- merge：待完成
- main fresh CI：待完成
- Change archive：待完成
- Issue Closure Audit：待完成
