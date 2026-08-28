# Agent_Skills 使用说明

这份文件是 Agent_Skills **Release 最终使用者唯一需要阅读的人类说明**。

你只需要从维护者提供的正式 Release 交付资产中取得当前操作系统的 Runtime binary、`USAGE.md` 和 `SHA256SUMS`。不需要访问 Agent_Skills 源仓库，也不需要安装 Python 环境。

## 1. 下载哪个文件

每个正式版本提供：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
USAGE.md
SHA256SUMS
```

- Windows：使用 `agent-skills-mcp-v<VERSION>-windows.exe`
- Linux：使用 `agent-skills-mcp-v<VERSION>-linux`
- macOS：使用 `agent-skills-mcp-v<VERSION>-macos`

建议同时取得 `SHA256SUMS` 校验文件完整性。

Windows PowerShell：

```powershell
Get-FileHash .\agent-skills-mcp-v<VERSION>-windows.exe -Algorithm SHA256
```

Linux / macOS：

```bash
sha256sum ./agent-skills-mcp-v<VERSION>-linux
# 或 macOS 对应文件
```

结果应与 `SHA256SUMS` 中对应文件一致。

## 2. 安装到一个项目

Agent_Skills 是**项目级安装**。一个项目安装一次，不会把 Runtime 全局注册到其他项目。

### Windows

进入目标项目根目录后直接运行：

```powershell
cd D:\work\MyProject
.\agent-skills-mcp-v<VERSION>-windows.exe
```

### Linux

```bash
cd /work/MyProject
chmod +x /path/to/agent-skills-mcp-v<VERSION>-linux
/path/to/agent-skills-mcp-v<VERSION>-linux
```

### macOS

```bash
cd /work/MyProject
chmod +x /path/to/agent-skills-mcp-v<VERSION>-macos
/path/to/agent-skills-mcp-v<VERSION>-macos
```

无参数运行时，binary 默认对**当前工作目录**执行安装或升级。

也可以显式指定项目。下面用 `agent-skills-mcp` 代表你拿到的当前平台 binary：

```text
agent-skills-mcp install --target <目标项目根目录> --json
```

安装成功后，项目中会出现 Agent_Skills 自己管理的 Skill、项目级 Runtime、MCP 配置和 `AGENTS.md` managed block。项目原有规则、项目自有 Skill 和其他 MCP 配置不会被整体接管。

## 3. 安装后怎么使用

安装完成后，不需要记 Agent_Skills 的内部规则。继续在 Codex、Cursor、Claude Code 或其他能够读取项目规则并连接项目 MCP 的 Coding Agent 中，用自然语言描述任务即可。

### Coding

```text
基于当前仓库真实实现完成这个功能。
先恢复项目规则和实际代码，再按当前 Agent Skills 完成实现、验证、Review 和交付。
```

### Review

```text
审查当前改动，只做 Review，不修改代码。
检查正确性、边界条件、错误处理、兼容性和测试充分性。
```

### Docs

```text
检查当前技术文档是否与真实代码和运行方式一致，只处理受影响文档域。
```

### Figma

```text
全面检查这个 Figma：<链接>
```

或：

```text
按这个 Figma 替换当前对应页面：<链接>
```

Agent 会根据项目中的 `AGENTS.md` 和正式 Skill 自动进入 Coding / Review / Docs / Figma 等正确工作流。

## 4. Codex、Cursor、Claude Code

安装器会在**当前项目范围**内建立 Agent Skills MCP 入口：

```text
Codex
→ .codex/config.toml

Cursor
→ .cursor/mcp.json

Claude Code
→ .mcp.json
→ CLAUDE.md 中的 @AGENTS.md bridge
```

这些文件只负责让宿主找到当前项目的 Runtime；项目研发规则仍由当前项目的 `AGENTS.md` 与已安装 Skill 负责。

宿主可能要求你对项目或 MCP 做首次 Trust / Approval。按宿主正常安全提示确认即可；Agent_Skills 不会绕过宿主自己的安全机制。

## 5. 检查 Runtime 状态

查看当前 binary 内置版本、Skill Catalog 和完整性摘要：

```text
agent-skills-mcp status --json
```

执行内置完整性自检：

```text
agent-skills-mcp self-test --json
```

如果是在已经安装过的项目中，也可以直接运行项目内 Runtime：

Windows：

```powershell
.\.agents\runtime\agent-skills-mcp.exe status --json
.\.agents\runtime\agent-skills-mcp.exe self-test --json
```

Linux / macOS：

```bash
./.agents/runtime/agent-skills-mcp status --json
./.agents/runtime/agent-skills-mcp self-test --json
```

## 6. 升级

升级不需要卸载旧版本。

1. 从维护者提供的新版本正式 Release 资产中取得当前平台的新 binary 和 `SHA256SUMS`；
2. 校验文件；
3. 在同一个目标项目根目录运行新 binary；
4. 安装器会根据项目里的 Agent_Skills ownership 记录升级自己负责的内容；
5. 如果宿主已经打开，升级后建议重新建立一次 MCP 会话。

项目自有 Skill、`AGENTS.md` managed block 之外的文本和其他 MCP server 不会因为普通升级被清理。

## 7. 回滚

需要回滚时：

1. 从维护者提供的历史正式 Release 资产中取得之前版本的同平台 binary 与 checksum；
2. 校验该版本文件；
3. 在目标项目根目录运行旧版本 binary；
4. 运行项目 Runtime 的 `status --json` 和 `self-test --json`；
5. 重新建立 MCP 会话。

不要只手工替换 `.agents/runtime/` 下的可执行文件而保留另一版本的 Skill/Reference Stub，这会形成版本混装。

## 8. 常见失败

### 已存在同名 Skill

首次安装时，如果项目已经存在与 Agent_Skills Release 同名、但无法证明由 Agent_Skills 管理的 Skill，安装会 **fail closed**，不会猜测性覆盖。先确认该目录归属，再决定如何处理。

### AGENTS managed marker 损坏

如果项目 `AGENTS.md` 中 Agent Skills managed marker 缺失、重复或顺序错误，安装器会停止，而不是猜测哪段内容可以覆盖。先修复 marker 边界再重新运行。

### MCP 无法加载 Reference

如果 Agent 报告 Reference ID 不存在、SHA256 不一致或无法取得 canonical text，不要让 Agent 按旧记忆继续执行依赖该规则的动作。先检查项目 Runtime 是否与当前安装版本一致，再运行 `status` / `self-test`。

## 9. 规则可见性边界

目标项目会保留用于宿主原生路由的 Core `SKILL.md`；详细 canonical Reference 正文不会以普通 Markdown 形式安装到目标项目，而由项目 Runtime 在需要时通过 MCP 返回并校验完整性。

这用于减少普通浏览和复制暴露面，但不是可信执行环境：拥有本机管理员权限、调试能力或能够观测进程内存/通信的人，理论上仍可能提取运行时明文。

## 10. ChatGPT 网页端

当前 Release Runtime 是本地 stdio MCP。纯网页端 ChatGPT 不能直接启动你电脑上的本地进程；如果使用的宿主只支持远程 MCP，需要另外的 Remote MCP / 安全隧道方案。