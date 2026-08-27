# Agent Skills Runtime Distribution Kit

这份文档面向**实际拿到 Runtime Kit 的使用者**。使用者不需要访问 `Agent_Skills` canonical 源仓库，也不会得到 canonical `references/*.md` 正文。

Kit 的目标是：

```text
Native Core SKILL.md
+ Reference Runtime Stub
+ agent-skills-mcp[.exe]
+ 独立目标项目安装器
```

让 Codex / Cursor / Claude Code 在需要某个 Reference 时，通过本地 MCP `agent_skills_load_context` 取得该 Reference 的 canonical 原文。

## 0. 从正式 GitHub Release 选择 Kit

正式版本号来自仓库根 `VERSION`，Release tag 为 `v<VERSION>`。同一个 Release 会提供三个平台独立 Runtime Kit：

```text
agent-skills-mcp-runtime-kit-v<VERSION>-linux.zip
agent-skills-mcp-runtime-kit-v<VERSION>-windows.zip
agent-skills-mcp-runtime-kit-v<VERSION>-macos.zip
SHA256SUMS
```

选择与你实际运行 Runtime 的操作系统一致的 ZIP。Windows onefile、Linux onefile、macOS onefile 不能跨平台混用。

下载后先校验 `SHA256SUMS`，再解压和安装。正式 Release 的 tag 和资产属于历史事实：升级使用更高 VERSION 的新 Release，回滚使用旧 Release 的完整 Kit；不要把不同版本的 Runtime 和目标项目 Stub 混装。

维护者可以直接运行 `scripts/build_runtime.py` 得到未重命名的本地构建 Kit；它用于开发验证。正式对外分发文件名由 Release workflow 增加 `v<VERSION>-<platform>`，二者内部 Kit 结构相同。

## 1. 你会拿到什么

Windows 构建产物解压前的正式 Release 文件名通常是：

```text
agent-skills-mcp-runtime-kit-v<VERSION>-windows.zip
```

解压后唯一顶层目录仍是：

```text
agent-skills-mcp-runtime-kit/
├── agent-skills-mcp.exe
├── agent-skills-mcp.manifest.json
├── agent-skills-runtime-kit.json
├── install_runtime.py
├── install_runtime_target.py
├── requirements-tools.txt
├── README.md
└── payload/
    └── .agents/
        └── skills/
            ├── coding/
            │   ├── SKILL.md
            │   ├── agents/
            │   ├── assets/
            │   ├── scripts/
            │   └── references/*.md   # Runtime Stub，不含 canonical 正文
            ├── review/
            └── docs/
```

Linux / macOS 的 Runtime 文件没有 `.exe` 后缀，其余结构相同。

`agent-skills-mcp[.exe]` 中包含经过 AES-256-GCM 加密并嵌入的 canonical Reference Bundle。它用于降低直接浏览/复制门槛，不承诺抵御本机管理员、调试器、内存转储或专业逆向。

`agent-skills-mcp.manifest.json` 与 `agent-skills-runtime-kit.json` 都记录当前 `release_version`；Reference 完整性仍由 `source_digest` 和每个 Reference SHA256 独立证明，版本号不替代 hash 校验。

## 2. Windows 首次使用

下面假设你已经把 ZIP 解压到：

```text
D:\tools\agent-skills-mcp-runtime-kit
```

### 2.1 准备 Python 工具环境

目标项目里的 Coding CLI 默认使用北京时间 `Asia/Shanghai`。Windows CPython 通常没有系统 IANA 时区数据库，因此先安装 Kit 固定的最小工具依赖：

```powershell
py -3.12 -m venv D:\tools\agent-skills-runtime-python
D:\tools\agent-skills-runtime-python\Scripts\python.exe -m pip install -r D:\tools\agent-skills-mcp-runtime-kit\requirements-tools.txt
```

以后执行 Kit 里的 Python 安装脚本时使用这个 Python。

### 2.2 安装或升级用户级 Runtime

```powershell
D:\tools\agent-skills-runtime-python\Scripts\python.exe `
  D:\tools\agent-skills-mcp-runtime-kit\install_runtime.py `
  --artifact D:\tools\agent-skills-mcp-runtime-kit\agent-skills-mcp.exe `
  --json
```

默认安装到：

```text
%LOCALAPPDATA%\AgentSkills\bin\agent-skills-mcp.exe
```

验证：

```powershell
& "$env:LOCALAPPDATA\AgentSkills\bin\agent-skills-mcp.exe" status --json
& "$env:LOCALAPPDATA\AgentSkills\bin\agent-skills-mcp.exe" self-test --json
```

## 3. 注册到 Codex

推荐把 Runtime 注册成用户级 stdio MCP，一台机器上的多个项目共享同一个 Runtime：

```powershell
codex mcp add agent-skills -- "$env:LOCALAPPDATA\AgentSkills\bin\agent-skills-mcp.exe" serve
codex mcp list
```

等价的 Codex 配置核心是：

```toml
[mcp_servers.agent-skills]
command = "C:/Users/<user>/AppData/Local/AgentSkills/bin/agent-skills-mcp.exe"
args = ["serve"]
```

只注册 MCP 还不表示每个任务都会自动调用它。真正的强制入口来自目标项目 `AGENTS.md` + Native Core Skill + Reference Stub。

## 4. 把 Agent Skills 接入目标项目

假设项目是：

```text
D:\work\MyProject
```

执行：

```powershell
D:\tools\agent-skills-runtime-python\Scripts\python.exe `
  D:\tools\agent-skills-mcp-runtime-kit\install_runtime_target.py `
  --runtime-command "$env:LOCALAPPDATA\AgentSkills\bin\agent-skills-mcp.exe" `
  --target "D:\work\MyProject" `
  --json
```

这个安装器只依赖**当前解压后的 Kit**：

- 先校验 `agent-skills-runtime-kit.json`；
- 逐文件校验 payload 的 SHA256 / size / 文件集合；
- 调用已安装 Runtime 的 `status/self-test`；
- 要求 Runtime `source_digest` 与 Kit 完全一致；
- 完整暂存三个 Core/Stub Skill 后再切换；
- 保留目标项目 `.agents/changes/`、项目自有 Skill 和其他 `.agents` 内容；
- 调用 Kit 中随 Core Skill 分发的 Coding Bootstrap 建立/增量更新目标项目 `AGENTS.md`；
- Bootstrap 或 Skill 切换失败时恢复本轮已经切换的受管 Skill。

目标项目最终大致是：

```text
MyProject/
├── AGENTS.md
└── .agents/
    └── skills/
        ├── coding/
        │   ├── SKILL.md
        │   └── references/*.md   # Stub
        ├── review/
        └── docs/
```

目标项目里不会出现 Kit 对应版本的 canonical Reference 正文。

## 5. 实际开发时怎么用

开发者仍然正常告诉 Agent 任务，不需要每次人工指定 Reference ID。例如：

```text
使用 coding，基于当前仓库真实实现完成这个功能。
```

正常链路：

```text
目标项目 AGENTS.md
→ .agents/skills/coding/SKILL.md
→ Core Skill 根据当前仓库事实判断命中的 Reference
→ Agent 读取同名 Runtime Stub
→ Stub 要求调用 agent_skills_load_context
→ MCP 解密并返回 canonical_text + SHA256
→ Agent 校验 SHA256
→ canonical_text 作为该 Reference 的完整正式上下文继续参与方案、开发、验证、Docs、Review 和交付
```

如果 MCP 不可用、Reference ID 不存在、返回 SHA256 与 Stub 不一致，Agent 必须明确报告并停止依赖该 Reference 的动作，不能把 Stub 或旧记忆当成规则正文。

## 6. Cursor

Cursor 全局 MCP 配置可放：

```text
~/.cursor/mcp.json
```

核心配置：

```json
{
  "mcpServers": {
    "agent-skills": {
      "command": "C:/Users/<user>/AppData/Local/AgentSkills/bin/agent-skills-mcp.exe",
      "args": ["serve"]
    }
  }
}
```

项目仍使用同一套 `AGENTS.md` / Core Skill / Stub；不要为了 Cursor 再复制一套 canonical Reference。

## 7. Claude Code

用户级 stdio MCP 示例：

```bash
claude mcp add-json agent-skills '{"type":"stdio","command":"C:/Users/<user>/AppData/Local/AgentSkills/bin/agent-skills-mcp.exe","args":["serve"]}' --scope user
claude mcp get agent-skills
```

不同 shell 的 JSON 引号规则可能不同；如果命令行转义造成问题，使用 Claude Code 当前版本支持的配置文件方式写入同等 `stdio` command + `serve` args。

## 8. Linux / macOS

先建立工具环境：

```bash
python3 -m venv ~/.local/share/agent-skills/tools-python
~/.local/share/agent-skills/tools-python/bin/python -m pip install -r ./requirements-tools.txt
```

安装 Runtime：

```bash
~/.local/share/agent-skills/tools-python/bin/python ./install_runtime.py \
  --artifact ./agent-skills-mcp \
  --json
```

默认 Runtime：

```text
~/.local/share/agent-skills/bin/agent-skills-mcp
```

接入目标项目：

```bash
~/.local/share/agent-skills/tools-python/bin/python ./install_runtime_target.py \
  --runtime-command "$HOME/.local/share/agent-skills/bin/agent-skills-mcp" \
  --target /work/MyProject \
  --json
```

Codex：

```bash
codex mcp add agent-skills -- "$HOME/.local/share/agent-skills/bin/agent-skills-mcp" serve
codex mcp list
```

## 9. 后续升级

维护者发布新的 Runtime Kit 后，使用者按固定顺序升级：

```text
1. 解压新 Kit 到新目录
2. 用新 Kit 的 install_runtime.py 升级用户级 Runtime
3. 对每个目标项目重新运行新 Kit 的 install_runtime_target.py
4. 必要时重启/重连 Codex、Cursor、Claude Code 的 MCP 会话
5. 用真实任务验证一次 Stub → agent_skills_load_context → canonical_text
```

**不要只升级 Runtime 而长期保留旧项目 Stub，也不要只刷新项目 Stub 而继续使用旧 Runtime。** 两边的 `source_digest` / Reference SHA 不匹配时，安装器和 Stub 都会拒绝把这种混装状态当成成功。

## 10. 回滚

完整版本配套关系是：

```text
Runtime Kit A
↔ Runtime A source_digest
↔ Target Core/Stub A
```

回滚到旧版本时：

1. 找回旧 Release 的对应平台 Kit；
2. 用旧 Kit 的 `install_runtime.py` 安装旧 Runtime；
3. 用同一个旧 Kit 的 `install_runtime_target.py` 重新安装目标项目 Core/Stub；
4. 检查 Runtime `status/self-test`；
5. 重新建立 MCP 会话并做一次真实 Reference 加载。

不要单独替换 `.exe` 后就认为回滚完成。

## 11. 对维护者：怎么生成 Kit

只有维护 canonical `Agent_Skills` 源仓库的人需要执行本地预构建；正式 Release 仍由合并后 `main` 的 `.github/workflows/release.yml` 重新构建。

### Windows

```powershell
py -3.12 -m venv .venv-runtime
.\.venv-runtime\Scripts\python.exe -m pip install -r runtime\requirements-build.txt
.\.venv-runtime\Scripts\python.exe scripts\build_runtime.py --output-dir dist --json
```

本地输出：

```text
dist\agent-skills-mcp.exe
dist\agent-skills-mcp.manifest.json
dist\agent-skills-mcp-runtime-kit.zip
```

### Linux / macOS

```bash
python3 -m venv .venv-runtime
./.venv-runtime/bin/python -m pip install -r runtime/requirements-build.txt
./.venv-runtime/bin/python scripts/build_runtime.py --output-dir dist --json
```

输出对应平台的 `agent-skills-mcp`、manifest 和未重命名 Runtime Kit ZIP。

PyInstaller onefile 不是跨平台产物：Windows `.exe` 必须在 Windows 构建/验证，Linux/macOS 也要在对应平台构建。正式 Release workflow 会把各平台已验证 Kit 重命名为带 VERSION 和 platform 的固定资产名，并与 Full Kit 一起生成 `SHA256SUMS`。
