---
schema: coding-change/v1
id: CHG-20260904-223026-ci-runner-consolidation
title: 合并日常 CI Runner 责任并保持三平台 Runtime 证明
level: L3
status: in_progress
owner: dingyuwen777
branch: infra/205-ci-runner-consolidation
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - runtime-package
  - testing
  - governance
affected_paths:
  - .github/workflows/skill-tests.yml
  - .github/workflows/runtime-package-tests.yml
  - .github/scripts/runtime_package_scope.py
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
  - .agents/skills/coding/tests/test_runtime_package_scope.py
  - .agents/changes/active/CHG-20260904-223026-ci-runner-consolidation/CHANGE.md
contracts:
  - Agent Skills Gate Identity
  - Runtime Package Gate Identity
  - Runtime Three-Platform Evidence
data_changes: []
---

# 目标

Requirement Source：Issue #205。

把当前 `skill-tests.yml` 与 `runtime-package-tests.yml` 中重复的 Ubuntu checkout/setup/scope/gate 责任收敛：普通 governance/content PR 只启动 `Agent Skills Gate` 与 `Runtime Package Gate` 两个 runner Job；package scope 仍真实运行 Linux/Windows/macOS onefile、自测、stdio MCP 与项目安装证明，且总 runner Job 不超过 4。

# 范围 / 非目标

Included：永久 CI Workflow、Runtime package scope classifier 与对应回归、当前 Change 生命周期。

Excluded：Coding/Testing/Review 等 Skill/Reference 语义、Router/Stable ID、Runtime CLI/MCP/install Contract、Bundle/加密 schema、正式 Release/Deploy、依赖或 Python 版本升级。

# 必须保持不变

- `Agent Skills Gate` 与 `Runtime Package Gate` required check identity 保持；
- `package` scope 的 Linux/Windows/macOS 三平台真实 package evidence 全部保留；
- Requirement Source、self-contained tests、ready_check、Source/Runtime conformance 不降低；
- Runtime/installer/build/release/CI package 边界变化继续进入 `package`；Skill 内容变化进入 `content`；纯治理变化可以 `governance`；
- 不修改 Ruleset，不降低 test threshold，不升级依赖/Runtime/Actions。

# Evidence Preservation Mapping

| 原责任 | 新 Owner | 证据变化 |
| --- | --- | --- |
| Requirement Source | `Agent Skills Gate` Core step | 命令保持 |
| Skill Tests / ready_check | `Agent Skills Gate` Core steps | 命令保持 |
| Runtime Package Scope | `Agent Skills Gate` Core output | classifier 唯一 Owner 保持 |
| Runtime Linux Package | `Agent Skills Gate` package 条件 steps | 原 build/self-test/MCP/install 命令保持 |
| Runtime Windows Package | 独立 package 条件 Job | 原命令保持 |
| Runtime macOS Package | 独立 package 条件 Job | 原命令保持 |
| Runtime Package Gate | 最终 always Job | 汇总 Core scope + Windows/macOS；package 时 Core 已包含 Linux 成功 |
| Agent Skills Gate | Core required Job | 不再为纯汇总额外启动 Ubuntu |

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | governance/content PR 5→≤2 runner Job | https://github.com/dingyuwen777/Agent_Skills/issues/205 | in_progress | 待真实 Actions 统计 |
| R2 | package PR 8→≤4 且三平台真实证明 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | in_progress | 待本 package-scope PR Actions |
| R3 | 两个 required context 不变且阻塞失败 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | in_progress | 待 Ruleset + check-runs |
| R4 | Runtime scope package/content/governance 责任不降 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | in_progress | 待 classifier 回归 |
| R5 | Workflow responsibility / Job model 永久回归 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | in_progress | 待测试 |
| R6 | Deep Review、merge、main fresh、archive、Closure | https://github.com/dingyuwen777/Agent_Skills/issues/205 | explicitly_deferred | 实现后按顺序完成 |

# Validation Matrix

| Layer | Required | Planned Evidence |
| --- | --- | --- |
| Unit / Governance | required | self-contained unittest 全量、scope/workflow regression |
| Runtime package Linux | required_when_package | onefile + self-test + MCP + install |
| Runtime package Windows | required_when_package | onefile + self-test + MCP + install |
| Runtime package macOS | required_when_package | onefile + self-test + MCP + install |
| Required checks | required | `Agent Skills Gate` + `Runtime Package Gate` exact check-runs |
| GitHub PR / main | required | final-head、Deep Review、guarded merge、main fresh |

# 实施步骤

- [x] 进入当前 Maintenance Mode 并读取 canonical Source routing/Validation/Delivery 规则。
- [x] 建立并写后重读 Issue #205。
- [x] 恢复 main、Ruleset、永久 Workflow、scope classifier 和 Workflow responsibility regression。
- [x] 完成 Evidence Preservation Mapping。
- [ ] 修改 scope/Workflow 回归并验证 Red/Green。
- [ ] 合并永久 CI Workflow，保留三平台 package evidence。
- [ ] final-head package-scope CI、Deep Review、Completion Audit。
- [ ] guarded merge、main fresh、独立 archive PR、Issue Closure Audit 与分支清理。

# 回滚

全部变化只涉及 Agent_Skills 仓库 CI 控制面。若 required context、scope 或三平台 evidence 异常，恢复本 Change 的 Workflow/classifier/test 提交即可；无 Runtime 用户安装迁移、数据迁移或 Release 回滚。
