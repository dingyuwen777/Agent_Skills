---
schema: coding-change/v1
id: "CHG-20260830-release-immutability-preflight-auth"
title: "修复 Release Immutability 预检鉴权边界"
level: L3
status: ready_for_review
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
  - "正式 Release fail-closed 与 Immutability 机器确认流程"
data_changes: []
---

# 目标

修复 Release #4 暴露的 Immutability 预检鉴权错误：GitHub Actions 默认 `GITHUB_TOKEN` 对仓库管理设置没有 `Administration: read`，访问 `GET /repos/{owner}/{repo}/immutable-releases` 返回 403 时，workflow 不能误报为“未启用 Release Immutability”。正式 Release 必须在任何三平台构建和 Publish 之前使用最小权限的管理员只读 Secret **机器确认** Immutability 已启用；不能把人工勾选或口头确认作为不可变性前置证明。

# 成功标准

- [x] Release workflow 区分 Immutability API 的 200 / 404 / 403 / 其他错误，不再把任意 API 失败解释成“未启用”。
- [x] 正式 Release 必须配置仓库 Actions Secret `RELEASE_SETTINGS_TOKEN`；缺失时在三平台构建前 fail closed。
- [x] `RELEASE_SETTINGS_TOKEN` 只需要当前仓库 `Administration: read`，只用于 Preflight 读取 Immutability 设置；不用于 tag、资产上传或 Publish。
- [x] API 返回 403 时明确提示 `RELEASE_SETTINGS_TOKEN` 权限不足并停止，不降级为人工确认。
- [x] API 返回 404 时明确表示当前仓库未启用 Release Immutability 并停止。
- [x] 只有 API 返回 200 且响应 `enabled=true` 才允许继续完整测试、Ready、三平台构建和发布。
- [x] 发布后继续验证正式 Release API 返回 `immutable=true`；Draft→Publish→immutable 与 Draft-only cleanup 既有链路不弱化。
- [x] README 与 Runtime Release canonical Reference 已同步新的权限边界和维护者操作方式。
- [x] Release 版本来源、三平台构建、正式资产集合、Runtime/Project Payload/MCP schema 与依赖均未修改。

# 范围

- 修复 `.github/workflows/release.yml` 的 Release Immutability Preflight。
- 增加永久 workflow preservation / security 回归。
- 同步维护者 README 与 Runtime/Release canonical Reference。

# 非目标

- 不自动创建、读取或管理 GitHub Actions Secret。
- 不赋予 `GITHUB_TOKEN` GitHub 平台不存在的 Administration permission。
- 不关闭或绕过 Release Immutability 门禁。
- 不提供人工确认 fallback；不可变性必须在 Publish 前机器确认。
- 不修改 Release `v<SemVer>` 版本语义、Runtime Builder 或正式发布资产。
- 本变更不创建实际正式 Release；合入后由维护者配置 Secret 并重新手工运行 Release workflow。

# 必须保持不变

- Release 只能从 `main` 手工触发，tag 是唯一正式版本来源。
- 已存在 tag / Release 不覆盖、不移动。
- 三平台使用固定 Python `3.12.10` 构建并验证同一 `release_version`。
- 正式资产先 Draft、上传并核对完整集合，再 Publish；发布后必须验证 tag、资产与 `immutable=true`。
- 发布失败清理仍只能自动删除未发布 Draft，不自动删除已发布 Release。
- 管理员只读 Secret 不提升 Publish Job 权限；实际发布仍由现有 `github.token` + `contents: write` 承担。

# 关键决策

最终采用**机器预检唯一放行路径**：正式 Release 必须配置 `RELEASE_SETTINGS_TOKEN`，推荐使用只授权 `dingyuwen777/Agent_Skills` 且 Repository permission 仅为 `Administration: Read-only` 的 fine-grained PAT。Preflight 使用该 Secret 调用 GitHub 官方 Immutability 设置 API；Secret 缺失、403、404、网络/API 异常或 200 但 `enabled!=true` 都在正式构建前失败关闭。

初始 Green 曾设计为“可选管理员 Secret + 默认 GITHUB_TOKEN 403 时人工勾选确认”。独立 Review 发现该方案不能证明 fail-closed：如果人工确认错误而 Immutability 实际未启用，workflow 会先把 Draft Publish，再在发布后 `immutable=true` 校验时失败；此时仓库已经留下一个公开、可变 Release，而既有安全清理逻辑按设计不会删除已发布 Release。因此人工 fallback 被删除并加入永久回归禁止恢复。

GitHub 官方当前文档确认 `GET /repos/{owner}/{repo}/immutable-releases` 要求仓库 `Administration: read`；200 表示已启用且示例响应 `enabled=true`，404 表示未启用。Release #4 的默认 Token 只有普通仓库读取权限，403 只能证明鉴权不足，不能当成设置状态。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 修复 Release #4 的失败根因和错误提示 | user:fix-release-4 | satisfied | Release #4 `33300984482` 403 根因已复现；workflow 改为专用 Admin-read Secret 并区分 200/404/403/其他状态；Initial Red/Green 与 Review Red/Green 均有证据 |
| R2 | Release Immutability 必须在 Publish 前机器确认并保持 fail-closed | .agents/MAINTENANCE.md | satisfied | 人工 fallback 已因 Review Finding 删除；永久测试要求 Secret 缺失/403/404 均失败且禁止 `confirm_immutable_releases`；发布后 `immutable=true` 复核继续保留 |
| R3 | Runtime/Release 现有版本、构建、资产与协议边界保持 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | 最终 clean run `33302620838`：181 tests、Linux onefile/真实 MCP/project install、Windows/macOS package/install 全部 Green；未改 Runtime Python、版本来源、资产集合或协议 |
| R4 | Workflow 变更必须完成责任审计、独立 Review 与新鲜验证 | .agents/skills/coding/references/07_通用验证与证据策略.md | satisfied | Workflow Responsibility Audit 完成；HIGH Finding 已 Red→Green 修复；最终 re-review `NO_FINDINGS_WITHIN_SCOPE`；clean run `33302620838` 产品链全绿 |
| R5 | 按仓库门禁完成非 Draft PR、merge、main fresh CI 与 Active Change 清理 | .agents/MAINTENANCE.md | explicitly_deferred | 必须发生在最终 Ready HEAD CI 之后；当前不得在 merge 前伪报完成 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 永久 `test_runtime_release_hardening.py` 覆盖强制 Secret、200/404/403、禁止人工 fallback、YAML run block 缩进、发布后 immutable 和 Draft-only cleanup；最终 181 tests Green |
| 接口 / Contract | required | workflow_dispatch 仍仅 `tag`；Release identity、Draft/Publish/immutable Contract 保持；新增仓库 Secret 是维护者安全前置，不进入 Runtime 公共协议 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改 Runtime 安装/持久化实现；现有 Runtime 链在永久 CI 全量回归 |
| 用户 / Workflow Acceptance | required | 维护者必须先配置 `RELEASE_SETTINGS_TOKEN` 并启用 Release Immutability；之后仍只输入 `v<SemVer>` 手工发布；README 已同步 |
| 跨组件 Golden Path | required | `33302620838` 覆盖 tests→onefile→真实 stdio MCP→project install；Release workflow 静态回归保持 preflight→tests/Ready→三平台→Draft→Publish→immutable |
| External Dependency / Provider Probe | required | Release #4 实际 403 日志 + GitHub 官方 immutable-releases API 当前文档确认 Administration(read)、200 enabled / 404 disabled；普通 PR 不真实 Publish Release |
| Build / Package / Runtime | required | `33302620838`：Linux onefile/MCP/install、Windows package/install、macOS package/install 全部成功 |
| Docs / Governance / Other | required | README/ref13/Change 已同步；独立 Review/re-review 完成；最终 Ready Check 待 ready_for_review HEAD 新鲜 CI |

# Workflow Responsibility Audit

- 旧责任：Release preflight 在正式构建前确认 Immutability 已启用。
- 旧故障：默认 `GITHUB_TOKEN` 无 Administration(read)，403 被通用 `||` 分支错误翻译为“未启用”。
- 新责任：Preflight 使用只读 Admin Secret 机器读取设置，并对 Secret 缺失、403、404、未知状态分别失败；只有 200 + `enabled=true` 放行。
- Evidence Preservation：全量测试、Ready、三平台构建、identity、Draft 资产校验、Publish 后 tag/asset/immutable 验证、Draft-only cleanup 全部保留。
- 权限隔离：`RELEASE_SETTINGS_TOKEN` 不进入 Publish Job，不代替 `github.token` 写 Release；只解决一个只读管理设置 API 的最小权限需求。

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取用户修复要求、当前 feature 根 AGENTS、Maintenance、Router、Coding、ref07/ref13/ref14、Release workflow、README、目标测试、最终 PR diff 和 Release #4 失败证据；并复核 GitHub 官方 immutable-releases API 当前权限/状态语义。
- [x] change_coverage：403 权限、404 未启用、Secret 缺失、200 enabled、未知/API 错误、发布后 immutable、Draft-only cleanup 和维护者配置说明均有 Owner。
- [x] reverse_audit：从维护者输入 `v2.0.0` 反查为 Secret machine preflight→tests/Ready→三平台→Draft→Publish→immutable；从 Secret 缺失/权限错/设置关闭反查均在构建前停止，不产生正式 Release。
- [x] unresolved_cleared：R1–R4 satisfied；R5 仅保留必须发生在 Ready 之后的正式交付生命周期 `explicitly_deferred`；无 `not_satisfied`。

# 任务

- [x] 调查 Release #4 日志、当前 workflow 与 GitHub 官方 Immutability API 权限事实。
- [x] 新增 Initial Red：旧实现精确暴露 403 鉴权/状态分类缺口。
- [x] 初始 Green 修复 403 误报并同步 workflow/ref13/README。
- [x] 独立 Review 发现人工确认可能先 Publish mutable Release 的 HIGH Finding，并建立 Review Red。
- [x] 收紧为 mandatory `RELEASE_SETTINGS_TOKEN` 机器预检；目标 Release-hardening 回归 Green。
- [x] 删除全部一次性 patch workflow/script，最终 PR 仅保留正式文件。
- [x] 最终 clean run `33302620838`：181 tests、Linux/Windows/macOS 产品链全部 Green，唯一 Job 失败为 Change 当时仍 `proposed` 的预期 Ready Gate。
- [x] 完成 re-review 与 Completion Audit，结论 `NO_FINDINGS_WITHIN_SCOPE`。
- [ ] 最终 `ready_for_review` HEAD 永久 CI 全绿后，处理 Draft→Ready/安全非 Draft 替代 PR 并正常合并；main fresh CI 后删除 Active Change。

# 独立 Review

Review Target：`main@6f5c582e99a304ef1d0c0d2781e7acfb7ff6b6c2 → fix/release-immutability-preflight-auth`。

模式：review-and-fix。

Finding：**HIGH — 人工 Immutability 确认不能保证正式 Release fail-closed**。

- 条件：未配置 Admin-read Secret，默认 `GITHUB_TOKEN` 返回 403；维护者误勾选确认，但仓库实际没有启用 Immutability。
- 旧初始 Green 行为：Preflight 放行，三平台构建成功后创建 Draft 并 Publish；之后才检查 Release API `.immutable == true`。
- 影响：公开 Release 已经创建且可变；现有 cleanup 出于安全边界只删除仍为 Draft 的 Release，不删除已发布 Release，因此仓库会留下违反正式不可变交付契约的公开 Release。
- 修复：删除人工确认 input / env / 403 fallback，强制使用只读 Admin Secret 在正式构建前机器确认；永久测试明确禁止恢复 manual fallback。
- Review Green：Runner 生成 commit `3d233f8ba396441209254bc66bf695a80478d976`，9 条 Release-hardening 回归全部通过，`git diff --check` 通过；GitHub Actions 自带 Token 仅因缺少 `workflows` permission 无法 push workflow 文件，随后由已连接 GitHub App 对同一已验证 commit 做普通非 force fast-forward。
- 最终 re-review：machine-only clean diff 未发现新的 BLOCKER/HIGH/MEDIUM；Secret 只在 Preflight 读取设置、Publish 权限没有扩大、所有既有 Release 证据链和失败边界保留。结论 `NO_FINDINGS_WITHIN_SCOPE`。

# 验证

## 新鲜证据

- Release #4 run `33300984482`：Preflight 调用 immutable-releases API 返回 HTTP 403 `Resource not accessible by integration`，后续测试/三平台/Publish 全部 skipped。
- Initial Red run `33301515574`：181 tests 中只有新增 Immutability 鉴权回归失败，原有 180 条通过。
- 初始 manual-fallback clean run `33302016250`：181 tests、Linux onefile/MCP/install、Windows/macOS package/install 均通过；Job 唯一失败为 Change 仍 `proposed` 的 Ready Gate。该实现随后因独立 Review HIGH Finding 被废弃。
- Review Red run `33302206596`：181 tests 中只有新的“必须机器预检”回归失败，其他 180 条通过。
- Machine-only target Green run `33302426944` / job `99232912126`：补丁后的 9 条 Release-hardening 回归全部通过；`git diff --cached --check` 通过；仅最终 push 因 GitHub Actions Token 无 `workflows` permission 被 GitHub 拒绝，代码本身未失败。
- Machine-only verified commit：`3d233f8ba396441209254bc66bf695a80478d976`；只修改 `release.yml`、README、ref13，之后两个一次性 patch 文件已删除。
- Final clean pre-Ready run `33302620838`：181 tests OK；Linux onefile/status/self-test/真实 stdio MCP/project install 成功；Windows/macOS package/install 成功；唯一失败为当时 Active Change `proposed` 的 Ready Check。

# 文档影响

- `README.md`：已同步 `RELEASE_SETTINGS_TOKEN` 的创建原则、用途、最小权限和失败边界。
- `ref13`：已同步正式 Release canonical 机器预检规则。
- `USAGE.md`：最终用户不负责维护源仓库 Release，因此不需要变化。

# Contract / Schema / Migration / 依赖

- Release workflow_dispatch：仍只有 `tag`，无新增版本输入或人工安全旁路。
- Runtime Bundle / Project Payload / install manifest / MCP / Task Route / Routing Manifest：不变。
- Schema / Migration / 数据：无。
- 直接依赖：无变化。

# 交付

- Branch：`fix/release-immutability-preflight-auth`
- Draft PR：#57
- Release：本任务不创建正式 Release；修复完成后如果 `v2.0.0` tag/Release 仍不存在，可在配置 Secret 和启用 Immutability 后重新运行。
