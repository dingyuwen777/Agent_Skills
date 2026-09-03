---
schema: coding-change/v1
id: CHG-20260903-174341-runtime-gitignore-preservation
title: 修复 Runtime 安装错误写入 gitignore
level: L3
status: ready_for_review
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
  - .agents/changes/active/CHG-20260903-174341-runtime-gitignore-preservation/CHANGE.md
contracts:
  - Runtime project installation contract
  - target project .gitignore preservation
  - sidecarless installation ownership
  - Runtime Package installation acceptance

data_changes: []
---

# 目标

修复正式 Runtime binary 安装/升级会向目标项目 `.gitignore` 自动新增 `/.agents/runtime/` 的行为。安装器以后只继续幂等维护 Agent_Skills 自己的本地缓存 ignore，不把 Runtime 目录变成自动忽略项；项目在安装前已经自行配置的 Runtime ignore 保持原样，不因本次修复被删除。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/191

实现 PR：https://github.com/dingyuwen777/Agent_Skills/pull/194

# 成功标准

- [x] 新项目首次安装后 `.gitignore` 不出现安装器新增的 `/.agents/runtime/`。
- [x] `.agents/project-context.json` 缓存 ignore 仍幂等维护，项目原有 `.gitignore` 内容与换行保持。
- [x] 项目原本已有 Runtime ignore 时保持原样，不删除、不重复。
- [x] Runtime 安装路径、宿主 MCP 配置、sidecarless ownership、回滚和三平台 package/install 不回归。
- [x] canonical Runtime/Bootstrap 规则与 `runtime/README.md` 同步为新契约。

# 范围

- Runtime installer 的 `.gitignore` 增量编辑行为；
- Runtime / Bootstrap canonical 安装规则；
- Runtime 维护说明；
- 永久安装回归；
- 三平台 Runtime Package 的真实安装验收断言同步。

# 非目标

- 不改变 `.agents/runtime/agent-skills[.exe]` 的安装路径；
- 不改变 Codex/Cursor/Claude Code 项目 MCP 配置路径；
- 不删除目标项目安装前已有的 `/.agents/runtime/` ignore；
- 不改变 Project Payload、Bundle、MCP Tool Contract、Release ZIP 结构或二进制名称；
- 不创建新 Release/tag；
- 不为历史版本增加新的兼容层。

# 必须保持不变

- `.agents/project-context.json` 仍是 Agent_Skills 本地缓存 ignore，并保持幂等；
- `.gitignore` 既有项目内容、换行风格和项目自有 Runtime ignore 均不得被重排/删除；
- `.agents/runtime/agent-skills[.exe]` 仍安装并校验当前 artifact；
- existing AGENTS/CLAUDE/Codex/Cursor 配置、sidecarless ownership、legacy v3 一次迁移和 rollback 保护不降低。

# 关键决策

1. 不再定义/追加 Runtime ignore；Runtime binary 是否被项目版本控制由项目 Owner 自己决定。
2. 不做旧 Runtime ignore 的自动迁移删除。当前 `.gitignore` 没有逐行 Agent_Skills ownership marker，无法安全证明已存在的 `/.agents/runtime/` 来自旧安装器；删除会侵犯项目自有规则。
3. Installer 仍会在需要时创建/增量更新 `.gitignore`，但只为 `.agents/project-context.json` 缓存规则服务。
4. Runtime Package Tests 原本仍正向断言 `/.agents/runtime/` 必须出现。Green 后第一次三平台 package 验收因此正确暴露 CI Contract drift；最终把永久 Workflow 同步为“cache ignore 存在 + Runtime ignore 不存在”，同时继续验证真实 onefile Runtime、MCP、安装路径和 install-state，而不是删除 package 验收。
5. 临时 patch/sync Workflow 只服务受限宿主写入，最终均已从 PR diff 删除，不增加第四个永久 Workflow。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | AC1：首次安装不得新增 Runtime ignore | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC1 | satisfied | 永久回归 `test_gitignore_helper_adds_cache_only_for_new_file` 与真实 `install_project()` 首次安装均断言 Runtime ignore 不存在；三平台 Runtime Package #382 真实 binary install 同样通过该断言 |
| R2 | AC2：缓存 ignore 与项目 `.gitignore` 保持 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC2 | satisfied | CRLF 既有 `.gitignore` 回归证明原 bytes 前缀/CRLF 保持且 cache ignore 只出现一次；三平台 package 明确验证 cache ignore 存在 |
| R3 | AC3：已有 Runtime ignore 保持，不删除不重复 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC3 | satisfied | `test_existing_project_owned_runtime_ignore_is_preserved_not_owned` 以安装前已有 `/.agents/runtime/` 的真实临时项目验证该行仍只出现一次且 cache ignore 正常补充 |
| R4 | AC4：Runtime/MCP/ownership/rollback 不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC4 | satisfied | Runtime Package #382 Linux/Windows/macOS 均完成 onefile build/self-test、real stdio MCP、显式安装/重复安装/无参数安装与 install-state 检查；永久回归还核对 Cursor MCP 命令仍指向 `.agents/runtime/agent-skills.exe` |
| R5 | AC5：canonical Runtime/Bootstrap 契约同步 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC5 | satisfied | ref12/ref13 当前 diff 明确“不自动新增 Runtime ignore”“项目原本已有则保持”，并把 `.gitignore` 自动 ownership 收窄到本地缓存 ignore |
| R6 | AC6：Runtime README 同步 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC6 | satisfied | `runtime/README.md` 已同步相同契约，永久回归禁止旧“Runtime 应加入 gitignore”表述回归 |
| R7 | AC7：永久回归先 Red 后 Green | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC7 | satisfied | Red Skill Tests #1085 / run `33740937173`：413 项中只有 5 个新契约 failure；Green head `c3bdbb3...` Skill Tests #1092 self-contained 全部通过，共 414 项；新增 package-workflow 回归没有删除保护性断言 |
| R8 | AC8：完整 CI 与独立 Review | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC8 | explicitly_deferred | A1/A2 Review 已完成且 `NO_FINDINGS_WITHIN_SCOPE`；Green package #382 全绿。当前 Ready commit 产生后必须由 PR #194 取得 exact final-head fresh Skill Tests + Runtime Package，不能复用 pre-ready head |
| R9 | AC9：merge/main/archive/closure/cleanup | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC9 | explicitly_deferred | 用户已授权合并 main；PR #194 final-head Green 后由 Post-Merge Finalization 执行 guarded merge、main-fresh、Change archive、archive-main fresh、Issue checklist 写回/重读/close/再读和分支清理 |

# Red / Green Evidence

## Red

Red head `e63a0a3d2f205202f8355ee72c950d1a5c5d158b` 只加入 Change 与永久回归，没有改生产实现/canonical Contract。

Skill Tests #1085 / run `33740937173`：Requirement Source success；self-contained 413 项中 5 个 failure，全部直接对应旧契约：helper 自动加入 Runtime ignore、首次安装加入 Runtime ignore、已有 CRLF 项目也被追加 Runtime ignore、installer 仍保留 `RUNTIME_IGNORE_RULE`、canonical 文本仍要求 Runtime ignore。项目原本已有 Runtime ignore 的保持测试已经通过。

## Green 与 CI Contract Drift

实现删除 `RUNTIME_IGNORE_RULE`，`_updated_gitignore()` 只维护 `.agents/project-context.json`；ref12/ref13/runtime README 同步。

Green head `84b88448...` 的 Skill Tests #1088：self-contained 全绿；仅 Change 仍为 `in_progress` 被 changed Change Ready Check 阻止。

同一阶段 Runtime Package #378 暴露旧 package Workflow 仍执行正向 `grep -Fq "/.agents/runtime/"`。Linux/macOS build/self-test/MCP 已成功，失败发生在旧安装验收断言。这被认定为 CI Contract drift，而不是放宽产品实现。

最终干净 Green head `c3bdbb3c04b8f7195c27bac1da416ecf6ccfa4c1`：

- Skill Tests #1092 / run `33742290135`：Requirement Source success，414 项 self-contained 全部通过；唯一失败是本 Change 仍处于 `in_progress` 的 Ready gate，符合预期；
- Runtime Package #382 / run `33742290144`：Scope=package，Linux/Windows/macOS 均 success，Runtime Package Gate success；三平台均验证 build/self-test/real stdio MCP/project install，并以新契约检查 cache ignore 存在、Runtime ignore 不存在。

# Independent Review

A1 Requirement→Implementation：重新读取 #191 AC1–AC9，从上游要求反查最终 7 文件 diff。AC1–AC3 由 installer + 安装级永久回归直接覆盖；AC4 由真实三平台 Runtime Package install/MCP/install-state 覆盖；AC5–AC6 由 ref12/ref13/Runtime README 当前正文覆盖；AC7 保留真实 Red；AC8/AC9 的 final-head 与 merge 后生命周期没有提前冒充完成。

A2 Implementation→Evidence：从最终 diff 反查，installer 只移除 Runtime-ignore ownership，没有修改 `.agents/runtime/agent-skills[.exe]` 目标路径、Host MCP 构造、install-state/legacy migration/rollback；已有 Runtime ignore 没有删除路径。Runtime Package Workflow 没有减少验证责任，只把旧的正向 ignore 断言替换为 cache-present/runtime-ignore-absent，并在 Windows/POSIX、显式/无参数安装上增加新契约。临时 Workflow 不在最终 diff。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。无 BLOCKER/HIGH/需要阻塞 Ready 的 MEDIUM。

# Validation Matrix

| 验证层 | 状态 | 范围 / Evidence |
| --- | --- | --- |
| Red | satisfied | #1085 / `33740937173` 精确证明旧实现/规则缺口 |
| 行为 / 单元 / 组件 | satisfied | 414 项 self-contained Green；新安装/重复安装/已有 CRLF/已有 Runtime ignore/helper/canonical/workflow 永久回归通过 |
| 接口 / 契约 | satisfied | ref12/ref13 与 installer 同步；Runtime Package 永久断言同步 |
| 集成 / 持久化 / 运行依赖 | satisfied | 临时真实项目文件写入、MCP 配置、install-state、三平台 binary install |
| 用户 / 工作流验收 | satisfied | Linux/Windows/macOS 真实 Runtime 安装均证明 Runtime 文件存在而 `.gitignore` 不新增 Runtime ignore |
| 跨组件关键路径 | satisfied | Builder → onefile → self-test → stdio MCP → install/reinstall/no-args install → installed MCP |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖第三方业务 Provider 或生产服务 |
| 构建 / 打包 / 运行 | satisfied | Runtime Package #382 全平台 + Gate success |
| 文档 / 治理 / 其他 | satisfied | #191、L3 Change、ref12/ref13、Runtime README、独立 A1/A2；PR final-head/merge 后生命周期由 R8/R9 正式 Owner 承担 |

# Workflow Responsibility Audit

本任务修改 `.github/workflows/runtime-package-tests.yml`，但没有新增/删除永久 Workflow。该 Workflow 仍是 Ruleset 所需 `Runtime Package Gate` 的唯一 package/platform Owner，分类保持 `necessary`。修改只同步其项目安装验收到新 Runtime Contract；Linux/Windows/macOS build/self-test/MCP/install 与 Gate 全部保留并实际 Green，因此不存在为了通过本修复而降低 CI 充分性的情况。

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取 #191、当前 installer、ref12/ref13、Runtime README、Runtime Package Workflow 与最终 PR diff；目标与实现一致。
- [x] change_coverage：AC1–AC7 已有直接实现/运行 Evidence；AC8 final-head 与 AC9 merge 后 lifecycle 分别有 PR/Post-Merge Finalization 正式 Owner，没有无主延期。
- [x] reverse_audit：从最终 7 文件 diff 反查 Runtime 路径、MCP、install-state/legacy migration/rollback、项目自有 `.gitignore` 没有被扩大修改；临时 Workflow 已退出 diff。
- [x] unresolved_cleared：实现/测试/canonical/CI Contract/Review 无 blocker；只剩必须发生在 Ready commit 之后的 fresh final-head CI 和 merge 后生命周期。

# 任务

- [x] 调查当前 installer、canonical Runtime/Bootstrap 规则与测试事实
- [x] 建立 L3 Requirement Source 与 Change
- [x] 建立并验证 Red
- [x] 完成最小实现
- [x] 同步 canonical Runtime/Bootstrap 与 Runtime README
- [x] 同步 Runtime Package 永久安装验收并完成三平台 Green
- [x] 完成独立 A1/A2 Review 与 Completion Audit
- [x] 更新 Change 为 `ready_for_review`
- [ ] PR Ready exact-head fresh CI
- [ ] guarded merge、main-fresh、归档、Issue Closure、分支清理

# 文档影响

- `runtime/README.md` required，已同步。
- `USAGE.md` 经 targeted search 未承担 Runtime ignore 契约，本次不修改。

# 交付

- 实现 PR：https://github.com/dingyuwen777/Agent_Skills/pull/194
- Release/tag：not_applicable；本任务只交付源码和验证，不创建新 Release/tag。
