---
schema: coding-change/v1
id: CHG-20260829-fix-release-artifact-upload
title: 修复 Release artifact 上传失败
level: L2
status: ready_for_review
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

- [x] 三个平台生成的待上传 Runtime binary 放在非隐藏发布目录中。
- [x] 三个平台 `actions/upload-artifact` 的 `path` 与实际生成目录一致，不依赖 `include-hidden-files: true` 绕过默认安全行为。
- [x] 保持最终 GitHub Release 的三个 binary 文件名、`USAGE.md`、`SHA256SUMS`、版本校验、不可覆盖 tag/Release 等现有 Contract 不变。
- [x] 增加回归测试，防止 Release Workflow 再次把上传源放回隐藏目录。
- [x] 完成功能、三平台 Package/Runtime、Review 与 Completion Audit 后进入 Ready；进入 Ready 后必须由新一轮 PR 永久 CI 验证 Change Ready Gate 全绿，才允许合并。本 Change 不直接重跑或创建正式 Release。

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
| R1 | 修复 Release #1 的实际失败根因 | user:2026-08-29-fix-release | satisfied | Release run `33232571749` 证明三平台 Build/verify 均成功而 Upload 均因 `.release-assets/...` 找不到文件失败；当前 diff 将三平台 staging 与 upload path 同步改为可见 `release-assets/...`。 |
| R2 | 保持现有 Release 产品 Contract 不变 | `.agents/MAINTENANCE.md` / `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md` / `.github/workflows/release.yml` | satisfied | PR diff 只修改三平台 staging/upload path；`test_release_publishes_three_binaries_usage_and_checksums`、`test_release_workflow_is_manual_and_immutable` 在 Green run `33233124852` 中通过；最终汇总目录、三平台文件名、`USAGE.md`、`SHA256SUMS`、VERSION/tag 与不可覆盖逻辑均未改变。 |
| R3 | Bug 修复需有回归测试并验证 Red→Green | `.agents/skills/coding/references/05_设计实施与根因调试.md` | satisfied | Red run `33233059615`：132 tests 中仅新增 `test_release_upload_sources_are_not_hidden` 失败，明确命中 `.release-assets`；Green run `33233124852`：132 tests 全部通过，包括该回归测试。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33233059615` 精确复现新增回归断言失败；Green run `33233124852` 的 132 个 self-contained tests 全部通过，新回归测试证明三平台 staging 与 upload path 不再使用隐藏目录。 |
| 接口 / Contract | required | Green run `33233124852` 中 Release productization 既有 Contract 测试继续通过；PR diff 复核确认三个 binary 名称、`USAGE.md`、`SHA256SUMS`、手工 main Release、VERSION/tag 和不可覆盖语义不变。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 本修复不改变数据库、文件持久化、Runtime dependency 或 installer 语义；实际受影响边界是 GitHub Actions artifact staging/upload path，由原失败日志、锁定 action contract 与 workflow 回归覆盖。 |
| 用户 / Workflow Acceptance | required | 原 Release run `33232571749` 提供真实 workflow 失败证据；Green run `33233124852` 验证修改后的永久 workflow 文件与所有现有 Release contract 测试。正式 `workflow_dispatch` 仍只允许 main 且会创建不可变 Release，因此不在 PR 阶段为测试而触发；合并后需由用户按正式流程手工运行。 |
| 跨组件 Golden Path | not_applicable | 本 Change 不改变 Runtime 内部组件接线，且既有 Linux/Windows/macOS 项目安装链已在 Green run `33233124852` 继续通过；artifact 上传本身是单一 Workflow handoff 边界，不需要新增另一条应用 Golden Path。 |
| External Dependency / Provider Probe | not_applicable | 不依赖第三方业务 Provider。`actions/upload-artifact` 的默认隐藏文件行为已由 Release #1 实际失败和当前锁定 action contract 共同确认；不需要额外外部 Probe。 |
| Build / Package / Runtime | required | Green run `33233124852`：Linux onefile build/status/self-test、真实 stdio MCP、项目安装均成功；`Runtime Windows Package` 成功；`Runtime macOS Package` 成功。Runtime `source_digest` / `payload_digest` 与失败 Release 构建保持一致，说明本 Change 未改变 Runtime 内容 Contract。 |
| Docs / Governance / Other | required | 独立 A1/A2、反向审计与代码质量 Review 已完成，结论 `NO_FINDINGS_WITHIN_SCOPE`；Green run `33233124852` 唯一失败是本 Change 当时仍为 `in_progress` 的 Ready Gate，当前已依据真实证据进入 `ready_for_review`，由 run `33233883147` 重新验证最终 Ready Gate。 |

# Completion Audit

- [x] upstream_re_read：重新核对用户“修复一下”的授权、Release #1 `33232571749` 原始日志、当前 `.github/workflows/release.yml`、Maintenance/ref14/ref15 的 Release Contract 与完成边界。
- [x] change_coverage：三平台 Linux/Windows/macOS 的 staging 创建、binary copy 与 `actions/upload-artifact path` 均覆盖；没有遗漏最终 download/aggregate/publish 路径，也没有扩大到 Runtime 实现。
- [x] reverse_audit：按 `build → staging path → upload-artifact path → download-artifact → final release-assets → GitHub Release` 反向复核；前三个平台改为同一可见目录，最终 download/publish 仍使用既有 `release-assets`，资产名称保持一致。
- [x] unresolved_cleared：R1–R3 均为 `satisfied`；所有 `not_applicable` 均有当前任务边界依据；正式不可变 Release 的真实重跑明确保留到合并后用户手工触发，不把未授权发布伪装成 PR 验证。

# TDD / 实施与验证证据

1. Red：在 `.agents/skills/coding/tests/test_release_productization.py` 增加 `test_release_upload_sources_are_not_hidden`。
2. Verify Red：PR CI run `33233059615` 执行 132 tests，只有新增测试失败，失败原因是 workflow 仍包含 `.release-assets`；其余 131 tests 通过。
3. Green：仅把 Linux/Windows/macOS 构建 Job 的 staging 与 upload path 从 `.release-assets` 改成 `release-assets`。
4. Verify Green：PR CI run `33233124852` 的 132 tests 全部通过；Linux build/self-test/MCP/install 全部通过；Windows/macOS Package 与项目安装 Job 全部通过。
5. Governance checkpoint：run `33233124852` 的 `Skill Tests` 最后只因 Active Change 状态仍为 `in_progress` 而失败，错误明确要求 `ready_for_review`；这不是代码/Runtime/平台回归。当前依据上述证据完成 Completion Audit 并进入 `ready_for_review`，由 run `33233883147` 验证最终 Ready Gate。

# Review

Review Target：PR #29，base `188d174c970eea1676fe64d6923f669eb0f583f6`，实现 head `c83aade2f0f71d2928bac523c2b6d9e88def3b36`（后续提交只更新本 Change 的验证记录，不改变 workflow/test 实现）。

模式：review-only 独立复核。

## A1 上游要求 → Change

- 用户要求修复 Release #1；Change 已覆盖真实失败根因、三平台路径、回归测试和不可变 Release Contract。
- 没有发现遗漏的 Runtime、业务、文档或依赖需求；本任务不授权为了测试创建正式 tag/Release。

## A2 Change → 实现 / 测试 / 文档

- `.github/workflows/release.yml` 只修改 Linux/Windows/macOS staging/copy/upload path，未改变最终发布资产、版本、权限或 tag/Release 语义。
- 回归测试经历正确 Red→Green，并同时保留既有 Release contract tests。
- Green CI 继续证明三平台 onefile/package/install 能力，没有证据显示 Runtime 内容发生变化。
- `README.md`、`USAGE.md`、`runtime/README.md` 无事实变化，因此不修改文档。

## 第二阶段：代码质量 / Workflow Responsibility Audit

- 触发仍为 `workflow_dispatch`，只允许 main；未扩大触发范围。
- Linux/Windows/macOS build/verify 责任保持；只修正 handoff staging path。
- `actions/upload-artifact` name、最终 asset filename 与 downstream `download-artifact` pattern 保持一致。
- 没有新增依赖、权限、Secret、外部写入或无关重构。
- 新回归测试直接断言本次失效机制：任何 `.release-assets` 回归都会失败，并校验三平台 copy/upload path 成对一致。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

未验证边界：尚未在修复后真实执行 main 的手工 Release workflow，因此“GitHub 实际接收三平台 artifacts 并创建最终 Release”尚未由 post-fix 发布运行证明。原因是该 workflow 会创建不可变 tag/Release，PR 阶段不应为了测试产生正式发布副作用。该边界必须在本 PR 合并、main 新鲜 CI 通过后，由用户按正式流程手工触发 Release 验证。

# 文档影响

`README.md`、`USAGE.md`、`runtime/README.md` 不受影响：最终用户命令、资产名称和 Runtime 行为均不改变，仅修复 Workflow 内部临时目录。

# Git / PR / Release 状态

- branch: `fix/release-artifact-upload`
- PR: `#29` Draft；当前 Ready 状态已触发 PR CI run `33233883147`，全绿后再转 Ready
- merge: 未执行
- main CI: 未执行；只有合并后才能取得 main 新鲜证据
- Release: 未触发；本 Change 不自动创建 tag/Release
