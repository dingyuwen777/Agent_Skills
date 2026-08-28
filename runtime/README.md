# Runtime 源码维护说明

`runtime/` 实现 Agent_Skills 当前唯一正式对外分发形态：**项目级 onefile Runtime + Native Core Skill + Encrypted Canonical References + local stdio MCP**。

最终使用者不需要阅读本文件；下载、安装、升级、回滚和排障见根 [`USAGE.md`](../USAGE.md)。

## 1. 模块职责

```text
agent_skills_runtime/skill_catalog.py
→ 动态发现 .agents/skills/*/SKILL.md 下的正式 Skill

agent_skills_runtime/catalog.py
→ 收集 canonical References、稳定 ID、SHA/size 与 source_digest

agent_skills_runtime/crypto.py
→ AES-GCM 加密/认证 Reference Bundle

agent_skills_runtime/project_payload.py
→ 构建目标项目需要的 Core/运行资产与 Reference Stub payload

agent_skills_runtime/project_installer.py
→ 项目级安装、ownership、AGENTS/.gitignore/宿主配置与回滚

agent_skills_runtime/runtime.py
→ 加载、校验加密 Bundle 与 Project Payload

agent_skills_runtime/server.py
→ CLI + stdio MCP Server
```

Runtime 不负责重新解释 Coding / Review / Docs / Figma 规则；完整语义仍由各 Skill 的 `SKILL.md` 和 canonical `references/*.md` 定义。

## 2. 两个完整性域

Reference Bundle：

```text
canonical Reference bytes
→ id / source_path / sha256 / size
→ source_digest
→ AES-GCM envelope
```

Project Payload：

```text
Native Core / assets / scripts / metadata
+ 同名 Reference Stub
→ path / sha256 / size / mode
→ payload_digest
```

`source_digest` 和 `payload_digest` 证明不同事实，不能互相替代。

Project Payload 明确排除：

- canonical `references/*.md` 正文；
- Skill 顶层 `README.md`；
- tests；
- Python cache/编译产物。

目标项目 Stub 只能保存逻辑 ID、Expected SHA256 和 MCP 加载协议，不复制摘要版规则。

## 3. 项目安装边界

onefile binary 无参数运行默认安装/升级当前目录；也支持：

```text
agent-skills-mcp install --target <project-root>
```

项目安装需要保持：

- `.agents/agent-skills-install.json` 只认领 Agent_Skills 自己可证明的 Skill；
- 首次同名未认领 Skill fail closed；
- 新 Release 删除 Skill 时只删除旧 manifest 明确认领项；
- `.agents/runtime/` 为项目本地运行资产并加入 `.gitignore`；
- `AGENTS.md` / CLAUDE / Codex 使用 managed marker；
- Cursor/Claude JSON 只认领 `mcpServers.agent-skills`；
- marker 外项目文本、其他 MCP server、项目自有 Skill 保留；
- 任一可预检错误先于写入发现；切换后的失败按快照恢复。

## 4. MCP Contract

稳定工具：

```text
agent_skills_status
agent_skills_manifest
agent_skills_start_task
agent_skills_load_context
agent_skills_checkpoint
```

其中 `agent_skills_load_context` 只接受稳定逻辑 ID，返回 canonical `sha256 / size / canonical_text`。它不接受任意路径/glob，也不自动摘要规则。

`checkpoint` 只检查本 MCP 进程内 required ID 是否已经 load，不能替代 Requirement Traceability、Completion Audit、Review、Docs Impact 或真实测试。

## 5. 本地构建

安装维护者构建依赖：

```bash
python3 -m pip install -r runtime/requirements-build.txt
```

构建当前平台 onefile：

```bash
python3 scripts/build_runtime.py --output-dir dist --json
```

构建器会读取根 `VERSION`，动态发现 Skill，构建/加密 Bundle 与 Project Payload，生成当前平台 artifact，并执行 `status` / `self-test` 校验。

Linux/macOS 默认产物：

```text
dist/agent-skills-mcp
dist/agent-skills-mcp.manifest.json
```

Windows：

```text
dist/agent-skills-mcp.exe
dist/agent-skills-mcp.manifest.json
```

## 6. 真实 MCP 验证

```bash
python3 scripts/runtime_mcp_smoke.py --artifact dist/agent-skills-mcp --json
```

该 smoke 使用真实 stdio MCP client 验证 tools/list、tools/call 和 canonical Reference 加载，不用内部 Python 函数调用冒充 MCP 边界。

## 7. 永久 CI

`.github/workflows/skill-tests.yml` 负责持续验证：

- self-contained unit/preservation/portability tests；
- Linux onefile build/status/self-test；
- real stdio MCP；
- project-only single-binary 首次安装、升级和无参数安装；
- 项目内 Runtime status/MCP smoke；
- Windows onefile + 项目安装；
- macOS onefile + 项目安装；
- Active Change Ready Check。

不同平台必须使用对应 Runner，不能把一个平台的 PyInstaller artifact 当跨平台二进制。

## 8. 正式 Release

正式 Release 由根 `.github/workflows/release.yml` 从 `main` 手工构建。最终用户资产和使用方式以根 [`USAGE.md`](../USAGE.md) 为准。

本文件不维护第二份最终用户教程，也不记录 Change/PR/Release 历史流水账。

## 9. 安全边界

onefile + AES-GCM 的目标是减少目标项目中的普通明文浏览/复制面，并检测 Bundle 篡改；它不是 TEE/KMS。

不能宣称能够抵御机器 Owner、调试器、内存转储、进程 Hook、MCP 通信观测或专业逆向。真正限制谁能读取 canonical 源文件，必须依赖源仓库访问控制。