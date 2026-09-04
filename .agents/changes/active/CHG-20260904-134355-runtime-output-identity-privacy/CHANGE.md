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
  - runtime-skill-projection
  - project-bootstrap
  - source-runtime-conformance
affected_paths:
  - .agents/skills/ENTRY.md
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/assets/AGENTS.template.md
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - runtime/agent_skills_runtime/disclosure.py
  - runtime/agent_skills_runtime/runtime.py
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - scripts/runtime_mcp_smoke.py
  - .github/workflows/runtime-package-tests.yml
  - .agents/skills/coding/tests/test_runtime_progress_privacy.py
  - .agents/skills/coding/tests/test_runtime_skill_projection.py
  - .agents/skills/coding/tests/test_runtime_disclosure_boundary.py
  - .agents/skills/coding/tests/test_managed_bootstrap_project_facing.py
  - .agents/skills/coding/tests/test_project_bootstrap.py
  - .agents/skills/coding/tests/test_project_governance_bootstrap.py
  - .agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py
  - .agents/skills/coding/tests/test_shared_root_router_contract.py
  - .agents/skills/coding/tests/test_skill_router_single_source.py
  - .agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py
  - .agents/skills/coding/tests/test_release_only_repository_surface.py
  - .agents/skills/coding/tests/test_figma_skill.py
  - .agents/skills/coding/tests/test_source_mode_installed_assets_noncanonical.py
contracts:
  - Runtime 用户可见表达 Contract
  - Runtime Skill Projection Contract
  - Source/Runtime 专业效果守恒 Contract
  - 目标项目 AGENTS Bootstrap Contract
data_changes: []
---

# 目标

修复 #199：同时满足三项不可互相牺牲的目标：

1. Source Mode 与 binary/Runtime 都保持最佳专业 Skill 使用效果，不为隐私删减 canonical/native 激活提示、路由、Handoff、专业 Core 或 required canonical Context；
2. 普通目标项目任务的 Agent 可控用户可见文本不把内部 Skill / Reference / Router / 路由 / Handoff identity 写成任务分工；
3. 目标项目 `AGENTS.md` 只承载项目事实、项目规则、首次治理校准、fail-closed 与安装 ownership，不写“不要泄漏内部规则”一类自我暴露说明。

# 最终方案边界

- **专业效果优先。** canonical `agents/openai.yaml` 中现有 `$coding/$docs/$review/$figma` 激活提示、跨专业 Handoff、失败/授权/回程条件保持 main 原文；本 Change 不通过改弱 canonical/native prompt 获得隐私。
- **内部身份与用户表达分层。** Skill identity、frontmatter、`agent-routing:v1` metadata、Router、Handoff 与 required Context 继续完整用于模型执行；隐私只约束 Agent 可控制的用户可见转写。
- shared Entry 为 Source/Runtime 普通目标项目任务提供薄输出边界，但保持上下文预算，不复制 Runtime 详细清单。
- Runtime `disclosure.py` 作为用户可见表达唯一代码级 Owner，同时供 MCP public progress rule 与 Runtime Skill Projection guard 使用。
- Runtime Skill Projection 继续按既有机制隐藏 canonical Reference filename/source_path/Stable ID，并对所有动态发现 Skill 自动追加用户可见表达 guard；frontmatter、routing metadata 和专业 Core 不因 guard 被删除。
- 目标 `AGENTS.md` managed/template 不承担 disclosure；三平台真实安装 CI 只验证项目侧 AGENTS Contract。用户输出边界由真实 MCP smoke / Entry / Projection 验证。
- 不做最终字符串 replace/filter，不维护 Coding/Testing/Docs/Review/Figma 固定隐私名单。
- 宿主 UI 自动生成 activity/trace 不是 Prompt/Skill/Runtime 可控制文本，不做不可实现承诺。

# 必须保持不变

- Source Mode 在显式维护/审计 Agent_Skills 自身或用户询问内部组织时，可正常查看和讨论 canonical Skill、Reference、路径、Stable ID 与路由过程。
- canonical/native 专业提示保持最佳激活与 Handoff 语义；当前四个 `agents/openai.yaml` 已精确恢复到 main blob，最终 diff 不包含它们。
- Runtime 动态 Skill Catalog、frontmatter、`agent-routing:v1` metadata、专业 Core 与 Handoff 保留。
- canonical Reference exact-text/hash、Bundle v3、Task Route evaluator、required Context、Project Payload v2 与 install-state schema 不变。
- Source/Runtime 等价性的 Owner 是路由结果、required Context、专业行为、失败/授权边界和最终使用效果，不要求为了隐私制造 native metadata 字节差异。
- 项目自有 `AGENTS.md` marker 外文本和其他项目资产继续保持。
- Context Budget 不通过抬阈值、删专业规则或少加载 Context 解决。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：目标 AGENTS 不承担 disclosure 自我说明 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC1 | satisfied | 426/426 self-contained Green；真实 managed/template 与 install 回归均验证内部 disclosure 词不进入目标 AGENTS。 |
| R2 | AC2：所有 Agent 可控用户文本禁止内部能力 identity 转写 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC2 | satisfied | Entry + Runtime public progress rule 明确禁止“用/调用/交给/由某个内部能力”式分工；MCP smoke Contract 已同步。 |
| R3 | AC3：canonical/native 专业提示保持最佳执行效果 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC3 | satisfied | 四个 canonical `agents/openai.yaml` 最终不在 diff；永久回归直接验证 `$coding/$docs/$review/$figma`、Handoff 与失败边界仍存在。 |
| R4 | AC4：动态 Skill Projection 自动注入输出 guard，内部语义保留 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC4 | satisfied | `test_every_runtime_skill_core_gets_user_visible_output_guard`、frontmatter/routing exact、专业 Core 语义与动态 fixture 全部 Green。 |
| R5 | AC5：永久回归覆盖真实失败模式与 future Skill | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC5 | satisfied | 426 tests Green；动态 `security` fixture 同时证明 Reference identity 隐藏、output guard 自动注入、native 强提示保留。 |
| R6 | AC6：Source/Runtime、Catalog、Reference、Handoff、安装与 Context Budget 不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC6 | not_satisfied | 426/426 + Context Budget 已 Green；同一 head 三平台 Runtime Package fresh evidence 尚在运行。 |
| R7 | AC7：Runtime/Bootstrap 文档同步唯一 Ownership | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC7 | satisfied | Bootstrap canonical Owner 已把 disclosure 移出目标 AGENTS；Runtime 既有 Owner 保留 Source/Runtime 分发与可见边界；最终用户 USAGE 无需变更且最终 diff 不含它。 |
| R8 | AC8：L3 Review、CI、merge、main/archive fresh 与 Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC8 | explicitly_deferred | 由 #199 与端到端交付 Owner 持续拥有，merge/archive 后取得。 |

# 验证矩阵

| 验证层 | 状态 |
| --- | --- |
| 行为 / 单元 | Green：426/426 self-contained tests。 |
| 接口 / 契约 | Green：Runtime public progress、Projection guard、frontmatter/routing metadata、native prompt preservation。 |
| Source/Runtime conformance | Green：routing manifest benchmark、required Context exact-text、Catalog/Handoff 现有回归全部通过。 |
| Context Budget | Green：代表性 L1/L2/Testing/Docs/Review/Figma 路由全部在既有阈值内；未抬阈值。 |
| Integration / Install | Python integration Green；三平台 onefile + real stdio MCP + real project install fresh evidence 运行中。 |
| Workflow Acceptance | #199 live Contract 已更新并重新读取；PR #200 保持 Draft。 |
| Docs / Governance | Green：Bootstrap/AGENTS Ownership 回归；target AGENTS 不承担 disclosure。 |
| L3 Review / Delivery | pending：待三平台 Green 后执行独立内容守恒 Review，再进入 ready/final-head CI。 |

# TDD 状态

- [x] 新增真实失败模式回归并在旧实现上取得 Red；失败集中在 AGENTS disclosure、输出 identity guard、Projection guard 与旧 CI Contract。
- [x] 实现最小修复并取得 targeted/full Green；最终方案撤回了可能削弱 canonical/native prompt 的错误方向。
- [ ] 取得同一 implementation head 的三平台 onefile / real MCP / real install Green。
- [ ] Completion Audit 与独立 L3 Review。

# 完成审计

- [x] upstream_re_read：Issue #199 创建后以及用户修正“最优效果优先”要求后均已更新并重新读取 live Issue；AC1–AC8 仍由 Requirement Source 持有。
- [x] change_coverage：R1–R8 映射 #199；最终实现不包含 AIMA_UGC 特例，也不把 native prompt 去身份化作为目标。
- [x] reverse_audit：从最终 diff、426 tests、Context Budget、native prompt preservation、Source/Runtime exact Context、clean AGENTS 反查，未发现通过删专业提示/少加载 Context 换隐私的路径。
- [ ] unresolved_cleared：R6 待三平台 fresh package evidence；R8 为合法 post-merge deferred。

# 当前证据

- implementation head `39a8c1c4a60571f0f09e54d52aa547dd1836bc29`：Skill Tests run `33844659153` 的 self-contained 阶段 426/426 Green，Context Budget Green；workflow 总体仅因本 Change 仍为 `proposed` 被 Ready Check 阻止。
- Runtime Package run `33844659170` 正在取得同一 head 的 Linux / Windows / macOS onefile、real stdio MCP 和 real project install 证据。
- compare `main@064b7eccc8d9deedb06a7d8f86d36a88f223c459...39a8c1c4...` 不包含任何 canonical `agents/openai.yaml`、`project_payload.py`、`USAGE.md` 修改。

# 文档影响

Docs Impact = targeted。Bootstrap canonical Owner 负责目标 `AGENTS.md` 职责；Runtime disclosure 的执行 Owner 在 shared Entry + Runtime progress rule + Runtime Skill Projection。既有 Runtime canonical Reference 已负责 Source/Runtime 模式与分发边界，最终用户 `USAGE.md` 无需增加内部隐私说明。

# 非目标

AIMA_UGC、正式 Release 发布、Deploy、依赖升级、Bundle/Task Route/Project Payload/install-state schema 迁移均不在本 Change 范围。