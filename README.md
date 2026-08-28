# Agent_Skills

`Agent_Skills` 是通用 Agent Skill 的**源仓库与维护仓库**。它保存正式 Skill、canonical References、项目级 Runtime、构建/验证脚本和维护期 Change 记录。

最终使用者不需要理解本仓库的维护过程，也不需要访问源码。正式对外交付只有：

```text
GitHub Release
→ 当前平台 agent-skills-mcp binary
→ USAGE.md
→ SHA256SUMS
```

最终用户入口见 [`USAGE.md`](USAGE.md)。

> **源码可见性边界**：如果完整 `SKILL.md` / canonical `references/*.md` 只允许维护者查看，本 GitHub 仓库必须设置为 **Private**。Runtime 的加密与 Stub 机制不能替代仓库访问控制。

## 1. 当前正式 Skills

当前仓库实际存在：

| Skill | 职责 | 正式入口 |
| --- | --- | --- |
| `coding` | 研发、调试、验证、Git/CI/交付与跨 Skill 路由 | `.agents/skills/coding/SKILL.md` |
| `review` | 独立 Code Review、Findings 与测试充分性审查 | `.agents/skills/review/SKILL.md` |
| `docs` | 技术文档事实同步、审查、编写与更新 | `.agents/skills/docs/SKILL.md` |
| `figma` | Figma 设计事实、Canvas/Prototype、Ready 与 Design-to-Code 交接 | `.agents/skills/figma/SKILL.md` |

这四个名称只是当前事实，不是永久白名单。正式 Skill 始终从：

```text
.agents/skills/*/SKILL.md
```

动态发现。新增合法正式 Skill 后，Runtime、Project Payload、manifest、安装和 Release 不应要求再维护一份固定名称列表。

## 2. 规则事实源与 Runtime

源码仓库中的规则边界：

```text
SKILL.md
→ Native Core
→ 负责宿主原生触发、任务路由和 Reference 加载时机

references/*.md
→ canonical 详细规则
→ 唯一完整 Reference 正文
```

正式 Runtime 构建时：

```text
Native Core / 必要运行资产
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

## 3. 三类入口不要混淆

### `AGENTS.md`

根 [`AGENTS.md`](AGENTS.md) 只负责指导 AI **维护 Agent_Skills 源仓库本身**：如何恢复事实、选择 Coding references、保护内容守恒、执行 Change/Review/CI/Git/Release 门禁。

它不是最终用户说明，也不得复制到目标项目。

### 目标项目 `AGENTS.md`

目标项目安装 Runtime 后，由 `.agents/skills/coding/assets/AGENTS.managed.md` 生成或更新项目自己的 managed block。这个 managed block 才负责告诉目标项目中的 AI：

- 先遵守项目规则；
- 进入 Coding；
- 命中 Reference 时通过 MCP 读取 canonical 原文；
- 何时进入 Figma / Review / Docs；
- 不绕过目标项目自己的 CI、PR、Release、安全等门禁。

### `USAGE.md`

[`USAGE.md`](USAGE.md) 是唯一最终用户人类说明，负责下载、安装、使用、升级、回滚和排障。

## 4. 仓库结构

```text
Agent_Skills/
├── AGENTS.md                 # AI 维护源仓库时的上位规则
├── README.md                 # 维护者源码仓库入口
├── USAGE.md                  # Release 最终用户唯一说明
├── VERSION                   # 产品版本事实源
├── .agents/
│   ├── changes/              # 维护期 Change 记录
│   └── skills/
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

开始维护前先读 [`AGENTS.md`](AGENTS.md) 和任务命中的正式 Skill/Reference。

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

Release 的用户可见内容固定为三平台 binary、`USAGE.md` 与 `SHA256SUMS`。Release 页面说明直接使用 `USAGE.md`，不自动把维护 commit / PR 历史生成给最终使用者。

## 7. 继续阅读

- 最终用户：[`USAGE.md`](USAGE.md)
- 源仓库 AI 维护规则：[`AGENTS.md`](AGENTS.md)
- Runtime 源码维护：[`runtime/README.md`](runtime/README.md)
- 正式 Skill：`.agents/skills/*/SKILL.md`
- Runtime 构建：[`scripts/build_runtime.py`](scripts/build_runtime.py)
- 正式发布：[`.github/workflows/release.yml`](.github/workflows/release.yml)