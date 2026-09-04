---
schema: coding-change/v1
id: CHG-20260904-134355-runtime-output-identity-privacy
title: 收口 Runtime 内部能力身份的用户可见披露边界
level: L3
status: proposed
owner: dingyuwen777
branch: chg/runtime-output-identity-privacy
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas:
  - runtime-disclosure
  - project-payload
  - project-bootstrap
  - skill-mutation
affected_paths:
  - .agents/skills/ENTRY.md
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/assets/AGENTS.template.md
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - runtime/agent_skills_runtime/runtime.py
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - runtime/agent_skills_runtime/project_payload.py
  - runtime/README.md
  - USAGE.md
  - .agents/skills/coding/tests/test_runtime_progress_privacy.py
  - .agents/skills/coding/tests/test_runtime_skill_projection.py
contracts:
  - Runtime 用户可见表达 Contract
  - Runtime Skill Projection Contract
  - Project Payload native metadata Contract
  - 目标项目 AGENTS Bootstrap Contract
data_changes: []
---

# 目标

修复 #199：在不削弱 Runtime 专业 Skill 路由、Handoff、required canonical Context、Source/Runtime 同源和动态分发能力的前提下，阻止模型把内部 Skill/Reference/Router/路由/Handoff identity 转写成用户可见进度，同时把目标项目 `AGENTS.md` 收敛回纯项目侧规则与 Bootstrap 边界。

# 方案边界

- 不从模型内部删除 Skill identity/frontmatter/routing metadata；不通过最终字符串 replace/filter 伪造隐私。
- 目标 `AGENTS.md` 不再承担 Runtime disclosure 规则，只保留项目事实优先、项目规则优先、首次治理校准、fail-closed 和安装 ownership 必需边界。
- Runtime 输出边界由 shared Entry + 每轮 Runtime progress rule + Runtime Skill Projection 统一强化。
- Project Payload 中 native agent metadata 采用 Runtime 视图，去掉 `$skill`、内部 Skill 路径和命名式跨 Skill 指令，但保留专业行为、授权/失败边界和回程语义。
- 规则必须对未来动态新增 Skill 自动生效，不维护固定 Skill 名单。
- 宿主 UI 自己生成的 activity/trace 不是 Prompt/Skill/Runtime 可控制文本，不做不可实现承诺。

# 必须保持不变

- Source Mode 可正常查看/讨论 canonical Skill、Reference、路径、Stable ID 与路由过程。
- Runtime 动态 Skill Catalog、frontmatter、`agent-routing:v1` metadata、专业 Core 与 Handoff 完整保留。
- canonical Reference exact-text/hash、Bundle v3、Task Route evaluator、required Context 和 install-state schema 不变。
- Project Payload schema 不因本次变更升级；若实现无法在 v2 内安全表达，必须先重新审议，不静默迁移。
- 项目自有 `AGENTS.md` marker 外文本和其他项目资产继续保持。
- Context Budget 不通过抬阈值或删测试解决。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：目标 AGENTS 不承担 disclosure 自我说明 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC1 | not_satisfied | 待 Red→Green。 |
| R2 | AC2：所有 Agent 可控用户文本禁止内部能力 identity 转写 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC2 | not_satisfied | 待 Red→Green。 |
| R3 | AC3：Runtime native metadata 不分发命名式内部导航 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC3 | not_satisfied | 待 Red→Green。 |
| R4 | AC4：动态 Skill Projection 自动注入输出 guard，内部语义保留 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC4 | not_satisfied | 待 Red→Green。 |
| R5 | AC5：永久回归覆盖真实失败模式与动态 future Skill | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC5 | not_satisfied | 先写 Red。 |
| R6 | AC6：Source/Runtime、Catalog、Reference、Handoff、安装与 Context Budget 不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC6 | not_satisfied | 待完整 CI。 |
| R7 | AC7：Runtime/Bootstrap/最终用户文档同步唯一 Ownership | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC7 | not_satisfied | 待文档同步。 |
| R8 | AC8：L3 Review、CI、merge、main/archive fresh 与 Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC8 | explicitly_deferred | 由 #199 与端到端交付 Owner 持续拥有，merge 后取得。 |

# 验证矩阵

| 验证层 | 状态 |
| --- | --- |
| 行为 / 单元 | required：privacy/projection/native metadata Red→Green |
| 接口 / 契约 | required：MCP progress contract、Project Payload v2、frontmatter/routing metadata |
| Integration / Persistence | required：真实 Project Payload / install projection；数据库 N/A |
| Workflow Acceptance | required：#199 live lifecycle + PR/Review/merge/Closure |
| Build / Package | required：Runtime package scope 按真实路径判定；命中 package 时三平台 binary |
| Docs / Governance | required：Bootstrap/Runtime maintainer docs + USAGE targeted sync + 内容守恒 Review |

# TDD 状态

- [ ] 新增真实失败模式回归并取得 Red。
- [ ] 实现最小修复并取得 targeted Green。
- [ ] 全量 self-contained / Source-Runtime conformance / dynamic distribution / install / package Green。
- [ ] Completion Audit 与独立 L3 Review。

# 完成审计

- [x] upstream_re_read：Issue #199 创建后已重新读取 live Issue，标题、正文和 AC1–AC8 task list 均符合当前 Requirement Source Contract。
- [x] change_coverage：R1–R8 逐条映射 #199；没有引入 AIMA_UGC 特例。
- [ ] reverse_audit：待 final implementation 后从 AGENTS、Entry、Runtime rule、Projection、native metadata、Source/Runtime conformance 反查。
- [ ] unresolved_cleared：R1–R7 尚未完成；R8 为合法 post-merge deferred。

# 文档影响

Docs Impact = targeted。`runtime/README.md` 拥有 Runtime 架构/披露边界；Bootstrap reference 拥有目标 AGENTS 职责；`USAGE.md` 只保留用户需要理解的工程过程，不解释内部 Skill/Reference 组织。

# 非目标

AIMA_UGC、Release 发布、Deploy、依赖升级均不在本 Change 范围。