# `.agents` 使用说明

`.agents/` 用来保存**仓库内 AI / Coding Agent 的辅助能力和本地导航信息**。它不是产品代码目录，也不是另一套项目架构文档。

在任意目标项目中处理分析、设计、开发、Review、文档、PR、CI 或交付任务时，先遵守目标项目自己的 `AGENTS.md`、`CONTRIBUTING` 或同等上位规则，再加载本目录对应 Skill。目标项目规则负责“这个项目具体是什么”，这里的通用 Skill 负责“怎样可靠工作”。本 README 只帮助人快速判断“这里有哪些能力、什么时候用哪个 Skill”，**不能替代项目规则或各 Skill 的 `SKILL.md` 正式规则**。

## 1. 这个目录为什么存在

项目里的 AI Agent 需要两类东西：

1. **可执行的工作规则**：例如怎样可靠开发、怎样独立审查代码、怎样检查文档；
2. **可失效的本地导航信息**：例如当前仓库有哪些事实入口，帮助 Agent 少走弯路。

把它们放在 `.agents/` 下，可以和产品代码、正式架构文档分开，避免把 Agent 工作流混入业务实现。

当前结构：

```text
.agents/
├── README.md
├── project-context.json       # 本地生成，必须忽略，不提交 Git
├── changes/                   # 项目无既有治理且采用 Coding fallback 时使用
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

`.agents/changes/` 不是每个项目都必须出现。目标项目已有 OpenSpec、RFC/ADR、Issue/PR 或其他正式治理，并且能承载 Requirement Traceability、Validation Matrix、Completion Audit 等语义时，优先复用项目已有载体，不创建平行制度。

### `project-context.json`

这是 Coding Skill 生成或刷新的**本地项目发现缓存**，主要用于快速定位规则、Manifest、锁文件、文档和其他事实入口。

它只是导航缓存，不是当前实现的事实源。缓存可能过期；真正的事实仍然要回到当前代码、Contract、Schema/Migration、测试、锁文件和项目正式文档确认。

从仓库根目录刷新：

```bash
python .agents/skills/coding/scripts/coding.py discover --root .
```

这个文件**不提交 Git**。目标项目应把 `.agents/project-context.json` 放进 `.gitignore`、本地 exclude 或等价忽略机制。不要因为缓存里写了某个路径，就跳过当前仓库事实检查。

## 2. `coding`、`review` 和 `docs` 分别解决什么问题

| Skill | 主要解决的问题 | 常见任务 |
| --- | --- | --- |
| [`coding`](skills/coding/README.md) | 怎样可靠完成软件研发、验证和交付 | Greenfield、仓库分析、方案设计、功能开发、Bug 修复、重构、PR、CI、Release，以及 Review 前的仓库事实与风险路由 |
| [`review`](skills/review/README.md) | 怎样以独立审查者和测试专家视角检查实现、测试充分性和交付证据 | Code Review、PR Review、代码质量/安全/兼容审计、测试充分性分析、Review 驱动的补测试与修复闭环 |
| [`docs`](skills/docs/README.md) | 怎样保证技术文档与正确事实同步，并让人真正看懂 | 文档 Review、文档修复、README/架构/API/运维文档编写与更新、代码与文档一致性检查 |

最简单的判断方式：

```text
主要任务是在开发或修改软件实现？
→ 用 Coding
→ 完成前如果存在 Review Skill，Coding 会强制路由 Review

仓库还是空的、需要从需求建立工程基线？
→ 用 Coding 的 Greenfield / Repository Bootstrap 路由

主要任务就是 Code Review / Audit？
→ 先按项目规则和 Coding 恢复事实/风险边界
→ 然后进入 Review

主要任务是在检查、编写或更新技术文档？
→ 用 Docs

代码变化可能影响文档？
→ Coding 先做 Docs Impact
→ 有影响时再加载 Docs

Docs 检查时发现其实是代码错了？
→ Docs 输出 code_issue_detected
→ 返回 Coding 修实现
→ Docs 做 targeted re-review
```

`review` 不维护第二套 Coding 规范。它在同仓存在 Coding 时读取 Coding，把 Coding 作为研发规则事实源，只增加独立审查、Findings、测试专家方法和 re-review。

## 3. 在任意项目中怎样进入这三个 Skill

### 首次接入 / 升级 Agent_Skills

目标项目只有 `.agents/skills/` 但没有明确项目入口时，不同宿主 Agent 未必会自动知道应该先读取哪个 Skill。因此正式接入不仅是复制目录，还需要目标项目自己的根 `AGENTS.md` Overlay。

推荐从 Agent_Skills 源仓库执行：

```bash
python scripts/install.py --target <目标项目根目录>
```

安装器只同步：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

它不复制 Agent_Skills 源仓库自己的根 `AGENTS.md`，也不复制 `.agents/changes/` 或 `project-context.json`。目标项目已有 `.agents/changes/`、项目自有 Skill 和其他 `.agents` 内容不属于清理范围。

随后安装器自动调用：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

Bootstrap 的目标不是自动设计项目，而是建立稳定入口：

```text
目标项目 AGENTS.md
→ 先读取项目本地规则
→ 必须读取 .agents/skills/coding/SKILL.md
→ Coding 按真实任务加载 references
→ 适用时进入 review / docs
```

如果目标项目没有 `AGENTS.md`，Bootstrap 使用 Coding 自带模板创建项目 Overlay 初版，并只列出当前真实存在的高价值事实入口作为导航；不会根据 Manifest 文件名猜测框架、数据库或架构。

如果目标项目已有 `AGENTS.md`，Bootstrap 不重写原文，只通过下面的 managed block 边界追加或升级 Agent Skills 自管内容：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

marker 外原文字节保持不变。只有 start/end 不完整、重复或顺序错误时会拒绝修改，避免猜错边界后删除用户规则。

安装、升级、创建/补充 `AGENTS.md` 或修复 managed block 的完整规则见 [`13_目标项目安装与AGENTS_Bootstrap.md`](skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md)。

### 普通研发任务

```text
项目 AGENTS.md / CONTRIBUTING / 同等规则
→ Coding
→ 按任务读取最少充分代码 / Contract / Migration / 测试 / 文档
→ 实现与验证
→ Docs Impact
→ 完成前 Review
→ Review Skill（仓库存在时）
→ PR / CI / 交付
```

Review 发现实现缺陷且任务已有修复授权时：

```text
Review
→ 返回 Coding
→ Coding 按完整研发门禁修复并取得新鲜验证
→ Review re-review
```

### Greenfield / Repository Bootstrap

```text
用户目标 / 正式需求 / 运行环境 / 硬约束
→ Coding Greenfield 路由
→ 区分已决定与待决定技术边界
→ 关键长期选择按风险比较方案
→ 建立最小 Manifest / Lock / Build / Test / Package / Run 基线
→ 新鲜验证
→ Docs / Review / Delivery
```

这里的 Greenfield / Repository Bootstrap 是**工程基线建立流程**；前面的 Agent Skills Bootstrap 是**研发规则接入流程**。二者不要混为一件事：安装脚本不会替用户决定 Greenfield 项目的技术路线。

Greenfield 不表示可以让 Agent 自由猜技术栈。没有现成项目事实时，用户已确认决定、目标环境和正式约束就是上游事实；只有真正影响结果的关键未决项才提请决策。

### 显式 Code Review / Audit

```text
项目规则
→ Coding 完成仓库事实恢复、四维任务路由、工具链/风险/权限确认
→ Review 成为主要审查工作流
→ 独立重建需求、审查 diff/调用链/测试充分性
→ 输出 Findings 和证据边界
```

Review 默认只报告，不因为“做 Review”自动获得修改、提交或合并权限。

### 单独做文档任务

Docs 可以独立承担文档工作。如果目标项目通过 `AGENTS.md` 或其他上位规则要求所有仓库任务先经过统一研发入口，则实际链路是：

```text
项目规则
→ Coding 只完成仓库级事实恢复、风险和 Git/权限路由
→ Docs 成为本任务的主要工作流
→ Review Only / Review + Fix / Write / Update
```

这不表示“用 Docs 还要由 Coding 来写文档”。Coding 在这里负责项目门禁；真正的文档判断和写作由 Docs 负责。

## 4. 最常用的请求方式

不需要记复杂命令。在支持仓库访问的 Agent 中，直接把目标和授权写清楚即可。

### 用 Coding 开发

```text
使用 coding，基于当前仓库真实实现完成这个功能。
先恢复事实和判断风险等级，再按适用规则开发、测试、文档影响检查，并在完成前进入 review，最后按项目现有 PR/CI 门禁交付。
```

### 从零建立项目

```text
使用 coding 的 Greenfield 模式，从当前正式需求建立最小可维护工程基线。
不要预设编程语言或框架；先确认目标环境和硬约束，关键长期决策比较方案后再建立代码、依赖、build/test/package/run 闭环。
```

### 做 Code Review

```text
使用 coding + review 审查当前实现，只 Review，不修改代码。
先恢复当前仓库事实和任务边界；由 review 从独立审查和测试充分性角度给出 Findings、证据和风险。
```

### 从测试专家角度审查

```text
使用 review-and-test 审查这个功能的测试充分性。
从需求和失败风险反推应有证据；按真实边界区分 Mock、Backend/API/Persistence、Contract、Real Cross-component 和 External Probe，不用较弱层冒充未运行边界。
```

### 用 Docs 只检查文档

```text
使用 docs 检查当前技术文档是否和实际代码、Contract、Schema/Migration、配置、测试一致。
只 Review，不修改文件。
```

### 用 Docs 检查并修正文档

```text
使用 docs 检查并修正受影响文档。
从为什么存在、解决什么问题、数据/调用怎么流、代码在哪实现开始解释；术语用白话，必要时给最小例子。
如果发现是代码问题，不要让文档迎合 Bug，按 Docs → Coding 路由处理。
```

### 用 Docs 新写 README

```text
使用 docs 为这个模块补 README。
面向第一次接手项目的人，说明为什么存在、负责什么、不负责什么、主要调用/数据流、真实实现入口、怎么使用和排障。
不要复制完整 Schema 或代码形成第二套事实。
```

## 5. Coding Change 与项目治理

Coding 的通用语义是：

```text
Requirement Traceability
Validation Matrix
Completion Audit
新鲜验证
Ready / Delivery
```

Coding 自带 schema 当前只支持：

```text
coding-change/v1
```

不兼容旧 Change schema。

项目没有可复用正式治理时，默认 carrier 为：

```text
.agents/changes/active/
.agents/changes/archive/
```

如果项目已经正式使用顶层 `changes/active` / `changes/archive` 承载同类 Coding Change，可以继续沿用。项目已有 OpenSpec 等不同治理体系时，不要直接运行 `new-change` 造平行制度；先按项目规则确定这些通用语义应该由谁承载。

## 6. 哪些文件才是正式规则

请区分“使用说明”和“执行规则”：

```text
项目级规则
→ 目标项目自己的 AGENTS.md / CONTRIBUTING / 同等规则

Agent Skills 安装 / AGENTS Overlay 正式规则
→ skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md
→ skills/coding/assets/AGENTS.managed.md
→ skills/coding/assets/AGENTS.template.md

Coding 正式规则
→ skills/coding/SKILL.md
→ skills/coding/references/

Review 正式规则
→ skills/review/SKILL.md
→ skills/review/references/

Docs 正式规则
→ skills/docs/SKILL.md
→ skills/docs/references/

人类快速使用说明
→ 本 README
→ skills/coding/README.md
→ skills/review/README.md
→ skills/docs/README.md

本地可失效导航缓存
→ project-context.json（不提交 Git）
```

README 可以解释“怎么用”，但不应复制所有详细规则。README 与 `SKILL.md` 冲突时，以当前适用的上位项目规则和 `SKILL.md` 为准；安装/Overlay 边界还必须同时满足上述专用 reference 与模板 Contract。

## 7. 进一步阅读

- [Coding Skill 使用说明](skills/coding/README.md)
- [Coding 正式规则](skills/coding/SKILL.md)
- [目标项目安装与 AGENTS Bootstrap](skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md)
- [Review Skill 使用说明](skills/review/README.md)
- [Review 正式规则](skills/review/SKILL.md)
- [Docs Skill 使用说明](skills/docs/README.md)
- [Docs 正式规则](skills/docs/SKILL.md)
- [仓库根使用说明](../README.md)
