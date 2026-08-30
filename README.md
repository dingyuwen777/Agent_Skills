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

> **源码可见性边界**：如果完整 `SKILL.md` / canonical `references/*.md` 只允许维护者查看，本 GitHub 仓库必须设置为 **Private**。Runtime 的加密与按任务渐进式披露不能替代仓库访问控制。
>
> 私有仓库的 Release 仍受该仓库 read 权限控制。**如果接收者不应获得源码权限，不要为了让他下载 Release 而授予本源仓库 read 权限。** 维护者应从私有源仓库取得并校验 Release 资产后，通过内部制品库、文件服务或独立的 release-only 仓库/渠道向最终使用者分发。

## 1. 当前正式 Skills

当前仓库实际存在：

| Skill | 职责 | 正式入口 |
| --- | --- | --- |
| `coding` | 研发、调试、验证、Git/CI/交付与跨 Skill 主流程 | [`.agents/skills/coding/SKILL.md`](.agents/skills/coding/SKILL.md) |
| `review` | 独立 Code Review、Findings 与测试充分性审查 | [`.agents/skills/review/SKILL.md`](.agents/skills/review/SKILL.md) |
| `docs` | 技术文档事实同步、审查、编写与更新 | [`.agents/skills/docs/SKILL.md`](.agents/skills/docs/SKILL.md) |
| `figma` | Figma 设计事实、Canvas/Prototype、Ready 与 Design-to-Code 交接 | [`.agents/skills/figma/SKILL.md`](.agents/skills/figma/SKILL.md) |

这四个名称只是当前事实，不是永久白名单。正式 Skill 始终从：

```text
.agents/skills/*/SKILL.md
```

动态发现。新增合法正式 Skill 后，Runtime、Project Payload、manifest、安装和 Release 不应要求再维护一份固定名称列表。

## 2. 规则事实源与 Runtime

跨 Skill 入口只维护一份：

```text
.agents/skills/ROUTER.md
→ Skills 根级共享运行资产
→ 唯一 Skill Catalog / Router
→ 负责项目事实优先、Skill 发现、Reference 加载方式和跨 Skill Handoff
```

`ROUTER.md` 不属于任何一个具体 Skill，也不是第五个 Skill；正式 Skill 仍只由各一级目录中的 `SKILL.md` 建立入口。

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
→ 按当前 metadata 的并集/依赖/风险语义确定 required References
→ 直接读取源仓库中的完整 canonical 原文

Runtime Mode
→ ROUTER.md + Native Core / 必要运行资产进入 no-Stub Project Payload
→ canonical References + 私有 Routing Manifest 认证加密嵌入 onefile
→ 宿主提交中文 Task Route
→ 本地 MCP 只返回当前 route required 的完整原文
```

Runtime 不安装 `references/` 或公开 Reference manifest，不接受任意 ID 加载。它不是第二套规则系统，也不摘要或重写 canonical References；Task Route 是宿主与 Runtime 的内部协议，不要求用户维护。

## 3. AI 入口职责

### 根 `AGENTS.md`

根 [`AGENTS.md`](AGENTS.md) 是 Agent 进入本仓库时的**薄 Bootstrap**：

- ChatGPT 网页端 / GitHub 直接使用 Agent_Skills 帮助另一个项目时，先要求读取目标项目自己的规则和真实事实，再进入唯一 Router；
- 当前任务是在维护 Agent_Skills 源仓库本身时，进入 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)，再按 Router / Coding 执行。

它不再保存第二套完整 Router 或完整源仓库维护规则，也不得复制到目标项目。

### [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)

[`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md) 是 Agent_Skills **源仓库自身**的开发、Review、测试、CI、Git、Release、内容守恒和 Runtime 维护规则。普通外部项目任务不读取它。

### 唯一 Router

[`.agents/skills/ROUTER.md`](.agents/skills/ROUTER.md) 是源码直读与 Runtime 安装两种模式共同使用的唯一跨 Skill Router。

源码直读时，required Reference 直接从本源仓库读取；Runtime 安装态通过 `agent_skills_route_contract → start_task → submit_route → load_required_context → checkpoint` 获取本任务最低必需的完整 Context。

### 目标项目 `AGENTS.md` managed block

Runtime 安装后，[`.agents/skills/coding/assets/AGENTS.managed.md`](.agents/skills/coding/assets/AGENTS.managed.md) 只作为目标项目里的**薄 Bootstrap**：它要求先遵守目标项目事实，再读取本地 [`.agents/skills/ROUTER.md`](.agents/skills/ROUTER.md)。Coding / Figma / Review / Docs 和 Reference 详细路由不再复制进 managed block。

### [`USAGE.md`](USAGE.md)

[`USAGE.md`](USAGE.md) 是唯一最终用户人类说明，负责下载、安装、使用、升级、回滚和排障。

## 4. 仓库结构

```text
Agent_Skills/
├── AGENTS.md                 # AI 双模式薄 Bootstrap
├── README.md                 # 维护者源码仓库入口
├── USAGE.md                  # Release 最终用户唯一说明
├── .agents/
│   ├── MAINTENANCE.md        # Agent_Skills 源仓库 AI 维护规范
│   ├── changes/              # 仅存在 Active L2/L3 Change 时临时出现；完成后删除
│   └── skills/
│       ├── ROUTER.md         # 唯一跨 Skill Router / 共享运行资产
│       ├── coding/
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

永久 CI 固定使用 Python `3.12.10` 构建 Runtime；本地维护者可以使用当前兼容 Python 执行源码测试，但正式三平台 artifact 必须以 CI/Release 中固定版本为准。

自包含回归：

```bash
python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v
```

构建当前平台开发态 Runtime：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

未显式传入版本时，Builder 使用 `0.0.0-dev` 作为 development identity；它不是正式 Release 版本。构建结果还会返回聚合 `context_budget`，用于量化 Router、各 Skill Core 和 canonical References 的上下文字节成本，不改变 Runtime `status/self-test` 的公开披露边界。

验证真实 stdio MCP：

```bash
python scripts/runtime_mcp_smoke.py --artifact dist/agent-skills-mcp --json
```

Completion Gate：

```bash
python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

不同平台的正式 onefile 必须在 Linux / Windows / macOS 对应 Runner 上分别构建和验证，不能互相替代。

## 6. 正式 Release

仓库不维护独立 `VERSION` 文件。**正式 Release 的唯一版本输入是手工 Release workflow 的 `tag`**：输入 `v<SemVer>` 后，workflow 去掉前缀 `v` 得到 `release_version`，并把同一个值显式传给 Linux / Windows / macOS 三个平台的 Runtime Builder。

每个平台构建都会把真实 `source_commit`、构建 Python 版本、Bundle/Task Route/Routing/MCP/Project Payload/install 协议、`source_digest`、`routing_digest` 和 `payload_digest` 写入 Runtime/Release identity；GitHub build 要求 `source_commit` 与 `GITHUB_SHA` 和 checkout HEAD 一致。公开 identity 不包含 Reference ID、文件名、路径、数量或私有路由映射。

网页端读当前 `main`、本地使用当前最新 Release 属于“最新规则模式”，发布间隙可能短暂不完全同版；需要严格复现时，Source Mode 必须切到 Runtime identity 对应的 Release tag/source commit，不能把旧 Runtime 与更新后的 `main` 声称为同一版本。

正式发布通过 [`.github/workflows/release.yml`](.github/workflows/release.yml) 手工触发：

```text
main
→ 输入 v<SemVer>
→ 由 tag 派生 release_version
→ Preflight 校验 main/tag/Release/Release Immutability + 全量自包含测试 + Ready
→ Linux / Windows / macOS 使用 Python 3.12.10 分别构建并验证
→ 交叉校验 identity / artifact SHA256
→ 创建 Draft Release 并上传完整正式资产
→ 核对 Draft 资产集合
→ Publish
→ 验证 tag、正式资产与 immutable 状态
```

Release workflow 对 Release Immutability 采用 fail-closed。GitHub 官方的仓库设置检查 API 需要 `Administration: read`，而默认 `GITHUB_TOKEN` 不具备读取该管理设置的权限；因此 Preflight 优先使用可选仓库 Secret `RELEASE_SETTINGS_TOKEN`（建议使用仅授权本仓库、`Administration: read` 的 fine-grained PAT）做机器验证。若没有配置该 Secret，默认 Token 返回 403 时不会再误报“未启用”，而是要求本次手工运行显式勾选 `confirm_immutable_releases`，确认维护者已经在 `Settings > Releases` 打开该设置；真正的 404 仍表示未启用并立即失败。

无论 Preflight 使用机器验证还是显式人工确认，正式发布后仍必须从 GitHub Release API 验证 `immutable=true`；Draft→资产校验→Publish、tag/资产核对和失败时只清理未发布 Draft 的边界保持不变。

源仓库 Release 资产固定为三平台 binary、[`USAGE.md`](USAGE.md) 与 `SHA256SUMS`。构建期 identity manifest 只在 CI 内校验后删除；版本与 digest 身份仍可通过 binary 的 `status --json` 读取。Release 页面说明直接使用 [`USAGE.md`](USAGE.md)，不自动把维护 commit / PR 历史生成给最终使用者。最终交付给不具备源仓库权限的用户时，只复制这些 Release 资产，不暴露源仓库访问权。

## 7. 继续阅读

- 最终用户：[`USAGE.md`](USAGE.md)
- AI 统一入口：[`AGENTS.md`](AGENTS.md)
- 源仓库 AI 维护规则：[`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)
- 唯一 Skill Router：[`.agents/skills/ROUTER.md`](.agents/skills/ROUTER.md)
- Runtime 源码维护：[`runtime/README.md`](runtime/README.md)
- 正式 Skill：`.agents/skills/*/SKILL.md`
- Runtime 构建：[`scripts/build_runtime.py`](scripts/build_runtime.py)
- 正式发布：[`.github/workflows/release.yml`](.github/workflows/release.yml)
