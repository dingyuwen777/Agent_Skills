---
schema: coding-change/v1
id: "CHG-20260826-local-mcp-skill-runtime"
title: "Native Core Skill + 本地 MCP 加密 Reference Runtime"
level: L3
status: in_progress
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
  - "scripts/build_runtime.py"
  - "scripts/install_runtime.py"
  - "scripts/install.py"
  - "README.md"
  - ".agents/README.md"
  - "AGENTS.md"
  - ".github/workflows/skill-tests.yml"
contracts:
  - "Agent Skills Runtime Bundle v1"
  - "Agent Skills Runtime MCP stdio Tool Contract"
  - "Runtime Reference Stub v1"
  - "scripts/build_runtime.py CLI"
  - "scripts/install_runtime.py CLI"
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

# 可观察成功标准

- [ ] 源仓库现有 `.agents/skills/{coding,review,docs}/references/*.md` 继续作为唯一 canonical 规则正文，不迁移到 Policy DSL，不自动摘要。
- [ ] 新增确定性 Bundle Builder，收集三个 Skill 的 Reference 原始 UTF-8 内容、路径、稳定 ID、SHA256、size，生成可验证的 `source_digest`；输入内容不改写。
- [ ] Bundle 使用 authenticated encryption 加密并在构建产物中嵌入；目标用户无需单独获得明文 Reference 文件或解密 key 文件。
- [ ] 新增本地 stdio MCP Runtime，至少暴露 `agent_skills_manifest`、`agent_skills_load_context`、`agent_skills_start_task`、`agent_skills_checkpoint`、`agent_skills_status`；不暴露任意路径读取接口。
- [ ] `agent_skills_load_context` 返回命中 Reference 的 canonical 原文和 hash，不做 LLM 总结、改写或规则抽取；Runtime manifest 不泄露正文。
- [ ] Runtime 维护当前 task/phase 已加载 Reference 状态，`checkpoint` 能明确报告 required / loaded / missing，阶段切换可继续加载规则但不替代 Codex 的自然语言路由判断。
- [ ] `scripts/build_runtime.py` 可使用当前仓库 canonical References 构建当前平台单文件可执行产物，并在构建完成后运行 `status` / `self-test` 验证 bundle 与当前 source digest 一致。
- [ ] `scripts/install_runtime.py` 可把构建好的 Runtime 原子安装/升级到用户级目录，安装后执行 `status` / `self-test`；失败恢复旧版本。
- [ ] `scripts/install.py` 保持现有 `python scripts/install.py --target ...` 行为兼容，默认仍为 `full`；新增显式 `--mode runtime`，只有 Runtime 自检和 source digest 匹配后才修改目标项目。
- [ ] Runtime 模式安装仍保留 Core `SKILL.md`、必要 assets/agents/scripts，并为每个 canonical Reference 生成同名 stub；目标项目中不出现 Reference 原始正文，现有 `SKILL.md` 相对链接仍能命中 stub。
- [ ] Stub 包含稳定 Runtime ID 和 expected SHA256，并明确要求在执行该 Reference 对应动作前调用 `agent_skills_load_context`；MCP 不可用、Reference 不存在或 hash 不一致时不得凭印象继续。
- [ ] 目标项目已有 `.agents/changes/`、项目自有 Skill、AGENTS marker 外内容和其他 `.agents` 内容继续受到现有安装/回滚保护。
- [ ] README、`.agents/README.md`、reference 13/14 和 AGENTS managed block 清楚说明如何构建、安装 Runtime、配置 MCP、首次接入目标项目、重复升级、full/runtime 两种模式和真实安全边界。
- [ ] CI 对 Runtime 源码、Bundle/crypto/store、Runtime 模式安装、原文守恒、CLI smoke 和 PyInstaller package smoke 提供新鲜证据；现有 Bootstrap/Change/Review/Docs/portability 测试不回归。

# 范围

- 新增 Runtime Bundle catalog、authenticated encryption、内嵌 payload 加载、状态存储和 MCP stdio Server。
- 新增当前平台 Runtime 单文件构建脚本与用户级安装/升级脚本。
- 在现有项目安装器中增加 opt-in Runtime 分发模式，默认 full 模式保持兼容。
- 新增 Reference Stub 生成和 source digest / Runtime artifact 匹配校验。
- 只对 Core Skill、managed block、安装 reference、README、CI 做实现 Runtime 所需的增量规则补充。
- 新增自包含单元/集成测试和真实 package smoke。

# 非目标

- 不把现有 Reference 自然语言重写成 Policy DSL、布尔规则或自动摘要。
- 不在第一版自动把任意自然语言任务全部路由成固定 Reference 列表；Codex 继续依据 Core Skill 和当前项目事实执行现有语义路由。
- 不把本地 MCP 描述成能够阻止机器 Owner 提取运行时明文的强保密系统。
- 不增加远程 Policy Server、OAuth、License Server、KMS 或服务器侧 LLM。
- 不让 MCP 任意读取目标仓库文件，也不把它重新实现成第二个 Coding Agent。
- 不删除现有 full Markdown 分发模式；已有用户可以继续使用当前安装命令。
- 不修改 `coding-change/v1` schema。
- 不改变项目事实来自目标仓库 Overlay/代码/Contract/运行证据的原则。

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

## Bundle 与加密边界

第一版使用 AES-256-GCM authenticated encryption。随机 32-byte key 与随机 nonce 只用于构建产物；构建时生成的 Python payload module 只存在临时构建目录，不提交 Git。单文件可执行产物同时包含解密所需 key 和 ciphertext，因此这一层只用于提高直接浏览/复制门槛，不是对本机管理员的可信执行环境。

Bundle `source_digest` 由排序后的 Reference ID、source path、SHA256 和 size 计算。目标项目 Runtime 安装模式在任何写入前比较当前源仓库计算的 digest 与 Runtime `status` 返回 digest；不匹配即拒绝，避免旧 Runtime 与新 stub/Reference hash 混装。

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

新的 Runtime 模式必须显式提供 Runtime command：

```bash
python scripts/install.py --mode runtime --runtime-command <agent-skills-mcp> --target <target>
```

Runtime 模式只在自检/digest 校验成功后切换目标受管 Skill。现有暂存、逐 Skill backup、失败回滚、Bootstrap 失败回滚继续复用。

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
→ dist/agent-skills-mcp[.exe] + manifest JSON
```

Runtime 是平台相关可执行文件；Windows 必须在 Windows 上构建 `.exe`，Linux/macOS 同理。用户级 Runtime 安装路径与目标项目解耦，升级 Runtime 后项目只需在 canonical source/stub 版本变化时再次执行 Runtime 模式项目安装以刷新 Core/stub/managed block。

## 回滚

- Runtime Build 不修改 canonical References。
- `install_runtime.py` 在替换用户级 Runtime 前保留旧版本；新版本 `status` / `self-test` 失败时恢复旧文件。
- `install.py --mode runtime` 在修改目标项目之前先验证 Runtime；Skill 切换和 Bootstrap 失败继续沿用现有多目录 rollback。
- 回滚到旧 Runtime 时，必须同时使用与该 Runtime `source_digest` 匹配的 Agent_Skills source/stub 版本；digest 不一致时安装器拒绝制造混合状态。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 保持现有完整 Skill 对 Codex 推理的效果，复杂 Reference 不压缩成布尔或摘要 | user:execution-effect-first | not_satisfied | 待实现 canonical 原文 Bundle + `agent_skills_load_context` 原文守恒测试 |
| R2 | 本地分发时不在目标项目明文放置完整 Reference，但不要求对机器 Owner 强保密 | user:local-mcp-protection-boundary | not_satisfied | 待实现 Runtime stub 分发、AES-GCM Bundle 与明文缺失测试 |
| R3 | 保留 Native Core Skill，让现有触发/路由继续指导 Agent，而不是纯 MCP 替代 Skill | user:native-core-plus-mcp | not_satisfied | 待验证 Runtime 模式 Core SKILL 原样复制、同名 stub 接回现有引用 |
| R4 | MCP 必须能把命中 Reference 原文传给本地 Codex 上下文 | user:read-skill-context-equivalence | not_satisfied | 待实现 `load_context` Tool Contract 和 RuntimeStore exact-text 测试 |
| R5 | 告诉用户如何打包、安装、配置和升级 | user:package-and-use | not_satisfied | 待更新 README / `.agents/README.md` / reference 14，并验证公开 CLI |
| R6 | 现有 full 安装方式和目标项目保护边界不得被静默破坏 | existing:reference-13 | not_satisfied | 待保留默认 full 模式并运行既有安装/Bootstrap 回归 + Runtime 模式回滚测试 |
| R7 | 原始 Skill/reference 高价值语义不得因本功能被总结、重写或丢失 | AGENTS.md:content-preservation | not_satisfied | 待通过 canonical source compare/hash、diff Review 和回归测试证明 |
| R8 | 代码、Git、时间、日志与交付遵守 Agent_Skills 全局硬规则及 CI/PR 门禁 | AGENTS.md | not_satisfied | 待完成函数中文 docstring、中文 commits、新鲜 CI、独立 Review、PR 合并和 Change 归档 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | catalog ID/hash/digest、AES-GCM roundtrip/tamper、RuntimeStore manifest/load/start/checkpoint、stub 生成和 digest mismatch 行为 |
| 接口 / Contract | required | MCP 五个稳定 Tool 名称/参数/返回结构、Bundle schema、Runtime stub、build/install/runtime-mode CLI 直接测试或 smoke |
| 集成 / Persistence / Runtime Dependency | required | 临时文件系统真实安装/升级/backup/rollback、Runtime subprocess `status/self-test`、目标 Runtime 模式分发，不以 Mock 冒充 filesystem/process |
| 用户 / Workflow Acceptance | required | canonical source → build bundle → Runtime self-test/load → 全局安装 → 目标 Runtime 模式安装的可重复命令和用户文档；至少通过真实 CLI/package smoke 验证关键链 |
| 跨组件 Golden Path | required | Source Reference → encrypted embedded bundle → onefile Runtime → MCP/runtime context loader → exact canonical text + target stub hash 的关键链 |
| 外部依赖 Probe | not_applicable | Runtime 为本地 stdio MCP，无付费 Provider、远端 API、生产资源或真实外部系统；PyPI 依赖安装属于 Build 依赖，不是产品外部运行边界 |
| Build / Package / Runtime | required | 当前 CI 平台执行 PyInstaller onefile 构建，运行可执行文件 `status --json` / `self-test --json`；README 明确 Windows `.exe` 必须在 Windows 构建 |
| Docs / Governance / Other | required | reference 13/14、README、`.agents/README.md`、AGENTS/managed block、Change Traceability/Completion Audit 与 CI path/compile/smoke 同步 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取本轮用户决定、根 `AGENTS.md`、reference 13/14 和受影响 Core Skill/README 事实源。
- [ ] change_coverage：逐条对照 R1-R8，确认没有为了“加密”漏掉执行效果、原文守恒、兼容、打包和使用要求。
- [ ] reverse_audit：从 Source Reference → Bundle → Encryption → Runtime → MCP Context → Stub/Target install，以及从 Existing Full Install → Upgrade/Bootstrap/rollback 两个方向反向审计。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零；延期/不适用均有依据；无 TODO/TBD 占位证据。

# 实施任务

1. 先写 Bundle/catalog/crypto/RuntimeStore 行为测试，确认 Red；实现最小 runtime core 后转 Green。
2. 新增 MCP v2 stdio Server 和非 MCP `status/self-test` CLI；验证 manifest 不含正文、load_context 原文完整。
3. 新增 PyInstaller onefile builder，构建期临时生成 embedded payload；验证产物 digest 与源一致。
4. 新增 Runtime 用户级原子安装/升级；验证安装后 self-test 和失败回滚。
5. 扩展目标项目安装器为 `full|runtime` 双模式；先写 Runtime 分发/兼容/失败不触碰目标测试，再实现 stub 生成和 Runtime 预检。
6. 增量更新 Core Skill、AGENTS managed block、reference 13，并新增完整 reference 14；不压缩既有规则。
7. 更新 README / `.agents/README.md` 的构建、安装、MCP 配置、项目接入、升级和安全边界。
8. 更新 CI paths/compile/CLI smoke/package smoke；运行完整自包含测试和真实 PyInstaller package 验证。
9. 执行 Completion Audit、A1/A2 和独立 Review；修复 Findings 后取得 `ready_for_review` 下新鲜 CI。
10. 正常 PR 合并到 `main`，确认 main 新鲜 CI 后通过独立归档 PR 将本 Change 标记 `done` 并移入 archive。

# 文档影响

- 根 README：用户构建/安装/使用入口。
- `.agents/README.md`：仓库内部 Skills/Runtime 分发边界。
- reference 13：现有 full 安装规则继续有效，增加 Runtime 模式导航与兼容说明。
- new reference 14：Runtime 的唯一详细规范源。
- `AGENTS.md` / managed block：维护本 Runtime 和目标项目读取 Runtime stub 时的强制入口。

# 交付

- Implementation Branch：`feature/local-mcp-skill-runtime`。
- PR：待实现/验证后创建 Draft，再按 Change/Review/CI 门禁转 Ready。
- Merge：未授权绕过 PR/CI；只在全绿和 Review 完成后正常合并。
- Change Archive：实现合并且 main 新鲜 CI 成功后使用独立归档 PR。
- Release：本任务提供可构建本地 Runtime artifact；是否创建 GitHub Release 不属于本轮成功标准，除非后续用户另行要求。
