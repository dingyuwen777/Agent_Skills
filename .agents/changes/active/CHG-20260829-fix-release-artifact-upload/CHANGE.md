---
schema: coding-change/v1
id: CHG-20260829-fix-release-artifact-upload
title: 修复 Release artifact 上传失败
level: L2
status: in_progress
owner: ChatGPT
branch: fix/release-artifact-upload
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - release
  - ci
  - tests
affected_paths:
  - ".github/workflows/release.yml"
  - ".agents/skills/coding/tests/test_release_productization.py"
contracts:
  - "Runtime binary Release asset contract"
data_changes: []
---

# 目标

修复手工 Release Workflow 在 Linux、Windows、macOS 三个平台完成 Runtime 构建与验证后，因为把待上传文件放在隐藏目录 `.release-assets/`，而 `actions/upload-artifact` 默认 `include-hidden-files: false` 导致找不到文件并失败的问题。

# 成功标准

- [ ] 三个平台生成的待上传 Runtime binary 放在非隐藏发布目录中。
- [ ] 三个平台 `actions/upload-artifact` 的 `path` 与实际生成目录一致，不依赖 `include-hidden-files: true` 绕过默认安全行为。
- [ ] 保持最终 GitHub Release 的三个 binary 文件名、`USAGE.md`、`SHA256SUMS`、版本校验、不可覆盖 tag/Release 等现有 Contract 不变。
- [ ] 增加回归测试，防止 Release Workflow 再次把上传源放回隐藏目录。
- [ ] PR 永久 CI 全绿后才进入 Ready；本 Change 不直接重跑或创建正式 Release。

# 范围

- 修改 `.github/workflows/release.yml` 的临时发布资产目录。
- 修改 Release productization 回归测试。
- 记录本次失败运行与修复验证证据。

# 非目标

- 不修改 Runtime 构建逻辑、Project Payload、Reference Bundle、MCP Contract 或 installer。
- 不升级 `actions/upload-artifact`、`actions/download-artifact` 或其他依赖版本。
- 不改变 Release 输入 tag、VERSION、最终资产命名和 Release Notes 行为。
- 不自动重新触发正式 Release。

# 必须保持不变

- Release 仍只允许从 `main` 手工运行并输入 `v<VERSION>`。
- Linux、Windows、macOS 构建、自检、真实 stdio MCP smoke 与项目安装验证继续保留。
- 最终 Release 仍只发布三平台 binary、`USAGE.md` 与 `SHA256SUMS`。
- 已存在 tag/Release 继续 fail closed，不覆盖、不移动。

# 已确认关键决策

采用最小方案：把构建 Job 中的 `.release-assets/` 改为非隐藏 `release-assets/`。不设置 `include-hidden-files: true`，因为这些文件本来就是明确待发布资产，不需要隐藏路径；同时避免扩大 upload-artifact 对隐藏内容的包含范围。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 修复 Release #1 的实际失败根因 | user:2026-08-29-fix-release | not_satisfied | run 33232571749：三平台 Build/verify 成功，Upload step 均报 `No files were found with the provided path: .release-assets/...`。 |
| R2 | 保持现有 Release 产品 Contract 不变 | `.agents/MAINTENANCE.md` / ref14 / 当前 `release.yml` | not_satisfied | 待回归测试与 PR CI 证明。 |
| R3 | Bug 修复需有回归测试并验证 Red→Green | `coding/references/05_设计实施与根因调试.md` | not_satisfied | 先补测试并在 PR CI 观察失败，再修改 workflow。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | `test_release_productization.py` 增加上传目录回归断言，先 Red 后 Green。 |
| 接口 / Contract | required | 保持三个 binary 文件名、`USAGE.md`、`SHA256SUMS` 及手工不可变 Release Contract。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 本修复不改变 Runtime/存储/外部运行依赖；原 Release #1 已证明三平台 Runtime 构建与安装验证本身成功。 |
| 用户 / Workflow Acceptance | required | PR CI 解析并验证永久 workflow；正式 Release 仅在合并后由用户手工触发。 |
| 跨组件 Golden Path | not_applicable | 本 Change 只修复 artifact staging/upload 路径，不改变 Runtime 内部跨组件链。 |
| External Dependency / Provider Probe | not_applicable | 不需要第三方业务 Provider；GitHub Actions 行为已有失败日志与 action contract 证据。 |
| Build / Package / Runtime | required | PR 永久 CI 必须继续完成现有 onefile build/self-test/MCP/install 责任。 |
| Docs / Governance / Other | required | Change、Ready Check、PR Review/CI 证据。 |

# Completion Audit

- [ ] upstream_re_read：重新核对用户修复请求、Release #1 日志和当前 Release Contract。
- [ ] change_coverage：确认只修复隐藏目录上传根因，没有遗漏三平台路径。
- [ ] reverse_audit：检查 `build → staging path → upload-artifact path → download → final release-assets` 全链一致。
- [ ] unresolved_cleared：Requirement Traceability 不再存在 `not_satisfied`。

# 实施任务

1. [Red] 在 `test_release_productization.py` 增加回归测试，要求构建上传源使用非隐藏 `release-assets/`，并确认当前 workflow 因 `.release-assets/` 失败。
2. [Green] 只把 Linux/Windows/macOS 构建 Job 的 `.release-assets/` 与 upload `path` 改为 `release-assets/`。
3. 运行 PR 永久 CI，复核 Release Workflow Responsibility：触发、三平台 build/verify、artifact handoff、最终 publish 责任不变。
4. 完成两阶段 Review、Ready Check 与 Completion Audit；满足门禁后再决定是否合并。

# 当前证据

- Release run `33232571749`：`Validate Release Request` 成功；Linux/Windows/macOS 的 `Build and verify ... single binary` 成功；三个 `Upload ... binary` 全部失败。
- Linux job `99047839436` 明确报错：`No files were found with the provided path: .release-assets/agent-skills-mcp-v*-linux`。
- 当前锁定的 `actions/upload-artifact@043fb46...` 定义 `include-hidden-files` 默认值为 `false`。

# 文档影响

`README.md`、`USAGE.md`、`runtime/README.md` 不受影响：最终用户命令、资产名称和 Runtime 行为均不改变，仅修复 Workflow 内部临时目录。

# Git / PR / Release 状态

- branch: `fix/release-artifact-upload`
- PR: 待创建
- merge: 未执行
- main CI: 未执行
- Release: 不在本 Change 内自动触发
