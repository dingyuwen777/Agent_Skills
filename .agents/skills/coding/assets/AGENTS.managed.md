<!-- agent-skills:managed:start -->
## Agent Skills 研发入口

本项目已接入 Agent_Skills。项目自己的 `AGENTS.md` / `CONTRIBUTING` / Spec / Contract / Schema / Migration / CI / 代码与测试负责说明“这个项目具体是什么”；Agent_Skills 负责说明“怎样可靠研发”。

处理本项目研发任务时：

1. 先读取并遵守当前目录及上级适用的项目规则，并以当前项目真实文件恢复技术栈、架构、Contract、Schema/Migration、CI、部署和设计事实；
2. 然后必须读取 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`；
3. 按 Router 选择本次真正需要的 Skill 与 References，不机械加载全部规则；
4. 不得用 Agent_Skills 的通用示例覆盖当前项目事实；
5. Router 缺失、无法读取或与更高优先级规则存在无法安全解析的冲突时，明确报告并停止依赖该 Router 的动作，不得假装已经遵守。

<!-- agent-skills:managed:end -->