---
schema: coding-change/v1
id: CHG-20260921-105500-actions-history-cleanup
title: 清理废弃 GitHub Actions Workflow 历史
level: L3
status: ready_for_review
owner: dingyuwen777
branch: maintenance/actions-history-cleanup
created: 2026-09-21
updated: 2026-09-21
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - github-actions
  - maintenance
affected_paths:
  - .github/workflows/skill-tests.yml
contracts:
  - GitHub Actions history cleanup
data_changes: []
---

# 变更摘要

- 目标：清理 Actions 左侧仍显示的已删除一次性 Workflow 历史 runs。
- 实施：临时在现有 Skill Tests 增加 main-push-only cleanup job，job 级别仅授予 actions: write；不新增第四个长期 Workflow。
- 收尾：确认 obsolete workflow run 数量为 0 后，第二个 PR 删除临时 cleanup job，最终 main 恢复只保留原有长期 CI。

# 背景、现状与问题

Requirement Source：GitHub Issue #289。

当前 main 的 workflow 文件只有 Release、Change Archive、Skill Tests；Actions 历史仍保留已删除的一次性 workflow runs，导致 All workflows 左侧继续显示旧名称。


# 事实与证据

| 证据编号 | 已确认事实 | 来源 | 支撑决策 |
| --- | --- | --- | --- |
| E1 | main 当前只有 release.yml / change-archive.yml / skill-tests.yml 三个 workflow 文件 | GitHub contents API / main | 旧名称不是现役 workflow 文件 |
| E2 | Actions 历史已分页扫描到空页，存在 #289 列出的 obsolete workflow path runs | GitHub Actions runs API | 需要删除历史 runs 才能清理 All workflows 左侧残留 |
| E3 | 当前 GitHub connector 没有 delete workflow run 动作 | 当前工具能力检查 | 需要复用仓库自身 GITHUB_TOKEN 执行一次性清理 |
| E4 | Skill Tests 已有 push main 触发入口 | .github/workflows/skill-tests.yml | 可在不新增 Workflow 名称的前提下承载一次性 main-only job |

# 计划改动

| 文件 / 模块 | 修改 | 原因 |
| --- | --- | --- |
| .github/workflows/skill-tests.yml | 临时增加 Cleanup Obsolete Actions History job | 用现有 workflow 名称执行一次性 Actions history DELETE |
| cleanup job permissions | 仅 job-level actions: write + contents: read | 不扩大其他 CI job 权限 |
| cleanup job trigger | 仅 push main | PR 阶段无删除副作用 |
| 后续第二 PR | 删除临时 cleanup job | 最终 main 不保留一次性逻辑 |

# 风险、兼容性、迁移与回滚

| 项目 | 结论 / 处理 |
| --- | --- |
| 主要风险 | workflow run 删除不可逆，会删除对应历史日志；用户已明确要求清理废弃历史 |
| 误删风险 | 只匹配显式 obsolete path allowlist，绝不按“非当前 workflow”泛化删除 |
| 权限风险 | actions: write 仅授予 cleanup job，且仅 main push 执行 |
| 兼容性 | 不改变 Release / Change Archive / Skill Tests 长期行为；不改 Runtime/License/Skill Contract |
| Migration | 不适用；仅 Actions 历史维护 |
| 回滚 | 已删除的历史 run 无法恢复，因此删除前必须按 allowlist 收集，删除后 readback 为 0 才算成功 |

# 文档、依赖、部署与发布影响

- 长期文档：不适用；这是 GitHub Actions 历史清理，不改变用户/Runtime 长期事实。
- 依赖：无新增依赖；cleanup 使用 runner 自带 Python 标准库。
- 部署：不适用。
- Release：不修改 release.yml，不删除任何 Release workflow run。
- CI：第一阶段临时增加一个 main-only cleanup job；第二阶段必须删除，最终 workflow 数量和长期职责恢复原状。

# 目标、成功标准与非目标

## 成功标准

- [x] 清理范围只包含 #289 列出的 obsolete workflow path。
- [x] Release / Change Archive / Skill Tests 的历史 runs 明确排除。
- [ ] main push cleanup job 成功删除所有 obsolete runs，并 readback 为 0。
- [ ] 第二阶段移除 cleanup job，最终 main 仍只有 3 个正式 workflow 文件。

## 非目标

- 不删除当前三个长期 Workflow 的任何 run。
- 不新增永久 Actions 清理 Workflow。
- 不修改 Release、Runtime、License、Skill/Reference 业务行为。

# 约束与意图决策

| 决策维度 | 当前决定 |
| --- | --- |
| 权限 | cleanup job 单独使用 actions: write；现有 core/package jobs 权限不扩大 |
| 触发 | 只在 push main 执行；PR 中 cleanup job 不执行 |
| 删除范围 | 使用显式 obsolete path allowlist，不使用“非当前 workflow 全删” |
| 验证 | 删除前收集 IDs；删除后重新分页 readback，任何残留 fail closed |
| 收尾 | 清理成功后立即通过第二 PR 删除一次性 job |

# 修改方案与决策依据

1. 在 Skill Tests 追加临时 cleanup-obsolete-actions-history job。
2. 用 GitHub Actions token + actions: write 调用 DELETE workflow run API。
3. 只删除 #289 中显式列出的旧 workflow path。
4. main push 后验证 remaining obsolete run count=0。
5. 第二 PR 移除该 job。

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- 浏览器逐个删除：历史 run 数量约数百，不可维护且当前浏览器无登录会话。
- 新建独立 Cleanup Workflow：会额外污染 All workflows，不采用。
- 复用 Skill Tests：不新增 workflow 名称，且可通过 job-level 权限把 destructive capability 限定到一个 main-only job，采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 不碰 3 个正式 Workflow 历史 | #289 AC1 | satisfied | 显式 obsolete path allowlist |
| R2 | 删除所有废弃 workflow runs | #289 AC2/AC3 | not_satisfied | 待 main cleanup job |
| R3 | 最终 main 不保留 cleanup job | #289 AC4/AC5 | not_satisfied | 待第二阶段 PR |
| R4 | required CI/main-fresh | #289 AC6 | not_satisfied | downstream gate |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | not_applicable | 一次性 GitHub Actions 外部副作用，无本地业务单元逻辑 |
| 接口 / Contract | required | workflow YAML + permission/if/path allowlist review |
| 集成 / Runtime Dependency | required | GitHub Actions API 真实 DELETE + readback |
| 用户 / Workflow Acceptance | required | Actions history 不再返回 obsolete path |
| Build / Package / Runtime | not_applicable | 不改 Runtime/package |
| Docs / Governance | required | Issue #289 + Change + PR/CI |

# 完成审计

- [x] upstream_re_read：已读取当前 workflows、全部 Actions 历史分页和当前 CI/Git 规则。
- [x] change_coverage：删除范围、保留范围、权限和收尾均已明确。
- [x] reverse_audit：obsolete path → run IDs → DELETE → fresh readback。
- [ ] unresolved_cleared：等待真实 main cleanup + 第二阶段移除临时 job。

# 完成证据与状态

## 新鲜证据

- 当前 main .github/workflows 只有 release.yml / change-archive.yml / skill-tests.yml。
- Actions 历史分页已完整扫描到空页；旧 workflow path 和 run IDs 已确认。

## 交付状态

- PR：待创建
- CI：待执行
- Merge：待执行
- Cleanup readback：待执行