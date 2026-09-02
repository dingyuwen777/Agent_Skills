---
schema: coding-change/v1
id: CHG-20260902-work-initialization-gate
title: Skill Mutation canonical 目标与本地开工门禁
level: L2
status: done
owner: dingyuwen777
branch: chore/156-work-initialization-gate
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - skill-mutation
  - git-delivery
affected_paths:
  - AGENTS.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py
  - .agents/skills/coding/tests/test_network_and_workflow_governance.py
contracts: []
data_changes: []
---

# 目标

把 Skill Mutation 的 canonical 写入目标和持久仓库开发的开工顺序固化为可执行门禁：通用 Skill/Reference Mutation 只写 `dingyuwen777/Agent_Skills` 当前 canonical 源码；需要 Git/PR 交付的工作先建立本地任务分支和首个本地提交，再首次 push 创建远程跟踪分支与早期 PR，同时保持 Issue/Change/PR/merge 等外部动作的授权边界。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/156

# 最终结果

- [x] Skill Mutation 的唯一通用写入目标已明确为 `dingyuwen777/Agent_Skills` 当前 canonical 源码仓库。
- [x] 本地 clone/worktree 只作为 canonical checkout，不是第二套 Skill Owner；`$CODEX_HOME/skills`、目标项目安装副本、插件缓存、Runtime/Project Payload、Release、缓存和 Stub 均不得作为替代写入目标。
- [x] canonical 源不可读、不可写或仓库要求的 Change/PR/CI 门禁不可执行时 fail closed，只能报告未同步/未交付。
- [x] Git 交付顺序已固化为“最新目标分支 → 本地任务分支 → 本地 Change/失败测试/最小治理提交 → 首个本地提交 → 首次 push 创建远程跟踪分支 → 早期 PR”，禁止远程空分支先行。
- [x] Issue、Change、PR、merge 等仍由项目制度、风险和授权决定；规则没有把所有 L1/L2 机械升级为完整治理，也没有把任务授权扩大成无限 Git/Release/Deploy 权限。
- [x] 永久回归覆盖 canonical Mutation target、禁止替代目标、本地分支优先顺序和相关路由/上下文边界。
- [x] 实现 PR #157 已合并；实际 merge commit `20e2a72bb33a8242835a02dd06940d43556e6989` 的 `main` fresh Skill Tests 与 Runtime Package Tests 均 success，因此本 Change 已满足 `done` / archive 前置条件。

# 范围

- 强化现有 Root `AGENTS.md`、Coding Core、Git Delivery Reference 与 Skill Mutation Reference，不创建平行 Skill。
- 扩展现有 Skill Mutation 与 Workflow Governance 永久回归。
- 保持 Runtime public protocol、Bundle/MCP、Project Payload/Installer/Release 产品面不变。
- 按 Requirement Source → Change → TDD → Review → PR CI → merge → main fresh → archive 的现行治理链交付。

# 非目标

- 不创建新的 Skill 或第二套 Mutation Owner。
- 不修改目标项目中的 Agent_Skills Runtime/Project Payload 安装副本。
- 不改变 Runtime public protocol、Bundle、MCP、安装器、Release 产物、数据 Schema 或 Migration。
- 不自动授予 commit、push、PR、merge、Release、Deploy、生产写入、force push 或无关分支删除权限。

# 必须保持不变

- Root `AGENTS.md` 继续是外部项目会话中 Skill Mutation 的 canonical Bootstrap Owner。
- Coding/ref15 继续承担 Mutation 详细内容守恒；Git 顺序与安全边界由 ref14 承担。
- Runtime Router / managed block 不暴露维护者专用 canonical Mutation 细节。
- 最小充分治理和 L1 fast path 保持；能力存在不等于每个任务都启用。
- 内容守恒、Review、CI、PR、main fresh 和 Change archive 门禁不得被授权语义削弱。

# 关键决策

- 采用：在既有 Root/Coding/ref14/ref15 Owner 内补 canonical target 与开工顺序，并扩展已有回归。这样不建立新的控制面，也能由现有 Router/Owner 触达。
- 拒绝：新增独立 Skill 承担开工治理；会形成重复 Owner。
- 拒绝：只依赖用户全局指令；它不能成为 Agent_Skills canonical 源码规则，也不能保证其他宿主/会话等价执行。
- 拒绝：把本地安装副本、Runtime Projection、插件缓存或 `$CODEX_HOME/skills` 当 Mutation fallback；canonical 不可用时必须 fail closed。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Skill/Reference Mutation 必须直接修改 canonical Agent_Skills，不得另建本地替代 Skill | https://github.com/dingyuwen777/Agent_Skills/issues/156 | satisfied | 当前 `AGENTS.md` 与 ref15 明确 Mutation Target Resolution、canonical source 与 fail-closed；PR #157 将该规则合入 `main` |
| R2 | 为持久仓库开发建立按风险、项目制度与授权决定的开工治理，不把 Issue/PR 机械强加给所有任务 | https://github.com/dingyuwen777/Agent_Skills/issues/156 | satisfied | Coding 最小充分治理保持 L1/轻量 L2 条件式；ref14 固化需要 Git/PR 时的本地分支优先顺序，未建立平行 Skill |
| R3 | L3/跨 PR/长期治理单元在生产实现前必须建立可追溯施工链 | https://github.com/dingyuwen777/Agent_Skills/issues/156 | satisfied | 当前 Coding/Change/Requirement Traceability 规则继续要求持久 gated 单元建立正式施工契约并向上追溯；PR #157 的 Change 与永久回归验证该路径 |
| R4 | 任务授权不得自动扩大为 commit/push/PR/merge/Release/Deploy 等外部权限 | https://github.com/dingyuwen777/Agent_Skills/issues/156 | satisfied | ref14 明确未经授权不得创建分支、提交、push、PR、merge、deploy；Root/ref15 对 canonical 不可写或门禁不可执行时 fail closed |
| R5 | 更新既有 Coding Owner、补 Change/内容守恒与路由回归、通过实际 Skill Tests | https://github.com/dingyuwen777/Agent_Skills/issues/156 | satisfied | PR #157 只强化既有 Owner 与测试；开发阶段全量 `336 tests` Green，Standard Review/re-review 无剩余 blocker |
| R6 | 实现合并后取得真实 `main` fresh CI，满足 Change 归档前置条件 | https://github.com/dingyuwen777/Agent_Skills/issues/156 | satisfied | PR #157 merge commit `20e2a72bb33a8242835a02dd06940d43556e6989`；main push Skill Tests run `33578652749` success；Runtime Package Tests run `33578652991` success |
| R7 | 归档 PR merge、archive-main fresh 与 Issue #156 Closure Audit/close | https://github.com/dingyuwen777/Agent_Skills/issues/156 | explicitly_deferred | 这些事实必须在本 archive-only 变更进入 PR/merge 后真实产生；由 Issue #156 生命周期继续记录，不能在归档文件创建前伪造 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Skill Mutation 与 Workflow Governance 永久回归；开发阶段全量 Skill Tests `Ran 336 tests` Green |
| 接口 / Contract | not_applicable | 不改变 Runtime public protocol、Bundle/MCP、安装 Contract 或 public API |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改变数据库、持久化或外部运行依赖 |
| 用户 / Workflow Acceptance | required | canonical target、禁止替代写入、本地分支优先与授权边界均由 live canonical 规则和回归覆盖 |
| 跨组件 Golden Path | not_applicable | 不改变业务产品跨组件接线 |
| 外部依赖 / Provider Probe | not_applicable | 不依赖业务第三方 Provider |
| Build / Package / Runtime | not_applicable | 本次为治理/content 变化，不改变 executable/package/platform boundary；Runtime Package Gate 仍取得 success |
| Docs / Governance / Other | required | Change/Requirement Traceability、Ready、Standard Review/re-review、PR CI、implementation-main fresh 均有证据 |

# TDD / Review / CI

## Red → Green

- Red：新增 Mutation 回归时因缺少 `Mutation Target Resolution` 失败；新增 Workflow 回归因缺少本地分支优先语义失败。
- Green：Mutation、Workflow、Coding progressive disclosure、Router migration 回归通过。
- 全量：开发阶段 `PYTHONUTF8=1 python -m unittest discover -s .agents\skills\coding\tests -p test_*.py` → exit 0，`Ran 336 tests in 13.633s`，`OK (skipped=1)`。
- 内容预算测试保持既有阈值；没有删除断言或抬高 context budget 制造 Green。

## Review

- Standard Review：base `af158d9db27e4054d2a0f4968298f66826d02066`、reviewed head `e48e242`；发现 ref14 顺序文本可能成为 Markdown 懒续行后已修复。
- re-review：修复 head `512f376` 后无剩余 Finding；相关 Workflow/Router/全量回归重新 Green。
- Ready：`ready_check.py --root . --require-active-ready` → exit 0，`carrier=.agents/changes，gated=31，strict=31`。

## Git / main fresh

- Requirement Source：Issue #156。
- 实现 PR：#157 `治理：约束Skill canonical目标与本地开工顺序`。
- PR head：`c8b5f92c9840ad1d569c6f2d6a47df8d3cf1342b`。
- merge commit：`20e2a72bb33a8242835a02dd06940d43556e6989`。
- implementation-main Skill Tests：run `33578652749`，`completed / success`。
- implementation-main Runtime Package Tests：run `33578652991`，`completed / success`。
- 原实现分支 `chore/156-work-initialization-gate` 当前已不存在于远程分支搜索结果。

# 完成审计

- [x] upstream_re_read：已重新读取 Issue #156、当前 `main` 的 Root/Maintenance/Entry/Router/Coding/ref14/ref15 与实现 PR #157/main fresh 证据。
- [x] change_coverage：Issue #156 的 canonical target、Work Initialization、本地分支顺序、授权边界、既有 Owner 与永久回归均能在当前 `main` 找到对应实现和直接证据。
- [x] reverse_audit：反查本地替代 Skill、目标项目安装副本、Runtime/缓存 fallback、远程空分支先行和未授权外部动作，当前 canonical 均明确拒绝。
- [x] unresolved_cleared：实现范围没有 `not_satisfied`；只有 archive PR merge/archive-main fresh/Issue close 因真实时序保留 `explicitly_deferred`，由 #156 生命周期在本归档提交后继续完成。

# 文档影响

Docs Impact：`not_applicable`。本次实现只修改 canonical Agent/Skill 治理 Owner 与回归；README/USAGE/Runtime 用户文档没有相反或需要同步的用户契约。

# 交付

- 实现 PR #157 已合并并取得 implementation-main fresh Green。
- 本文件作为独立 archive-only 收尾更新为 `done` 并移动到 `archive/2026-09/CHG-20260902-work-initialization-gate/CHANGE.md`。
- archive PR merge、archive-main fresh、Issue #156 Closure Audit/close 只能在后续真实发生后记录到 Issue 生命周期；在这些动作完成前不把完整端到端收尾伪装为已经完成。
