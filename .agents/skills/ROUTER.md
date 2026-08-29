# Agent Skills 统一研发路由

本文件是 Agent_Skills **唯一的跨 Skill Catalog / Router 事实源**。它负责回答：当前任务应先恢复哪些项目事实、进入哪些正式 Skill、何时加载哪些 Reference，以及加载失败时必须怎样停止或降级。

它不是第二套 Coding / Review / Docs / Figma 专业规则，也不是目标项目的技术栈说明。各 Skill 的详细规则仍由自己的 `SKILL.md + references` 承担；目标项目自己的规则和真实文件负责说明“这个项目具体是什么”。

## 1. 先建立目标项目事实

无论通过 ChatGPT 网页端直接读取 Agent_Skills 源仓库，还是通过 Release Runtime 在目标项目中使用本 Router，都必须先读取当前目标项目及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则，再按任务需要读取真实代码、Manifest/lock、Contract、Schema/Migration、配置、测试、CI、正式文档和当前设计事实。

项目自己的事实优先于 Agent_Skills 中的通用示例。Agent_Skills 规定“怎样可靠工作”，不能反向发明“这个项目是什么”。

以下事实必须来自目标项目当前真实内容或用户/Owner 已确认决定：

- 语言、Runtime、编译器、包管理器、Manifest、锁文件和构建/测试工具；
- Web/Backend/Frontend/Mobile/Desktop/CLI/Library/Data/Embedded/IaC 等实际项目形态；
- 框架、数据库、缓存、消息系统、外部 Provider 与部署平台；
- 模块职责、目录 Owner、公共 API/ABI/CLI、Contract、Schema、Migration 和数据语义；
- 正式需求、Roadmap、ADR/RFC/Spec/OpenSpec/Change、CI Job、发布和回滚流程；
- Figma/设计系统中的项目品牌、页面尺寸、Token、组件名、业务字段、Prototype、动态数据和用户流程。

看到 `package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、`pom.xml` 等文件，只能证明对应事实入口存在，**不能单凭文件名推出 React、FastAPI、PostgreSQL** 或其他具体技术路线。Greenfield / Prototype 没有稳定工程事实时，先以用户已确认目标、硬约束和预期运行环境作为上游事实，再建立最小工程基线。

## 2. 正式 Skill Catalog 与动态发现

正式 Skill 集合始终从：

```text
.agents/skills/*/SKILL.md
```

动态发现。当前仓库实际存在：

| Skill | 当前职责 | 正式入口 |
| --- | --- | --- |
| `coding` | 通用研发、调试、验证、Change、Git/CI/交付与跨 Skill 主流程 | `.agents/skills/coding/SKILL.md` |
| `review` | 独立 Review、Findings、测试充分性与 re-review | `.agents/skills/review/SKILL.md` |
| `docs` | 技术文档事实同步、审查、编写与更新 | `.agents/skills/docs/SKILL.md` |
| `figma` | Figma 设计事实、Canvas/Prototype、设计系统、Ready 与 Design-to-Code 交接 | `.agents/skills/figma/SKILL.md` |

这些名称只是当前 Catalog，**不是分发白名单**。新增合法 `.agents/skills/<name>/SKILL.md` 后，Runtime、Project Payload、manifest、测试和 Release 仍应依赖动态发现，而不是要求在 Bootstrap 里同步另一份固定名单。

Review、Docs、Figma 不复制第二套 Coding 研发规则；Coding 也不复制第二套 Figma/Docs/Review 专业细则。

## 3. 每个研发任务的固定入口

处理代码分析、方案设计、功能开发、Bug 修复、重构、测试、Review、文档、Figma、Git、CI、PR、Release 或交付任务时：

1. 先按第 1 节恢复当前目标项目事实，只读取与当前任务直接相关的最少充分内容；
2. 然后必须读取 `.agents/skills/coding/SKILL.md`，按项目形态、研发阶段/任务类型、实际语言/工具链和 L1/L2/L3 风险完成任务路由；
3. Coding Skill 要求读取某个 `references/` 文件时，必须在执行对应动作前取得该 Reference 的完整正式原文，不能只读 `SKILL.md` 后凭印象补流程；
4. 只有任务命中其他专业 Skill 时才进入对应 `SKILL.md`，不机械读取全部 Skills 或全部 References；
5. 能由当前目标项目仓库确认的事实先自行检查，不从历史聊天、旧缓存或 Skill 示例猜当前实现。

`coding` 是当前研发主流程的核心锚点；改变这一上位入口关系属于独立架构变化，不能因为新增 Skill 就静默改变。

## 4. Reference 的两种加载模式

### 4.1 源码直接读取模式

当 Agent（例如 ChatGPT 网页端通过 GitHub）能够访问 Agent_Skills 源仓库，且命中的 `references/<file>.md` 是完整 canonical Markdown 时：

```text
SKILL.md
→ 命中 Reference
→ 直接读取 Agent_Skills 源仓库中的 canonical Reference
→ 以该文件当前完整正文作为正式规则
```

不得使用历史聊天中的旧版本、摘要、转述或记忆替代当前 canonical 文件。

### 4.2 Runtime 安装模式

当目标项目中的同名 Reference 是 Agent Skills Runtime Stub 时：

1. 必须按 Stub 指示调用项目本地 Agent Skills MCP 的 `agent_skills_load_context`；
2. 使用 Stub 中的稳定 ID 请求正文；
3. 比较 MCP 返回的 `SHA256` 与 Stub 的 Expected SHA256；
4. 把返回的 `canonical_text` 当作该 Reference 的完整正式原文；
5. MCP 不可用、ID 不存在、SHA256 不一致、没有 `canonical_text` 或原文无法取得时，必须明确报告，并停止依赖该 Reference 的动作；
6. 不得把 Stub、旧缓存、旧记忆或自己补写的摘要当成 canonical 规则正文。

这两种模式只改变 Reference **如何取得**，不改变同一 Skill/Reference 的正式语义。

## 5. Bootstrap / Runtime 专项路由

如果任务是首次安装、升级 Agent_Skills、创建/补充目标项目 `AGENTS.md` 或修复 Agent Skills managed block，必须读取：

```text
.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md
```

如果任务涉及本地 MCP Runtime 构建/Release/项目安装/升级、Project Payload、Reference Stub、Bundle、installation manifest 或宿主 MCP 配置，还必须读取：

```text
.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md
```

不得自由重写项目 Overlay、managed ownership 或 Runtime Contract。

## 6. Figma 路由

如果任务涉及 Figma 创建、修改、整理、审查、设计系统、Prototype、正式设计基线验收，或者按 Figma 实现/替换页面，且 `.agents/skills/figma/SKILL.md` 存在：

1. 必须按 Coding 的任务路由读取并执行 Figma Skill；
2. Figma 负责设计事实、Canvas/Prototype、设计修复和 `READY / READY_WITH_NOTES / NOT_READY`；
3. `NOT_READY` 时不得把已知设计缺陷直接写入生产实现；
4. 达到 `READY / READY_WITH_NOTES` 后再回到 Coding，完成真实代码、测试、Review、CI、Git 与交付；
5. Figma Ready 不能冒充代码、PR 或 Release Ready。

## 7. Review 路由

Coding Skill 判断需要独立 Review，或用户显式要求 Code Review / Audit，且 `.agents/skills/review/SKILL.md` 存在时，必须读取并按 Review Skill 执行。

Review 负责独立 Findings、测试充分性和 re-review，不维护第二套 Coding 研发规则；发现问题需要修复时回到 Coding 主流程处理并重新验证。

## 8. Docs 路由

Coding Skill 判断存在文档影响，或用户显式要求技术文档审查、事实同步、编写或更新，且 `.agents/skills/docs/SKILL.md` 存在时，必须读取并按 Docs Skill 执行。

Docs 负责技术文档事实同步与文档质量，不复制第二套 Coding 研发规范；默认只读取受影响文档域，不机械扫描所有 Markdown。

## 9. 失败、冲突与权限边界

- 某个必需 Skill、Router 或 Reference 文件缺失、无法读取，或者 Runtime Stub 无法取得并验证 canonical 原文时，明确报告真实阻塞，不得假装已经遵守；
- 通用 Skill 与更高优先级指令或更具体项目规则存在冲突时，遵守更高优先级和更具体规则；无法安全解析冲突时停止受影响动作并提请 Owner，而不是自行选择有利解释；
- 不绕过目标项目已有 CI、Branch Protection、PR、Release、Migration、安全或其他质量门禁；
- 没有相应授权时，不自动获得创建/切换分支、修改文件、提交、推送、创建 PR、合并、发布、部署、数据库写入或其他外部副作用权限；
- 不覆盖项目已有工作，不用 `git reset --hard`、`git clean -fd`、强制推送或历史重写制造“干净状态”。

## 10. Router 自身的维护边界

本文件只拥有**跨 Skill 的发现、入口、加载和 Handoff**。以下细节必须继续留在各自 Owner：

- Coding 的 L1/L2/L3、TDD、调试、验证、Change、Git/CI/交付细节 → Coding `SKILL.md + references`；
- Review 的 Findings、测试审查与 re-review 方法 → Review；
- Docs 的文档事实、范围与写作/审查方法 → Docs；
- Figma 的 Canvas、Prototype、Owner、状态、Ready、失败处理与写后复核 → Figma；
- Runtime 的 Bundle/Payload/Stub/MCP/安装/升级/回滚细节 → Coding ref13/ref14 + Runtime 实现。

不能为了让入口“自包含”再把这些专业细则复制回根 `AGENTS.md`、`AGENTS.managed.md` 或本 Router。
