---
schema: coding-change/v1
id: CHG-20260923-063500-actions-hygiene
title: GitHub Actions 失效 Workflow 自动清理
level: L3
status: done
owner: dingyuwen777
branch: maintenance/actions-hygiene
created: 2026-09-23
updated: 2026-09-23
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - github-actions
  - maintenance
affected_paths:
  - .github/scripts/actions_hygiene.py
  - .github/scripts/runtime_package_scope.py
  - .github/workflows/skill-tests.yml
  - .agents/skills/coding/tests/test_actions_hygiene.py
  - .agents/MAINTENANCE.md
contracts:
  - GitHub Actions Hygiene
data_changes: []
---

# 变更摘要

- **要解决的问题**：删除或重命名 Workflow 后，历史 Actions runs 会继续让失效 Workflow 出现在 All workflows；此前只有一次性清理，没有长期自动治理。
- **拟议修改**：新增 repo-local Actions Hygiene 脚本，并在现有 Skill Tests 中增加 main-push-only hygiene job；不新增独立 Workflow。
- **预期结果**：以后 Workflow 从 main 删除/重命名后，符合安全判据的 completed 历史 runs 会在后续健康 main push 中自动清理。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #294。用户要求 Agent_Skills 与 AIMA_UGC 都长期自动清理 Actions → All workflows 中已失效的 Workflow 历史项。

## 当前现状

- main 当前长期 Workflow 只有 Release、Change Archive、Skill Tests。
- 2026-09-21 已进行一次性历史清理，临时脚本/job 已从 main 删除。
- 当前没有永久 Actions Hygiene 实现。

## 问题、根因或约束

GitHub 删除 Workflow YAML 不会自动删除历史 workflow runs，因此 All workflows 可长期保留旧入口。删除历史 run 是不可逆外部写操作，必须最小权限、fail-closed 识别范围，并避免影响现役 Workflow。

## 不修改的后果

以后每次删除/重命名 Workflow 都可能再次产生历史噪音，需要人工重复清理。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | main 只有 3 个长期 Workflow | .github/workflows 当前目录 | 不新增第 4 个 Cleanup Workflow |
| E2 | 一次性 cleanup 已被移除 | main readback / 历史提交 | 本次需要长期机制 |
| E3 | Skill Tests 已有 main push 与正式 Gate | .github/workflows/skill-tests.yml | Hygiene 可复用现有 Workflow |
| E4 | GitHub Actions run 删除需要 actions: write | GitHub Actions API Contract | 权限只能下放到 hygiene job |

## 推断与待确认

- 待确认：main-fresh 时 GitHub token 的 job-level actions: write 能完成真实 read/delete API；若 API 临时失败，job 按 best-effort warning 返回，不影响产品 CI。
- 当前干净基线下预期 deleted=0 / remaining=0。

# 目标、成功标准与非目标

## 目标

建立长期、自动、保守的失效 Workflow 历史清理能力。

## 成功标准

- [x] AC1 当前 Workflow path 永不进入删除集合。
- [x] AC2 只有当前 main 已消失且真实存在于默认分支祖先历史的 Workflow path 可进入 obsolete candidate；PR-only path 不删除。
- [x] AC3 candidate path 存在未完成 run 时整条 path 跳过；只删除 completed runs。
- [x] AC4 删除前完整分页，删除后 fresh readback，API/历史判断异常 fail closed。
- [x] AC5 hygiene 只在 main push + 正式 Gate Green 后执行；actions: write 只授予该 job。
- [x] AC6 API 临时失败 warning + 后续 main push 重试，不使产品 CI 失败。
- [x] AC7 main 最终仍只有 3 个长期 Workflow。
- [ ] AC8 完成 tests/Review/CI/merge/main-fresh/archive/#294 closure。

## 范围

- repo-local Actions Hygiene 脚本。
- Skill Tests 中永久 hygiene job。
- 单元/Contract 回归。
- canonical Workflow 生命周期规则。

## 非目标

- 不新增独立 Cleanup Workflow。
- 不删除当前 Workflow 的历史 runs。
- 不清理 Issue/PR/Release/tag/branch。
- 不新增服务、数据库或计划任务。

## 必须保持不变

- Release / Change Archive / Skill Tests 的当前职责与名称。
- Runtime package、License、Router/Skill 语义。
- 现有 required CI/Change Archive 门禁。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 仅 GitHub Actions 历史维护 | #294 / E1-E4 | 不影响产品与 Runtime |
| 接口与契约 | 新增 repo-local CLI，dry-run 默认，--execute 才删除 | #294 / AC4 | 易测试、默认安全 |
| 数据与迁移 | 不适用 | 无业务数据 | 无 Migration |
| 错误与失败语义 | 判定/API 失败 fail closed；CI wrapper warning 不阻塞产品 Gate | #294 / AC4/AC6 | 不误删、不把维护波动变成产品红灯 |
| 兼容性 | 当前 3 个 Workflow 及其 runs 全部保护 | #294 / AC1/AC7 | 不改变现役入口 |
| 部署与回滚 | 代码可 revert；已删除 Actions run 不可恢复 | GitHub 平台事实 | 删除前判定必须保守 |

# 修改方案与决策依据

## 最小充分方案

1. 新增 .github/scripts/actions_hygiene.py：完整分页 repository workflow records，结合当前 workflow paths 与 Git first-parent main 历史识别 stale workflow IDs。
2. 只对 stale workflow ID 定向完整分页 runs；脚本默认 dry-run，--execute 才删除 eligible completed runs，并逐 stale workflow ID fresh readback。正常 main push 无 stale record 时不扫描全仓 runs。
3. Skill Tests 增加 actions-hygiene job，仅 push main、正式 Gate Green 后运行；job-level actions: write + contents: read。
4. job 调用脚本；远端 API 异常转为 ::warning:: 并退出 0，下次 main push 自动重试。
5. 增加测试覆盖 current / obsolete / PR-only / active-run / completed obsolete / workflow permissions。
6. canonical CI Rule 记录 Workflow Responsibility Audit 的历史清理责任。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 复用 Skill Tests | E1/E3 | 不新增 All workflows 菜单项 |
| D2 main-history 判定 | #294 / AC2 | 防止误删只在 PR branch 出现的 Workflow |
| D3 path 有 active run 时整条跳过 | #294 / AC3 | 避免删除与进行中运行同属一 Workflow 的历史证据 |
| D4 best-effort wrapper | #294 / AC6 | 维护 API 波动不应阻塞产品 CI |

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- 独立 Cleanup Workflow：会新增长期菜单项，与目标冲突；不采用。
- 名字/固定 allowlist：长期维护成本高且 rename 易漂移；不采用。
- 定时任务：当前 main push 已足够触发，增加 schedule 无必要。
- 直接删除所有“当前不存在”的 path：会误删 PR-only/不确定历史；不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | current path 永不删除 | #294 / AC1 | satisfied | stale workflow record selection 以 current path 为绝对保护，回归已覆盖 |
| R2 | main-history / PR-only 边界 | #294 / AC2 | satisfied | first-parent main-history 判定与真实 Git fixture 覆盖 main 删除/PR-only merge |
| R3 | active-run skip / completed only | #294 / AC3 | satisfied | stale workflow ID 定向 run 快照保持 active 整条 skip；completed-only deterministic plan 覆盖 |
| R4 | targeted snapshot/delete/readback + fail closed | #294 / AC4 | satisfied | repository workflow records → stale workflow ID → targeted runs → DELETE → per-ID readback；测试禁止 global runs scan |
| R5 | main + Gate + minimal permission | #294 / AC5 | satisfied | Skill Tests main-only hygiene job + job-level actions:write；workflow 顶层不提升 |
| R6 | maintenance failure semantics | #294 / AC6 | satisfied | 仅 429/5xx/network 返回 75；权限/结构/历史/readback 保持硬失败，CLI/Workflow 回归覆盖 |
| R7 | 保持 3 个长期 Workflow | #294 / AC7 | satisfied | 未新增 .github/workflows 文件；仅在现有 Skill Tests 中增加 job，当前正式 Workflow 文件数量保持 3 |
| R8 | 完整交付闭环 | #294 / AC8 | not_applicable | pre-merge Change 不自证未来 Review/merge/main-fresh/archive/Issue closure；由 delivery downstream gate 持有 |
# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| .github/scripts/actions_hygiene.py | 新增安全计划/执行器 | 自动清理 | R1-R4 |
| .github/workflows/skill-tests.yml | 新增 hygiene job | repository-native 触发 | R5-R7 |
| .agents/skills/coding/tests/test_actions_hygiene.py | 新增行为/Contract 回归 | 防回归 | R1-R6 |
| reference 07 | 增加 Workflow 生命周期责任 | canonical 规则 | R5-R7 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 清理计划算法和边界 |
| 接口 / 契约 | required | CLI JSON、Workflow trigger/needs/permissions |
| 集成 / 持久化 / 运行依赖 | required | Git history + GitHub Actions REST |
| 用户 / 工作流验收 | required | All workflows 不再累积失效历史 |
| 跨组件关键路径 | required | main push → Gate → hygiene → API → readback |
| 外部依赖 / 供应方探测 | required | main-fresh GitHub Actions API dry/execute |
| 构建 / 打包 / 运行 | not_applicable | 不改 Runtime build/package |
| 文档 / 治理 / 其他 | required | canonical CI rule + Change/Issue |

## 验证计划

- 目标测试：test_actions_hygiene.py。
- 相关回归：selected/full semantic according to Skill Tests selector。
- 静态检查或构建：py_compile。
- 专项真实边界：main-fresh hygiene job。
- 就绪检查：ready_check --require-active-ready。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | Actions run 删除不可逆 | 保守候选 + active skip + fresh readback |
| 兼容性 | 保持当前 Workflow 与 runs | current path 绝对保护 |
| 数据 / Migration | 不适用 | 无业务数据 |
| 部署 / 运行 | 不适用 | 仅仓库维护 |
| 回滚 / 恢复 | 代码可 revert；已删 run 不可恢复 | 删除前强门禁 |

# 文档、依赖、部署与发布影响

- **长期文档**：仅 canonical CI/Workflow 生命周期规则更新。
- **依赖 / Runtime**：无新增依赖，Python 标准库。
- **配置 / Secret**：只使用 GitHub 自动 token，不新增 Secret。
- **部署 / Release**：不适用，不修改 Release surface。
- **兼容 / 消费方通知**：维护者可见 Actions 历史自动清理。

# 完成审计

- [x] upstream_re_read：Ready 前已重读 Issue #294、current main 与本 Change 的直接事实源。
- [x] change_coverage：AC1-AC7 已映射到定向实现与回归资产；AC8 post-merge 由 downstream gate 持有。
- [x] reverse_audit：已按 workflow records → main history → stale workflow IDs → targeted runs → delete → per-ID readback 反向复核。
- [x] unresolved_cleared：实现侧 blocker 已清零；current-head CI/Review 与 post-merge 继续由 delivery gate 持有。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main | workflows/readback + cleanup absence | confirmed | 当前干净基线且无永久实现 |
| V2 | current branch / PR #295 | current-head diff + static Contract audit | Green | 候选算法、Git main-history、权限最小化、canonical 生命周期规则均已落库；真实 API 待 Ready/main-fresh |
| V3 | PR #295 / Issue #294 | canonical Requirement Source revalidation | fixed | 技术变更 Issue 已补齐动机/根因、兼容迁移、风险回滚、稳定 AC、验证要求和上游事实源 |
| V4 | current branch | destructive boundary regression expansion | added | first-parent history、DELETE+fresh-zero、fresh-residual fail-closed 已加入 targeted tests |
| V5 | AIMA_UGC #573 archive | 36,626 runs + 全仓 paginate 首轮卡住 → stale workflow ID 定向方案 Green | confirmed | 长期 Hygiene 禁止每次 main push 扫描全仓 runs；Agent_Skills 同步采用成熟定向模型 |

## 未验证内容与剩余风险

- 定向分页 redesign 尚未取得 current-head required CI。
- 尚未在 main-fresh 验证真实 GitHub Actions API。

## 交付状态

- 提交：实现、测试、Workflow 接线和文档已在 maintenance/actions-hygiene
- 拉取请求：#295（Ready）
- CI：历史 run 受私有 Runner 0ms 平台问题影响；定向 redesign 提交后等待 fresh required CI
- 合并：未执行
- Change 归档：未执行
- 发布 / 部署：不适用

## 备注

无。