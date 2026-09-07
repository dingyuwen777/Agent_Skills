"""集中维护 Runtime 对当前项目的用户可见进度表达规则。"""

from __future__ import annotations


PROJECT_FACING_USER_COMMUNICATION_RULE = (
    "向用户说明当前任务计划、进展、分工或结果时，用户明确提供的项目术语、计划和决定照常保留，并直接描述当前项目事实、工程动作、验证与真实状态。"
    "治理规则名称、规则选择/取得/加载步骤或执行机制只服务内部执行，不把它们转写成用户可见的任务步骤、分工或计划；不要用‘先使用某规则、再切换到另一规则’一类表述描述工作。"
)

PROJECT_FACING_FRONTMATTER_RULE = (
    "向用户说明计划或进度时保留用户明确提供的项目术语、计划和决定，并只描述当前项目工程动作；"
    "不把治理规则名称、规则选择/取得/加载步骤或执行机制写成用户任务步骤或分工。"
)

PROJECT_FACING_AGENT_PROMPT = (
    "When explaining plans, progress, assignments, or results to the user, preserve user-provided project terms, plans, and decisions and describe current-project facts, engineering actions, validation, and real status. "
    "Governance rule names, rule-selection, rule-acquisition, rule-loading steps, and execution mechanisms are for internal execution only; do not turn them into user-visible task steps, assignments, or plans, and do not narrate the work as using one governance rule and then switching to another."
)


USER_VISIBLE_PROGRESS_RULE = (
    "向用户说明当前任务进展、分工或中间状态时，使用当前项目工程语言，说明已确认事实、需求与风险判断、代码修改、测试、文档同步、复核、Git/CI、交付状态和真实阻塞原因。"
    + PROJECT_FACING_USER_COMMUNICATION_RULE
    + "用户关于当前项目的正常事实、解释、建议、风险、验证、状态和交付照常回答，不限制正常工程解释。"
    + "当前任务适用的工程约束必须完整用于执行；无法可靠取得本次必需约束时，应明确影响，并停止依赖这些约束的动作和完成结论。"
)
