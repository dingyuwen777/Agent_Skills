---
schema: coding-change/v1
id: CHG-20260829-fix-release-checksum-generation
title: 修复 Release SHA256SUMS 生成失败
level: L2
status: done
owner: ChatGPT
branch: fix/release-checksum-generation
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
  - "Release checksum asset contract"
data_changes: []
---

# 目标

修复 Release #2 在三平台 Runtime artifact 均成功上传并被最终 Job 下载后，`Generate SHA256SUMS` 因输出文件 `SHA256SUMS` 在 `find` 扫描前已被 Shell 重定向创建，导致把自身纳入 checksum、最终生成 5 行而触发 `test ... -eq 4` 失败的问题。

# 成功标准

- [x] `Generate SHA256SUMS` 只对三个 Runtime binary 和 `USAGE.md` 四个正式资产计算 SHA256。
- [x] `SHA256SUMS` 自身不会进入 checksum 输入集合。
- [x] 目录中的其他临时文件不会被静默纳入 checksum。
- [x] checksum 文件恰好 4 行，每个正式资产各出现一次。
- [x] 不改变三平台 binary 文件名、`USAGE.md`、Release notes、tag/VERSION、不可覆盖 Release 等现有 Contract。
- [x] 增加真实执行 workflow checksum Shell 片段的回归测试，并完成 Red→Green。
- [x] 完成 A1/A2、Workflow Responsibility Audit、测试充分性 re-review、Ready CI、非 Draft PR CI、feature merge 和 main 新鲜 CI。
- [x] 通过独立 archive 分支完成 active→archive 字节级移动并将 Change 标记为 `done`；归档 PR 仍需自身永久 CI、merge 与最终 main CI 后才完成仓库级清理。

# 范围

- 修改 `.github/workflows/release.yml` 的 `Generate SHA256SUMS` step。
- 修改 Release productization 回归测试，使其真实执行该 step 的 Shell 脚本。
- 记录 Release #2 与修复验证证据。

# 非目标

- 不修改 Runtime build、MCP、Project Payload、installer 或三平台 artifact 上传逻辑。
- 不升级 GitHub Actions、Python、Runtime 或其他依赖。
- 不改变 Release 输入 tag、最终资产命名、Release notes 或不可变发布策略。
- 不在开发/PR 阶段创建正式 tag/Release。

# 必须保持不变

- Release 仍只允许从 `main` 手工运行并输入 `v<VERSION>`。
- Linux、Windows、macOS 的 build/self-test/MCP/install/upload 责任继续保留。
- 最终 GitHub Release 仍只包含三个 binary、`USAGE.md`、`SHA256SUMS`。
- 已存在 tag/Release 继续 fail closed，不覆盖、不移动。

# 已确认关键决策

采用显式资产白名单生成 checksum，而不是继续扫描整个 `release-assets/` 目录：`agent-skills-mcp-v${RELEASE_VERSION}-linux`、`agent-skills-mcp-v${RELEASE_VERSION}-windows.exe`、`agent-skills-mcp-v${RELEASE_VERSION}-macos`、`USAGE.md`。这样 `SHA256SUMS` 和任何未来临时文件都不会被静默纳入 checksum。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 修复 Release #2 的 checksum 实际失败根因 | user:2026-08-29-fix-release-checksum | satisfied | Release run `33234762483` 三平台 upload/download 均成功，最终只在 `Generate SHA256SUMS` exit code 1；合入 main 的实现不再扫描目录，而是显式传入四个正式资产。 |
| R2 | 保持现有 Release 产品 Contract 不变 | `.github/workflows/release.yml` | satisfied | feature diff 只修改 `Generate SHA256SUMS`；触发、main/tag/VERSION、三平台 build/upload、asset filename、`USAGE.md`、`gh release create`、不可覆盖检查均未改变；feature PR #33 与 main run `33235520945` 均保持三平台永久门禁绿色。 |
| R3 | Bug 修复需有真实行为回归并验证 Red→Green | `.agents/skills/coding/references/05_设计实施与根因调试.md` | satisfied | Red run `33235084203`：133 tests 中仅新增 checksum 真实执行测试失败；后续 Green/Ready/PR/main runs 均为 133 tests success，并实际断言四个正式资产各一次、`SHA256SUMS` 与 `unexpected.tmp` 均不进入 checksum。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33235084203` 精确复现 Shell exit 1；Ready run `33235338275`、非 Draft PR run `33235448273`、main run `33235520945` 均 133 tests success；新增测试直接执行 workflow 的真实 `Generate SHA256SUMS` run block。 |
| 接口 / Contract | required | Release productization tests 继续锁定三个 binary、`USAGE.md`、`SHA256SUMS`、Release notes、main/tag/VERSION 与不可覆盖语义；feature diff 未改变这些边界。 |
| 集成 / Persistence / Runtime Dependency | required | 新增测试使用临时真实文件系统 + Bash + `sha256sum` 执行 workflow Shell，覆盖重定向、文件读取和 checksum 输出真实语义；不是 Mock。 |
| 用户 / Workflow Acceptance | required | Release #2 `33234762483` 是真实失败证据；feature PR 与 main 永久 CI 验证修复后的 workflow 逻辑。正式 `workflow_dispatch` 会创建不可变 Release，因此留给用户在最终 main 稳定后手工运行。 |
| 跨组件 Golden Path | not_applicable | 本 Change 不改变 Runtime 组件接线；Release #2 已真实证明三平台 artifact upload→final download handoff 成功，当前缺陷只在 final Job checksum 子步骤。 |
| External Dependency / Provider Probe | not_applicable | 不依赖第三方业务 Provider；GitHub artifact 上传/下载边界已经由 Release #2 的真实运行证明。 |
| Build / Package / Runtime | required | Ready run `33235338275`、非 Draft PR run `33235448273`、main run `33235520945` 均证明 Linux onefile/status/self-test、真实 stdio MCP、项目安装，以及 Windows/macOS package/install success。 |
| Docs / Governance / Other | required | A1/A2、Workflow Responsibility Audit、测试充分性 re-review、Completion Audit、Ready Gate、非 Draft PR、feature merge、main fresh CI 和独立 archive 分支均已执行；archive PR/final main CI 作为归档收尾门禁。 |

# Completion Audit

- [x] upstream_re_read：重新核对用户修复授权、Release #2 `33234762483` 完整失败日志、当前 Release Workflow、Maintenance、Coding ref05/ref07/ref14/ref15 与 Review 规则。
- [x] change_coverage：根因、四个正式 checksum 资产、自包含污染、额外临时文件污染、现有 Release Contract 与测试缺口均已覆盖；没有扩大到 Runtime/上传实现。
- [x] reverse_audit：按 `三平台 upload → final download → include USAGE → validate assets → checksum → gh release create → published asset verification` 反向复核；只修改 checksum 子步骤，前后 handoff 名称保持一致。
- [x] unresolved_cleared：R1–R3 全部 `satisfied`；`not_applicable` 均有当前任务边界依据；无开放 Review Finding。

# TDD / 实施与验证证据

1. Red：新增 `_extract_workflow_run_block` 与 `test_release_checksum_step_hashes_only_expected_assets`，直接从 `release.yml` 提取 `Generate SHA256SUMS` 的 Shell 正文并执行。
2. Verify Red：run `33235084203` 执行 133 tests，只有新增 checksum 测试失败，`result.returncode == 1`；其余 132 tests 全部通过，和 Release #2 同形。
3. Green：`Generate SHA256SUMS` 增加 `RELEASE_VERSION` env、`set -euo pipefail`，使用显式四资产数组调用 `sha256sum`，不再 `find` 整个目录。
4. Verify Green：run `33235120350` 的 133 tests 全通过；Linux onefile/MCP/install、Windows/macOS package/install 均成功；唯一失败为当时 Change 仍 `in_progress` 的预期 Ready Gate。
5. Re-review test gap：为临时目录加入 `unexpected.tmp`，证明显式资产白名单不会把未来临时文件纳入 checksum。
6. Re-verify：run `33235230471` 的 133 tests、Linux onefile/MCP/install、Windows/macOS package/install 全部成功；唯一失败仍为当时 `in_progress` Ready Gate。
7. Ready：HEAD `8a84b9e52d7c96b7a2cb2c1667c631884619df63` 的 run `33235338275` 三个 Job 全部 success，Active Change Ready Gate success。
8. Draft→Ready 连接器故障：Draft PR #32 在 mutation 时再次遇到 GitHub 连接器 GraphQL `Repository.fullDatabaseId` 字段错误；未绕过 Draft 门禁，#32 关闭未合并。
9. 非 Draft PR：使用完全相同的 HEAD 创建 PR #33；run `33235448273` 三个 Job 全部 success。
10. Feature merge：PR #33 正常 merge，merge commit `68d0bd9ee0241fee1a1bc0808e86888d4b6112a9`。
11. Feature main fresh CI：run `33235520945` 三个 Job 全部 success。

# 独立 Review

Review Target：Draft PR #32 / 替代非 Draft PR #33，base `518ba7c89036120b2e7f9906b747314c8343bf4b`，最终 feature HEAD `8a84b9e52d7c96b7a2cb2c1667c631884619df63`。生产实现 commit `4d821f28ead2da51fc89541ca584052df6fd3b5b`；后续只强化测试与治理证据。

模式：review-and-fix 后 re-review；用户已明确授权修复 Release #2。

## A1 上游要求 → Change

- 用户要求按已确认方案修复 Release #2；Change 覆盖实际 checksum 根因、真实行为回归、Release Contract 保持与完整交付门禁。
- 用户未授权为了测试创建正式 tag/Release；不可变发布保持为最终 main 稳定后人工触发边界。
- 未发现需要修改 Runtime、上传 artifact、版本、用户文档或依赖的上游要求。

## A2 Change → 实现 / 测试 / 文档

- workflow 只修改 `Generate SHA256SUMS`：输入从目录扫描收敛为四个正式资产，避免输出自包含和额外临时文件污染。
- 新回归测试执行 workflow 的真实 Shell，而不是仅检查字符串；经历正确 Red→Green。
- 现有静态 Contract tests 与三平台 package/install 在 feature PR 和 main 均继续通过。
- `README.md`、`USAGE.md`、`runtime/README.md` 的用户/维护事实没有变化，因此无需修改。

## Workflow Responsibility Audit / Evidence Preservation

- Trigger：仍只有 `workflow_dispatch`，仍要求 `main` 与 `v<VERSION>`。
- Preflight：VERSION、tag/Release 不可覆盖、Ready Check 未变。
- Build：Linux/Windows/macOS build/self-test/MCP/install 未变。
- Artifact handoff：三平台 upload name/path 与 final `download-artifact pattern` 未变。
- Final validation：四个正式基础资产存在性检查未变。
- Checksum：从“不受控目录发现”改成“正式资产白名单”，证据更强且不改变输出文件名 `SHA256SUMS`。
- Publish：`gh release create`、目标 SHA、标题、notes、五个 published asset 校验未变。
- Permissions/dependencies：无新增权限、Secret、Action 或依赖版本变化。

测试充分性 re-review：最初 Green 后发现“额外临时文件排除”未被行为测试主动制造；已回到 Coding 补 `unexpected.tmp` 并重新验证。当前无剩余高价值测试缺口。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

未验证边界：修复后的正式 `workflow_dispatch` 尚未执行，因此“最终 `gh release create` 已实际成功创建 v1.0.0”仍未被 feature/main CI 证明。该操作会创建不可变 tag/Release，保持为最终仓库收尾后用户手工运行。

# 文档影响

Docs Impact：`not_applicable`。`README.md`、`USAGE.md`、`runtime/README.md` 不受影响：最终用户资产名称、下载/安装/使用方式与 Runtime 行为均不改变，仅修复 Release 内部 checksum 生成逻辑。

# Git / PR / Release 状态

- feature branch: `fix/release-checksum-generation`
- Draft PR: `#32`，关闭未合并，仅因连接器 Draft→Ready mutation 缺陷被替代
- Feature PR: `#33`，已合并
- Feature merge: `68d0bd9ee0241fee1a1bc0808e86888d4b6112a9`
- Feature main CI: run `33235520945` success
- Archive branch: `chore/archive-fix-release-checksum-generation`
- active→archive 原始移动：原 Active blob 与初始 Archive blob 均为 `3a65a7defd26692ff6b303e08f662a7ca0d7eeaa`，字节级守恒
- Archive PR: 待创建
- Release: 未触发；正式 `v1.0.0` 保持用户手工运行
