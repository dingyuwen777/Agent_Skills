---
schema: coding-change/v1
id: CHG-20260904-223026-ci-runner-consolidation
title: 合并日常 CI Runner 责任并保持三平台 Runtime 证明
level: L3
status: ready_for_review
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

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | governance/content PR 5→≤2 runner Job | https://github.com/dingyuwen777/Agent_Skills/issues/205 | explicitly_deferred | Workflow 静态结构已收敛为 Core + Runtime Package Gate；最终 Job 数必须由本 PR final-head Actions 实际统计后回填。 |
| R2 | package PR 8→≤4 且三平台真实证明 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | explicitly_deferred | 新 DAG 设计为 Core 内 Linux + 独立 Windows/macOS + Runtime Package Gate；本 PR 修改 Workflow 本身会被 classifier 判为 package，最终由三平台真实 CI 回填。 |
| R3 | 两个 required context 不变且阻塞失败 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | explicitly_deferred | Workflow 中仍保留 exact `Agent Skills Gate` / `Runtime Package Gate` job name；Ruleset 未修改，最终以 final-head check-runs 验证。 |
| R4 | Runtime scope package/content/governance 责任不降 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | satisfied | classifier 继续三档；新统一 `skill-tests.yml` 与已删除旧 Workflow 路径均列为 package，Runtime 非 README 仍为 package，Skill/Reference 仍为 content，并有永久回归。 |
| R5 | Workflow responsibility / Job model 永久回归 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | satisfied | `test_ci_workflow_minimal_sufficiency.py` 锁定永久 Workflow 只剩 Release + unified Skill Tests，并锁定 4 个 `runs-on` Owner 与两个 required context；`test_runtime_package_scope.py` 锁定 scope 与 package 条件。 |
| R6 | Deep Review、merge、main fresh、archive、Closure | https://github.com/dingyuwen777/Agent_Skills/issues/205 | explicitly_deferred | 这些是 final-head CI 之后的 L3/Post-Merge 生命周期动作，按 canonical 顺序执行，不在实现前伪造完成。 |

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
- [x] 合并 Requirement/Skill/scope/Linux package 到 `Agent Skills Gate` Core；Windows/macOS 保持真实平台 Job。
- [x] 删除失去独立 Owner 的 `runtime-package-tests.yml`，并把 `Runtime Package Gate` 汇总责任迁入统一 Workflow。
- [x] 更新 scope 与 Workflow responsibility 永久回归。
- [ ] final-head package-scope CI、Deep Review、Completion Audit。
- [ ] guarded merge、main fresh、独立 archive PR、Issue Closure Audit 与分支清理。

# 完成审计

- [x] upstream_re_read：写入前已重新读取 Issue #205、当前 main、Ruleset、Maintenance、永久 Workflow、scope classifier 与对应回归，未发现目标或门禁漂移。
- [x] change_coverage：R1–R6 全部映射 #205；R4/R5 已由机器实现与回归覆盖，必须依赖 final-head Actions 的 R1/R2/R3 保持显式 deferred。
- [x] reverse_audit：从两个 required context 反查 Core、scope、Linux/Windows/macOS、ready_check 与最终 package gate；没有删除 package evidence，也没有用 Workflow path skip 制造 required Pending/假绿。
- [x] unresolved_cleared：没有 `not_satisfied`；尚需真实 GitHub Actions、Review、merge/main fresh/archive/Closure 的项目均有明确 Owner 与后置阶段，因此只标 `explicitly_deferred`。

# 回滚

全部变化只涉及 Agent_Skills 仓库 CI 控制面。若 required context、scope 或三平台 evidence 异常，恢复本 Change 的 Workflow/classifier/test 提交即可；无 Runtime 用户安装迁移、数据迁移或 Release 回滚。
