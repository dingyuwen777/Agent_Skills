# Agent Skills Entry

稳定 Source Mode 薄入口。

1. 先读目标项目及上级适用的 `AGENTS.md`、`CONTRIBUTING` 等规则；
2. 从当前真实文件/机器事实恢复最少充分事实；
3. 无条件读取 [`.agents/skills/router/SKILL.md`](router/SKILL.md)，由 Router 选择所需 Skill/References；
4. 项目事实和上位指令优先，不用历史聊天或缓存猜实现；
5. 必需 Router/Skill/Reference 无法读取或验证时，说明影响并停止依赖动作。

普通项目任务保持专业执行完整，项目事实、解释、建议、风险、验证和交付照常呈现。Source Mode 维护 Agent_Skills 时可讨论内部导航；Runtime 详细边界由其 canonical Owner 负责。
