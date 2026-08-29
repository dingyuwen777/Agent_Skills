# Agent_Skills AI Bootstrap

本文件是 Agent 进入 `Agent_Skills` 仓库时的**稳定入口**。它只负责判断当前使用模式并导航到唯一 Skill Router / 源仓库维护规则，不再保存第二套完整 Skill Router，也不再保存 Agent_Skills 自身的完整维护规范。

本文件不是最终用户说明，也**不得复制到目标项目**。最终人类使用说明见 `USAGE.md`；Runtime 安装到目标项目时使用的是项目自己的 `AGENTS.md` managed block。

## 1. 使用 Agent_Skills 帮助另一个项目

如果当前任务的真实目标是另一个业务/技术项目，而这里只作为通用 Skill Library：

1. 首先读取**目标项目**当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则；
2. 再按任务需要从目标项目真实代码、Manifest/lock、Contract、Schema/Migration、配置、测试、CI、正式文档和设计事实恢复项目上下文；
3. 然后读取本仓库 `.agents/skills/ROUTER.md`；
4. 按 Router 进入对应 `SKILL.md` 和本次真正命中的 References；
5. 目标项目事实优先于 Agent_Skills 通用示例，不从历史聊天或其他业务仓库猜当前实现；
6. 只读取当前任务直接相关的最少充分事实源，不机械读取全部 Skills、References 或 Markdown。

这种模式**通常不读取 `.agents/MAINTENANCE.md`**，因为当前不是在维护 Agent_Skills 源仓库；但命中第 4 节 Skill Mutation 时，必须按该节切换到 Agent_Skills Maintenance Mode。

## 2. 维护 Agent_Skills 源仓库本身

如果当前任务就是分析、开发、修改、Review、测试、交付或发布 `dingyuwen777/Agent_Skills`：

1. 读取 `.agents/MAINTENANCE.md`；
2. 读取 `.agents/skills/ROUTER.md`；
3. 再按 Maintenance 与 Router 进入 Coding 及任务命中的专业 Skill / References；
4. 以当前目标分支真实文件、GitHub 状态和本轮新鲜验证为准，不从历史会话猜当前实现；
5. 不绕过本仓库 Change、Review、CI、PR、Git、Release 或其他质量门禁。

## 3. 失败边界

如果 `.agents/MAINTENANCE.md`、Router、必需 Skill 或命中的 Reference 无法读取，必须明确指出缺失事实，并停止依赖该规则的动作；不得用旧记忆、摘要或推测声称“已经按 Skill 执行”。

## 4. 外部项目会话中的 Skill Mutation

当正在帮助另一个目标项目，但用户提出针对 **Skill 本身** 的维护意图，例如“更新 Skill”“修改 Skill”“新增 Skill”“删除 Skill”“重命名 Skill”、修改 Reference、迁移/拆分/合并/通用化规则，或明确要求“把这条规则同步到 Skill”时：

1. 不把当前业务项目中的 Runtime 安装副本、Reference Stub、缓存或历史聊天当作 canonical Skill 写入目标；
2. 默认把 `dingyuwen777/Agent_Skills` 视为通用 Agent Skill 的 canonical repository，并把当前动作目标切换为 Agent_Skills Maintenance Mode；
3. 在任何写入前重新读取 Agent_Skills **当前目标分支**的本 `AGENTS.md`、`.agents/MAINTENANCE.md` 和 `.agents/skills/ROUTER.md`，再由 Router/Coding 进入规则内容守恒与受影响 Skill；
4. 当前目标项目只继续提供本次变更的事实背景、失败证据和项目约束；项目特定技术栈、业务字段、Provider、Schema、部署、品牌或设计业务事实不得直接升级成通用 Skill 默认事实；
5. 如果用户明确说“只改当前项目规则”或明确指向项目自有 Skill，则保持当前项目 Ownership，不跨仓库同步；
6. 如果无法从当前仓库事实安全判断 Skill Ownership，或当前宿主没有 Agent_Skills 所需读取/写入权限，必须明确报告并停止对应写入，不得通过修改本地安装副本或口头声称“已同步”来绕过；
7. Custom Instructions、Project instructions 或其他宿主提示可以作为进入本入口的触发器，但不是 canonical Skill 正文，也不会自动授予 GitHub 写入、PR、merge 或 Release 权限。

完整的 Mutation 触发、canonical Ownership、项目事实防污染和维护流程由 `.agents/skills/ROUTER.md` 与 `.agents/MAINTENANCE.md` 负责，本 Bootstrap 不复制第二套详细规则。
