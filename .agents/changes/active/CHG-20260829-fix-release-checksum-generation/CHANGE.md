---
schema: coding-change/v1
id: CHG-20260829-fix-release-checksum-generation
title: 修复 Release SHA256SUMS 生成失败
level: L2
status: in_progress
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

- [ ] `Generate SHA256SUMS` 只对三个 Runtime binary 和 `USAGE.md` 四个正式资产计算 SHA256。
- [ ] `SHA256SUMS` 自身不会进入 checksum 输入集合。
- [ ] checksum 文件恰好 4 行，每个正式资产各出现一次。
- [ ] 不改变三平台 binary 文件名、`USAGE.md`、Release notes、tag/VERSION、不可覆盖 Release 等现有 Contract。
- [ ] 增加真实执行 workflow checksum Shell 片段的回归测试，并完成 Red→Green。
- [ ] PR 永久 CI、Review、main 新鲜 CI 和独立 Change 归档完成后才结束；本 Change 不自动重新触发正式 Release。

# 范围

- 修改 `.github/workflows/release.yml` 的 `Generate SHA256SUMS` step。
- 修改 Release productization 回归测试，使其真实执行该 step 的 Shell 脚本。
- 记录 Release #2 与修复验证证据。

# 非目标

- 不修改 Runtime build、MCP、Project Payload、installer 或三平台 artifact 上传逻辑。
- 不升级 GitHub Actions、Python、Runtime 或其他依赖。
- 不改变 Release 输入 tag、最终资产命名、Release notes 或不可变发布策略。
- 不在 PR 阶段创建正式 tag/Release。

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
| R1 | 修复 Release #2 的 checksum 实际失败根因 | user:2026-08-29-fix-release-checksum | not_satisfied | Release run `33234762483`：三平台 upload 全成功，最终 Job 在 `Generate SHA256SUMS` exit code 1；日志显示当前命令先重定向创建 `SHA256SUMS`，再用 `find` 扫描同目录。 |
| R2 | 保持现有 Release 产品 Contract 不变 | `.github/workflows/release.yml` | not_satisfied | 待回归测试、diff Review 与 PR CI 证明。 |
| R3 | Bug 修复需有真实行为回归并验证 Red→Green | `.agents/skills/coding/references/05_设计实施与根因调试.md` | not_satisfied | 先增加提取并真实执行 checksum step 的测试，确认当前 workflow Red，再最小修改 workflow。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 回归测试真实执行 `Generate SHA256SUMS` Shell，当前实现先 Red，修复后要求 4 行且不包含 `SHA256SUMS` 自身。 |
| 接口 / Contract | required | 三个平台 binary 名、`USAGE.md`、`SHA256SUMS`、Release notes、VERSION/tag/不可覆盖语义保持。 |
| 集成 / Persistence / Runtime Dependency | required | 使用临时真实文件系统运行 workflow Shell，验证重定向、文件枚举和 `sha256sum` 的真实语义。 |
| 用户 / Workflow Acceptance | required | Release #2 提供真实 workflow 失败证据；PR 阶段验证永久 workflow，不为测试创建不可变正式 Release。 |
| 跨组件 Golden Path | not_applicable | 本 Change 不改变 Runtime 组件接线；三平台 artifact→final Job handoff 已由 Release #2 成功 download 证明。 |
| External Dependency / Provider Probe | not_applicable | 不依赖第三方业务 Provider；GitHub artifact 上传/下载在 Release #2 已成功。 |
| Build / Package / Runtime | required | 永久 CI 必须继续证明 Linux onefile/MCP/install 及 Windows/macOS package/install，不得因 checksum 修复破坏现有 Release Runtime 能力。 |
| Docs / Governance / Other | required | Change、Workflow Responsibility Audit、独立 Review、Ready Gate、PR/main CI 与归档。 |

# Completion Audit

- [ ] upstream_re_read：重新核对用户修复授权、Release #2 完整失败日志与当前 Release Contract。
- [ ] change_coverage：确认只修复 checksum 输入集合与对应回归测试，没有遗漏最终发布资产链。
- [ ] reverse_audit：按 `download artifacts → include USAGE → validate assets → checksum → gh release create` 反向复核。
- [ ] unresolved_cleared：Requirement Traceability 不再存在 `not_satisfied`。

# 实施任务

1. [Red] 增加测试，提取当前 workflow 的 `Generate SHA256SUMS` `run:` 内容，在临时目录创建四个正式资产并真实执行，确认当前实现失败。
2. [Green] 将 checksum 输入改为显式四资产列表，不扫描输出目录，也不把 `SHA256SUMS` 自身纳入输入。
3. 跑永久 CI，复核 workflow 触发、三平台构建上传、artifact handoff、checksum、最终 publish 责任没有被削弱。
4. 完成独立 Review、Ready Check、PR 合并、main 新鲜 CI 与独立归档。

# 当前证据

- Release run `33234762483`：`Validate Release Request` success；Linux/Windows/macOS build/verify/upload 全部 success；三个 artifacts 均成功下载到最终 Job。
- `Validate release identity and assets` success，说明四个正式资产均存在。
- `Generate SHA256SUMS` 执行 `find . -maxdepth 1 -type f ... | xargs sha256sum > SHA256SUMS` 后，紧接的 4 行断言失败，step exit code 1。
- `Create immutable GitHub Release` 因上一步失败被 skipped；当前 `v1.0.0` tag/Release 均未创建。

# 文档影响

`README.md`、`USAGE.md`、`runtime/README.md` 不受影响：最终用户资产名称、下载/安装/使用方式与 Runtime 行为均不改变，仅修复 Release 内部 checksum 生成逻辑。

# Git / PR / Release 状态

- branch: `fix/release-checksum-generation`
- PR: 待创建
- merge: 未执行
- main CI: 未执行
- Release: 不在本 Change 内自动触发
