<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.14","触发":{"任一":[{"包含":{"维度":"范围","取值":["Runtime","Runtime Bundle","Project Payload","MCP"]}},{"包含":{"维度":"意图","取值":["Runtime Bundle","Project Payload"]}}]},"依赖":["coding.reference.03","coding.reference.06","coding.reference.07","coding.reference.13"],"最低风险":"L3"}
-->

# 本地 MCP Runtime 分发与原文上下文加载

这份规则定义 Agent_Skills 当前唯一正式对外分发模式：**Native Core Skill + Shared Skill Router + Project-local MCP Runtime + Encrypted Canonical References + onefile binary**。

目标是：最终使用者只拿到对应平台 Release binary，在目标项目根运行即可完成项目级接入；详细 canonical `references/*.md` 不作为普通 Markdown 分发到目标项目，同时保持现有自然语言 Skill 的执行语义和逐字完整性。跨 Skill 的 Catalog / Router 只维护一份 [`.agents/skills/ROUTER.md`](../../ROUTER.md)，源码直读和 Runtime 安装共享同一正文。

Runtime 还必须建立**模式感知的信息披露边界**：Source Mode 直接使用明文仓库时，维护者可以正常看到和讨论 Skill、Reference、文件路径、Stable ID 与路由过程；Runtime Mode 允许正常展示项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git/CI 与交付状态，但不应把治理系统内部文件名、目录结构、规则标识、命中映射、内部凭据或加载明细作为用户可见过程主动复述。

本文件只规定 Runtime 分发、动态 Skill 发现、Skills 根级共享运行资产、Project Payload、Reference 原文加载、项目级安装/升级、宿主接入、完整性、Release、披露和失败边界。Coding / Review / Docs / Figma 的研发语义仍由各自 `SKILL.md` 与 canonical References 定义；跨 Skill 入口、Reference 取得方式和 Handoff 由唯一 Router 定义。

## 1. 何时必须读取

出现以下任务时必须读取本文件：

- 构建、Release、安装或升级 `agent-skills-mcp`；
- 修改 Project Payload、动态 Skill Catalog、Skills 根级 shared runtime files、共享 Router、installation manifest 或项目宿主 MCP 配置；
- 修改 Runtime Bundle、Project Payload、install manifest、路由 metadata/Stable ID、加密格式、MCP Tool Contract、`source_digest`、`routing_digest` 或 `payload_digest`；
- 修改 Runtime 用户可见进度、MCP 公共返回字段或治理实现细节披露边界；
- 调试中文 Task Route → 私有 Routing Manifest → required canonical Context 链；
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

canonical SKILL.md / references/*.md 路由元数据
→ 编译唯一私有 Routing Manifest

canonical references/*.md
→ 唯一完整 Reference 正文
→ 构建时逐字收集、hash，并与私有 Routing Manifest 一起 AES-256-GCM 认证加密
→ 嵌入 Runtime

目标项目 Project Payload
→ 只安装 Router、Skill Core 与运行资产
→ 不安装 Reference 或 Stub

Project-local Runtime
→ 安装在目标项目 .agents/runtime/
→ Codex / Cursor / Claude Code 只配置当前项目 Runtime

Local MCP
→ 接收中文 Task Route
→ 只返回当前路由 required 的完整 canonical 原文
→ 公共 envelope 不附带不必要的 Skill / Reference 身份、文件路径、hash/size 或内部求值明细
→ 不摘要、不重写、不生成新的研发规则

Runtime 用户可见过程
→ 可以说明真实工程活动与验证证据
→ 不主动复述内部治理资产、分类、标识、路由和加载明细
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
- 不把“用户可见不主动披露”宣称成对本机 Owner 的安全隔离；
- 不隐藏目标项目自己的代码、测试、文档、配置、Git/CI 路径或实际修改过程；
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

[`.agents/skills/ROUTER.md`](../../ROUTER.md) 是根级普通文件，**不能被识别成正式 Skill**。`coding` 仍是当前目标项目研发路由的核心锚点；Router 在 Source Mode 可以展示当前 Catalog 供 Agent/维护者导航，但明确不是 Runtime 分发白名单。Runtime MCP 的公共 route contract 不需要把 Catalog 再次暴露给用户可见过程。改变 Coding 的上位入口关系属于独立架构变化，不能借动态发现静默修改。

## 4. 规则与 Router 事实源

每个正式 Skill 的专业规则事实源：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
```

跨 Skill 的 Catalog、项目事实优先、Source/Runtime 两种取得方式和 Coding/Figma/Review/Docs Handoff 的唯一正文 Owner：

[`.agents/skills/ROUTER.md`](../../ROUTER.md)

Router 是 Skills 根级 shared runtime file，不是新的专业 Skill，也不得复制各 Skill 的完整详细规则；根 `AGENTS.md` 与 `AGENTS.managed.md` 只做 Bootstrap，不再拥有第二套完整 Router。

### 源仓库 Mutation 与普通 Runtime 明文面

源仓库 Mutation 的意图识别与 canonical Ownership 由 Agent_Skills **根 `AGENTS.md`** 独立承担，详细 Skill/Reference 内容守恒继续由 ref16 承担。普通 Runtime 安装给目标项目的 shared Router 与 `AGENTS.managed.md` 不复制这套源仓库 Mutation、canonical repository、Maintenance 或跨仓库同步治理。

这不是建立第二个 Router：[`.agents/skills/ROUTER.md`](../../ROUTER.md) 仍是源码直读与 Runtime 安装共享的普通研发 Router；根 `AGENTS.md` 只在 Agent_Skills 源仓库维护场景增加源仓库专用 Bootstrap。Custom Instructions 可以把维护者意图引导到当前根 `AGENTS.md`，但不进入 Project Payload，也不替代当前源码事实。

Builder 读取 canonical References 时：

- 不修改源文件；
- 不标准化换行；
- 不去标题/frontmatter；
- 不摘要；
- Bundle entry `content` 来自原始 UTF-8 bytes 直接 decode；
- SHA256 与 size 对应同一份原始 bytes。

Runtime Mode 不在目标项目创建同名 Reference。Core/Router 中的人类可读源码链接仍必须保留给 Source Mode 和同版本运行资产，但目标项目根 managed block 不再引导 Runtime 日常任务直接打开这些受管源码导航。Runtime 日常任务通过已配置的项目级治理 MCP 取得 route contract、提交 Task Route 并加载 required Context。

**完整 canonical Context 本身不能为了用户可见保密而删改 routing metadata、Stable ID 或其他原文字节。** 模式感知披露只收窄 MCP 公共 envelope，并要求宿主不要把完整正文中的治理实现身份主动复述给用户；否则会破坏 source digest、routing provenance、逐字守恒和 Source/Runtime 同源性。

## 5. Native Core 与 Router 为什么继续明文

Core `SKILL.md` 负责：

- 让支持 Skill/Rules/AGENTS 的宿主进入本 Skill 的正式工作流；
- 恢复项目事实并完成任务/风险/工具链路由；
- 决定何时必须读取某个 Reference；
- 保留 Reference 缺失/加载失败时的停止条件和完成门禁。

共享 Router 负责：

- 在 Source Mode 提供唯一跨 Skill Catalog / Router；
- 在 Runtime Project Payload 中作为同版本 shared runtime asset 保持宿主兼容与内部导航；
- 固定项目事实优先；
- 说明 Source Mode 直接读取 canonical Reference 与 Runtime Mode 通过 Task Route 加载 required Context 两种取得方式；
- 把 Coding / Figma / Review / Docs Handoff 放在单一 Owner，而不是复制到两个 AGENTS 入口。

如果 Core/Router 也完全从 Project Payload 删除，只留下 MCP Tool，支持原生 Skill/Rules 的宿主可能失去当前进入工作流所需的运行资产，会增加执行效果和兼容回归风险。因此 Core/Router/必要运行资产继续作为 Project Payload 明文安装；详细 canonical Reference 正文保留在加密 Bundle 中。

**“继续明文安装”与“用户可见过程不主动展示”是两个不同边界。** 目标项目 Owner 仍可查看这些本地文件，本方案不宣称物理隐藏；managed block 和 MCP Contract 只要求 Runtime 日常工作不把这些内部资产作为用户过程输出，也不把源码维护导航当作 required Context 的本地替代路径。

## 6. Canonical 路由元数据与 Stable Reference ID

完整自然语言 `SKILL.md + references/*.md` 仍是唯一规则语义。路由元数据只回答“什么任务事实会命中、依赖哪些 Reference、最低风险是什么”，不得承载自然语言规则摘要。

每个正式 `SKILL.md` 和 Reference 必须且只能包含一个 UTF-8 JSON 注释块：

```text
HTML 注释开始 + agent-routing:v1
{中文 JSON 对象}
HTML 注释结束
```

自有键和值使用中文；协议名、Skill 名、Stable ID、L1/L2/L3、Git、Figma 等技术标识可保留原样。元数据必须由构建器严格解析、规范化和校验，禁止任意表达式执行或 build 时调用 LLM。

Reference Stable ID 是 metadata 中的显式 `标识`，例如：

```text
coding.reference.14
```

它不再由文件名或两位数字前缀推导。文件改名默认不改变 Stable ID；真正修改 ID 是内部 Runtime Contract / canonical identity 变化，必须记录迁移、兼容、回滚和 conformance 证据。所有 ID 全局唯一；依赖必须指向真实 ID、无环且无悬空引用。Runtime MCP v3 不再把这些 Stable ID 作为普通 `load_required_context` envelope 字段公开，但它们继续存在于认证加密 Bundle 和 canonical 原文中。

## 7. Reference Bundle v2

Bundle 当前协议：

```text
agent-skills-runtime-bundle/v2
```

构建器动态发现正式 Skill，逐字读取 canonical Reference 原始 UTF-8 bytes，并把下列信息放入同一个认证加密边界：

```text
完整 Reference 原文
+ 显式 Stable ID / Skill / filename / source_path / SHA256 / size
+ 由 canonical metadata 编译的私有 Routing Manifest
```

其中：

- `source_digest` 独立证明所有 Reference 的身份、路径、hash 和大小；
- `routing_digest` 独立证明规范化 Skill/Reference 路由、依赖和风险下限；
- `bundle_version` 同时绑定 Bundle schema、`source_digest` 与 `routing_digest`；
- serialize → encrypt → decrypt → deserialize 后，原文、manifest、两个 digest 和同一 Task Route 的求值结果必须一致；
- 任何非法 UTF-8、hash/size 不一致、manifest 不一致、重复 ID、悬空依赖、循环依赖或未知协议都必须失败关闭。

私有 Routing Manifest 不能单独作为公开构建产物，也不能通过普通 status、self-test 或 MCP route contract 枚举。MCP v3 进一步要求普通 required Context envelope 不附带 Reference ID、Skill、filename、source_path、SHA256 或 size；这些字段仍在 Runtime 内部用于完整性和路由。

## 8. Project Payload v2：只分发 Core，不分发 Reference/Stub

Project Payload 当前协议仍为：

```text
agent-skills-project-payload/v2
```

它只用于在没有源仓库和 Python 安装脚本的目标项目中重建：

```text
ROUTER.md
+ 每个正式 Skill 的 SKILL.md / agents / assets / scripts / templates / schemas 等运行资产
```

明确禁止进入 Project Payload：

- `references/*.md`，无论是 canonical 正文还是 Stub；
- 私有 Routing Manifest；
- 任意深度的维护 `README.md`；
- tests、Python cache 和编译产物。

Payload 必须动态发现 Skill，显式记录 `skills`、`shared_files`、文件 path/hash/size/mode 和 `payload_digest`。`ROUTER.md` 当前是唯一 Skills 根级 shared file；根级任意新文件不会自动进入 Payload。

Project Payload 的 `mode` 必须以 Git index executable bit 为跨平台 canonical 来源：普通文件映射为 `0644`，Git 标记 executable 的文件映射为 `0755`；非 Git 源只按宿主是否存在任一执行位回退到同一组可移植权限。不得直接把 Windows `0666` 或其他宿主 `stat` mode 写入 Payload identity，导致同一 source commit 在三平台得到不同 `payload_digest`。

目标项目因此没有 Agent_Skills 的同名 Reference 文件。Runtime Mode 命中规则时不得尝试打开本地 `references/<file>.md`，也不得寻找或生成 Stub，而是通过当前 Task Route 的路由令牌取得 required canonical Context。目标根 `AGENTS.md` 同时明确禁止把受管源码维护导航当作 Runtime 日常 required Context 入口。

## 9. 单一 Routing Compiler / Evaluator

Source Mode 与 Runtime Mode 使用同一 canonical metadata、Stable ID、依赖图和风险下限。唯一 evaluator 语义是：

```text
校验中文 Task Route 和公开词汇
→ 多个事实条件取并集
→ 匹配 Skill 与 Reference
→ 展开跨 Skill 依赖闭包
→ 应用 required Context 的风险下限并重新求值到固定点
→ 未知事实保守扩大，不选择狭窄路径
```

同一 task 后续提交采用单调扩展：新 required Context 与此前 required Context 取并集，只有显式 `start_task` 建立新任务才能清空。

canonical routing compiler 的原始 `public_route_contract()` 可以在 Source/维护侧包含动态 Skill Catalog，供一致性和构建测试使用；**Runtime MCP 公共路由 Contract v2 在返回宿主前移除 Skill Catalog**，只暴露构造 Task Route 所需的中文维度、合法取值与说明，并附带用户可见进度边界。两者都不得返回 Reference ID、文件名、路径、数量、trigger→Reference mapping 或依赖图。

新增普通 Skill/Reference 通过 committed metadata 和动态发现进入编译，不修改 Runtime 固定白名单或 Task Route 顶层 schema。

Task Route 是宿主模型与 Runtime 的内部交换协议，不是用户配置文件。用户继续用自然语言提出任务；宿主模型依据目标项目事实构造路由，Runtime 只校验和求值，不扫描目标项目猜技术栈，也不调用模型。Task Route、命中 Skill、required ID 集合、风险下限和 route token 都属于 Runtime 执行细节，不应作为日常用户过程主动展示。

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

模式感知用户可见边界额外提供：

- 正常 Agent 过程输出不需要列出内部 Skill/Reference 文件名和路径；
- MCP envelope 不再主动提供不必要的内部身份字段，降低模型顺手复述的机会；
- 仍允许完整展示代码、测试、文档、Review、Git/CI 和验证等真实工程过程。

不能据此宣称：

- 本机管理员无法提取 key；
- 内存永远没有明文；
- 目标项目 Owner 无法查看已安装的明文 Core/Router；
- 反编译、Hook 或 MCP 通信观测不能取得规则；
- Prompt/managed block 可以成为机密安全边界；
- Runtime 是可信执行环境。

源仓库 canonical 文本的访问控制必须由仓库权限承担。

## 11. MCP Tool Contract v3 与用户可见披露边界

本地 Runtime 使用 stdio MCP；`serve` 模式下 stdout 只用于 MCP wire protocol。稳定 ASCII Tool 名保持不变：

```text
agent_skills_status
agent_skills_route_contract
agent_skills_start_task
agent_skills_submit_route
agent_skills_load_required_context
agent_skills_checkpoint
```

正式 Runtime 不再提供 `agent_skills_manifest` 或接受 `ids` 的任意加载 Tool。MCP v3 收窄的是**返回字段**，不是调用顺序、canonical 规则或路由语义。

所有关键工具响应都携带同一 `用户可见进度规则`，语义必须覆盖：

```text
允许：
项目调查 / 需求与风险判断 / 代码修改 / 测试 / 文档同步 / 复核 / Git/CI / 交付状态

禁止主动复述：
治理系统内部分类 / 文件名 / 目录路径 / 规则标识 / 路由映射 / 内部凭据 / 加载明细

解释原因：
解释工程步骤本身为什么需要，而不是引用内部治理资产名称
```

该规则只约束 Runtime Mode 的用户可见表达；Source Mode 明文仓库维护任务可以正常显示内部文件、Skill/Reference 和路由过程。

### `agent_skills_status`

只返回：

- MCP Tool Contract 协议；
- Release 版本；
- 当前任务是否存在；
- 当前约束是否已建立；
- 当前约束是否已加载完成；
- 用户可见进度规则。

不得返回 Skill Catalog、Reference count/ID、loaded IDs、文件名、路径、source/routing/payload digest、内部协议全表或 required/loaded 数量。

### `agent_skills_route_contract`

动态返回当前 `Agent Skills MCP公共路由契约/v2`：稳定中文维度、当前公开取值及说明、Task Route 协议和用户可见进度规则。不得公开 Skill Catalog、Reference ID/文件名/路径/数量、触发映射或依赖图。

### `agent_skills_start_task`

中文请求字段：

```json
{"任务标识":"task-001","阶段":"规划"}
```

显式建立或重置任务，清空此前 task 的 route、required Context 和 loaded Context。切换 task 不能靠提交不同 ID 静默发生。响应只需要返回任务标识、当前阶段、当前约束未建立和用户可见进度规则。

### `agent_skills_submit_route`

中文请求字段保持：

```json
{
  "任务标识":"task-001",
  "任务路由":{
    "协议":"Agent Skills 任务路由/v1",
    "信号":{
      "执行模式":["实现"],
      "项目形态":["前端Web"],
      "阶段":["功能开发"],
      "风险":["L2"],
      "工具链":["已确认"],
      "范围":["前端","API"],
      "意图":[],
      "治理":["存在活动变更"],
      "能力":["Git","测试"],
      "授权":["允许修改项目"]
    },
    "未知项":[],
    "依据":["目标项目当前真实入口和调用链"]
  }
}
```

Runtime 校验协议和公开词汇，使用唯一 evaluator 求值，并与当前 task 已有 required Context 做单调并集。内部仍保留命中 Skill、required ID、依赖闭包、风险下限和 unknown 状态；公共响应只返回：

- task；
- 不透明路由令牌；
- 是否需要继续加载约束；
- 是否仍存在未确认任务事实；
- 用户可见进度规则。

不得返回命中 Skill、required/缺失数量、最低风险、Reference ID 或未命中目录。

`授权` 只是任务事实数据，不能替宿主授予 Git、发布、部署、数据库写入或任何外部副作用权限。

### `agent_skills_load_required_context`

请求只提供当前不透明 `路由令牌`，可选 `重新加载`。Runtime 只返回当前 task 已求值为 required 的完整 canonical 原文；默认只返回尚未加载的新 Context。

每个公开 Context envelope 必须且只能是：

```json
{"完整原文":"<canonical exact text>"}
```

外层只需要返回任务标识、`上下文`、`加载完成` 和用户可见进度规则。不得附带 Stable ID、Skill、SHA256、字节数、文件名、source path、required/loaded 数量或全库 Catalog。

**完整原文仍逐字包含 canonical 文件原本拥有的 routing metadata/frontmatter/正文。不得为了隐藏 Stable ID 或内部词汇而修改 `完整原文`。** 这些文本用于模型执行治理，但用户可见过程受本节 disclosure rule 约束，不应主动复述其中的治理资产身份。

不得通过参数请求任意非 required ID。旧令牌、其他 task 令牌、空令牌或未先提交 route 必须失败关闭。

### `agent_skills_checkpoint`

请求为：

```json
{"路由令牌":"...","阶段":"完成前检查"}
```

不接受 `required_ids`。Runtime 根据内部 required/loaded 状态返回 task、是否通过、当前阶段和用户可见进度规则；不得公开缺失/已加载数量或内部最低风险。它不能替代 Requirement Traceability、Completion Audit、Review、Docs、测试或 CI。

### `self-test` 的不透明完整性证明

公共 `status` 不再公开 source/routing/payload digest 和 Catalog，但 Builder 仍必须证明 onefile artifact 与当前源码、路由、Payload、Release/source identity 完全一致。为此 `self-test` 在完整 Bundle 验证通过后额外返回一个**不可逆整体完整性指纹**：

```text
bundle schema/version
+ source_digest
+ routing_digest
+ Skill Catalog
+ release_version
+ payload_digest
+ source_commit
+ MCP Tool Contract version
→ deterministic JSON
→ SHA256 完整性指纹
```

Builder 在维护侧用同一构建材料独立计算期望指纹，要求 artifact `self-test` 完全一致。这样保留构建强校验，又不需要把详细内部 identity 字段通过 Runtime 公共状态逐项暴露。

真实 MCP 验证必须通过 SDK 执行 `tools/list` 和 `tools/call`，断言六个 Tool、中文 property、去标识化 envelope、route→submit→required Context exact-text→checkpoint 全链，不能用内部 Python 方法冒充协议兼容。

## 12. 最终用户 CLI 与项目级安装

稳定入口：

```text
无参数
→ install 当前工作目录

install --target <项目根目录>
→ 显式安装/升级

status --json
→ 查看 Release 版本与当前最小运行状态

self-test --json
→ 校验内嵌 Runtime/Project Payload，并返回通过状态与整体完整性指纹

serve
→ stdio MCP Server
```

项目 Runtime 安装：

```text
Windows: .agents/runtime/agent-skills-mcp.exe
POSIX:   .agents/runtime/agent-skills-mcp
```

`.agents/runtime/` 是本地运行资产，应被目标项目 `.gitignore` 忽略。

## 13. Install Manifest v3 与逐文件 ownership

当前项目安装协议：

```text
agent-skills-install/v3
```

manifest 记录 Release、`source_digest`、`payload_digest`、公开 Skill/`shared_files`、项目 Runtime、宿主配置和显式 `managed_files`。真正决定更新/删除边界的是相对 `.agents/skills` 的逐文件 `managed_files`，不是“整个 Skill 目录归安装器”。这些维护/ownership 字段存在于项目 manifest 不等于它们必须通过 MCP `status` 或用户过程输出再次公开。

规则：

```text
新 Payload 文件 + 目标不存在
→ 创建并在 v3 manifest 认领

目标文件 + 旧 v3 manifest 明确认领
→ 原子升级

旧 v3 managed file + 新 Payload 已删除
→ 只删除该受管文件

目标同名文件 + 旧 manifest 未认领
→ 项目自有/归属不明
→ fail closed，不猜 ownership

同一 Skill 目录内未认领的项目文件/Reference
→ 保留
```

首次安装遇到未认领的同名正式 Skill 目录或 `ROUTER.md` 仍必须在任何写入前失败关闭。不同名项目 Skill、项目自有 `.agents` 内容、AGENTS marker 外文本和其他 MCP server 永不因普通升级而清理。

安装器只接受 `agent-skills-install/v3`。v1、v2、未知或损坏 manifest 全部失败关闭；实现中不保留旧 schema 解析、目录级 ownership 推断、旧 Stub 识别或自动清理分支。需要从旧安装切换时，由项目 Owner 在当前安装器之外先备份并显式处理旧安装边界。

## 14. AGENTS / `.gitignore` / 宿主配置保护

项目安装还会建立：

- 根 `AGENTS.md`：创建或只更新 `agent-skills:managed` block；该 block 只负责项目事实优先、调用已配置的项目级治理 MCP、首次治理校准、受管资产保护、失败关闭和用户可见进度边界，不直接暴露项目内 Router/Skill/Reference 源码导航；
- `.gitignore`：增量加入项目缓存和 Runtime ignore；
- Cursor：`.cursor/mcp.json` 的 `mcpServers.agent-skills`；
- Claude Code：`.mcp.json` 的 `mcpServers.agent-skills` + `CLAUDE.md` 最薄 `@AGENTS.md` bridge；
- Codex：`.codex/config.toml` Agent Skills 自管 MCP block。

只能修改稳定可证明边界：

- AGENTS/CLAUDE/Codex 使用 managed marker；
- JSON 只认领 `mcpServers.agent-skills`；
- 其他配置、其他 MCP server、marker 外文本保持；
- 已存在未被 manifest 认领的同名 Agent Skills MCP 时拒绝静默覆盖；
- **Codex 已存在 `[mcp_servers.agent-skills]` 但 managed marker 缺失时，即使旧 install manifest 仍存在，也必须 fail closed；manifest 不能证明当前 TOML table 仍是可安全替换的原受管块；**
- 已存在未被 manifest 认领的同名 Skill/shared file 时拒绝静默覆盖；
- marker 损坏、文本编码不可安全增量编辑、受管路径为符号链接时预检失败。

Runtime managed block 还必须明确：正常工程过程可以显示，但内部治理实现细节不作为用户过程输出；Runtime Mode 不根据受管运行资产里的 Source Mode 导航去本地枚举或尝试读取不存在的 Reference。Codex workspace trust 以及 Cursor/Claude 的首次确认属于宿主安全边界，安装器不得绕过。

## 15. 安装原子性与回滚

安装器修改项目研发入口，必须先完整预检，再进入可恢复写入：

1. 验证 Project Payload v2、path/hash/size/mode/shared files/no-reference 边界；
2. 校验 v3 install manifest、逐文件 ownership、同名冲突、符号链接、AGENTS/host marker 和 JSON/TOML 边界；
3. 对全部新/旧 managed files、Runtime、manifest 和受管文本保留原始 bytes/权限快照；
4. 每个受管文件使用同目录临时文件 + 原子替换，不移动或替换整棵 Skill 目录；
5. 只删除旧 v3 明确认领且新 Payload 已删除的文件；
6. 安装 Runtime 并验证 artifact SHA256；
7. 写入 AGENTS、`.gitignore`、宿主配置和 v3 manifest；
8. 任一步异常时恢复本轮 touched 文件、Runtime、manifest 与受管文本快照；
9. **任何快照恢复失败都必须聚合到明确的“回滚不完整”错误中，并把原始安装异常保留为 cause；不得用 `except: pass` 静默吞掉回滚失败后只报告最初异常。**

目标路径任一上级是符号链接、目标是特殊文件、manifest 损坏或 ownership 不可证明时必须失败关闭。回滚不得使用 `git reset --hard`、`git clean`、强制推送或历史重写。

普通文件系统不是数据库事务；实现必须把所有可预检失败前移，并让故障注入测试证明 Router 写入失败、Runtime hash 失败以及安装失败后 rollback 自身失败时的可恢复/可诊断行为。

## 16. 构建与验证

Builder 固定顺序：

```text
规范化显式 release_version（未传则 0.0.0-dev）与真实 source commit
→ 动态发现 Skill/Reference
→ 解析并校验 committed canonical metadata
→ 编译私有 Routing Manifest / routing_digest
→ 构建 Bundle v2 / source_digest / bundle_version
→ 量化 Router / Skill Core / Reference 聚合 Context footprint
→ 构建 no-Stub Project Payload v2 / payload_digest
→ AES-256-GCM 认证加密 Bundle
→ 生成当前平台 onefile
→ artifact status / self-test + 不透明完整性指纹交叉验证
→ 真实 stdio MCP smoke
```

至少验证：

1. 所有 Skill/Reference metadata 协议、中文字段、Stable ID、依赖、风险下限合法；
2. ID 全局唯一，依赖无环、无悬空项，文件 rename 不静默改变显式 ID；
3. canonical 原始 bytes、SHA256、size 和 `source_digest` 在 build/encrypt/decrypt 后逐字一致；
4. Routing Manifest 稳定序列化、`routing_digest` 和同一 Task Route 求值在编译/加密 roundtrip 前后一致；
5. Project Payload 动态包含 Router、全部 Skill Core/运行资产，但没有 `references/`、Stub 或私有 Routing Manifest；
6. `status` 不公开 Skill Catalog、Reference count/ID/filename/path/loaded IDs 或内部 digest；`self-test` 只额外公开不可逆整体完整性指纹；Builder 的 `context_budget` 只允许输出 Router、各 Skill Core、各 Skill Reference 总字节和 Router+Core 聚合值，不得列单个 Reference 身份；
7. 真实 MCP `tools/list` 恰为六个 Tool，中文 property 可调用，Runtime 公共 envelope 不泄露内部身份，route→submit→load exact-text→checkpoint 成功；
8. `load_required_context` 每项公开 envelope 只含 `完整原文`，且原文与 canonical source 逐字一致；
9. 同一 task 多次 route 只能单调扩展，旧 token/任意 ID load/未知词汇失败关闭，未知事实保守扩大；
10. 首次安装、无参数安装、显式 target、v3 升级、非 v3 schema 拒绝、项目自有 Reference 保留、同名冲突、符号链接、Codex marker 丢失 fail-closed 和 rollback/rollback-failure reporting；
11. Source Mode 根入口继续可见唯一 Router；Runtime 安装后的根 `AGENTS.md` 不主动暴露 `.agents/skills/`、Router/Reference 名称、Stable ID 或内部路由细节，同时保留代码、测试、文档、复核、Git/CI 等工程进度语义；
12. 维护侧 `release_version`、`python_version`、`source_commit`、Bundle/Task Route/Routing Manifest/MCP/Project Payload/install schema、三个 digest、Project Payload 和 artifact identity 仍通过构建 manifest + 完整性指纹交叉一致。

Routing Conformance Benchmark 必须永久覆盖 Greenfield、Fact Recovery、L1/L2/L3、Feature/Bug/Incident/Refactor/Performance/Schema、Frontend/Figma/Docs/Review、多 Agent/多 Change、Dependency/CI/Git/PR/Release、Runtime/Project Payload/Skill Mutation/Security、unknown 和复杂组合。最低门禁是 `Expected Required ⊆ Actual Required`；每次修改 trigger/依赖/风险下限都同步审查正例、必要反例和 ambiguous case，并力求 `Expected == Actual`。

正式平台构建的 Python 版本必须由永久 CI/Release workflow 显式固定；不能使用 Linux/Windows/macOS Runner 各自随机漂移的预装 Python 冒充同一构建环境。不同平台的 onefile 必须在 Linux、Windows、macOS 对应 Runner 构建、启动、MCP smoke 和 project install，不能把一个平台的产物当跨平台证据。

## 17. Release Identity 与正式资产

构建器生成的 artifact identity manifest 只用于本地/CI 校验，不是 Reference manifest，也不进入正式 Release 资产。当前 schema：

```text
agent-skills-runtime-release-identity/v1
```

维护侧构建 manifest 可以包含：

```text
release_version / source_commit
artifact / artifact_sha256 / python_version
Bundle/Task Route/Routing Manifest/MCP Tool/Project Payload protocol
bundle_version / source_digest / routing_digest / payload_digest
Skill 集合
```

这些维护侧 identity 字段不等于 Runtime MCP 公共状态。Runtime `status --json` 只公开 Release 版本和最小任务状态；`self-test --json` 只额外公开通过状态和不可逆整体完整性指纹。不得通过 Runtime 公共 Tool 枚举 Reference ID、文件名、路径、数量、trigger mapping、依赖图或 canonical 原文 Catalog。

Builder 可以在维护者构建结果中返回聚合 `context_budget`，但该信息不进入 Runtime `status/self-test` 的 Reference 明细面。

正式 GitHub build 必须满足 `source_commit == GITHUB_SHA == 当前 checkout HEAD`；不一致、伪造或无法解析时失败。非 Git 本地源码允许明确为 `null`，不能编造 commit。

仓库不维护独立根版本文件。**正式 Release 的唯一版本来源是 `.github/workflows/release.yml` 手工输入的 `v<SemVer>` tag；workflow 去掉前缀 `v` 得到 `release_version`，并把同一个值显式传给三个平台 Builder。**普通本地、PR 和 main 常规构建没有正式 tag 时使用 `0.0.0-dev` development identity，不得冒充已发布版本。

正式 Release 只发布三平台 binary、[`USAGE.md`](../../../../USAGE.md) 与 `SHA256SUMS`；不发布构建期 identity manifest、源包、Python 安装器、Runtime Kit、私有 Routing Manifest 或公开 Reference Catalog。构建期 identity manifest 至少绑定 `release_version`、真实 `source_commit`、artifact 文件名/SHA256、构建 `python_version`、source/routing/payload digest 以及 Bundle/Task Route/Routing Manifest/MCP/Project Payload/install 协议版本；workflow 先逐一验证协议、digest 与 `artifact_sha256`，再删除平台特有 `artifact` / `artifact_sha256` 字段并比较三平台其余公共 identity，任一漂移都必须失败关闭。完成交叉校验后必须在生成 checksum 和 Release 前删除这些 manifest。

Release workflow 必须从 main 构建，在正式构建前校验 tag 不存在、Release 不存在，再在目标 main SHA 上重新运行完整 self-contained tests 与 Ready Check。workflow 不依赖自定义 PAT/Actions Secret，也不读取或要求仓库 Release Immutability 设置；tag/Release 操作使用 GitHub Actions 自动提供的 `github.token`，发布 job 只申请最小 `contents: write` 权限。三平台继续使用同一固定 Python 版本，且 identity 必须满足 `source_commit == GITHUB_SHA`、`release_version == tag 去 v 后值`、artifact SHA256 和协议/digest 一致。

正式资产完成交叉校验后，workflow 必须先创建 **Draft Release**，上传三平台 binary、[`USAGE.md`](../../../../USAGE.md) 和 `SHA256SUMS`，核对 Draft 资产集合完整后才 Publish；发布后再核对 tag 指向当前 `GITHUB_SHA` 与资产集合。正式发布不使用 Release Immutability，有仓库管理权限的维护者仍可修改或删除已发布资产；workflow 拒绝覆盖已有 tag/Release，但不能把这项流程保护描述成不可变存储。Draft 上传不完整、identity 不一致或发布后 tag/资产不可验证时必须失败关闭。

版本语义分为两种：网页端读取当前 main、Runtime 使用当前最新 Release 时追求“最新规则”，但发布间隙允许短暂版本差；需要严格复现正式 Runtime 时，使用 Runtime `status --json` 的 `Release版本` 定位对应正式 Release/tag，再读取该 tag/commit 的 Source Mode 规则。development `0.0.0-dev` 不能仅靠公共 Runtime 状态反推出任意构建 commit；维护者需要使用本次构建保留的 identity manifest 或 CI 证据完成精确复现。

AES-GCM 和 onefile 只减少普通明文浏览面并检测静态篡改，不是 TEE/KMS，也不能抵御机器 Owner、调试器、内存转储、Hook、MCP 通信观测或专业逆向。canonical 源码访问仍由仓库/制品渠道权限控制；如果源仓库是 Public，则 canonical Skill/Reference 本身就是公开内容，Runtime 加密不能反向把公开源码变成保密事实。Runtime 的用户可见 disclosure rule 同样不是安全隔离承诺。

## 18. 升级

升级必须使用同一 Release 的 binary；Payload 与 identity 已嵌入该 binary，不能跨版本拆换：

```text
校验当前平台 artifact / SHA256
→ 校验 Bundle v2 / Project Payload v2 / routing identity
→ 只读取并校验 v3 manifest
→ 预检 managed_files / 项目自有内容 / host config
→ 逐文件原子升级 Runtime + Core + Router + managed 配置
→ 写入 v3 manifest
→ status / self-test / MCP / install smoke
```

Reference bytes 变化只通过新 Bundle 与 `source_digest` 体现；route metadata/依赖/风险变化通过 `routing_digest` 体现；Core/Router/运行资产变化通过 `payload_digest` 体现。三者不能互相代替。

v1/未知 install schema、Bundle v1、旧 MCP Contract 或损坏状态不静默兼容。需要跨不兼容 Contract 迁移时必须建立独立 Change，给出明确迁移/回滚与验证，不保留无限期双路径。

## 19. 回滚

安装过程内失败由 v3 Installer 快照恢复；用户手工回退必须取得目标版本的完整同平台资产并重新运行安装，不能只替换 Runtime、Router、Skill Core 或 manifest。

如果安装过程自身失败且任何快照恢复失败，安装器必须明确报告“回滚不完整”及未恢复路径/原因，并保留最初安装异常作为根因链；不得因 rollback exception 被吞掉而让维护者误判项目已经恢复。

如果目标版本不理解当前 schema/ownership，应停止并按该版本正式迁移说明处理。不得手工删除归属不明的 `.agents` 内容，不得用 Git destructive 命令冒充安装回滚。

## 20. 正常任务生命周期

### Source Mode

```text
目标项目 AGENTS / 真实事实
→ Agent_Skills 根 AGENTS / ROUTER
→ 读取命中 Skill Core
→ 用 canonical metadata 的同一语义确定 Required References
→ 直接读取 Agent_Skills 源仓库中这些 Reference 的当前完整原文
→ Coding / Review / Docs / Figma Handoff
→ 真实验证与交付门禁
```

Source Mode 是明文维护/直读模式；在用户已经有源码访问权时，可以正常显示正在读取哪个 Skill/Reference、具体路径、路由判断和维护过程，不应用 Runtime Mode 的用户可见隐藏策略伪装源码事实。

### Runtime Mode

```text
目标项目 AGENTS managed block / 当前项目真实事实
→ 使用已配置的项目级治理 MCP
→ agent_skills_route_contract
→ agent_skills_start_task
→ 宿主依据当前项目事实提交中文 Task Route
→ agent_skills_submit_route
→ agent_skills_load_required_context(路由令牌)
→ 使用返回的完整原文
→ 事实变化时追加 submit_route 并只加载新增 required Context
→ agent_skills_checkpoint
→ Coding / Review / Docs / Figma Handoff 与真实门禁
```

目标项目中的 Router/Core 继续作为当前 Release 的受管内部运行资产存在，但根 managed block 不引导模型把这些 Source Mode 导航当作 Runtime 日常 required Context 取得路径。Runtime Mode 不尝试打开目标项目不存在的同名 Reference。

两种模式共享同一 canonical Markdown、Stable ID、路由 metadata、依赖、风险下限和版本身份，只改变 Context 的取得通路和用户可见披露层。任何必需 Context 无法取得、digest/协议不一致或路由含未公开值时，明确报告并停止依赖该规则的动作。

Runtime Mode 对用户可以继续说明：检查了哪些**目标项目**代码/配置/测试、准备补什么测试、修改了什么业务文件、是否同步文档、运行了什么验证、Review/CI/Git 状态如何；但不要把内部 Skill/Reference 文件、Stable ID、route token、命中集合或 Context 加载计数作为过程播报。需要解释“为什么补测试/同步文档/做 Review”时，直接说明工程风险和影响，不说“因为命中了某内部规则”。

授权信号不产生权限；checkpoint 不产生完成事实；Runtime 不执行 Git/PR/Release/部署/数据库副作用。

## 21. ChatGPT 网页端边界

当前 Runtime 是项目本地 stdio MCP。纯网页端 ChatGPT 不能直接启动用户电脑上的 `agent-skills-mcp`，也不能因为 GitHub 中存在 Runtime 源码就把本地 MCP 当作已经连接。

网页端如果通过 GitHub 获得 Agent_Skills 源仓库读取权限，使用 Source Mode：先读取目标项目事实与 Agent_Skills 根 AGENTS.md，再按 Router 和 canonical metadata 直接读取 required References。该路径是源码直接读取模式，不调用本地六个 MCP Tool，也不读取/修改目标项目的 Runtime 安装副本；因为这是 Source Mode，可以正常显示明文 Skill/Reference 和源码导航过程。

网页端如需调用目标机器 Runtime，必须使用受支持的 Remote MCP、安全隧道或等价远程部署；这是另一部署形态，不属于当前本地 stdio Runtime，不得为实现它绕过宿主、网络或权限边界。
