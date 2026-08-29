# 本地 MCP Runtime 分发与原文上下文加载

这份规则定义 Agent_Skills 当前唯一正式对外分发模式：**Native Core Skill + Shared Skill Router + Project-local MCP Runtime + Encrypted Canonical References + onefile binary**。

目标是：最终使用者只拿到对应平台 Release binary，在目标项目根运行即可完成项目级接入；详细 canonical `references/*.md` 不作为普通 Markdown 分发到目标项目，同时保持现有自然语言 Skill 的执行语义和逐字完整性。跨 Skill 的 Catalog / Router 只维护一份 `.agents/skills/ROUTER.md`，源码直读和 Runtime 安装共享同一正文。

本文件只规定 Runtime 分发、动态 Skill 发现、Skills 根级共享运行资产、Project Payload、Reference 原文加载、项目级安装/升级、宿主接入、完整性、Release 和失败边界。Coding / Review / Docs / Figma 的研发语义仍由各自 `SKILL.md` 与 canonical References 定义；跨 Skill 入口、Reference 取得方式和 Handoff 由唯一 Router 定义。

## 1. 何时必须读取

出现以下任务时必须读取本文件：

- 构建、Release、安装或升级 `agent-skills-mcp`；
- 修改 Project Payload、动态 Skill Catalog、Skills 根级 shared runtime files、共享 Router、installation manifest 或项目宿主 MCP 配置；
- 修改 Runtime Bundle schema、Project Payload schema、install manifest schema、Reference ID、加密格式、MCP Tool Contract、Stub、`source_digest` 或 `payload_digest`；
- 调试目标项目 Reference Stub → MCP canonical 原文链；
- Review Runtime 是否仍逐字返回 canonical Reference；
- 修改正式 Skill 或 shared runtime file，使其进入下一次 Runtime Release；
- 修改 onefile 项目安装、升级、rollback 或 fail-closed ownership 逻辑。

## 2. 设计目标与非目标

### 目标

```text
Agent_Skills 源仓库 .agents/skills/*/SKILL.md
→ 构建时动态发现正式 Skill

Agent_Skills 源仓库 .agents/skills/ROUTER.md
→ 显式 Skills 根级 shared runtime file
→ 不属于任何具体 Skill

Shared Router + Native Core / 必要运行资产
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

- 访问或 clone Agent_Skills 源仓库；
- 为**安装、升级、status/self-test 或 MCP Runtime** 预先安装 Python、pip、venv；
- 外部安装脚本；
- Runtime Kit ZIP；
- 用户级或全局 Runtime 前置安装。

但 Project Payload 会保留正式 Skill 自己需要的运行资产。当前 Coding Core 明确使用 `coding/scripts/coding.py` 和 `coding/scripts/ready_check.py` 完成项目发现、Change 辅助与 Ready Check，因此这两个 Python helper 仍必须随 Skill 安装。目标项目/宿主没有可用 Python 时，Coding 只能按对应规则使用明确 manual fallback；无法执行的机器门禁必须记为未验证，不能用 onefile Runtime 的存在冒充已执行。

### 非目标

- 不把 Markdown Skill 改写成 Policy DSL、布尔规则数据库或另一套 prompt 系统；
- 不让 Runtime 自己成为第二个 Coding Agent；
- 不自动扫描整个目标项目替 Agent 判断架构/业务语义；
- 不提供任意路径读取、glob 或批量导出 canonical 规则接口；
- 不承诺抵御机器 Owner、调试器、内存转储、进程 Hook 或专业逆向；
- 不用 Runtime 替代项目 `AGENTS.md`、CI、PR、Review、Migration、安全和授权门禁；
- 不把网页端 Remote MCP / secure tunnel 混进本地 stdio Runtime；
- 不在本规则建立在线许可证、远程 KMS 或自动更新服务；
- 不为了 shared files 自动打包 `.agents/skills/` 根目录下所有文件。

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

`.agents/skills/ROUTER.md` 是根级普通文件，**不能被识别成正式 Skill**。`coding` 仍是当前目标项目研发路由的核心锚点；Router 可以展示当前 Catalog 供 Agent 导航，但明确不是 Runtime 分发白名单。改变 Coding 的上位入口关系属于独立架构变化，不能借动态发现静默修改。

## 4. 规则与 Router 事实源

每个正式 Skill 的专业规则事实源：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
```

跨 Skill 的 Catalog、项目事实优先、Reference 两种取得方式和 Coding/Figma/Review/Docs Handoff 的唯一正文 Owner：

```text
.agents/skills/ROUTER.md
```

Router 是 Skills 根级 shared runtime file，不是新的专业 Skill，也不得复制各 Skill 的完整详细规则；根 `AGENTS.md` 与 `AGENTS.managed.md` 只做 Bootstrap，不再拥有第二套完整 Router。

### 源仓库 Mutation 与普通 Runtime 明文面

源仓库 Mutation 的意图识别与 canonical Ownership 由 Agent_Skills **根 `AGENTS.md`** 独立承担，详细 Skill/Reference 内容守恒继续由 ref16 承担。普通 Runtime 安装给目标项目的 shared Router 与 `AGENTS.managed.md` 不复制这套源仓库 Mutation、canonical repository、Maintenance 或跨仓库同步治理。

这不是建立第二个 Router：`.agents/skills/ROUTER.md` 仍是源码直读与 Runtime 安装共享的普通研发 Router；根 `AGENTS.md` 只在 Agent_Skills 源仓库维护场景增加源仓库专用 Bootstrap。Custom Instructions 可以把维护者意图引导到当前根 `AGENTS.md`，但不进入 Project Payload，也不替代当前源码事实。

Builder 读取 canonical References 时：

- 不修改源文件；
- 不标准化换行；
- 不去标题/frontmatter；
- 不摘要；
- Bundle entry `content` 来自原始 UTF-8 bytes 直接 decode；
- SHA256 与 size 对应同一份原始 bytes。

Runtime Stub 不是规则事实源，只负责把 Core Skill 中原有相对链接接到 MCP canonical 原文加载能力。

## 5. Native Core 与 Router 为什么继续明文

Core `SKILL.md` 负责：

- 让支持 Skill/Rules/AGENTS 的宿主进入本 Skill 的正式工作流；
- 恢复项目事实并完成任务/风险/工具链路由；
- 决定何时必须读取某个 Reference；
- 保留 Reference 缺失/加载失败时的停止条件和完成门禁。

共享 Router 负责：

- 在两个 Bootstrap 之后提供同一跨 Skill Catalog / Router；
- 固定项目事实优先；
- 说明源码 canonical Reference 与 Runtime Stub 两种取得方式；
- 把 Coding / Figma / Review / Docs Handoff 放在单一 Owner，而不是复制到两个 AGENTS 入口。

如果 Core/Router 也完全隐藏，只留下 MCP Tool，模型还需要额外猜“什么时候进入哪个 Skill、什么时候调用 MCP”，会增加执行效果回归风险。因此 Core/Router/必要运行资产继续作为 Project Payload 明文安装；详细 canonical Reference 正文保留在加密 Bundle 中。

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

Core/Router/Project Payload 变化不一定改变 `source_digest`，所以必须独立维护 `payload_digest`。

## 8. Project Payload Contract

当前 schema：

```text
agent-skills-project-payload/v2
```

用于让 onefile binary 在**没有源仓库和 Python 安装脚本**的情况下重建目标项目需要的受管共享运行文件、Skill 运行资产和 Reference Stub。

Project Payload 至少包含：

```text
skills
→ 动态正式 Skill 名称列表

shared_files
→ Skills 根级共享运行文件列表
→ 当前为 ["ROUTER.md"]

files
→ shared files + Skill-owned runtime files + Reference Stubs
```

构建原则：

```text
显式 shared_files
→ 当前只收集 .agents/skills/ROUTER.md
→ 不扫描并自动认领 Skills 根目录所有文件

正式 Skill 根目录
→ canonical references/ 排除正文
→ 为每个 canonical Reference 生成同名 Runtime Stub
→ tests/、任意深度的维护 `README.md`、__pycache__、*.pyc、*.pyo 等维护内容排除
→ 其余普通运行资产原样进入 payload

shared files + Skill files
→ 记录 path / size / SHA256 / mode / content
→ 连同 skills/shared_files 一起计算 payload_digest
```

未来某 Skill 新增 `templates/`、`schemas/`、`scripts/` 或其他真实运行资产时，只要不属于明确排除范围，应自动进入其 Skill payload；未来新增 Skills 根级共享运行文件时，必须显式进入 shared-files Contract，不能靠目录里“碰巧有文件”自动分发。

Payload 路径必须是安全相对路径，拒绝绝对路径、盘符、`..`、符号链接和特殊文件。根级 payload file 必须被 `shared_files` 明确认领；非根级文件必须属于动态发现的正式 Skill。POSIX mode 进入完整性 Contract。

本版本不兼容 `agent-skills-project-payload/v1`，不保留旧 Router 路径 fallback。

永久测试必须证明 `ROUTER.md` 原样进入 Payload、`shared_files == ["ROUTER.md"]`，使目标项目 managed block 不会指向不存在的 Router。

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

源仓库 canonical 文本的访问控制必须由仓库权限承担。

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

当前 schema：

```text
agent-skills-install/v2
```

记录 Agent_Skills 可证明的 ownership、Release Version、`source_digest`、`payload_digest`、受管 Skill 集合、`shared_files` 和项目 Runtime 位置。

两类 ownership：

```text
skills
→ 受管正式 Skill 目录

shared_files
→ 受管 Skills 根级共享运行文件
→ 当前包含 ROUTER.md
```

升级规则：

```text
旧 manifest 明确认领 + 新 Release 仍存在
→ 可以替换对应 Skill/shared file

旧 manifest 明确认领 + 新 Release 已删除
→ 可以删除旧受管项

目标存在 + 旧 manifest 从未认领
→ 项目自有/归属不明
→ 普通安装不得删除或接管
```

首次安装已存在同名 Skill 或 `.agents/skills/ROUTER.md`，但没有合法当前 manifest 证明由 Agent_Skills 管理时，必须 fail closed。禁止用内容相似/hash 猜 ownership。

本版本不兼容 `agent-skills-install/v1`。旧 schema 不作为迁移输入，直接报告不支持；不通过旧路径、内容或 hash 猜 ownership。

`.agents/changes/`、`.agents/project-context.json`、项目自有 Skill、未认领 Skills 根级文件、其他 `.agents` 内容和 AGENTS marker 外文本都不是清理目标。

## 14. AGENTS / `.gitignore` / 宿主配置保护

项目安装还会建立：

- 根 `AGENTS.md`：创建或只更新 `agent-skills:managed` block；该 block 只负责项目事实优先并指向项目内 `.agents/skills/ROUTER.md`；
- `.gitignore`：增量加入项目缓存和 Runtime ignore；
- Cursor：`.cursor/mcp.json` 的 `mcpServers.agent-skills`；
- Claude Code：`.mcp.json` 的 `mcpServers.agent-skills` + `CLAUDE.md` 最薄 `@AGENTS.md` bridge；
- Codex：`.codex/config.toml` Agent Skills 自管 MCP block。

只能修改稳定可证明边界：

- AGENTS/CLAUDE/Codex 使用 managed marker；
- JSON 只认领 `mcpServers.agent-skills`；
- 其他配置、其他 MCP server、marker 外文本保持；
- 已存在未被 manifest 认领的同名 Agent Skills MCP 时拒绝静默覆盖；
- 已存在未被 manifest 认领的同名 Skill/shared file 时拒绝静默覆盖；
- marker 损坏、文本编码不可安全增量编辑、受管路径为符号链接时预检失败。

Codex workspace trust 以及 Cursor/Claude 的首次确认属于宿主安全边界，安装器不得绕过。

## 15. 安装原子性与回滚

1. 先验证 Project Payload v2、路径/hash/mode/shared_files、当前 install manifest、同名 Skill/shared-file ownership、AGENTS/host config marker/JSON 编码和符号链接；
2. 在 `.agents` 下完整暂存新 Skill 和 shared files，必须包含 managed block 指向的 `ROUTER.md`；
3. 备份旧 manifest 明确认领的受管 Skill 和 shared files；
4. 切换 Skill；
5. 切换 shared files；
6. 安装项目 Runtime 并验证 SHA256；
7. 原子写入 AGENTS、`.gitignore`、宿主配置和 install manifest；
8. 任一步异常恢复本轮已切换 shared files、Skill、Runtime 和受管文本快照。

不能保证多个普通文件具备数据库式事务，但必须做到：能预检的错误先发现；切换后失败尽最大可能恢复；绝不用破坏性 Git 命令实现回滚。

## 16. 构建与验证

维护者构建入口：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

Builder 至少：

1. 动态 Skill Catalog 校验，确认 `ROUTER.md` 不进入 Skill 名称列表；
2. canonical References UTF-8 / ID / SHA / size / `source_digest`；
3. Project Payload v2 的 `skills / shared_files / path / SHA / size / mode / payload_digest`；
4. 确认 `.agents/skills/ROUTER.md` 原样作为 shared runtime file 进入 Payload；
5. AES-GCM Reference 加密；
6. PyInstaller onefile build；
7. artifact `status --json`；
8. artifact `self-test --json`；
9. source/payload digest、skills、VERSION 与当前源一致。

永久 CI 使用最终 artifact 验证：

```text
artifact status/self-test
→ real stdio MCP tools/list + tools/call
→ 真实临时项目单 binary 安装
→ 重复升级
→ 无参数当前目录安装
→ 项目 Runtime / Skill / shared Router / Stub / manifest / host config
→ 项目 AGENTS managed block → .agents/skills/ROUTER.md 导航闭环
→ 项目内 Runtime status + MCP smoke
```

还必须确认：

- 正式 Coding helper 继续进入 Project Payload；
- 同名未认领 Router 在任何目标写入前失败；
- shared Router 已切换后若 Runtime/后续写入失败，旧 Router 能恢复；
- 旧 Project Payload/install manifest schema 被明确拒绝而不是静默兼容。

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

如果源仓库是私有且最终使用者不应获得源码 read 权限，源仓库 GitHub Release 只是维护者构建/留存点；维护者应取得并校验上述资产后，通过内部制品库、文件服务或独立 release-only 渠道交付，不要为了下载同仓 Release 向接收者授予源仓库 read 权限。

## 18. 升级

当前版本只接受当前 v2 install manifest：

```text
下载新 Release binary + checksum
→ 在目标项目根运行
→ 校验 Bundle / Project Payload v2
→ 根据当前 v2 manifest 计算 Skill/shared-file ownership
→ 原子升级项目 Runtime + 受管 Skill/ROUTER.md/Stub + managed 配置
→ 写入新 v2 manifest
→ 重新建立 MCP 会话（宿主需要时）
```

Reference bytes 变化会改变 SHA/source_digest；Core/Router/运行资产变化会改变 payload_digest。Stub Expected SHA256 与项目 Runtime 不匹配时，Agent 必须停止依赖该 Reference。

旧 v1 manifest/旧 `coding/assets/AGENT_SKILLS_ROUTER.md` 不在本版本迁移与兼容范围；不要为了兼容旧版本保留双路径或第二份 Router。

## 19. 回滚

完整版本配套：

```text
Runtime binary A
↔ source_digest A
↔ payload_digest A
↔ target managed Skill / shared ROUTER.md / Stub A
```

同一当前 Contract 范围内的安装失败回滚必须由 Installer 快照恢复。跨 Release 手工回退只允许回到使用相同当前 schema/路径 Contract 的版本；本规则不承诺通过 v2 Installer 自动迁移或恢复旧 v1 安装。

不要只手工替换 Runtime、Router 或 Stub，避免版本混装。

## 20. 正常任务生命周期

第一版不要求所有任务机械调用 `start_task/checkpoint` 才能读 Reference；关键不变量是**命中 Reference 后必须取得并校验 canonical_text**。

推荐：

```text
任务开始
→ 项目 AGENTS managed block / 源码根 AGENTS
→ .agents/skills/ROUTER.md
→ agent_skills_start_task(task_id, phase)（安装态可选）
→ Coding/Core 恢复项目事实并路由
→ 读命中 canonical Reference 或 Runtime Stub
→ Stub 模式调用 agent_skills_load_context(ids)
→ 校验 SHA
→ 使用 canonical_text 工作
→ 阶段变化继续按 Router/Core 触发新 Skill/Reference
→ 可用 checkpoint 检查 required IDs
```

MCP 负责 Reference 传输和完整性，不替 Agent 判断需求是否满足。

## 21. ChatGPT 网页端边界

当前 Runtime 是**项目本地 stdio MCP**。纯网页端 ChatGPT 不能直接启动用户电脑上的本地 `agent-skills-mcp` 进程，也不能因为 GitHub 中存在 Runtime 源码就把本地 stdio MCP 当作已经连接。

如果 ChatGPT 网页端已经通过 GitHub 连接获得 Agent_Skills 源仓库的读取权限，可以使用本规则定义的**源码直接读取模式**：

```text
目标项目当前规则/事实
→ Agent_Skills 根 AGENTS.md
→ .agents/skills/ROUTER.md
→ 命中的 SKILL.md
→ 直接读取 canonical Reference
```

这条路径不需要启动用户电脑上的本地 Runtime，也不经过 Reference Stub / `agent_skills_load_context`。

如果未来需要让网页端 ChatGPT 调用目标项目机器上的 Agent Skills Runtime，则需要 Remote MCP、受支持的安全隧道或等价远程部署能力；这是另一种部署形态，不属于当前本地 stdio Runtime，也不得为实现它绕过宿主或网络安全边界。