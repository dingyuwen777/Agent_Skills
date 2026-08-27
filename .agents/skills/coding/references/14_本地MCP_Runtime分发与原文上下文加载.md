# 本地 MCP Runtime 分发与原文上下文加载

这份规则定义 `Agent_Skills` 的 **Native Core Skill + Local MCP Encrypted Reference Bundle** 模式。它解决的不是“把自然语言 Skill 编译成 Policy”，而是：**怎样在尽量保持现有 Skill 执行效果的前提下，让目标项目不再直接持有完整 Reference Markdown 正文。**

本文件只规定 Runtime 分发、Reference 原文加载、打包、安装、升级、完整性和失败边界。Coding / Review / Docs 的研发语义仍由各自 `SKILL.md` 与 canonical `references/*.md` 定义。

## 1. 何时必须读取

出现以下任务时必须读取本文件：

- 构建、发布、安装或升级 `agent-skills-mcp` 本地 Runtime；
- 使用 `scripts/install.py --mode runtime` 接入目标项目；
- 修改 Runtime Bundle schema、Reference ID、加密格式、MCP Tool Contract、stub 格式或 source digest；
- 调试“目标项目只有 Reference Stub，没有完整正文”的场景；
- 比较 full 与 runtime 两种 Agent_Skills 分发方式；
- Review Runtime 是否仍逐字返回 canonical Reference，而没有摘要、改写或语义漂移。

普通 full Markdown 分发继续按 [13_目标项目安装与AGENTS_Bootstrap.md](13_目标项目安装与AGENTS_Bootstrap.md) 执行；目标项目自己的项目事实、AGENTS Overlay、Change、CI 和授权边界也不因 Runtime 存在而改变。

## 2. 设计目标与非目标

### 目标

```text
Native Core SKILL.md
→ 继续负责稳定工作流入口和复杂语义路由

Canonical references/*.md
→ 继续作为唯一完整规则正文
→ 构建时逐字收集、hash、加密并嵌入本地 Runtime

目标项目 Runtime Stub
→ 保持原文件名/相对链接可达
→ 只声明 Runtime ID + expected SHA256 + 加载协议

Local MCP
→ 只按稳定逻辑 ID 返回 canonical_text
→ 不摘要、不重写、不推断新的规则
```

### 非目标

- 不把现有复杂 Markdown 改写成布尔 Policy、DSL 或另一套规则数据库；
- 不让 Runtime 自己变成第二个 Coding Agent；
- 不自动扫描整个目标项目并替 Codex 做架构/业务语义判断；
- 不提供任意路径读取或通配规则导出接口；
- 不承诺防止机器 Owner、调试器、内存转储或专业逆向提取运行时明文；
- 不用 Runtime 替代目标项目 `AGENTS.md`、CI、Branch Protection、PR、Review 或授权门禁。

## 3. 唯一规则事实源

正式自然语言规则仍然只有：

```text
.agents/skills/coding/SKILL.md
.agents/skills/coding/references/*.md
.agents/skills/review/SKILL.md
.agents/skills/review/references/*.md
.agents/skills/docs/SKILL.md
.agents/skills/docs/references/*.md
```

Builder 只读取这些 canonical References，不修改源文件、不标准化换行、不去标题、不去 frontmatter、不生成摘要。Bundle entry 的 `content` 必须由 Reference 原始 UTF-8 bytes 直接 decode 得到；SHA256 与 size 必须对应同一份原始 bytes。

Runtime 模式下目标项目的 stub **不是规则事实源**。它只是把现有相对链接接到 MCP 上下文加载能力。

## 4. Native Core 为什么继续明文

Core `SKILL.md` 负责：

- 让支持 Skill/Rules/AGENTS 的宿主在任务开始就进入正确研发工作流；
- 恢复项目事实并完成任务/风险/工具链路由；
- 决定什么时候必须读取某个 Reference；
- 路由 Review / Docs；
- 保留 Reference 缺失时的失败处理和完成门禁。

如果把 Core 也完全删除，只留下 MCP Tools，模型还要额外猜“什么时候应该调用 MCP”，反而增加执行效果回归风险。因此第一版只隐藏详细 Reference 正文，不牺牲 Core 原生入口。

## 5. Stable Reference ID

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
```

同一 Skill 中两个文件使用相同两位数字前缀时，Builder 必须失败，不能根据文件名猜哪一个才是正式规则。

非编号 Markdown 使用由文件名 SHA256 派生的稳定 fallback ID；正常正式 References 仍推荐沿用当前两位数字导航约定。

## 6. Bundle Contract

当前 Bundle schema：

```text
agent-skills-runtime-bundle/v1
```

每个 Reference 至少记录：

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

计算，用于证明 Runtime 与当前 canonical Reference 集合是同一个版本。`bundle_version` 当前取 `source_digest` 前 16 个十六进制字符，是机器导航版本，不替代 Git SHA 或 Release Version。

## 7. 加密与真实安全边界

当前 envelope 使用 AES-256-GCM：

```text
magic
+ random 12-byte nonce
+ authenticated ciphertext/tag
```

每次构建生成随机 32-byte key。Builder 在临时目录生成 `_embedded_payload.py`，把 key 和 ciphertext 一同打入 onefile Runtime；源仓库不提交该生成文件。

因为 Runtime 在本机必须持有解密能力，所以这不是 KMS/TEE 意义上的秘密保护。它提供的是：

- 目标项目不出现完整 Reference 明文；
- 普通使用者不能直接打开 `.md` 浏览全部规则；
- 密文篡改由 GCM tag 检测；
- 提高批量复制和静态浏览门槛。

不能据此声称：

- 本机管理员无法提取 key；
- 内存里永远没有明文；
- 反编译或 Hook 无法取得规则；
- Runtime 是可信执行环境。

## 8. MCP Tool Contract

本地 Runtime 使用 stdio MCP，stdout 只用于 MCP wire protocol。第一版稳定 Tools：

### `agent_skills_status`

返回 Runtime/bundle/schema/source digest/reference count 和当前 task/phase/load 状态，不返回规则正文。

### `agent_skills_manifest`

参数：可选 `skill`。

返回 Reference ID、skill、filename、source_path、SHA256、size，不返回 `content` / `canonical_text`。

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

`canonical_text` 必须等于 canonical source UTF-8 解码结果。它进入 Coding Agent 上下文后，作用等价于“当前 Agent 实际读取了这份 Reference 正文”；stub 自身不能替代它。

### `agent_skills_checkpoint`

参数：

```text
required_ids
phase（可选）
```

只检查当前 MCP task state 中哪些 required ID 已经 load，不做自然语言 Requirement/Review/Docs 判断。返回 `required_ids / loaded_ids / missing_ids / ok`。

## 9. Reference Stub Contract

Runtime 模式仍创建：

```text
.agents/skills/<skill>/references/<canonical filename>.md
```

因为现有 Core Skill 使用这些相对链接触发读取。Stub 至少包含：

- Runtime ID；
- canonical filename；
- Expected SHA256；
- `agent_skills_load_context` 调用示例；
- 明确 `canonical_text` 是完整正式原文；
- 必须比较返回 SHA256 与 Expected SHA256；
- MCP 不可用、ID 不存在、hash 不一致或没有 canonical_text 时停止依赖该 Reference 的动作并明确报告。

禁止把 Reference 摘要、关键规则节选或“方便版”复制进 stub；否则会形成第二套容易漂移的规则事实源。

## 10. Full 与 Runtime 两种安装模式

### Full（默认、向后兼容）

```bash
python scripts/install.py --target <target>
```

等价：

```bash
python scripts/install.py --mode full --target <target>
```

完整复制三个 Skill，包含 canonical References。适合不在意明文分发、追求最短规则读取链的场景。

### Runtime（显式 opt-in）

```bash
python scripts/install.py \
  --mode runtime \
  --runtime-command <agent-skills-mcp> \
  --target <target>
```

在任何目标文件写入前必须：

```text
source build_bundle().source_digest
=
Runtime status.source_digest
=
Runtime self-test.source_digest
```

否则失败。之后才暂存三个 Core Skill + Reference Stubs，并继续使用既有 Skill swap/backup/Bootstrap rollback。

## 11. Runtime 模式允许分发什么

目标受管 Skill 允许：

```text
SKILL.md
agents/
assets/
scripts/
references/*.md   # 仅 Runtime Stub
```

当前不复制：

```text
README.md
tests/
canonical Reference body
```

目标项目自己的：

```text
.agents/changes/
.agents/project-context.json
.agents/skills/<项目自有 Skill>/
.agents/<其他内容>/
AGENTS marker 外文本
```

仍不属于安装器清理目标。

## 12. 构建与验证

构建入口：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

构建产物至少经过：

1. canonical References UTF-8 / ID / SHA / size / source digest 校验；
2. AES-GCM roundtrip/authentication；
3. PyInstaller onefile build；
4. artifact `status --json`；
5. artifact `self-test --json`；
6. `scripts/runtime_mcp_smoke.py` 的真实 stdio MCP `tools/list` / `tools/call`；
7. `install.py --mode runtime` 的真实临时目标项目安装。

不能用“Python 模块单测绿色”直接宣称“最终 `.exe` / binary 可用”。Windows `.exe`、Linux、macOS artifact 必须在目标平台分别构建/验证；不要把一个平台的 onefile 当成跨平台产物。

## 13. 用户级安装与升级

```bash
python scripts/install_runtime.py --artifact <built artifact> --json
```

默认：

```text
Windows: %LOCALAPPDATA%\AgentSkills\bin\agent-skills-mcp.exe
POSIX:   ~/.local/share/agent-skills/bin/agent-skills-mcp
```

安装器必须在替换前验证 artifact，完整暂存后再切换；已有 Runtime 先备份，新版本 `status/self-test` 失败时恢复旧版本。

Runtime 与目标项目解耦：一台机器只需要全局/用户级安装一个 Runtime，每个目标项目通过自己的 Core Skill + Stub 使用它。

## 14. 宿主接入责任

宿主必须把已安装 Runtime 注册为 stdio MCP：

```text
command = <absolute agent-skills-mcp path>
args = ["serve"]
```

宿主只是“能看到 MCP Tools”还不等于每个任务一定会调用，所以目标项目仍保留 `AGENTS.md` + Native Core Skill。Core 的 Reference 触发条件命中后，Agent 必须读 stub 并执行其中的 `load_context` 协议。

ChatGPT 网页端不能直接启动本地 stdio Runtime；需要 Remote MCP / secure tunnel 时属于另一部署方案。

## 15. 正常任务生命周期

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

`checkpoint` 不能替代 Completion Audit、独立 Review、Docs Impact 或真实测试，因为它只知道“Reference 是否通过 MCP 取过”，不知道项目语义是否正确执行。

## 16. 升级顺序与版本锁

canonical Reference 任何原始字节变化都会改变相应 SHA，并通常改变 `source_digest`。标准升级顺序：

```text
更新 Agent_Skills source
→ build_runtime
→ install_runtime
→ 对目标项目重新 install.py --mode runtime
→ 宿主重新建立 MCP 会话（需要时）
→ 实际加载一个 Reference 验证
```

不要先用新源生成 stub，再继续使用旧 Runtime。安装器的 digest preflight 就是为了阻止这种混装。

## 17. 回滚

回滚是三件东西的版本配套：

```text
Agent_Skills canonical source
↔ Runtime source_digest
↔ Target Core/Stub expected SHA
```

要恢复旧 Runtime，应同时恢复对应源版本并重新对目标项目执行 runtime-mode install。仅替换 executable 而保留不匹配的 Stub 不是完整回滚。

## 18. 内容守恒 Review

任何 Runtime 变更完成前至少检查：

- canonical References 没有因为 Runtime 功能被摘要、压缩或搬成第二套 DSL；
- Source → Bundle `content` → decrypted Bundle → `RuntimeStore.load_context().canonical_text` 完全一致；
- manifest/stub 不泄露正文；
- stub 的 ID/SHA 与 Runtime manifest 一致；
- full 安装仍保持原行为；
- Runtime 不可用/hash mismatch 时 Agent 不能把 stub 当规则原文继续；
- Review / Docs Reference 与 Coding Reference 走同一个内容守恒链；
- 原本的 Bootstrap、target AGENTS 保护、Change carrier、项目自有 `.agents` 内容和 rollback 不回归。

如果为了“让 MCP 更智能”需要新增自动摘要、自动路由或 Policy Compiler，必须作为后续独立设计评估，不能在没有内容守恒证据时静默改变本 Runtime 的 canonical-text Contract。
