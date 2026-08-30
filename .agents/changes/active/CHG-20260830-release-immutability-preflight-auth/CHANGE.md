---
schema: coding-change/v1
id: "CHG-20260830-release-immutability-preflight-auth"
title: "修复 Release Immutability 预检鉴权边界"
level: L3
status: proposed
owner: "dingyuwen777"
branch: "fix/release-immutability-preflight-auth"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "GitHub Release preflight"
  - "Release Immutability 权限与失败分类"
  - "维护者 Release 使用说明"
affected_paths:
  - ".github/workflows/release.yml"
  - ".agents/skills/coding/tests/test_runtime_release_hardening.py"
  - ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"
  - "README.md"
contracts:
  - "正式 Release fail-closed 与 Immutability 确认流程"
data_changes: []
---

# 目标

修复 Release #4 暴露的 Immutability 预检鉴权错误：GitHub Actions 默认 `GITHUB_TOKEN` 对仓库管理设置没有 `Administration: read`，访问 `GET /repos/{owner}/{repo}/immutable-releases` 返回 403 时，workflow 不能误报为“未启用 Release Immutability”。在不降低正式 Release 不可变性门禁的前提下，让维护者可以通过明确的本次人工确认继续发布，并保留可选管理员只读 Token 的机器预检路径和发布后的 `immutable=true` 机器验证。

# 成功标准

- [ ] Release workflow 区分 Immutability API 的 200 / 404 / 403 / 其他错误，不再把任意 API 失败都解释成“未启用”。
- [ ] 配置 `RELEASE_SETTINGS_TOKEN` 且具备仓库 `Administration: read` 时，Preflight 使用它机器验证仓库 Immutability 设置。
- [ ] 未配置管理员只读 Secret、默认 `GITHUB_TOKEN` 返回 403 时，只有本次 `workflow_dispatch` 明确确认 Immutability 已启用才允许继续；未确认时 fail closed。
- [ ] 若配置了 `RELEASE_SETTINGS_TOKEN` 但它仍返回 403，则 fail closed 并提示修正 Token 权限，不静默降级成人工确认。
- [ ] 机器可确认的 404 继续明确表示未启用并阻止正式构建。
- [ ] 发布后继续验证正式 Release API 返回 `immutable=true`；不删除或弱化 Draft→Publish→immutable 的既有链路。
- [ ] README 与 Runtime Release canonical Reference 同步解释新的权限边界和维护者操作方式。
- [ ] 不修改 Release 版本来源、三平台构建、正式资产集合、Runtime/Project Payload/MCP schema 或依赖。

# 范围

- 修复 `.github/workflows/release.yml` 的 Release Immutability Preflight。
- 增加永久 workflow preservation 回归。
- 同步维护者 README 与 Runtime/Release canonical Reference。

# 非目标

- 不自动创建、读取或管理 GitHub Actions Secret。
- 不赋予 `GITHUB_TOKEN` GitHub 平台并不存在的 Administration permission。
- 不关闭 Release Immutability 门禁。
- 不修改 Release v<SemVer> 版本语义、Runtime Builder 或正式发布资产。
- 不创建实际正式 Release；修复合入后由维护者重新手工运行 Release workflow。

# 必须保持不变

- Release 只能从 `main` 手工触发，tag 是唯一正式版本来源。
- 已存在 tag / Release 不覆盖、不移动。
- 三平台使用固定 Python 3.12.10 构建并验证同一 release_version。
- 正式资产先 Draft、上传并核对完整集合，再 Publish；发布后必须验证 tag、资产与 `immutable=true`。
- 发布失败清理仍只能自动删除未发布 Draft，不自动删除已发布 Release。

# 关键决策

采用双路径 Preflight：优先使用可选 `RELEASE_SETTINGS_TOKEN` 做 GitHub 官方 Administration-read API 机器验证；未配置时仍尝试默认 `GITHUB_TOKEN`，若因其固有权限边界得到 403，则要求 `workflow_dispatch` 的显式人工确认。这样无需强迫仓库新增长期 PAT 才能发布，同时 403 不再被伪装成 404；有更高权限 Secret 时仍获得发布前机器证明。发布后现有 `immutable=true` 校验继续作为最终机器事实。

GitHub 官方当前说明 `GET /repos/{owner}/{repo}/immutable-releases` 要求仓库 Administration(read)；200 表示已启用、404 表示未启用。因此默认仅有 Contents(read) 的 `GITHUB_TOKEN` 返回 403 属于权限边界而不是设置事实。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 修复 Release #4 的失败根因 | user:fix-release-4 | not_satisfied | 待 workflow 实现与回归 |
| R2 | Release Immutability 仍必须在正式发布流程中确认并保持 fail-closed | .agents/MAINTENANCE.md | not_satisfied | 待 preflight 状态分类、人工/机器确认和发布后验证 |
| R3 | Runtime/Release 现有版本、构建、资产与协议边界保持 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待永久回归与三平台 CI |
| R4 | Workflow 变更必须有责任审计与新鲜验证证据 | .agents/skills/coding/references/07_通用验证与证据策略.md | not_satisfied | 待 Red/Green、Review、Ready、永久 CI |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | workflow preservation test 覆盖 200/404/403 权限语义、人工确认和可选 Secret |
| 接口 / Contract | required | 保持 workflow_dispatch tag、Release identity、Draft/Publish/immutable 既有 Contract；新增确认输入为显式维护者交互 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改 Runtime 安装/持久化实现；永久 CI 的现有 Runtime 链继续回归 |
| 用户 / Workflow Acceptance | required | 维护者能从 Actions 手工 Release：无管理员 Secret 时明确确认；有 Secret 时机器验证 |
| 跨组件 Golden Path | required | 永久 CI 继续覆盖测试→onefile→真实 stdio MCP→project install；Release workflow 静态责任链保持完整 |
| External Dependency / Provider Probe | required | GitHub Release #4 日志与 GitHub 官方 API 权限/状态语义作为当前外部事实；不在普通 PR CI 真实发布 Release |
| Build / Package / Runtime | required | Linux/Windows/macOS 永久 Runtime package/install 全绿，证明 workflow 修复未破坏构建面 |
| Docs / Governance / Other | required | README/ref13/Change/Ready/独立 Review 与 main fresh CI |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户修复要求、当前分支 AGENTS、Maintenance、Router、Coding、ref07/ref13/ref14、Release workflow、README、目标测试和 Release #4 失败证据。
- [ ] change_coverage：确认 403 权限、404 未启用、可选 Secret、人工确认、发布后 immutable 验证和错误信息都有 Owner。
- [ ] reverse_audit：从维护者手工输入 v2.0.0 反查 preflight→tests/Ready→三平台→Draft→Publish→immutable；从错误权限/未启用设置反查不会误放行或误报。
- [ ] unresolved_cleared：所有 not_satisfied 清零；交付后置步骤只有明确 deferred。

# 任务

- [x] 调查 Release #4 日志、当前 workflow 与 GitHub 官方 Immutability API 权限事实。
- [ ] 新增 Release Immutability Preflight Red 回归并确认旧实现精确失败。
- [ ] 修复 workflow 并同步 ref13 / README。
- [ ] 跑永久测试与三平台 Runtime CI。
- [ ] 独立 Review、Completion Audit、Ready Check。
- [ ] 非 Draft PR 正常合并，main fresh CI 后删除 Active Change。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_runtime_release_hardening.py`
- 相关测试：全量 `.agents/skills/coding/tests/test_*.py`
- 构建：永久 Linux/Windows/macOS Runtime package/install
- External fact：Release #4 run `33300984482` + GitHub 官方 immutable-releases API 文档
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Release #4 run `33300984482`：Preflight 的 `gh api repos/.../immutable-releases` 返回 HTTP 403 `Resource not accessible by integration`，后续测试/三平台/Publish 全部 skipped。
- 尚未建立 Red/Green。

# 文档影响

- `README.md`：需要同步维护者 Release 操作与可选 Secret / 人工确认边界。
- `ref13`：需要同步正式 Release canonical 规则，不影响最终用户 `USAGE.md`。

# 交付

- Commit：待完成
- PR：待创建
- 发布：本任务不创建正式 Release；修复合入后可重新运行 `v2.0.0`，前提是 tag/Release 仍不存在。
