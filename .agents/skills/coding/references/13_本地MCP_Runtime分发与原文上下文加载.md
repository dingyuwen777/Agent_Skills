<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.14","触发":{"任一":[{"包含":{"维度":"范围","取值":["Runtime","Runtime Bundle","Project Payload","MCP"]}},{"包含":{"维度":"意图","取值":["Runtime Bundle","Project Payload"]}}]},"依赖":["coding.reference.03","coding.reference.06","coding.reference.07","coding.reference.13"],"最低风险":"L3"}
-->

# 本地 MCP Runtime 分发与原文上下文加载

这份规则定义 Agent_Skills 当前唯一正式对外分发模式：**Shared Entry + Native Router/专业 Runtime Skill Projection + Project-local MCP Runtime + Encrypted Canonical References + onefile binary**。

目标是：正式 Release 为 Windows、Linux、macOS 分别发布一个平台 ZIP；每个 ZIP 根目录只包含对应平台 binary 与同一版本的 [`USAGE.md`](../../../../USAGE.md)，最终使用者只需下载并解压当前平台 ZIP，运行其中 binary 即可完成项目级接入。详细 canonical `references/*.md` 不作为普通 Markdown 分发到目标项目，同时保持现有自然语言 Skill 的执行语义和逐字完整性。薄入口是 [`.agents/skills/ENTRY.md`](../../ENTRY.md)，跨 Skill Catalog / Router 的唯一人工维护正文仍在 [`.agents/skills/router/SKILL.md`](../../router/SKILL.md)；Source Mode 直接读取 canonical Core，Runtime 安装由同一 canonical Core 构建确定性的 Runtime Projection，不维护第二份人工 `SKILL.md`。

Runtime 还必须建立**模式感知的信息披露边界**：Source Mode 直接使用明文仓库时，维护者可以正常看到和讨论 Skill、Reference、文件路径、Stable ID 与路由过程；Runtime Mode 允许正常展示项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git/CI 与交付状态，但不应把治理系统内部文件名、目录结构、规则标识、命中映射、内部凭据或加载明细作为用户可见过程主动复述。

本文件只规定 Runtime 分发、动态 Skill 发现、Skills 根级共享运行资产、Project Payload、Reference 原文加载、**无 sidecar 项目级 installation ownership**、宿主接入、完整性、Release、披露和失败边界。Coding / Review / Docs / Figma 的研发语义仍由各自 canonical `SKILL.md` 与 canonical References 定义；跨 Skill 入口、Reference 取得方式和 Handoff 由唯一 Router 定义。

## 1. 何时必须读取

出现以下任务时必须读取本文件：

- 构建、Release、安装或升级 `agent-skills-mcp`；
- 修改 Project Payload、动态 Skill Catalog、Skills 根级 shared Entry、Router Skill、Runtime install-state 或项目宿主 MCP 配置；
- 修改 Runtime Bundle、Project Payload、previous ownership、legacy install manifest 迁移、路由 metadata/Stable ID、加密格式、MCP Tool Contract、`source_digest`、`routing_digest` 或 `payload_digest`；
- 修改 Runtime Skill Projection、Runtime 用户可见进度、MCP 公共返回字段或治理实现细节披露边界；
- 调试中文 Task Route → 私有 Routing Manifest → required canonical Context 链；
- Review Runtime 是否仍逐字返回 canonical Reference；
- 修改正式 Skill 或 shared runtime file，使其进入下一次 Runtime Release；
- 修改 onefile 项目安装、升级、rollback 或 fail-closed ownership 逻辑；
- 修改 Builder/Release identity 证据的传递方式、三平台 SHA 校验或平台 ZIP 资产合同。

## 2. 设计目标与非目标

### 目标

```text
Agent_Skills 源仓库 .agents/skills/*/SKILL.md
→ 构建时动态发现正式 Skill
→ canonical Core 是唯一人工维护的 Skill 规则 Owner

Agent_Skills 源仓库 .agents/skills/ENTRY.md
→ 显式 Skills 根级 shared runtime file
→ 只负责恢复项目事实、无条件进入 Router、失败关闭

Agent_Skills 源仓库 .agents/skills/router/SKILL.md
→ 动态发现的正式 Router Skill
→ 唯一跨 Skill 选择与 Handoff canonical 控制面

canonical SKILL.md
→ 根据当前 Bundle 中实际 Reference 身份生成 deterministic Runtime Skill Projection
→ 去除 Reference filename / source_path / Stable ID / 直接 Markdown 导航与内部编号映射
→ 保留 frontmatter、Skill routing metadata、核心工作语义、失败关闭和完成门禁

Shared Entry + Runtime Router/专业 Skill Projection / 必要运行资产
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
→ 只安装 Entry、Router/专业 Skill Runtime Projection 与运行资产
→ 不安装 Reference 或 Stub

Project-local Runtime
→ 安装在目标项目 .agents/runtime/
→ 自身内嵌当前 Release 的 Project Payload ownership
→ 后续升级通过内部 install-state 提供 previous managed_files
→ 不写 .agents/agent-skills-install.json 或其他 ownership sidecar
→ Codex / Cursor / Claude Code 只配置当前项目 Runtime

Local MCP
→ 接收中文 Task Route
→ 只返回当前路由 required 的完整 canonical 原文
→ 公共 envelope 不附带不必要的 Skill / Reference 身份、文件路径、hash/size 或内部求值明细
→ 不摘要、不重写、不生成新的研发规则

Runtime Builder / Release
→ build_runtime.py --json 直接返回 release/source/python/integrity/digest/artifact SHA identity
→ GitHub Actions job outputs 传递三平台公共 identity
→ Release job 比较公共 identity 并对下载后的每个平台 binary 重算 SHA256
→ 不生成或搬运 *.manifest.json identity sidecar

Runtime 用户可见过程
→ 可以说明真实工程活动与验证证据
→ 不主动复述内部治理资产、分类、标识、路由和加载明细
```

最终使用者不需要：

- 访问或 clone Agent_Skills 源仓库；
- 为**安装、升级、status/self-test 或 MCP Runtime** 预先安装 Python、pip、venv；
- 外部安装脚本；
- Runtime Kit ZIP；
- 用户级或全局 Runtime 前置安装；
- 维护 `.agents/agent-skills-install.json`；
- 处理 Builder/Release `*.manifest.json` sidecar。

但 Project Payload 会保留正式 Skill 自己需要的运行资产。当前 Coding Core 明确使用 `coding/scripts/coding.py` 和 `coding/scripts/ready_check.py` 完成项目发现、Change 辅助与 Ready Check，因此这两个 Python helper 仍必须随 Skill 安装。目标项目/宿主没有可用 Python 时，Coding 只能按对应规则使用明确 manual fallback；无法执行的机器门禁必须记为未验证，不能用 onefile Runtime 的存在冒充已执行。

### 非目标

- 不把 Markdown Skill 改写成 Policy DSL、布尔规则数据库或另一套 prompt 系统；
- 不维护 `SKILL.runtime.md` 或其他人工 Runtime Core 镜像；
- 不让 Runtime 自己成为第二个 Coding Agent；
- 不自动扫描整个目标项目替 Agent 判断架构/业务语义；
- 不提供任意路径读取、glob 或批量导出 canonical 规则接口；
- 不把“用户可见不主动披露”宣称成对本机 Owner 的安全隔离；
- 不隐藏目标项目自己的代码、测试、文档、配置、Git/CI 路径或实际修改过程；
- 不承诺抵御机器 Owner、调试器、内存转储、进程 Hook 或专业逆向；
- 不用 Runtime 替代项目 `AGENTS.md`、CI、PR、Review、Migration、安全和授权门禁；
- 不把网页端 Remote MCP / secure tunnel 混进本地 stdio Runtime；
- 不在本规则建立在线许可证、远程 KMS 或自动更新服务；
- 不为了 shared files 自动打包 `.agents/skills/` 根目录下所有文件；
- 不用 SQLite、注册表、隐藏 JSON、改名 manifest 或其他替代 sidecar 保存 installation ownership。

## 3. 动态正式 Skill Catalog

Runtime、Project Payload、install-state、测试和 Release **不得维护固定完整 Skill 名单**。

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

[`.agents/skills/ENTRY.md`](../../ENTRY.md) 是根级普通文件，**不能被识别成正式 Skill**；[`.agents/skills/router/SKILL.md`](../../router/SKILL.md) 必须作为正式 Skill 被动态发现。Router 是所有任务的保留控制面，Coding 只在研发任务命中后负责自己的专业工作。Router 在 Source Mode 可以展示当前 Catalog 供 Agent/维护者导航，但 Catalog 明细不是 Runtime 分发白名单；Runtime MCP 的公共 route contract 不需要把 Catalog 再次暴露给用户可见过程。

Runtime Projection 和 install-state 同样不得维护固定 Skill 或 Reference 身份白名单。新增、删除或改名合法 Reference 后，构建器从当前 Bundle 中实际 `filename`、`source_path` 与 Stable ID 自动更新去身份集合；新增普通 Skill 也自动进入 Project Payload，并由 `build_install_state()` 从同一 Payload 派生 ownership。

## 4. 规则与 Router 事实源

每个正式 Skill 的专业规则事实源：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
```

跨 Skill 的 Catalog、项目事实优先、Source/Runtime 两种取得方式和专业 Skill Handoff 的唯一正文 Owner：

[`.agents/skills/router/SKILL.md`](../../router/SKILL.md)

Router 是正式控制面 Skill，不是专业执行 Skill，也不得复制各 Skill 的完整详细规则；根 `AGENTS.md`、[`.agents/skills/ENTRY.md`](../../ENTRY.md) 与 `AGENTS.managed.md` 只做 Bootstrap，不再拥有第二套完整 Router。

### 源仓库 Mutation 与普通 Runtime 明文面

源仓库 Mutation 的意图识别与 canonical Ownership 由 Agent_Skills **根 `AGENTS.md`** 独立承担，详细 Skill/Reference 内容守恒继续由 ref16 承担。普通 Runtime 安装给目标项目的 Entry、Router Runtime Projection 与 `AGENTS.managed.md` 不复制这套源仓库 Mutation、canonical repository、Maintenance 或跨仓库同步治理。

这不是建立第二个 Router：[`.agents/skills/router/SKILL.md`](../../router/SKILL.md) 仍是唯一 canonical Router Owner；Source Mode 读取其原文，Runtime Mode 只安装由该原文构建的确定性 Runtime Projection。根 `AGENTS.md` 只在 Agent_Skills 源仓库维护场景增加源仓库专用 Bootstrap。Custom Instructions 可以把维护者意图引导到当前根 `AGENTS.md`，但不进入 Project Payload，也不替代当前源码事实。

Builder 读取 canonical References 时：

- 不修改源文件；
- 不标准化换行；
- 不去标题/frontmatter；
- 不摘要；
- Bundle entry `content` 来自原始 UTF-8 bytes 直接 decode；
- SHA256 与 size 对应同一份原始 bytes。

Builder 读取 canonical `SKILL.md` 时也不修改源文件。Source Mode 的人类可读 Reference 链接、文件名和维护导航继续保留在 canonical Core；Runtime Mode 在 Project Payload 边界对 Core 做 deterministic Projection，去除这些 Reference 身份和直接导航，再安装到目标项目。Runtime 日常任务通过已配置的项目级治理 MCP 取得 route contract、提交 Task Route 并加载 required Context，不依赖本地投影 Core 重新猜具体 Reference 文件。

**完整 canonical Context 本身不能为了用户可见保密而删改 routing metadata、Stable ID 或其他原文字节。** Runtime Skill Projection 只作用于 Project Payload 的 Core 明文视图，不作用于 canonical Reference、私有 Routing Manifest 或 MCP `load_required_context` 返回的完整原文，因此不能改变 `source_digest`、`routing_digest`、routing provenance 或逐字守恒。

## 5. Entry、Runtime Skill Projection 与 Router 为什么继续明文

canonical Core `SKILL.md` 负责：

- 让支持 Skill/Rules/AGENTS 的宿主进入本 Skill 的正式工作流；
- 保存 Skill 的完整核心工作语义、硬不变量、失败关闭和完成门禁；
- 在 Source Mode 为维护者保留详细 Reference 导航；
- 作为 Runtime Projection 的唯一人工维护输入。

Runtime Skill Projection 负责：

- 保留 frontmatter、Skill routing metadata、核心执行链、失败关闭和完成门禁，让支持原生 Skill/Rules 的宿主仍能进入工作流；
- 把“必须取得当前场景详细约束”的工程语义保留下来；
- 去除具体 Reference 文件名、路径、Stable ID、直接 Markdown 导航和内部编号缩写，不让 Runtime Core 再承担私有 Reference Catalog；
- 由当前 Bundle Reference 身份自动驱动并确定性生成，不建立第二份人工规则源；
- 输出后仍发现当前 canonical Reference 身份或 `references/` 路径时失败关闭。

薄 Entry 与 Router 负责：

- Entry 在 Source Mode 恢复项目事实并无条件进入 Router，在 Runtime Project Payload 中作为同版本 shared runtime asset；
- Router 的 canonical Core 仍是唯一跨 Skill Catalog / Handoff Owner，Runtime 安装的是该 Core 的投影视图；
- Router 不生成项目执行计划、不创建子 Agent、不调用项目实现工具、不接管专业 Skill；
- 固定项目事实优先；
- Source Mode 直接读取 canonical Reference；Runtime Mode 的具体 required Reference 选择由私有 Routing Manifest/evaluator 完成，再通过 Task Route 加载 required Context；
- 把 Coding / Figma / Review / Docs Handoff 放在单一 Owner，而不是复制到两个 AGENTS 入口。

如果 Router/专业 Core 也完全从 Project Payload 删除，只留下 MCP Tool，支持原生 Skill/Rules 的宿主可能失去当前进入工作流所需的运行资产，会增加执行效果和兼容回归风险。因此 Entry、Runtime Router/专业 Skill Projection 与必要运行资产继续作为 Project Payload 明文安装；详细 canonical Reference 正文保留在加密 Bundle 中。

**“继续明文安装投影 Core”与“用户可见过程不主动展示”是两个不同边界。** 目标项目 Owner 仍可查看这些本地投影文件，本方案不宣称物理隐藏；Projection 减少的是 Reference 身份/导航映射明文面，managed block 和 MCP Contract 继续要求 Runtime 日常工作不把内部资产作为用户过程输出。

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

## 8. Project Payload v2：分发 Runtime Core Projection，不分发 Reference/Stub

Project Payload 当前协议仍为：

```text
agent-skills-project-payload/v2
```

它只用于在没有源仓库和 Python 安装脚本的目标项目中重建：

```text
ENTRY.md
+ Router 与每个专业 Skill 的 Runtime SKILL Projection
+ agents / assets / scripts / templates / schemas 等运行资产
```

明确禁止进入 Project Payload：

- canonical `references/*.md`，无论是正文还是 Stub；
- 私有 Routing Manifest；
- canonical `SKILL.md` 的 Reference 身份导航原样副本；
- 任意深度的维护 `README.md`；
- tests、Python cache 和编译产物。

Payload 必须动态发现 Skill，显式记录 `skills`、`shared_files`、文件 path/hash/size/mode 和 `payload_digest`。`ENTRY.md` 当前是唯一 Skills 根级 shared file；Router 通过动态正式 Skill Catalog 进入 Payload，但写入的是 canonical Router Core 的 Runtime Projection，根级任意新文件不会自动进入。

Runtime Projection 必须满足：

1. 输入只来自当前 canonical `SKILL.md` 与同一 Bundle 中当前 Reference 身份，不创建人工第二副本；
2. 保留 frontmatter、`agent-routing:v1` Skill metadata、核心工作语义、硬不变量、失败关闭和完成门禁；
3. 指向 canonical Reference 的 Markdown 链接整体替换为不暴露标题/目标的通用约束语义；裸 `filename`、`source_path`、Stable ID、`references/` 路径和内部 `refN` 编号缩写也必须去除；
4. Reference 身份集合由当前 Bundle 动态生成，不能写固定 Skill/Reference 白名单；
5. 输出确定性；同一 canonical 输入重复构建必须得到相同 Runtime Core bytes 与 `payload_digest`；
6. 输出后重新扫描当前 canonical Reference 身份，任何残留都必须让 Project Payload 构建失败关闭；
7. Projection 只改变 Project Payload Core bytes，因此只体现在 `payload_digest`；不得改写 canonical Reference bytes、`source_digest`、Routing Manifest 或 `routing_digest`。

Project Payload 的 `mode` 必须以 Git index executable bit 为跨平台 canonical 来源：普通文件映射为 `0644`，Git 标记 executable 的文件映射为 `0755`；非 Git 源只按宿主是否存在任一执行位回退到同一组可移植权限。不得直接把 Windows `0666` 或其他宿主 `stat` mode 写入 Payload identity，导致同一 source commit 在三平台得到不同 `payload_digest`。

目标项目因此没有 Agent_Skills 的同名 Reference 文件。Runtime Mode 命中规则时不得尝试打开本地 `references/<file>.md`，也不得寻找或生成 Stub，而是通过当前 Task Route 的路由令牌取得 required canonical Context。目标根 `AGENTS.md` 同时明确禁止把受管源码维护导航当作 Runtime 日常 required Context 入口。

Project Payload 还承担**当前 Runtime install-state 的唯一结构化 ownership 来源**：`build_install_state()` 只从已验证 Payload 派生当前 `skills/shared_files/managed_files/source_digest/payload_digest`。安装器不得在另一份 JSON 中复制一套长期 ownership 状态。

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

新增普通 Skill/Reference 通过 committed metadata 和动态发现进入编译，不修改 Runtime 固定白名单或 Task Route 顶层 schema。Runtime Projection 使用的是同一当前 Bundle Reference 身份集合，只减少 Core 明文导航，不参与或替代 evaluator 求值。

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
- Runtime Core 不再明文列出当前 canonical Reference 文件名、路径、Stable ID 或直接导航映射；
- 普通静态浏览/复制门槛提高；
- 密文篡改由 GCM tag 检测。

模式感知用户可见边界额外提供：

- 正常 Agent 过程输出不需要列出内部 Skill/Reference 文件名和路径；
- MCP envelope 不再主动提供不必要的内部身份字段，降低模型顺手复述的机会；
- 仍允许完整展示代码、测试、文档、Review、Git/CI 和验证等真实工程过程。

不能据此宣称：

- 本机管理员无法提取 key；
- 内存永远没有明文；
- 目标项目 Owner 无法查看已安装的投影 Core/Router；
- 反编译、Hook 或 MCP 通信观测不能取得规则；
- Prompt/managed block 可以成为机密安全边界；
- Runtime Skill Projection 是加密或可信执行环境；
- Runtime 是可信执行环境；
- 旧 Runtime install-state 可以抵御目标项目 Owner 恶意替换本地 `.agents/runtime` binary。

源仓库 canonical 文本的访问控制必须由仓库权限承担。执行 Runtime 安装/升级同样以**用户已经信任并明确选择的目标项目工作区**为前提；无 sidecar ownership 解决的是普通升级状态重复问题，不是恶意工作区代码签名机制。

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

正式 Runtime 不再提供 `agent_skills_manifest` 或接受 `ids` 的任意加载 Tool。**内部 `__install-state --json` 不属于 MCP Tool Contract，也不进入普通 CLI help；它只供下一版安装器从旧已安装 Runtime 取得 previous ownership。** MCP v3 收窄的是返回字段，不是调用顺序、canonical 规则或路由语义。

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

稳定公开入口：

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

`.agents/runtime/` 是本地运行资产，应被目标项目 `.gitignore` 忽略。安装结果不创建 `.agents/agent-skills-install.json`。

## 13. Sidecarless Install State 与逐文件 ownership

当前正常项目安装**没有持久 install manifest schema**。当前 ownership 自描述协议是：

```text
agent-skills-runtime-install-state/v1
```

它不是磁盘 sidecar，也不是 MCP Tool。每个 Runtime 根据自身内嵌且已验证的 Project Payload 确定性派生：

```text
release_version
source_digest / payload_digest
skills
shared_files
managed_files
```

真正决定更新/删除边界的是相对 `.agents/skills` 的逐文件 `managed_files`，不是“整个 Skill 目录归安装器”。

升级 previous ownership 来源只有：

```text
历史合法 agent-skills-install/v3
→ 只作为一次迁移输入
→ 成功升级事务末端删除

否则

旧已安装 .agents/runtime/agent-skills-mcp[.exe]
→ 内部 __install-state --json
→ 返回旧 Runtime 内嵌 Project Payload 对应的 install-state
→ 新安装器严格校验 schema/digest/path/skills/shared_files/managed_files
```

规则：

```text
新 Payload 文件 + 目标不存在
→ 创建并由当前 Runtime install-state 认领

目标文件 + previous managed_files 明确认领
→ 原子升级

previous managed file + 新 Payload 已删除
→ 只删除该受管文件

目标同名文件 + previous ownership 未认领
→ 项目自有/归属不明
→ fail closed，不猜 ownership

同一 Skill 目录内未认领的项目文件/Reference
→ 保留
```

首次安装遇到未认领的同名正式 Skill 目录、`ENTRY.md` 或其他同名 managed file 仍必须在任何写入前失败关闭。不同名项目 Skill、项目自有 `.agents` 内容、AGENTS marker 外文本和其他 MCP server 永不因当前 ownership 更新而清理。

Legacy 兼容只保留 `agent-skills-install/v3` → sidecarless 的一次迁移；v1、v2、未知或损坏 manifest 全部失败关闭。不存在合法 legacy v3 且旧 Runtime 无法返回合法 install-state 时同样失败关闭；不得根据目录、文件名、内容相似或当前 Payload 猜 previous ownership。

该机制以用户已经信任并明确选择升级的目标工作区为前提。读取旧 Runtime install-state 不是对项目 Owner 的防篡改证明，不能宣称为代码签名或安全隔离。

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
- 已存在没有 previous Agent Skills ownership 证据的同名 MCP 时拒绝静默覆盖；
- **Codex 已存在 `[mcp_servers.agent-skills]` 但 managed marker 缺失时，即使 legacy v3 或旧 Runtime install-state 能证明历史安装存在，也必须 fail closed；ownership 不能证明当前 TOML table 仍是可安全替换的原受管块；**
- 已存在 previous ownership 未认领的同名 Skill/shared/managed file 时拒绝静默覆盖；
- marker 损坏、文本编码不可安全增量编辑、受管路径为符号链接时预检失败。

Runtime managed block 还必须明确：正常工程过程可以显示，但内部治理实现细节不作为用户过程输出；Runtime Mode 不根据受管运行资产里的 Source Mode 导航去本地枚举或尝试读取不存在的 Reference。Codex workspace trust 以及 Cursor/Claude 的首次确认属于宿主安全边界，安装器不得绕过。

## 15. 安装原子性与回滚

安装器修改项目研发入口，必须先完整预检，再进入可恢复写入：

1. 验证 Project Payload v2、path/hash/size/mode/shared files/no-reference 边界；
2. 恢复并校验 previous ownership：legacy v3 或旧 Runtime install-state；校验同名冲突、符号链接、AGENTS/host marker 和 JSON/TOML 边界；
3. 对全部新/旧 managed files、Runtime、legacy manifest（如存在）和受管文本保留原始 bytes/权限快照；
4. 每个受管文件使用同目录临时文件 + 原子替换，不移动或替换整棵 Skill 目录；
5. 只删除 previous managed_files 明确认领且新 Payload 已删除的文件；
6. 安装 Runtime 并验证 artifact SHA256；
7. 写入 AGENTS、`.gitignore` 与宿主配置；不写新的 install manifest；
8. legacy v3 迁移成功时，在其他新状态全部完成后才删除旧 manifest；
9. 任一步异常时恢复本轮 touched 文件、Runtime、legacy manifest 与受管文本快照；
10. **任何快照恢复失败都必须聚合到明确的“回滚不完整”错误中，并把原始安装异常保留为 cause；不得用 `except: pass` 静默吞掉回滚失败后只报告最初异常。**

目标路径任一上级是符号链接、目标是特殊文件、legacy manifest 损坏、旧 Runtime install-state 非法或 ownership 不可证明时必须失败关闭。回滚不得使用 `git reset --hard`、`git clean`、强制推送或历史重写。

普通文件系统不是数据库事务；实现必须把所有可预检失败前移，并让故障注入测试证明 Entry/Router 写入失败、Runtime hash 失败、legacy manifest 恢复以及安装失败后 rollback 自身失败时的可恢复/可诊断行为。

## 16. 构建与验证

Builder 固定顺序：

```text
规范化显式 release_version（未传则 0.0.0-dev）与真实 source commit
→ 动态发现 Skill/Reference
→ 解析并校验 committed canonical metadata
→ 编译私有 Routing Manifest / routing_digest
→ 构建 Bundle v2 / source_digest / bundle_version
→ 量化 canonical Router / Skill Core / Reference 聚合 Context footprint
→ canonical Router/Skill Core → deterministic Runtime Skill Projection
→ 构建 no-Stub Project Payload v2 / payload_digest
→ AES-256-GCM 认证加密 Bundle
→ 生成当前平台 onefile
→ artifact status / self-test + 不透明完整性指纹交叉验证
→ 直接返回 Builder JSON identity + artifact SHA256
→ 真实 stdio MCP smoke
```

至少验证：

1. 所有 Skill/Reference metadata 协议、中文字段、Stable ID、依赖、风险下限合法；
2. ID 全局唯一，依赖无环、无悬空项，文件 rename 不静默改变显式 ID；
3. canonical Reference 原始 bytes、SHA256、size 和 `source_digest` 在 build/encrypt/decrypt 后逐字一致；
4. Routing Manifest 稳定序列化、`routing_digest` 和同一 Task Route 求值在编译/加密 roundtrip 前后一致；
5. Source Mode canonical `SKILL.md` 保持完整 Reference 导航；Project Payload 动态包含 Router/全部 Skill 的 Runtime Projection 与运行资产，Projection 不含当前 canonical Reference filename/source_path/Stable ID、`references/` 路径、直接导航或内部 `refN` 缩写，同时保留 frontmatter、Skill routing metadata、核心语义、失败关闭和完成门禁；新增 Skill/Reference 无需扩固定白名单；
6. 同一 canonical 输入重复构建得到相同 Runtime Projection bytes 与 `payload_digest`，投影后仍残留当前 canonical Reference 身份时构建失败关闭；
7. `status` 不公开 Skill Catalog、Reference count/ID/filename/path/loaded IDs 或内部 digest；`self-test` 只额外公开不可逆整体完整性指纹；Builder 的 `context_budget` 只允许输出 Router、各 Skill Core、各 Skill Reference 总字节和 Router+Core 聚合值，不得列单个 Reference 身份；
8. 真实 MCP `tools/list` 恰为六个 Tool，中文 property 可调用，Runtime 公共 envelope 不泄露内部身份，route→submit→load exact-text→checkpoint 成功；
9. `load_required_context` 每项公开 envelope 只含 `完整原文`，且原文与 canonical source 逐字一致；
10. 同一 task 多次 route 只能单调扩展，旧 token/任意 ID load/未知词汇失败关闭，未知事实保守扩大；
11. 首次安装、无参数安装、显式 target、无 sidecar 重复安装/升级、legacy v3 一次迁移、v1/v2/未知 schema 拒绝、项目自有 Reference 保留、同名冲突、符号链接、Codex marker 丢失 fail-closed 和 rollback/rollback-failure reporting；
12. Source Mode 根入口继续可见唯一 Router；Runtime 安装后的根 `AGENTS.md` 不主动暴露 `.agents/skills/`、Router/Reference 名称、Stable ID 或内部路由细节，同时保留代码、测试、文档、复核、Git/CI 等工程进度语义；
13. Builder JSON 必须包含 `release_version`、`python_version`、`source_commit`、Bundle/Task Route/Routing Manifest/MCP/Project Payload 协议、三个 digest、不可逆完整性指纹和真实 `artifact_sha256`；Builder 输出目录不得生成 `*.manifest.json`；
14. 三平台 Runtime Package Tests 必须重新计算实际 artifact SHA，验证 Builder 输出，完成 onefile status/self-test、真实 stdio MCP、首次安装、重复安装和目标项目无 install manifest；
15. Release 三个平台必须通过 job outputs 传递公共 identity；Release job 对公共 identity 逐字段一致性比较，并对下载后的 Linux/Windows/macOS binary 分别重新计算 SHA256 与各平台 Builder 输出比对。

Routing Conformance Benchmark 必须永久覆盖 Greenfield、Fact Recovery、L1/L2/L3、Feature/Bug/Incident/Refactor/Performance/Schema、Frontend/Figma/Docs/Review、多 Agent/多 Change、Dependency/CI/Git/PR/Release、Runtime/Project Payload/Skill Mutation/Security、unknown 和复杂组合。最低门禁是 `Expected Required ⊆ Actual Required`；每次修改 trigger/依赖/风险下限都同步审查正例、必要反例和 ambiguous case，并力求 `Expected == Actual`。Runtime Projection 不参与 trigger/依赖/风险求值；如果 Projection 变更导致 Routing Conformance 结果变化，应视为实现错误而不是接受新的路由语义。

正式平台构建的 Python 版本必须由永久 CI/Release workflow 显式固定；不能使用 Linux/Windows/macOS Runner 各自随机漂移的预装 Python 冒充同一构建环境。不同平台的 onefile 必须在 Linux、Windows、macOS 对应 Runner 构建、启动、MCP smoke 和 project install，不能把一个平台的产物当跨平台证据。

## 17. Release Identity 与正式资产

Builder **不生成 artifact identity manifest sidecar**。维护侧 Release identity 直接由 `scripts/build_runtime.py --json` 返回，至少包含：

```text
release_version / source_commit
artifact / artifact_sha256 / python_version
integrity_fingerprint
Bundle/Task Route/Routing Manifest/MCP Tool/Project Payload protocol
bundle_version / source_digest / routing_digest / payload_digest
Skill 集合与聚合 context_budget
```

这些维护侧 identity 字段不等于 Runtime MCP 公共状态。Runtime `status --json` 只公开 Release 版本和最小任务状态；`self-test --json` 只额外公开通过状态和不可逆整体完整性指纹。不得通过 Runtime 公共 Tool 枚举 Reference ID、文件名、路径、数量、trigger mapping、依赖图或 canonical 原文 Catalog。

Builder 可以在维护者构建结果中返回聚合 `context_budget`，但该信息不进入 Runtime `status/self-test` 的 Reference 明细面。

正式 GitHub build 必须满足 `source_commit == GITHUB_SHA == 当前 checkout HEAD`；不一致、伪造或无法解析时失败。非 Git 本地源码允许明确为 `null`，不能编造 commit。

仓库不维护独立根版本文件。**正式 Release 的唯一版本来源是 `.github/workflows/release.yml` 手工输入的 `v<SemVer>` tag；workflow 去掉前缀 `v` 得到 `release_version`，并把同一个值显式传给三个平台 Builder。**普通本地、PR 和 main 常规构建没有正式 tag 时使用 `0.0.0-dev` development identity，不得冒充已发布版本。

正式 GitHub Release 最终精确发布三个版本 ZIP：

```text
agent-skills-v<SemVer>-linux.zip
├── agent-skills-mcp-v<SemVer>-linux
└── USAGE.md

agent-skills-v<SemVer>-windows.zip
├── agent-skills-mcp-v<SemVer>-windows.exe
└── USAGE.md

agent-skills-v<SemVer>-macos.zip
├── agent-skills-mcp-v<SemVer>-macos
└── USAGE.md
```

每个 ZIP 根目录的成员集合必须精确为当前平台 Runtime binary 与同一版本 [`USAGE.md`](../../../../USAGE.md) 两项。源包、Python 安装器、Runtime Kit、私有 Routing Manifest、公开 Reference Catalog、临时文件、其他平台 binary、Builder JSON 缓存或其他维护资产都不得进入任一 ZIP，也不得作为独立正式 Release asset 暴露。

三平台 Builder 通过 GitHub job outputs 向发布 job 传递公共 identity 与各自 `artifact_sha256`。发布 job 必须先比较三平台的 `release_version/source_commit/python_version/integrity_fingerprint`、Bundle/Task Route/Routing Manifest/MCP/Project Payload 协议、bundle/source/routing/payload identity 完全一致；`artifact_sha256` 因平台 binary 不同**不参与公共 identity 相等比较**，而是分别绑定 Linux、Windows、macOS 对应 artifact。下载 artifact 后必须重新计算每个平台 binary SHA256，并与对应平台 job output 比对。任一公共 identity 漂移、任一平台 SHA 不一致或出现 `*.manifest.json` sidecar 都必须失败关闭。

随后使用显式成员白名单分别组装三个平台 ZIP，每个 ZIP 只加入当前平台 binary 与 [`USAGE.md`](../../../../USAGE.md)，并逐一重新打开核对精确成员集合，不能通过 `release-assets/*` 等宽泛通配把临时文件、其他平台 binary 或维护资产带入最终包。

Release workflow 必须从 main 构建，在正式构建前校验 tag 不存在、Release 不存在，再在目标 main SHA 上重新运行完整 self-contained tests 与 Ready Check。workflow 不依赖自定义 PAT/Actions Secret，也不读取或要求仓库 Release Immutability 设置；tag/Release 操作使用 GitHub Actions 自动提供的 `github.token`，发布 job 只申请最小 `contents: write` 权限。三平台继续使用同一固定 Python 版本，且 identity 必须满足 `source_commit == GITHUB_SHA`、`release_version == tag 去 v 后值`、协议/digest/integrity 一致以及各自 artifact SHA256 正确。

正式资产完成交叉校验和三个 ZIP 成员核对后，workflow 必须先创建 **Draft Release**，并且只上传 `agent-skills-v<SemVer>-linux.zip`、`agent-skills-v<SemVer>-windows.zip`、`agent-skills-v<SemVer>-macos.zip` 三个资产；Draft Release 资产集合必须精确等于这三个平台 ZIP，不能同时上传独立 binary、说明文件、checksum 或 identity sidecar。核对 Draft 通过后才 Publish；发布后再核对 tag 指向当前 `GITHUB_SHA`，且已发布资产集合仍精确只有这三个平台 ZIP。Release 页面正文可以继续使用源码仓库同版本 [`USAGE.md`](../../../../USAGE.md) 作为 notes，但最终分发文件以各平台 ZIP 内说明为准。正式发布不使用 Release Immutability，有仓库管理权限的维护者仍可修改或删除已发布资产；workflow 拒绝覆盖已有 tag/Release，但不能把这项流程保护描述成不可变存储。Draft 上传不完整、identity 不一致、任一平台 ZIP 成员不一致或发布后 tag/资产不可验证时必须失败关闭。

版本语义分为两种：网页端读取当前 main、Runtime 使用当前最新 Release 时追求“最新规则”，但发布间隙允许短暂版本差；需要严格复现正式 Runtime 时，使用 Runtime `status --json` 的 `Release版本` 定位对应正式 Release/tag，再读取该 tag/commit 的 Source Mode 规则。development `0.0.0-dev` 的精确构建 identity 由本次 Builder JSON/CI 证据记录，不再依赖磁盘 identity manifest。

AES-GCM、onefile 和 Runtime Skill Projection 共同减少普通明文浏览面并检测静态篡改，但它们不是 TEE/KMS，也不能抵御机器 Owner、调试器、内存转储、Hook、MCP 通信观测或专业逆向。canonical 源码访问仍由仓库/制品渠道权限控制；如果源仓库是 Public，则 canonical Skill/Reference 本身就是公开内容，Runtime 加密/投影不能反向把公开源码变成保密事实。Runtime 的用户可见 disclosure rule 同样不是安全隔离承诺。

## 18. 升级

升级必须使用同一 Release 的 binary；Payload 与 identity 已嵌入该 binary，不能跨版本拆换：

```text
校验当前平台 artifact / SHA256
→ 校验 Bundle v2 / Project Payload v2 / routing identity
→ 恢复 previous ownership
   ├─ legacy v3 manifest：严格校验，一次迁移
   └─ 旧已安装 Runtime：内部 install-state
→ 预检 previous managed_files / 项目自有内容 / host config
→ 逐文件原子升级 Runtime + Runtime Router/Skill Projection + managed 配置
→ legacy v3 成功迁移则删除旧 manifest
→ 不写新的 ownership sidecar
→ status / self-test / MCP / install smoke
```

Reference bytes 变化只通过新 Bundle 与 `source_digest` 体现；route metadata/依赖/风险变化通过 `routing_digest` 体现；canonical Core/Router 或其他运行资产变化会使 Runtime Projection/Project Payload bytes 变化，并通过 `payload_digest` 体现。三者不能互相代替。

legacy v1/v2/未知 schema、Bundle v1、旧 MCP Contract 或损坏状态不静默兼容。需要跨其他不兼容 Contract 迁移时必须建立独立 Change，给出明确迁移/回滚与验证，不保留无限期双路径。

## 19. 回滚

安装过程内失败由 sidecarless Installer 快照恢复；若本轮从 legacy v3 迁移，旧 manifest 也是必须恢复的快照之一。用户手工回退必须取得目标版本的完整同平台资产并重新运行该版本正式安装流程，不能只替换 Runtime 或投影 Router/Skill Core。

如果安装过程自身失败且任何快照恢复失败，安装器必须明确报告“回滚不完整”及未恢复路径/原因，并保留最初安装异常作为根因链；不得因 rollback exception 被吞掉而让维护者误判项目已经恢复。

如果目标版本不理解当前 ownership/install-state，应停止并按该版本正式迁移说明处理。不得手工删除归属不明的 `.agents` 内容，不得用 Git destructive 命令冒充安装回滚。

## 20. 正常任务生命周期

### Source Mode

```text
目标项目 AGENTS / 真实事实
→ Agent_Skills 根 AGENTS / ROUTER
→ 读取命中 canonical Skill Core
→ 用 canonical metadata 的同一语义确定 Required References
→ 直接读取 Agent_Skills 源仓库中这些 Reference 的当前完整原文
→ Coding / Review / Docs / Figma Handoff
→ 真实验证与交付门禁
```

Source Mode 是明文维护/直读模式；在用户已经有源码访问权时，可以正常显示正在读取哪个 Skill/Reference、具体路径、路由判断和维护过程，不应用 Runtime Mode 的用户可见隐藏策略伪装源码事实。**目标项目旧版本 Agent_Skills 安装资产不能作为 Source Mode 当前通用治理规则来源；项目自己的规则和真实事实仍必须读取。安装版本漂移只报告正式 Runtime upgrade 需要。**

### Runtime Mode

```text
目标项目 AGENTS managed block / 当前项目真实事实
→ 受管 Runtime Router/专业 Skill Projection 提供宿主原生 Core 工作语义
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

目标项目中的 Router/专业 Skill 以当前 Release 的 Runtime Projection 作为受管内部运行资产存在；这些投影保留 Core 执行语义，但不保留 Source Mode 的具体 Reference 文件名、路径、Stable ID 和直接导航。Runtime Mode 不尝试打开目标项目不存在的同名 Reference，具体 required Context 始终由同一 canonical metadata 编译出的私有 Routing Manifest/evaluator 决定。

两种模式共享同一 canonical `SKILL.md + references/*.md`、Stable ID、路由 metadata、依赖、风险下限和版本身份；Runtime Projection 只是 Project Payload 的派生明文视图，不是第二个规则事实源。两种模式只改变 Core 的呈现/安装视图、Context 的取得通路和用户可见披露层，不能改变 required Context 求值结果。任何必需 Context 无法取得、digest/协议不一致或路由含未公开值时，明确报告并停止依赖该规则的动作。

Runtime Mode 对用户可以继续说明：检查了哪些**目标项目**代码/配置/测试、准备补什么测试、修改了什么业务文件、是否同步文档、运行了什么验证、Review/CI/Git 状态如何；但不要把内部 Skill/Reference 文件、Stable ID、route token、命中集合或 Context 加载计数作为过程播报。需要解释“为什么补测试/同步文档/做 Review”时，直接说明工程风险和影响，不说“因为命中了某内部规则”。

授权信号不产生权限；checkpoint 不产生完成事实；Runtime 不执行 Git/PR/Release/部署/数据库副作用。

## 21. ChatGPT 网页端边界

当前 Runtime 是项目本地 stdio MCP。纯网页端 ChatGPT 不能直接启动用户电脑上的 `agent-skills-mcp`，也不能因为 GitHub 中存在 Runtime 源码就把本地 MCP 当作已经连接。

网页端如果通过 GitHub 获得 Agent_Skills 源仓库读取权限，使用 Source Mode：先读取目标项目事实与 Agent_Skills 根 AGENTS.md，再按 Router 和 canonical metadata 直接读取 required References。该路径不调用本地六个 MCP Tool；目标项目安装资产只作安装状态事实，不能替代当前 canonical Source。Source Mode 可以正常显示明文 Skill/Reference 和源码导航过程。

网页端如需调用目标机器 Runtime，必须使用受支持的 Remote MCP、安全隧道或等价远程部署；这是另一部署形态，不属于当前本地 stdio Runtime，不得为实现它绕过宿主、网络或权限边界。
