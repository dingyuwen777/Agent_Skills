# Agent_Skills 仓库维护规范

本仓库维护可复制到不同软件项目中的通用 Agent Skills。这里的规则用于**开发和维护 Agent_Skills 本身**，不是任何业务项目的架构、技术栈或产品约束。

先记住一条原则：**通用 Skill 规定“怎样可靠工作”，目标项目规定“这个项目具体是什么”。** 不得把某个项目的语言、框架、数据库、目录、业务流程、Provider、Stage、CI Job、部署拓扑或文档编号冒充通用事实。

## 1. 开始前

处理本仓库的分析、设计、实现、Review、测试、Git 或交付前：

1. 先读本文件；
2. 读取 `.agents/skills/coding/SKILL.md`，按其任务路由执行；
3. 修改 Coding Skill 时，只读取本次受影响的 references、脚本、模板、Agent metadata 和测试；
4. 修改 Review 或 Docs Skill 时，分别读取对应 `SKILL.md` 与直接相关 references；
5. 不从历史聊天或其他业务仓库猜当前实现，以本仓库当前文件和本轮验证为准；
6. 规则重组、通用化、拆分、合并或改名时，必须保持仍有效的触发条件、例外、失败处理、验证责任、安全与兼容边界；不得为了缩短文本把多条可执行规则压成一句抽象原则；
7. 本仓库不保存任何目标项目的 `.agents/project-context.json`；该文件是目标项目本地可失效导航缓存，应由目标项目 `.gitignore` 忽略。

## 2. 本仓库的长期边界

当前正式 Skills：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

职责：

```text
Coding
→ 通用研发、调试、验证、Git 和交付工作流

Review
→ 独立代码审查、Findings 和测试充分性验证

Docs
→ 技术文档事实同步、审查、编写和更新
```

Review 不维护第二套 Coding 规范；Docs 不复制 Coding 的研发规则。Coding 在适用时负责路由到 Review/Docs。

目标项目正式分发边界仍然只有上述三个 Skill。根 `scripts/install.py` 是 Agent_Skills 源仓库的分发/升级入口，不意味着目标项目应复制本仓库根 `AGENTS.md`、`.agents/changes/` 或其他仓库维护状态。目标项目 Overlay 的安装与 `AGENTS.md` Bootstrap 规则由 `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` 和对应 assets 定义。

## 3. 通用核心与项目 Overlay

通用 Skill 可以强制跨项目工作方式，但不能伪造项目事实。

### 通用核心必须保留

包括但不限于：

- 当前仓库事实优先；
- 权限边界和用户工作保护；
- 不静默升级依赖、切换技术路线、改变公共兼容语义或扩大范围；
- L1/L2/L3 风险分级；
- Requirement Traceability、Validation Matrix、Completion Audit；
- Red → Verify Red → Green → Refactor → Re-verify；
- 根因调试和连续三次失败假设后的停止条件；
- 按真实边界选择 Contract、Integration、Workflow、Golden Path、External Probe、Build/Package/Runtime 证据；
- 多人/多 Agent 冲突预检；
- Docs Impact；
- 独立 Review；
- 新鲜证据门禁；
- Git/CI/Branch Protection/Release/回滚边界。

### 用户定义的全局工程硬规则

以下规则是本 Skill 作者明确要求的跨项目硬规则，不属于任何业务项目残留，通用化时不得删除或降级：

1. 代码注释统一使用中文；专有名词、标识符、协议、库、标准名以及必须原样保留的外部文本除外；
2. 所有新增或修改的函数都必须有函数级中文注释或文档注释，包括 public/exported 与 internal/private/helper；
3. Git 提交信息统一使用中文；
4. Agent 自有或默认解释的时间统一使用北京时间 `Asia/Shanghai`（UTC+8）；外部协议/既有 Contract 明确其他时区时保留原始语义，在人类展示边界转换；
5. 除更高优先级外部 wire-format Contract 强制其他序列化形式外，人类可读日志统一使用 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`；结构化日志必须提供等价的北京时间、source、line、level 字段。

### 必须留在目标项目 Overlay 的内容

例如：

- 某个 Python/Node/Go/Rust/JVM/.NET/C++ 版本；
- FastAPI、Spring、Vue、React、PostgreSQL、MySQL、Redis 等实际技术选型；
- 业务表、字段、Provider、Prompt、外部平台；
- 具体 `docs/` 目录、Blueprint/Roadmap/ADR 编号；
- 目标项目 CI Job、Branch Ruleset、Release 流程；
- 项目自己的架构、Owner、Contract、Migration、运行和部署方式。

这些事实只能来自目标仓库当前 `AGENTS.md`、`CONTRIBUTING`、README、Spec/ADR、Manifest、locks、Contract/Schema/Migration、代码、测试和 CI。

目标项目没有 `AGENTS.md` 时，可以通过当前安装器/Bootstrap 建立项目 Overlay 初版；已有 `AGENTS.md` 时只能在稳定 managed markers 内增量接入 Agent Skills，marker 外项目原文必须保持。Bootstrap 只可以记录实际发现的事实入口作为导航，不能把文件名推断成框架、数据库或架构事实。

## 4. Change 与治理载体

本仓库当前 Coding Change schema 为：

```text
coding-change/v1
```

不兼容、不读取、不迁移任何历史 Change schema；新文件只使用当前 `coding-change/v1`。

Coding 的 Requirement Traceability、Validation Matrix、Completion Audit 是通用语义；承载位置不是所有项目的固定架构。

- 目标项目已有可承载这些语义的正式 Change/RFC/Spec/OpenSpec/Issue 流程时，优先使用目标项目现有机制；
- Coding 自带 CLI 只管理 Coding Change 文档，不擅自改写任意第三方治理格式；
- 需要 Coding 自带载体时，默认使用 `.agents/changes/`；
- 目标项目已经存在受支持的顶层 `changes/active` / `changes/archive` 时可继续使用；
- 发现已有治理机制但无法无损映射时，不能静默再造一套平行治理；应先明确 carrier 或使用项目原生机制。

## 5. 开发与测试

本仓库的 Skill 修改本身至少要验证：

- 所有 Markdown/YAML/Python 文件可读；
- Coding CLI 的 `bootstrap/discover/status/conflicts/new-change` 入口可运行；
- `scripts/install.py` 可在临时目标项目完成三个受管 Skill 的首次安装和重复升级，且不删除目标项目 `.agents/changes/`、项目自有 Skill 或其他 `.agents` 内容；
- 安装器拒绝把目标项目设为 Agent_Skills source 自身或 source 内部后代目录，避免递归复制、源树污染或无界磁盘增长；正常 sibling/外部目标继续可安装；
- Bootstrap 在无 `AGENTS.md`、已有 `AGENTS.md`、已有 managed block、坏 marker、LF/CRLF 和 `.gitignore` 幂等场景都保留用户内容并按 Contract 工作；
- `ready_check.py` 的 schema、Traceability、Completion Audit 和 Change root 行为正确；
- portability 测试证明不同语言/项目形态不会被反向推断成固定 Web/Python/PostgreSQL 项目；
- preservation 测试证明 Coding 主规则结构调整后，全局不变量、停止条件、Review/Docs 硬路由以及迁移到 references 的详细规则仍可达且没有语义降级；
- 任一业务项目名称、业务源码路径、具体 Provider/平台或项目级 Blueprint/Stage 事实不出现在通用 live 规则或自包含测试中；
- 用户定义的五项全局工程硬规则仍可从 Coding 主规则和完成前 Review 到达；
- 删除/改名 reference 后没有 live 引用残留；
- README、`FULL_DISTRIBUTION.md`、`runtime/DISTRIBUTION.md`、`RELEASING.md` 与实际文件路径、CLI、安装/Bootstrap、Release 和缓存策略一致；
- Full Kit 解压后的 `README.md` 来自 `FULL_DISTRIBUTION.md`，Runtime Kit 解压后的 `README.md` 来自 `runtime/DISTRIBUTION.md`；不得把只在源仓库存在的维护者命令原样当成 Kit 用户入口；
- CI 的 path filters 和编译/测试命令真实覆盖根 `scripts/install.py`、Full Kit Builder、Runtime Builder、两个分发说明和所有永久 Workflow，不能出现发布/安装能力只在本地存在而不进永久门禁。

测试必须自包含。禁止让 Agent_Skills 自己的单元测试依赖另一个业务仓库才存在的 Blueprint、backend、workflow 或脚本。

## 6. Git 与交付

- 修改前确认当前 `main` HEAD，重要修改从最新 `main` 创建专用分支；
- 不覆盖、回滚或混入无关用户修改；
- 禁止强制推送、`git reset --hard`、`git clean -fd` 和共享历史重写；
- 提交信息使用中文；
- 重要规则/脚本变化先完成本轮新鲜验证和 Review，再创建 PR；
- 不绕过 Branch Protection、CI 或仓库已有门禁；
- PR 合并后再确认 `main` 指向预期提交；若本次使用了 Coding Change，最终归档状态必须与实际合并结果一致。

## 7. 完成报告

交付至少说明：

- 变更摘要；
- 逐文件/按类别目的；
- 哪些项目特定内容被移出通用核心；
- 用户定义的全局硬规则是否完整保留；
- Change schema / carrier / cache 策略变化；
- 实际运行的测试、命令、退出码和结果；
- 未验证内容及风险；
- Git 分支、提交、PR、CI、合并和归档状态。

禁止只回复“已完成”或“测试通过”。

## 8. 本地 MCP Runtime 维护边界

当任务涉及 `runtime/`、`scripts/build_runtime.py`、`scripts/install_runtime.py`、`scripts/runtime_mcp_smoke.py`、`scripts/install.py --mode runtime`、Reference Stub、Bundle/加密格式或 MCP Tool Contract 时，在 Coding 主规则和直接相关开发/验证规则之外，还必须读取 `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md`。

Runtime 是三个正式 Skill 的**可选分发通道**，不是第四个 Skill，也不是第二套研发规则源。维护时必须保持：

- 源仓库 `coding/review/docs` 的 `SKILL.md` 与 canonical `references/*.md` 仍是唯一完整自然语言规则事实源；
- Runtime 不把复杂 Reference 自动摘要、重写成 Guidance、Policy DSL 或布尔判断；
- `full` 安装模式继续保持现有完整 Markdown 分发语义；
- `runtime` 模式保留 Native Core `SKILL.md`，详细 Reference 只分发同名 stub，并由本地 MCP `agent_skills_load_context` 返回 canonical 原文；
- Source Reference bytes → Bundle hash/content → 解密结果 → MCP `canonical_text` 必须有逐字守恒证据；
- Bundle 加密/onefile 只作为普通防浏览/复制能力，不宣称能够抵御机器 Owner、调试器、内存转储或专业逆向；
- Runtime/source digest 不匹配时必须在修改目标项目之前失败，不能制造旧 Runtime 与新 Stub 的混装状态；
- Runtime build 必须验证最终平台 artifact，而不只验证 Python 模块；永久 CI 至少覆盖 onefile `status/self-test`、真实 stdio MCP `tools/list`/`tools/call` 和 runtime-mode 临时目标项目安装；
- Windows `.exe`、Linux、macOS artifact 分别在对应目标平台构建/验证，不把 PyInstaller onefile 当作跨平台产物。

## 9. 版本与正式 Release 维护边界

根 `VERSION` 是 Agent_Skills 正式产品版本的唯一事实源。修改 VERSION、Full Distribution Kit、Runtime Release metadata、Release asset、tag 或 `.github/workflows/release.yml` 时，必须把它视为 Build / Package / Release Contract 变化并读取 Coding 的 Git/Release 与永久 Workflow 规则。

正式 Release 至少保持：

- SemVer `VERSION` → `v<VERSION>` tag 一一对应；
- Release 只通过 GitHub Actions 的 `workflow_dispatch` 手工运行；维护者必须从 `main` 输入 `v<VERSION>`，Workflow 校验 tag 与根 `VERSION` 一致后再自动创建该 tag 和 GitHub Release；不得因 `VERSION` push 自动发布，也不得提前手工创建同名 tag；
- Full Kit 只携带三个完整 Skill、安装器、版本和必要用户资料，不携带源仓库根 `AGENTS.md`、`.agents/changes/`、`project-context.json` 或其他仓库维护状态；
- Linux / Windows / macOS Runtime Kit 分别在对应平台构建和验证；
- Runtime manifest / Kit metadata 可以记录 `release_version`，但不能把版本号替代 canonical Reference `source_digest` / SHA256 完整性；
- 正式 Release asset 至少包含版本化 Full Kit、三平台 Runtime Kit 和 `SHA256SUMS`；
- Release Workflow 的 Preflight/构建 Job 只读；只有全部 Release Candidate 构建/测试成功后，最终 Publish Job 才能获得 `contents: write`；
- 已存在同版本 tag/Release 时拒绝覆盖或移动历史事实；修复使用新 VERSION；
- 正式资产必须由合并后的 `main` SHA 重新构建，不把 PR 临时产物直接发布；
- 永久 `Skill Tests` 与 Release Workflow 分别承担持续回归和实际发布候选验证，任何 Workflow 精简都要按 Evidence Preservation Mapping 证明独立责任没有丢失。

维护者完整流程见 `RELEASING.md`，Full Kit 用户入口见 `FULL_DISTRIBUTION.md`，Runtime Kit 用户入口见 `runtime/DISTRIBUTION.md`，当前版本变化见 `CHANGELOG.md`。Release 完成结论必须核对真实 GitHub tag、Release、资产和 checksum；只看到 Workflow YAML 或本地 `dist/` 不足以宣称发布成功。
