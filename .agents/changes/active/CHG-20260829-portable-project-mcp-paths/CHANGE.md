---
schema: coding-change/v1
id: CHG-20260829-portable-project-mcp-paths
title: 修复项目级 MCP 配置绝对路径不可移植
level: L2
status: in_progress
owner: ChatGPT
branch: fix/portable-project-mcp-paths
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - installer
  - host-config
  - tests
  - coding-rules
affected_paths:
  - "runtime/agent_skills_runtime/project_installer.py"
  - ".agents/skills/coding/tests/test_single_binary_project_install.py"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
contracts:
  - "Project-local MCP host configuration portability"
data_changes: []
---

# 目标

修复项目级安装后 `.cursor/mcp.json`、`.mcp.json`、`.codex/config.toml` 把安装机器的绝对路径写入 `command`，导致这些项目配置被复制、提交或在另一台机器/另一路径打开时携带旧盘符、用户名或工作目录的问题。

# 成功标准

- [ ] Cursor 项目配置不包含安装机器绝对路径，并使用 Cursor 官方项目根插值定位 `.agents/runtime/`。
- [ ] Claude Code 项目配置不包含安装机器绝对路径，并使用 Claude Code 官方项目根变量定位 `.agents/runtime/`。
- [ ] Codex 项目配置不包含安装机器绝对路径，使用项目相对 Runtime command；明确当前 Codex 相对命令仍依赖会话工作目录/宿主实现，不能伪称上游未提供的 workspace placeholder。
- [ ] Windows `.exe` 与 POSIX 无扩展名 Runtime 都生成正确的宿主 command。
- [ ] `.agents/agent-skills-install.json` 继续保存项目相对 `runtime`，不改变 install manifest schema、Skill/shared ownership 或 Runtime 安装位置。
- [ ] 升级已有受管安装时能把旧绝对 command 收敛为新可移植 command，同时保留其他 MCP server、TOML/JSON 用户内容和 managed marker 外文本。
- [ ] 建立能在旧实现上失败的永久回归，并完成 Red → Green → Review → Ready → PR CI → main CI → 独立归档。

# 范围

- 调整 `project_installer.py` 生成 Cursor、Claude Code、Codex 项目级 MCP command 的方式。
- 增加 Windows/POSIX 项目安装回归，检查所有持久 Host 配置不泄露目标项目绝对路径。
- 同步 Coding ref13/ref14 的项目级 MCP 可移植性 Contract。

# 非目标

- 不把 `.agents/runtime/` 提交到 Git；每台开发机仍需在目标项目根运行一次对应平台 Release binary 完成本地 Runtime 安装。
- 不改 Runtime binary、Bundle、Project Payload schema、Reference Stub、MCP Tool Contract 或加密格式。
- 不引入全局安装、用户级 MCP 配置、在线下载器或自动更新服务。
- 不解决 Codex 上游所有 Desktop/VS Code 工作目录差异；只保证本仓库不再把安装机器绝对路径固化进项目配置，并按当前项目级配置能力提供最小可移植路径。

# 必须保持不变

- Runtime 继续安装到项目内 `.agents/runtime/agent-skills-mcp[.exe]`，且该目录继续被 `.gitignore` 排除。
- Cursor/Claude/Codex 继续只修改各自 Agent Skills 可证明认领的项目级 MCP 边界。
- AGENTS、CLAUDE bridge、其他 MCP server、用户 TOML/JSON 内容、manifest ownership 和安装回滚语义保持。
- 目标项目另一台机器如果没有本地 `.agents/runtime/agent-skills-mcp[.exe]`，不得伪装成无需安装即可运行；需要先运行对应平台安装器。

# 已确认关键决策

采用宿主各自支持的项目根语义，而不是把同一种占位符强行写给三个宿主：

- Cursor：`${workspaceFolder}` + `${pathSeparator}`；官方定义为包含 `.cursor/mcp.json` 的项目根。
- Claude Code：`${CLAUDE_PROJECT_DIR:-.}`；官方说明 stdio MCP 进程具有稳定项目根变量，项目 `.mcp.json` 中引用时需提供默认值。
- Codex：项目相对 `.agents/runtime/...`；当前 Codex 项目 `.codex/config.toml` 可定义 stdio MCP，但没有与 Cursor/Claude 等价、可在项目配置中稳定展开的 workspace placeholder，因此保留这一上游能力边界并通过实际项目根运行/CI 验证本仓库可控部分。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 安装后的项目配置不能绑定安装者电脑绝对路径，换电脑/目录后应保持项目级可移植 | user:2026-08-29-portable-mcp-paths | not_satisfied | 当前 `install_project()` 使用 `runtime_command = str(runtime_target)`，截图与源码均证明三个 Host config 固化绝对路径。 |
| R2 | 继续保持项目级、单二进制、每台机器本地安装模式 | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | not_satisfied | Runtime 位置、gitignore、manifest 与 Host ownership 均需回归保持。 |
| R3 | Runtime/Host config 变化必须匹配真实宿主能力并有跨平台构建/安装证据 | `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md` | not_satisfied | 需要行为回归、Linux/Windows/macOS 永久 CI 与最终 artifact 项目安装验证。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 安装 fixture 检查 Cursor/Claude/Codex 三份 Host config 的 command，旧实现先 Red，新实现无目标绝对路径。 |
| 接口 / Contract | required | Host config key/args、manifest schema/runtime、managed marker、其他 MCP server 与用户配置保持；同步 ref13/ref14 正式 Contract。 |
| 集成 / Persistence / Runtime Dependency | required | 临时真实文件系统执行 `install_project()`，覆盖首次安装与已有受管配置升级写回。 |
| 用户 / Workflow Acceptance | required | 从项目根运行安装器后，配置引用项目本地 Runtime；另一机器需本地运行一次对应平台 binary，但不继承上一机器绝对目录。 |
| 跨组件 Golden Path | required | 永久 CI 继续执行 onefile → 项目安装 → 项目内 Runtime/MCP smoke，验证新 Host config 未破坏安装闭环。 |
| External Dependency / Provider Probe | not_applicable | Cursor/Claude/Codex 配置语义使用当前官方文档/上游源码确认；普通 CI 不启动第三方 IDE GUI，真实 GUI 宿主差异作为明确证据边界。 |
| Build / Package / Runtime | required | Linux onefile/MCP/install + Windows/macOS package/install 永久 CI；不得仅用 Python fixture 声称平台 artifact 可用。 |
| Docs / Governance / Other | required | ref13/ref14、Change、Completion Audit、独立 Review、Ready Gate、PR/main CI、独立归档。 |

# Completion Audit

- [ ] upstream_re_read：重新核对用户“换电脑可直接使用”的真实边界与每台机器仍需项目级本地安装的既定模式。
- [ ] change_coverage：逐项检查 Cursor、Claude、Codex、manifest、AGENTS/CLAUDE bridge、gitignore、升级与回滚。
- [ ] reverse_audit：按 `Release binary → install target → runtime copy → Host config → Host spawn → MCP serve` 反向复核。
- [ ] unresolved_cleared：R1–R3 无 `not_satisfied`，所有 required 验证有新鲜证据。

# 实施任务

1. [Red] 增加 Windows/POSIX Host config 可移植性回归，证明当前绝对路径实现失败。
2. [Green] 用宿主特定项目根语义生成 command，最小修改安装器。
3. 同步 ref13/ref14，明确“项目配置可提交/复制，但 Runtime binary 每机本地安装”的边界。
4. 运行永久 CI、独立 Review、Ready Gate、PR/main CI 与独立归档。

# 当前证据

- 当前 main `5daaf524c60302bdd30f5d5c3e769a80840a633c`。
- `project_installer.py` 已把 manifest runtime 写为相对 `runtime_relative`，但 Host configs 使用 `runtime_command = str(runtime_target)`。
- 用户截图实际生成 `E:\\Desktop\\test\\AIMA_UGC\\.agents\\runtime\\agent-skills-mcp.exe`，与源码路径完全一致。
- Cursor 当前官方文档支持 `${workspaceFolder}`/`${pathSeparator}` 且项目 `.cursor/mcp.json` 用于项目共享。
- Claude Code 当前官方文档定义 `CLAUDE_PROJECT_DIR` 为稳定项目根，并说明项目 `.mcp.json` 引用该变量时使用 `${CLAUDE_PROJECT_DIR:-.}`。
- Codex 当前配置支持项目 `.codex/config.toml` 与 stdio `cwd`，但上游仍存在不同宿主工作目录差异；本 Change 不夸大该边界。

# 文档影响

Coding ref13/ref14 需要同步项目 Host config 可移植性约束；`USAGE.md` 的“一台机器在项目根运行对应平台二进制完成安装”使用方式不改变，暂不修改最终用户说明，完成前复核。

# Git / PR / Release 状态

- branch: `fix/portable-project-mcp-paths`
- PR: 待创建
- merge: 未执行
- main CI: 未执行
- Release: 本 Change 不自动发布新版本
