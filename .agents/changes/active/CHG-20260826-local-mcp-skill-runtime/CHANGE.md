---
schema: coding-change/v1
id: "CHG-20260826-local-mcp-skill-runtime"
title: "Native Core Skill + 本地 MCP 加密 Reference Runtime"
level: L3
status: ready_for_review
owner: "ChatGPT"
branch: "feature/local-mcp-skill-runtime"
created: 2026-08-26
updated: 2026-08-26
completion_gate: required
depends_on: []
affected_areas:
  - "Coding Skill"
  - "Review Skill"
  - "Docs Skill"
  - "Local MCP Runtime"
  - "Skill Bundle Packaging"
  - "Runtime Distribution Kit"
  - "Installation and Upgrade"
  - "Target Project Overlay"
  - "CI"
affected_paths:
  - ".agents/skills/coding/SKILL.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/tests"
  - "runtime/"
  - "runtime/DISTRIBUTION.md"
  - "runtime/requirements.txt"
  - "runtime/requirements-build.txt"
  - "runtime/requirements-tools.txt"
  - "scripts/build_runtime.py"
  - "scripts/install_runtime.py"
  - "scripts/install_runtime_target.py"
  - "scripts/runtime_mcp_smoke.py"
  - "scripts/install.py"
  - "README.md"
  - ".agents/README.md"
  - "AGENTS.md"
  - ".github/workflows/skill-tests.yml"
contracts:
  - "Agent Skills Runtime Bundle v1"
  - "Agent Skills Runtime Manifest v1"
  - "Agent Skills Runtime MCP stdio Tool Contract"
  - "Runtime Reference Stub v1"
  - "Agent Skills Runtime Distribution Kit v1"
  - "scripts/build_runtime.py CLI"
  - "scripts/install_runtime.py CLI"
  - "scripts/install_runtime_target.py CLI"
  - "scripts/install.py --mode runtime CLI"
  - "目标项目 AGENTS managed block"
data_changes: []
---

# 目标

在不压缩、不摘要、不重写现有 Coding / Review / Docs 复杂自然语言规则的前提下，为 Agent_Skills 增加可本地分发的 MCP Runtime，使目标项目可以继续保留原生 Core Skill 对 Coding Agent 的稳定入口和任务路由，同时不再以普通 Markdown 形式分发完整 `references/` 正文。

目标运行链：

```text
目标项目 AGENTS.md
→ 原生 Core Skill（SKILL.md）
→ 按现有触发条件命中同名 Reference Stub
→ 本地 Agent Skills MCP
→ 加密内嵌的 canonical Reference Bundle
→ agent_skills_load_context
→ 返回该 Reference 的原始 canonical_text + SHA256
→ Codex 将原文作为当前阶段规则上下文继续工作
```

本任务的第一优先级是**保持现有 Skill 执行效果**。本地加密仅用于避免部门使用者直接打开目标项目中的 Markdown 就获得全部高价值 Reference；不把它描述成能抵御机器 Owner、调试器、内存转储或专业逆向的强安全边界。

在 Completion Audit 中还确认了一个原始方案未显式写出的分发要求：部门使用者不应为了给新项目接入 Runtime 而获得私有 canonical Agent_Skills 源仓库。因此最终构建还必须输出一个**不含 canonical Reference 正文的 Runtime Distribution Kit**，让使用者只拿 Kit 就能安装/升级用户级 Runtime、注册 MCP，并给目标项目安装 Native Core + Runtime Stub。

# 可观察成功标准

- [x] 源仓库现有 `.agents/skills/{coding,review,docs}/references/*.md` 继续作为唯一 canonical 规则正文，不迁移到 Policy DSL，不自动摘要。
- [x] 新增确定性 Bundle Builder，收集三个 Skill 的 Reference 原始 UTF-8 内容、路径、稳定 ID、SHA256、size，生成可验证的 `source_digest`；输入内容不改写。
- [x] Bundle 使用 authenticated encryption 加密并在构建产物中嵌入；目标用户无需单独获得明文 Reference 文件或解密 key 文件。
- [x] 新增本地 stdio MCP Runtime，至少暴露 `agent_skills_manifest`、`agent_skills_load_context`、`agent_skills_start_task`、`agent_skills_checkpoint`、`agent_skills_status`；不暴露任意路径读取接口。
- [x] `agent_skills_load_context` 返回命中 Reference 的 canonical 原文和 hash，不做 LLM 总结、改写或规则抽取；Runtime manifest 不泄露正文。
- [x] Runtime 维护当前 task/phase 已加载 Reference 状态，`checkpoint` 能明确报告 required / loaded / missing，阶段切换可继续加载规则但不替代 Codex 的自然语言路由判断。
- [x] `scripts/build_runtime.py` 可使用当前仓库 canonical References 构建当前平台单文件可执行产物，并在构建完成后运行 `status` / `self-test` 验证 bundle 与当前 source digest 一致。
- [x] `scripts/install_runtime.py` 可把构建好的 Runtime 原子安装/升级到用户级目录，安装后执行 `status` / `self-test`；失败恢复旧版本。
- [x] `scripts/install.py` 保持现有 `python scripts/install.py --target ...` 行为兼容，默认仍为 `full`；新增显式 `--mode runtime`，只有 Runtime 自检和 source digest 匹配后才修改目标项目。
- [x] Runtime 模式安装仍保留 Core `SKILL.md`、必要 assets/agents/scripts，并为每个 canonical Reference 生成同名 stub；目标项目中不出现 Reference 原始正文，现有 `SKILL.md` 相对链接仍能命中 stub。
- [x] Stub 包含稳定 Runtime ID 和 expected SHA256，并明确要求在执行该 Reference 对应动作前调用 `agent_skills_load_context`；MCP 不可用、Reference 不存在或 hash 不一致时不得凭印象继续。
- [x] 目标项目已有 `.agents/changes/`、项目自有 Skill、AGENTS marker 外内容和其他 `.agents` 内容继续受到现有安装/回滚保护。
- [x] 构建输出 `agent-skills-mcp-runtime-kit.zip`；Kit 只包含平台 Runtime、manifest、Core/Stub payload、独立安装器和使用资料，不含 canonical Reference 正文；解压后可以在不访问私有 Agent_Skills 源仓库的条件下给新目标项目完成安装。
- [x] README、`.agents/README.md`、`runtime/README.md`、`runtime/DISTRIBUTION.md`、reference 13/14 和 AGENTS managed block 清楚说明如何构建、安装 Runtime、配置 MCP、首次接入目标项目、重复升级、full/runtime 两种模式和真实安全边界。
- [x] CI 对 Runtime 源码、Bundle/crypto/store、Runtime 模式安装、原文守恒、CLI smoke、PyInstaller package、真实 stdio MCP、用户级安装、Distribution Kit 无源仓库安装提供新鲜证据；现有 Bootstrap/Change/Review/Docs/portability 测试不回归。

# 范围

- 新增 Runtime Bundle catalog、authenticated encryption、内嵌 payload 加载、状态存储和 MCP stdio Server。
- 新增当前平台 Runtime 单文件构建脚本与用户级安装/升级脚本。
- 在现有项目安装器中增加 opt-in Runtime 分发模式，默认 full 模式保持兼容。
- 新增 Reference Stub 生成和 source digest / Runtime artifact 匹配校验。
- 新增 source-independent Runtime Distribution Kit，以及 Kit 内独立 `install_runtime_target.py`，让使用者不需要私有源仓库即可把 Core/Stub 安装到目标项目。
- 新增 Kit payload 文件集合、path、size、SHA256 完整性验证，拒绝 symlink/path traversal 和未声明 payload 文件。
- 只对 Core Skill、managed block、安装 reference、README、Runtime 分发文档、CI 做实现 Runtime 所需的增量规则补充。
- 新增自包含单元/集成测试、真实 stdio MCP smoke 和 Linux/Windows package smoke。

# 非目标

- 不把现有 Reference 自然语言重写成 Policy DSL、布尔规则或自动摘要。
- 不在第一版自动把任意自然语言任务全部路由成固定 Reference 列表；Codex 继续依据 Core Skill 和当前项目事实执行现有语义路由。
- 不把本地 MCP 描述成能够阻止机器 Owner 提取运行时明文的强保密系统。
- 不增加远程 Policy Server、OAuth、License Server、KMS 或服务器侧 LLM。
- 不让 MCP 任意读取目标仓库文件，也不把它重新实现成第二个 Coding Agent。
- 不删除现有 full Markdown 分发模式；已有用户可以继续使用当前安装命令。
- 不修改 `coding-change/v1` schema。
- 不改变项目事实来自目标仓库 Overlay/代码/Contract/运行证据的原则。
- 本轮不把 Kit metadata 升级成公钥签名供应链；当前威胁模型不要求对抗机器 Owner 或恶意本地篡改者。
- 本轮不把 `start_task/checkpoint` 升级为多会话持久状态数据库；它们只作为当前 MCP 进程的辅助加载状态，不能替代 Completion Audit/Review/CI 权威门禁。

# 必须保持不变

- Coding / Review / Docs 的职责分离不变；Coding 仍负责按条件路由 Review / Docs。
- 现有 `SKILL.md` 与 references 的可执行语义、触发条件、例外、失败处理、停止条件、验证责任、安全与兼容边界必须完整保留；Runtime 模式只是改变 Reference 正文的交付通道。
- 源仓库 canonical Reference 仍然可以直接被 Agent_Skills 维护者读取和 Review，构建器不回写或格式化源 Markdown。
- `coding-change/v1`、Requirement Traceability、Validation Matrix、Completion Audit、Ready Check 语义不变。
- 目标项目 `AGENTS.md` managed marker 外原文、`.agents/changes/`、项目自有 Skill 和其他 `.agents` 内容不因 Runtime 安装被删除或覆盖。
- `.agents/project-context.json` 继续是本地可失效缓存并被目标项目忽略。
- 用户定义的五项跨项目工程硬规则完整保留：中文代码注释；所有新增或修改函数都有函数级中文说明；中文 Git 提交；默认北京时间 `Asia/Shanghai`；统一人类可读日志前缀。

# 关键决策

## 方案比较

### 方案 A：继续完整 Markdown 原生分发

优点：Codex 读取路径最短，现有执行效果上限最高，几乎没有新增运行时失败点。

缺点：目标项目和员工机器可直接浏览完整 Reference 正文，无法满足“避免随手复制全部 Skill 知识资产”的分发目标。

### 方案 B：纯 MCP Policy / Boolean / Guidance

优点：可以最大限度隐藏原始规则文本，接口容易控制。

缺点：复杂文档写作、Review、根因调试、验证与例外规则不能可靠压缩成布尔结果；如果返回自动摘要 Guidance，会降低现有 Skill 原文对 Codex 上下文和推理的影响；需要重写大量规则并产生语义漂移风险。

### 方案 C：Native Core Skill + Local MCP Encrypted Canonical Reference Bundle（采用）

Core `SKILL.md` 保持原生 plaintext，继续负责稳定进入研发工作流、恢复事实、判断触发条件和决定何时需要某个 Reference；详细 Reference 正文在构建期逐字收集、哈希、加密并嵌入本地 MCP 可执行产物。目标项目保留与原文件同名的 stub，保证 Core Skill 现有链接不失效；Agent 读取 stub 后调用 MCP `load_context` 获得 canonical 原文。

该方案把新增机制限制为“规则内容传输和完整性验证”，不重新实现 Skill 的复杂自然语言方法论，因此在当前目标下兼顾执行效果、升级便利和普通防复制能力。

## Reference ID 与原文守恒

编号 Reference 使用稳定 ID：

```text
coding.reference.02
review.reference.01
docs.reference.04
```

ID 从 `<skill>` + Reference 两位数字前缀生成；重复编号必须构建失败。每条 Bundle entry 记录 exact UTF-8 bytes 的 SHA256 与 size。`load_context` 返回的 `canonical_text` 必须与源文件 UTF-8 解码内容一致，不能换行标准化、去 frontmatter、摘要或重新排版。

`source_digest` 明确先按 Reference ID 排序，再基于 `id/source_path/sha256/size` 生成稳定 JSON 物料并计算 SHA256；不能依赖当前目录遍历顺序偶然稳定。

## Bundle 与加密边界

第一版使用 AES-256-GCM authenticated encryption。随机 32-byte key 与随机 nonce 只用于构建产物；构建时生成的 Python payload module 只存在临时构建目录，不提交 Git。单文件可执行产物同时包含解密所需 key 和 ciphertext，因此这一层只用于提高直接浏览/复制门槛，不是对本机管理员的可信执行环境。

Bundle `source_digest` 由排序后的 Reference ID、source path、SHA256 和 size 计算。目标项目 Runtime 安装模式在任何写入前比较当前源仓库计算的 digest 与 Runtime `status/self-test` 返回 digest；不匹配即拒绝，避免旧 Runtime 与新 stub/Reference hash 混装。

## MCP Contract

第一版 stdio MCP 不提供 `read_any_file(path)` / `read_skill(path)` 或通配路径接口，只提供稳定逻辑 ID：

- `agent_skills_status()`：Runtime / bundle/schema/digest/reference count；不返回正文。
- `agent_skills_manifest(skill?)`：Reference ID、skill、filename、SHA256、size；不返回正文。
- `agent_skills_start_task(task_id, phase="planning")`：建立或重置当前任务上下文状态。
- `agent_skills_load_context(ids)`：验证 ID 后返回每条 canonical_text、SHA256、filename，并记录为已加载。
- `agent_skills_checkpoint(required_ids, phase?)`：报告 required / loaded / missing；不替代自然语言语义 Review。

MCP `mcp.run()` 使用 stdio；stdout 只用于 MCP wire protocol，不输出人类日志。

## Full / Runtime 安装兼容

现有：

```bash
python scripts/install.py --target <target>
```

保持等价于：

```bash
python scripts/install.py --mode full --target <target>
```

新的源仓库 Runtime 模式必须显式提供 Runtime command：

```bash
python scripts/install.py --mode runtime --runtime-command <agent-skills-mcp> --target <target>
```

Runtime 模式只在自检/digest 校验成功后切换目标受管 Skill。现有暂存、逐 Skill backup、失败回滚、Bootstrap 失败回滚继续复用。

普通部门使用者不需要源仓库。维护者构建出的 Distribution Kit 还提供：

```bash
python install_runtime.py --artifact <agent-skills-mcp[.exe]> --json
python install_runtime_target.py --runtime-command <已安装 Runtime> --target <target> --json
```

`install_runtime_target.py` 只读取解压后的 Kit metadata/payload，逐文件验证 payload path/size/SHA256，并验证 Runtime `source_digest` 与 Kit 一致；它不 import、搜索或访问私有 Agent_Skills 源仓库。

## 打包 / 升级

源仓库构建当前平台 Runtime：

```text
canonical References
→ deterministic catalog + source_digest
→ JSON bundle
→ AES-GCM ciphertext + random key
→ 临时 _embedded_payload.py
→ PyInstaller onefile
→ status/self-test
→ dist/agent-skills-mcp[.exe]
→ dist/agent-skills-mcp.manifest.json
→ dist/agent-skills-mcp-runtime-kit.zip
```

Distribution Kit 包含平台 Runtime、manifest、`install_runtime.py`、`install_runtime_target.py`、工具依赖/说明和已经由正式 runtime-mode 安装逻辑生成的 Core/Stub payload；它**不包含 canonical Reference 正文**。Kit Builder 复用 `scripts/install.py --mode runtime` 生成 payload，避免维护第二套 Stub 生成逻辑。

Runtime 是平台相关可执行文件；Windows 必须在 Windows 上构建 `.exe`，Linux/macOS 同理。用户级 Runtime 安装路径与目标项目解耦。Reference/Core 变化后，使用者应使用同一新版 Kit 先升级用户级 Runtime，再对每个目标项目重新运行 Kit 的目标安装器；禁止只升级一侧长期制造旧 Runtime/新 Stub 或新 Runtime/旧 Stub 混装。

Windows CPython 通常没有系统 IANA 时区数据库，而既有 Coding Bootstrap 使用 `ZoneInfo("Asia/Shanghai")`。因此 Runtime build/tools 环境固定 `tzdata==2026.3`；Windows 使用者按 `runtime/DISTRIBUTION.md` 建立工具 venv，并用该 Python 执行 Kit 的安装脚本，从而保持北京时间硬规则而不改写既有 Coding Bootstrap 语义。

## 回滚

- Runtime Build 不修改 canonical References。
- `install_runtime.py` 在替换用户级 Runtime 前保留旧版本；新版本 `status` / `self-test` 失败时恢复旧文件。
- `install.py --mode runtime` 在修改目标项目之前先验证 Runtime；Skill 切换和 Bootstrap 失败继续沿用现有多目录 rollback。
- Kit 的 `install_runtime_target.py` 同样先验证 metadata/payload/Runtime digest，再暂存三个 Skill；切换或 Bootstrap 失败时恢复本轮已切换 Skill。
- 回滚到旧 Runtime 时，必须同时使用与该 Runtime `source_digest` 匹配的 Agent_Skills source/stub 版本；部门使用者最安全的方式是使用对应旧 Kit 同时恢复 Runtime 与目标项目 Core/Stub，digest 不一致时安装器拒绝制造混合状态。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 保持现有完整 Skill 对 Codex 推理的效果，复杂 Reference 不压缩成布尔或摘要 | user:execution-effect-first | satisfied | canonical Reference bytes 直接进入 Bundle；`RuntimeStore.load_context`/真实 stdio MCP smoke 将 `canonical_text` 与源 Reference 原文逐字比较；ref14 明确禁止自动摘要/DSL |
| R2 | 本地分发时不在目标项目明文放置完整 Reference，但不要求对机器 Owner 强保密 | user:local-mcp-protection-boundary | satisfied | AES-256-GCM onefile Runtime + Runtime Stub；`test_runtime_distribution` 与 Kit 测试断言目标/Kit stub 不含 canonical body；文档明确本地逆向边界 |
| R3 | 保留 Native Core Skill，让现有触发/路由继续指导 Agent，而不是纯 MCP 替代 Skill | user:native-core-plus-mcp | satisfied | runtime/source/Kit 两条目标安装链均原样复制 Core `SKILL.md`，Reference 保持同名 stub，managed block 要求 Core 命中 stub 后加载 canonical context |
| R4 | MCP 必须能把命中 Reference 原文传给本地 Codex 上下文 | user:read-skill-context-equivalence | satisfied | `agent_skills_load_context` 返回 exact `canonical_text` + SHA256；run `32971575613`、`32971926415` 的 Linux/Windows 真实 stdio `tools/list`/`tools/call` smoke 均通过 |
| R5 | 告诉用户如何打包、安装、配置和升级 | user:package-and-use | satisfied | `runtime/README.md`、`runtime/DISTRIBUTION.md`、根 README、`.agents/README.md`、ref13/ref14 已覆盖 Windows/POSIX 构建、Runtime 安装、Codex/Cursor/Claude 注册、项目接入、升级、回滚与安全边界；所有公开 CLI `--help` 进入 CI |
| R6 | 现有 full 安装方式和目标项目保护边界不得被静默破坏 | .agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md | satisfied | `install.py` 默认仍为 full；既有 Bootstrap/rollback 测试继续通过；runtime digest mismatch 在创建目标 `.agents` 前失败；`.agents/changes`/自有 Skill/marker 外规则保持 |
| R7 | 原始 Skill/reference 高价值语义不得因本功能被总结、重写或丢失 | AGENTS.md | satisfied | canonical `references/*.md` 未迁移或重写；Bundle content 由原始 UTF-8 bytes decode；exact-text/hash 单测 + 真实 MCP smoke；Stub 明确不能替代 canonical_text；Review ID `5030751931` 完成内容守恒 A1/A2 检查 |
| R8 | 代码、Git、时间、日志与交付遵守 Agent_Skills 全局硬规则及 CI/PR 门禁 | AGENTS.md | satisfied | 新增/修改函数均有中文函数级 docstring，feature commits 使用中文；Windows 时区依赖保持 `Asia/Shanghai`；没有绕过 CI/PR/Ready Gate；run `32971926415` 证明实现链全绿且 Ready Check 因本 Change 尚为 in_progress 正常阻断，现已完成 Review 后转 ready_for_review |
| R9 | 部门成员只拿构建产物即可安装/升级 Runtime 和新目标项目，不需要私有 canonical Agent_Skills 源仓库 | user:package-and-use | satisfied | `agent-skills-mcp-runtime-kit.zip` + 独立 `install_runtime_target.py`；Verify Red run `32970949023` 的 2 个新 Kit 用例仅因实现不存在失败；Green run `32971575613` 在 Linux/Windows 均从解压 Kit、切换到源仓库外目录后成功安装全新目标项目 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | `test_runtime_bundle.py` 覆盖 ID/hash/digest、exact text、AES-GCM roundtrip/tamper、manifest 不泄露；`test_runtime_distribution.py` 覆盖 stub/full 兼容与 digest preflight；`test_runtime_installer.py` 覆盖用户级 Runtime 最终自检失败 rollback；Kit tests 覆盖 no-source payload/安装；run `32971575613`/`32971926415` 70/70 自包含测试通过 |
| 接口 / Contract | required | MCP 五个稳定 Tool 名称/参数/返回结构、Bundle/Manifest/Kit schema、Runtime stub、build/install/install-target/runtime-mode CLI；`runtime_mcp_smoke.py` 对最终 onefile 做真实 `tools/list` 与 `tools/call` |
| 集成 / Persistence / Runtime Dependency | required | 临时真实文件系统执行 Runtime 安装/backup/rollback、源 runtime-mode 目标安装、解压 Kit 无源目标安装；真实 subprocess `status/self-test`，不用 Mock 冒充 filesystem/process |
| 用户 / Workflow Acceptance | required | canonical source → build bundle → onefile → user install → host stdio MCP → source runtime-mode 或 source-independent Kit target install 的可重复命令已固化；`runtime/DISTRIBUTION.md` 提供部门使用路径 |
| 跨组件 Golden Path | required | Source Reference → encrypted embedded bundle → onefile Runtime → true stdio MCP `load_context` → exact canonical text/SHA → target same-name stub；Linux/Windows 均有 runner 证据 |
| 外部依赖 Probe | not_applicable | Runtime 为本地 stdio MCP，无付费 Provider、远端 API、生产资源或真实外部系统；PyPI build/tool 依赖属于 Build 依赖，不是产品外部运行边界 |
| Build / Package / Runtime | required | run `32971575613` 与 `32971926415`：Ubuntu onefile + Runtime Kit + status/self-test + MCP + user install + target install；Windows `.exe` Job 全绿并完成同等链路；PyInstaller 不以 Linux artifact 冒充 Windows 证据 |
| Docs / Governance / Other | required | AGENTS/managed block、ref13/ref14、README、`.agents/README.md`、`runtime/README.md`、`runtime/DISTRIBUTION.md`、Change Traceability/Completion Audit 与 CI path/compile/package smoke 同步；PR Review `5030751931` 无 blocker |

## 关键 Red / Green 证据

- 初始 Runtime package Red：PR Runner 在 PyInstaller `--collect-all mcp` 阶段因扫描未使用的 `mcp.cli` 可选 `typer` 失败；修复没有引入无关 `typer`，而是收窄为 Runtime 真实静态 import，随后 Linux/Windows onefile 与真实 MCP smoke 通过。
- Windows Runtime target Red：run `32969775531` 已证明 `.exe`/MCP/用户级安装成功，但目标 Bootstrap 因 Windows 缺 IANA `Asia/Shanghai` 数据失败；固定 build/tools `tzdata==2026.3` 并要求使用该工具 Python 后，后续 Windows target install 全绿。
- Distribution Kit Verify Red：run `32970949023` 共 70 个测试，仅新增的 2 个 Kit 测试因为 `build_distribution_kit` 尚不存在而失败；其余旧测试和 Windows Runtime 通过，证明失败确实来自新能力未实现。
- Distribution Kit Green：run `32971575613` 70/70 测试通过；Linux 从构建、MCP、用户级安装到解压 Kit 无源目标安装全部通过，唯一失败为 Change 仍 `in_progress` 的预期 Ready Gate；Windows Job 整体 success。
- 最新 pre-ready 证据：run `32971926415` 在显式 Reference-ID digest 排序修复后，Linux build/MCP/user install/source target/Kit target 全部通过，只在 Change `in_progress` Ready Gate 失败；Windows Job整体 success。

# Completion Audit

- [x] upstream_re_read：完成前重新读取本轮用户“效果优先、允许本地 MCP、复杂规则必须原文进入 Codex Context、需要打包与使用方式”的决定，以及根 `AGENTS.md`、Coding 主规则、ref13/ref14、Docs/Review 规则和受影响 Runtime/安装/README 事实源；没有用历史假设替代当前仓库。
- [x] change_coverage：逐条对照 R1-R9。除原始 R1-R8 外，A1 反向审计发现“部门成员仍需私有源仓库才能给新项目安装”的遗漏并新增 R9；已经用 source-independent Runtime Kit 补齐，没有为了加密牺牲 Native Core、原文守恒、full 兼容、目标项目保护或使用/升级能力。
- [x] reverse_audit：完成 Source Reference → catalog/hash → AES-GCM → onefile → status/self-test → stdio MCP → canonical_text/SHA → Reference Stub → target AGENTS/Core，以及 Distribution Kit → payload file manifest → independent target installer → Bootstrap/rollback 两条正反链；同时从 Existing Full Install → Upgrade/Bootstrap/rollback 反向确认旧行为仍存在。
- [x] unresolved_cleared：R1-R9 均有实现与新鲜证据；Review `5030751931` 无 blocker。Kit metadata 公钥签名、多任务持久状态属于明确非目标且与当前威胁模型/权威门禁边界一致，不存在未说明的 not_satisfied/TODO/TBD。

# 实施任务

1. 先写 Bundle/catalog/crypto/RuntimeStore 行为测试，确认 Red；实现最小 runtime core 后转 Green。
2. 新增 MCP v2 stdio Server 和非 MCP `status/self-test` CLI；验证 manifest 不含正文、load_context 原文完整。
3. 新增 PyInstaller onefile builder，构建期临时生成 embedded payload；验证产物 digest 与源一致。
4. 新增 Runtime 用户级原子安装/升级；验证安装后 self-test 和失败回滚。
5. 扩展目标项目安装器为 `full|runtime` 双模式；先写 Runtime 分发/兼容/失败不触碰目标测试，再实现 stub 生成和 Runtime 预检。
6. 增量更新 AGENTS managed block、reference 13，并新增完整 reference 14；不压缩既有规则。
7. 更新 README / `.agents/README.md` / Runtime 文档的构建、安装、MCP 配置、项目接入、升级和安全边界。
8. 更新 CI paths/compile/CLI smoke/package smoke；运行完整自包含测试、真实 PyInstaller package 和真实 stdio MCP 验证。
9. Completion Audit 发现 source-independent 分发缺口后，先增加 2 个 Kit Red 用例，再实现 Distribution Kit、独立目标安装器和 Linux/Windows no-source CI。
10. 执行 A1/A2 和独立 Review；修复 PyInstaller 依赖边界、Windows tzdata、Distribution Kit、digest 显式排序 Finding，Review `5030751931` 无 blocker。
11. 当前 Change 已进入 `ready_for_review`；必须由这一 HEAD 触发的新鲜 Linux + Windows CI 全绿后才能把 PR #5 从 Draft 转 Ready。
12. 正常 PR 合并到 `main`，确认 main 新鲜 CI 后通过独立归档 PR 将本 Change 标记 `done` 并移入 archive。

# 文档影响

- 根 README：保留原安装/使用说明并增加 Runtime 分发入口。
- `.agents/README.md`：仓库内部 Skills/Runtime 分发边界。
- `runtime/README.md`：维护者构建、源仓库 runtime-mode、宿主注册、升级/回滚。
- `runtime/DISTRIBUTION.md`：部门使用者拿 Runtime Kit 后的 Windows/POSIX 安装、Codex/Cursor/Claude 配置、目标项目接入、升级与回滚。
- reference 13：现有 full 安装规则继续有效，增量增加 Runtime 模式导航与兼容说明。
- new reference 14：Runtime canonical-text、Bundle、Stub、MCP、安全和维护的详细规范源。
- `AGENTS.md` / managed block：维护本 Runtime 和目标项目读取 Runtime stub 时的强制入口。

# 交付

- Implementation Branch：`feature/local-mcp-skill-runtime`。
- Draft PR：`#5 增加本地 MCP 加密 Reference Runtime`。
- Independent Review：PR review `5030751931`，当前 HEAD 无阻断 Finding。
- Pre-ready CI：run `32971926415` 的 Linux 实现链与 Windows Job均通过；Linux 仅因当时 Change 仍为 `in_progress` 被 Ready Gate 正常阻断。
- Ready：本 Change 现已 `ready_for_review`，等待当前 HEAD 的新鲜永久 CI；全绿后才将 PR #5 转 Ready。
- Merge：未授权绕过 PR/CI；只在全绿和 Review 完成后正常合并。
- Change Archive：实现合并且 main 新鲜 CI 成功后使用独立归档 PR，完整保留本 Change 详细内容并将状态改为 `done`。
- Release：本任务提供可构建且已在 Linux/Windows Runner 验证的 Runtime artifact/Distribution Kit；是否创建正式 GitHub Release 不属于本轮成功标准，除非后续用户另行要求。
