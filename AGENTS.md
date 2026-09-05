# Agent_Skills AI Bootstrap

本文件是 Agent 进入 `Agent_Skills` 仓库时的**稳定入口**。它只负责判断当前使用模式并导航到唯一 Skill Router / 源仓库维护规则，不再保存第二套完整 Skill Router，也不再保存 Agent_Skills 自身的完整维护规范。

本文件不是最终用户说明，也**不得复制到目标项目**。最终人类使用说明见 [`USAGE.md`](USAGE.md)；Runtime 安装到目标项目时使用的是项目自己的 `AGENTS.md` managed block。

## 1. 使用 Agent_Skills 帮助另一个项目

如果当前任务的真实目标是另一个业务/技术项目，而这里只作为通用 Skill Library：

1. 首先读取**目标项目**当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则；如果根 `AGENTS.md` 含 `agent-skills:managed` marker，**marker 外的项目自有规则与事实仍必须正常读取和遵守**；
2. 再按任务需要从目标项目真实代码、Manifest/lock、Contract、Schema/Migration、配置、测试、CI、正式文档和设计事实恢复项目上下文；
3. Source Mode 下，目标项目中的 `agent-skills:managed` block、`.agents` 内 Runtime / Project Payload / Runtime Skill Projection、legacy install-state 或同类 Agent_Skills **安装资产**只用于识别 marker、ownership、安装版本与 drift；这些内容应保留其安装归属，但**不作为 Source Mode 的通用治理规则来源**，也不能覆盖当前 canonical Source；
4. 当前通用治理语义只从本仓库当前目标分支的 canonical Owner 取得；不得把目标项目旧安装资产中的 Runtime/MCP/披露/路由/加载说明复制、转述或改写到 marker 外项目 Overlay；
5. 然后读取本仓库唯一薄入口 [`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)；
6. 由 ENTRY 无条件进入 [`.agents/skills/router/SKILL.md`](.agents/skills/router/SKILL.md)，再按 Router 进入对应专业 `SKILL.md` 和本次真正命中的 References；
7. 目标项目事实优先于 Agent_Skills 通用示例，不从历史聊天或其他业务仓库猜当前实现；
8. 只读取当前任务直接相关的最少充分事实源，不机械读取全部 Skills、References 或 Markdown。

这种模式**通常不读取 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)**，因为当前不是在维护 Agent_Skills 源仓库；但命中第 4 节 Skill Mutation 时，必须按该节切换到 Agent_Skills Maintenance Mode。

## 2. 维护 Agent_Skills 源仓库本身

如果当前任务就是分析、开发、修改、Review、测试、交付或发布 `dingyuwen777/Agent_Skills`：

1. 读取 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)；
2. 读取 [`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)，并由其无条件进入 [`.agents/skills/router/SKILL.md`](.agents/skills/router/SKILL.md)；
3. 再按 Maintenance 与 Router 进入本次任务命中的专业 Skill / References；
4. 以当前目标分支真实文件、GitHub 状态和本轮新鲜验证为准，不从历史会话猜当前实现；
5. 不绕过本仓库 Change、Review、CI、PR、Git、Release 或其他质量门禁。

## 3. 失败边界

如果 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)、[`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)、Router、必需 Skill 或命中的 Reference 无法读取，必须明确指出缺失事实，并停止依赖该规则的动作；不得用旧记忆、摘要或推测声称“已经按 Skill 执行”。

## 4. 外部项目会话中的 Skill Mutation

当正在帮助另一个目标项目，但用户提出针对 **Skill 本身** 的维护意图，例如“更新 Skill”“修改 Skill”“新增 Skill”“删除 Skill”“重命名 Skill”、修改 Reference、迁移/拆分/合并/通用化规则，或明确要求“把这条规则同步到 Skill”时：

1. 不把当前业务项目中的 Runtime 安装副本、Reference Stub、缓存或历史聊天当作 canonical Skill 写入目标；
2. 先执行 **Mutation Target Resolution**：默认把 `dingyuwen777/Agent_Skills` 当前目标分支视为通用 Agent Skill 的唯一 canonical repository，并把当前动作目标切换为 Agent_Skills Maintenance Mode；
3. 本地 clone / worktree 只能是该 canonical repository 的工作 checkout。不得把 `$CODEX_HOME/skills`、目标项目 `.agents/skills`、插件缓存、Runtime / Project Payload、Release / 缓存 / Stub 作为替代写入目标，也不得创建或修改替代 Skill 后声称 canonical 已更新；
4. 进入同一 `Mutation Apply` 写入阶段时，先对 Agent_Skills **当前目标分支/HEAD** 完成一次本 `AGENTS.md`、[`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md)、[`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)、Router、Coding、规则内容守恒与受影响 Skill 的 canonical 重读。只要目标 HEAD、Ownership 和必需治理规则未变化，连续多文件写入**不逐文件机械重复重读**；发生 HEAD 漂移、Ownership/required Context 变化或写入前事实已失效时再重读；
5. 当前目标项目只继续提供本次变更的事实背景、失败证据和项目约束；项目特定技术栈、业务字段、Provider、Schema、部署、品牌或设计业务事实不得直接升级成通用 Skill 默认事实；
6. 如果用户明确说“只改当前项目规则”或明确指向项目自有 Skill，则保持当前项目 Ownership，不跨仓库同步；
7. 先区分 `Mutation Audit / Proposal` 与 `Mutation Apply`：**Mutation Audit / Proposal 只要求 canonical read** 能力；只要当前 canonical Source 可读，就可以完成审计、影响分析和修改建议，缺少写入/PR/CI 权限本身不阻塞只读结论。真正进入 **Mutation Apply** 后，才要求与当前动作匹配的 **write / Change / PR / CI / delivery** 能力；某一能力或权限缺失时，只阻塞依赖该能力的写入/交付并明确报告未同步/未交付，不得通过修改本地安装副本或口头声称“已同步”绕过。若连 canonical Ownership 或只读事实都无法安全恢复，则对应 Audit/Apply 都按依赖边界失败关闭；
8. Custom Instructions、Project instructions 或其他宿主提示可以作为进入本入口的薄触发器，但不是 canonical Skill 正文，也不会自动授予 GitHub 写入、PR、merge 或 Release 权限。

本节是 **Skill Mutation 意图与 canonical Ownership 的源仓库唯一 Bootstrap Owner**。Mutation 的详细内容守恒、Skill/Reference 新增删除重命名与跨仓库同步细则由 [`coding/references/15_规则内容守恒与Skill维护.md`](.agents/skills/coding/references/15_规则内容守恒与Skill维护.md) 负责；进入 Agent_Skills 后的 Change、Review、CI、PR、main 验证与当前 Change 清理继续由 [`.agents/MAINTENANCE.md`](.agents/MAINTENANCE.md) / Coding 现有交付规则负责。普通 Runtime 安装给目标项目的 Router 和 managed block 不复制这套源仓库维护治理；Custom Instructions 只需要把相应意图引导回当前根 `AGENTS.md`，再以当前源码事实继续执行。
