---
schema: coding-change/v1
id: CHG-20260923-102000-actions-hygiene-rate-limit
title: Actions Hygiene 403 Rate Limit 临时错误识别
level: L3
status: done
owner: dingyuwen777
branch: fix/actions-hygiene-rate-limit
created: 2026-09-23
updated: 2026-09-23
completion_gate: required
depends_on:
  - CHG-20260923-063500-actions-hygiene
affected_areas:
  - ci
  - github-actions
  - maintenance
affected_paths:
  - .github/scripts/actions_hygiene.py
  - .agents/skills/coding/tests/test_actions_hygiene.py
contracts:
  - GitHub Actions Hygiene transient error semantics
data_changes: []
---

# 变更摘要

- **要解决的问题**：GitHub 安装级 API rate limit 可返回 HTTP 403；当前 Hygiene 只把 429/5xx/network 识别为 transient，会把明确限流误判为硬失败。
- **拟议修改**：仅在 403 响应具有明确 rate-limit 证据时映射为 transient/exit 75；普通 403 permission 继续硬失败。
- **预期结果**：GitHub 临时限流不会把 main 产品/治理 CI 误报为实现缺陷，同时权限错误仍 fail closed。

# 背景、现状与问题

## 背景

Requirement Source：Issue #296。AIMA_UGC main-fresh Actions Hygiene 真实返回 HTTP 403 + API rate limit exceeded for installation，证明 GitHub 的 rate-limit 不只使用 429。

## 当前现状

- Agent_Skills Actions Hygiene v2 已在 main，main-fresh #1804 Green。
- 当前 transient HTTP 状态只包含 429/500/502/503/504。
- 普通 403 当前硬失败，这一安全边界必须保持。

## 问题、根因或约束

不能简单把所有 403 加入 transient 集合，否则 actions:write 权限被撤销、token scope 错误等真实治理缺陷会被 warning 吞掉。必须通过 body/header 的 rate-limit 证据做窄判定。

## 不修改的后果

后续 GitHub 安装级 quota 耗尽时，Actions Hygiene 会把临时平台限流错误当成硬失败，违背 maintenance best-effort Contract。

# 事实与证据

| 证据 | 已确认事实 | 来源 | 决策 |
| --- | --- | --- | --- |
| E1 | GitHub rate-limit 真实返回 403 | AIMA #5534 Hygiene job | 403 不能一概视为硬失败 |
| E2 | 普通 403 可能表示权限错误 | GitHub REST 语义 | 不能把所有 403 transient |
| E3 | CI wrapper 只对 exit 75 warning | 当前 Skill Tests | 脚本错误分类是唯一需要修改的 Owner |

# 目标、成功标准与非目标

## 目标

精确识别 GitHub rate-limit 403，同时保持普通 403 权限错误 fail closed。

## 成功标准

- [ ] 明确 rate-limit 403 → TransientGitHubApiError → CLI 75。
- [ ] X-RateLimit-Remaining=0 / Retry-After 等明确 header 信号可触发 transient。
- [ ] 普通 403 permission denied → RuntimeError / CLI 1。
- [ ] 429/5xx/network/404 retired 既有语义不回归。
- [ ] 完成 tests/Review/CI/merge/main-fresh/archive/#296 closure。

## 范围

只修改 Actions Hygiene HTTP 错误分类和对应回归。

## 非目标

- 不改变 stale workflow 发现/删除算法。
- 不改变 Workflow/Job 权限或触发。
- 不新增 Workflow/Secret/依赖。

## 必须保持不变

current path 保护、first-parent history、active skip、completed-only delete、per-ID readback、job-level actions:write。

# 约束与意图决策

| 维度 | 决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| transient 判定 | 403 必须有明确 rate-limit 证据 | E1/E2 | 不吞普通权限失败 |
| CLI | transient=75，hard=1 | 既有 Contract | wrapper 无需修改 |
| API 404 | retired 语义不变 | 既有 v2 | 无行为扩张 |
| 依赖 | 标准库 | 当前实现 | 无依赖升级 |

# 修改方案与决策依据

## 最小充分方案

1. 新增纯函数判断 transient HTTP response。
2. 429/5xx 直接 transient。
3. 403 只有 body 包含 rate limit/secondary rate limit，或 response headers 明确 Retry-After / X-RateLimit-Remaining=0 时 transient。
4. 其他 403 保持 RuntimeError。
5. 单测覆盖 rate-limit 403、permission 403、429/5xx 回归。

## 证据到决策

| 决策 | 依据 | 原因 |
| --- | --- | --- |
| 不把 403 放进 TRANSIENT_HTTP_STATUS | E2 | 防止权限缺陷被吞 |
| 用 body/header 窄判定 | E1 | 覆盖真实 GitHub 安装级限流 |
| 不改 CI wrapper | E3 | 现有 exit75→warning Contract 已正确 |

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- 所有 403 transient：过宽，拒绝。
- 所有 403 hard：已被真实 rate-limit 证据否定。
- 只看 body：可行但不如 body+header 稳健。
- body+header：最小且可靠，采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | rate-limit 403 transient | #296 / AC1 | satisfied | `_is_transient_http_error()` 覆盖 body/header 明确信号；回归资产已落库 |
| R2 | permission 403 hard | #296 / AC2 | satisfied | 普通 403 不命中 rate-limit 证据时返回 False，继续 RuntimeError；回归已覆盖 |
| R3 | 既有 transient/404 不回归 | #296 / AC3 | satisfied | 429/503 回归已覆盖；404 retired 分支未修改 |
| R4 | 完整交付 | #296 / AC4 | not_applicable | pre-merge 不自证 CI/merge/main-fresh/archive/closure；由 delivery downstream gate 持有 |

# 计划改动

| 文件 | 修改 | 原因 |
| --- | --- | --- |
| .github/scripts/actions_hygiene.py | 精确 403 rate-limit 判定 | R1-R3 |
| .agents/skills/coding/tests/test_actions_hygiene.py | 错误分类回归 | R1-R3 |

- [x] 调查真实失败证据
- [x] 建立最小方案
- [x] 完成实现
- [ ] 取得 current-head CI（Ready gate 执行）
- [ ] 完成交付闭环

# 验证矩阵

| 层级 | 是否要求 | 证据 |
| --- | --- | --- |
| unit | required | 403 rate-limit / 403 permission / 429 / 5xx |
| CLI | required | transient=75 / hard=1 |
| CI | required | Skill Tests current-head |
| main-fresh | required | Hygiene 不因明确 rate-limit 403 变红 |
| Runtime package | proportional | 由现有 selector 决定 |

# 风险、兼容性、迁移与回滚

| 项目 | 结论 |
| --- | --- |
| 主要风险 | 误把权限 403 判成 transient；通过窄证据避免 |
| 兼容性 | 只扩充明确 rate-limit 错误分类 |
| Migration | 不适用 |
| 回滚 | 可 revert |

# 文档、依赖、部署与发布影响

无长期文档新增；无依赖、Secret、部署或 Release 变化。

# 完成审计

- [x] upstream_re_read：已重读 #296、AIMA #5534 真实 403 rate-limit 日志与 current main
- [x] change_coverage：AC1-AC3 已映射到实现/回归；AC4 downstream
- [x] reverse_audit：HTTPError → body/header rate-limit 判定 → TransientGitHubApiError → CLI 75 → CI warning
- [x] unresolved_cleared：实现侧 blocker 清零；CI/Review/post-merge 由 delivery gate 持有

# 完成证据与状态

## 新鲜证据

- V1：AIMA #5534 返回 403 API rate limit exceeded for installation。

## 未验证内容与剩余风险

待 current-head unit/CI/main-fresh。

## 交付状态

- PR：待创建
- CI：待 Ready PR current-head
- merge/archive/closure：未执行
