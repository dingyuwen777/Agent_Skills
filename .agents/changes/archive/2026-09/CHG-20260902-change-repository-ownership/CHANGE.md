---
schema: coding-change/v1
id: CHG-20260902-change-repository-ownership
title: 明确 Change 仓库归属与跨仓库治理边界
level: L2
status: done
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

把 Change 的 Repository Ownership 固化为可执行、可回归的 canonical 规则：Change 属于本次被修改/治理的仓库，而不是提供 Agent_Skills 规则的仓库；一次任务实际修改多个仓库时，各仓库只在自己确实达到持久施工契约条件时分别治理，不允许一个 Change 跨仓承载实现范围。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/163

# 最终结果

- [x] Change Repository Ownership 已明确由“谁被修改 / 谁被治理”决定，而不是由“规则从哪里加载”决定。
- [x] 使用 Agent_Skills 开发外部项目时，Agent_Skills 只是治理规则来源；外部项目的持久 Change 留在外部项目自己的正式治理载体 / carrier。
- [x] 维护 Agent_Skills 自身时，Agent_Skills 自身变更继续由 Agent_Skills 自己的 Change carrier 承载。
- [x] 一次任务实际修改多个仓库时，每个仓库独立判断是否需要持久施工契约；只读、调查或事实来源仓库不自动建 Change。
- [x] 多仓实际写入且各自达到持久治理条件时，各仓库分别治理，可用 Issue / PR / Change ID 关联，但单个 Change 不得拥有另一仓库的路径、Contract、数据、Evidence 或交付状态。
- [x] Skill Mutation 场景已明确：外部项目 Change 不承担 Agent_Skills canonical Skill Mutation；Agent_Skills Change 也不承担外部项目业务实现。
- [x] `coding-change/v1`、既有 Stable Reference ID、Runtime/MCP/Bundle/Project Payload/Installer/Release 协议保持不变；未新增 `change_repository` frontmatter 字段。
- [x] 详细 Repository Ownership / Carrier 规则按渐进披露拆到唯一窄 Owner，只在 L3 或真实持久治理事实命中时加载；普通 Review/Git/轻量 L2 不预付 carrier/schema 上下文。
- [x] 实现 PR #164 已 guarded merge 到 `main`；实际 merge commit `98edb9596dc8bb65cadec0b023ce86f87e622832` 的 main fresh Skill Tests 与 Runtime Package Tests 均 success，因此本 Change 满足 `done` 与 archive 前置条件。

# 范围

- 保持 ref04 负责“何时需要 Change”、Requirement Traceability、Validation Matrix、Completion Audit、状态和归档，并增加到详细 Owner 的硬入口。
- 新增窄触发 Reference `24_Change仓库归属与Carrier.md`，作为 Repository Ownership、carrier、ID 与元数据的唯一详细 Owner。
- ref15 只补 Skill Mutation 专属跨仓 Ownership 边界并引用详细 Owner，不复制第二套 carrier/schema 规则。
- 新增永久回归，覆盖外部项目、Agent_Skills 自维护、多仓 Mutation、真实 `coding.py --root` carrier、schema 不变与渐进披露正反路由。
- 按现行端到端交付流程完成 Requirement Source、Change、TDD、Review、PR CI、guarded merge 与 implementation-main fresh 验证。

# 非目标

- 不新增 Skill，也不建立平行的第二套 Change Ownership Owner。
- 不改变 `coding-change/v1` schema、模板必需字段或 carrier 目录结构。
- 不重写 `coding.py` 已正确存在的 repository-root carrier 机制。
- 不修改 Runtime evaluator、MCP、Bundle、Project Payload、Installer、Release 或三平台二进制。
- 不把所有 L2 变成必须创建 Change；是否需要持久施工契约继续由最小充分治理决定。
- 不修改 README / USAGE；当前调查没有发现这些人类文档存在相反的 Change Ownership 用户契约。

# 必须保持不变

- Change carrier 继续由被治理 repository root 与项目既有治理决定，不引入全局共享 Change 目录。
- Skill Mutation canonical 写入目标仍是 `dingyuwen777/Agent_Skills`。
- Runtime Mode 不增加维护者专用路径/文件名披露。
- L1 / 普通轻量 L2 的最小充分治理语义保持不变。
- 既有上下文预算不通过提高阈值或弱化测试制造 Green。
- Release、Deploy、生产数据/生产 Migration、force push 与无关破坏性动作没有获得新增授权。

# 关键决策

- 采用：ref04 保留 Change 生命周期和 hard handoff，把 Repository Ownership / Carrier / ID / metadata 细节放入窄触发唯一 Owner；这样真实持久治理完整可达，同时普通 Review/Git/轻量 L2 不预付目录/schema 上下文。
- 验证否决：最初直接把完整 Ownership 细节补进 ref04。新增语义测试通过，但完整路由回归出现 4 个 context-budget failure；按仓库规则没有提高预算阈值，而是改为渐进披露。
- 拒绝：新增 `change_repository` frontmatter。会把语义澄清扩大为 schema/工具 Migration，当前没有必要。
- 拒绝：新增 Skill 或第二套平行 Ownership Reference。会制造重复 Owner 并扩大控制面。
- 拒绝：只把长期规则写进本 Change。Change 最终归档，不是未来任务的 canonical 规则来源。

## 历史 Active Change 协调

任务开始时 `main` 仍有 `CHG-20260902-work-initialization-gate` 留在 active，且其历史 `affected_paths` 包含 Skill Mutation Reference；其实现 PR #157 已在本任务开始前合并进 `main`。本 Change 基于包含该实现的最新 `main` 开始，因此没有两个实现分支同时修改旧版本 ref15；这是旧 Change 生命周期未归档与新任务的历史范围重叠。本任务没有修改旧 Change，也没有混入其交付证据。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Change 必须归属于唯一被修改/治理仓库，而非 Skill 来源仓库 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | `24_Change仓库归属与Carrier.md` 的 `Change Repository Ownership`；`test_detailed_reference_owns_repository_scoped_change_semantics` Green |
| R2 | carrier 与仓库相对影响边界以该 Change 所属 repository root 为边界 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | ref24 明确 carrier/affected_paths/contracts/data_changes/Evidence 相对仓库根；`test_change_root_is_scoped_to_explicit_repository_root` 直接调用真实 `coding.py.resolve_change_root` 验证两个 repo root 隔离 |
| R3 | 外部项目与 Agent_Skills 自维护 Change Ownership 分离 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | ref24 明确外部项目不得写 Agent_Skills carrier，自维护才使用 Agent_Skills carrier；Ownership 回归 Green |
| R4 | 外部项目实现 + Agent_Skills Skill Mutation 的多仓任务分别治理 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | ref24 多仓规则 + ref15 `Skill Mutation 与外部项目 Change Ownership`；`test_multi_repository_task_uses_separate_governance_units` Green |
| R5 | 不改变 Change schema、既有 Stable ID、Runtime/Bundle/Project Payload/安装协议，并保持渐进披露 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | `test_change_schema_does_not_gain_repository_field`、metadata/bundle/projection/full suite Green；`test_detailed_owner_loads_only_for_persistent_change_facts` 证明 L3/持久治理加载而 Review/Git 不加载；既有 context-budget 回归最终 Green |
| R6 | 实现 PR merge 后取得真实 `main` fresh CI，满足 Change `done` / archive 前置条件 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | satisfied | PR #164 guarded merge → `98edb9596dc8bb65cadec0b023ce86f87e622832`；main push Skill Tests run `33591476787` completed/success；Runtime Package Tests run `33591476793` completed/success |
| R7 | 归档 PR merge、archive-main fresh、Issue Closure Audit/close 与本任务分支清理 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | explicitly_deferred | 这些事实只能在本归档提交进入 PR/merge 后真实产生；按现行 Post-Merge Finalization 模式由 Issue 生命周期继续承接，不能在 archive 文件创建前伪造。完成前不得报告整个端到端任务完成 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新增 6 个 Change Repository Ownership / 渐进披露回归；最终完整 self-contained suite 353/353 Green |
| 接口 / Contract | not_applicable | 不改变 public API、Change schema、Runtime/MCP protocol；schema/metadata/bundle 回归证明边界保持 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改变数据库、持久化或 Runtime 依赖 |
| 用户 / Workflow Acceptance | required | 外部项目 / Agent_Skills 自维护 / 多仓 Mutation 三种场景由 canonical 规则与 routing regressions 覆盖 |
| 跨组件 Golden Path | not_applicable | 不改变产品组件接线 |
| 外部依赖 / Provider Probe | not_applicable | 不依赖业务第三方服务 |
| Build / Package / Runtime | content fast path | Runtime Package Gate 在 PR Ready 与 implementation-main fresh 均 success；三平台 binary package jobs按 content scope skipped |
| Docs / Governance / Other | required | Requirement Source、Changed Change Ready、Agent Skills Gate、Standard Review/current-head re-review、implementation-main fresh 均取得新鲜证据 |

# TDD / 渐进披露证据

## Red

- test-only commit：`316e03dffc2e01989599e214017ce1ef8c86de24`。
- PR Skill Tests run `33589999080`：新增 Ownership 回归触发 self-contained tests 失败；compile、CLI smoke 与 Requirement Source 正常，证明缺口在 canonical 语义而非环境。

## 初始 Green 与根因

- 初始规则补充后，新 Ownership 断言本身通过，但 Skill Tests run `33590281806` 暴露 4 个历史 context-budget failure：Review-only、Git Delivery、Skill Mutation、Figma review。
- 根因：完整 carrier/Ownership 细节直接进入 ref04，使没有真实 Change 操作的路由也加载额外上下文。
- 没有提高预算阈值、删除测试或抽象掉边界；改为窄触发详细 Owner。
- 第一次拆分后只剩 L3 public API 比既有预算多 766 bytes；继续删除等价重复，未降低触发、例外、失败、schema 或跨仓边界。

## 最终 Green

- 语义实现稳定 HEAD：`67b5d53982a0a517b4bf6759078016c3ee460c86`。
- PR Skill Tests run `33590986588`：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v` → `Ran 353 tests in 5.551s`，`OK`。
- 6 个 `test_change_repository_ownership` 测试全部 Green。
- 既有 Reference 编号、metadata compiler、Bundle、Project Payload、Runtime disclosure、Routing Conformance 与 context-budget 回归全部 Green。
- Runtime Package Tests run `33590986661`：Scope/Gate success；Linux/Windows/macOS package jobs按 content scope skipped。

# Review

## A1 Requirement Review

重新读取 Issue #163，并按 R1–R7 反查最终实现与真实交付状态。R1–R6 已有 canonical / 自动化 / merge / main-fresh 直接 Evidence；R7 属于本 archive commit 之后的真实时序，只能由 Issue lifecycle 继续记录，不能提前 completed。

## A2 Implementation / Content Preservation Review

- ref04 只保留 Change 生命周期与 hard handoff；ref24 是 Repository Ownership/Carrier/ID/metadata 唯一详细 Owner；ref15 只保留 Skill Mutation 专属跨仓边界。
- `coding.reference.25` 只在 L3 或真实持久治理事实加载；普通 Review-only / Git Delivery 不加载。
- `coding-change/v1`、既有 Stable ID、Runtime/MCP/Bundle/Project Payload/Installer 协议未改变。
- 多仓只读/调查不会自动建 Change；实际修改多个仓库时也只有各自确实达到持久契约条件才分别治理。
- 未发现 secrets、依赖升级、无关重构、用户工作覆盖或 README/USAGE 事实漂移。
- Standard Review：base `d6bd9361d9f786907d86c66255e2415532b21b0c`，reviewed head `f28ec7ddae7af369bcf8c20bb3909523dd973cee`，PR review #5085595149，A1/A2 无 blocker。
- Current-head re-review：reviewed head `1b2ec87273ec2b23b7d526fe4ffa0e34a112b020`，PR review #5085600674，无新增 Finding。

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取 Issue #163，并按 context-budget 根因同步 Requirement Source；merge 后重新读取实际 `main` merge commit 与 push workflows。
- [x] change_coverage：R1–R6 均有直接 canonical / 自动化 / Git / CI Evidence；R7 明确由 post-archive Issue lifecycle 承接，没有把未来动作伪造成已完成。
- [x] reverse_audit：外部项目、自维护、多仓 Mutation、Review/Git 轻量路由和 `coding.py --root` 均完成反向检查；未发现跨仓 carrier 泄漏或轻量路由膨胀。
- [x] unresolved_cleared：无 `not_satisfied`；实现、Review、PR Ready、guarded merge 与 implementation-main fresh 均完成。本 Change 满足 `done` 并移动 archive；剩余 post-archive 尾部事实按上游批准顺序显式 `explicitly_deferred`，由 Issue lifecycle 继续完成。

# Git / CI / 交付证据

- Requirement Source：Issue #163。
- 实现分支：`chore/163-change-repository-ownership`。
- 实现 PR：#164 `治理：明确 Change 仓库归属与跨仓库边界`。
- Ready head：`1b2ec87273ec2b23b7d526fe4ffa0e34a112b020`。
- PR Ready Skill Tests run `33591361533`：success。
- PR Ready Runtime Package Tests run `33591361578`：success。
- merge 方法：普通 merge commit，使用 `expected_head_sha=1b2ec87273ec2b23b7d526fe4ffa0e34a112b020` guard。
- 实现 merge commit：`98edb9596dc8bb65cadec0b023ce86f87e622832`，已确认是实际 `main` HEAD。
- implementation-main fresh Skill Tests run `33591476787`：event=push，head_sha=`98edb9596dc8bb65cadec0b023ce86f87e622832`，completed/success；self-contained tests、Verify active Coding Change、Agent Skills Gate 均 success。
- implementation-main fresh Runtime Package Tests run `33591476793`：event=push，同一 merge commit，completed/success。
- 归档动作：独立 archive-only PR，在本文件进入 archive 后继续记录到 Issue #163；其 merge/main-fresh 不能写成当前已发生事实。

# 文档影响

Docs Impact：`not_applicable`。README / USAGE 不描述内部 Change Repository Ownership/Carrier；canonical Reference 本身即本次治理实现。未发现人类用户文档存在相反事实。

# 兼容、依赖、迁移、部署与回滚

- public API / ABI：无变化。
- `coding-change/v1` schema / 必需字段：无变化；没有 `change_repository`。
- 既有 Stable Reference ID：无变化；新窄 Reference 使用唯一 ID `coding.reference.25`，由动态 discovery/metadata compiler 承载。
- Runtime / MCP / Bundle / Project Payload / Installer / Release：无协议或实现变化。
- 依赖 / Python / Runtime 版本：无变化。
- 数据 / Schema / Migration / 部署：不适用。
- 回滚：撤销实现 merge 中的 ref04/ref15/ref24 与回归测试即可；无数据或 Runtime migration 需要反向操作。归档记录本身保留历史，不通过改写 archive 隐藏已发生过程。

# Post-Archive Handoff

本 Change 到此满足 `done` 并进入 `archive/2026-09/`。以下动作属于归档提交之后的真实 Issue 生命周期，必须继续执行且必须以新鲜事实记录到 Issue #163：

1. 归档 PR required CI Green 后 guarded merge；
2. 对 archive merge commit 取得 `main` fresh Skill Tests + Runtime Package Tests；
3. 对 Issue #163 重新逐项执行 Closure Audit，确认验收标准全部有直接 Evidence；
4. Closure Audit 无 unresolved 后，以 `completed` 关闭 Issue #163；
5. 清理本仓本任务已 merged 且不再需要的实现分支与归档分支；
6. 最后确认 active Change 已不存在、archive 文件可读、Issue closed、任务分支不存在；任一步未完成前不得报告整个端到端任务完成。
