# Agent Skills Local MCP Runtime

本目录实现 `Agent_Skills` 的本地 MCP 分发方式。目标不是把复杂 Markdown 规则改写成布尔 Policy，而是保持当前 `coding / review / docs` 的自然语言执行效果，同时避免把完整 `references/*.md` 作为普通明文文件复制到每个目标项目。

正式规则仍以源仓库中的：

```text
.agents/skills/coding/SKILL.md
.agents/skills/coding/references/*.md
.agents/skills/review/SKILL.md
.agents/skills/review/references/*.md
.agents/skills/docs/SKILL.md
.agents/skills/docs/references/*.md
```

为准。Runtime 不维护第二套规则正文。

详细规范见 [`../.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md`](../.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md)。

## 1. 运行模型

```text
目标项目 AGENTS.md
→ 原生 Core SKILL.md
→ Core Skill 按现有语义判断需要哪个 Reference
→ 读取目标项目中的同名 Runtime Stub
→ Stub 要求调用 agent_skills_load_context
→ 本地 agent-skills-mcp 解密内嵌 Bundle
→ 返回 canonical Reference 原文 + SHA256
→ Coding Agent 把原文作为当前阶段规则上下文继续工作
```

`SKILL.md` 继续明文分发，是为了保留宿主原生 Skill/Rules 入口和复杂任务路由效果。高价值详细 `references/*.md` 在 Runtime 模式下只以 stub 形式进入目标项目。

## 2. 安全边界

Runtime 使用 AES-256-GCM 加密 Reference Bundle，并用 PyInstaller 打成当前平台单文件可执行产物。这样可以阻止普通使用者直接进入目标项目 `.agents/skills/*/references/` 阅读完整规则。

这**不是**针对机器 Owner 的强保密方案。单文件程序必须在本机解密 Reference 才能把原文交给 Codex/Cursor/Claude Code，因此具备调试、内存转储、进程 Hook 或二进制逆向能力的机器 Owner 理论上仍可以取得运行时明文。当前目标是提高直接浏览/复制门槛，同时最大程度保持 Skill 效果。

## 3. 构建当前平台 Runtime

建议使用独立 Python 3.11/3.12 虚拟环境。仓库把运行时和构建依赖固定在：

```text
runtime/requirements.txt
runtime/requirements-build.txt
```

`requirements-build.txt` 还固定包含 `tzdata`。这是因为 Windows CPython 通常没有系统 IANA 时区数据库，而 Coding Bootstrap 的北京时间硬规则使用 `Asia/Shanghai`；后续在 Windows 执行目标项目 Runtime 安装时应继续使用这个虚拟环境的 Python，不要换回没有 `tzdata` 的裸系统 Python。

### Windows PowerShell

```powershell
py -3.12 -m venv .venv-runtime
.\.venv-runtime\Scripts\python.exe -m pip install -r runtime\requirements-build.txt
.\.venv-runtime\Scripts\python.exe scripts\build_runtime.py --output-dir dist --json
```

产物：

```text
dist\agent-skills-mcp.exe
dist\agent-skills-mcp.manifest.json
```

### Linux / macOS

```bash
python3 -m venv .venv-runtime
./.venv-runtime/bin/python -m pip install -r runtime/requirements-build.txt
./.venv-runtime/bin/python scripts/build_runtime.py --output-dir dist --json
```

产物：

```text
dist/agent-skills-mcp
dist/agent-skills-mcp.manifest.json
```

PyInstaller 不是跨平台交叉编译器：Windows `.exe` 应在 Windows 构建，Linux/macOS 产物也应在对应平台构建。

Builder 会自动执行：

```text
canonical References
→ exact UTF-8 content/hash/size catalog
→ source_digest
→ JSON Bundle
→ AES-256-GCM
→ 临时 embedded payload module
→ PyInstaller --onefile
→ artifact status/self-test
→ artifact SHA256 manifest
```

构建过程不会修改 canonical Markdown，也不会把生成的 key/payload module 提交进仓库。

## 4. 验证构建产物

```powershell
.\dist\agent-skills-mcp.exe status --json
.\dist\agent-skills-mcp.exe self-test --json
.\.venv-runtime\Scripts\python.exe scripts\runtime_mcp_smoke.py --artifact .\dist\agent-skills-mcp.exe --json
```

POSIX：

```bash
./dist/agent-skills-mcp status --json
./dist/agent-skills-mcp self-test --json
./.venv-runtime/bin/python scripts/runtime_mcp_smoke.py --artifact ./dist/agent-skills-mcp --json
```

`runtime_mcp_smoke.py` 会真正通过 stdio MCP 建立 Client/Server 会话，检查五个 Tool、读取一个 Reference，并把返回的 `canonical_text` / SHA256 与源仓库 canonical Reference 对比。

## 5. 安装/升级用户级 Runtime

### Windows

```powershell
.\.venv-runtime\Scripts\python.exe scripts\install_runtime.py --artifact .\dist\agent-skills-mcp.exe --json
```

默认安装到：

```text
%LOCALAPPDATA%\AgentSkills\bin\agent-skills-mcp.exe
```

### Linux / macOS

```bash
./.venv-runtime/bin/python scripts/install_runtime.py --artifact ./dist/agent-skills-mcp --json
```

默认安装到：

```text
~/.local/share/agent-skills/bin/agent-skills-mcp
```

安装器会先验证源 artifact，再完整复制到同目录临时位置并再次验证；替换已有版本后还会再次执行 `status/self-test`。新版本验证失败时恢复旧文件。

也可以用 `--install-dir <path>` 指定用户级目录。

## 6. 注册到 Codex

推荐安装为用户级 MCP，让不同项目共用同一个 Runtime。

### CLI

Windows 示例：

```powershell
codex mcp add agent-skills -- "$env:LOCALAPPDATA\AgentSkills\bin\agent-skills-mcp.exe" serve
codex mcp list
```

Linux / macOS：

```bash
codex mcp add agent-skills -- "$HOME/.local/share/agent-skills/bin/agent-skills-mcp" serve
codex mcp list
```

也可以直接维护 `~/.codex/config.toml`：

```toml
[mcp_servers.agent-skills]
command = "/absolute/path/to/agent-skills-mcp"
args = ["serve"]
```

Windows TOML 中反斜杠需要按 TOML 字符串规则转义，或使用适合本机的绝对路径写法。

## 7. 注册到 Cursor

Cursor 支持本地 stdio MCP。全局配置放在：

```text
~/.cursor/mcp.json
```

示例：

```json
{
  "mcpServers": {
    "agent-skills": {
      "command": "/absolute/path/to/agent-skills-mcp",
      "args": ["serve"]
    }
  }
}
```

项目级配置可以放 `.cursor/mcp.json`，但本 Runtime 通常适合全局配置。可用 `cursor-agent mcp list` 和 `cursor-agent mcp list-tools agent-skills` 检查是否加载。

## 8. 注册到 Claude Code

Claude Code 支持本地 stdio MCP。可以用用户级配置：

```bash
claude mcp add-json agent-skills '{"type":"stdio","command":"/absolute/path/to/agent-skills-mcp","args":["serve"]}' --scope user
claude mcp get agent-skills
```

也可以把同等 `mcpServers` JSON 作为项目 `.mcp.json` 配置。若 shell 对 JSON 引号有特殊处理，优先使用 Claude Code 当前版本提供的配置命令或编辑配置文件，不要把 shell 转义问题误判为 Runtime 故障。

## 9. 把 Runtime 模式接入一个项目

先完成第 3–8 节：**Runtime 必须已经构建、安装并让宿主能看到 MCP Tools。** 然后从与 Runtime 同一个 canonical `Agent_Skills` 源版本执行：

### Windows

```powershell
.\.venv-runtime\Scripts\python.exe scripts\install.py `
  --mode runtime `
  --runtime-command "$env:LOCALAPPDATA\AgentSkills\bin\agent-skills-mcp.exe" `
  --target "D:\work\MyProject" `
  --json
```

### Linux / macOS

```bash
./.venv-runtime/bin/python scripts/install.py \
  --mode runtime \
  --runtime-command "$HOME/.local/share/agent-skills/bin/agent-skills-mcp" \
  --target /work/MyProject \
  --json
```

安装器在修改目标项目之前比较：

```text
当前源仓库 canonical References source_digest
=
已安装 Runtime status/self-test source_digest
```

不一致直接失败，避免“旧 Runtime + 新 Stub”混装。

Runtime 模式目标项目大致是：

```text
MyProject/
├── AGENTS.md
└── .agents/
    └── skills/
        ├── coding/
        │   ├── SKILL.md          # 原生 Core，完整保留
        │   ├── assets/
        │   ├── agents/
        │   ├── scripts/
        │   └── references/
        │       └── *.md          # 同名 Runtime Stub，不含 canonical 正文
        ├── review/
        └── docs/
```

目标项目已有 `.agents/changes/`、项目自有 Skill、其他 `.agents` 内容以及 `AGENTS.md` managed marker 外原文仍按现有 Bootstrap/rollback Contract 保护。

## 10. Agent 实际怎么使用

开发者仍然可以像以前一样提需求，例如：

```text
使用 coding，基于当前仓库真实实现完成这个功能。
```

正常链路：

1. Agent 读目标项目 `AGENTS.md`；
2. 读 `.agents/skills/coding/SKILL.md`；
3. Core Skill 根据当前项目事实和任务语义命中某个 Reference；
4. Agent 读取同名 stub；
5. stub 要求调用 `agent_skills_load_context`，例如 `coding.reference.07`；
6. MCP 返回 `canonical_text`、SHA256、filename；
7. Agent 校验 SHA256 与 stub 的 `Expected SHA256`，把 `canonical_text` 当作该 Reference 完整正式原文继续执行；
8. Review / Docs 发生路由时使用相同机制。

Runtime **不负责替 Codex 自动理解任意自然语言任务**，也不会把复杂规则摘要成 Guidance。第一版把新增失败点限制在“Reference 内容传输与完整性验证”。

## 11. Full 模式仍然保留

旧命令保持向后兼容：

```bash
python scripts/install.py --target <target>
```

等价于：

```bash
python scripts/install.py --mode full --target <target>
```

`full` 会像以前一样把完整三个 Skill（含 canonical References）复制到目标项目。如果你的首要目标只是最短加载链、完全不在意明文分发，可以继续使用它。

## 12. 后续升级

当你修改任一 canonical `SKILL.md` / `references/*.md`、Runtime 或安装规则后，Runtime 模式推荐按固定顺序升级：

```text
1. 更新本地 Agent_Skills 源仓库
2. 重新安装 runtime/requirements-build.txt（依赖变化时）
3. scripts/build_runtime.py 重新构建当前平台 artifact
4. scripts/install_runtime.py 原子升级用户级 Runtime
5. 对每个目标项目重新执行 scripts/install.py --mode runtime
6. 宿主重新建立 MCP 会话/重启相关 Agent（宿主需要时）
7. 用一次真实任务确认 Stub → load_context 链正常
```

Reference 正文变化会改变 `source_digest` 和对应 SHA256。旧 Runtime 与新源版本不匹配时，目标项目安装器会拒绝继续，而不是悄悄制造混合状态。

## 13. 回滚

用户级 Runtime 回滚必须和目标项目 Stub/Core 版本一起考虑：

```text
Runtime A source_digest
↔ Agent_Skills Source A
↔ Target Runtime Stubs A
```

如果只把 Runtime 降级到旧版本、目标项目仍是新 Stub，Reference SHA/ID 可能不匹配。最安全的回滚方式是：

1. 恢复到与旧 Runtime 对应的 Agent_Skills 源版本；
2. 安装旧 Runtime artifact；
3. 从该源版本重新执行 `install.py --mode runtime`；
4. 验证 MCP `status/self-test` 和目标 Stub hash。

## 14. ChatGPT 网页端边界

本 Runtime 是**本地 stdio MCP**。ChatGPT 网页端不能直接启动用户电脑上的本地 stdio 进程；网页端接入需要 Remote MCP 或受支持的安全隧道，这是另一种部署形态，不属于本 Runtime 第一版范围。
