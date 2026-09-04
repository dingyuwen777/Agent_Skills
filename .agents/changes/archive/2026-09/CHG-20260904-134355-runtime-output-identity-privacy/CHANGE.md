---
schema: coding-change/v1
id: CHG-20260904-134355-runtime-output-identity-privacy
title: 收口 Runtime 内部能力身份的用户可见披露边界
level: L3
status: done
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
  - .agents/changes/archive/2026-09/CHG-20260904-134355-runtime-output-identity-privacy/CHANGE.md
contracts:
  - Runtime 用户可见表达 Contract
  - Runtime Skill Projection Contract
  - Source/Runtime 专业效果守恒 Contract
  - 目标项目 AGENTS Bootstrap Contract
data_changes: []
---

# 目标

修复 #199，同时满足三项不可互相牺牲的目标：

1. Source Mode 与 binary/Runtime 都保持最佳专业 Skill 使用效果，不为隐私删减 canonical/native 激活提示、路由、Handoff、专业 Core 或 required canonical Context；
2. 普通目标项目任务的 Agent 可控用户可见文本不把内部 Skill / Reference / Router / 路由 / Handoff identity 写成任务分工；
3. 目标项目 `AGENTS.md` 只承载项目事实、项目规则、首次治理校准、fail-closed 与安装 ownership，不写“不要泄漏内部规则”一类自我暴露说明。

# 最终方案边界

- **专业效果优先。** canonical `agents/openai.yaml` 中原有 `$coding/$docs/$review/$figma` 激活提示、跨专业 Handoff、失败/授权/回程条件保持 main 原文；本 Change 没有通过改弱 canonical/native prompt 获得隐私。
- **内部身份与用户表达分层。** Skill identity、frontmatter、`agent-routing:v1` metadata、Router、Handoff 与 required Context 继续完整用于模型执行；隐私只约束 Agent 可控制的用户可见转写。
- 用户关于目标项目的正常事实、解释、建议、风险、验证、状态和交付照常回答；只有涉及 Agent 自身的进度、分工或执行过程时，才禁止内部 identity 转写，不能把隐私规则扩大成“只能报告动作”。
- shared Entry 保持薄入口；Runtime `disclosure.py` 集中拥有用户可见表达 Contract，并供 MCP public progress rule 与 Runtime Skill Projection guard 复用。
- Runtime Skill Projection 继续隐藏 canonical Reference filename/source_path/Stable ID，同时对所有动态发现 Skill 自动追加用户可见表达 guard；frontmatter、routing metadata 和专业 Core 不因 guard 被删除。
- 目标 `AGENTS.md` managed/template 不承担 disclosure；内部 Bootstrap Owner 仍禁止把通用治理能力自身的执行、分发或实现说明复制/改写进项目 Overlay。
- 不做最终字符串 replace/filter，不维护固定 Skill 名单；宿主 UI 自动生成 activity/trace 不做不可实现的隐藏承诺。

# 必须保持不变

- Source Mode 在显式维护/审计 Agent_Skills 自身或用户询问内部组织时，可正常查看和讨论 canonical Skill、Reference、路径、Stable ID 与路由过程。
- canonical/native 专业提示保持最佳激活与 Handoff 语义；四个 `agents/openai.yaml` 最终不在 implementation diff。
- Runtime 动态 Skill Catalog、frontmatter、`agent-routing:v1` metadata、专业 Core 与 Handoff 保留。
- canonical Reference exact-text/hash、Bundle v3、Task Route evaluator、required Context、Project Payload v2 与 install-state schema 不变。
- Source/Runtime 等价性的 Owner 是路由结果、required Context、专业行为、失败/授权边界和最终使用效果，不要求为了隐私制造 native metadata 字节差异。
- Context Budget 不通过抬阈值、删专业规则或少加载 Context 解决。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：目标 AGENTS 不承担 disclosure 自我说明 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC1 | satisfied | final PR head `5484a14aa3289e78cb8b6d09698a24289597a404` 的 Skill Tests `33845881829` 全绿；真实 managed/template 与三平台安装回归均验证内部 disclosure 说明不进入目标 AGENTS。 |
| R2 | AC2：正常项目问答保留，Agent 自身执行过程禁止内部 identity 转写 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC2 | satisfied | Entry + Runtime public progress rule 明确“正常事实/解释/建议/风险/验证/状态/交付照常回答”，同时禁止“用/调用/交给/由某个内部能力”式任务分工；Review-fix Red `33845169676` 曾精确暴露过宽边界，最终已 Green。 |
| R3 | AC3：canonical/native 专业提示保持最佳执行效果 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC3 | satisfied | 四个 canonical `agents/openai.yaml` 不在 final diff；永久回归验证 `$coding/$docs/$review/$figma`、Handoff、失败/授权/回程边界仍存在，Runtime 原样携带 native prompt。 |
| R4 | AC4：动态 Skill Projection 自动注入输出 guard，内部语义保留 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC4 | satisfied | 动态 Runtime Skill Core 全部获得同一 guard；frontmatter / `agent-routing:v1` exact、专业 Core 语义和动态 fixture 全部通过。 |
| R5 | AC5：永久回归覆盖真实失败模式与 future Skill | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC5 | satisfied | final-head Skill Tests `33845881829` success；动态 `security` fixture 同时证明 Reference identity 隐藏、guard 自动注入、native 强提示保留；正常项目问答不受限制也有永久回归。 |
| R6 | AC6：Source/Runtime、Catalog、Reference、Handoff、安装与 Context Budget 不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC6 | satisfied | final-head Skill Tests `33845881829` success（428/428、Context Budget、Ready Check、Agent Skills Gate）；final-head Runtime Package `33845881814` Linux/Windows/macOS onefile + real MCP + real install 全绿；implementation main-fresh Skill `33846245854` 与 Runtime Package `33846245791` 也 success。 |
| R7 | AC7：Runtime/Bootstrap 文档同步唯一 Ownership | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC7 | satisfied | Bootstrap canonical Owner 把 disclosure 移出目标 AGENTS，同时保留“不得复制治理执行/分发/实现说明到 Overlay”的内部内容守恒边界；最终用户 `USAGE.md` 无需修改且不在 diff。 |
| R8 | AC8：L3 Review、final-head CI、guarded merge、main-fresh、Change archive、archive-main、Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/199#AC8 | explicitly_deferred | final-head L3 Review `5110070936` 为 `NO_FINDINGS_WITHIN_SCOPE`，无 unresolved review thread；PR #200 expected-head guarded squash merge → `main@2090a15a28744974021d844b6b408437080df85b`；implementation main-fresh Skill `33846245854`、Runtime Package `33846245791` success。当前 archive PR/merge、archive-main fresh 与 #199 Closure 由 post-merge finalization 继续承担，避免 archived Change 自引用。 |

# Red / Green 与 Review

- 初始 Red：新增 disclosure / AGENTS / Projection 回归在旧实现上按预期失败，证明问题可复现。
- 中间实现一度尝试清理 canonical native prompt；用户指出这可能降低 Source 使用效果后，该方向被完整撤回，四个 canonical `agents/openai.yaml` 精确恢复到 main。
- Context Budget 中间曾因 Entry 膨胀超过既有阈值；没有抬阈值，而是压缩共享入口，把详细 Runtime 规则留给运行层。
- Review-fix Red：run `33845169676`，新增“正常项目问答不受隐私规则误伤”和“内部 Bootstrap Owner 继续阻止治理实现复制进 Overlay”回归按预期失败。
- final code head `c864c63f5cd5dc2c21e726fe9f32dcfdf1483b90`：428/428 与原 Context Budget Green。
- final PR head `5484a14aa3289e78cb8b6d09698a24289597a404`：Skill Tests `33845881829`、Runtime Package `33845881814` success。
- final-head L3 A1/A2 + 内容守恒 Review：review id `5110070936`，结论 `NO_FINDINGS_WITHIN_SCOPE`，无 unresolved review thread。
- implementation merge：PR #200 expected-head guarded squash merge → `main@2090a15a28744974021d844b6b408437080df85b`。
- implementation main-fresh：Skill Tests `33846245854` success；Runtime Package `33846245791` success，三平台再次通过 onefile/self-test、real MCP、real project install。

# 验证矩阵

| 验证层 | 结论 |
| --- | --- |
| 行为 / 单元 | required；真实 Red→Green；final 428/428 Green |
| 接口 / 契约 | required；Runtime public progress、正常项目问答、Projection guard、frontmatter/routing metadata、native prompt preservation Green |
| Source/Runtime conformance | required；routing、required Context exact-text、Catalog/Handoff、Reference exact-text/hash 现有回归保持 Green |
| Context Budget | required；既有绝对预算通过，未提高阈值 |
| Integration / Install | required；PR final-head 与 implementation main-fresh 均取得 Linux/Windows/macOS onefile、real MCP、real project install Green |
| Workflow Acceptance | required；#199 live Contract 多次更新后均重新读取；PR #200 final-head Review/CI/merge preflight 均使用 live Requirement Source |
| Docs / Governance | required；target AGENTS 不承担 disclosure；内部 Bootstrap Owner 保留内容守恒边界 |
| Release / Deploy | not_applicable；未发布正式 Release，未部署生产 |

# 完成审计

- [x] upstream_re_read：#199 创建后、用户提出“最优效果优先”修正后以及 final Review 前均重新读取 live Requirement Source。
- [x] change_coverage：R1–R8 直接映射 #199；没有 AIMA_UGC 特例，也没有把 native prompt 去身份化作为目标。
- [x] reverse_audit：从 final diff、428 tests、Context Budget、native prompt preservation、Source/Runtime exact Context、三平台 Runtime evidence、clean AGENTS 反查；没有通过删专业提示/少加载 Context 换隐私。
- [x] unresolved_cleared：R1–R7 satisfied；R8 的 archive/Closure 自引用生命周期有正式 Owner #199 与端到端 finalization，按规则 explicitly_deferred。

# 文档影响

Docs Impact = targeted。Bootstrap canonical Owner 负责目标 `AGENTS.md` 职责；Runtime disclosure 执行 Owner 位于 shared Entry + Runtime public progress rule + Runtime Skill Projection。既有 Runtime canonical Reference 继续负责 Source/Runtime 分发与可见边界；最终用户 `USAGE.md` 无需增加内部隐私说明。

# 归档生命周期

- [x] PR #200 final-head Review、fresh CI 和 expected-head guarded squash merge 完成。
- [x] implementation `main@2090a15a28744974021d844b6b408437080df85b` 的 Skill Tests `33846245854` / Runtime Package `33846245791` main-fresh success。
- [ ] 当前 archive PR merge 并取得 archive-main fresh CI。
- [ ] #199 AC1–AC8 Closure Evidence、body checkbox writeback、重读、close、再次重读。
- [ ] 当前任务 implementation/archive 分支完成安全清理。

# 交付边界

未修改 AIMA_UGC；无依赖升级；无正式 Release/Deploy；无 Bundle v3 / Task Route / Project Payload schema / install-state schema 迁移。宿主 UI 自动生成 activity/trace 不属于 Prompt/Skill/Runtime 可直接控制表面，因此不宣称可以隐藏。