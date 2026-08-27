# Agent Skills Runtime Binary

这份文档面向**实际使用 Agent Skills Runtime 的团队成员**。正式 Runtime 用户不需要访问或 clone `Agent_Skills` canonical 源仓库，也不需要 Python、pip、venv 或额外安装脚本。

你只需要拿到与你当前操作系统匹配的一个 binary，在需要接入 Agent Skills 的**目标项目根目录**运行它。

Runtime 的目标是：

```text
一个平台 binary
→ 安装当前项目自己的 Runtime
→ 安装当前 Release 自动发现的全部正式 Native Skill
→ canonical Reference 只安装 Stub
→ 建立 AGENTS.md 与项目级 MCP 配置
→ Codex / Cursor / Claude Code 共同使用当前项目 Runtime
```

详细 canonical `references/*.md` 正文不会作为普通 Markdown 文件落到目标项目；需要某个 Reference 时，Agent 通过本地 MCP `agent_skills_load_context` 取得对应 canonical 原文。

## 1. 从正式 GitHub Release 选择 binary

正式版本号来自仓库根 `VERSION`，Release tag 为 `v<VERSION>`。同一个正式团队 Release 提供：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
SHA256SUMS
```

Windows、Linux、macOS binary 不是跨平台通用文件；选择与你实际运行环境一致的资产。

下载后建议先按 `SHA256SUMS` 校验文件完整性。正式 Release 的 tag 和资产属于历史事实：升级下载更高版本的新 binary，回滚下载旧 Release 的同平台 binary；不要手工混装不同版本的 Runtime 与 Stub。

正式团队 Release **不同时发布包含 canonical Reference 明文的 Full Kit**。Full Distribution 是维护者/明确允许明文分发场景的独立兼容能力，不是 Runtime 团队用户入口。

## 2. Windows：项目根运行一次

假设你的业务项目是：

```text
D:\work\MyProject
```

把下载的 Windows binary 放到任意方便的位置；最简单可以临时放到项目根，然后执行：

```powershell
cd D:\work\MyProject
.\agent-skills-mcp-v<VERSION>-windows.exe
```

无参数运行默认安装/升级**当前工作目录**。

也可以显式指定目标项目：

```powershell
.\agent-skills-mcp-v<VERSION>-windows.exe install --target D:\work\MyProject
```

需要机器可读结果时：

```powershell
.\agent-skills-mcp-v<VERSION>-windows.exe install --target D:\work\MyProject --json
```

不需要：

```text
clone Agent_Skills
python
pip
venv
install_runtime.py
install_runtime_target.py
用户级 MCP Runtime
```

安装完成后，最开始下载的外部 `.exe` 不再是项目运行所必需的；当前项目会拥有自己的 Runtime 副本。

## 3. Linux / macOS

下载后如果文件没有执行位，先执行一次：

```bash
chmod +x ./agent-skills-mcp-v<VERSION>-linux
```

或 macOS：

```bash
chmod +x ./agent-skills-mcp-v<VERSION>-macos
```

然后进入目标项目根目录运行：

```bash
cd /work/MyProject
/path/to/agent-skills-mcp-v<VERSION>-linux
```

macOS 同理：

```bash
cd /work/MyProject
/path/to/agent-skills-mcp-v<VERSION>-macos
```

也可以显式：

```bash
/path/to/agent-skills-mcp-v<VERSION>-linux install --target /work/MyProject --json
```

## 4. 安装后项目里有什么

以 Windows 为例，目标项目大致会出现：

```text
MyProject/
├── AGENTS.md
├── CLAUDE.md
├── .gitignore
├── .mcp.json
├── .codex/
│   └── config.toml
├── .cursor/
│   └── mcp.json
└── .agents/
    ├── agent-skills-install.json
    ├── runtime/
    │   └── agent-skills-mcp.exe
    └── skills/
        ├── coding/
        │   ├── SKILL.md
        │   ├── assets/
        │   ├── scripts/
        │   └── references/*.md   # Runtime Stub，不含 canonical 正文
        ├── docs/
        ├── review/
        └── <未来 Release 中其他正式 Skill>/
```

Linux/macOS 项目 Runtime 文件名没有 `.exe`。

`.agents/runtime/` 是本机平台运行资产，安装器会增量加入 `.gitignore`，避免把 binary 误提交到业务仓库。

`.agents/agent-skills-install.json` 只记录 Agent_Skills 自己的安装 ownership、版本和摘要，帮助后续安全升级；它不是目标项目业务架构或需求事实源。

## 5. 未来新增 Skill 会自动进入 Release

Runtime Release 不维护固定 `coding/review/docs` 全量名单。构建时会从源仓库：

```text
.agents/skills/*/SKILL.md
```

动态发现全部合法正式 Skill。

因此以后维护者新增：

```text
.agents/skills/security/
.agents/skills/testing/
.agents/skills/architecture/
```

只要满足正式 Skill Contract，下一次 binary 会自动内嵌并安装这些 Skill。最终使用者不需要换安装方式，也不需要逐个指定 Skill。

当前 `coding / review / docs` 是仓库当前实际正式 Skill，不是 Runtime 中写死的永久名单。

## 6. canonical Reference 为什么看不到正文

每个正式 Skill 的 Core `SKILL.md` 和必要运行资产会进入项目，因为宿主需要它们完成原生 Skill/规则入口和任务路由。

详细 canonical Reference 则构建为 AES-256-GCM 加密 Bundle，嵌入 `agent-skills-mcp`。目标项目同名 `references/*.md` 只保留 Stub，例如包含：

```text
Runtime ID
Canonical filename
Expected SHA256
agent_skills_load_context 调用协议
```

正常链路：

```text
目标项目 AGENTS.md
→ Native Core SKILL.md
→ Core Skill 根据任务命中 Reference
→ 读取同名 Runtime Stub
→ Stub 要求调用 agent_skills_load_context
→ 项目 Runtime 解密并返回 canonical_text + SHA256
→ Agent 校验 Expected SHA256
→ 把 canonical_text 当作该 Reference 完整正式原文继续工作
```

如果 MCP 不可用、Reference ID 不存在、返回 SHA256 与 Stub 不一致，Agent 必须明确报告并停止依赖该 Reference 的动作，不能把 Stub、摘要或旧记忆当成规则正文。

## 7. Codex / Cursor / Claude Code

同一个项目 Runtime：

```text
.agents/runtime/agent-skills-mcp[.exe] serve
```

供三个宿主共同使用。安装器只创建**项目级**配置，不安装全局/用户级 Runtime。

### Codex

项目配置：

```text
.codex/config.toml
```

安装器在稳定 managed marker 中维护 `mcp_servers.agent-skills`，保留其他项目 TOML 文本。

Codex 是否加载项目 `.codex/config.toml` 还受 Codex 自己的 workspace trust 安全机制约束。首次打开项目时如果宿主要求 Trust/Approval，应按宿主提示处理；Agent Skills 不绕过这个安全边界。

### Cursor

项目配置：

```text
.cursor/mcp.json
```

安装器只认领：

```text
mcpServers.agent-skills
```

其他 MCP server 和 JSON 字段保留。

### Claude Code

项目 MCP：

```text
.mcp.json
```

Claude Code 使用 `CLAUDE.md` 作为项目规则入口，因此安装器还会维护一个很薄的 bridge：

```markdown
@AGENTS.md
```

它只复用同一个 `AGENTS.md`，不复制第二套 Agent Skills 规则。已有 `CLAUDE.md` 用户内容保留，Agent Skills 只维护自己的 marker block。

不同宿主可能要求首次批准项目 MCP；这是宿主自身安全机制，不是 Runtime 故障。

## 8. 目标项目已有 Skill 或配置时怎么处理

安装器不会把 `.agents/skills/` 当成可以整体清空的目录。

### 项目自有不同名 Skill

例如项目原有：

```text
.agents/skills/company-internal/
```

而当前 Release 包含：

```text
coding
docs
review
security
```

安装后 `company-internal` 保留。

### 首次安装已有同名 Skill

如果目标项目已经存在：

```text
.agents/skills/security/
```

但 `.agents/agent-skills-install.json` 不能证明它是旧 Agent_Skills 版本安装的，安装会停止并报告同名冲突，不会猜测性覆盖项目资产。

### 升级时 Release 删除旧 Skill

只有旧 install manifest 明确认领过的 Skill，在新 Release 已经移除时才允许被删除。项目自有 Skill 不因 Agent_Skills 升级被清理。

### 宿主已有同名 MCP

如果项目配置里已经有未被 Agent Skills ownership 认领的 `agent-skills` MCP server，安装器拒绝静默覆盖。先由项目 Owner 明确归属，再重新安装。

## 9. AGENTS 与项目原文保护

目标项目已有 `AGENTS.md` 时，安装器只管理：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

marker 前后项目原文保持。只有 start、只有 end、marker 逆序或重复时，安装会失败，不猜测“哪段可能是旧 Agent Skills 内容”。

目标项目没有 `AGENTS.md` 时，安装器使用内嵌模板创建最小 Overlay，只列当前真实存在的事实入口，不会因为看到 `package.json`、`pyproject.toml`、migration 文件就自动宣布项目使用 React、FastAPI 或 PostgreSQL。

## 10. 验证当前 binary

不安装项目也可以检查下载的 binary：

Windows：

```powershell
.\agent-skills-mcp-v<VERSION>-windows.exe status --json
.\agent-skills-mcp-v<VERSION>-windows.exe self-test --json
```

Linux/macOS：

```bash
./agent-skills-mcp-v<VERSION>-linux status --json
./agent-skills-mcp-v<VERSION>-linux self-test --json
```

`status` / `self-test` 会报告 Release Version、动态 Skill 集合、Reference `source_digest`、Project Payload `payload_digest` 等元数据，不返回 canonical Reference 正文。

安装后还可以对项目 Runtime 执行同样检查：

```text
<项目>/.agents/runtime/agent-skills-mcp[.exe] status --json
<项目>/.agents/runtime/agent-skills-mcp[.exe] self-test --json
```

## 11. 后续升级

维护者发布新版本后：

```text
1. 下载当前操作系统的新 binary
2. 校验 SHA256SUMS
3. 在同一个目标项目根重新运行新 binary
4. binary 根据旧 install manifest 判断 ownership
5. 原子升级项目 Runtime、全部受管 Skill/Stub 和 managed 配置
6. 宿主需要时重新打开项目或重连 MCP
7. 用真实开发任务验证一次 Stub → agent_skills_load_context → canonical_text
```

不再存在“先升级用户级 Runtime，再分别刷新项目 Stub”的两阶段安装。

## 12. 回滚

完整版本关系是：

```text
Runtime binary A
↔ source_digest A
↔ payload_digest A
↔ Target managed Skill / Stub A
```

回滚时：

1. 下载旧 Release 的同平台 binary；
2. 校验旧 checksum；
3. 在目标项目根运行旧 binary；
4. 由旧 binary 按 managed manifest 恢复该版本的 Runtime/Skill/Stub/配置；
5. 检查项目 Runtime `status/self-test`；
6. 重新建立 MCP 会话并做一次真实 Reference 加载。

不要只手工替换 `.agents/runtime/agent-skills-mcp`，也不要只手工改 Stub；这样可能制造版本混装。

## 13. 安全边界

`agent-skills-mcp[.exe]` 中包含 AES-256-GCM 加密的 canonical Reference Bundle。它的目标是：

- 团队成员不需要访问 Agent_Skills 源仓库；
- 目标项目不直接保存 canonical Reference 明文；
- 降低普通浏览、复制和传播规则正文的便利程度。

它**不是** TEE/KMS 意义上的不可提取秘密保护。因为 Runtime 必须在本机解密后把 `canonical_text` 交给 Agent，所以拥有机器高级控制权的人理论上仍可能通过逆向、调试器、进程 Hook、内存转储或 MCP 通信观测取得运行时明文。

不要对这个 binary 宣称“本机管理员绝对无法读取规则”。

## 14. ChatGPT 网页端边界

本 Runtime 是本地 stdio MCP。ChatGPT 网页端不能直接启动你电脑上的本地 stdio 进程；网页端需要 Remote MCP 或受支持的安全隧道，是另一种部署方案，不属于当前 Runtime binary。

## 15. 对维护者

最终使用者只需要 binary；只有维护 `Agent_Skills` 源仓库的人需要 Python 构建环境。

当前平台本地预构建：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

Windows 输出：

```text
dist\agent-skills-mcp.exe
dist\agent-skills-mcp.manifest.json
```

Linux/macOS 输出：

```text
dist/agent-skills-mcp
dist/agent-skills-mcp.manifest.json
```

`manifest.json` 是维护者构建验证资料，不是正式团队 Release 必须下载的第二个安装文件。正式 Release workflow 会在 Linux、Windows、macOS 分别重新构建和验证 binary，再发布平台文件和 `SHA256SUMS`。
