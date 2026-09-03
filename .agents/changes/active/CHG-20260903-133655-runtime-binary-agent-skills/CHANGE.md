---
schema: coding-change/v1
id: CHG-20260903-133655-runtime-binary-agent-skills
title: 统一 Runtime 二进制命名为 agent-skills
level: L3
status: in_progress
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
  - runtime/agent_skills_runtime/project_installer.py
  - .github/workflows/runtime-package-tests.yml
  - .github/workflows/release.yml
  - USAGE.md
  - runtime/README.md
  - .agents/MAINTENANCE.md
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
| R1 | Builder、Installer、宿主配置和 live 规则统一使用 agent-skills | https://github.com/dingyuwen777/Agent_Skills/issues/181 | not_satisfied | Red/Green 命名契约回归与三平台 package CI |
| R2 | Windows 安装为 .agents/runtime/agent-skills.exe，Linux/macOS 为 .agents/runtime/agent-skills | https://github.com/dingyuwen777/Agent_Skills/issues/181 | not_satisfied | 三平台项目安装与 MCP smoke |
| R3 | Release 仍精确三个 agent-skills-v<SemVer>-<platform>.zip，每包仍只有 binary + USAGE.md | https://github.com/dingyuwen777/Agent_Skills/issues/181 | not_satisfied | Release workflow 静态契约回归 + Runtime Package CI |
| R4 | 不新增旧名兼容层，不验证旧安装升级 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | not_satisfied | live 旧名扫描与实现 Review |
| R5 | Maintenance 固化 Agent_Skills 默认不承担跨版本升级兼容义务 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | not_satisfied | Maintenance preservation 回归 |
| R6 | MCP/Bundle/Project Payload schema、Python/依赖和 Release 打包方式不发生无关变化 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | not_satisfied | diff Review + existing regression suites |
| R7 | 完整 Skill Tests、三平台 Runtime Package、独立 Review、guarded merge 与 main-fresh 闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/181 | not_satisfied | PR/main/Archive CI 与 Review Evidence |

# Validation Matrix

| 层级 | Scope | 状态 | 证据 |
| --- | --- | --- | --- |
| Red | 当前旧名必须让新命名契约失败 | pending | PR Red CI |
| Static contract | Builder/Installer/Workflow/Docs/Maintenance live 表面 | pending | self-contained tests |
| Runtime package | Linux/Windows/macOS onefile + status/self-test + stdio MCP + project install | pending | Runtime Package Tests |
| Release contract | 三平台 ZIP 名称与两项成员结构不变 | pending | Release productization/platform ZIP tests |
| Review | Requirement A1/A2 + 内容守恒 + 无兼容层 + 无 live 旧名残留 | pending | independent Review |

# 完成审计

- [ ] upstream_re_read: 合并前重新读取 Issue #181 与当前 main 规则。
- [ ] change_coverage: R1-R7 均有直接实现或验证证据。
- [ ] reverse_audit: 从最终 diff 反查命名、Release 打包、不兼容策略和未授权变化。
- [ ] unresolved_cleared: 无未解决 blocker、CI failure 或旧名 live 残留。
