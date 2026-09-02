---
schema: coding-change/v1
id: CHG-20260902-164914-actions-history-cleanup
title: 清理已删除临时 workflow 的历史 Actions 运行
level: L3
status: done
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
- 同一收尾 PR 同步归档已完成的 Release identity 修复 Change。

# 非目标

- 不删除 `Release`、`Runtime Package Tests`、`Skill Tests` 的任何 run。
- 不删除当前三个正式 workflow 文件。
- 不改变 required checks、Runtime、Release artifact、协议或依赖。
- 不把 Actions 历史清理能力长期产品化。
- 不触发 tag、GitHub Release 或部署。

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

清理成功后，分支 commit `c7528ccd51e45affb6d1c057b3ed3c88cf3fbda8` 已把 `.github/workflows/skill-tests.yml` 恢复为正式 canonical blob `868362b9a4ebf890390bea22643d3ed60adcde17`，因此临时 `actions: write` 与 cleanup job 没有进入最终 `main`。

# 最终交付证据

- PR #173 在 head `55e71c28c9a2da174c075faaf60f92c6d5a149e4` 上通过 `Requirement Source`、`Skill Tests`、`Agent Skills Gate`、`Runtime Package Scope` 与 `Runtime Package Gate`；最终 diff 仅有两个治理记录文件，Linux/Windows/macOS package jobs 按 governance scope 正确 skipped。
- PR #173 独立 Review 锚定相同 head，结论为 `NO_FINDINGS_WITHIN_SCOPE`，review threads 为 0。
- PR #173 使用带 `expected_head_sha` 的 REST squash merge 合入 `main`，真实 merge commit / main HEAD 为 `1dc52c93fe7ac0f5b4ae86f0482cf175b8632675`。
- 合并后的 main `Skill Tests` run `33612609138`：`Skill Tests`、`Requirement Source`、`Agent Skills Gate` 全部 success。
- 合并后的 main `Runtime Package Tests` run `33612609204`：`Runtime Package Scope`、`Runtime Package Gate` success；由于该 merge 只改变治理记录，Linux/Windows/macOS package jobs 正确 skipped。
- 合并后重新读取 `main/.github/workflows/`，仍精确只有 `release.yml`、`runtime-package-tests.yml`、`skill-tests.yml` 三个正式 workflow。
- Issue #172 已在 PR #173 merge 后关闭，`state=closed`、`state_reason=completed`。
- 原任务分支 `chore/actions-history-cleanup` 在合并后查询为不存在；没有遗留该实现分支。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 只保留当前三个正式 workflow 的历史 runs | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | cleanup job `100185793432` 删除 22 条非 allowlist 已完成 run，并验证清理前正式 run ID 全部保留；最终 `STALE_WORKFLOW_RUNS_AFTER=0` |
| R2 | 不把临时清理逻辑留在 main | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | cleanup 后恢复 `skill-tests.yml` 为 canonical blob；PR #173 最终 changed files 不含 workflow 文件，merge 后 main 重新核对仍只有三个正式 workflow |
| R3 | 清理后全量复扫 stale_count=0 | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | cleanup job 日志明确输出 `STALE_WORKFLOW_RUNS_AFTER=0`，并保存正式 run ID 守恒断言 |
| R4 | 不删除三个正式 workflow 文件和历史 | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | allowlist 固定为当前三个正式 workflow；正式 run ID 守恒断言通过；merge 后 main workflow 目录重新核对仍精确为三个文件 |
| R5 | 完成 PR/merge/main fresh CI/Requirement Source/分支收尾 | user:2026-09-02-彻底完成这次工作 | satisfied | PR #173 merged；main runs `33612609138`/`33612609204` success；Issue #172 completed；原实现分支不存在；本 Change 进入最终归档流程 |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | 用户截图与清理前真实 Actions 历史证明存在已删除 workflow 的 stale surface；cleanup 收集到 22 条非 allowlist run。 |
| 行为 / Unit / Component | required | cleanup 先全量收集再删除；删除后全量复扫并得到 `STALE_WORKFLOW_RUNS_AFTER=0`。 |
| 接口 / Contract | required | GitHub Workflow Runs REST DELETE 在 job `100185793432` 中真实执行成功；token 未输出，日志只显示掩码。 |
| 集成 / Runtime Dependency | required | 在真实 GitHub-hosted PR workflow 中使用仓库 Actions API 完成永久删除。 |
| 用户 / Workflow Acceptance | required | 22 条 stale run 已删除；剩余 run 通过 cleanup 全量复扫的正式 path allowlist。GitHub Web 侧栏即时视觉刷新由平台 UI/cache 决定，不作为 API 删除成功的替代证据。 |
| 跨组件 Golden Path | not_applicable | 不涉及 Runtime/业务组件接线。 |
| 外部依赖 Probe | required | GitHub Actions REST 是本次真实外部依赖；delete + post-delete rescan 均成功。 |
| Build / Package / Runtime | required | 临时 workflow revision Runtime Package Tests run `33610981382` success；PR #173 最终 Runtime Package Gate success；merge 后 main run `33612609204` Runtime Package Gate success，最终治理-only scope 正确 skip 三平台 package jobs。 |
| Docs / Governance / Other | required | Issue #172、L3 Change、cleanup job 日志、PR #173 Review/CI/merge、main fresh CI、Release identity Change archive、当前 workflow 目录复核与本 Change 最终归档。 |

# 任务

- [x] 确认当前 main 真实只有三个正式 workflow 文件。
- [x] 建立 Issue #172 和本 L3 Change。
- [x] 临时修改 Skill Tests，增加仅 PR 使用的 stale-run cleanup job。
- [x] 执行 cleanup 并记录删除数量、路径/名称集合和最终 stale_count。
- [x] 恢复 Skill Tests 原文件，更新本 Change 为 ready_for_review。
- [x] 将已合入且完成 main fresh CI 的 Release identity Change 转为 `done` 并移动到 `archive/2026-09`。
- [x] 完成 PR #173 required checks、独立 Review、guarded merge、main fresh CI、Issue #172 closure 与原实现分支清理。
- [x] 将本 Change 更新为 `done` 并进入 `archive/2026-09` 最终归档交付。

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #172、当前 main、main workflow 目录、cleanup job 日志、PR #173、独立 Review、merge 后 main CI 和当前 Agent_Skills canonical 维护/交付规则；上游目标与最终结果一致。
- [x] change_coverage: 删除集合只包含 22 条非 allowlist 已完成 run；正式 run ID 集合守恒断言通过；PR #173 最终没有 workflow 文件 diff；Release identity Change 已归档；本次最终归档只移动并补全本 Change 的交付证据。
- [x] reverse_audit: cleanup 后非 allowlist run 为 0；main workflow 目录仍精确三个正式文件；PR #173 merged head、真实 main、main fresh CI、Issue closure 和原任务分支状态均已反向核对。
- [x] unresolved_cleared: R1-R5 均有直接 Evidence；没有 `not_satisfied`、未批准延期或需要阻塞本 Change 归档的未验证项。正式 Release/Tag/Deploy 从始至终属于非目标，未被冒充为已执行。
