---
schema: coding-change/v1
id: CHG-20260903-133655-runtime-binary-agent-skills
title: 统一 Runtime 二进制命名为 agent-skills
level: L3
status: done
owner: dingyuwen777
branch: chg/runtime-binary-agent-skills
created: 2026-09-03
updated: 2026-09-03
completion_gate: required
depends_on: []
affected_areas:
  - runtime-product-name
  - project-installer
  - release-packaging
  - maintenance-governance
affected_paths:
  - scripts/build_runtime.py
  - scripts/runtime_mcp_smoke.py
  - runtime/agent_skills_runtime/project_installer.py
  - runtime/agent_skills_runtime/server.py
  - .github/workflows/runtime-package-tests.yml
  - .github/workflows/release.yml
  - USAGE.md
  - runtime/README.md
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/tests/
contracts:
  - Agent Skills Runtime binary name
  - Agent Skills 三平台 Release ZIP contract
data_changes: []
---

# 目标

把 Agent_Skills 当前所有 live Runtime 二进制表面从旧基础名统一为 `agent-skills`，同时保持三个按平台拆分的 Release ZIP 名称、数量、Draft/Publish 流程和“binary + USAGE.md”两项成员结构不变。Windows 当前版本使用 `agent-skills.exe`，Linux/macOS 当前版本使用 `agent-skills`；项目安装路径、Codex/Cursor/Claude Code command、Builder 默认产物、Runtime Package CI 和 Release build/zip 成员全部一致。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/181

实现 PR：https://github.com/dingyuwen777/Agent_Skills/pull/182

本次明确不提供旧二进制名 alias、fallback、双写、迁移探测或旧版本升级兼容。Maintenance 已固化：Agent_Skills 自身后续修改默认以当前目标版本干净安装和当前版本行为为验收基线；只有 Requirement Source 明确要求时才承担跨版本升级兼容。

# 采用方案

Runtime 当前产品 basename 固定为：

```text
Windows: agent-skills.exe
Linux/macOS: agent-skills
```

Builder 默认产物、目标项目 `.agents/runtime/` 安装路径、Codex/Cursor/Claude Code 项目配置、Runtime Package CI、Release build artifact 与最终 ZIP 内 binary 使用同一 basename。

Linux 与 macOS 最终 binary 同名后，Release workflow 不再把三个 Actions artifact 扁平 merge 到同一目录，而是保留 `release-runtime-linux` / `release-runtime-windows` / `release-runtime-macos` 子目录再分别校验与打包。该调整只解决内部同名碰撞；外部 Release 契约保持：

```text
agent-skills-v<SemVer>-linux.zip   -> agent-skills + USAGE.md
agent-skills-v<SemVer>-windows.zip -> agent-skills.exe + USAGE.md
agent-skills-v<SemVer>-macos.zip   -> agent-skills + USAGE.md
```

没有改变三个 ZIP 的数量、文件名规则、根目录两项成员、tag 驱动版本、identity/SHA 校验、Draft/Publish 流程或正式 Release 资产集合。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Builder、Installer、宿主配置和 live 规则统一使用 agent-skills | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | `test_runtime_binary_product_name` + 389 项 self-contained 回归 + PR/main package CI |
| R2 | Windows 安装为 .agents/runtime/agent-skills.exe，Linux/macOS 为 .agents/runtime/agent-skills | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | PR final-head Runtime Package #337 / run `33722393935` 与 main-fresh #338 / run `33722605842` 三平台项目安装、status/self-test、stdio MCP 全部成功 |
| R3 | Release 仍精确三个 agent-skills-v<SemVer>-<platform>.zip，每包仍只有 binary + USAGE.md | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | Release productization/platform ZIP 永久回归在 final-head Skill #1047 与 main-fresh Skill #1048 通过；Release workflow 外层 ZIP 契约未改 |
| R4 | 不新增旧名兼容层，不验证旧安装升级 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | live 旧名扫描回归通过；最终实现未新增旧名 alias、fallback、双文件或迁移探测 |
| R5 | Maintenance 固化 Agent_Skills 默认不承担跨版本升级兼容义务 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | Maintenance preservation 回归通过；规则明确只有显式 Requirement 才增加兼容/迁移层 |
| R6 | MCP/Bundle/Project Payload schema、Python/依赖和 Release 打包方式不发生无关变化 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | changed-files 不含协议/Schema/requirements；389 项既有 Runtime/路由/Release 回归和三平台 package identity 均通过 |
| R7 | 完整 Skill Tests、三平台 Runtime Package、独立 Review、guarded merge 与 main-fresh 闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | explicitly_deferred | 实现 PR #182 已 guarded merge，implementation main-fresh #1048/#338 已成功；当前归档 PR 自身的 merge/final-main-fresh 与随后 Issue Closure/branch cleanup 由 finalization 流程执行，避免 archived Change 自引用 |

# Red 与实现证据

Red head `f483307a675a746e1f52215153641c2b2e28b59e` 建立 Runtime `agent-skills` 命名契约。Skill Tests #1035 / run `33719759904` 在旧实现上按预期失败，证明旧 `agent-skills-mcp` live 表面不满足新契约。

实现过程中完成 Builder、Installer、host 配置、Runtime/Release workflows、用户/维护文档与现有测试的统一改名，并新增 `test_runtime_binary_product_name.py`。机械替换曾把 `USAGE.md` 的 Linux/macOS ZIP 列表误改为 `agent-skills.zip`，Skill Tests #1045 正确捕获；随后只恢复三平台 ZIP 文件名，未修改 Runtime/打包逻辑。

Ready head：`b53a1973b704a500a57e44b353512f5eb4d71e91`。

# 独立 Review

A1 从 Issue #181 反查实现：basename、安装路径、三平台 ZIP 不变、无旧名兼容层、Maintenance 默认不兼容策略均有直接实现和永久回归；非目标中的 MCP Tool Contract、Task Route、Routing Manifest、Bundle、Project Payload schema、Python 与依赖没有对应文件变化。

A2 从最终 diff 反查证据：Builder/Installer 只改变当前 basename；Server/smoke 仅同步错误/帮助名称；Runtime Package CI 对三平台执行真实 onefile、status/self-test、stdio MCP 与项目安装；Release 继续 tag/identity/SHA/Draft/Publish 原流程；live 旧名扫描排除历史 Change archive。

Review 过程中发现 Change `affected_paths` 初稿漏列 `server.py`、Bootstrap Reference、smoke 等真实影响路径，已在 Ready commit 补齐；未发现产品实现缺陷。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`，无未解决 BLOCKER/HIGH/MEDIUM。

# PR Final-head 验证

PR #182 Ready head：`b53a1973b704a500a57e44b353512f5eb4d71e91`。

- Skill Tests #1047 / run `33722394100`：success；Requirement Source、compile、CLI smoke、389 项 self-contained、changed Change Ready Check、Agent Skills Gate 全部成功。
- Runtime Package Tests #337 / run `33722393935`：success；Linux/Windows/macOS onefile build+self-test、real stdio MCP、project-only single-binary install、Package Gate 全部成功。
- 合并前 PR 非 Draft、mergeable，head/main 未漂移，无 review comment/thread。

# 实现合并与 Main-fresh 验证

PR #182 使用 `expected_head_sha=b53a1973b704a500a57e44b353512f5eb4d71e91` guarded squash merge。

实现 merge SHA：`88b8ca22c8051bd04d166dbd3d78e7b886a869cc`。

`main@88b8ca22...` fresh CI：

- Skill Tests #1048 / run `33722605782`：success；Requirement Source、389 项 self-contained、Active Change Ready Check、Agent Skills Gate 全部通过。
- Runtime Package Tests #338 / run `33722605842`：success；Linux/Windows/macOS onefile build+self-test、real stdio MCP、project-only install、Package Gate 全部通过。

只有取得以上 implementation main-fresh evidence 后才开始本次 Change archive。

# 文档与 Contract 影响

- `USAGE.md`：最终用户只看到 `agent-skills[.exe]`，并继续下载原三平台 ZIP；升级说明明确默认不承诺跨版本原地兼容。
- `runtime/README.md` 与 Runtime canonical References：同步当前 basename、安装路径、ZIP 成员和 Maintenance 兼容策略。
- `.agents/MAINTENANCE.md`：新增长期“默认不承担跨版本升级兼容”规则，同时明确不能借此绕过当前 Requirement 明确要求保持的产品契约。
- MCP Tool Contract、Task Route、Routing Manifest、Bundle/Project Payload schema、Stable Reference ID、Python 版本和依赖未变化。
- 未创建 Release/tag。

# 归档生命周期

- [x] PR #182 使用 expected head guard 合并到 main。
- [x] implementation merge `88b8ca22...` 的 main-fresh Skill Tests #1048 与 Runtime Package #338 全绿。
- [ ] 当前 finalization PR 合并，并取得 archive-main fresh CI。
- [ ] Issue #181 Closure Audit 后关闭。
- [ ] `chg/runtime-binary-agent-skills` 与 finalization 分支确认已清理。

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #181、main 根 `AGENTS.md`、Maintenance/Runtime 规则、PR #182 最终 diff 与 implementation main-fresh 结果。
- [x] change_coverage: R1-R6 已完成；R7 的 archive PR 自身 merge/main-fresh 与 closure 按 `explicitly_deferred` 由 finalization 生命周期继续，不伪造自引用证据。
- [x] reverse_audit: 已反查 basename、安装路径、Release artifact 隔离/ZIP 成员、不兼容策略、协议/Schema/依赖边界、历史 archive 排除和无 Release/tag。
- [x] unresolved_cleared: implementation main-fresh Skill #1048、Runtime #338 全绿，独立 Review `NO_FINDINGS_WITHIN_SCOPE`，无未解决产品 finding。
