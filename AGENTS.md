# Agent_Skills 仓库维护规范

本仓库维护可复制到不同软件项目中的通用 Agent Skills。这里的规则用于**开发和维护 Agent_Skills 本身**，不是任何业务项目的架构、技术栈或产品约束。

先记住一条原则：**通用 Skill 规定“怎样可靠工作”，目标项目规定“这个项目具体是什么”。** 不得把某个项目的语言、框架、数据库、目录、业务流程、Provider、Stage、CI Job、部署拓扑或文档编号冒充通用事实。

## 1. 开始前

处理本仓库的分析、设计、实现、Review、测试、Git 或交付前：

1. 先读本文件；
2. 读取 `.agents/skills/coding/SKILL.md`，按其任务路由执行；
3. 修改 Coding Skill 时，只读取本次受影响的 references、脚本、模板、Agent metadata 和测试；
4. 修改 Review、Docs 或 Figma Skill 时，分别读取对应 `SKILL.md` 与直接相关 references；Figma 规则发生迁移、通用化或 Ownership 调整时还必须读取 Coding 的规则内容守恒 reference；
5. 不从历史聊天或其他业务仓库猜当前实现，以本仓库当前文件和本轮验证为准；
6. 规则重组、通用化、拆分、合并或改名时，必须保持仍有效的触发条件、例外、失败处理、验证责任、安全与兼容边界；不得为了缩短文本把多条可执行规则压成一句抽象原则；
7. 本仓库不保存任何目标项目的 `.agents/project-context.json`；该文件是目标项目本地可失效导航缓存，应由目标项目 `.gitignore` 忽略。

## 2. 本仓库的长期边界

当前仓库实际存在的正式 Skills：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
.agents/skills/figma/
```

职责：

```text
Coding
→ 通用研发、调试、验证、Git 和交付工作流

Review
→ 独立代码审查、Findings 和测试充分性验证

Docs
→ 技术文档事实同步、审查、编写和更新

Figma
→ 通用 Figma 设计事实、Canvas/Prototype、可用性、真实系统能力映射、设计修复、Ready 验收和 Design-to-Code 实施交接
```

Review 不维护第二套 Coding 规范；Docs 不复制 Coding 的研发规则；Figma 不复制 Coding 的 Change/TDD/CI/Git 研发规则，Coding 也不维护第二套 Figma Canvas/Spacing/Annotation/Prototype 详细规则。Coding 在适用时负责路由到 Review/Docs/Figma；Figma 达到 `READY / READY_WITH_NOTES` 后再把已确认设计事实交回 Coding 进入真实实现。

**当前四个目录只是当前仓库事实，不是分发代码里的永久全量名单。** 正式可分发 Skill 必须从：

```text
.agents/skills/*/SKILL.md
```

动态发现。未来新增合法正式 Skill 后，Runtime、Project Payload、源安装器、Full Kit、manifest、永久 CI 和 Release 不得要求再手工维护 Skill 名称列表。

目标项目真正的分发边界是“当前 Release 动态发现的全部正式 Skill”，不意味着目标项目应复制本仓库根 `AGENTS.md`、`.agents/changes/` 或其他仓库维护状态。目标项目 Overlay 的安装与 `AGENTS.md` Bootstrap 规则由 `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` 和对应 assets 定义；项目级单 binary Runtime、动态 Skill/Project Payload/Reference Stub 规则由 Reference 14 定义。

仓库文档按读者职责分层：

```text
README.md
→ Agent_Skills 仓库总入口、安装与导航

docs/distribution/
→ 分发最终用户说明；runtime-kit.md 当前保留路径但内容是 Runtime binary 用户说明

docs/maintainers/
→ Agent_Skills 维护者流程

runtime/README.md
→ Runtime 源码、构建与本地调试维护说明

.agents/README.md
→ .agents 目录导航，不复制仓库总教程或 Skill 正式规则
```

不要把不同读者的完整教程重复维护在多个 README 中。Full Kit 内需要的 `README.md` 由 Builder 从 `docs/distribution/full-kit.md` 生成；Runtime 正式团队 Release 只有平台 binary 和 checksum，不再依赖 Runtime Kit ZIP 内 README。源码维护说明不能冒充最终用户说明。

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
- Figma 设计任务的事实恢复、Prototype/Canvas 审查、Ready 门禁和 READY 后 Coding Handoff；
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
- 项目自己的架构、Owner、Contract、Migration、运行和部署方式；
- 项目自己的品牌、设计 Token、页面基准尺寸、业务组件、菜单、Prototype 数据、动态字段和产品术语。

这些事实只能来自目标仓库当前 `AGENTS.md`、`CONTRIBUTING`、README、Spec/ADR、Design Guide/Design System、Manifest、locks、Contract/Schema/Migration、代码、测试、CI 和当前正式 Figma 事实。

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
- 正式 Skill Catalog 从 `.agents/skills/*/SKILL.md` 动态发现合法 Skill，不维护固定全量名单；新增一个合法测试 Skill 后能自动进入 Reference Bundle、Project Payload、安装结果和公开 manifest；
- 当前正式 `figma` Skill 也必须通过同一动态 Catalog 自动进入 Reference Bundle、Project Payload、Full/source 安装、Runtime 项目安装和 ownership manifest，不能为第四个 Skill 新增静态分发名单；
- `scripts/install.py` 可在临时目标项目完成当前动态正式 Skill 的首次安装和重复升级，且不删除目标项目 `.agents/changes/`、项目自有 Skill 或其他 `.agents` 内容；
- 安装器拒绝把目标项目设为 Agent_Skills source 自身或 source 内部后代目录，避免递归复制、源树污染或无界磁盘增长；正常 sibling/外部目标继续可安装；
- Bootstrap 在无 `AGENTS.md`、已有 `AGENTS.md`、已有 managed block、坏 marker、LF/CRLF 和 `.gitignore` 幂等场景都保留用户内容并按 Contract 工作；
- Bootstrap/managed block 能把 Figma 创建、修改、审查、Prototype、Ready 和 Figma-to-code 场景路由到正式 Figma Skill，并保持 `NOT_READY` 不进入生产实现、READY 后返回 Coding 的职责边界；
- Runtime Project Payload 不分发 canonical Reference 正文；Stub 的 Runtime ID / Expected SHA256 与加密 Bundle 对应；Project Payload path/hash/size/mode 和 `payload_digest` 有机器验证；
- 单 binary 项目安装使用 `.agents/agent-skills-install.json` 区分 Agent_Skills ownership 与项目自有 Skill；首次未认领同名 Skill 冲突 fail closed；新 Release 删除 Skill 时只删除旧 manifest 明确认领项；
- 项目 Runtime 安装在 `.agents/runtime/agent-skills-mcp[.exe]`，目标项目 `.gitignore` 增量忽略该 Runtime；Codex/Cursor/Claude Code 只配置项目级 MCP，并保留宿主其他用户配置；
- `ready_check.py` 的 schema、Traceability、Completion Audit 和 Change root 行为正确；
- portability 测试证明不同语言/项目形态不会被反向推断成固定 Web/Python/PostgreSQL 项目；Figma portability 还必须证明 Design-only、Static、Web/Full-stack、Mobile/Desktop、Dashboard、Design System 等形态不会被强制套用不存在的 API/数据库/Browser 边界；
- preservation 测试证明 Coding 主规则结构调整后，全局不变量、停止条件、Review/Docs/Figma 硬路由以及迁移到专门 Skill/references 的详细规则仍可达且没有语义降级；
- Figma 内容守恒测试至少覆盖 Canvas/Section/Spacing/Annotation、Prototype、Owner、状态、`READY / READY_WITH_NOTES / NOT_READY`、失败处理、Fresh Screenshot/Machine Audit 和写后 Canvas-level Review；
- 任一业务项目名称、业务源码路径、具体 Provider/平台或项目级 Blueprint/Stage 事实不出现在通用 live 规则或自包含测试中；
- 用户定义的五项全局工程硬规则仍可从 Coding 主规则和完成前 Review 到达；
- 删除/改名 reference 后没有 live 引用残留；
- `README.md`、`docs/distribution/full-kit.md`、`docs/distribution/runtime-kit.md`、`docs/maintainers/releasing.md`、`runtime/README.md` 与实际文件路径、CLI、安装/Bootstrap、动态 Skill、Release 和缓存策略一致；
- Full Kit 解压后的 `README.md` 来自 `docs/distribution/full-kit.md`，并能脱离源仓库安装全部动态正式 Skill；Runtime 最终用户说明来自 `docs/distribution/runtime-kit.md`，但正式团队 Release 不再构建 Runtime Kit ZIP；
- Runtime build 必须验证最终平台 artifact，而不只验证 Python 模块；永久 CI 至少覆盖 onefile `status/self-test`、真实 stdio MCP、真实临时项目单 binary 安装、重复升级、无参数当前目录安装和项目内 Runtime MCP smoke；
- Windows `.exe`、Linux、macOS artifact 分别在对应目标平台构建/验证，不把 PyInstaller onefile 当作跨平台产物；
- CI 的 path filters 和编译/测试命令真实覆盖根 `scripts/install.py`、Full Kit Builder、Runtime Builder、动态 Skill/Project Payload/Installer、`docs/distribution/`、`docs/maintainers/` 和所有永久 Workflow，不能出现发布/安装能力只在本地存在而不进永久门禁。

测试必须自包含。禁止让 Agent_Skills 自己的单元测试依赖另一个业务仓库才存在的 Blueprint、backend、workflow 或脚本。Figma preservation 测试也必须以当前仓库正式 Figma Skill 为事实源，不运行时依赖 AIMA_UGC。

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
- Figma 内容守恒与跨 Skill Ownership 是否完整保留；
- Change schema / carrier / cache 策略变化；
- 实际运行的测试、命令、退出码和结果；
- 未验证内容及风险；
- Git 分支、提交、PR、CI、合并和归档状态。

禁止只回复“已完成”或“测试通过”。

## 8. 本地 MCP Runtime 维护边界

当任务涉及 `runtime/`、`scripts/build_runtime.py`、`scripts/runtime_mcp_smoke.py`、Project Payload、Project Installer、动态 Skill Catalog、Reference Stub、Bundle/加密格式、MCP Tool Contract、项目宿主 MCP 配置，或历史兼容 `scripts/install.py --mode runtime` / `scripts/install_runtime*.py` 时，在 Coding 主规则和直接相关开发/验证规则之外，还必须读取 `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md`。

Runtime 是**当前正式 Skill 集合的项目级分发通道**，不是一个新的业务 Skill，也不是第二套研发规则源。维护时必须保持：

- 源仓库每个正式 Skill 的 `SKILL.md` 与 canonical `references/*.md` 仍是对应 Skill 的唯一完整自然语言规则事实源；
- 正式 Skill 集合通过 `.agents/skills/*/SKILL.md` 动态发现，Runtime/Builder/Installer/Release 不维护固定全量名单；
- Runtime 不把复杂 Reference 自动摘要、重写成 Guidance、Policy DSL 或布尔判断；
- Full/source 安装继续保持完整 Markdown 分发语义，但最终团队 Runtime 用户不需要访问源仓库或 Python；
- Runtime onefile 内嵌 Native Core/运行资产 Project Payload 与加密 canonical Reference Bundle；目标项目 Reference 只分发同名 Stub，并由项目 MCP `agent_skills_load_context` 返回 canonical 原文；
- Source Reference bytes → Bundle hash/content → 解密结果 → MCP `canonical_text` 必须有逐字守恒证据；
- Project Payload 独立维护 `payload_digest`，不能用 Reference `source_digest` 代替 Core/资产完整性；
- Bundle 加密/onefile 只作为普通防浏览/复制能力，不宣称能够抵御机器 Owner、调试器、内存转储、进程 Hook 或专业逆向；
- 最终用户无参数运行 binary 默认安装/升级当前项目，Runtime 固定进入 `.agents/runtime/`；不得把用户级/全局 Runtime 恢复成推荐前置步骤；
- 项目安装必须使用 managed installation manifest 保护项目自有 Skill；同名未认领冲突 fail closed；
- Codex/Cursor/Claude Code 的接入只写项目级配置并遵守宿主 trust/approval，不绕过宿主安全机制；
- Runtime build 必须验证最终平台 artifact，而不只验证 Python 模块；永久 CI 至少覆盖 onefile `status/self-test`、真实 stdio MCP、项目级单 binary 安装/升级和项目内 Runtime MCP smoke；
- Windows `.exe`、Linux、macOS artifact 分别在对应目标平台构建/验证，不把 PyInstaller onefile 当作跨平台产物。

## 9. 版本与正式 Release 维护边界

根 `VERSION` 是 Agent_Skills 正式产品版本的唯一事实源。修改 VERSION、Runtime Release metadata、Release asset、tag、Full Distribution 能力或 `.github/workflows/release.yml` 时，必须把它视为 Build / Package / Release Contract 变化并读取 Coding 的 Git/Release 与永久 Workflow 规则。

正式**团队 Runtime Release**至少保持：

- SemVer `VERSION` → `v<VERSION>` tag 一一对应；
- Release 只通过 GitHub Actions 的 `workflow_dispatch` 手工运行；维护者必须从 `main` 输入 `v<VERSION>`，Workflow 校验 tag 与根 `VERSION` 一致后再自动创建该 tag 和 GitHub Release；不得因 `VERSION` push 自动发布，也不得提前手工创建同名 tag；
- 正式 Release 资产只包含对应版本的 Linux binary、Windows `.exe`、macOS binary 和 `SHA256SUMS`；不默认同时发布含 canonical Reference 明文的 Full Kit，也不发布 Runtime Kit ZIP、Python 安装脚本或外部 payload；
- Linux / Windows / macOS Runtime binary 分别在对应平台构建，并在成为 Release Candidate 前实际通过 `status/self-test`、真实 stdio MCP、真实项目单 binary 安装和项目内 Runtime MCP smoke；
- Runtime manifest/status 可以记录 `release_version`，但版本号不能替代 canonical Reference `source_digest` / SHA256 或 Project Payload `payload_digest`；
- Full Kit Builder 作为维护者/明确授权的完整 Markdown 兼容能力继续进入永久 CI，但不能因为它存在就把 canonical Reference 明文自动附到团队 Runtime Release；
- Release Workflow 的 Preflight/构建 Job 只读；只有全部 Release Candidate 构建/测试成功后，最终 Publish Job 才能获得 `contents: write`；
- 已存在同版本 tag/Release 时拒绝覆盖或移动历史事实；修复使用新 VERSION；
- 正式资产必须由合并后的 `main` SHA 重新构建，不把 PR 临时产物直接发布；
- 永久 `Skill Tests` 与 Release Workflow 分别承担持续回归和实际发布候选验证，任何 Workflow 精简都要按 Evidence Preservation Mapping 证明独立责任没有丢失。

维护者完整流程见 `docs/maintainers/releasing.md`，Runtime binary 最终用户入口见 `docs/distribution/runtime-kit.md`，Full 明文兼容说明见 `docs/distribution/full-kit.md`，当前版本变化见 `CHANGELOG.md`。Release 完成结论必须核对真实 GitHub tag、Release、资产和 checksum；只看到 Workflow YAML 或本地 `dist/` 不足以宣称发布成功。
