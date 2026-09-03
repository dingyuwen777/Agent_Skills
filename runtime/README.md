# Runtime 源码维护说明

`runtime/` 实现 Agent_Skills 当前唯一正式对外分发形态：**项目级 onefile Runtime + Shared Entry + Native Router/专业 Runtime Skill Projection + Encrypted Canonical References + local stdio MCP**。

最终使用者不需要阅读本文件；下载、安装、升级、回滚和排障见根 [`USAGE.md`](../USAGE.md)。

## 1. 模块职责

```text
agent_skills_runtime/skill_catalog.py
→ 动态发现 .agents/skills/*/SKILL.md 下的正式 Skill

agent_skills_runtime/catalog.py
→ 收集 canonical References，并构建 Bundle v3 的逻辑 canonical identity / source_digest / bundle identity

agent_skills_runtime/routing.py
→ 从 canonical Markdown 编译/校验私有 Routing Manifest，生成公共 route contract，并用唯一 evaluator 求值；事实充分时保持原二值语义，未知事实使用三值保守求值

agent_skills_runtime/crypto.py
→ 使用 HKDF-SHA256 派生用途隔离密钥，并提供 AES-256-GCM authenticated encryption

agent_skills_runtime/encrypted_bundle.py
→ 把逻辑 Bundle 构建为 encrypted private manifest + per-reference authenticated records；Runtime 启动只恢复私有索引，正文按 required Context lazy decrypt

agent_skills_runtime/runtime_skill_projection.py
→ 从唯一 canonical SKILL.md 自动生成 Runtime Core 视图，去除 Reference 文件名、路径、Stable ID 和直接导航映射；残留身份时 fail closed

agent_skills_runtime/project_payload.py
→ 构建 Skills 根级共享运行资产、各 Skill Runtime Projection 与其他运行资产；显式禁止 Reference/Stub

agent_skills_runtime/install_state.py
→ 从已验证 Project Payload 确定性派生 Runtime 内嵌 installation ownership；严格校验 legacy v3 migration 与安全 managed path

agent_skills_runtime/project_installer.py
→ 无 sidecar 项目安装/升级、previous ownership、宿主配置与回滚；legacy v3 仅作为一次迁移输入

agent_skills_runtime/runtime.py
→ 维护 task-bound route capability、单调 required Context、按需原文加载、用户可见进度/防披露边界与 checkpoint

agent_skills_runtime/server.py
→ CLI + stdio MCP Server；另有不进入普通 help/MCP 的内部 install-state 自描述入口供下一版安装器升级使用
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

逻辑 Reference Bundle v3
→ source_digest + routing_digest + bundle schema
→ bundle_version

Runtime encrypted container v3
→ random build root material + random bundle salt
→ HKDF-SHA256 派生 private-manifest key 与 per-reference key
→ encrypted private manifest
   + opaque record locator
   + per-reference AES-256-GCM authenticated records
```

Private Manifest 保存 Runtime 求值必须使用但不应暴露为外层 Catalog 的 Reference identity、hash/size、opaque locator、动态 Skill Catalog 与 private Routing Manifest。外层 encrypted container 只保存 schema/salt、加密 Manifest 与 opaque record framing。Reference record 的 AEAD AAD 绑定 bundle version、Stable ID、locator、SHA256 和 size，record 交换或材料篡改必须失败关闭。

Runtime 打开 encrypted container 时只解密和验证 private Manifest，不预解密 canonical Reference 正文；`load_required_context` 只对当前 required Reference 派生 record key、解密、验证 hash/size/UTF-8，再以 exact-text 返回。显式 `self-test` 会逐 record 验证全库，但同样不建立长期 plaintext corpus cache。

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

目标项目没有 Agent_Skills `references/`。Source Mode 直接读取源仓库 required References；Runtime Mode 通过中文 Task Route 和当前不透明 task-bound route capability 取得 required 完整原文。完整原文继续逐字保留 canonical routing metadata；Runtime 的保密边界不能通过删改 Reference 原文实现，否则会破坏 source/routing 完整性。

## 3. 项目安装边界

当前 Runtime 产品 basename 统一为 `agent-skills`：Windows 项目安装为 `.agents/runtime/agent-skills.exe`，Linux/macOS 安装为 `.agents/runtime/agent-skills`。该名称同时用于 Builder 默认产物与 Release ZIP 内 binary。

onefile binary 无参数运行默认安装/升级当前目录；也支持：

```text
agent-skills install --target <project-root>
```

当前 Project Payload 使用 v2。**新安装和升级不再生成 `.agents/agent-skills-install.json` 或其他 ownership sidecar。** 当前 Runtime 的 installation ownership 由 `install_state.py` 直接从已验证 Project Payload 确定性派生，协议为：

```text
agent-skills-runtime-install-state/v1
```

它包含当前 Release 的 `skills`、`shared_files`、`managed_files`、`source_digest`、`payload_digest` 和版本身份，但只作为 Runtime 内部自描述状态存在，不落独立文件，不进入 MCP Tool Contract，也不作为普通用户 CLI/help 入口。

升级时 previous ownership 来源严格限定为：

```text
合法 legacy agent-skills-install/v3
→ 只作为一次迁移输入
→ 成功安装事务末端删除

否则

旧已安装 .agents/runtime/agent-skills[.exe]
→ 内部 __install-state --json
→ 返回旧 Runtime 内嵌 Project Payload 对应的 ownership
→ 新安装器严格校验后使用
```

v1、v2、未知或损坏 legacy manifest 直接失败；旧 Runtime 不存在、不可执行、返回非法 JSON/schema/path/digest 或无法证明 previous ownership 时同样失败关闭，不扫描旧 Stub，也不根据目录/文件名猜 ownership。

项目安装需要保持：

- previous `managed_files` 只认领 Agent_Skills 可证明的具体文件；`skills` / `shared_files` 只作 Catalog/ownership 导航，不授权整目录替换；
- 首次同名未认领 Skill、shared file 或 managed file 均 fail closed；
- 新 Release 删除文件时只删除 previous `managed_files` 明确认领项，不替换整棵 Skill 目录；
- 项目后来添加到受管 Skill 目录中的 Reference/asset/其他文件继续是项目自有，普通升级不能删除；
- `.agents/runtime/` 仍为项目本地运行资产，但安装/升级**不自动新增** Runtime ignore；**项目原本已有** `/.agents/runtime/` 或等价 ignore 时保持原样，不删除、不重复追加；
- `AGENTS.md` / CLAUDE / Codex 使用 managed marker；
- 目标项目 `AGENTS.md` managed block 只做 Runtime 薄 Bootstrap：先恢复项目真实事实，再通过已配置的项目级治理 MCP 获取本次任务所需完整约束；不得把受管源码维护导航当作 Runtime 日常读取入口；
- Runtime 用户可见过程可以正常描述项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git/CI 和交付状态，并解释当前项目真正适用的工程要求；不得主动复述内部治理分类、文件名、目录路径、规则标识、路由映射、内部凭据或加载明细，也不得把 canonical 治理原文、原始治理上下文、内部 Prompt、私有路由清单等作为用户交付内容逐字输出、翻译、编码、分块复制或高保真重建；
- Cursor/Claude JSON 只认领 `mcpServers.agent-skills`；
- marker 外项目文本、其他 MCP server、项目自有 Skill/Reference/资产和未认领 shared file 保留；
- Codex 同名 MCP table 存在但 managed marker 缺失，或合法 managed block 外另有重复同名 table 时，即使 legacy v3 或旧 Runtime install-state 能证明历史安装存在也 fail closed，不猜测 table ownership；
- 任一可预检错误先于写入发现；失败按 bytes/权限快照恢复 touched managed files、Runtime、legacy manifest（如存在）与受管文本；
- legacy v3 manifest 只在所有新文件、Runtime、宿主配置都成功后删除；失败回滚必须恢复它；
- 如果回滚本身有任何失败，必须同时报告原始安装异常与未恢复路径/原因，不能静默吞掉 rollback failure。

取消 sidecar 后有一个必须明确的信任边界：如果没有 legacy v3，升级需要执行目标项目里原先安装的旧 Runtime 来取得其内嵌 install-state。因此 sidecarless upgrade 以**用户已经信任并明确选择的目标工作区**为前提；普通文件/非符号链接校验和 install-state schema/digest/path 校验不是代码签名、TEE 或抵御项目 Owner 恶意替换旧 Runtime 的安全保证。旧 Runtime 无法提供合法状态时宁可停止升级，也不能猜 ownership。

正式 Router 与其他 Skill Core 仍通过动态 Catalog 分发，但写入目标项目的是各自 canonical Core 的确定性 Runtime Projection；Skills 根级 Entry 只通过 Project Payload 的显式 `shared_files` Contract 分发，二者职责不混淆。内部 Entry/Router/Core 存在于目标项目并不意味着它们必须成为用户可见的日常导航；安装 ownership 与用户披露是两个独立边界。

### 宿主连接级生命周期

项目安装写入的 Codex、Cursor、Claude Code MCP 配置都是 `stdio`，命令参数为 `serve`。这意味着 Runtime 是由当前宿主启动并通过标准输入/输出保持连接的**前台子进程**，采用**宿主连接级生命周期**，不是系统常驻服务：

```text
宿主打开项目 / 建立 MCP 连接
→ 启动项目 Runtime `serve`
→ stdio 连接期间保持进程
→ 可在同一连接内复用 task、route capability 与已加载 Context
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
- `submit_route` 仍由唯一 evaluator 在 Runtime 内部计算并单调扩展 required Context，但只返回不透明 route capability、是否还需加载约束和是否仍存在未确认任务事实，不公开命中 Skill、Reference 数量或内部风险结果；capability 内部绑定当前 process/session、task、route digest、累积 required-set digest 与 generation，新一轮 submit、切换 task 或伪造 token 均使旧凭据失败关闭；
- `load_required_context` 只接受当前 route capability，默认只返回尚未加载的 required 完整原文；每个公开 context envelope 只含 `完整原文`，不附带 Stable ID、Skill、文件名、路径、SHA256、字节数或 locator，也不接受任意 ID/filename/path/Catalog/glob/dump 参数；
- `checkpoint` 只返回当前阶段和是否通过，不公开 required/loaded 集合详情。

事实充分、`未知项=[]` 的 Task Route 继续使用原有二值 fixed-point 语义。存在未知维度时，Runtime evaluator 使用 TRUE/FALSE/UNKNOWN 三值逻辑：UNKNOWN 只保守扩大真正依赖该未知维度的候选 Context，再展开依赖与风险 fixed-point；不得因为任一未知事实直接把全库设为 required。如果仅由未知事实把候选扩大到 full corpus，而事实充分部分本身并不需要全库，则 fail closed 并要求宿主先恢复更多当前项目事实。

这些变化只收窄**公共 envelope 与不充分事实的过宽导出路径**，不改变事实充分任务的 canonical 路由语义、加密 Bundle 内部 provenance、hash/size、依赖图、风险下限或 canonical exact-text。`checkpoint` 仍不能替代 Requirement Traceability、Completion Audit、Review、Docs Impact 或真实测试。Task Route 的授权字段只是数据，不能产生 Git、发布或部署权限。

内部 `__install-state --json` 不是第七个 MCP Tool，也不加入普通 CLI help；它只服务后续 Runtime 安装器恢复 previous ownership。Runtime 给宿主的每个关键 MCP 返回仍携带同一用户可见进度规则：允许说明真实工程活动及其原因；不得把 MCP 内部调用、治理资产身份、分类、路由和加载明细作为用户可见过程复述，也不得把内部治理原文作为用户交付内容。这里是输出层约束，不是禁止模型执行这些治理步骤，更不是对本机 Owner 的密码学访问控制。

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
scripts/build_runtime.py ... --release-version <SemVer> --json
```

构建器读取显式版本和真实 source commit，动态发现 Skill/Reference，编译 canonical metadata，构建逻辑 Bundle v3 / source identity，从 canonical exact-text 生成 encrypted private manifest + per-reference authenticated records，并从同一 canonical Skill Core 自动生成 no-Stub Project Payload 中的 Runtime Projection，再生成当前平台 artifact 并执行 `status` / `self-test` 校验。由于公共 `status/self-test` 不再暴露详细内部摘要，Builder 会在维护侧用同一份 Bundle、Payload、release/source 身份计算一个不可逆整体完整性指纹，并要求 artifact `self-test` 返回完全一致的指纹；这样仍能证明 artifact 与当前构建材料一致，同时不把内部身份字段重新开放给 Runtime 日常调用。

Build 每次生成新的高熵 root material 与 bundle salt。完全本地、离线、零额外用户配置的 Runtime binary 必然包含或能够恢复执行解密所需的根材料；当前实现将其与 v3 encrypted container 一同嵌入 onefile 临时构建副本。该事实只能描述为 reverse-engineering hardening，不得宣称 binary 内存在本机 Owner 无法恢复的秘密。root material、派生 key、route capability 和 plaintext corpus 都不得写入日志、Release asset 或 sidecar。

**Builder 不再生成 `.manifest.json` sidecar。** `--json` 直接返回维护侧 build identity，至少包括：

```text
artifact / artifact_sha256
release_version / source_commit / python_version
integrity_fingerprint
bundle_schema / bundle_version
Task Route / Routing Manifest / MCP Tool / Project Payload protocol
source_digest / routing_digest / payload_digest
Skill 集合与 context_budget
```

这些字段由普通 Runtime Package CI 直接解析；正式 Release 的每个平台 job 再通过 `GITHUB_OUTPUT` 把公共 identity 和该平台 `artifact_sha256` 传给发布 job。构建目录因此只有实际 onefile binary 等必要构建产物，不再需要 `agent-skills*.manifest.json` 作为第二份身份副本。

Builder 的维护者 JSON 输出还包含聚合 `context_budget`：

```text
entry_bytes
router_bytes
skill_core_bytes
reference_bytes_by_skill
base_router_plus_core_bytes
```

它只量化 Entry / Runtime Router Projection / 专业 Runtime Skill Projection / canonical Reference 的聚合字节成本，不列出单个 Reference ID、文件名、路径或触发映射，也不改变 Runtime `status/self-test` 的公开披露合同。为保持现有构建报告消费者兼容，`router_bytes` 与 `base_router_plus_core_bytes` 字段名保留；新增 `entry_bytes` 单独记录薄入口成本。

“最新规则模式”允许网页端 Source Mode 读取当前 `main`、本地 Runtime 使用当前最新 Release，但二者在发布间隙可能短暂不同步；“精确复现模式”应以 Runtime 的 `Release版本` 定位对应正式 Release/tag，再从该 tag 的源码事实复现同一版本。development `0.0.0-dev` 的精确构建证据以 Builder JSON/CI 记录为准，不再依赖磁盘 identity manifest。

Linux/macOS 默认输出目录中正式 onefile：

```text
dist/agent-skills
```

Windows：

```text
dist/agent-skills.exe
```

同目录不应出现同名或版本化 `*.manifest.json`。

## 6. 真实 MCP 验证

```bash
python scripts/runtime_mcp_smoke.py --artifact dist/agent-skills --json
```

该 smoke 使用真实 stdio MCP client 验证六个 Tool、中文 input schema、去标识化公共 envelope、route contract、submit、required Context exact-text、stale/伪造/跨 task capability、unknown-induced full-corpus fail-closed 和 checkpoint，不用内部 Python 函数调用冒充 MCP 边界。hash/size/source/routing 等完整性仍在维护侧 Bundle/Builder 验证，不要求通过公共 context envelope 暴露。

## 7. 永久 CI

永久 CI 按证明责任拆分，不再让每次纯 Skill/Reference/治理变化都重复构建三平台 binary。

### Skill Tests

`.github/workflows/skill-tests.yml` 使用 Python `3.14.7`，安装 Runtime 的运行依赖而不是 PyInstaller 构建依赖，并持续验证：

- self-contained unit/preservation/portability tests；
- Source Mode 唯一 Skills 根级 Router 与 Maintenance 职责、Runtime 薄 Bootstrap 可见性边界，以及 Project Payload shared-file 分发；
- metadata compiler/evaluator、Routing Conformance、tri-state unknown semantics、private manifest/per-reference encryption 与 exact-text parity；
- Runtime Projection 不暴露当前 canonical Reference 文件名、路径、Stable ID 或直接导航映射，同时保留 frontmatter、路由 metadata、核心工程语义并由动态 Reference 身份自动驱动；
- Runtime 公共返回面不暴露内部治理身份，同时 required canonical Context exact-text 不被删改；
- v3 Manifest/record tamper、record swap、locator mismatch、lazy decrypt、自检全库与 task capability 安全回归；
- sidecarless install-state、legacy v3 一次迁移、v1/v2/未知 schema 拒绝、项目自有 Reference 保留、同名冲突、Codex marker/重复 table fail-closed 和失败/回滚诊断；
- Builder JSON identity 与 no-sidecar Release preservation；
- 动态 Skill Bundle + Project Payload 的源码级构建、投影确定性与内容守恒；
- Active/changed Change Ready Check。

这条 Workflow 不运行 PyInstaller，不构建 onefile，也不创建 Windows/macOS package job。规则正文会进入下一次正式 Runtime，但它的内容、路由、Bundle/Payload 和治理正确性由上述源码级自动化证明。

### Runtime Package Tests

`.github/workflows/runtime-package-tests.yml` 只在 Runtime/Builder/MCP 安装/Release 工作流相关路径变化时触发，并使用 Linux、Windows、macOS 对应 Runner 真实验证：

- onefile build/status/self-test；
- development `release_version=0.0.0-dev` 与固定 Python identity；
- Builder JSON 的 `integrity_fingerprint` 和实际 binary `artifact_sha256`；
- 构建目录不存在 `*.manifest.json`；
- real stdio MCP，包括 stable Tool Contract、exact-text、capability 与 unknown full-corpus anti-export；
- project-only single-binary 首次安装、重复安装/升级和无参数安装；
- 安装项目不存在 `.agents/agent-skills-install.json`，也不存在 canonical Reference/Stub/Private Routing Manifest；
- 已安装 Runtime 的内部 install-state 能认领当前 Entry/Router，但不进入 MCP；
- 项目内 Runtime status/MCP smoke；
- Windows/macOS 对应平台 package/install。

不同平台必须使用对应 Runner，不能把一个平台的 PyInstaller artifact 当跨平台二进制。Skill Tests 的绿色不能替代这一层；反过来，Runtime package 绿色也不能替代规则/内容守恒/Ready 的广覆盖测试。

## 8. 正式 Release

正式 Release 由根 `.github/workflows/release.yml` 从 `main` 手工构建。输入 `v<SemVer>` tag 后，workflow 将同一 `release_version` 显式传入 Linux/Windows/macOS Builder；Release preflight 会重新运行完整 self-contained tests 与 Ready Check。

三个平台 build job 都直接解析 Builder JSON，并把下列**公共 identity**通过 job outputs 传给最终发布 job：

```text
release_version / source_commit / python_version
integrity_fingerprint
Bundle/Task Route/Routing Manifest/MCP Tool/Project Payload protocols
bundle_version / source_digest / routing_digest / payload_digest
```

同时每个平台单独传递自己的 `artifact_sha256`。发布 job 要求三平台公共 identity 完全一致，并要求 `source_commit == GITHUB_SHA`、Python 与协议固定值正确、digest/fingerprint 格式合法；随后对下载后的 Linux、Windows、macOS binary 分别重新计算 SHA256，并与对应平台 output 比对。平台 binary 不同，因此三个 `artifact_sha256` **不做互相相等比较**，而是各自绑定自己的真实 artifact。

Release 流程明确不生成、上传或打包任何 identity `*.manifest.json`。所有三平台 artifact / identity 完成验证后，workflow 从显式白名单成员分别组装并回读验证三个最终分发 ZIP：`agent-skills-v<SemVer>-linux.zip`、`agent-skills-v<SemVer>-windows.zip`、`agent-skills-v<SemVer>-macos.zip`。每个 ZIP 根目录只包含当前平台 Runtime binary 与同一版本 [`USAGE.md`](../USAGE.md)，Draft 与正式 Release 都必须精确只有这三个平台 ZIP 资产；Builder JSON、checksum 文件、独立 binary、说明文件、root material、private manifest 或其他维护资产都不进入正式 Release。

最终用户资产和使用方式以根 [`USAGE.md`](../USAGE.md) 为准。本文件不维护第二份最终用户教程，也不记录 Change/PR/Release 历史流水账。

## 9. 安全边界

Private Repository 承担 canonical Source 的访问控制；Runtime 加密不能替代仓库权限。Local Hardened Runtime v3 的目标是减少目标项目中的普通明文浏览/复制面、避免 Runtime 启动即持有全库 plaintext、检测 Manifest/record 篡改，并堵住方便的 unknown-route full-corpus export。它不是 TEE/KMS/DRM。

v3 使用 encrypted private manifest、opaque record locator、HKDF-SHA256 用途隔离派生与 per-reference AES-256-GCM authenticated records。Runtime 默认只解密当前 required Context；这缩小主动 plaintext 生命周期，但 Python `bytes`/`str` 不能提供可证明的物理 zeroize，因此不得宣称离开作用域后 RAM 已立即清零。

完全本地、离线、零额外用户配置意味着 binary 必然包含或能够恢复执行解密所需的根密钥材料。当前实现不再使用“一个明显完整 Bundle key + 整包 ciphertext”的 v2 结构，但这只是提高静态提取和批量导出的成本，不形成对本机 Owner 不可恢复的秘密。不得打印或发布 root material、派生 key、route capability、private manifest 或 canonical plaintext corpus。

MCP anti-export 同样是应用层边界：公共协议不提供按 ID/filename/path/Catalog/glob/dump 的任意读取接口；未知事实只保守扩大相关候选，unknown-induced full corpus fail closed；task-bound capability 阻止 stale、cross-task 与伪造 token。它不能阻止控制本机的用户观察合法 MCP plaintext、反复构造真实任务或 Hook Runtime。

Runtime Mode 的 disclosure policy 约束正常 Agent/Prompt/Skill/Runtime 可控制输出：内部治理原文、原始治理上下文、内部 Prompt、私有 Routing Manifest 等不能因用户要求而被逐字输出、翻译、编码、分块复制或高保真重建；但 Agent 必须继续直接解释当前目标项目实际适用的工程要求、风险、测试、Review、Docs、Git/CI 和交付理由。Source Mode 维护者在拥有 canonical 仓库访问权时仍可正常查看和讨论内部源文件。

sidecarless installation ownership 同样不是新的安全隔离层。它减少的是目标项目和构建目录中的状态副本：当前 ownership 已经存在于 Runtime 内嵌 Project Payload，Builder identity 已经存在于构建结果与 CI。升级通过旧 Runtime 的内部 install-state 读取 previous ownership，以用户已经信任并明确选择的目标工作区为前提；普通文件/路径/schema/digest 校验不能抵御项目 Owner 主动替换旧 Runtime，也不能宣称等价于代码签名、TEE 或可信远程证明。旧 Runtime 不可验证时必须停止升级而不是猜 ownership。

模式感知披露只能减少正常 Agent 对话中主动复述内部治理结构和治理原文的产品表面，不等于阻止拥有机器控制权的用户查看受管明文 Runtime Core/Router、MCP 通信或进程内解密后的完整规则。不能宣称能够抵御机器 Owner、调试器、内存转储、进程 Hook、MCP 通信观测或专业逆向。真正限制谁能读取 canonical 源文件，必须依赖源仓库访问控制；如果未来要求恶意本机 Owner 也不能取得 canonical 原文，需要迁移到受控 Remote Governance 架构，并作为独立架构 Change 处理。
