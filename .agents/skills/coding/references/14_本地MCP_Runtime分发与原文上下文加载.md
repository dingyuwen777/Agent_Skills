# 本地 MCP Runtime 分发与原文上下文加载

这份规则定义 `Agent_Skills` 的 **Native Core Skill + Project-local MCP Runtime + Encrypted Canonical References** 模式。它解决的不是“把自然语言 Skill 编译成 Policy”，而是：**怎样在尽量保持现有 Skill 执行效果的前提下，让最终使用者只拿到一个平台 binary，在目标项目根运行后完成项目级接入，同时不把 canonical `references/*.md` 正文明文分发到目标项目。**

本文件只规定 Runtime 分发、动态 Skill 发现、Project Payload、Reference 原文加载、项目级安装/升级、宿主接入、完整性和失败边界。Coding / Review / Docs 以及以后新增正式 Skill 的研发语义，仍由各自 `SKILL.md` 与 canonical `references/*.md` 定义。

## 1. 何时必须读取

出现以下任务时必须读取本文件：

- 构建、发布、安装或升级 `agent-skills-mcp` 本地 Runtime；
- 修改单二进制 Project Payload、动态 Skill Catalog、安装 manifest 或项目宿主 MCP 配置；
- 修改 Runtime Bundle schema、Reference ID、加密格式、MCP Tool Contract、stub 格式、`source_digest` 或 `payload_digest`；
- 调试“目标项目只有 Reference Stub，没有完整正文”的场景；
- 比较 full Markdown 分发与 Runtime binary 分发；
- Review Runtime 是否仍逐字返回 canonical Reference，而没有摘要、改写或语义漂移；
- 修改 Release，使未来新增 `.agents/skills/<skill>/` 能自动进入 Runtime binary。

普通 full Markdown 分发继续按 [13_目标项目安装与AGENTS_Bootstrap.md](13_目标项目安装与AGENTS_Bootstrap.md) 执行。目标项目自己的项目事实、AGENTS Overlay、Change、CI、授权边界和项目自有 Skill，也不因 Runtime 存在而改变。

## 2. 设计目标与非目标

### 目标

```text
Agent_Skills 源仓库 .agents/skills/*
→ 构建时动态发现正式 Skill

Native Core / 运行资产
→ 构建成 Project Payload
→ 随 onefile Runtime 一起嵌入
→ 安装时释放到目标项目 .agents/skills/

Canonical references/*.md
→ 继续作为唯一完整 Reference 正文
→ 构建时逐字收集、hash、AES-256-GCM 加密并嵌入 Runtime

目标项目 Runtime Stub
→ 保持 canonical 文件名和相对链接可达
→ 只声明 Runtime ID + Expected SHA256 + 加载协议

Project-local Runtime
→ 安装在目标项目 .agents/runtime/
→ Codex / Cursor / Claude Code 项目配置只指向这个项目 Runtime

Local MCP
→ 只按稳定逻辑 ID 返回 canonical_text
→ 不摘要、不重写、不推断新的研发规则
```

最终使用者的正式 Runtime 分发不要求：

- clone `Agent_Skills` 源仓库；
- Python、pip、venv；
- `install_runtime.py`；
- `install_runtime_target.py`；
- Runtime Kit ZIP；
- 用户级或全局 Runtime 前置安装。

### 非目标

- 不把现有复杂 Markdown 改写成布尔 Policy、DSL 或另一套规则数据库；
- 不让 Runtime 自己变成第二个 Coding Agent；
- 不自动扫描整个目标项目并替 Agent 做架构/业务语义判断；
- 不提供任意路径读取或通配规则导出接口；
- 不承诺防止机器 Owner、调试器、内存转储、进程 Hook 或专业逆向提取运行时明文；
- 不用 Runtime 替代目标项目 `AGENTS.md`、CI、Branch Protection、PR、Review、Migration、安全或授权门禁；
- 不把 ChatGPT 网页端 Remote MCP / secure tunnel 混进本地 stdio Runtime；
- 不在本规则中建立在线许可证、远程 KMS 或自动更新服务。

## 3. 动态正式 Skill Catalog

Runtime、Project Payload、源安装器、Full Kit、manifest、测试和 Release **不得维护 `coding/review/docs` 之类的静态完整 Skill 名单**。

正式 Skill 从源仓库：

```text
.agents/skills/<skill-name>/SKILL.md
```

动态发现。当前机器 Contract 由 `runtime/agent_skills_runtime/skill_catalog.py` 实现；规则层必须保持以下语义：

1. 只发现 `.agents/skills/` 的一级真实目录；
2. Skill 目录和 `SKILL.md` 不能是符号链接；
3. `SKILL.md` 必须是普通 UTF-8 文件；
4. Skill 名使用稳定小写标识符；
5. `SKILL.md` 存在 frontmatter 时，必须有唯一 `name` 且与目录名一致；
6. Skill 可以没有 `references/`；这不影响它作为正式 Skill 进入 Project Payload；
7. `references/` 存在时，只接受当前 Contract 支持的直接 Markdown Reference，不能通过特殊文件、目录或符号链接越界；
8. 发现结果按名称确定性排序。

因此未来新增：

```text
.agents/skills/security/
.agents/skills/testing/
.agents/skills/architecture/
```

只要满足正式 Skill Contract，下一次构建就自动进入 Runtime/Full 分发，不要求再修改安装器、Builder、Runtime 或 Release Workflow 的 Skill 名称列表。

`coding` 当前仍是目标项目 AGENTS Bootstrap 的核心锚点；如果维护者要改变这个上位入口关系，需要作为独立架构变化处理，不能因为动态发现就静默移除 Coding Bootstrap 责任。

## 4. 唯一规则事实源

每个正式 Skill 的自然语言规则事实源是：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
```

当前仓库实际存在的 `coding / review / docs` 只是当前正式 Skill 集合，不是 Runtime 代码里的永久白名单。

Builder 读取 canonical References 时：

- 不修改源文件；
- 不标准化换行；
- 不去标题；
- 不去 frontmatter；
- 不生成摘要；
- Bundle entry 的 `content` 由 Reference 原始 UTF-8 bytes 直接 decode；
- SHA256 与 size 对应同一份原始 bytes。

Runtime 目标项目里的 Stub **不是规则事实源**。它只是把 Core Skill 中现有相对链接接到 MCP 原文加载能力。

## 5. Native Core 为什么继续明文

Core `SKILL.md` 负责：

- 让支持 Skill/Rules/AGENTS 的宿主在任务开始进入正确工作流；
- 恢复项目事实并完成任务/风险/工具链路由；
- 决定什么时候必须读取某个 Reference；
- 在 Skill 之间做显式路由；
- 保留 Reference 缺失时的失败处理和完成门禁。

如果把 Core 也完全删除，只留下 MCP Tools，模型还要额外猜“什么时候应该调用 MCP”，会增加执行效果回归风险。因此 Runtime 模式继续让 Core/必要运行资产作为 Project Payload 明文安装，而详细 canonical Reference 正文保持在加密 Bundle 中。

## 6. Stable Reference ID

编号 Reference 使用：

```text
<skill>.reference.<两位数字>
```

例如：

```text
coding.reference.02
coding.reference.07
review.reference.01
docs.reference.04
security.reference.01
```

同一 Skill 中两个文件使用相同两位数字前缀时，Builder 必须失败，不能根据文件名猜哪一个才是正式规则。

非编号 Markdown 使用由文件名 SHA256 派生的稳定 fallback ID；正式 References 仍推荐沿用当前两位数字导航约定。

## 7. Reference Bundle Contract

当前 Bundle schema：

```text
agent-skills-runtime-bundle/v1
```

Bundle 至少记录动态 `skills` 集合和每个 Reference 的：

```text
id
skill
filename
source_path
sha256
size
content
```

`source_digest` 只基于排序后 Reference 的：

```text
id
source_path
sha256
size
```

计算，用于证明 canonical Reference 集合及内容版本。`bundle_version` 当前取 `source_digest` 前 16 个十六进制字符，是机器导航版本，不替代 Git SHA 或 Release Version。

Core/其他 Project Payload 文件变化不一定改变 `source_digest`，因此 Runtime 还必须独立维护 `payload_digest`；不能用 Reference digest 冒充整个安装 payload 的版本证明。

## 8. Project Payload Contract

当前 Project Payload schema：

```text
agent-skills-project-payload/v1
```

它用于让最终 onefile binary 在**没有源仓库和 Python 安装脚本**的情况下重建目标项目需要的全部受管 Skill 运行资产。

构建原则：

```text
正式 Skill 根目录
→ canonical references/ 整体排除明文 payload
→ 对每个 canonical Reference 生成同名 Runtime Stub
→ tests/、顶层 README.md、__pycache__、*.pyc、*.pyo 等维护期内容排除
→ 其余普通运行期文件原样进入 payload
→ 记录 path / size / SHA256 / mode / content
→ 计算独立 payload_digest
```

这里使用“少量明确排除项”，而不是不断扩展 `RUNTIME_CORE_ENTRIES` 白名单。这样未来某个正式 Skill 新增 `templates/`、`schemas/`、`examples/` 或其他真实运行资产时，只要不属于明确排除范围，就能自动随 Release 进入 binary。

Payload 路径必须是安全相对路径，拒绝绝对路径、盘符、`..` 跳转、符号链接和特殊文件。POSIX 可执行位等文件 mode 必须进入完整性 Contract，不能因为打包后重新释放而静默破坏脚本可执行性。

## 9. Reference Stub Contract

Runtime 模式创建：

```text
.agents/skills/<skill>/references/<canonical filename>.md
```

Stub 至少包含：

- Runtime ID；
- canonical filename；
- Expected SHA256；
- `agent_skills_load_context` 调用示例；
- 明确 `canonical_text` 是完整正式原文；
- 必须比较返回 SHA256 与 Expected SHA256；
- MCP 不可用、Reference ID 不存在、hash 不一致或没有 canonical_text 时停止依赖该 Reference 的动作并明确报告。

禁止把 Reference 摘要、关键规则节选或“方便版”复制进 stub；否则会形成第二套容易漂移的规则事实源。

## 10. 加密与真实安全边界

canonical Reference envelope 使用 AES-256-GCM：

```text
magic
+ random 12-byte nonce
+ authenticated ciphertext/tag
```

每次构建生成随机 32-byte key。Builder 只在临时构建副本生成 `_embedded_payload.py`，把 key、ciphertext、Project Payload 和 Release Version 一同打入 PyInstaller onefile；源仓库不提交该生成文件。

因为 Runtime 在本机必须持有解密能力，所以这不是 KMS/TEE 意义上的秘密保护。它提供的是：

- 最终使用者不需要访问 `Agent_Skills` canonical 源仓库；
- 目标项目不出现完整 Reference 明文；
- 普通使用者不能直接打开 `.md` 浏览全部规则；
- 密文篡改由 GCM tag 检测；
- 提高批量复制和静态浏览门槛。

不能据此声称：

- 本机管理员无法提取 key；
- 内存里永远没有明文；
- 反编译、Hook 或 MCP 通信观测无法取得规则；
- Runtime 是可信执行环境。

## 11. MCP Tool Contract

本地 Runtime 使用 stdio MCP，`stdout` 在 `serve` 模式只用于 MCP wire protocol。稳定 Tools：

### `agent_skills_status`

返回 Runtime/Release/Bundle/Project Payload、动态 Skill 集合、source/payload digest、Reference count 和当前 task/phase/load 状态，不返回规则正文。

### `agent_skills_manifest`

参数：可选 `skill`。

返回动态 Skill Catalog 和 Reference ID、skill、filename、source_path、SHA256、size，不返回 `content` / `canonical_text`。

### `agent_skills_start_task`

参数：

```text
task_id
phase = planning（默认）
```

建立或重置当前 MCP 进程的任务状态，并清空旧 task 已加载 Reference 集合。

### `agent_skills_load_context`

参数：

```text
ids: [stable reference id, ...]
```

只接受已知逻辑 ID，不接受文件路径、glob 或任意资源 URI。返回每个命中 Reference 的：

```text
id
skill
filename
source_path
sha256
size
canonical_text
```

`canonical_text` 必须等于 canonical source UTF-8 解码结果。它进入 Agent 上下文后，作用等价于“当前 Agent 实际读取了这份 Reference 正文”；stub 自身不能替代它。

### `agent_skills_checkpoint`

参数：

```text
required_ids
phase（可选）
```

只检查当前 MCP task state 中哪些 required ID 已经 load，不做自然语言 Requirement/Review/Docs 判断。返回 `required_ids / loaded_ids / missing_ids / ok`。

`checkpoint` 不能替代 Completion Audit、独立 Review、Docs Impact 或真实测试。

## 12. 最终用户 CLI 与项目级安装

正式 onefile Runtime 的稳定入口：

```text
无参数
→ install 当前工作目录

install --target <项目根目录>
→ 显式安装/升级目标项目

status --json
→ 查看当前 binary 的版本、digest、Skill Catalog

self-test --json
→ 校验内嵌 Bundle / Project Payload

serve
→ stdio MCP Server
```

Windows 最终用户典型流程：

```powershell
cd D:\work\MyProject
.\agent-skills-mcp.exe
```

Linux/macOS：

```bash
cd /work/MyProject
chmod +x ./agent-skills-mcp   # 下载后没有可执行位时执行一次
./agent-skills-mcp
```

项目级 Runtime 安装位置：

```text
Windows: .agents/runtime/agent-skills-mcp.exe
POSIX:   .agents/runtime/agent-skills-mcp
```

`.agents/runtime/` 是本地运行资产，应由目标项目 `.gitignore` 忽略。目标项目受管 Skill、AGENTS managed block 和宿主项目配置则按目标项目自己的 Git 策略决定是否提交；安装器不能擅自提交。

## 13. Managed Installation Manifest 与 ownership

目标项目使用：

```text
.agents/agent-skills-install.json
```

记录 Agent_Skills 自己可证明的安装 ownership、Release Version、`source_digest`、`payload_digest`、受管 Skill 集合和项目 Runtime 位置。

它不是项目架构/业务事实源，只用于安全升级和回滚判断。

升级规则：

```text
旧 manifest skills
∩ 新 Release skills
→ 可以替换对应 Agent_Skills 受管 Skill

旧 manifest 有、新 Release 无
→ 可以删除这个“旧版本明确认领”的 Skill

目标项目存在、旧 manifest 从未认领
→ 项目自有内容；普通升级不得删除或接管
```

首次安装如果目标项目已存在与 Release Skill 同名目录，但没有合法旧 manifest 证明它由 Agent_Skills 管理，必须 **fail closed**。禁止通过文件名相似、内容相似、hash 猜测 ownership 后覆盖。

`.agents/changes/`、`.agents/project-context.json`、项目自有 Skill、其他 `.agents` 内容和 AGENTS managed marker 外文本都不是 Runtime 安装器的清理目标。

## 14. AGENTS / `.gitignore` / 宿主配置保护

项目级 Runtime 安装除了释放 Skill/Runtime，还会建立必要项目入口：

- 根 `AGENTS.md`：创建或只更新 `agent-skills:managed` block；
- `.gitignore`：增量加入 `.agents/project-context.json` 和项目 Runtime ignore；
- Cursor：`.cursor/mcp.json` 中的 `mcpServers.agent-skills`；
- Claude Code：根 `.mcp.json` 中的 `mcpServers.agent-skills`，以及 `CLAUDE.md` 中最薄 `@AGENTS.md` bridge；
- Codex：`.codex/config.toml` 中 Agent Skills 自管 MCP block。

安装器只能修改自己稳定可证明的边界：

- AGENTS/CLAUDE/Codex 使用 managed marker；
- JSON MCP 配置只认领 `mcpServers.agent-skills`；
- 其他项目配置、其他 MCP server、marker 外文本必须保留；
- 已存在未被 Agent_Skills manifest 认领的同名 `agent-skills` MCP server 时，不能静默覆盖；
- marker 损坏、文本编码不可安全增量编辑、受管路径为符号链接时必须在可预检阶段失败。

Codex 的项目 `.codex/config.toml` 是否加载还受 Codex 自己的 workspace trust 安全机制约束；安装器不得绕过宿主 trust/approval。Cursor / Claude Code 也可能按当前宿主版本要求对项目 MCP 做首次确认，这属于宿主安全边界。

## 15. 安装原子性与回滚

项目安装修改研发治理入口和本地 Runtime，失败边界必须严格：

1. 先验证内嵌 Project Payload、路径、hash、mode、旧 install manifest、同名 Skill ownership、AGENTS/host config marker/JSON 编码和符号链接；
2. 在 `.agents` 下完整暂存新 Skill；
3. 备份此前 manifest 明确认领的受管 Skill；
4. 切换 Skill；
5. 安装项目 Runtime 并验证 SHA256；
6. 原子写入 AGENTS、`.gitignore`、宿主配置和 install manifest；
7. 任一步异常时恢复本轮已切换 Skill、Runtime 和受管文本文件快照。

安装器不能保证多个普通文件之间拥有数据库式事务，但必须做到：**能预检的错误先于写入发现；已开始切换后的失败尽最大可能恢复本轮前状态；绝不使用 `git reset --hard`、`git clean`、强制推送或历史重写来实现回滚。**

## 16. 构建与验证

构建入口：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

维护者需要 Python/构建依赖；**最终使用者不需要**。

Builder 至少执行：

1. 动态正式 Skill Catalog 校验；
2. canonical References UTF-8 / ID / SHA / size / `source_digest`；
3. Project Payload path / SHA / size / mode / `payload_digest`；
4. AES-GCM Reference 加密；
5. PyInstaller onefile build；
6. artifact `status --json`；
7. artifact `self-test --json`；
8. `source_digest / payload_digest / skills / VERSION` 与当前源一致。

永久 CI 还必须使用**最终平台 artifact**做：

```text
artifact status/self-test
→ 真实 stdio MCP tools/list + tools/call
→ 在真实临时项目直接运行 binary 安装
→ 重复升级
→ 检查项目 Runtime / Skill / Stub / managed manifest / 宿主配置
→ 使用项目内 Runtime 再做 status + MCP smoke
```

Windows `.exe`、Linux、macOS artifact 必须在目标平台分别构建/验证。不能用 Python 模块单测绿色直接宣称最终 binary 可用，也不能用 Linux onefile 结果替代 Windows/macOS。

## 17. Release 边界

最终团队 Runtime Release 只发布平台 binary 和 checksum：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
SHA256SUMS
```

正式 Runtime Release **不同时发布含 canonical Reference 明文的 Full Kit**，否则会破坏“团队只拿 binary、不直接得到 Reference 正文”的分发目标。

Full Distribution Builder 仍可作为维护者/兼容能力存在并进入永久 CI，但不因此成为 Runtime 团队 Release 资产。需要对外分发 Full Kit 时必须作为明确的不同授权/安全决定处理。

PyInstaller onefile 不是跨平台产物；平台名称表示实际构建平台，不表示一个 binary 可以跨系统运行。

## 18. 升级顺序与版本锁

Runtime 项目级升级只需要同一项目重新运行新版本 binary：

```text
下载新平台 binary
→ 校验 SHA256SUMS
→ 在目标项目根运行新 binary
→ 校验内嵌 Bundle / Project Payload
→ 根据旧 install manifest 计算 ownership
→ 原子升级项目 Runtime + 全部受管 Skill/Stub + managed 配置
→ 写入新 install manifest
→ 宿主需要时重新建立 MCP 会话
```

canonical Reference 原始字节变化会改变对应 SHA，并通常改变 `source_digest`；Core/其他 Project Payload 变化会改变 `payload_digest`。安装后的 Stub Expected SHA256 与项目 Runtime 的 canonical Reference 不匹配时，Agent 必须停止依赖该 Reference，不能用旧记忆继续。

## 19. 回滚

完整版本配套关系是：

```text
Runtime binary A
↔ source_digest A
↔ payload_digest A
↔ Target managed Skill / Stub A
```

回滚到旧版本时：

1. 找回旧 Release 的同平台 binary；
2. 校验旧 Release checksum；
3. 在目标项目根运行旧 binary；
4. 由旧 binary 根据当前 install manifest 原子恢复其版本对应的 Runtime/Skill/Stub/managed 配置；
5. 检查项目 Runtime `status/self-test`；
6. 重新建立 MCP 会话并做一次真实 Reference 加载。

不要只手工替换 `.agents/runtime/agent-skills-mcp` 而保留新 Stub，也不要只手工回退 Stub；这会制造 `source_digest` / Reference SHA / payload 版本混装。

## 20. Full 模式兼容边界

源码仓库和维护者 Full Distribution 仍可以使用：

```bash
python scripts/install.py --target <target>
```

完整复制动态发现的正式 Skill，包括 canonical References。这个模式适合明确允许 Markdown 明文分发、需要最短 Reference 加载链的环境。

`scripts/install.py --mode runtime` 可以作为源码/历史兼容维护入口继续存在，但它**不是最终团队用户的推荐安装路径**；正式 Runtime 用户只需要 onefile binary。

Full/兼容安装仍必须动态发现正式 Skill，不允许重新维护静态全量 Skill 名单。

## 21. 正常任务生命周期

第一版不要求所有任务机械执行 `start_task/checkpoint` 才能读 Reference；最关键的不变量是**命中 Reference 后必须取得 canonical_text**。

推荐：

```text
任务开始
→ agent_skills_start_task(task_id, phase)
→ Core Skill 恢复项目事实并做现有自然语言路由
→ 读命中 Reference Stub
→ agent_skills_load_context(ids)
→ 校验 SHA
→ 使用 canonical_text 工作
→ 阶段变化时继续按 Core 触发新的 Reference
→ 可用 checkpoint 检查当前阶段已知 required IDs 是否都已加载
```

MCP 负责 Reference 传输和完整性，不负责替 Agent 判断需求是否满足。

## 22. ChatGPT 网页端边界

本 Runtime 是**本地 stdio MCP**。ChatGPT 网页端不能直接启动用户电脑上的本地 stdio 进程；网页端接入需要 Remote MCP 或受支持的安全隧道，是另一种部署形态，不属于当前 Runtime 范围。
