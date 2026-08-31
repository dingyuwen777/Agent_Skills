# Runtime 源码维护说明

`runtime/` 实现 Agent_Skills 当前唯一正式对外分发形态：**项目级 onefile Runtime + Shared Entry + Native Router/专业 Runtime Skill Projection + Encrypted Canonical References + local stdio MCP**。

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

agent_skills_runtime/runtime_skill_projection.py
→ 从唯一 canonical SKILL.md 自动生成 Runtime Core 视图，去除 Reference 文件名、路径、Stable ID 和直接导航映射；残留身份时 fail closed

agent_skills_runtime/project_payload.py
→ 构建 Skills 根级共享运行资产、各 Skill Runtime Projection 与其他运行资产；显式禁止 Reference/Stub

agent_skills_runtime/project_installer.py
→ install v3 逐文件 ownership、宿主配置与回滚；非 v3 manifest 直接拒绝

agent_skills_runtime/runtime.py
→ 维护 task/route token、单调 required Context、渐进式披露、用户可见进度边界与 checkpoint

agent_skills_runtime/server.py
→ CLI + stdio MCP Server
```

Runtime 不负责重新解释专业 Skill 规则；跨 Skill 发现与 Handoff 由 [`.agents/skills/router/SKILL.md`](../.agents/skills/router/SKILL.md) 唯一负责，各 Skill 完整专业语义仍由自己的 canonical `SKILL.md` 和 canonical `references/*.md` 定义。[`.agents/skills/ENTRY.md`](../.agents/skills/ENTRY.md) 只做无条件进入 Router 的共享薄 Bootstrap。

这里需要区分**规则事实源**与**Runtime 明文视图**：Source Mode 直接使用源码仓库时，维护者先读 Entry，再显式读取 Router、Skill、Reference、路径和路由过程；Runtime Mode 仍安装 Entry 与动态发现的 Router/专业 Skill Core 以维持宿主原生发现和 ownership，但这些 `SKILL.md` 不是第二份人工规则，而是构建时从同一 canonical Core 自动生成的 deterministic Runtime Projection。Projection 只去除 Reference 身份和导航映射，不参与 canonical Routing Manifest 编译，也不改 required Context 原文。Runtime 日常任务统一通过项目级 MCP 取得所需完整规则正文。

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
shared_files（当前 ENTRY.md）
+ canonical SKILL.md → deterministic Runtime Skill Projection
+ assets / scripts / metadata
→ path / sha256 / size / mode
→ payload_digest
```

`source_digest`、`routing_digest` 和 `payload_digest` 证明不同事实，不能互相替代。`shared_files` 是显式 Contract，不代表 Skills 根目录任意文件都会自动进入 Payload。Runtime Skill Projection 改变的是 Project Payload 中受管 Core bytes，因此只应体现在 `payload_digest`；不能反向改变 canonical Reference 的 `source_digest` 或 Routing Manifest 的 `routing_digest`。

Project Payload 的 `mode` 以 Git index 的 executable bit 为 canonical 来源：普通文件固定为 `0644`，Git 标记 executable 的文件固定为 `0755`；非 Git 源仅按宿主是否具有任一执行位回退到同一组可移植权限。不能直接把 Windows `0666` 或其他宿主 `stat` mode 写进 `payload_digest`，否则同一 commit 会产生跨平台 identity 漂移。

Project Payload 明确排除：

- canonical `references/*.md` 和 Runtime Stub；
- private Routing Manifest；
- 任意深度的维护 `README.md`；
- tests；
- Python cache/编译产物。

Runtime Skill Projection 必须由当前 Bundle 中实际 canonical Reference 的 `filename` / `source_path` / Stable ID 动态驱动，不维护固定 Skill/Reference 白名单，也不要求新增、删除或改名 Reference 时同步第二份 Runtime 文件。构建会整体去除指向 canonical Reference 的 Markdown 导航，再处理裸身份和内部编号缩写；最终扫描仍发现当前 canonical Reference 身份或 `references/` 路径时直接失败关闭。维护者始终只改 canonical `SKILL.md`，不能新增 `SKILL.runtime.md` 等人工镜像。

因此像 [`coding/scripts/tzdata/README.md`](../.agents/skills/coding/scripts/tzdata/README.md) 这种源码维护说明可以留在私有源仓库，但不会安装到目标项目；真正运行需要的 `coding/scripts/tzdata/zoneinfo/Asia/Shanghai` 和共享 [`.agents/skills/ENTRY.md`](../.agents/skills/ENTRY.md) 会原样进入 Payload，动态发现的 [`.agents/skills/router/SKILL.md`](../.agents/skills/router/SKILL.md) 与其他正式 Skill Core 则以 Runtime Projection 进入 Payload。

目标项目没有 Agent_Skills `references/`。Source Mode 直接读取源仓库 required References；Runtime Mode 通过中文 Task Route 和当前不透明 route token 取得 required 完整原文。完整原文继续逐字保留 canonical routing metadata；Runtime 的保密边界不能通过删改 Reference 原文实现，否则会破坏 source/routing 完整性。

## 3. 项目安装边界

onefile binary 无参数运行默认安装/升级当前目录；也支持：

```text
agent-skills-mcp install --target <project-root>
```

当前 Project Payload 使用 v2，install manifest 使用 v3 `managed_files` 逐文件 Contract。安装器只接受当前 v3 manifest；v1、v2、未知或损坏 schema 全部失败关闭，不扫描旧 Stub，也不根据旧目录结构推断 ownership。本迁移不承诺旧安装版本升级；只验证全新安装、重复安装和当前 v3 ownership 更新。

项目安装需要保持：

- `.agents/agent-skills-install.json` 用 `managed_files` 认领 Agent_Skills 可证明的具体文件，并另列公开 Skill/`shared_files`；
- 首次同名未认领 Skill 或 shared file 均 fail closed；
- 新 Release 删除文件时只删除旧 v3 `managed_files` 明确认领项，不替换整棵 Skill 目录；
- `.agents/runtime/` 为项目本地运行资产并加入 `.gitignore`；
- `AGENTS.md` / CLAUDE / Codex 使用 managed marker；
- 目标项目 `AGENTS.md` managed block 只做 Runtime 薄 Bootstrap：先恢复项目真实事实，再通过已配置的项目级治理 MCP 获取本次任务所需完整约束；不得把受管源码维护导航当作 Runtime 日常读取入口；
- Runtime 用户可见过程可以正常描述项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git/CI 和交付状态；不得主动复述内部治理分类、文件名、目录路径、规则标识、路由映射、内部凭据或加载明细；
- Cursor/Claude JSON 只认领 `mcpServers.agent-skills`；
- marker 外项目文本、其他 MCP server、项目自有 Skill/Reference/资产和未认领 shared file 保留；
- Codex 同名 MCP table 存在但 managed marker 缺失，或合法 managed block 外另有重复同名 table 时，即使 install manifest 仍存在也 fail closed，不猜测 table ownership；
- 任一可预检错误先于写入发现；失败按 bytes/权限快照恢复 touched managed files、Runtime、manifest 与受管文本；
- 如果回滚本身有任何失败，必须同时报告原始安装异常与未恢复路径/原因，不能静默吞掉 rollback failure。

正式 Router 与其他 Skill Core 仍通过动态 Catalog 分发，但写入目标项目的是各自 canonical Core 的确定性 Runtime Projection；Skills 根级 Entry 只通过 Project Payload 的显式 `shared_files` Contract 分发，二者职责不混淆。内部 Entry/Router/Core 存在于目标项目并不意味着它们必须成为用户可见的日常导航；安装 ownership 与用户披露是两个独立边界。

### 宿主连接级生命周期

项目安装写入的 Codex、Cursor、Claude Code MCP 配置都是 `stdio`，命令参数为 `serve`。这意味着 Runtime 是由当前宿主启动并通过标准输入/输出保持连接的**前台子进程**，采用**宿主连接级生命周期**，不是系统常驻服务：

```text
宿主打开项目 / 建立 MCP 连接
→ 启动项目 Runtime `serve`
→ stdio 连接期间保持进程
→ 可在同一连接内复用 task、route token 与已加载 Context
→ 宿主关闭/重载项目或断开 stdio/stdin
→ Runtime 进程退出
```

因此一个 Tool 调用或一次模型回复结束后，Codex 等宿主仍可能继续保持 Runtime 进程，这是正常的连接复用；**不应为了“用完即关”把每个 MCP Tool 调用改成一次独立进程**，否则会丢失当前任务的进程内渐进状态并反复完成 MCP 初始化。

Runtime 不自行 fork/detach，不注册 Windows Service，也不创建 systemd、launchd 或其他 daemon/自动启动项。若宿主已经完全退出或明确断开项目 MCP，而 `serve` 进程仍长期存在，应按 orphan process 缺陷调查，而不能把这种状态当成设计目标。

## 4. MCP Contract

稳定工具名称保持：

```text
agent_skills_status
agent_skills_route_contract
agent_skills_start_task
agent_skills_submit_route
agent_skills_load_required_context
agent_skills_checkpoint
```

当前 MCP Tool Contract 为 v3，公共路由 Contract 为 v2。工具调用顺序保持兼容，但公共返回面收窄为完成宿主协作所需的最少信息：

- `status` 只返回 Release 版本、当前任务/约束是否建立和是否加载完成，以及用户可见进度边界；不公开 Skill Catalog、Reference 身份、source/routing/payload digest 或内部计数；
- `route_contract` 继续提供宿主构造中文 Task Route 所需的维度/词汇，但不公开 Skill Catalog 或 Reference mapping；
- `submit_route` 仍由唯一 evaluator 在 Runtime 内部计算并单调扩展 required Context，但只返回不透明 route token、是否还需加载约束和是否仍存在未确认任务事实，不公开命中 Skill、Reference 数量或内部风险结果；
- `load_required_context` 只接受当前 route token，默认只返回尚未加载的 required 完整原文；每个公开 context envelope 只含 `完整原文`，不附带 Stable ID、Skill、文件名、路径、SHA256 或字节数；
- `checkpoint` 只返回当前阶段和是否通过，不公开 required/loaded 集合详情。

这些变化只收窄**公共 envelope**，不改变加密 Bundle 内部 provenance、hash/size、依赖图、风险下限、路由求值或 canonical 原文。`checkpoint` 仍不能替代 Requirement Traceability、Completion Audit、Review、Docs Impact 或真实测试。Task Route 的授权字段只是数据，不能产生 Git、发布或部署权限。

Runtime 给宿主的每个关键返回都携带同一用户可见进度规则：允许说明真实工程活动及其原因；不得把 MCP 内部调用、治理资产身份、分类、路由和加载明细作为用户可见过程复述。这里是输出层约束，不是禁止模型执行这些治理步骤。

## 5. 本地构建

安装维护者构建依赖：

```bash
python -m pip install -r runtime/requirements-build.txt
```

构建当前平台 development onefile：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

未传 `--release-version` 时，Builder 使用 `0.0.0-dev` 作为明确的 development identity；该值用于手工开发构建和 Runtime package CI，不代表任何正式 Release。纯 Skill/Reference/治理变化的常规 CI 不需要为了验证规则正文而调用 PyInstaller。

正式 Release 不读取仓库根版本文件。`.github/workflows/release.yml` 从用户输入的 `v<SemVer>` tag 派生无 `v` 的 `release_version`，然后三平台统一显式调用：

```text
scripts/build_runtime.py ... --release-version <SemVer>
```

构建器读取显式版本和真实 source commit，动态发现 Skill/Reference，编译 canonical metadata，构建/加密 Bundle v2，并从同一 canonical Skill Core 自动生成 no-Stub Project Payload 中的 Runtime Projection，再生成当前平台 artifact 并执行 `status` / `self-test` 校验。由于公共 `status/self-test` 不再暴露详细内部摘要，Builder 会在维护侧用同一份 Bundle、Payload、release/source 身份计算一个不可逆整体完整性指纹，并要求 artifact `self-test` 返回完全一致的指纹；这样仍能证明 artifact 与当前构建材料一致，同时不把内部身份字段重新开放给 Runtime 日常调用。

构建目录中的 `.manifest.json` 是 CI 校验用 Release identity，仍可记录维护侧详细摘要和 Catalog，用于 Release 交叉验证；它不作为正式 GitHub Release 资产发布，也不属于 Runtime MCP 公共披露面。

Builder 的维护者 JSON 输出还包含聚合 `context_budget`：

```text
entry_bytes
router_bytes
skill_core_bytes
reference_bytes_by_skill
base_router_plus_core_bytes
```

它只量化 Entry / Runtime Router Projection / 专业 Runtime Skill Projection / canonical Reference 的聚合字节成本，不列出单个 Reference ID、文件名、路径或触发映射，也不改变 Runtime `status/self-test` 的公开披露合同。为保持现有构建报告消费者兼容，`router_bytes` 与 `base_router_plus_core_bytes` 字段名保留；新增 `entry_bytes` 单独记录薄入口成本。

“最新规则模式”允许网页端 Source Mode 读取当前 `main`、本地 Runtime 使用当前最新 Release，但二者在发布间隙可能短暂不同步；“精确复现模式”应以 Runtime 的 `Release版本` 定位对应正式 Release/tag，再从该 tag 的源码事实复现同一版本，而不是依赖 Runtime 日常状态接口导出源仓库内部 identity。

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
python scripts/runtime_mcp_smoke.py --artifact dist/agent-skills-mcp --json
```

该 smoke 使用真实 stdio MCP client 验证六个 Tool、中文 input schema、去标识化公共 envelope、route contract、submit、required Context exact-text 和 checkpoint，不用内部 Python 函数调用冒充 MCP 边界。hash/size/source/routing 等完整性仍在维护侧 Bundle/Builder 验证，不要求通过公共 context envelope 暴露。

## 7. 永久 CI

永久 CI 按证明责任拆分，不再让每次纯 Skill/Reference/治理变化都重复构建三平台 binary。

### Skill Tests

`.github/workflows/skill-tests.yml` 使用 Python `3.14.7`，安装 Runtime 的运行依赖而不是 PyInstaller 构建依赖，并持续验证：

- self-contained unit/preservation/portability tests；
- Source Mode 唯一 Skills 根级 Router 与 Maintenance 职责、Runtime 薄 Bootstrap 可见性边界，以及 Project Payload shared-file 分发；
- metadata compiler/evaluator、Routing Conformance、private manifest/encryption parity；
- Runtime Projection 不暴露当前 canonical Reference 文件名、路径、Stable ID 或直接导航映射，同时保留 frontmatter、路由 metadata、核心工程语义并由动态 Reference 身份自动驱动；
- Runtime 公共返回面不暴露内部治理身份，同时 required canonical Context exact-text 不被删改；
- install v3 ownership、非 v3 schema 拒绝、项目自有 Reference 保留、同名冲突、Codex marker/重复 table fail-closed 和失败/回滚诊断；
- 动态 Skill Bundle + Project Payload 的源码级构建、投影确定性与内容守恒；
- Active/changed Change Ready Check。

这条 Workflow 不运行 PyInstaller，不构建 onefile，也不创建 Windows/macOS package job。规则正文会进入下一次正式 Runtime，但它的内容、路由、Bundle/Payload 和治理正确性由上述源码级自动化证明。

### Runtime Package Tests

`.github/workflows/runtime-package-tests.yml` 只在 Runtime/Builder/MCP 安装/Release 工作流相关路径变化时触发，并使用 Linux、Windows、macOS 对应 Runner 真实验证：

- onefile build/status/self-test；
- development `release_version=0.0.0-dev` 与固定 Python identity；
- real stdio MCP；
- project-only single-binary 首次安装、升级和无参数安装；
- 项目内 Runtime status/MCP smoke；
- Windows/macOS 对应平台 package/install。

不同平台必须使用对应 Runner，不能把一个平台的 PyInstaller artifact 当跨平台二进制。Skill Tests 的绿色不能替代这一层；反过来，Runtime package 绿色也不能替代规则/内容守恒/Ready 的广覆盖测试。

## 8. 正式 Release

正式 Release 由根 `.github/workflows/release.yml` 从 `main` 手工构建。输入 `v<SemVer>` tag 后，workflow 将同一 `release_version` 显式传入 Linux/Windows/macOS Builder；Release preflight 会重新运行完整 self-contained tests 与 Ready Check。

所有三平台 artifact / identity 完成验证后，workflow 逐一校验协议、digest 和 `artifact_sha256`，并删除平台特有的 `artifact` / `artifact_sha256` 字段后比较其余公共 identity；三平台任一 source/routing/bundle/payload/protocol/Skill identity 漂移都会在发布前失败关闭。校验通过后分别从白名单成员组装并回读验证三个最终分发 ZIP：`agent-skills-v<SemVer>-linux.zip`、`agent-skills-v<SemVer>-windows.zip`、`agent-skills-v<SemVer>-macos.zip`。每个 ZIP 根目录只包含当前平台 Runtime binary 与同一版本 [`USAGE.md`](../USAGE.md)，Draft 与正式 Release 都必须精确只有这三个平台 ZIP 资产；构建期 identity manifest 不进入最终 ZIP 或正式 Release。

最终用户资产和使用方式以根 [`USAGE.md`](../USAGE.md) 为准。本文件不维护第二份最终用户教程，也不记录 Change/PR/Release 历史流水账。

## 9. 安全边界

onefile + AES-GCM 的目标是减少目标项目中的普通明文浏览/复制面，并检测 Bundle 篡改；它不是 TEE/KMS。Runtime Skill Projection 进一步缩小安装后的普通明文面，但它只隐藏 canonical Reference 的身份/导航映射，不是加密层，也不能替代 Reference Bundle 的完整性与访问边界。

模式感知披露只能减少正常 Agent 对话中主动复述内部治理结构的概率和产品表面，不等于阻止拥有机器控制权的用户查看受管明文 Runtime Core/Router、MCP 通信或进程内解密后的完整规则。不能宣称能够抵御机器 Owner、调试器、内存转储、进程 Hook、MCP 通信观测或专业逆向。真正限制谁能读取 canonical 源文件，必须依赖源仓库访问控制。
