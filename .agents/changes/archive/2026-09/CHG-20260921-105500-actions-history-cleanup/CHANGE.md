---
schema: coding-change/v1
id: CHG-20260921-105500-actions-history-cleanup
title: 清理废弃 GitHub Actions Workflow 历史
level: L3
status: done
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

## 背景

Requirement Source：GitHub Issue #289。用户明确要求删除 Actions / All workflows 中冗余且已无用的历史 Workflow 项。

## 当前现状

- main 当前 `.github/workflows/` 只有 release.yml、change-archive.yml、skill-tests.yml。
- GitHub Actions 历史仍保留多个已删除 workflow path 的 runs，因此左侧仍显示旧 Workflow 名称。
- Actions 历史已经分页扫描到空页，旧 Workflow path 与 run IDs 均已确认。

## 问题、根因或约束

删除 YAML 文件只移除了当前 Workflow 定义，并不会自动删除历史 runs。当前 GitHub connector 没有 delete workflow run 动作，因此需要使用仓库自身 GitHub Actions token 执行一次性历史清理。

## 不修改的后果

Actions 左侧继续展示 Runtime Package Tests、Runtime Name Migration、CI238/Temporary 等已废弃 Workflow，增加维护噪音并误导当前 CI 事实。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 | 支撑决策 |
| --- | --- | --- | --- |
| E1 | main 当前只有 3 个 workflow 文件 | GitHub contents API / main | 旧名称不是现役 Workflow |
| E2 | 历史 runs 仍包含 #289 所列 obsolete workflow path | GitHub Actions runs API 分页到空页 | 需要删除 runs 才能清理左侧历史条目 |
| E3 | 当前 connector 没有 delete workflow run 动作 | 当前工具能力检查 | 需要通过 GITHUB_TOKEN 执行一次性 DELETE |
| E4 | Skill Tests 已有 push main 入口 | skill-tests.yml | 可复用现有 Workflow 名称，不新增第 4 个 Workflow |

## 推断与待确认

- 待确认：GitHub 在所有 obsolete runs 删除后，Actions 左侧对应旧 Workflow 项会消失；本任务以 Actions API fresh readback 中 obsolete path=0 作为直接完成证据。
- 待确认：当前仓库 GITHUB_TOKEN 在 job-level actions: write 下可执行 DELETE workflow run；若平台拒绝则 fail closed，不改用扩大权限的替代方案。

# 目标、成功标准与非目标

## 目标

清理已删除一次性 Workflow 的历史 runs，并在完成后移除所有临时清理代码，使 main 继续只保留 Release / Change Archive / Skill Tests 三个长期 Workflow。

## 成功标准

- [ ] obsolete workflow path 的历史 run 数量为 0。
- [ ] Release / Change Archive / Skill Tests 的历史 runs 未被删除。
- [ ] 第一阶段 cleanup job 在 main push 中真实成功。
- [ ] 第二阶段删除一次性 cleanup job。
- [ ] 最终 main `.github/workflows/` 仍只有 3 个正式文件。

## 范围

- #289 中显式列出的 11 个 obsolete workflow path 的历史 runs。
- skill-tests.yml 中一次性 main-only cleanup job。
- cleanup 成功后的临时逻辑移除。

## 非目标

- 不删除当前三个长期 Workflow 的任何历史 run。
- 不新增永久 Actions Cleanup Workflow。
- 不修改 Runtime、Release、License、Skill/Reference 行为。
- 不清理 Issues、PR、Release、tag 或分支。

## 必须保持不变

- Release / Change Archive / Skill Tests 三个 Workflow 的当前长期职责。
- 现有 core/package jobs 的权限模型。
- Branch Protection、required CI 和 Change Archive 门禁。

# 约束与意图决策

| 决策维度 | 当前决定 |
| --- | --- |
| 删除范围 | 仅显式 obsolete path allowlist |
| 权限 | cleanup job 单独 actions: write + contents: read |
| 触发 | 仅 push main；PR 阶段 cleanup job 不执行 |
| 删除算法 | 先完整分页收集 IDs，再逐个 DELETE，最后 fresh readback |
| 失败语义 | 任一删除失败或 readback 残留均 fail closed |
| 收尾 | 成功后第二 PR 删除一次性 job |

# 修改方案与决策依据

## 最小充分方案

1. 在 Skill Tests 追加一次性 `cleanup-obsolete-actions-history` job。
2. job 仅在 push main 时运行，并单独授予 actions: write。
3. 用 Python 标准库调用 GitHub Actions REST API，按显式 path allowlist 收集并删除 runs。
4. 删除后再次完整分页查询；存在任何 obsolete run 即失败。
5. 确认清理成功后提交第二 PR 删除临时 job。

## 证据到决策

| 决策 | 依据 | 原因 |
| --- | --- | --- |
| 复用 Skill Tests | E1/E4 | 不新增 Actions 左侧 Workflow 名称 |
| 显式 allowlist | E2 | 降低误删现役历史的风险 |
| job-level actions: write | E3 | 只给 destructive job 最小权限，不扩大其他 CI |
| 两阶段交付 | 用户目标 + 最小长期表面 | 清理动作需要临时执行能力，但 main 最终不应保留死逻辑 |

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- 浏览器逐个删除：历史 runs 数量数百，且当前浏览器无登录会话；不可行。
- 新建独立 Cleanup Workflow：会新增一个新的 Actions 菜单项，和清理目标冲突；不采用。
- 永久保留 cleanup job：会形成长期无用 CI 逻辑；不采用。
- 复用 Skill Tests 两阶段清理：权限可局部化、无新增 Workflow 名称、完成后可恢复原状；采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 不删除 3 个正式 Workflow 历史 | #289 / AC1 | satisfied | cleanup 只匹配显式 obsolete path allowlist，Release/Change Archive/Skill Tests 均不在 allowlist |
| R2 | 删除全部废弃 workflow runs | #289 / AC2 | not_applicable | pre-merge Change 不自证 merge 后 destructive side effect；由 implementation main-push cleanup job 持有 |
| R3 | 删除后 obsolete path fresh readback 为 0 | #289 / AC3 | not_applicable | 依赖 R2 实际 DELETE 后执行；由 post-merge delivery gate 持有 |
| R4 | 最终 main 仍只有 3 个正式 Workflow | #289 / AC4 | not_applicable | 需要第二阶段移除临时 cleanup job 后才能验证 |
| R5 | 一次性 cleanup job 完成后移除 | #289 / AC5 | not_applicable | 第二阶段 cleanup-removal PR 持有 |
| R6 | 两阶段 required CI/main-fresh 全部完成 | #289 / AC6 | not_applicable | pre-merge Change 不自证未来 CI/merge/main-fresh；由 downstream delivery gate 持有 |

# 计划改动

| 文件 / 模块 | 修改 | 原因 |
| --- | --- | --- |
| `.github/workflows/skill-tests.yml` | 临时增加 Cleanup Obsolete Actions History job | 执行一次性历史 DELETE |
| cleanup job permissions | actions: write + contents: read | 最小 destructive 权限 |
| cleanup job trigger | push main only | PR 阶段无删除副作用 |
| 第二阶段同文件 | 删除临时 cleanup job | 恢复长期 workflow 原状 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | not_applicable | 无新的可复用业务单元逻辑 |
| 接口 / Contract | required | Workflow YAML、if、permissions、allowlist Review |
| 集成 / Runtime Dependency | required | GitHub Actions API 真实 DELETE + readback |
| 用户 / Workflow Acceptance | required | Actions history obsolete path=0 |
| 跨组件关键路径 | required | main push → cleanup job → DELETE API → readback |
| 外部依赖 / 供应方探测 | required | GitHub Actions REST API |
| Build / Package / Runtime | not_applicable | 不改 Runtime/package |
| Docs / Governance | required | Issue #289 + Change + PR/CI |

## 验证计划

- PR current-head：Requirement Source、Ready Check、Skill Tests required CI。
- Merge main：确认 cleanup job success，并读取日志中的删除总数/最终 0。
- API fresh readback：完整分页确认 obsolete path 不再出现。
- 第二阶段：删除临时 job，PR/CI/main-fresh Green。
- 最终 contents readback：`.github/workflows/` 精确只有 3 个文件。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 / 处理 |
| --- | --- |
| 主要风险 | workflow run 删除不可逆，会删除历史日志；用户已明确授权清理废弃历史 |
| 误删风险 | 只匹配显式 obsolete path，不采用泛化删除 |
| 权限风险 | actions: write 只授予 main-only cleanup job |
| 兼容性 | 不改变长期 Workflow 行为 |
| 数据 / Migration | 不适用；仅 GitHub Actions 历史维护 |
| 回滚 | 已删除历史 run 无法恢复，因此删除前 allowlist + 删除后 readback 是硬门禁 |

# 文档、依赖、部署与发布影响

- 长期文档：不适用；不改变产品/用户事实。
- 依赖：无新增依赖，使用 Python 标准库。
- 部署：不适用。
- Release：不修改 release.yml，不删除任何 Release run。
- CI：临时增加一个 main-only cleanup job，第二阶段必须移除。

# 完成审计

- [x] upstream_re_read：已读取 #289、当前 workflows、Actions 全量历史分页与 CI/Git 规则。
- [x] change_coverage：删除范围、保留范围、权限、执行和收尾均已覆盖。
- [x] reverse_audit：obsolete path → run IDs → DELETE → fresh readback → 临时 job removal。
- [x] unresolved_cleared：pre-merge Requirement 已清零；DELETE/readback/第二阶段移除/main-fresh/Issue Closure 明确由 downstream delivery gate 持有，不在当前 Change 中伪造完成。

# 完成证据与状态

## 新鲜证据

- 当前 main `.github/workflows/` 只有 3 个正式文件。
- Actions 历史分页已完整扫描到空页。
- PR 阶段 cleanup job 因 main-only 条件正确 skipped。

## 未验证内容与剩余风险

- 尚未在 main push 中真实执行 DELETE。
- 尚未取得删除后的 Actions API 0 残留 readback。
- 尚未移除临时 cleanup job。

## 交付状态

- Requirement Source：#289 open
- PR：#290 open
- CI：等待 current-head fresh run
- Merge：未执行
- Cleanup：未执行

## 备注

本 Change 只承担第一阶段 destructive cleanup 的正式门禁；第二阶段仅删除已完成使命的临时 CI job，并继续使用 #289 作为 Requirement Source。