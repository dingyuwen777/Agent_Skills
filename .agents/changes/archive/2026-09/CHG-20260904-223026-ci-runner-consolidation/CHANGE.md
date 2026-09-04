---
schema: coding-change/v1
id: CHG-20260904-223026-ci-runner-consolidation
title: 合并日常 CI Runner 责任并保持三平台 Runtime 证明
level: L3
status: done
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
  - .agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
  - .agents/skills/coding/tests/test_release_productization.py
  - .agents/skills/coding/tests/test_runtime_gitignore_install_contract.py
  - .agents/skills/coding/tests/test_runtime_package_scope.py
  - .agents/skills/coding/tests/test_runtime_release_hardening.py
  - .agents/skills/coding/tests/test_runtime_sidecarless_state.py
  - .agents/changes/archive/2026-09/CHG-20260904-223026-ci-runner-consolidation/CHANGE.md
contracts:
  - Agent Skills Gate Identity
  - Runtime Package Gate Identity
  - Runtime Three-Platform Evidence
data_changes: []
---

# 目标

Requirement Source：Issue #205。

把原 `skill-tests.yml` 与 `runtime-package-tests.yml` 中重复的 Ubuntu checkout/setup/scope/gate 责任收敛：普通 governance/content PR 只启动 `Agent Skills Gate` 与 `Runtime Package Gate` 两个 runner Job；package scope 真实运行 Linux/Windows/macOS onefile、自测、stdio MCP 与项目安装证明，总 runner Job 不超过 4。

# 范围 / 非目标

Included：永久 CI Workflow、Runtime package scope classifier、对应回归、实现 PR 与当前 Change 生命周期。

Excluded：Coding/Testing/Review 等 Skill/Reference 语义、Router/Stable ID、Runtime CLI/MCP/install Contract、Bundle/加密 schema、正式 Release/Deploy、依赖或 Python 版本升级。

# 必须保持不变

- `Agent Skills Gate` 与 `Runtime Package Gate` required check identity 保持；
- `package` scope 的 Linux/Windows/macOS 三平台真实 package evidence 全部保留；
- Requirement Source、self-contained tests、ready_check、Source/Runtime conformance 不降低；
- Runtime/installer/build/release/CI package 边界变化继续进入 `package`；Skill 内容变化进入 `content`；纯治理变化进入 `governance`；
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
| R1 | governance/content PR 5→≤2 runner Job | https://github.com/dingyuwen777/Agent_Skills/issues/205 | explicitly_deferred | 统一 DAG 的 governance/content 静态结构只有 `Agent Skills Gate` + `Runtime Package Gate`；Issue 明确要求由本独立 governance-only archive PR 的真实 Actions 统计完成最终 Evidence，归档 PR 首轮成功后回填。 |
| R2 | package PR 8→≤4 且三平台真实证明 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | satisfied | PR #206 final-head run `33886346584` 实际 `total_count=4`，Agent Skills Gate、Runtime Windows Package、Runtime macOS Package、Runtime Package Gate 全部 success；Core 内 Linux onefile/self-test/MCP/install success，Windows/macOS 对应真实 runner 的 build/self-test/MCP/install 也 success。merge revision `main@1399fcef44fca6a9fd743c4fbe96e68d6fd803c2` 的 push run `33887326289` 再次 4/4 success。 |
| R3 | 两个 required context 不变且阻塞失败 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | satisfied | active Ruleset `main-quality-gate` 仍精确要求 `Agent Skills Gate` 与 `Runtime Package Gate`；PR #206 final-head 两个 context success。首轮 Red `33885577141` 中 Core self-contained tests 失败后 Windows/macOS 被 skipped 且 Runtime Package Gate failure，直接证明失败不会被假绿吞掉。 |
| R4 | Runtime scope package/content/governance 责任不降 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | satisfied | classifier 继续三档；统一 `skill-tests.yml`、已删除旧 Workflow 路径、Release 与 Runtime package 边界均列为 package；Skill/Reference 仍为 content；永久 scope regression 通过 final-head 436 tests。 |
| R5 | Workflow responsibility / Job model 永久回归 | https://github.com/dingyuwen777/Agent_Skills/issues/205 | satisfied | final-head 436 self-contained tests success；`test_ci_workflow_minimal_sufficiency.py` 锁定永久 Workflow 为 Release + unified Skill Tests 与 4 个 runner Owner，Runtime package / sidecar / gitignore / action pin / Python pin 等旧证明断言已迁入统一 Workflow Owner。 |
| R6 | Deep Review、merge、main fresh、archive、Closure | https://github.com/dingyuwen777/Agent_Skills/issues/205 | explicitly_deferred | implementation Deep Review `5114631619` 为 `NO_FINDINGS_WITHIN_SCOPE`，PR #206 expected-head guarded squash merge 已完成，merge revision `1399fcef...` 的 main-fresh `33887326289` success。当前独立 archive PR、archive-main fresh、Issue Acceptance writeback/Closure 与分支清理仍按 post-merge 顺序执行。 |

# Validation Matrix

| Layer | Required | Evidence |
| --- | --- | --- |
| Unit / Governance | required | PR #206 final-head 436/436 self-contained tests success；Requirement Source、changed Change readiness success。 |
| Runtime package Linux | required_when_package | `33886346584` / `33887326289` Core 内 Linux onefile + self-test + MCP + install success。 |
| Runtime package Windows | required_when_package | `33886346584` / `33887326289` Windows 2025 real package build/self-test/MCP/install success。 |
| Runtime package macOS | required_when_package | `33886346584` / `33887326289` macOS 15 real package build/self-test/MCP/install success。 |
| Required checks | required | final-head `Agent Skills Gate` + `Runtime Package Gate` success；Ruleset unchanged；首轮 Red 证明 fail-safe。 |
| Review | required | L3 Deep Review `5114631619`，exact base `fac6c7a72cfba82275bb31bf4ca11d86aa6f6f00` / head `cd1bd8beabd43969d6185d92def81da7b8df5df8`，结论 `NO_FINDINGS_WITHIN_SCOPE`，review threads 为空。 |
| GitHub PR / main | required | PR #206 guarded squash merge → `1399fcef44fca6a9fd743c4fbe96e68d6fd803c2`；implementation main-fresh run `33887326289` completed/success。 |
| Governance fast path | required | 当前 archive PR 用于取得 governance-only 2-job 直接证据；首轮结果回填 R1 后再 merge。 |

# 实施步骤

- [x] 进入当前 Maintenance Mode 并读取 canonical Source routing/Validation/Delivery/Review 规则。
- [x] 建立并写后重读 Issue #205。
- [x] 恢复 main、Ruleset、永久 Workflow、scope classifier 和 Workflow responsibility regression。
- [x] 完成 Evidence Preservation Mapping。
- [x] 合并 Requirement/Skill/scope/Linux package 到 `Agent Skills Gate` Core；Windows/macOS 保持真实平台 Job。
- [x] 删除失去独立 Owner 的 `runtime-package-tests.yml`，并把 `Runtime Package Gate` 汇总责任迁入统一 Workflow。
- [x] 更新 scope 与 Workflow responsibility 永久回归。
- [x] PR #206 final-head package-scope 4-job CI 全绿并完成 L3 Deep Review。
- [x] expected-head guarded squash merge，implementation main-fresh package-scope 4-job CI 全绿。
- [ ] 当前 governance-only archive PR 实测 2-job fast path并回填 R1。
- [ ] archive PR merge、archive-main fresh、Issue #205 Acceptance writeback/Closure 与可用范围内的分支清理。

# 完成审计

- [x] upstream_re_read：implementation merge 前已重新读取 Issue #205、当前 main、active Ruleset、Maintenance、永久 Workflow、scope classifier 与 Review 规则；目标与门禁未漂移。
- [x] change_coverage：R1–R6 全部映射 #205；R2–R5 已由 final-head/main-fresh 直接机器证据闭合；R1 按 Issue 指定由 governance-only archive PR 实测，R6 只剩 archive/Closure 生命周期。
- [x] reverse_audit：从两个 required context 反查 Core、scope、Linux/Windows/macOS、ready_check 与最终 package gate；首轮 Red 还证明 Core failure 会阻止平台任务并使 Gate failure，没有删减或静默 skip package evidence。
- [x] unresolved_cleared：没有 `not_satisfied`；R1 与 R6 的剩余项是当前 archive/Closure 自引用生命周期，均明确 Owner 与执行顺序，不冒充已完成。

# Red / Green / Review / Merge 证据

- Red `33885577141`：Core Requirement Source/scope/compile 通过，self-contained tests 因旧 Workflow 路径断言 2 fail + 6 error；Windows/macOS 被 fail-safe skipped，Runtime Package Gate failure。失败证明未在 Core 红时继续浪费三平台 runner。
- Green final-head `33886346584`：实际 `total_count=4`，四个 Job 全 success；Agent Skills Gate 内 436 tests 与 Linux package 完整成功；Windows/macOS 真实目标平台完整成功。
- Deep Review `5114631619`：A1/A2、testing adequacy、Ruleset/main freshness 复核，`NO_FINDINGS_WITHIN_SCOPE`，无 unresolved review thread。
- Guarded merge：PR #206 使用 `expected_head_sha=cd1bd8beabd43969d6185d92def81da7b8df5df8` squash merge，merge revision `1399fcef44fca6a9fd743c4fbe96e68d6fd803c2`。
- implementation main-fresh `33887326289`：push event completed/success，`total_count=4`，Linux/Windows/macOS 与 Runtime Package Gate 再次全部 success。

# 回滚

全部变化只涉及 Agent_Skills 仓库 CI 控制面。若 required context、scope 或三平台 evidence 后续异常，可恢复 PR #206 前的 Workflow/classifier/test 状态；无 Runtime 用户安装迁移、数据迁移或 Release 回滚。
