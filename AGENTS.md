# Agent_Skills AI Bootstrap

本文件是 Agent 进入 `Agent_Skills` 仓库时的**稳定入口**。它只负责判断当前使用模式并导航到唯一 Skill Router / 源仓库维护规则，不再保存第二套完整 Skill Router，也不再保存 Agent_Skills 自身的完整维护规范。

本文件不是最终用户说明，也**不得复制到目标项目**。最终人类使用说明见 `USAGE.md`；Runtime 安装到目标项目时使用的是项目自己的 `AGENTS.md` managed block。

## 1. 使用 Agent_Skills 帮助另一个项目

如果当前任务的真实目标是另一个业务/技术项目，而这里只作为通用 Skill Library：

1. 首先读取**目标项目**当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则；
2. 再按任务需要从目标项目真实代码、Manifest/lock、Contract、Schema/Migration、配置、测试、CI、正式文档和设计事实恢复项目上下文；
3. 然后读取本仓库 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`；
4. 按 Router 进入对应 `SKILL.md` 和本次真正命中的 References；
5. 目标项目事实优先于 Agent_Skills 通用示例，不从历史聊天或其他业务仓库猜当前实现；
6. 只读取当前任务直接相关的最少充分事实源，不机械读取全部 Skills、References 或 Markdown。

这种模式**不读取 `.agents/MAINTENANCE.md`**，因为当前不是在维护 Agent_Skills 源仓库。

## 2. 维护 Agent_Skills 源仓库本身

如果当前任务就是分析、开发、修改、Review、测试、交付或发布 `dingyuwen777/Agent_Skills`：

1. 读取 `.agents/MAINTENANCE.md`；
2. 读取 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`；
3. 再按 Maintenance 与 Router 进入 Coding 及任务命中的专业 Skill / References；
4. 以当前目标分支真实文件、GitHub 状态和本轮新鲜验证为准，不从历史会话猜当前实现；
5. 不绕过本仓库 Change、Review、CI、PR、Git、Release 或其他质量门禁。

## 3. 失败边界

如果 `.agents/MAINTENANCE.md`、Router、必需 Skill 或命中的 Reference 无法读取，必须明确指出缺失事实，并停止依赖该规则的动作；不得用旧记忆、摘要或推测声称“已经按 Skill 执行”。