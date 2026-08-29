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

## 11. Skill Mutation / canonical Repository Ownership

本节拥有“**什么时候从目标项目工作切换为 Agent_Skills 本身的维护任务**”这一跨仓库路由。详细的内容守恒、Change、测试、Review、Git/CI 与交付细则仍由 Coding / Maintenance / ref16 承担，不在这里复制第二套研发流程。

### 11.1 Mutation 触发

以下针对 Skill 本身的用户意图都属于 **Skill Mutation**：

- “更新 Skill”“修改 Skill”“新增 Skill”“删除 Skill”“重命名 Skill”；
- 新增、修改、删除、重命名某个 Reference；
- 把当前项目中发现的通用规则“同步到 Skill”；
- 规则迁移、拆分、合并、通用化、Ownership 调整；
- 修改跨 Skill Router，或与某个 Skill 直接归属的 metadata、assets、scripts、tests。

当当前会话正在处理另一个目标项目，但命中上述意图时，默认 canonical Owner 是：

```text
dingyuwen777/Agent_Skills
```

也就是从“用 Agent_Skills 帮助目标项目”切换为“维护 Agent_Skills canonical 源仓库”。目标项目继续作为需求背景、调用链、失败证据和项目约束的事实来源，但不成为通用 Skill 正文 Owner。

如果用户明确说“只改当前项目规则”“不要同步到 Agent_Skills”，或明确指向目标项目自己的 **项目自有 Skill**，则保持目标项目 Ownership，不跨仓库写 Agent_Skills。若现有仓库事实无法安全判断某个 Skill 属于 Agent_Skills 还是项目自有内容，必须先报告 Ownership 不确定并停止相关写入，不猜测性覆盖任一方。

### 11.2 canonical 明文事实源

通用 Agent Skill 的 canonical 明文只来自 Agent_Skills 当前源码仓库中的正式 Owner：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
.agents/skills/ROUTER.md
以及该 Skill 明确认领的 metadata / assets / scripts / tests
```

以下都**不是 canonical Skill 写入目标**：

- 目标项目中的 Runtime / Project Payload **本地安装副本**；
- Reference Stub；
- MCP 返回结果的旧缓存；
- 历史聊天、摘要或旧版本复制件；
- ChatGPT Custom Instructions / Project instructions 中的转述。

Runtime 安装副本和 Stub 用于目标项目运行与加载，不用于反向维护 canonical 规则。需要修改 Skill 时，必须回到 `dingyuwen777/Agent_Skills` 当前目标分支重新读取真实源码；不得直接编辑本地安装副本后声称“Skill 已更新”。

### 11.3 Mutation 固定入口

进入 Agent_Skills Mutation 后，在任何 canonical 写入前至少执行：

```text
重新读取 Agent_Skills 当前目标分支根 AGENTS.md
→ .agents/MAINTENANCE.md
→ .agents/skills/ROUTER.md
→ .agents/skills/coding/SKILL.md
→ coding/references/16_规则内容守恒与Skill维护.md
→ 本次真正受影响 Skill 的 SKILL.md / references
```

如果 Mutation 会影响 managed block / Bootstrap，则再读 ref13；影响 Runtime、Project Payload、Bundle、Stub、MCP、正式 Skill 分发、Skill 删除/重命名的运行时可达性时，再读 ref14。随后按 Agent_Skills Maintenance/Coding 的当前 Change、TDD、独立 Review、CI、PR、main 新鲜 CI 和 archive 门禁执行，不建立一套 Mutation 专用的平行交付流程。

当前宿主只有只读 GitHub 能力、没有 Agent_Skills 源仓库权限、没有所需写权限或不能执行仓库要求的 PR/CI 门禁时，明确报告未同步/未交付，不得改本地安装副本冒充 canonical 写入，也不得口头声称“已同步”。

### 11.4 universal 与 project-specific 边界

只有可跨项目、跨业务复用的研发方法、失败处理、验证责任、通用工具/流程规则才进入 Agent_Skills。以下项目特定事实继续由目标项目自己的 AGENTS / Spec / Contract / Schema / Design System /代码等 Owner 管理：

- 具体语言、Runtime、框架、数据库和包管理器选择；
- 业务字段、Prompt、Provider、平台、Schema/Migration 和数据口径；
- 项目 CI、部署环境、Release/恢复细节；
- 品牌、页面尺寸、业务组件、设计 Token、动态字段和业务流程。

当用户明确要求“更新 Skill”，但输入同时混有通用规则与项目特定事实时，先拆分语义：只把可证明可复用的通用部分写入 Agent_Skills；项目特定部分仍留在目标项目 Owner。若没有可安全抽取的通用规则，则不为了满足“同步”字样而污染 Agent_Skills，并明确说明为什么本次没有 canonical Skill 变更。

### 11.5 新增、删除与重命名的 Router 责任

- 新增 Skill：正式入口仍是 `.agents/skills/<name>/SKILL.md`，不得给 Runtime 增加固定白名单；如果本 Router 展示“当前 Catalog”，必须同步可读导航，但该导航永远不是分发白名单。
- 删除 Skill：必须同步删除/修改 Router 当前 Catalog 与其他 live Handoff/引用，不能留下指向不存在 Skill 的导航。
- 重命名 Skill：同时视为旧 Skill 删除 + 新 Skill 建立，并把 Reference ID namespace、Runtime 安装路径、Stub、Bundle/Payload、live links 等潜在 Contract 影响交给 ref14/ref16 审查，不能只改目录名。
- Reference 新增/删除/重命名、规则拆分/合并/通用化的内容守恒细则由 ref16 承担。

Custom Instructions 可以帮助 ChatGPT 在任意会话更早发现本 Router，但它不是本规则的上位事实源；真正的 Mutation 行为以当前目标项目规则、当前 Agent_Skills 源仓库和更高优先级指令为准。
