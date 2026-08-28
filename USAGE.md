# Agent_Skills 使用说明

这份文件是 Agent_Skills **最终使用者唯一需要阅读的人类说明**。

你只需要从维护者提供的正式 Release 交付资产中取得当前操作系统的 Runtime binary、`USAGE.md` 和 `SHA256SUMS`，不需要访问 Agent_Skills 源仓库，也不需要了解 Skill 的构建、分发或维护过程。

**安装和 MCP Runtime 本身不需要 Python。** 部分 Coding 流程可能需要 Python 执行项目发现或机器校验。如果目标项目或当前 Coding Agent 环境没有可用 Python，Agent 必须按已安装规则使用明确的 **fallback**；无法执行的机器检查必须标记为未验证，不能假装已经通过。

## 1. 取得正确的文件

每个正式版本提供：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
USAGE.md
SHA256SUMS
```

按系统选择一个 binary：

- Windows：`agent-skills-mcp-v<VERSION>-windows.exe`
- Linux：`agent-skills-mcp-v<VERSION>-linux`
- macOS：`agent-skills-mcp-v<VERSION>-macos`

建议同时取得 `SHA256SUMS` 并校验文件完整性。

Windows PowerShell：

```powershell
Get-FileHash .\agent-skills-mcp-v<VERSION>-windows.exe -Algorithm SHA256
```

Linux：

```bash
sha256sum ./agent-skills-mcp-v<VERSION>-linux
```

macOS 可以使用系统可用的 SHA-256 校验工具，并与 `SHA256SUMS` 中对应记录比较。

## 2. 安装到一个项目

Agent_Skills 是**项目级安装**。在某个项目根目录执行安装，只会为这个项目建立 Agent_Skills 运行环境，不会全局修改其他项目。

### Windows

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

安装成功后即可在该项目中使用 Agent_Skills。项目原有规则和项目自己的开发配置会继续保留；如果安装器发现无法安全接管的冲突，会停止并报告，而不是猜测性覆盖。

## 3. 安装后怎么使用

安装完成后，不需要记忆 Agent_Skills 的内部规则。继续在 Codex、Cursor、Claude Code 或其他能够读取项目规则并连接项目 MCP 的 Coding Agent 中，用自然语言描述任务即可。

### 开发 / Bug / 重构

```text
基于当前仓库真实实现完成这个功能。
先恢复项目规则和实际代码，再按当前 Agent Skills 完成实现、验证、Review 和交付。
```

### Code Review

```text
审查当前改动，只做 Review，不修改代码。
检查正确性、边界条件、错误处理、兼容性和测试充分性。
```

### 文档审查或更新

```text
检查当前技术文档是否与真实代码和运行方式一致，只处理受影响文档域。
```

### Figma 审查

```text
全面检查这个 Figma：<链接>
```

### 按 Figma 实现页面

```text
按这个 Figma 替换当前对应页面：<链接>
```

Agent 会依据当前项目规则和已安装的 Agent_Skills 自动选择正确工作流。你不需要手工指定内部规则文件。

## 4. Codex、Cursor、Claude Code

安装器会在**当前项目范围**内配置 Agent Skills MCP 入口，并尽量保留项目已有的其他配置。

宿主可能要求你对当前项目或 MCP 做首次 Trust / Approval。按 Codex、Cursor、Claude Code 自己的正常安全提示确认即可；Agent_Skills 不会绕过宿主的安全确认。

如果安装成功但 Coding Agent 没有识别到 Agent_Skills：

1. 关闭并重新打开当前项目或新建一次 Agent 会话；
2. 检查宿主是否提示项目 Trust / MCP Approval；
3. 运行下面的 Runtime 状态检查；
4. 如果自检失败，重新使用同一版本 binary 安装一次。

## 5. 检查 Runtime 状态

查看当前 binary 的版本和运行状态：

```text
agent-skills-mcp status --json
```

执行完整性自检：

```text
agent-skills-mcp self-test --json
```

如果命令返回错误，不要忽略错误继续假设安装正常。先按错误提示处理，再重新运行自检。

## 6. 升级

同一当前安装格式下的后续正式版本，升级不需要先卸载旧版本：

1. 从维护者提供的新版本正式 Release 资产中取得当前平台的新 binary 和 `SHA256SUMS`；
2. 校验文件完整性；
3. 在同一个目标项目根目录运行新 binary；
4. 安装成功后重新运行 `status --json` 和 `self-test --json`；
5. 如果宿主已经打开，建议重新建立一次 Coding Agent / MCP 会话。

升级只应更新 Agent_Skills 自己管理的内容；项目自有规则和其他开发配置不应因为普通升级被整体清理。

**当前版本不承诺从历史不兼容开发版的项目安装状态直接原地升级。** 如果运行新 binary 时明确报告旧安装状态不受支持，不要强制删除项目文件或绕过冲突；应按维护者提供的当前版本重新接入说明处理。

## 7. 回滚

回滚仅适用于使用**同一当前安装格式**的正式版本：

1. 从维护者提供的历史正式 Release 资产中取得兼容版本的同平台 binary 和 checksum；
2. 校验文件；
3. 在目标项目根目录运行该版本 binary；
4. 运行 `status --json` 和 `self-test --json`；
5. 重新建立 Coding Agent / MCP 会话。

不要只手工替换项目内 Agent_Skills 文件的一部分；不同版本混用可能导致运行状态不一致。历史不兼容开发版不在当前自动回滚范围内。

## 8. 常见失败

### 已存在同名 Skill 或配置冲突

首次安装时，如果项目已经存在与 Agent_Skills 冲突、但无法证明可以安全覆盖的内容，安装会停止。先确认冲突内容归属，再决定如何处理，不要直接强制删除项目文件。

### 项目规则边界损坏

如果安装器报告项目规则中的 Agent Skills 管理边界缺失、重复或顺序错误，应先修复该边界，再重新运行安装。安装器不会猜测哪段项目规则可以覆盖。

### 旧安装状态不受支持

如果新 binary 明确报告当前项目中的历史 Agent_Skills 安装状态或版本不受支持，不要尝试强制覆盖、手工拼接不同版本文件或绕过错误。当前版本不承担历史不兼容开发版的自动迁移；按维护者提供的当前版本重新接入说明处理。

### 规则加载或完整性校验失败

如果 Coding Agent 报告 Agent_Skills 规则无法加载、版本不一致或完整性校验失败：

1. 运行 `status --json`；
2. 运行 `self-test --json`；
3. 使用当前版本 binary 在项目根重新安装；
4. 重新建立 Coding Agent / MCP 会话。

在问题解决前，不要要求 Agent 按旧记忆继续执行受影响的规则。

### 没有可用 Python

安装和 MCP Runtime 仍可工作，但部分 Coding 流程可能无法执行对应 Python 机器检查。此时 Agent 应使用规则允许的 fallback，并明确哪些检查没有实际运行；不能把“安装成功”当成这些检查已经通过。

## 9. ChatGPT 网页端

当前 Release Runtime 是本地 stdio MCP。纯网页端 ChatGPT 不能直接启动你电脑上的本地进程。

如果使用的宿主只支持远程 MCP，需要另外的 Remote MCP / 安全隧道方案；这不属于当前本地 Release 的使用范围。
