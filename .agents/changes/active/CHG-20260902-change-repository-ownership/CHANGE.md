---
schema: coding-change/v1
id: CHG-20260902-change-repository-ownership
title: 明确 Change 仓库归属与跨仓库治理边界
level: L2
status: in_progress
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
  - .agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py
contracts: []
data_changes: []
---

# 目标

把 Change 的 Repository Ownership 固化为可执行、可回归的 canonical 规则：Change 永远属于本次被修改/治理的仓库，而不是提供 Agent_Skills 规则的仓库；一次任务实际修改多个仓库时，各仓库在自己确实达到持久施工契约条件时分别治理，不允许一个 Change 跨仓承载实现范围。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/163

# 成功标准

- [ ] Change 管理 canonical Owner 明确唯一被治理仓库、carrier 与仓库相对影响边界。
- [ ] 外部项目使用 Agent_Skills 时，外部项目 Change 不进入 Agent_Skills carrier。
- [ ] Agent_Skills 自维护时，自身 Change 继续留在 Agent_Skills carrier。
- [ ] 外部项目实现与 Agent_Skills Skill Mutation 同时发生时，各自进入各仓库治理闭环，不共用跨仓 Change。
- [ ] 保持 `coding-change/v1`、Stable Reference ID、Runtime/Bundle/Project Payload/安装协议不变，不新增 `change_repository` frontmatter 字段。
- [ ] 永久回归锁定规则语义并验证现有 `coding.py` carrier 继续由传入 repository root 决定。
- [ ] 目标测试、完整 Skill Tests、Ready Check、独立 Review、PR CI 和 merge 后 `main` fresh CI 均有本轮新鲜证据。

# 范围

- 修改现有 Change 管理 Reference，作为 Change Repository Ownership 唯一详细 Owner。
- 修改现有 Skill Mutation Reference，只补跨仓 Mutation 的 Ownership 边界并引用 Change Owner。
- 扩展现有 Skill Mutation canonical ownership 回归测试。
- 完成 Issue → Change → PR → Review/CI → merge → main fresh → archive → Issue Closure Audit → 分支清理闭环。

# 非目标

- 不新增 Skill 或 Reference。
- 不改变 Coding Change schema、模板必需字段或 carrier 目录结构。
- 不重写 `coding.py` 已正确存在的 repository-root carrier 机制。
- 不修改 Runtime evaluator、MCP、Bundle、Project Payload、Installer、Release 或三平台二进制。
- 不把所有 L2 变成必须创建 Change；是否需要持久施工契约继续由最小充分治理决定。
- 不修改 README / USAGE 等人类用户文档，除非实现事实证明存在真实影响。

# 必须保持不变

- `coding-change/v1` 是当前唯一 Coding Change schema。
- Change carrier 继续由目标 repository root 与项目既有治理决定，不引入全局共享 Change 目录。
- Skill Mutation canonical 写入目标仍是 `dingyuwen777/Agent_Skills`。
- Runtime Mode 不增加维护者专用路径/文件名披露。
- L1 / 普通轻量 L2 的最小充分治理语义保持不变。

# 关键决策

- 方案 A（采用）：在 ref04 中增加 Change Repository Ownership 单一详细 Owner，在 ref15 中只补 Skill Mutation 跨仓边界；用现有回归测试锁定语义。优点是职责单一、上下文最小、与现有 `coding.py --root` 实现一致。
- 方案 B（拒绝）：新增 `change_repository` frontmatter 字段。会把纯语义澄清升级为 schema/工具 Migration，当前没有必要。
- 方案 C（拒绝）：新增独立 Reference 或 Skill。会产生平行 Owner，并扩大 Router/Runtime 分发面。
- 方案 D（拒绝）：只把说明写进本 Change。Change 最终会归档，不是长期 canonical 规则 Owner，无法保证未来任务加载。

## Active Change 协调

当前 `main` 仍有 `CHG-20260902-work-initialization-gate` 留在 active，且其 `affected_paths` 包含 Skill Mutation Reference；其实现 PR #157 已经合并进 `main`。本 Change 明确从包含该实现的最新 `main` 开始，因此不存在两个实现分支同时修改旧版本 ref15；这是“已合并旧 Change 的生命周期尚未归档”与新任务的历史范围重叠。当前任务不修改旧 Change，也不把旧任务证据混入本 Change。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Change 必须归属于唯一被修改/治理仓库，而非 Skill 来源仓库 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | not_satisfied | 待 canonical 规则与回归实现 |
| R2 | carrier 和影响路径必须以该 Change 所属仓库根为边界 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | not_satisfied | 待规则与 `coding.py` root-scoped 回归验证 |
| R3 | 外部项目与 Agent_Skills 自维护的 Change Ownership 必须明确分离 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | not_satisfied | 待 ref04/ref15 实现 |
| R4 | 外部项目实现 + Skill Mutation 的多仓任务必须分别治理，不得用一个 Change 跨仓承载实现 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | not_satisfied | 待 ref15 与回归实现 |
| R5 | 不新增 schema 字段，不改变 Runtime/Bundle/Project Payload/安装协议 | https://github.com/dingyuwen777/Agent_Skills/issues/163 | not_satisfied | 待最终 diff 与完整 Skill Tests 证明 |
| R6 | 完成端到端 Git 交付与 Post-Merge 收尾 | user:current-request | not_satisfied | 待 PR/CI/merge/main fresh/archive/Issue closure/branch cleanup |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | canonical Ownership 回归 + `coding.py` repository-root carrier 行为 |
| 接口 / Contract | not_applicable | 不改变 public API、Change schema、Runtime/MCP protocol |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改变数据库、文件持久化或 Runtime 依赖 |
| 用户 / Workflow Acceptance | required | Source Mode 外部项目 / Agent_Skills 自维护 / 多仓 Mutation 三种治理场景的规则回归 |
| 跨组件 Golden Path | not_applicable | 不改变产品组件接线 |
| 外部依赖 / Provider Probe | not_applicable | 不依赖第三方运行时事实 |
| Build / Package / Runtime | not_applicable | 不改变 Runtime/build/package 产品面；按 content scope 不运行三平台 package matrix |
| Docs / Governance / Other | required | 完整 Skill Tests、Ready Check、内容守恒、独立 Review、PR CI、main fresh CI |

# 完成审计

- [ ] upstream_re_read：Ready 前重新读取 Issue #163、当前 canonical Root/Maintenance/Router/Coding/ref04/ref15。
- [ ] change_coverage：逐项比较 Issue #163 验收与当前 Change，确认无 requirement omission。
- [ ] reverse_audit：反查外部项目、自维护、多仓 Mutation 与现有 `coding.py --root` carrier，确认没有跨仓泄漏。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零，required 验证有新鲜证据，延期/不适用均有依据。

# 任务

- [x] 读取最新 `main` 的 Source Mode canonical 入口、Maintenance、Router、Coding 与命中 References。
- [x] 搜索重复 Requirement Source；确认没有同范围开放 Issue。
- [x] 创建 Issue #163。
- [x] 检查现有 `coding.py` carrier：由传入 repository root 解析，不需要 schema/脚本重写。
- [x] 识别旧 active Change 对 ref15 的历史范围重叠并明确顺序边界。
- [ ] 建立本 Change 与任务分支并创建早期 PR。
- [ ] 先增加失败回归并取得 Red。
- [ ] 最小修改 ref04/ref15 canonical Owner。
- [ ] 运行 targeted + full Skill Tests、Ready Check。
- [ ] 执行独立 Standard Review 与 re-review。
- [ ] 取得当前 PR HEAD CI，guarded merge 到 `main`。
- [ ] 取得 `main` fresh CI，独立归档本 Change。
- [ ] 对 Issue #163 执行 Closure Audit、关闭 Issue并清理当前已合并分支。

# 验证

## 计划

- Red/Green：扩展 `.agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py`。
- Targeted：Skill Mutation canonical ownership 与 Change/governance 相关测试。
- Full：仓库正式 Skill Tests（content scope）。
- Ready：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`（PR 阶段按 changed-since/current Change 语义执行）。
- Review/CI：当前 PR HEAD 独立 Review + GitHub Actions；merge 后读取 `main` fresh workflow 结果。

## 新鲜证据

当前仅有 Source Mode 调查证据；实现、测试、Review、CI、merge 与 Post-Merge 证据尚未产生，不提前声明通过。

# 文档影响

Docs Impact：当前计划为 `not_applicable`（README/USAGE 不描述内部 Change Repository Ownership；canonical Skill/Reference 本身就是本次治理实现）。如果实现中发现人类文档存在相反事实，再升级为 targeted Docs。

# 交付

- Requirement Source：#163
- 分支：`chore/163-change-repository-ownership`
- PR：待创建
- merge：待完成
- main fresh CI：待完成
- Change archive：待完成
- Issue Closure Audit：待完成
