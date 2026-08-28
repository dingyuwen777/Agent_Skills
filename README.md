# Agent_Skills

`Agent_Skills` 是通用 Agent Skill 的**源仓库与维护仓库**。它保存正式 Skill、唯一跨 Skill Router、canonical References、项目级 Runtime、构建/验证脚本和维护期 Change 记录。

最终使用者不需要理解本仓库的维护过程，也不需要访问源码。正式构建产物只有：

```text
GitHub Release
→ 当前平台 agent-skills-mcp binary
→ USAGE.md
→ SHA256SUMS
```

最终用户入口见 [`USAGE.md`](USAGE.md)。

> **源码可见性边界**：如果完整 `SKILL.md` / canonical `references/*.md` 只允许维护者查看，本 GitHub 仓库必须设置为 **Private**。Runtime 的加密与 Stub 机制不能替代仓库访问控制。
>
> 私有仓库的 Release 仍受该仓库 read 权限控制。**如果接收者不应获得源码权限，不要为了让他下载 Release 而授予本源仓库 read 权限。** 维护者应从私有源仓库取得并校验 Release 资产后，通过内部制品库、文件服务或独立的 release-only 仓库/渠道向最终使用者分发。

## 1. 当前正式 Skills

当前仓库实际存在：

| Skill | 职责 | 正式入口 |
| --- | --- | --- |
| `coding` | 研发、调试、验证、Git/CI/交付与跨 Skill 主流程 | `.agents/skills/coding/SKILL.md` |
| `review` | 独立 Code Review、Findings 与测试充分性审查 | `.agents/skills/review/SKILL.md` |
| `docs` | 技术文档事实同步、审查、编写与更新 | `.agents/skills/docs/SKILL.md` |
| `figma` | Figma 设计事实、Canvas/Prototype、Ready 与 Design-to-Code 交接 | `.agents/skills/figma/SKILL.md` |

这四个名称只是当前事实，不是永久白名单。正式 Skill 始终从：

```text
.agents/skills/*/SKILL.md
```

动态发现。新增合法正式 Skill 后，Runtime、Project Payload、manifest、安装和 Release 不应要求再维护一份固定名称列表。

## 2. 规则事实源与 Runtime

跨 Skill 入口只维护一份：

```text
.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md
→ 唯一 Skill Catalog / Router
→ 负责项目事实优先、Skill 发现、Reference 加载方式和跨 Skill Handoff
```

各专业 Skill 的正式规则边界：

```text
SKILL.md
→ Native Core
→ 负责本 Skill 的入口、主流程和 Reference 加载时机

references/*.md
→ canonical 详细规则
→ 唯一完整 Reference 正文
```

正式 Runtime 构建时：

```text
Native Core / Router / 必要运行资产
→ Project Payload
→ 安装到目标项目

canonical references/*.md
→ 逐字 hash
→ AES-GCM 加密嵌入 onefile Runtime

目标项目 references/
→ 只安装同名 Stub
→ 命中后由本地 MCP 返回 canonical_text
```

Runtime 不是第二套规则系统，也不摘要或重写 canonical References。

## 3. AI 入口职责

### 根 `AGENTS.md`

根 [`AGENTS.md`](AGENTS.md) 是 Agent 进入本仓库时的**薄 Bootstrap**：

- ChatGPT 网页端 / GitHub 直接使用 Agent_Skills 帮助另一个项目时，先要求读取目标项目自己的规则和真实事实，再进入唯一 Router；
- 当前任务是在维护 Agent_Skills 源仓库本身时，进入 `.agents/MAINTENANCE.md`，再按 Router / Coding 执行。

它不再保存第二套完整 Router 或完整源仓库维护规则，也不得复制到目标项目。

### `.agents/MAINTENANCE.md`

[`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md) 是 Agent_Skills **源仓库自身**的开发、Review、测试、CI、Git、Release、内容守恒和 Runtime 维护规则。普通外部项目任务不读取它。

### 唯一 Router

[`.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`](.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md) 是源码直读与 Runtime 安装两种模式共同使用的唯一跨 Skill Router。

源码直读时，命中的 canonical Reference 直接从本源仓库读取；Runtime 安装态命中 Stub 时，通过项目本地 MCP 的 `agent_skills_load_context` 取得并校验 `canonical_text`。

### 目标项目 `AGENTS.md` managed block

Runtime 安装后，`.agents/skills/coding/assets/AGENTS.managed.md` 只作为目标项目里的**薄 Bootstrap**：它要求先遵守目标项目事实，再读取本地同一个 Router。Coding / Figma / Review / Docs 和 Reference 详细路由不再复制进 managed block。

### `USAGE.md`

[`USAGE.md`](USAGE.md) 是唯一最终用户人类说明，负责下载、安装、使用、升级、回滚和排障。

## 4. 仓库结构

```text
Agent_Skills/
├── AGENTS.md                 # AI 双模式薄 Bootstrap
├── README.md                 # 维护者源码仓库入口
├── USAGE.md                  # Release 最终用户唯一说明
├── VERSION                   # 产品版本事实源
├── .agents/
│   ├── MAINTENANCE.md        # Agent_Skills 源仓库 AI 维护规范
│   ├── changes/              # 维护期 Change 记录
│   └── skills/
│       ├── coding/
│       │   └── assets/
│       │       └── AGENT_SKILLS_ROUTER.md  # 唯一跨 Skill Router
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

`.agents/project-context.json` 是 Coding 在目标项目中生成的**本地可失效导航缓存**，不是本仓库的团队事实，也不应提交 Git。

## 5. 维护者常用验证

开始维护前先读根 [`AGENTS.md`](AGENTS.md)，再按它进入 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)、唯一 Router 和任务命中的正式 Skill/Reference。

自包含回归：

```bash
python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v
```

构建当前平台 Runtime：

```bash
python3 scripts/build_runtime.py --output-dir dist --json
```

验证真实 stdio MCP：

```bash
python3 scripts/runtime_mcp_smoke.py --artifact dist/agent-skills-mcp --json
```

Completion Gate：

```bash
python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

不同平台的正式 onefile 必须在 Linux / Windows / macOS 对应 Runner 上分别构建和验证，不能互相替代。

## 6. 正式 Release

根 [`VERSION`](VERSION) 是版本事实源。

正式发布通过 [`.github/workflows/release.yml`](.github/workflows/release.yml) 手工触发：

```text
main
→ 输入 v<VERSION>
→ Preflight 校验 VERSION / tag / Ready
→ Linux / Windows / macOS 分别构建并验证
→ Publish
→ 创建不可覆盖的 tag / GitHub Release
```

源仓库 Release 资产固定为三平台 binary、`USAGE.md` 与 `SHA256SUMS`。Release 页面说明直接使用 `USAGE.md`，不自动把维护 commit / PR 历史生成给最终使用者。最终交付给不具备源仓库权限的用户时，只复制这些 Release 资产，不暴露源仓库访问权。

## 7. 继续阅读

- 最终用户：[`USAGE.md`](USAGE.md)
- AI 统一入口：[`AGENTS.md`](AGENTS.md)
- 源仓库 AI 维护规则：[`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)
- 唯一 Skill Router：[`.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`](.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md)
- Runtime 源码维护：[`runtime/README.md`](runtime/README.md)
- 正式 Skill：`.agents/skills/*/SKILL.md`
- Runtime 构建：[`scripts/build_runtime.py`](scripts/build_runtime.py)
- 正式发布：[`.github/workflows/release.yml`](.github/workflows/release.yml)
