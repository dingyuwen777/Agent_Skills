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

版本、源码 commit、协议和 digest 身份已嵌入可执行文件，可用 `status --json` 查看；用户不需要额外下载或维护 identity 文件。

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

**安装成功不等于项目治理已经完成。** 可执行文件负责把 Agent_Skills 接入当前项目；项目实际使用什么技术栈、模块如何协作、哪些规则长期有效，需要由你当前使用的 Codex、Cursor、Claude Code 等开发工具中的大模型读取真实项目后确认。

## 3. 开始使用

安装完成后，在 Codex、Cursor、Claude Code 或其他支持项目 MCP 的开发工具中打开该项目，然后直接用自然语言描述任务。

你不需要手工编写路由 JSON、选择规则文件或记忆内部标识。工具会根据当前任务已经确认的事实选择最少充分的规则；关键信息仍不明确时会保守扩大规则范围，缺少必要信息时会明确提示，而不是静默猜测。

### 首次接入：先校准项目 `AGENTS.md`

首次接入任意项目时，当前大模型应先完成一次 `Project Governance Bootstrap`（项目规则初始化/校准），再进入实质性开发；Greenfield 和已有项目都适用。这一步不是让安装程序猜项目架构，而是让**当前正在帮助你开发这个项目的大模型**先调查项目真实情况，再创建或修正项目自己的 `AGENTS.md`。

可以直接使用下面这段自然语言：

```text
这是本项目第一次接入 Agent_Skills。先不要修改业务代码。

请先读取当前已有的 AGENTS.md、CONTRIBUTING、README、需求/规格、Manifest/lock、真实代码、Contract、Schema/Migration、测试、CI、部署配置和其他与长期开发规则有关的事实源，完成 Project Governance Bootstrap。

校准 AGENTS.md 时：
1. 区分规范性规则、描述性事实和未确认事项；
2. 规范性规则不能因为当前代码没有遵守就直接删除或弱化；如果实现违反正式规则，应指出实现问题；
3. 描述性事实只有在当前项目有充分证据证明已经过时时才修正；
4. 无法确认的内容保持未确认，不要猜技术栈、架构、数据库、CI 或部署方式；
5. 保留现有仍有效内容，只做必要的增量修正；
6. 完成后重新读取最终 AGENTS.md，再告诉我当前项目的工程基线、主要模块边界、开发/测试入口和仍未确认的事项。
```

如果你的真实目标本来就是开发功能，也可以把原任务直接接在后面：

```text
这是本项目第一次接入 Agent_Skills。先不要修改业务代码。
先按当前仓库真实情况完成 Project Governance Bootstrap，校准项目 AGENTS.md；完成后重新读取最终 AGENTS.md。
然后继续原始任务：实现用户批量导出功能，并完成必要测试。
```

你也**可以直接用自然语言提出开发任务**，例如“基于当前仓库真实实现完成这个功能”。如果项目仍处于首次接入或项目规则尚未完成校准，Agent_Skills 会要求当前大模型先完成上述项目调查和 `AGENTS.md` 校准，再继续原来的开发请求。

### 日常开发

首次校准完成后，普通开发不需要每次重写 `AGENTS.md`。大模型应先读取当前项目规则并检查是否存在明显长期事实漂移；没有变化时直接继续当前任务。只有技术栈、模块职责、Contract/Schema、开发验证入口、CI/Release/部署等长期工程事实发生变化，或你明确要求刷新项目规则时，才针对受影响部分更新。

开发 / Bug / 重构可以直接说：

```text
基于当前仓库真实实现完成这个功能。
先读取项目规则和实际代码，再完成实现、验证和交付。
如果本次变化会改变长期项目规则或工程事实，同步更新 AGENTS.md 中对应内容。
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

当前版本不提供旧安装格式的原地兼容升级。旧版本项目应先备份项目规则，并按对应版本说明显式移除旧安装边界后重新安装；不要让新版本猜测或自动删除来源不明的项目文件。

## 7. 回退

需要回到之前的版本时：

1. 获取需要回退到的同平台版本及其校验文件；
2. 校验文件完整性；
3. 在目标项目根目录运行该版本；
4. 运行 `status --json` 和 `self-test --json`；
5. 重新打开项目或新建一次 Agent 会话。

不要手工混合不同版本的 Agent_Skills 文件。如果目标版本明确拒绝当前项目状态，应停止操作并根据错误信息处理。

回退必须使用目标版本对应的同一个完整可执行文件，让规则、运行文件和版本身份一起恢复；不要只复制其中一部分文件。

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
