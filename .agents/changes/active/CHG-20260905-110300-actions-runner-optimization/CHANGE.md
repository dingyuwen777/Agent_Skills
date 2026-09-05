---
schema: coding-change/v1
id: CHG-20260905-110300-actions-runner-optimization
title: 优化 Actions 风险分层与 Change-only Fast Path
level: L3
status: proposed
owner: dingyuwen777
branch: chg/20260905-actions-runner-optimization
created: 2026-09-05
updated: 2026-09-05
completion_gate: required
depends_on: []
affected_areas:
  - github-actions
  - ci-governance
  - runtime-evidence
  - change-lifecycle
affected_paths:
  - .github/scripts/runtime_package_scope.py
  - .github/workflows/skill-tests.yml
  - .github/workflows/change-archive.yml
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
  - .agents/skills/coding/tests/test_runtime_package_scope.py
  - .agents/skills/coding/tests/test_repository_change_archive_automation.py
contracts:
  - Agent Skills CI Evidence Preservation Contract
  - Runtime Package Scope Contract
  - Repository-native Change Archive Trigger Contract
data_changes: []
---

# 目标

在不删除 Runtime semantic regression、Linux/Windows/macOS package evidence、required checks 或 Release 三平台构建的前提下，为 Change-only 生命周期提交和 Draft package 迭代增加精确 fast-path，减少无效 GitHub Runner 时间。

# 成功标准

- [ ] 只有 `.agents/changes/**` 的变更命中 Change-only 档位，普通 governance 不误入。
- [ ] Change-only 保留 Requirement/Ready/Change 合法性和 required gate，但不重复 Runtime semantic/package 工作。
- [ ] Draft package 迭代不构建三平台 binary，且 required Runtime Package Gate 保持阻塞；Ready 后重新跑完整 package evidence。
- [ ] Change Archive 不为没有 Active Change 的 merged PR 自动启动。
- [ ] 依赖缓存只复用下载缓存，不缓存 binary/test result。

# 范围

- 扩展 Runtime package scope classifier 与回归。
- 调整统一 Skill Tests 的 Change-only/Draft/Ready 路由和 dependency cache。
- 调整 Change Archive closed-PR path filter。
- 更新 Workflow Responsibility Audit 永久回归。

# 非目标

- 不修改 Runtime 协议、Bundle、Project Payload、MCP 或 Source/Runtime parity。
- 不删除 Linux/Windows/macOS Runtime package evidence。
- 不降低 `Agent Skills Gate` / `Runtime Package Gate` required contexts。
- 不修改正式 Release 产品格式或三平台 Release 构建。

# 必须保持不变

- 根 `AGENTS.md`、`.agents/MAINTENANCE.md` 等普通 governance 变化仍运行现有 semantic regression；只有 Change carrier 变化才能 fast-path。
- content/package 变化继续运行原 self-contained tests；package 变化在 Ready/non-draft/main 继续真实构建 Linux/Windows/macOS binary。
- Draft 轻量路径不得成为可合并 package 证据，Ready 后必须重新触发完整 evidence。
- Change Archive helper、strict allowlist、App token、main drift guard 与 workflow_dispatch 语义不变。
- Release Workflow 的三平台正式构建与 identity 交叉验证不变。

# 关键决策

- 新增 `change_only` 作为比 `governance` 更窄的证据档位，而不是把所有 governance 一起变轻；这样保留 #212 已证明必要的 Maintenance/Bootstrap 语义回归。
- Draft package PR 通过明确失败的 `Runtime Package Gate` 保持 fail-closed；`ready_for_review` 事件重新运行完整 package evidence。
- Cache 只使用 setup-python/pip 下载缓存并绑定 requirements；binary artifact 每个需要证据的 SHA 仍重新构建。
- 回滚只涉及 CI/分类器/测试，无数据或 Runtime 协议迁移。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 精确 Change-only scope，不误伤普通 governance | #213 / AC1 | not_satisfied | 尚未实现 |
| R2 | Change-only 保留治理 required checks，跳过 Runtime semantic/package 重工作 | #213 / AC2 | not_satisfied | 尚未实现 |
| R3 | Draft package 不构建三平台且 gate 阻塞，Ready/non-draft/main 恢复完整 evidence | #213 / AC3 | not_satisfied | 尚未实现 |
| R4 | 普通 governance/content/package 原 semantic 责任保持 | #213 / AC4 | not_satisfied | 尚未实现 |
| R5 | Change Archive 增加 Active Change path filter，dispatch 保留 | #213 / AC5 | not_satisfied | 尚未实现 |
| R6 | pip cache 只缓存依赖下载，package 仍真实构建 | #213 / AC6 | not_satisfied | 尚未实现 |
| R7 | 永久回归与 Workflow Responsibility Audit 证明 required identity/runner budget/Release 责任守恒 | #213 / AC7 | not_satisfied | 尚未实现 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | scope classifier、Workflow fast-path 与 Archive trigger 永久回归 |
| 接口 / 契约 | required | `runtime_scope` 枚举、required check names、Ready event contract |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变外部持久化或 Runtime 执行协议；CI 执行本身由 GitHub Actions 验证 |
| 用户 / 工作流验收 | required | Draft package → Ready full evidence；Change-only archive/main gate 工作流 |
| 跨组件关键路径 | not_applicable | 不改变目标项目跨组件产品链 |
| 外部依赖 / 供应方探测 | not_applicable | 不改变第三方 Provider/远端服务事实 |
| 构建 / 打包 / 运行 | required | 本 PR 因修改 package Workflow 自身必须取得 Linux/Windows/macOS current-head package evidence |
| 文档 / 治理 / 其他 | required | Workflow Responsibility Audit、Ready gate、Change completion 与 Release Owner 守恒 |

# 完成审计

- [ ] upstream_re_read：完成前重读 #213 AC1-AC7 与 Maintenance/CI References。
- [ ] change_coverage：逐项确认 R1-R7 有实现和 current evidence。
- [ ] reverse_audit：反查 Change-only、普通 governance、content、package、Draft/Ready/main/release 五类路径。
- [ ] unresolved_cleared：所有 not_satisfied 清零且无较弱证据冒充。

# 任务

- [x] 调查当前 Skill Tests、Scope、Release、Change Archive 与实际 Run 成本。
- [x] 建立 Workflow Responsibility Audit / Evidence Preservation 方案。
- [ ] 增加 Red 回归覆盖 Change-only 与 Draft package 缺口。
- [ ] 实现 scope/Workflow/cache/path filter。
- [ ] 取得 current-head 三平台 package evidence。
- [ ] 完成 Completion Audit / Review。

# 验证

## 计划

- targeted：`test_runtime_package_scope.py`、`test_ci_workflow_minimal_sufficiency.py`、`test_repository_change_archive_automation.py`。
- self-contained：Coding tests 全量。
- Ready：`python .agents/skills/coding/scripts/ready_check.py --root . --changed-since <base>`。
- Actions：本 Workflow 自身属于 package 风险，current-head 必须验证 Linux/Windows/macOS package evidence 与 required gates。

## 新鲜证据

- 尚未执行。

# 文档影响

- 人类 README/USAGE/runtime README 不承担本次 CI 内部证据路由语义；永久治理事实由 Workflow + 回归 + Change 承担。

# 交付

- Requirement Source：#213
- 提交：待实现
- 拉取请求：待创建
- 发布：不适用
