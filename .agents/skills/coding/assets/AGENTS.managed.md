<!-- agent-skills:managed:start -->
## Agent Skills 研发入口

本项目已接入 Agent_Skills。项目自己的 `AGENTS.md` / `CONTRIBUTING` / Spec / Contract / Schema / Migration / CI / 代码与测试负责说明“这个项目具体是什么”；Agent_Skills 负责说明“怎样可靠研发”。

处理本项目研发任务时：

1. 先读取并遵守当前目录及上级适用的项目规则，并以当前项目真实文件恢复技术栈、架构、Contract、Schema/Migration、CI、部署和设计事实；
2. 如果用户直接提出开发、修复、重构等**自然语言研发任务**，且这是项目**首次接入** Agent_Skills、当前 `AGENTS.md` 在 **managed block 外**尚未记录 `Project Governance Bootstrap` **状态：已校准**，或本次任务暴露长期治理事实可能已经漂移，则在任何实质性生产代码修改前先通过 Router / Coding 执行 `Project Governance Bootstrap`：由当前宿主大模型调查仓库真实实现，只维护项目自有 Overlay；完成后重新读取最终 `AGENTS.md`，再继续用户原始研发任务；
3. 然后必须读取 [`.agents/skills/ROUTER.md`](../../ROUTER.md)；
4. 按 Router 选择本次真正需要的 Skill 与 References，不机械加载全部规则；
5. 不得用 Agent_Skills 的通用示例覆盖当前项目事实；
6. Agent_Skills 安装器认领的 `.agents` 受管运行资产用于本项目运行，不属于项目自有规则；项目自己的长期规则应维护在项目自身正式事实源中，不直接手工修改受管运行资产；
7. Router 缺失、无法读取，或与更高优先级规则存在无法安全解析的冲突时，明确报告并停止依赖对应 Agent_Skills 路由，不得假装已经遵守。

<!-- agent-skills:managed:end -->