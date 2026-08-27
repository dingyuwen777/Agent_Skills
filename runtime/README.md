# Agent Skills Local MCP Runtime

本目录实现 `Agent_Skills` 的本地 MCP Runtime。当前正式方向是：**动态发现全部正式 Skill，把 Native Core/运行资产作为 Project Payload 与加密 canonical Reference Bundle 一起嵌入当前平台 onefile；最终用户只拿一个 binary，在目标项目根完成项目级安装。**

Runtime 的目标不是把复杂 Markdown 规则改写成布尔 Policy，也不是维护第二套研发规则。

正式规则事实源始终是：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
```

当前仓库实际正式 Skill 是 `coding / docs / review`；Runtime 不把这三个名称作为永久全量名单。未来 `.agents/skills/*/SKILL.md` 下新增合法正式 Skill 后，应由统一 Skill Catalog 自动进入 Bundle/Project Payload/安装/Release。

详细规范见 [`../.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md`](../.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md)。最终用户说明见 [`../docs/distribution/runtime-kit.md`](../docs/distribution/runtime-kit.md)。

## 1. 运行模型

```text
目标项目 AGENTS.md
→ Native Core SKILL.md
→ Core Skill 按任务语义判断需要哪个 Reference
→ 读取目标项目中的同名 Runtime Stub
→ Stub 要求调用 agent_skills_load_context
→ 项目 .agents/runtime/agent-skills-mcp[.exe] 解密内嵌 Bundle
→ 返回 canonical Reference 原文 + SHA256
→ Agent 校验 hash 后把原文作为当前阶段正式规则上下文继续工作
```

`SKILL.md` 和必要运行资产继续明文进入 Project Payload，是为了保留宿主原生 Skill/Rules 入口和复杂任务路由效果。详细 `references/*.md` 在 Runtime 模式下只以 Stub 形式进入目标项目。

## 2. 核心模块

```text
runtime/agent_skills_runtime/
├── skill_catalog.py       # 动态发现/验证全部正式 Skill
├── catalog.py             # canonical Reference Bundle / public manifest
├── crypto.py              # AES-256-GCM envelope
├── project_payload.py     # Core/运行资产 + Reference Stub Project Payload
├── project_installer.py   # 项目级安装、ownership、回滚、宿主配置
├── runtime.py             # RuntimeStore / MCP 上下文状态
└── server.py              # 无参数 install、显式 install/status/self-test/serve
```

构建脚本：

```text
scripts/build_runtime.py
```

真实 stdio MCP smoke：

```text
scripts/runtime_mcp_smoke.py
```

`scripts/install_runtime.py` / `scripts/install_runtime_target.py` 可以暂时作为历史维护/兼容代码存在，但**不再属于正式团队 Runtime 用户安装链**。新 Runtime/Release/文档/CI 不得重新依赖它们作为最终用户前置步骤。

## 3. Dynamic Skill Catalog

正式 Skill 由：

```text
.agents/skills/*/SKILL.md
```

动态发现。

统一发现规则包括：

- 只接受一级真实目录；
- Skill 目录和 `SKILL.md` 不跟随符号链接；
- 名称使用稳定小写标识符；
- 有 YAML frontmatter 时唯一 `name` 必须与目录名一致；
- Skill 可以没有 `references/`；
- `references/` 存在时按当前 Contract 枚举直接 Markdown 文件；
- 结果确定性排序。

Builder、Reference Bundle、Project Payload、源安装器、Full Kit 和测试共用这一发现语义。不要在任何一层重新引入 `MANAGED_SKILLS = ("coding", "review", "docs")` 一类静态完整名单。

## 4. Reference Bundle 与 Project Payload

### Reference Bundle

canonical `references/*.md`：

```text
原始 UTF-8 bytes
→ id / source_path / SHA256 / size / content
→ source_digest
→ AES-256-GCM envelope
```

Runtime 返回的 `canonical_text` 必须与源 Reference UTF-8 解码结果逐字一致。

### Project Payload

正式 Skill 中除明确维护期内容和 canonical `references/` 正文外的运行资产：

```text
path / size / SHA256 / mode / content
→ payload_digest
```

canonical Reference 位置改写为同名 Stub。当前明确排除：

```text
top-level README.md
tests/
canonical references/
__pycache__/
*.pyc
*.pyo
```

其他真实运行资产默认随 Payload 进入 binary，避免维护不断扩展的 `RUNTIME_CORE_ENTRIES` 白名单。

## 5. 安全边界

Runtime 使用 AES-256-GCM 加密 Reference Bundle，并用 PyInstaller 打成当前平台 onefile。目标是：

- 团队成员不需要访问 Agent_Skills 源仓库；
- 目标项目不保存 canonical Reference 明文；
- 降低普通浏览、复制和传播规则正文的便利程度；
- 密文篡改能被认证失败检测。

这**不是**针对机器 Owner 的强保密方案。单文件程序必须在本机解密 Reference 才能把原文交给 Codex/Cursor/Claude Code，因此具备调试、内存转储、进程 Hook、MCP 通信观测或二进制逆向能力的机器 Owner 理论上仍可以取得运行时明文。

不要把当前方案宣传成 TEE、HSM 或“本机管理员绝对无法提取”。

## 6. 构建当前平台 Runtime

维护者使用仓库固定的构建依赖：

```text
runtime/requirements.txt
runtime/requirements-build.txt
```

Windows 构建环境仍需要 `tzdata` 等工具依赖，因为目标项目安装生成的 Coding 资产和现有测试使用 `Asia/Shanghai` IANA 时区语义；这些是**维护者构建依赖**，不是最终用户依赖。

### Windows PowerShell

```powershell
py -3.12 -m venv .venv-runtime
.\.venv-runtime\Scripts\python.exe -m pip install -r runtime\requirements-build.txt
.\.venv-runtime\Scripts\python.exe scripts\build_runtime.py --output-dir dist --json
```

输出：

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

输出：

```text
dist/agent-skills-mcp
dist/agent-skills-mcp.manifest.json
```

PyInstaller 不是跨平台交叉编译器：Windows `.exe` 应在 Windows 构建，Linux/macOS binary 也必须在对应平台构建和验证。

## 7. Builder 做什么

`scripts/build_runtime.py` 当前链路：

```text
VERSION
+
Dynamic Skill Catalog
        ↓
canonical References
→ exact UTF-8 content/hash/size
→ source_digest
→ AES-256-GCM
        +
Project runtime files
→ Reference Stub
→ path/hash/size/mode
→ payload_digest
        ↓
临时 _embedded_payload.py
        ↓
PyInstaller --onefile
        ↓
artifact status/self-test
        ↓
交叉校验 VERSION / skills / source_digest / payload_digest
        ↓
维护者 manifest
```

构建过程不会修改 canonical Markdown，也不会把生成的 key/embedded payload module 提交进仓库。

`agent-skills-mcp.manifest.json` 用于维护者构建验证，不是最终团队 Release 必须携带的第二个安装文件。

## 8. 验证构建产物

Windows：

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

`runtime_mcp_smoke.py` 会真正通过 stdio MCP 建立 Client/Server 会话，检查稳定 Tool Contract，读取一个 Reference，并把返回 `canonical_text` / SHA256 与源仓库 canonical Reference 对比。

## 9. 最终 onefile 项目安装验证

不能只验证 `status/self-test`。平台 artifact 还必须直接安装真实临时项目。

例如 Linux/macOS：

```bash
target="$(mktemp -d)"
./dist/agent-skills-mcp install --target "$target" --json
./dist/agent-skills-mcp install --target "$target" --json
"$target/.agents/runtime/agent-skills-mcp" status --json
python scripts/runtime_mcp_smoke.py --artifact "$target/.agents/runtime/agent-skills-mcp" --json
```

还要单独验证无参数当前目录安装：

```bash
cd <empty-target>
/path/to/dist/agent-skills-mcp
```

Windows 使用同等 PowerShell 流程。

至少检查：

- `.agents/runtime/agent-skills-mcp[.exe]`；
- `.agents/agent-skills-install.json`；
- 动态正式 Skill 全部存在；
- canonical Reference 只安装 Stub；
- `AGENTS.md` managed marker 幂等；
- `.gitignore` 忽略 project-context 与 Runtime；
- `.codex/config.toml`；
- `.cursor/mcp.json`；
- `.mcp.json`；
- `CLAUDE.md` 的 `@AGENTS.md` bridge；
- 项目内 Runtime 真实 MCP smoke。

## 10. 项目级安装 ownership

Runtime installer 使用：

```text
.agents/agent-skills-install.json
```

证明上一版本哪些 Skill 属于 Agent_Skills。

规则：

- 首次安装已有未认领同名 Skill：fail closed；
- 升级替换旧 manifest 已认领 Skill；
- 新 Release 删除 Skill：只删除旧 manifest 已认领项；
- 项目其他 Skill 不清理；
- AGENTS/Codex/Claude marker 外用户文本不重写；
- JSON MCP 只认领 `mcpServers.agent-skills`；
- 受管路径为 symlink、marker 损坏、JSON 不可安全解析时在可预检阶段失败；
- 切换中失败恢复本轮 Runtime/Skill/文本快照。

完整规则见 Reference 13/14。

## 11. 项目宿主接入

安装后的三个宿主都指向当前项目：

```text
.agents/runtime/agent-skills-mcp[.exe] serve
```

- Codex：`.codex/config.toml`；项目配置仍受 Codex workspace trust 约束；
- Cursor：`.cursor/mcp.json`；
- Claude Code：`.mcp.json` + `CLAUDE.md` 中 `@AGENTS.md` bridge。

这些配置只是 MCP 传输适配，不复制第二套 Skill 规则。

宿主安全确认、workspace trust 或项目 MCP approval 不属于 Runtime 可以绕过的边界。

## 12. MCP 正常任务生命周期

开发者正常提需求，不需要人工枚举 Reference ID。

```text
Agent 读 AGENTS.md
→ 读 Core SKILL.md
→ Core 根据项目事实/任务触发某个 Reference
→ 读同名 Stub
→ agent_skills_load_context(ids)
→ 校验 Expected SHA256
→ 使用 canonical_text
```

可选任务状态：

```text
agent_skills_start_task
agent_skills_checkpoint
```

它们只记录 Reference 是否已加载，不能替代 Requirement Traceability、Completion Audit、Review、Docs 或真实测试。

## 13. Full/source 兼容模式

源码仓库仍保留：

```bash
python scripts/install.py --target <target>
```

用于完整 Markdown 分发。它会动态发现全部正式 Skill并复制 canonical References。

Full Kit Builder：

```bash
python scripts/build_full_distribution.py --output-dir dist --json
```

也继续作为维护者/兼容能力进入永久 CI。

但正式团队 Runtime Release 不发布 Full Kit，因为它包含 canonical Reference 明文；也不把 `scripts/install.py --mode runtime` 重新当作最终用户路径。

## 14. 正式 Release

当前正式团队 Release 资产：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
SHA256SUMS
```

Release Workflow 在三个目标平台重新构建 onefile，执行 `status/self-test`、真实 stdio MCP 和真实项目安装，再把通过验证的 binary 交给 Publish Job。

详细维护流程见 [`../docs/maintainers/releasing.md`](../docs/maintainers/releasing.md)。

## 15. 升级与回滚

最终用户升级：

```text
新版本 binary
→ 在同一个项目根重新运行
→ 根据旧 install manifest 判断 ownership
→ 更新项目 Runtime + Skill/Stub + managed 配置
```

完整版本关系：

```text
Runtime binary
↔ Release Version
↔ source_digest
↔ payload_digest
↔ 项目受管 Skill / Stub
```

回滚使用旧 Release 的同平台 binary 在目标项目根重新运行。不要只替换 `.agents/runtime/` binary 或只回退 Stub。

## 16. ChatGPT 网页端边界

本 Runtime 是**本地 stdio MCP**。ChatGPT 网页端不能直接启动用户电脑上的本地 stdio 进程；网页端接入需要 Remote MCP 或受支持的安全隧道，是另一种部署形态，不属于当前 Runtime。
