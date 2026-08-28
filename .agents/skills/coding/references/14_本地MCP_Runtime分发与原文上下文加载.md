# 本地 MCP Runtime 分发与原文上下文加载

这份规则定义 Agent_Skills 当前唯一正式对外分发模式：**Native Core Skill + Project-local MCP Runtime + Encrypted Canonical References + onefile binary**。

目标是：最终使用者只拿到对应平台 Release binary，在目标项目根运行即可完成项目级接入；详细 canonical `references/*.md` 不作为普通 Markdown 分发到目标项目，同时保持现有自然语言 Skill 的执行语义和逐字完整性。

本文件只规定 Runtime 分发、动态 Skill 发现、Project Payload、Reference 原文加载、项目级安装/升级、宿主接入、完整性、Release 和失败边界。Coding / Review / Docs / Figma 的研发语义仍由各自 `SKILL.md` 与 canonical References 定义。

## 1. 何时必须读取

出现以下任务时必须读取本文件：

- 构建、Release、安装或升级 `agent-skills-mcp`；
- 修改 Project Payload、动态 Skill Catalog、installation manifest 或项目宿主 MCP 配置；
- 修改 Runtime Bundle schema、Reference ID、加密格式、MCP Tool Contract、Stub、`source_digest` 或 `payload_digest`；
- 调试目标项目 Reference Stub → MCP canonical 原文链；
- Review Runtime 是否仍逐字返回 canonical Reference；
- 修改正式 Skill，使新 Skill/资产自动进入下一次 Runtime Release；
- 修改 onefile 项目安装、升级、rollback 或 fail-closed ownership 逻辑。

## 2. 设计目标与非目标

### 目标

```text
Agent_Skills 源仓库 .agents/skills/*
→ 构建时动态发现正式 Skill

Native Core / 必要运行资产
→ 构建成 Project Payload
→ 随 onefile Runtime 嵌入
→ 安装到目标项目 .agents/skills/

canonical references/*.md
→ 唯一完整 Reference 正文
→ 构建时逐字收集、hash、AES-256-GCM 加密
→ 嵌入 Runtime

目标项目 Reference Stub
→ 保持 canonical 文件名和相对链接可达
→ 只声明 Runtime ID + Expected SHA256 + 加载协议

Project-local Runtime
→ 安装在目标项目 .agents/runtime/
→ Codex / Cursor / Claude Code 只配置当前项目 Runtime

Local MCP
→ 按稳定逻辑 ID 返回 canonical_text
→ 不摘要、不重写、不生成新的研发规则
```

最终使用者不需要：

- clone Agent_Skills 源仓库；
- Python、pip、venv；
- 外部安装脚本；
- Runtime Kit ZIP；
- 用户级或全局 Runtime 前置安装。

### 非目标

- 不把 Markdown Skill 改写成 Policy DSL、布尔规则数据库或另一套 prompt 系统；
- 不让 Runtime 自己成为第二个 Coding Agent；
- 不自动扫描整个目标项目替 Agent 判断架构/业务语义；
- 不提供任意路径读取、glob 或批量导出 canonical 规则接口；
- 不承诺抵御机器 Owner、调试器、内存转储、进程 Hook 或专业逆向；
- 不用 Runtime 替代项目 `AGENTS.md`、CI、PR、Review、Migration、安全和授权门禁；
- 不把网页端 Remote MCP / secure tunnel 混进本地 stdio Runtime；
- 不在本规则建立在线许可证、远程 KMS 或自动更新服务。

## 3. 动态正式 Skill Catalog

Runtime、Project Payload、manifest、测试和 Release **不得维护固定完整 Skill 名单**。

正式 Skill 从：

```text
.agents/skills/<skill-name>/SKILL.md
```

动态发现。`runtime/agent_skills_runtime/skill_catalog.py` 至少保持：

1. 只发现 `.agents/skills/` 一级真实目录；
2. Skill 目录和 `SKILL.md` 不能是符号链接；
3. `SKILL.md` 必须是普通 UTF-8 文件；
4. Skill 名使用稳定小写标识符；
5. frontmatter 存在时 `name` 唯一且与目录名一致；
6. Skill 可以没有 `references/`；
7. `references/` 存在时只接受当前 Contract 支持的普通 Markdown，不通过特殊文件/符号链接越界；
8. 发现结果确定性排序。

`coding` 仍是当前目标项目 AGENTS Bootstrap 的核心锚点。改变这一上位入口关系属于独立架构变化，不能借动态发现静默修改。

## 4. 唯一规则事实源

每个正式 Skill 的规则事实源：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
```

Builder 读取 canonical References 时：

- 不修改源文件；
- 不标准化换行；
- 不去标题/frontmatter；
- 不摘要；
- Bundle entry `content` 来自原始 UTF-8 bytes 直接 decode；
- SHA256 与 size 对应同一份原始 bytes。

Runtime Stub 不是规则事实源，只负责把 Core Skill 中原有相对链接接到 MCP canonical 原文加载能力。

## 5. Native Core 为什么继续明文

Core `SKILL.md` 负责：

- 让支持 Skill/Rules/AGENTS 的宿主在任务开始进入正确工作流；
- 恢复项目事实并完成任务/风险/工具链路由；
- 决定何时必须读取某个 Reference；
- 在 Skill 之间显式路由；
- 保留 Reference 缺失/加载失败时的停止条件和完成门禁。

如果 Core 也完全隐藏，只留下 MCP Tool，模型还需要额外猜“什么时候调用 MCP”，会增加执行效果回归风险。因此 Core/必要运行资产继续作为 Project Payload 明文安装；详细 canonical Reference 正文保留在加密 Bundle 中。

## 6. Stable Reference ID

编号 Reference 使用：

```text
<skill>.reference.<两位数字>
```

例如：

```text
coding.reference.02
review.reference.01
docs.reference.04
figma.reference.07
```

同一 Skill 两个文件使用相同两位数字前缀时 Builder 必须失败，不能根据文件名猜正式规则。

非编号 Markdown 使用由文件名 SHA256 派生的稳定 fallback ID；正式 References 仍推荐当前两位数字导航。

## 7. Reference Bundle Contract

当前 schema：

```text
agent-skills-runtime-bundle/v1
```

至少记录动态 `skills` 集合和每个 Reference 的：

```text
id
skill
filename
source_path
sha256
size
content
```

`source_digest` 只基于排序后的：

```text
id
source_path
sha256
size
```

计算，用于证明 canonical Reference 集合与内容版本。`bundle_version` 是机器导航版本，不替代 Git SHA 或 Release Version。

Core/Project Payload 变化不一定改变 `source_digest`，所以必须独立维护 `payload_digest`。

## 8. Project Payload Contract

当前 schema：

```text
agent-skills-project-payload/v1
```

用于让 onefile binary 在**没有源仓库和 Python 安装脚本**的情况下重建目标项目需要的受管 Skill 运行资产。

构建原则：

```text
正式 Skill 根目录
→ canonical references/ 排除正文
→ 为每个 canonical Reference 生成同名 Runtime Stub
→ tests/、顶层 README.md、__pycache__、*.pyc、*.pyo 等维护内容排除
→ 其余普通运行资产原样进入 payload
→ 记录 path / size / SHA256 / mode / content
→ 计算 payload_digest
```

使用明确排除项，而不是不断扩展固定 Core 白名单。未来某 Skill 新增 `templates/`、`schemas/` 或其他真实运行资产时，只要不属于明确排除范围，应自动进入 payload。

Payload 路径必须是安全相对路径，拒绝绝对路径、盘符、`..`、符号链接和特殊文件。POSIX mode 进入完整性 Contract。

## 9. Reference Stub Contract

目标项目创建：

```text
.agents/skills/<skill>/references/<canonical filename>.md
```

Stub 至少包含：

- Runtime ID；
- canonical filename；
- Expected SHA256；
- `agent_skills_load_context` 调用示例；
- `canonical_text` 是完整正式原文；
- 必须比较返回 SHA256 与 Expected SHA256；
- MCP 不可用、ID 不存在、hash 不一致或没有 `canonical_text` 时停止依赖该 Reference 的动作并报告。

禁止把 Reference 摘要、关键规则节选或“方便版”复制进 Stub，否则会形成第二套容易漂移的规则事实源。

## 10. 加密与真实安全边界

canonical Reference envelope 使用 AES-256-GCM：

```text
magic
+ random 12-byte nonce
+ authenticated ciphertext/tag
```

每次构建生成随机 32-byte key。Builder 只在临时构建副本生成 embedded payload，将 key、ciphertext、Project Payload 和 Release Version 一起打入 onefile；源仓库不提交生成文件。

它提供：

- 最终用户不需要源仓库访问权；
- 目标项目不出现详细 Reference 普通 Markdown 正文；
- 普通静态浏览/复制门槛提高；
- 密文篡改由 GCM tag 检测。

不能据此宣称：

- 本机管理员无法提取 key；
- 内存永远没有明文；
- 反编译、Hook 或 MCP 通信观测不能取得规则；
- Runtime 是可信执行环境。

源仓库 canonical 文本的访问控制必须由 GitHub 仓库权限承担。

## 11. MCP Tool Contract

本地 Runtime 使用 stdio MCP；`serve` 模式下 stdout 只用于 MCP wire protocol。

稳定 Tools：

### `agent_skills_status`

返回 Runtime/Release/Bundle/Project Payload、动态 Skill 集合、source/payload digest、Reference count 和 task/phase/load 状态，不返回规则正文。

### `agent_skills_manifest`

参数可选 `skill`。返回 Skill Catalog 和 Reference ID、filename、source_path、SHA256、size，不返回 `content` / `canonical_text`。

### `agent_skills_start_task`

参数：

```text
task_id
phase = planning（默认）
```

建立/重置当前 MCP 进程 task state，并清空旧 task 已加载 Reference 集合。

### `agent_skills_load_context`

参数：

```text
ids: [stable reference id, ...]
```

只接受已知逻辑 ID，不接受路径/glob。返回：

```text
id
skill
filename
source_path
sha256
size
canonical_text
```

`canonical_text` 必须等于 canonical source UTF-8 解码结果。它进入 Agent 上下文后，作用等价于实际读取该 Reference 正文。

### `agent_skills_checkpoint`

参数：

```text
required_ids
phase（可选）
```

只检查当前 MCP task state 中 required ID 是否 load，不能替代 Requirement Traceability、Completion Audit、Review、Docs Impact 或真实测试。

## 12. 最终用户 CLI 与项目级安装

稳定入口：

```text
无参数
→ install 当前工作目录

install --target <项目根目录>
→ 显式安装/升级

status --json
→ 查看版本、digest、Skill Catalog

self-test --json
→ 校验内嵌 Bundle / Project Payload

serve
→ stdio MCP Server
```

项目 Runtime 安装：

```text
Windows: .agents/runtime/agent-skills-mcp.exe
POSIX:   .agents/runtime/agent-skills-mcp
```

`.agents/runtime/` 是本地运行资产，应被目标项目 `.gitignore` 忽略。

## 13. Managed Installation Manifest 与 ownership

目标项目：

```text
.agents/agent-skills-install.json
```

记录 Agent_Skills 可证明的 ownership、Release Version、`source_digest`、`payload_digest`、受管 Skill 集合和项目 Runtime 位置。

升级规则：

```text
旧 manifest skills ∩ 新 Release skills
→ 可以替换对应受管 Skill

旧 manifest 有、新 Release 无
→ 可以删除旧版本明确认领 Skill

目标存在、旧 manifest 从未认领
→ 项目自有/归属不明
→ 普通安装不得删除或接管
```

首次安装已存在同名 Skill，但没有合法旧 manifest 证明由 Agent_Skills 管理时，必须 fail closed。禁止用内容相似/hash 猜 ownership。

`.agents/changes/`、`.agents/project-context.json`、项目自有 Skill、其他 `.agents` 内容和 AGENTS marker 外文本都不是清理目标。

## 14. AGENTS / `.gitignore` / 宿主配置保护

项目安装还会建立：

- 根 `AGENTS.md`：创建或只更新 `agent-skills:managed` block；
- `.gitignore`：增量加入项目缓存和 Runtime ignore；
- Cursor：`.cursor/mcp.json` 的 `mcpServers.agent-skills`；
- Claude Code：`.mcp.json` 的 `mcpServers.agent-skills` + `CLAUDE.md` 最薄 `@AGENTS.md` bridge；
- Codex：`.codex/config.toml` Agent Skills 自管 MCP block。

只能修改稳定可证明边界：

- AGENTS/CLAUDE/Codex 使用 managed marker；
- JSON 只认领 `mcpServers.agent-skills`；
- 其他配置、其他 MCP server、marker 外文本保持；
- 已存在未被 manifest 认领的同名 Agent Skills MCP 时拒绝静默覆盖；
- marker 损坏、文本编码不可安全增量编辑、受管路径为符号链接时预检失败。

Codex workspace trust 以及 Cursor/Claude 的首次确认属于宿主安全边界，安装器不得绕过。

## 15. 安装原子性与回滚

1. 先验证 Project Payload、路径/hash/mode、旧 manifest、同名 Skill ownership、AGENTS/host config marker/JSON 编码和符号链接；
2. 在 `.agents` 下完整暂存新 Skill；
3. 备份旧 manifest 明确认领的受管 Skill；
4. 切换 Skill；
5. 安装项目 Runtime 并验证 SHA256；
6. 原子写入 AGENTS、`.gitignore`、宿主配置和 install manifest；
7. 任一步异常恢复本轮已切换 Skill、Runtime 和受管文本快照。

不能保证多个普通文件具备数据库式事务，但必须做到：能预检的错误先发现；切换后失败尽最大可能恢复；绝不用破坏性 Git 命令实现回滚。

## 16. 构建与验证

维护者构建入口：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

Builder 至少：

1. 动态 Skill Catalog 校验；
2. canonical References UTF-8 / ID / SHA / size / `source_digest`；
3. Project Payload path / SHA / size / mode / `payload_digest`；
4. AES-GCM Reference 加密；
5. PyInstaller onefile build；
6. artifact `status --json`；
7. artifact `self-test --json`；
8. source/payload digest、skills、VERSION 与当前源一致。

永久 CI 使用最终 artifact 验证：

```text
artifact status/self-test
→ real stdio MCP tools/list + tools/call
→ 真实临时项目单 binary 安装
→ 重复升级
→ 无参数当前目录安装
→ 项目 Runtime / Skill / Stub / manifest / host config
→ 项目内 Runtime status + MCP smoke
```

Windows `.exe`、Linux、macOS 必须在对应平台分别构建验证。

## 17. 正式 Release Contract

正式团队 Release 只发布：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
USAGE.md
SHA256SUMS
```

`USAGE.md` 是唯一最终用户说明，同时作为 GitHub Release 页面 notes 的来源；不能用自动生成 commit/PR 流水账替代用户说明。

Release 规则：

- 根 `VERSION` 为唯一产品版本事实源；
- 只从 `main` 手工 `workflow_dispatch`，输入 `v<VERSION>`；
- tag 与 VERSION 必须一致；
- tag/Release 已存在时拒绝覆盖/移动；
- Linux/Windows/macOS 在各自 Runner 重新构建并通过最终 artifact 验证；
- Preflight/构建 Job 只读；候选全部成功后 Publish Job 才获得 `contents: write`；
- `SHA256SUMS` 覆盖三平台 binary 与 `USAGE.md`；
- 不把 PR 临时 artifact 直接发布。

## 18. 升级

```text
下载新 Release binary + checksum
→ 在目标项目根运行
→ 校验 Bundle / Project Payload
→ 根据旧 manifest 计算 ownership
→ 原子升级项目 Runtime + 受管 Skill/Stub + managed 配置
→ 写入新 manifest
→ 重新建立 MCP 会话（宿主需要时）
```

Reference bytes 变化会改变 SHA/source_digest；Core/运行资产变化会改变 payload_digest。Stub Expected SHA256 与项目 Runtime 不匹配时，Agent 必须停止依赖该 Reference。

## 19. 回滚

完整版本配套：

```text
Runtime binary A
↔ source_digest A
↔ payload_digest A
↔ target managed Skill / Stub A
```

回滚：

1. 找回旧 Release 同平台 binary；
2. 校验旧 checksum；
3. 在目标项目根运行旧 binary；
4. 由旧 binary 根据当前 manifest 恢复该版本对应 Runtime/Skill/Stub/managed 配置；
5. 检查项目 Runtime `status/self-test`；
6. 重新建立 MCP 会话并做真实 Reference 加载。

不要只手工替换 Runtime 或只回退 Stub，避免版本混装。

## 20. 正常任务生命周期

第一版不要求所有任务机械调用 `start_task/checkpoint` 才能读 Reference；关键不变量是**命中 Reference 后必须取得并校验 canonical_text**。

推荐：

```text
任务开始
→ agent_skills_start_task(task_id, phase)
→ Core 恢复项目事实并路由
→ 读命中 Reference Stub
→ agent_skills_load_context(ids)
→ 校验 SHA
→ 使用 canonical_text 工作
→ 阶段变化继续按 Core 触发新 Reference
→ 可用 checkpoint 检查 required IDs
```

MCP 负责 Reference 传输和完整性，不替 Agent 判断需求是否满足。

## 21. ChatGPT 网页端边界

当前 Runtime 是本地 stdio MCP。纯网页端 ChatGPT 不能直接启动用户电脑本地进程；网页端接入需要 Remote MCP 或受支持的安全隧道，是另一种部署形态，不属于当前 Runtime。