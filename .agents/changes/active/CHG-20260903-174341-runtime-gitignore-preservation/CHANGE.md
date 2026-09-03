---
schema: coding-change/v1
id: CHG-20260903-174341-runtime-gitignore-preservation
title: 修复 Runtime 安装错误写入 gitignore
level: L3
status: in_progress
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
affected_paths:
  - runtime/agent_skills_runtime/project_installer.py
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - runtime/README.md
  - .agents/skills/coding/tests/test_runtime_gitignore_install_contract.py
  - .agents/changes/active/CHG-20260903-174341-runtime-gitignore-preservation/CHANGE.md
contracts:
  - Runtime project installation contract
  - target project .gitignore preservation
  - sidecarless installation ownership
data_changes: []
---

# 目标

修复正式 Runtime binary 安装/升级会向目标项目 `.gitignore` 自动新增 `/.agents/runtime/` 的行为。安装器以后只继续幂等维护 Agent_Skills 自己的本地缓存 ignore，不把 Runtime 目录变成自动忽略项；项目在安装前已经自行配置的 Runtime ignore 保持原样，不因本次修复被删除。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/191

# 成功标准

- [ ] 新项目首次安装后 `.gitignore` 不出现安装器新增的 `/.agents/runtime/`。
- [ ] `.agents/project-context.json` 缓存 ignore 仍幂等维护，项目原有 `.gitignore` 内容与换行保持。
- [ ] 项目原本已有 Runtime ignore 时保持原样，不删除、不重复。
- [ ] Runtime 安装路径、宿主 MCP 配置、sidecarless ownership、回滚和三平台 package/install 不回归。
- [ ] canonical Runtime/Bootstrap 规则与 `runtime/README.md` 同步为新契约。

# 范围

- Runtime installer 的 `.gitignore` 增量编辑行为；
- Runtime / Bootstrap canonical 安装规则；
- Runtime 维护说明；
- 永久安装回归与三平台 Runtime Package 验证。

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
4. 这属于 Runtime 安装 Contract 变化，必须同步 ref12/ref13 与 `runtime/README.md`，不能只改 Python 实现。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：首次安装不得新增 Runtime ignore | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC1 | not_satisfied | Red/实现待完成 |
| R2 | AC2：缓存 ignore 与项目 `.gitignore` 保持 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC2 | not_satisfied | Red/实现待完成 |
| R3 | AC3：已有 Runtime ignore 保持，不删除不重复 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC3 | not_satisfied | Red/实现待完成 |
| R4 | AC4：Runtime/MCP/ownership/rollback 不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC4 | not_satisfied | Runtime package/install 验证待完成 |
| R5 | AC5：canonical Runtime/Bootstrap 契约同步 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC5 | not_satisfied | ref12/ref13 待修改 |
| R6 | AC6：Runtime README 同步 | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC6 | not_satisfied | 文档待修改 |
| R7 | AC7：永久回归先 Red 后 Green | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC7 | not_satisfied | Red 待形成 |
| R8 | AC8：完整 CI 与独立 Review | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC8 | not_satisfied | final-head 证据待完成 |
| R9 | AC9：merge/main/archive/closure/cleanup | external:https://github.com/dingyuwen777/Agent_Skills/issues/191#AC9 | explicitly_deferred | Post-Merge Finalization 承担 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | `.gitignore` 更新函数与真实 `install_project()` 首次/重复安装回归 |
| 接口 / 契约 | required | ref12/ref13 安装 Contract 与实现一致，不再要求 Runtime ignore |
| 集成 / 持久化 / 运行依赖 | required | 临时目标项目真实文件写入、已有 `.gitignore`/Runtime ignore 保持、rollback 相关既有回归 |
| 用户 / 工作流验收 | required | 运行 binary/project installer 后 Runtime 仍安装但 `.gitignore` 不新增 Runtime ignore |
| 跨组件关键路径 | required | Builder/Runtime artifact → project install → MCP 配置 → installed Runtime 路径 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖第三方业务 Provider 或远程生产服务 |
| 构建 / 打包 / 运行 | required | Runtime Package Tests 按 package scope 在 Linux/Windows/macOS 构建、self-test、MCP、项目安装 |
| 文档 / 治理 / 其他 | required | #191、本 L3 Change、canonical ref12/ref13、Runtime README、独立 Review 与 Finalization |

# Red 计划

新增永久回归，旧实现应至少因以下事实失败：

- `_updated_gitignore(None)` 当前会加入 `/.agents/runtime/`；
- 首次真实 `install_project()` 当前会把 Runtime ignore 写入新 `.gitignore`；
- 当前 ref12/ref13/Runtime README 仍明确要求 Runtime ignore。

Red 只证明缺口，不在同一提交修改生产实现或 canonical Contract。

# 完成审计

- [ ] upstream_re_read：完成前重新读取 #191 与当前 Runtime/Bootstrap canonical Owner。
- [ ] change_coverage：AC1–AC9 均有直接实现、验证或正式 Finalization Owner。
- [ ] reverse_audit：从最终 diff 反查 Runtime 路径/MCP/ownership/rollback/项目自有 `.gitignore` 未被误改。
- [ ] unresolved_cleared：进入 Ready 前除 Post-Merge 生命周期外不存在 `not_satisfied`。

# 任务

- [x] 调查当前 installer、canonical Runtime/Bootstrap 规则与测试事实
- [x] 建立 L3 Requirement Source 与 Change
- [ ] 建立并验证 Red
- [ ] 完成最小实现
- [ ] 同步 canonical Runtime/Bootstrap 与 Runtime README
- [ ] 执行 targeted/full Skill Tests 与 Runtime Package Tests
- [ ] 完成独立 A1/A2 Review、Completion Audit 与 Ready
- [ ] guarded merge、main-fresh、归档、Issue Closure、分支清理

# 文档影响

- `runtime/README.md` required：当前明确声明 Runtime 目录进入 `.gitignore`，必须同步。
- `USAGE.md` 当前未发现该 Runtime ignore 契约，默认不修改；若最终反查发现相关正文再 targeted 同步。

# 交付

- 实现 PR：待创建。
- Release/tag：not_applicable，本任务未授权也不需要发布新版本。
