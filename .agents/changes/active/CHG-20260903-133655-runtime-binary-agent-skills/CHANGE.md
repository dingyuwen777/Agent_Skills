---
schema: coding-change/v1
id: CHG-20260903-133655-runtime-binary-agent-skills
title: 统一 Runtime 二进制命名为 agent-skills
level: L3
status: ready_for_review
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

本次明确不提供旧二进制名 alias、fallback、双写、迁移探测或旧版本升级兼容。Maintenance 同步固化：Agent_Skills 自身后续修改默认以当前目标版本干净安装和当前版本行为为验收基线；只有 Requirement Source 明确要求时才承担跨版本升级兼容。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Builder、Installer、宿主配置和 live 规则统一使用 agent-skills | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | `test_runtime_binary_product_name` 全部通过；Builder/Installer/host 配置由 389 项 self-contained 回归覆盖 |
| R2 | Windows 安装为 .agents/runtime/agent-skills.exe，Linux/macOS 为 .agents/runtime/agent-skills | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | Runtime Package Tests #336 / run 33721967090：Linux、Windows、macOS 项目安装、status/self-test、stdio MCP 全部成功 |
| R3 | Release 仍精确三个 agent-skills-v<SemVer>-<platform>.zip，每包仍只有 binary + USAGE.md | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | Skill Tests #1046 的 Release productization/platform ZIP 回归全部通过；Release workflow 仍精确生成三个原命名 ZIP，binary 成员改为 agent-skills[.exe] |
| R4 | 不新增旧名兼容层，不验证旧安装升级 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | live 旧名扫描回归通过；最终 diff 只改当前 basename/路径/文档/CI，没有新增旧名 alias、fallback、双文件或迁移探测 |
| R5 | Maintenance 固化 Agent_Skills 默认不承担跨版本升级兼容义务 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | `test_maintenance_declares_no_default_cross_version_upgrade_compatibility` 通过，Maintenance 明确只有显式 Requirement 才增加兼容/迁移层 |
| R6 | MCP/Bundle/Project Payload schema、Python/依赖和 Release 打包方式不发生无关变化 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | satisfied | PR changed-files 不含协议/Schema/requirements；389 项既有 Runtime/路由/Release 回归全部通过；三平台 package identity 与安装门禁通过 |
| R7 | 完整 Skill Tests、三平台 Runtime Package、独立 Review、guarded merge 与 main-fresh 闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | explicitly_deferred | PR final implementation head 已有 389/389 self-contained + Runtime Package #336 三平台全绿；guarded merge、main-fresh、归档和 Issue Closure 必须在本 Change 进入 Ready 后按下方生命周期继续完成，不在合并前伪造完成事实 |

# Validation Matrix

| 层级 | Scope | 状态 | 证据 |
| --- | --- | --- | --- |
| Red | 当前旧名必须让新命名契约失败 | passed | Skill Tests #1035 / run 33719759904：新增命名契约在旧实现上按预期失败，证明 Red 有效 |
| Static contract | Builder/Installer/Workflow/Docs/Maintenance live 表面 | passed | Skill Tests #1046 / run 33721967093：self-contained step 389/389 通过；整体仅因当时 Change 仍为 in_progress 被 Ready Check 正确阻止 |
| Runtime package | Linux/Windows/macOS onefile + status/self-test + stdio MCP + project install | passed | Runtime Package Tests #336 / run 33721967090：三平台 jobs 与 Runtime Package Gate 全部 success |
| Release contract | 三平台 ZIP 名称与两项成员结构不变 | passed | `test_release_platform_zips`、`test_release_productization`、`test_release_only_repository_surface` 与新命名契约回归全部通过 |
| Review | Requirement A1/A2 + 内容守恒 + 无兼容层 + 无 live 旧名残留 | passed | implementation head `6b05079d7a9df6572118383187b5b47bf27a9761` 独立 A1/A2 Review：产品实现无发现；Change affected_paths 记录缺口已在本次 ready commit 修正 |

# 独立 Review

## A1：Requirement → Change / Implementation

- Issue #181 的 basename、安装路径、三平台 ZIP 不变、无旧名兼容层、Maintenance 默认不兼容策略均有直接实现与永久回归。
- Release 下载阶段因 Linux/macOS 同 basename 可能发生扁平化冲突，workflow 改为保留三个 artifact 子目录后再分别打包；这是实现新 basename 所必需的内部结构调整，外部三个 ZIP 名称、数量、两项成员和 Draft/Publish 流程均保持。
- 非目标中的 MCP Tool Contract、Task Route、Routing Manifest、Bundle、Project Payload schema、Python 与依赖没有发生对应文件变化。

## A2：Implementation → Evidence / Scope

- Builder 与 Installer 只改变当前 Runtime basename；Server/smoke 仅同步用户可见错误/帮助名称。
- Runtime Package CI 对 Linux、Windows、macOS 都执行真实 onefile build、status/self-test、stdio MCP 与项目安装，不以单元测试替代平台证据。
- Release workflow 继续由 tag 驱动版本、job outputs 交叉 identity、Draft 验证后发布；最终资产仍只有三个平台 ZIP。
- live 旧名扫描明确覆盖 `scripts/`、`runtime/`、`.github/`、`.agents/skills/`、`USAGE.md`、Maintenance，并故意不改写 `.agents/changes/archive` 历史记录。
- 未新增 Release/tag，未改依赖、Schema、Stable Reference ID 或协议版本。

结论：`NO_FINDINGS_WITHIN_SCOPE`。唯一发现的 Change `affected_paths` 记录不完整已在本次 ready commit 修正，不属于产品实现缺陷，当前无未解决 Review finding。

# 合并后生命周期

以下动作只能在本 Change 已 Ready 且 PR final-head fresh CI 通过后执行，当前不得提前声称完成：

- [ ] 使用 expected head guard 合并 PR #182。
- [ ] implementation merge 后执行并确认 main fresh Skill Tests / Runtime Package Tests。
- [ ] 将 Change 更新为 `done` 并移动到 `archive/2026-09/`，补入 merge/main CI 证据。
- [ ] 归档 PR 合并后再次确认 main fresh CI。
- [ ] 对 Issue #181 执行 Closure Audit 后关闭，并清理任务分支。

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #181、当前 main 根 `AGENTS.md`、当前 Maintenance/Runtime 规则和 PR #182 最终实现 diff。
- [x] change_coverage: R1-R6 均有直接实现与验证证据；R7 合并后生命周期按 `explicitly_deferred` 明确保留，没有伪造完成。
- [x] reverse_audit: 已从 24 个最终 changed files 反查 basename、安装路径、Release artifact 隔离/ZIP 成员、不兼容策略、协议/Schema/依赖边界和历史 archive 排除。
- [x] unresolved_cleared: 389 项 self-contained 回归通过，Runtime Package #336 三平台与 Gate 全绿，独立 Review 无未解决产品 finding；此前 USAGE ZIP 名机械误改已修复并由最终回归证明。
