# Agent_Skills 使用说明

Agent_Skills 按项目安装。选择与你操作系统匹配的可执行文件，在项目根目录运行即可。

安装和基础运行无需预装 Python。如具体任务需要额外环境，工具会明确提示；未满足条件的检查不会被当作已经完成。

## 1. 获取文件

每个正式版本提供：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
USAGE.md
SHA256SUMS
```

按系统选择一个可执行文件：

- Windows：`agent-skills-mcp-v<VERSION>-windows.exe`
- Linux：`agent-skills-mcp-v<VERSION>-linux`
- macOS：`agent-skills-mcp-v<VERSION>-macos`

建议同时使用 `SHA256SUMS` 校验文件完整性。

Windows PowerShell：

```powershell
Get-FileHash .\agent-skills-mcp-v<VERSION>-windows.exe -Algorithm SHA256
```

Linux：

```bash
sha256sum ./agent-skills-mcp-v<VERSION>-linux
```

macOS 使用系统可用的 SHA-256 校验工具，并与 `SHA256SUMS` 中对应记录比较。

## 2. 安装到项目

在目标项目根目录运行对应文件。安装只作用于当前项目，不会全局修改其他项目。

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

无参数运行时，默认安装或更新当前工作目录中的 Agent_Skills。

也可以显式指定项目。下面用 `agent-skills-mcp` 代表当前平台的可执行文件：

```text
agent-skills-mcp install --target <目标项目根目录> --json
```

安装成功后即可在该项目中使用。已有项目配置会尽量保留；如果检测到无法安全处理的冲突，安装会停止并给出错误信息。

## 3. 开始使用

安装完成后，在 Codex、Cursor、Claude Code 或其他支持项目 MCP 的开发工具中打开该项目，然后直接用自然语言描述任务。

### 开发 / Bug / 重构

```text
基于当前仓库真实实现完成这个功能。
先恢复项目规则和实际代码，再完成实现、验证和交付。
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

## 4. Codex、Cursor、Claude Code

首次打开项目时，开发工具可能要求确认项目 Trust、Approval 或 MCP 权限。按工具自身提示完成确认即可。

如果安装成功后没有识别到 Agent_Skills：

1. 关闭并重新打开当前项目，或新建一次 Agent 会话；
2. 检查是否有未确认的 Trust / Approval 提示；
3. 运行下面的状态检查；
4. 如果自检失败，在项目根目录重新运行当前版本的可执行文件。

## 5. 状态检查

查看当前版本和运行状态：

```text
agent-skills-mcp status --json
```

执行自检：

```text
agent-skills-mcp self-test --json
```

如果命令返回错误，先按错误信息处理，再重新运行自检。

## 6. 升级

升级到新版本：

1. 获取当前平台的新版本可执行文件和 `SHA256SUMS`；
2. 校验文件完整性；
3. 在同一个项目根目录运行新版本；
4. 运行 `status --json` 和 `self-test --json`；
5. 重新打开项目或新建一次 Agent 会话。

如果升级过程中报告版本不支持、配置冲突或其他错误，不要强制覆盖或手工删除未知项目文件，按错误信息处理后再重试。

## 7. 回退

需要回到之前的版本时：

1. 获取需要回退到的同平台版本及其校验文件；
2. 校验文件完整性；
3. 在目标项目根目录运行该版本；
4. 运行 `status --json` 和 `self-test --json`；
5. 重新打开项目或新建一次 Agent 会话。

不要手工混合不同版本的 Agent_Skills 文件。如果目标版本明确拒绝当前项目状态，应停止操作并根据错误信息处理。

## 8. 常见问题

### 安装时报告冲突

如果安装因为项目中已有内容或配置冲突而停止，不要直接强制覆盖。先查看错误信息，确认冲突文件属于当前项目还是 Agent_Skills，再决定如何处理。

### 安装成功但开发工具没有识别

依次尝试：

1. 重新打开项目或新建 Agent 会话；
2. 完成开发工具提示的 Trust / Approval；
3. 运行 `status --json`；
4. 运行 `self-test --json`；
5. 在项目根目录重新运行当前版本。

### 规则加载或完整性检查失败

依次运行：

```text
agent-skills-mcp status --json
agent-skills-mcp self-test --json
```

如果仍失败，在项目根目录重新运行当前版本，然后重新打开开发工具。

### 任务提示缺少额外环境

安装和基础运行无需预装 Python。如具体任务需要额外环境，按提示补充对应环境后重新执行该任务即可。

## 9. 网页端说明

本地安装方式适用于能够连接项目 MCP 的开发工具。纯网页会话不能直接运行你电脑上的本地可执行文件。
