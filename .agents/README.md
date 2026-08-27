# `.agents` 目录导航

`.agents/` 用来保存仓库内 AI / Coding Agent 的通用 Skill、Change fallback 和本地导航约定。它不是产品代码目录，也不是第二套项目架构文档。

完整的仓库安装、分发和使用入口见 [`../README.md`](../README.md)。本文件只回答：**`.agents` 里面有什么，应该从哪里进入。**

## 1. 目录结构

当前仓库实际结构：

```text
.agents/
├── README.md
├── project-context.json       # 目标项目本地可失效缓存；不提交 Git
├── changes/                   # 项目采用 Coding fallback Change 时使用
│   ├── active/
│   └── archive/
└── skills/
    ├── coding/
    │   ├── README.md
    │   ├── SKILL.md
    │   ├── agents/
    │   ├── assets/
    │   ├── references/
    │   ├── scripts/
    │   └── tests/
    ├── review/
    │   ├── README.md
    │   ├── SKILL.md
    │   ├── agents/
    │   └── references/
    └── docs/
        ├── README.md
        ├── SKILL.md
        ├── agents/
        └── references/
```

这只是**当前实际 Skill 集合**。正式分发不会把 `coding/review/docs` 写成永久全量白名单，而是从：

```text
.agents/skills/*/SKILL.md
```

动态发现合法正式 Skill。未来增加新的正式 Skill 后，Runtime、Full/source 安装和 Release 应自动识别，不要求更新静态名称列表。

## 2. 当前三个核心 Skill

| Skill | 负责什么 | 使用说明 | 正式规则 |
| --- | --- | --- | --- |
| Coding | 研发、调试、验证、Git、CI、Release 与交付主流程 | [`skills/coding/README.md`](skills/coding/README.md) | [`skills/coding/SKILL.md`](skills/coding/SKILL.md) |
| Review | 独立审查、Findings、测试充分性和 re-review | [`skills/review/README.md`](skills/review/README.md) | [`skills/review/SKILL.md`](skills/review/SKILL.md) |
| Docs | 技术文档事实同步、审查、编写与更新 | [`skills/docs/README.md`](skills/docs/README.md) | [`skills/docs/SKILL.md`](skills/docs/SKILL.md) |

`README.md` 用来帮助人理解入口；真正约束 Agent 行为的是对应 `SKILL.md` 以及任务命中的 `references/`。

Review 不维护第二套 Coding 规范；Docs 也不复制 Coding 的研发规则。当前常见路由是：

```text
目标项目 AGENTS.md / CONTRIBUTING / 同等规则
→ Coding
→ 按任务读取最少充分 references
→ 需要文档同步时进入 Docs
→ 完成前进入 Review
→ PR / CI / Delivery
```

以后增加其他正式 Skill 时，由当前 Core Skill、目标项目规则和新增 Skill 自身 `SKILL.md` 定义触发/路由；不要回到本文件维护一份“所有 Skill 必须怎样串联”的静态全集。

显式 Code Review 可以让 Review 成为主要工作流，但仍先遵守项目上位规则和真实仓库事实。Docs 发现实现本身错误时返回 Coding，而不是修改文档去迎合 Bug。

## 3. `changes/`

Coding 自带 Change 只是**项目没有可复用治理载体时的 fallback**。

当前 Coding Change schema：

```text
coding-change/v1
```

默认目录：

```text
.agents/changes/
├── active/
└── archive/
```

如果目标项目已有正式 RFC / ADR / Spec / OpenSpec / Issue / Change 流程，并且能够承载 Requirement Traceability、Validation Matrix、Completion Audit 等语义，应优先复用项目已有机制，不为了使用 Agent_Skills 再平行造一套制度。

## 4. `project-context.json`

```text
.agents/project-context.json
```

是 Coding 在目标项目中生成的**本地可失效导航缓存**。它只帮助找到规则、Manifest、锁文件、文档和其他事实入口：

- 不是需求事实副本；
- 不是架构结论；
- 不是长期记忆；
- 不能替代当前代码、Contract、Schema/Migration、测试或运行结果；
- 应由目标项目 `.gitignore`、local exclude 或等价机制忽略，不提交 Git。

刷新入口：

```bash
python .agents/skills/coding/scripts/coding.py discover --root .
```

Runtime binary 安装还会把目标项目：

```text
/.agents/runtime/
```

加入 `.gitignore`，因为项目 Runtime 是本机平台 binary，不应被普通业务仓库提交。

## 5. Agent Skills Bootstrap 与项目安装

### 最终团队用户

推荐只拿对应平台：

```text
agent-skills-mcp[.exe]
```

在目标项目根运行。binary 会完成：

```text
当前 Release 全部正式 Skill
→ Project Payload / Reference Stub
→ .agents/runtime/ 项目 Runtime
→ AGENTS.md managed block
→ Codex / Cursor / Claude Code 项目级 MCP
```

最终用户不需要 Python 或 Agent_Skills 源仓库。

### Full/source 维护入口

从源仓库或受控 Full Kit 安装完整 Markdown Skill 后，可以显式运行 Coding Bootstrap：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

Bootstrap 的职责只有：

```text
目标项目自己的规则
→ 接入 Agent Skills managed block
→ 后续任务进入 Coding
```

它不会因为看到 `package.json`、`pyproject.toml`、`Cargo.toml` 等文件名就自行决定框架、数据库或架构。

已有目标项目 `AGENTS.md` 时，只有 Agent Skills managed markers 内由 Bootstrap 管理；marker 外项目原文必须保持。

完整安装与 Bootstrap 规则：

[`skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md`](skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md)

Runtime 单 binary、动态 Skill、Reference Stub 和项目 MCP 规则：

[`skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md`](skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md)

## 6. Runtime 目标项目额外状态

Runtime 模式的目标项目还会出现：

```text
.agents/
├── agent-skills-install.json   # Agent_Skills 安装 ownership / 版本 / digest
├── runtime/                    # 当前项目本地 MCP binary；忽略 Git
└── skills/                     # 当前 Release 正式 Skill；Reference 只放 Stub
```

`agent-skills-install.json` 不是业务事实源。它只证明上一版本哪些 Skill / managed 配置属于 Agent_Skills，使升级能够：

- 更新自己之前认领的 Skill；
- 删除新 Release 已移除、但旧 manifest 明确认领的 Skill；
- 保留项目自有不同名 Skill；
- 首次遇到未认领的同名 Skill 时 fail closed，而不是猜测性覆盖。

## 7. 从哪里继续读

普通使用者通常不需要浏览 `.agents` 全目录。按任务直接进入：

- 开发 / Bug / 方案 / Greenfield：[`skills/coding/README.md`](skills/coding/README.md)
- Code Review / Audit：[`skills/review/README.md`](skills/review/README.md)
- 文档 Review / 编写 / 更新：[`skills/docs/README.md`](skills/docs/README.md)
- 仓库整体安装、Runtime binary、Full/source 分发和 Release：[`../README.md`](../README.md)

不要机械读取所有 references；由对应 `SKILL.md` 的触发条件决定当前任务真正需要加载哪些规则。Runtime 项目里的 Reference Stub 也不能替代 MCP 返回的 canonical 原文。
