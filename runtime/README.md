# Runtime 源码维护说明

`runtime/` 实现 Agent_Skills 当前唯一正式对外分发形态：**项目级 onefile Runtime + Native Core Skill + Shared Skill Router + Encrypted Canonical References + local stdio MCP**。

最终使用者不需要阅读本文件；下载、安装、升级、回滚和排障见根 [`USAGE.md`](../USAGE.md)。

## 1. 模块职责

```text
agent_skills_runtime/skill_catalog.py
→ 动态发现 .agents/skills/*/SKILL.md 下的正式 Skill

agent_skills_runtime/catalog.py
→ 收集 canonical References，并构建 Bundle v2 / source_digest / bundle identity

agent_skills_runtime/routing.py
→ 从 canonical Markdown 编译/校验私有 Routing Manifest，生成公共 route contract，并用唯一 evaluator 求值

agent_skills_runtime/crypto.py
→ AES-GCM 加密/认证 Reference Bundle

agent_skills_runtime/project_payload.py
→ 构建 Skills 根级共享运行资产与各 Skill Core/运行资产；显式禁止 Reference/Stub

agent_skills_runtime/project_installer.py
→ install v3 逐文件 ownership、宿主配置与回滚；非 v3 manifest 直接拒绝

agent_skills_runtime/runtime.py
→ 维护 task/route token、单调 required Context、渐进式披露与 checkpoint

agent_skills_runtime/server.py
→ CLI + stdio MCP Server
```

Runtime 不负责重新解释 Coding / Review / Docs / Figma 规则；跨 Skill 发现与 Handoff 由 `.agents/skills/ROUTER.md` 唯一负责，各 Skill 完整专业语义仍由自己的 `SKILL.md` 和 canonical `references/*.md` 定义。

## 2. 三个独立完整性域

Reference Bundle：

```text
canonical Reference bytes
→ 显式 Stable ID / source_path / sha256 / size
→ source_digest

canonical SKILL/Reference metadata
→ 规范化 Skill/Reference trigger / dependency / risk floor
→ private Routing Manifest / routing_digest

Reference Bundle v2
→ canonical bytes + private Routing Manifest
→ bundle_version
→ AES-GCM authenticated envelope
```

Project Payload：

```text
shared_files（当前 ROUTER.md）
+ Native Core / assets / scripts / metadata
→ path / sha256 / size / mode
→ payload_digest
```

`source_digest`、`routing_digest` 和 `payload_digest` 证明不同事实，不能互相替代。`shared_files` 是显式 Contract，不代表 Skills 根目录任意文件都会自动进入 Payload。

Project Payload 明确排除：

- canonical `references/*.md` 和 Runtime Stub；
- private Routing Manifest；
- 任意深度的维护 `README.md`；
- tests；
- Python cache/编译产物。

因此像 `coding/scripts/tzdata/README.md` 这种源码维护说明可以留在私有源仓库，但不会安装到目标项目；真正运行需要的 `coding/scripts/tzdata/zoneinfo/Asia/Shanghai` 等资源和 Skills 根级 `.agents/skills/ROUTER.md` 仍会进入 Payload。

目标项目没有 Agent_Skills `references/`。Source Mode 直接读取源仓库 required References；Runtime Mode 通过中文 Task Route 和当前不透明 route token 取得 required 完整原文。

## 3. 项目安装边界

onefile binary 无参数运行默认安装/升级当前目录；也支持：

```text
agent-skills-mcp install --target <project-root>
```

当前 Project Payload 使用 v2，install manifest 使用 v3 `managed_files` 逐文件 Contract。安装器只接受当前 v3 manifest；v1、v2、未知或损坏 schema 全部失败关闭，不扫描旧 Stub，也不根据旧目录结构推断 ownership。

项目安装需要保持：

- `.agents/agent-skills-install.json` 用 `managed_files` 认领 Agent_Skills 可证明的具体文件，并另列公开 Skill/`shared_files`；
- 首次同名未认领 Skill 或 shared file 均 fail closed；
- 新 Release 删除文件时只删除旧 v3 `managed_files` 明确认领项，不替换整棵 Skill 目录；
- `.agents/runtime/` 为项目本地运行资产并加入 `.gitignore`；
- `AGENTS.md` / CLAUDE / Codex 使用 managed marker；
- 目标项目 `AGENTS.md` managed block 只做薄 Bootstrap，并指向 `.agents/skills/ROUTER.md`；
- Cursor/Claude JSON 只认领 `mcpServers.agent-skills`；
- marker 外项目文本、其他 MCP server、项目自有 Skill/Reference/资产和未认领 shared file 保留；
- 任一可预检错误先于写入发现；失败按 bytes/权限快照恢复 touched managed files、Runtime、manifest 与受管文本。

正式 Skill 仍通过动态 Catalog 分发；Skills 根级共享文件只通过 Project Payload 的显式 `shared_files` Contract 分发，二者职责不混淆。

## 4. MCP Contract

稳定工具：

```text
agent_skills_status
agent_skills_route_contract
agent_skills_start_task
agent_skills_submit_route
agent_skills_load_required_context
agent_skills_checkpoint
```

`route_contract` 只公开当前中文词汇和 Skill，不公开 Reference mapping；`submit_route` 通过唯一 evaluator 计算并单调扩展当前 required Context；`load_required_context` 只接受当前 route token，默认只返回尚未加载的 required 完整原文。Runtime 不提供 public manifest 或 arbitrary-ID load。

`checkpoint` 不接受 required IDs，只检查本 MCP 进程内部状态，不能替代 Requirement Traceability、Completion Audit、Review、Docs Impact 或真实测试。Task Route 的授权字段只是数据，不能产生 Git、发布或部署权限。

## 5. 本地构建

安装维护者构建依赖：

```bash
python3 -m pip install -r runtime/requirements-build.txt
```

构建当前平台 onefile：

```bash
python3 scripts/build_runtime.py --output-dir dist --json
```

构建器会读取根 `VERSION` 和真实 source commit，动态发现 Skill/Reference，编译 canonical metadata，构建/加密 Bundle v2 与 no-Stub Project Payload，生成当前平台 artifact，并执行 `status` / `self-test` 校验。构建目录中的 `.manifest.json` 是 CI 校验用 Release identity，不包含 Reference Catalog，也不作为正式 GitHub Release 资产发布。

“最新规则模式”允许网页端 Source Mode 读取当前 `main`、本地 Runtime 使用当前最新 Release，但二者在发布间隙可能短暂不同步；“精确复现模式”必须让 Source Mode 读取 Runtime `status --json` 中 `source_commit` 对应的 Release tag/commit，并使用同一 Release Runtime。

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

该 smoke 使用真实 stdio MCP client 验证六个 Tool、中文 input schema、route contract、submit、required Context exact-text/hash 和 checkpoint，不用内部 Python 函数调用冒充 MCP 边界。

## 7. 永久 CI

`.github/workflows/skill-tests.yml` 负责持续验证：

- self-contained unit/preservation/portability tests；
- 唯一 Skills 根级 Router / 双 Bootstrap / Maintenance 职责与 Project Payload shared-file 分发；
- metadata compiler/evaluator、Routing Conformance、private manifest/encryption parity；
- install v3 ownership、非 v3 schema 拒绝、项目自有 Reference 保留、同名冲突和失败回滚；
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
