<!-- agent-skills:managed:start -->
## Agent Skills 研发入口

本项目已接入 Agent_Skills。项目自己的 `AGENTS.md` / `CONTRIBUTING` / Spec / Contract / Schema / Migration / CI / 代码与测试负责说明“这个项目具体是什么”；Agent_Skills 负责说明“怎样可靠研发”。

处理本项目研发任务时：

1. 先读取并遵守当前目录及上级适用的项目规则，并以当前项目真实文件恢复技术栈、架构、Contract、Schema/Migration、CI、部署和设计事实；
2. 然后必须读取 `.agents/skills/ROUTER.md`；
3. 按 Router 选择本次真正需要的 Skill 与 References，不机械加载全部规则；
4. 不得用 Agent_Skills 的通用示例覆盖当前项目事实；
5. 如果用户提出 **Skill Mutation**（例如“更新 Skill”或要求把通用规则同步到 Skill），不得把本项目 `.agents/skills/` 下的 Runtime **本地安装副本**当作 canonical 明文直接维护；必须按 Router 的 Mutation 路由判断 canonical Owner。用户明确要求“只改当前项目规则 / 项目自有 Skill”时保持项目 Ownership；
6. Router 缺失、无法读取、canonical 源仓库不可达/无所需权限，或与更高优先级规则存在无法安全解析的冲突时，明确报告并停止依赖该 Router 或对应同步动作，不得假装已经遵守或已经同步。

<!-- agent-skills:managed:end -->