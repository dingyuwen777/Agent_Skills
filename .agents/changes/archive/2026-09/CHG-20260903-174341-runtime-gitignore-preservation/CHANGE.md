---
schema: coding-change/v1
id: CHG-20260903-174341-runtime-gitignore-preservation
title: 修复 Runtime 安装错误写入 gitignore
level: L3
status: done
owner: dingyuwen777
branch: fix/runtime-gitignore-preservation
created: 2026-09-03
updated: 2026-09-03
completion_gate: required
depends_on: []
affected_areas:
  - runtime-installation
  - project-bootstrap
  - gitignore-preservation
  - runtime-contract
  - ci-validation
affected_paths:
  - runtime/agent_skills_runtime/project_installer.py
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - runtime/README.md
  - .agents/skills/coding/tests/test_runtime_gitignore_install_contract.py
  - .github/workflows/runtime-package-tests.yml
  - .agents/changes/archive/2026-09/CHG-20260903-174341-runtime-gitignore-preservation/CHANGE.md
contracts:
  - Runtime project installation contract
  - target project .gitignore preservation
  - sidecarless installation ownership
  - Runtime Package installation acceptance
data_changes: []
---

# 目标

修复正式 Runtime binary 安装/升级会向目标项目 `.gitignore` 自动新增 `/.agents/runtime/` 的行为。安装器现在只继续幂等维护 Agent_Skills 自己的 `.agents/project-context.json` 本地缓存 ignore，不把 Runtime 目录变成自动忽略项；项目在安装前已经自行配置的 Runtime ignore 保持原样。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/191

实现 PR：https://github.com/dingyuwen777/Agent_Skills/pull/194

实现 merge SHA：`ee4b399e2efef5369e4c04126cbf951c4b05d03a`

# 最终实现

- 删除 installer 的 `RUNTIME_IGNORE_RULE`，`_updated_gitignore()` 只认领 `.agents/project-context.json` 缓存 ignore。
- 首次安装、重复安装均不自动新增 `/.agents/runtime/`。
- 项目安装前已经存在的 `/.agents/runtime/` 或等价 Runtime ignore 不删除、不重排、不重复追加；当前 `.gitignore` 没有逐行 ownership marker，不能猜它由旧 Agent_Skills 创建。
- `.agents/runtime/agent-skills[.exe]` 安装路径、Codex/Cursor/Claude Code MCP 配置、sidecarless install-state、legacy v3 一次迁移和 rollback 语义保持。
- ref12/ref13 与 `runtime/README.md` 同步新安装 Contract。
- `Runtime Package Tests` 保留必要的三平台 build/self-test/stdio MCP/project install 责任，只把旧的“Runtime ignore 必须存在”验收同步成“cache ignore 必须存在、Runtime ignore 不得由新安装产生”。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | AC1：首次安装不得新增 Runtime ignore | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC1 | satisfied | 永久回归覆盖 helper 与真实首次安装；final-head Runtime Package #383、implementation main-fresh #384 均在 Linux/Windows/macOS 真实 binary install 中验证 Runtime 文件存在而 `/.agents/runtime/` ignore 不存在 |
| R2 | AC2：缓存 ignore 与项目 `.gitignore` 保持 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC2 | satisfied | 永久回归用 CRLF 既有 `.gitignore` 证明原内容/换行前缀保持且 cache ignore 只追加一次；三平台 package install 验证 `.agents/project-context.json` ignore 存在 |
| R3 | AC3：已有 Runtime ignore 保持，不删除不重复 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC3 | satisfied | `test_existing_project_owned_runtime_ignore_is_preserved_not_owned` 在安装前已有 `/.agents/runtime/` 的临时项目上验证该行仍只出现一次 |
| R4 | AC4：Runtime/MCP/ownership/rollback 不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC4 | satisfied | final-head #383 与 main-fresh #384 三平台均通过 onefile build/self-test、real stdio MCP、显式安装/重复安装/无参数安装、installed Runtime 与 install-state；永久回归核对 Cursor MCP 仍指向 `.agents/runtime/agent-skills.exe` |
| R5 | AC5：canonical Runtime/Bootstrap 契约同步 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC5 | satisfied | 当前 ref12/ref13 明确“不自动新增 Runtime ignore”“项目原本已有则保持”，`.gitignore` 自动 ownership 收窄为本地缓存 ignore |
| R6 | AC6：Runtime README 同步 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC6 | satisfied | `runtime/README.md` 与 installer/canonical Contract 同步，永久回归禁止旧“Runtime 应加入 gitignore”语义回归 |
| R7 | AC7：永久回归先 Red 后 Green | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC7 | satisfied | Red Skill Tests #1085 / run `33740937173`：413 项仅 5 个新契约 failure；Green/final-head self-contained 414 项全绿，保护性断言保留并增加 package workflow Contract 回归 |
| R8 | AC8：完整 CI 与独立 Review | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC8 | satisfied | A1/A2 `NO_FINDINGS_WITHIN_SCOPE`；final-head `4f2378d8...` 的 Skill Tests #1093 / `33742732167` success，Runtime Package #383 / `33742732136` 三平台与 Gate success；review threads=0 |
| R9 | AC9：merge/main/archive/closure/cleanup | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC9 | explicitly_deferred | guarded implementation merge 已完成，main-fresh Skill #1094 / `33743021502` 与 Runtime #384 / `33743021522` success；本 Change 因 implementation main-fresh 已满足而进入 `done`/archive，归档 PR merge、archive-main fresh、Issue checklist/closure 与任务分支 cleanup 继续由 Post-Merge Finalization 承担，不能在本归档文件中预写未来证据 |

# Red / Green 证据

## Red

Red head `e63a0a3d2f205202f8355ee72c950d1a5c5d158b` 只加入 Change 与永久回归，没有改生产实现/canonical Contract。

Skill Tests #1085 / run `33740937173`：Requirement Source success；self-contained 413 项中 5 个 failure，全部直接对应旧契约：helper 自动加入 Runtime ignore、首次安装加入 Runtime ignore、已有 CRLF 项目也被追加 Runtime ignore、installer 仍保留 `RUNTIME_IGNORE_RULE`、canonical 文本仍要求 Runtime ignore。项目原本已有 Runtime ignore 的保持测试已经通过。

## Green 与 CI Contract Drift

实现删除 `RUNTIME_IGNORE_RULE`，`_updated_gitignore()` 只维护 `.agents/project-context.json`；ref12/ref13/runtime README 同步。

第一次 Green 后 Runtime Package #378 暴露永久 package Workflow 仍正向执行 `grep -Fq "/.agents/runtime/"`。build/self-test/MCP 已成功，失败发生在旧项目安装验收断言。这被作为 CI Contract drift 修复，而不是降低产品实现或删除 package 门禁。

干净 Green head `c3bdbb3c04b8f7195c27bac1da416ecf6ccfa4c1`：Skill Tests #1092 self-contained 414 项全绿；Runtime Package #382 / `33742290144` 的 Linux/Windows/macOS 与 Gate 全部 success。

# Independent Review

A1 Requirement→Implementation：从 #191 AC1–AC9 反查最终实现，AC1–AC3 由 installer + 安装级永久回归直接覆盖；AC4 由真实三平台 Runtime Package install/MCP/install-state 覆盖；AC5–AC6 由 ref12/ref13/Runtime README 覆盖；AC7 有真实 Red；AC8 exact final-head 证据完整；AC9 的 archive/closure 生命周期未提前冒充完成。

A2 Implementation→Evidence：从最终 diff 反查，installer 只移除 Runtime-ignore ownership，没有修改 `.agents/runtime/agent-skills[.exe]` 目标路径、Host MCP 构造、install-state/legacy migration/rollback；已有 Runtime ignore 没有删除路径。Runtime Package Workflow 没有减少验证责任，只把旧正向 ignore 断言替换为 cache-present/runtime-ignore-absent，并在 POSIX/Windows、显式/无参数安装上证明新 Contract。临时 patch/sync Workflow 均未进入最终产品 diff。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

# Final-head 验证

Ready head：`4f2378d8b77655cf29965c4e40166688274b106a`。

- Skill Tests #1093 / run `33742732167`：success，Requirement Source、414 项 self-contained、changed Change Ready、Agent Skills Gate 均成功。
- Runtime Package Tests #383 / run `33742732136`：success，Scope=package，Linux/Windows/macOS onefile build/self-test、real stdio MCP、project install 与 Runtime Package Gate 全部成功。
- 合并前 PR head/base 未漂移，mergeable=true，review threads=0。

# 实现合并与 Main-fresh 验证

PR #194 使用 `expected_head_sha=4f2378d8b77655cf29965c4e40166688274b106a` guarded merge。

实现 merge SHA / main revision：`ee4b399e2efef5369e4c04126cbf951c4b05d03a`。

`main@ee4b399e...` fresh CI：

- Skill Tests #1094 / run `33743021502`：success；
- Runtime Package Tests #384 / run `33743021522`：success；Linux/Windows/macOS build/self-test/real stdio MCP/project install 与 Runtime Package Gate 全部成功。

只有取得以上 implementation main-fresh evidence 后，本 Change 才更新为 `done` 并进入 archive。

# Validation Matrix

| 验证层 | 结论 |
| --- | --- |
| Red | satisfied；#1085 精确证明旧行为缺口 |
| 行为 / Unit / Component | satisfied；414 项 self-contained + 首次/重复/CRLF/既有 Runtime ignore/helper/canonical/workflow 回归 |
| 接口 / Contract | satisfied；ref12/ref13、installer、Runtime Package 永久验收一致 |
| 集成 / 持久化 / Runtime Dependency | satisfied；真实临时项目文件写入、MCP 配置、install-state、三平台 binary install |
| 用户 / Workflow Acceptance | satisfied；三平台真实安装证明 Runtime 存在而新 `.gitignore` 不含 Runtime ignore |
| 跨组件关键路径 | satisfied；Builder → onefile → self-test → stdio MCP → install/reinstall/no-args install → installed MCP |
| External Provider Probe | not_applicable；无业务第三方 Provider |
| Build / Package / Runtime | satisfied；final-head #383 与 implementation main-fresh #384 三平台全绿 |
| Docs / Governance | satisfied through implementation finalization；#191、L3 Change、ref12/ref13、Runtime README、Review、PR/merge/main-fresh 已完成；archive PR/Issue Closure 继续由 finalization 承担 |

# Workflow Responsibility Audit

本任务修改 `.github/workflows/runtime-package-tests.yml`，但没有新增/删除永久 Workflow。该 Workflow 继续是 `Runtime Package Gate` 的必要 package/platform Owner；三平台 build/self-test/MCP/install 与 Gate 均保留并实际 Green。本次仅同步其安装验收到新的 `.gitignore` Contract，没有以减少 Workflow 或跳过平台验证换取 Green。

# Completion Audit

- [x] upstream_re_read：已重新读取 #191、installer、ref12/ref13、Runtime README、Runtime Package Workflow、PR #194 final head、implementation main 与 fresh CI。
- [x] change_coverage：AC1–AC8 有直接实现/运行 Evidence；AC9 的归档 PR、archive-main、Issue Closure/cleanup 有 Post-Merge Finalization Owner。
- [x] reverse_audit：Runtime 路径、MCP、install-state/legacy migration/rollback、项目自有 `.gitignore` 未被扩大修改；临时 Workflow 未进入 main。
- [x] unresolved_cleared：实现/测试/canonical/CI Contract/Review/merge/main-fresh 无 blocker；只剩归档 PR 自身与 Requirement/branch finalization。

# 任务

- [x] 调查当前 installer、canonical Runtime/Bootstrap 规则与测试事实
- [x] 建立 L3 Requirement Source 与 Change
- [x] 建立并验证 Red
- [x] 完成最小实现
- [x] 同步 canonical Runtime/Bootstrap 与 Runtime README
- [x] 同步 Runtime Package 永久安装验收并完成三平台 Green
- [x] 完成独立 A1/A2 Review 与 Completion Audit
- [x] PR exact final-head fresh CI
- [x] guarded implementation merge
- [x] implementation main-fresh CI
- [x] 本 Change 更新为 `done` 并进入 archive carrier
- [ ] 归档 PR merge / archive-main fresh / #191 Closure Audit / branch cleanup

# 文档影响

- `runtime/README.md` required，已同步。
- `USAGE.md` 经 targeted search 未承担 Runtime ignore 契约，本次不修改。

# 交付边界

- Release/tag：not_applicable；用户仅要求源码修复并合并 main，本任务不创建新 Release/tag。
- Deploy：not_applicable。
