---
schema: coding-change/v1
id: CHG-20260902-164914-actions-history-cleanup
title: 清理已删除临时 workflow 的历史 Actions 运行
level: L3
status: in_progress
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
- 临时 cleanup job 在同一 PR 分支完成清理后撤回，最终合入 `main` 的 `skill-tests.yml` 与清理前正式版本无差异。

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

# 风险与回滚

Workflow run 删除不可恢复，因此采用 fail-closed allowlist：只有 `status=completed` 且 `path` 不在三个正式路径中的 run 才进入删除集合；先收集完整集合后再删除，避免分页删除导致漏项。任何非 2xx/204 响应立即失败并停止。删除完成后只能通过重新扫描确认结果，无法恢复被删除的历史 run。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 只保留当前三个正式 workflow 的历史 runs | https://github.com/dingyuwen777/Agent_Skills/issues/172 | not_satisfied | 待临时 cleanup job 扫描并删除非 allowlist runs |
| R2 | 不把临时清理逻辑留在 main | https://github.com/dingyuwen777/Agent_Skills/issues/172 | not_satisfied | cleanup 成功后在同一 PR 分支恢复 `skill-tests.yml` |
| R3 | 清理后全量复扫 stale_count=0 | https://github.com/dingyuwen777/Agent_Skills/issues/172 | not_satisfied | 待 PR cleanup job 输出最终扫描证据 |
| R4 | 不删除三个正式 workflow 文件和历史 | https://github.com/dingyuwen777/Agent_Skills/issues/172 | satisfied | allowlist 固定为当前 main 三个真实 workflow 路径；代码写入前已重新读取 main 目录 |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | 当前 Actions 历史 API 总数中存在非 allowlist workflow runs，截图和 API 历史事实均证明 stale surface 存在。 |
| 行为 / Unit / Component | required | cleanup 脚本先只收集再删除；删除后全量复扫 stale count。 |
| 接口 / Contract | required | GitHub Workflow Runs REST API，DELETE `/actions/runs/{run_id}`；只使用 `GITHUB_TOKEN`，不输出 token。 |
| 集成 / Runtime Dependency | required | 在真实 GitHub-hosted `Skill Tests` PR job 中执行，对真实仓库 Actions 历史生效。 |
| 用户 / Workflow Acceptance | required | Actions API 最终只剩三个正式 workflow path 的 runs；侧栏显示由 GitHub UI 基于剩余历史刷新。 |
| 跨组件 Golden Path | not_applicable | 不涉及 Runtime/业务组件接线。 |
| 外部依赖 Probe | required | GitHub Actions REST 是本次真实外部依赖，使用当前仓库 token 做有界删除与复扫。 |
| Build / Package / Runtime | required | 因临时修改 workflow，PR `Runtime Package Gate` 按当前 classifier 给出新鲜证据；最终恢复 workflow 后再跑一次最终 CI。 |
| Docs / Governance / Other | required | Change、Issue #172、最终 diff、main fresh CI 与历史清理审计。 |

# 任务

- [x] 确认当前 main 真实只有三个正式 workflow 文件。
- [x] 建立 Issue #172 和本 L3 Change。
- [ ] 临时修改 Skill Tests，增加仅 PR 使用的 stale-run cleanup job。
- [ ] 执行 cleanup 并记录删除数量、路径/名称集合和最终 stale_count。
- [ ] 恢复 Skill Tests 原文件，更新本 Change 为 ready_for_review。
- [ ] 归档已完成的 Release identity Change，并让最终 PR required checks 全绿。

# 完成审计

- [ ] upstream_re_read: 清理完成后重新读取 Issue #172、main workflow 目录与 Actions runs。
- [ ] change_coverage: 清理完成后核对删除集合与 allowlist，没有扩大到正式 workflow。
- [ ] reverse_audit: 从剩余 Actions runs 反向确认只存在正式三个 path，并复核最终 PR diff 不含临时 cleanup 逻辑。
- [ ] unresolved_cleared: R1-R3 和所有清理/恢复/最终 CI 完成后再勾选。