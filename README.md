# Agent_Skills

`Agent_Skills` 是通用 Agent Skill 的**源仓库与维护仓库**。本 README 面向仓库维护者、项目管理员和负责把治理能力接入目标项目的人；普通项目开发者不需要阅读本仓库，也不需要理解 Runtime、MCP、Router、Skill、Reference 或源码维护过程。

面向已经完成安装与首次治理的普通项目开发者，只下发 [`USAGE.md`](USAGE.md) 中的**桌面 AI Agent 日常开发说明**。`USAGE.md` 不承担二进制安装、首次治理、升级/回退、源码直读或网页端维护说明。

## 1. 人类文档职责

本仓库只保留三个人类入口：

```text
README.md
→ 维护者 / 项目管理员
→ 源仓库结构、分发、安装、首次治理、升级/回退、Source Mode、验证与 Release

USAGE.md
→ 已完成接入和首次治理后的普通项目开发者
→ 只说明如何在 Codex、Cursor、Claude Code 等桌面 AI Agent 中开展日常研发

runtime/README.md
→ Runtime 源码子系统维护者
→ Runtime 内部实现、构建和维护细节
```

普通项目开发者不需要知道 Agent_Skills 如何安装、如何路由规则或如何维护源码；他们只需要在已经配置好的目标项目里使用团队允许的桌面 AI Agent，并遵守目标项目自身的权限、Review、CI 和交付门禁。

## 2. 正式分发资产与源码可见性

正式构建产物按平台拆分：

```text
GitHub Release
├── agent-skills-v<SemVer>-linux.zip
│   ├── agent-skills
│   └── USAGE.md
├── agent-skills-v<SemVer>-windows.zip
│   ├── agent-skills.exe
│   └── USAGE.md
└── agent-skills-v<SemVer>-macos.zip
    ├── agent-skills
    └── USAGE.md
```

每个 ZIP 只包含当前平台 Runtime binary 和同版本 `USAGE.md`。`USAGE.md` 即使随 Release 打包，也只描述**项目已经接入后的日常开发使用方式**；binary 的部署、安装、升级和首次治理由维护者按本 README 执行，不交给普通开发者处理。

> **源码可见性边界**：如果完整 `SKILL.md` / canonical `references/*.md` 只允许维护者查看，本 GitHub 仓库必须设置为 **Private**。Runtime 的加密与按任务渐进式披露不能替代仓库访问控制。
>
> 私有仓库的 Release 仍受该仓库 read 权限控制。如果接收者不应获得源码权限，不要为了让他下载 Release 而授予本源仓库 read 权限。维护者应从私有源仓库取得并校验 Release 资产后，通过内部制品库、文件服务或独立的 release-only 仓库/渠道分发项目所需资产。

## 3. 当前正式 Skills

当前仓库实际存在：

| Skill | 职责 | 正式入口 |
| --- | --- | --- |
| `router` | 所有任务的无条件入口、动态 Catalog、跨 Skill 选择、上下文与 Handoff | [`.agents/skills/router/SKILL.md`](.agents/skills/router/SKILL.md) |
| `coding` | 研发、调试、开发期验证治理、Git/CI 与交付 | [`.agents/skills/coding/SKILL.md`](.agents/skills/coding/SKILL.md) |
| `testing` | 测试策略、黑盒/User Journey、探索式、Integration/Workflow/Regression 与独立测试执行 | [`.agents/skills/testing/SKILL.md`](.agents/skills/testing/SKILL.md) |
| `review` | 独立 Code Review、Findings 与测试充分性/Evidence 审查 | [`.agents/skills/review/SKILL.md`](.agents/skills/review/SKILL.md) |
| `docs` | 技术文档事实同步、审查、编写与更新 | [`.agents/skills/docs/SKILL.md`](.agents/skills/docs/SKILL.md) |
| `figma` | Figma 设计事实、Canvas/Prototype、Ready 与 Design-to-Code 交接 | [`.agents/skills/figma/SKILL.md`](.agents/skills/figma/SKILL.md) |

其中 Coding / Testing / Review 的长期边界是：

```text
Coding
→ 实现、根因修复、开发期 TDD 与 Validation/Completion 治理

Testing
→ Test Strategy、用户场景黑盒、探索式、分层功能验证与 Regression 方法

Review
→ 独立需求/实现审查、Findings、测试充分性和 Evidence 是否足以支持结论
```

这些名称只是当前事实，不是永久白名单。正式 Skill 始终从 `.agents/skills/*/SKILL.md` 动态发现；新增合法正式 Skill 后，Runtime、Project Payload、安装和 Release 不应要求再维护一份固定名称列表。

## 4. 规则事实源与 Runtime

跨 Skill 入口分成薄 Bootstrap 和唯一正式 Router：

```text
.agents/skills/ENTRY.md
→ Skills 根级唯一共享运行资产
→ 只恢复项目事实、无条件进入 Router、失败关闭

.agents/skills/router/SKILL.md
→ 动态 Catalog 中的正式 Router Skill
→ 唯一跨 Skill Catalog / Router
→ 负责项目事实优先、Skill 发现、Reference 加载方式和跨 Skill Handoff
```

[`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md) 不复制 Catalog、路由矩阵或专业规则；[`.agents/skills/router/SKILL.md`](.agents/skills/router/SKILL.md) 只负责选择和交接，不生成项目执行计划、不创建子 Agent，也不接管专业工作流。

各专业 Skill 的正式规则边界：

```text
SKILL.md
→ Native Core
→ 负责本 Skill 的入口、主流程和 Reference 加载时机

references/*.md
→ canonical 详细规则
→ 唯一完整 Reference 正文
```

两种使用模式共享同一 canonical Markdown 和 committed 路由元数据：

```text
Source Mode
→ 按当前 metadata 的并集 / 依赖 / 风险语义确定 required References
→ 直接读取源仓库中的完整 canonical 原文

Runtime Mode
→ Entry + Router / 专业 Skill Runtime Projection + 必要运行资产进入 Project Payload
→ canonical References 与私有 Routing Manifest 加密嵌入 onefile
→ 宿主按任务事实提交 Task Route
→ 本地 MCP 只返回当前任务 required 的完整原文
```

Runtime 不安装 canonical `references/` 或公开 Reference manifest，不接受任意 ID 加载。它不是第二套规则系统，也不摘要或重写 canonical References。

### 同版本、跨宿主与模型边界

Source / Runtime 是治理规则的取得方式，不是 Git 执行能力。实际仓库操作仍必须满足当前身份权限、Branch Protection / Ruleset、原子性、revision guard、Review、CI 和目标项目门禁；本地某一个 transport 失败不代表所有安全等价能力都不可用。

“合并到主分支”表示完成当前已确认任务的适用端到端收尾，而不是只调用一次 merge API；“提交 PR 给我审核”则止于 PR Ready。详细语义由 [`.agents/skills/coding/references/23_端到端交付与合并后收尾.md`](.agents/skills/coding/references/23_端到端交付与合并后收尾.md) 维护，不按模型品牌复制不同流程。

源码与二进制严格比较必须绑定同一 source revision、任务事实和环境。旧安装不会因为 canonical `main` 更新而自动热更新；需要严格复现时，应使用 Runtime identity 对应的 Release tag / source commit。

## 5. AI 与维护入口职责

### 根 `AGENTS.md`

根 [`AGENTS.md`](AGENTS.md) 是 Agent 进入本仓库时的薄 Bootstrap：

- 使用 Agent_Skills 帮助另一个项目时，先读取目标项目自己的规则和真实事实，再进入 [`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)；
- 维护 Agent_Skills 源仓库本身时，进入 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md) 和 Entry，再由 Router 选择专业 Skill。

它不保存第二套完整 Router 或完整源仓库维护规则，也不得复制到目标项目。

### `.agents/MAINTENANCE.md`

[`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md) 是 Agent_Skills 源仓库自身的开发、Review、测试、CI、Git、Release、内容守恒和 Runtime 维护规则。普通目标项目开发不读取它。

### 目标项目 managed block

Runtime 安装后，[`.agents/skills/coding/assets/AGENTS.managed.md`](.agents/skills/coding/assets/AGENTS.managed.md) 只在目标项目中提供薄项目侧行为契约：目标项目自身规则和真实事实始终优先，内部 Runtime/Router/Reference 细节不复制到目标项目长期规则中。

## 6. 安装到目标项目

本节只给维护者 / 项目管理员使用。普通项目开发者收到项目时，应已经完成本节以及第 7 节的首次治理。

### 6.1 获取对应平台资产

从正式 Release 或内部受控分发渠道取得与目标开发环境匹配的平台 ZIP，并先核对来源和完整性。三个正式平台包分别为：

```text
agent-skills-v<VERSION>-windows.zip
agent-skills-v<VERSION>-linux.zip
agent-skills-v<VERSION>-macos.zip
```

不要从不同版本手工混合 binary、说明或安装后的受管文件。

### 6.2 Windows

在目标项目根目录运行当前版本：

```powershell
cd D:\work\MyProject
.\agent-skills.exe
```

也可以显式指定目标：

```powershell
.\agent-skills.exe install --target D:\work\MyProject --json
```

### 6.3 Linux

```bash
cd /work/MyProject
chmod +x /path/to/agent-skills
/path/to/agent-skills
```

或：

```bash
/path/to/agent-skills install --target /work/MyProject --json
```

### 6.4 macOS

```bash
cd /work/MyProject
chmod +x /path/to/agent-skills
/path/to/agent-skills
```

或：

```bash
/path/to/agent-skills install --target /work/MyProject --json
```

无参数运行等价于安装 / 更新当前工作目录。安装只作用于目标项目，不全局修改其他项目；已有项目内容必须按安装器 ownership 与 fail-closed 边界保留。

### 6.5 安装后状态与自检

维护者完成安装或升级后运行：

```text
agent-skills status --json
agent-skills self-test --json
```

只有实际命令成功并检查结果后，才能声明当前项目 Runtime 已安装且完整。安装器或自检报告冲突、ownership 不可证明、完整性错误时停止处理，不强制覆盖项目文件。

## 7. 首次项目治理

**二进制安装成功不等于目标项目已经完成工程治理。** 第一次接入一个项目时，维护者应让当前具备项目写权限的 AI Agent 先调查项目真实情况，完成一次 Project Governance Bootstrap，再进入实质性业务开发。

这一步的目的不是让安装器猜技术栈，而是让当前开发 Agent 基于真实仓库建立或校准项目自己的长期 Overlay。

维护者可以使用下面的自然语言：

```text
这是本项目第一次接入 Agent_Skills。先不要修改业务代码。

请先读取当前已有的 AGENTS.md、CONTRIBUTING、README、需求/规格、Manifest/lock、真实代码、Contract、Schema/Migration、测试、CI、部署配置和其他与长期开发规则有关的事实源，完成 Project Governance Bootstrap。

校准项目规则时：
1. 区分规范性规则、描述性事实和未确认事项；
2. 规范性规则不能因为当前代码没有遵守就直接删除或弱化；如果实现违反正式规则，应指出实现问题；
3. 描述性事实只有在当前项目有充分证据证明已经过时时才修正；
4. 无法确认的内容保持未确认，不要猜技术栈、架构、数据库、CI 或部署方式；
5. 保留现有仍有效内容，只做必要的增量修正；
6. 完成后重新读取最终项目规则，再报告工程基线、主要模块边界、开发/测试入口和仍未确认的事项。
```

如果真实目标本来就是开发功能，可以把原任务直接接在后面，但必须先完成治理校准再继续生产代码修改。

首次治理完成后，普通功能开发不重复全量校准。只有技术栈、模块职责、Contract/Schema、开发验证入口、CI/Release/部署等长期项目事实真实变化，或维护者明确要求刷新项目规则时，才对受影响 Overlay 做定向更新。

## 8. Codex、Cursor、Claude Code 接入检查

安装器负责维护目标项目中的项目级接入配置。首次打开项目时，Codex、Cursor、Claude Code 可能要求用户确认项目 Trust、Approval 或相关工具权限；宿主自身的安全确认不得绕过。

如果目标项目没有正常识别已配置的治理能力，维护者按以下顺序处理：

1. 关闭并重新打开当前项目，或新建 Agent 会话；
2. 检查宿主是否存在待确认的 Trust / Approval；
3. 运行 `status --json` 和 `self-test --json`；
4. 如当前版本安装状态可安全恢复，在项目根重新执行同版本安装；
5. 仍失败时按当前错误和 Runtime 维护文档调查，不让普通项目开发者手工改内部受管文件。

## 9. 升级与回退

Agent_Skills 默认不承诺不同版本之间的原地升级兼容。切换版本时以目标版本当前说明、真实安装 Contract 和可恢复边界为准；不要因为旧项目中存在历史 Runtime、旧配置或旧状态，就假定新版本会自动识别、迁移或删除。

### 升级

1. 备份目标项目规则、未提交工作和其他需要保留的本地状态；
2. 取得目标版本对应平台 ZIP；
3. 在可恢复的项目副本或满足目标版本要求的项目边界中运行目标版本 binary；
4. 运行 `status --json` 与 `self-test --json`；
5. 重新打开项目或新建 Agent 会话；
6. 如果新版本报告当前项目状态不受支持，停止并按目标版本迁移/安装说明处理，不强制覆盖或猜 ownership。

### 回退

1. 取得目标旧版本对应平台 ZIP；
2. 使用该版本完整平台资产执行其安装流程；
3. 运行 `status --json` 与 `self-test --json`；
4. 重新打开项目或新建 Agent 会话；
5. 如果目标版本不理解当前项目状态，停止并按该版本明确支持的迁移路径处理。

不要只复制某一个旧 binary 或手工拼接不同版本的受管文件；版本身份、Project Payload 和安装边界必须成套恢复。

## 10. 网页端 / Source Mode

当前本地 Runtime 是项目级 stdio MCP；纯网页会话不能直接启动用户电脑中的本地 Runtime。

维护者在 ChatGPT 网页端等环境中，如果当前会话拥有 Agent_Skills 源仓库读取权限，可以使用 **Source Mode**：

```text
目标项目规则与真实事实
→ Agent_Skills 当前目标 revision 的根 AGENTS.md
→ Entry / Router
→ 当前任务命中的 canonical Skill / Reference 完整原文
→ 目标项目真实验证与交付门禁
```

网页端 Source Mode 不调用用户电脑的本地 Runtime，也不能把目标项目旧安装副本当作 canonical Source。网页连接器是否能提交、创建 PR、查询 CI 或合并，取决于当前连接器实际能力、授权身份和仓库保护规则；本地 Git 网络失败不等于这些托管能力也失效。

需要 Source 与 Runtime 严格一致时，Source Mode 必须读取 Runtime identity 对应的 Release tag/source commit；不能把旧 Runtime 与更新后的 `main` 声称为同一版本。

## 11. 仓库结构

```text
Agent_Skills/
├── AGENTS.md                 # AI 双模式薄 Bootstrap
├── README.md                 # 维护者 / 项目管理员入口
├── USAGE.md                  # 已接入项目的普通开发者日常使用说明
├── .agents/
│   ├── MAINTENANCE.md        # Agent_Skills 源仓库 AI 维护规范
│   ├── changes/              # Active L2/L3 Change；完成后归档到 archive/YYYY-MM
│   └── skills/
│       ├── ENTRY.md          # 唯一共享薄入口
│       ├── router/           # 唯一正式跨 Skill Router
│       ├── coding/
│       ├── testing/
│       ├── review/
│       ├── docs/
│       └── figma/
├── runtime/
│   ├── README.md             # Runtime 源码维护说明
│   ├── requirements.txt
│   ├── requirements-build.txt
│   └── agent_skills_runtime/
├── scripts/
│   ├── build_runtime.py
│   └── runtime_mcp_smoke.py
└── .github/workflows/
    ├── skill-tests.yml
    └── release.yml
```

`.agents/project-context.json` 是 Coding 在目标项目中生成的本地可失效导航缓存，不是团队事实，也不应提交 Git。

## 12. 维护者常用验证

开始维护前先读根 [`AGENTS.md`](AGENTS.md)，再按它进入 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)、[`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)、唯一 Router 和任务命中的正式 Skill/Reference。

永久 CI 固定使用 Python `3.14.7` 构建 Runtime；本地维护者可以使用当前兼容 Python 执行源码测试，但正式三平台 artifact 必须以 CI/Release 固定版本为准。

自包含回归：

```bash
python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v
```

构建当前平台开发态 Runtime：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

未显式传入版本时，Builder 使用 `0.0.0-dev` 作为 development identity；它不是正式 Release 版本。

验证真实 stdio MCP：

```bash
python scripts/runtime_mcp_smoke.py --artifact dist/agent-skills --json
```

Completion Gate：

```bash
python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

不同平台正式 onefile 必须在 Linux / Windows / macOS 对应 Runner 上分别构建和验证，不能互相替代。

[`.github/workflows/skill-tests.yml`](.github/workflows/skill-tests.yml) 根据真实 changed scope 执行永久门禁；`Agent Skills Gate` 与 `Runtime Package Gate` 保持 required check 身份。文档或 content 变化不能通过手工声称“不影响 Runtime”绕过当前 classifier 和 required CI。

## 13. 正式 Release

仓库不维护独立 `VERSION` 文件。正式 Release 的唯一版本输入是手工 Release workflow 的 `tag`：输入 `v<SemVer>` 后，workflow 去掉前缀 `v` 得到 `release_version`，并把同一个值显式传给 Linux / Windows / macOS 三个平台 Runtime Builder。

正式发布通过 [`.github/workflows/release.yml`](.github/workflows/release.yml) 手工触发：

```text
main
→ 输入 v<SemVer>
→ 由 tag 派生 release_version
→ Preflight 校验 main/tag/Release + 全量自包含测试 + Ready
→ Linux / Windows / macOS 使用 Python 3.14.7 分别构建并验证
→ 交叉校验 identity / artifact SHA256
→ 创建 Draft Release 并上传完整正式资产
→ 核对 Draft 资产集合
→ Publish
→ 验证 tag 与正式资产
```

每个平台构建都会把真实 source commit、构建 Python、Bundle/Task Route/Routing/MCP/Project Payload/install 协议、`source_digest`、`routing_digest` 和 `payload_digest` 纳入 Runtime / Release identity。正式 GitHub build 要求 source commit 与 `GITHUB_SHA`、checkout HEAD 一致。

Release workflow 不依赖自定义 PAT；发布使用 GitHub Actions 自动提供的 `github.token` 和最小 `contents: write`。workflow 拒绝覆盖已有 tag/Release，但这不等价于底层存储不可变。

Release 页面说明继续使用 [`USAGE.md`](USAGE.md)，每个正式 ZIP 也继续包含该文件；但 `USAGE.md` 只解释项目已经接入后的日常桌面 AI Agent 使用方式，安装和首次治理由本 README 承担。

## 14. 继续阅读

- 已接入项目的普通开发者：[`USAGE.md`](USAGE.md)
- AI 统一入口：[`AGENTS.md`](AGENTS.md)
- 源仓库 AI 维护规则：[`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)
- 薄 Entry：[`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)
- 唯一 Skill Router：[`.agents/skills/router/SKILL.md`](.agents/skills/router/SKILL.md)
- Runtime 源码维护：[`runtime/README.md`](runtime/README.md)
- Runtime 构建：[`scripts/build_runtime.py`](scripts/build_runtime.py)
- 正式发布：[`.github/workflows/release.yml`](.github/workflows/release.yml)