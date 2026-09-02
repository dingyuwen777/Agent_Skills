---
schema: coding-change/v1
id: CHG-20260902-164914-actions-history-cleanup
title: 清理已删除临时 workflow 的历史 Actions 运行
level: L3
status: ready_for_review
owner: dingyuwen777
branch: chore/actions-history-cleanup
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - github-actions
  - repository-governance
affected_paths:
  - .github/workflows/skill-tests.yml
contracts:
  - github-actions-history-cleanup
data_changes: []
---

# 目标

删除已经从 `main` 移除、但仍因历史 workflow runs 出现在 GitHub Actions 左侧栏的临时 workflow 记录；严格保留当前三个正式 workflow 及其全部历史。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/172 。

# 成功标准

- 当前 `main/.github/workflows/` 仍精确只有 `release.yml`、`runtime-package-tests.yml`、`skill-tests.yml`。
- 清理只删除 workflow `path` 不属于上述 allowlist 的已完成 runs。
- 删除前完整枚举 stale run IDs/path/name；删除过程中任一 API 错误 fail closed。
- 删除后重新分页扫描全部 Actions runs，`stale_count == 0`。
- 三个正式 workflow 的历史 run 不删除。
- 临时 cleanup job 在同一 PR 分支完成清理后撤回，最终分支中的 `skill-tests.yml` 与 `main` 当前正式版本逐字一致。

# 范围

- GitHub Actions 历史 workflow run 清理。
- 使用现有 `Skill Tests` 的 PR run 临时执行一次 cleanup，不新增第四个 workflow。
- 清理完成后恢复 `Skill Tests` 原权限和原 jobs。
- 同一收尾 PR同步归档已完成的 Release identity 修复 Change。

# 非目标

- 不删除 `Release`、`Runtime Package Tests`、`Skill Tests` 的任何 run。
- 不删除当前三个正式 workflow 文件。
- 不改变 required checks、Runtime、Release artifact、协议或依赖。
- 不把 Actions 历史清理能力长期产品化。

# 风险与回滚

Workflow run 删除不可恢复，因此采用 fail-closed allowlist：只有 `status=completed` 且 `path` 不在三个正式路径中的 run 才进入删除集合；先收集完整集合后再删除，避免分页删除导致漏项。任何非 2xx/204 响应立即失败并停止。删除完成后只能通过重新扫描确认结果，无法恢复被删除的历史 run。

# 清理执行证据

真实 GitHub-hosted `Skill Tests` run `33610981434` 的 `Cleanup Stale Workflow Runs` job `100185793432` 使用仓库 `GITHUB_TOKEN` 的 `Actions: write` 临时权限执行。job 日志确认：

- `STALE_WORKFLOW_RUNS_COUNT=22`；
- 被清理的历史路径全部位于当前三个正式 workflow allowlist 之外，包括 `temporary-*` / `tmp-*` 系列；
- `STALE_WORKFLOW_RUNS_AFTER=0`；
- `PRESERVED_FORMAL_RUNS=1287`；
- cleanup job conclusion = `success`；
- cleanup 后 Actions runs API `total_count=1287`，与清理前相差精确 22；
- 清理脚本对所有清理前正式 run ID 做集合守恒断言，未发现正式 run 被删除。

清理成功后，分支 commit `c7528ccd51e45affb6d1c057b3ed3c88cf3fbda8` 已把 `.github/workflows/skill-tests.yml` 恢复为当前 `main` 的 canonical blob `868362b9a4ebf890390bea22643d3ed60adcde17`，因此临时 `actions: write` 与 cleanup job 不再存在于最终分支文件。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 只保留当前三个正式 workflow 的历史 runs | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | cleanup job `100185793432` 删除 22 条非 allowlist 已完成 run，并验证清理前正式 run ID 全部保留；最终 `STALE_WORKFLOW_RUNS_AFTER=0` |
| R2 | 不把临时清理逻辑留在 main | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | commit `c7528ccd51e45affb6d1c057b3ed3c88cf3fbda8` 恢复 `skill-tests.yml` 为 main canonical blob `868362b9a4ebf890390bea22643d3ed60adcde17` |
| R3 | 清理后全量复扫 stale_count=0 | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | cleanup job 日志明确输出 `STALE_WORKFLOW_RUNS_AFTER=0`；真实 API 后续 total count 为 1287 |
| R4 | 不删除三个正式 workflow 文件和历史 | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | allowlist 固定为当前 main 三个真实 workflow 路径；正式 run ID 守恒断言通过；main workflow 目录未修改 |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | 用户截图与清理前真实 Actions 历史证明存在已删除 workflow 的 stale surface；cleanup 收集到 22 条非 allowlist run。 |
| 行为 / Unit / Component | required | cleanup 先全量收集再删除；删除后全量复扫并得到 `STALE_WORKFLOW_RUNS_AFTER=0`。 |
| 接口 / Contract | required | GitHub Workflow Runs REST DELETE 在 job `100185793432` 中真实执行成功；token 未输出，日志只显示掩码。 |
| 集成 / Runtime Dependency | required | 在真实 GitHub-hosted PR workflow 中使用仓库 Actions API 完成永久删除。 |
| 用户 / Workflow Acceptance | required | 22 条 stale run 已删除；剩余 run 均通过 cleanup 全量复扫的正式 path allowlist。GitHub Actions Web 侧栏可能需要页面刷新/平台缓存更新后反映 API 状态。 |
| 跨组件 Golden Path | not_applicable | 不涉及 Runtime/业务组件接线。 |
| 外部依赖 Probe | required | GitHub Actions REST 是本次真实外部依赖；delete + post-delete rescan 均成功。 |
| Build / Package / Runtime | required | 临时 workflow revision Runtime Package Tests run `33610981382` success；最终恢复 canonical workflow 后以最终 PR head 的 required Gate 作为交付证据。 |
| Docs / Governance / Other | required | Issue #172、本 Change、cleanup job 日志、Release identity Change done archive、最终 diff 与最终 PR fresh CI。 |

# 任务

- [x] 确认当前 main 真实只有三个正式 workflow 文件。
- [x] 建立 Issue #172 和本 L3 Change。
- [x] 临时修改 Skill Tests，增加仅 PR 使用的 stale-run cleanup job。
- [x] 执行 cleanup 并记录删除数量、路径/名称集合和最终 stale_count。
- [x] 恢复 Skill Tests 原文件，更新本 Change 为 ready_for_review。
- [x] 将已合入且完成 main fresh CI 的 Release identity Change 转为 `done` 并移动到 `archive/2026-09`。
- [ ] 取得最终 PR required checks / Review 证据后等待 Git 交付授权。

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #172、main workflow 目录、cleanup job 日志和清理后的 Actions runs API；当前三个正式 workflow Owner 未变化。
- [x] change_coverage: 删除集合只包含 22 条非 allowlist 已完成 run；正式 run ID 集合守恒断言通过，未扩大到三个正式 workflow；Release identity Change 已按其实际 merge/main 证据归档。
- [x] reverse_audit: cleanup 后从全部剩余 runs 反向筛选非 allowlist path 得到 0；临时 `skill-tests.yml` 已恢复为 main canonical blob；PR 最终实现 diff 不再包含临时清理逻辑。
- [x] unresolved_cleared: R1-R4、实际清理/恢复和 Release Change 归档均已满足；最终 PR CI/Review 与 Git merge 属于后续交付门禁，不冒充为当前已通过。
