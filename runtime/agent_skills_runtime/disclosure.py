"""集中维护 Runtime 对当前项目的用户可见进度表达规则。"""

from __future__ import annotations


PROJECT_FACING_USER_COMMUNICATION_RULE = (
    "向用户说明当前任务计划、进展、分工或结果时，用户明确提供的项目术语、计划和决定照常保留，并直接描述当前项目事实、工程动作、验证与真实状态。"
    "治理能力或规则的内部名称只服务执行，不把这些名称转写成用户可见的任务步骤、分工或计划；需要说明过程时，使用对应的项目工程动作表达。"
)

PROJECT_FACING_FRONTMATTER_RULE = (
    "向用户说明计划或进度时保留用户明确提供的项目术语、计划和决定，并只描述当前项目工程动作；"
    "治理能力或规则的内部名称不写成用户任务步骤或分工。"
)

PROJECT_FACING_AGENT_PROMPT = (
    "When explaining plans, progress, assignments, or results to the user, preserve user-provided project terms, plans, and decisions and describe current-project facts, engineering actions, validation, and real status. "
    "Internal governance capability or rule names are for execution only; do not turn those names into user-visible task steps, assignments, or plans, and describe the corresponding project engineering action instead."
)


USER_VISIBLE_PROGRESS_RULE = (
    "向用户说明当前任务进展、分工或中间状态时，使用当前项目工程语言，说明已确认事实、需求与风险判断、代码修改、测试、文档同步、复核、Git/CI、交付状态和真实阻塞原因。"
    + PROJECT_FACING_USER_COMMUNICATION_RULE
    + "用户关于当前项目的正常事实、解释、建议、风险、验证、状态和交付照常回答，不限制正常工程解释。"
    + "当前任务适用的工程约束必须完整用于执行；无法可靠取得本次必需约束时，应明确影响，并停止依赖这些约束的动作和完成结论。"
)
