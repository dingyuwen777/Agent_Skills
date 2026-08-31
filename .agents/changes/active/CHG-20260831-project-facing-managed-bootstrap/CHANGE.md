---
schema: coding-change/v1
id: CHG-20260831-project-facing-managed-bootstrap
title: 将 Runtime managed block 收敛为项目侧行为契约
level: L3
status: ready_for_review
owner: dingyuwen777
branch: change/managed-block-project-facing-contract
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - project-bootstrap
  - runtime-disclosure
  - project-governance
  - tests
affected_paths:
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/assets/AGENTS.template.md
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/tests/
contracts:
  - project-managed-bootstrap
  - runtime-user-visible-disclosure
data_changes: []
---

# 目标

把安装到目标项目根 `AGENTS.md` 的 Agent_Skills managed block 从“解释内部治理控制面如何运行”的实现说明，收敛为短、稳定、面向项目维护者的行为契约：始终先读取并遵守目标项目规则和真实事实；更高优先级的 Agent_Skills 执行方式只允许改变通用治理约束的取得和呈现方式，不得跳过、替代或降低目标项目自己的规则、Contract、Schema/Migration、CI、正式设计、部署和验收边界；真实工程过程继续可见，详细内部披露约束留在 Runtime/Entry/canonical Runtime Owner 中。

# 成功标准

- [x] 目标项目 managed block 不再逐条枚举内部能力发现、选择、路由、上下文加载、内部文件/标识或各类用户可见通道名称。
- [x] managed block 明确“无论采用哪种通用治理执行方式，都必须先读取并遵守目标项目适用规则和当前真实项目事实”。
- [x] 更高优先级模式覆盖只改变通用 Agent_Skills 约束的取得/呈现方式，不能跳过项目 `AGENTS.md` / `CONTRIBUTING`、Contract、Schema/Migration、CI、正式设计、部署或验收边界。
- [x] Runtime Mode 的详细用户可见披露约束继续由 Runtime 公共进度规则、shared Entry 和 Runtime canonical Reference 承担，语义未降低。
- [x] Project Governance Bootstrap 生成/维护的项目 Overlay 只描述项目自己的规则和事实，不把通用治理能力自身的执行、分发或实现说明复制进项目规范。
- [x] Runtime 安装 ownership、Project Payload、MCP Tool Contract、Task Route、Routing Manifest、Bundle、Stable ID、加密和 exact-text required Context 语义未改变。
- [x] 新旧披露回归、真实 Project Payload/Installer 路径、内容守恒和 Deep Review 已取得进入 Ready 所需的新鲜证据。

# 范围

- 重写 `AGENTS.managed.md` 为项目侧行为契约。
- 补充 `AGENTS.template.md` 的项目化表达边界。
- 调整 Bootstrap canonical Reference 的 managed block 职责，避免未来再次把内部实现清单写回目标项目根入口。
- 重新读取并验证现有 Runtime canonical Reference、shared Entry 与 Runtime 公共进度规则仍完整承担详细披露约束；它们不需要代码修改。
- 更新/新增 Runtime disclosure、Project Governance Bootstrap、Project Payload/Installer 和内容守恒回归测试。

# 非目标

- 不改变 MCP Tool 名称、请求/响应 schema、Task Route、Routing Manifest、Bundle、Stable ID、Project Payload 或安装 ownership。
- 不修改 `runtime.py` 当前详细用户可见进度规则；现有规则已由回归证明仍承担详细披露职责。
- 不修改 AIMA_UGC 当前安装副本；新模板随后续 Runtime Release/升级进入目标项目。
- 不把 Runtime 加密或 managed block 描述成对机器 Owner 的安全隔离。
- 不创建或发布新的 Runtime Release/tag。

# 必须保持不变

- 无论 Source Mode、Runtime Mode 或其他更高优先级明确模式，目标项目当前路径适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则始终先读并继续生效。
- 项目真实代码、Manifest/lock、Contract、Schema/Migration、测试、CI、正式文档与设计事实优先于通用示例。
- Runtime required Context 仍从当前 Release canonical Bundle 逐字取得并保持完整性/fail-closed。
- Source Mode 维护者仍可以正常查看和讨论 canonical Skill/Reference/Router/路径与路由事实。
- Runtime 用户仍可以看到项目调查、需求与风险、代码、测试、文档、Review、Git/CI/Release 和交付状态。
- 安装器只维护 managed marker 内文本，marker 外项目 Overlay 与项目自有内容继续受保护。

# 关键决策

## 方案比较

1. **只润色现有 managed block**：改字但仍在目标项目根入口解释内部控制面，无法解决信息架构错误；拒绝。
2. **让项目大模型自由改 managed block**：文案可更自然，但破坏安装器 ownership、确定性升级与回滚边界；拒绝。
3. **managed block 只保留外部行为契约，详细内部规则留在 Runtime/Entry/canonical Runtime Owner，项目大模型只维护 block 外项目 Overlay**：既减少目标项目暴露面，又保持运行约束和单一 Owner；采用。

## 兼容、迁移、部署与回滚

- 这是目标项目 Bootstrap/披露契约的 L3 语义调整，但不改 MCP/Bundle/Project Payload schema。
- 迁移：未来 Runtime Release 安装/升级时仅替换 installer 认领的 managed block；marker 外项目文本保持。
- 部署：本任务只交付 Agent_Skills main，不创建正式 Release。
- 回滚：回退本变更 commit/后续包含它的 Release 即恢复旧 managed block；不涉及业务数据或 Schema 回滚。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | managed block 不应通过“禁止泄露”反向详细暴露内部治理实现 | user:managed-block-project-facing | satisfied | `AGENTS.managed.md` 已改为 6 条项目侧行为契约；`test_managed_bootstrap_project_facing.py`、`test_runtime_disclosure_boundary.py`、`test_runtime_progress_privacy.py` 同时断言内部通道/路由/Context 术语不回到根入口。Skill Tests #766 的 285 项 self-contained tests 全部通过。 |
| R2 | 项目宿主大模型把治理结果写成项目自己的自然规范，但 managed block 仍由安装器确定性维护 | user:managed-block-project-facing | satisfied | `AGENTS.template.md` 与 ref12 Project Governance Bootstrap 要求 marker 外 Overlay 使用项目自身模块/Contract/Schema/测试/CI/部署/业务/设计术语；既有 installer ownership/marker 回归全部通过。 |
| R3 | 更高优先级模式只能改变通用治理约束取得/呈现方式，不能跳过目标项目 Agent/项目规则 | user:project-rules-always-read | satisfied | managed 第 1 条先要求读取项目规则，第 2 条才允许切换通用治理取得/呈现；`test_mode_override_never_skips_project_rules` 与 `test_higher_priority_mode_override_cannot_skip_project_rules` 还验证顺序和 Contract/Schema/Migration/CI/正式设计/部署/验收边界。 |
| R4 | Runtime 详细静默控制面约束必须继续有效，真实工程过程继续可见 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | ref13 与 `runtime.py` 未修改；`test_runtime_public_progress_rule_reinforces_silent_control_plane`、Entry 模式回归、Runtime MCP 公共返回回归均通过，同时 managed 仍保留代码/测试/文档/复核/Git/CI/Release/交付状态可见。 |
| R5 | managed block 只能做 Bootstrap，不重新生长成第二套 Router/Runtime 实现说明 | .agents/MAINTENANCE.md | satisfied | ref12 第 7 节明确详细 Runtime 披露不由 managed 承担，并禁止把内部控制面清单复制回根 `AGENTS.md`；Source Router、Runtime Projection、Project Payload/no-Reference、Skill Mutation 与 Release surface 回归全部通过。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red：Skill Tests #751 在旧 managed 上 self-contained tests 按预期失败；Green：Skill Tests #766 `Ran 285 tests in 4.621s`、`OK`，项目侧契约和旧回归全部通过。 |
| 接口 / 契约 | required | managed bootstrap 的外部行为契约已迁移；MCP/Task Route/Bundle/Project Payload schema 与 `runtime.py` 未改，既有 routing/bundle/projection/disclosure contract tests 全绿。 |
| 集成 / 持久化 / 运行依赖 | required | 多组测试使用 canonical Bundle + Project Payload + Installer 生成真实临时目标项目，验证最终根 `AGENTS.md`、marker ownership、shared Entry/Router 与 no-Reference/sidecarless 边界。 |
| 用户 / 工作流验收 | required | 安装后的根入口只表达“项目规则先读、模式覆盖不跳过项目规则、工程过程可见”，并反向禁止 Runtime/Source/MCP/内部路由/required Context 清单。 |
| 跨组件关键路径 | required | canonical managed/template → Project Payload → Installer → target `AGENTS.md` 与 Entry/ref13/Runtime public progress rule 两条链分别有回归，证明外部薄契约和内部详细 Owner 同时可达。 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖第三方服务、真实生产系统或现时外部数据。 |
| 构建 / 打包 / 运行 | not_applicable | 未修改 `runtime/**`、Builder、MCP smoke、package/release workflow；仓库 path-scoped 规则不要求三平台 onefile。Skill Tests 已实际构建/校验 Bundle、Project Payload 与 Installer 语义。 |
| 文档 / 治理 / 其他 | required | ref12、managed、template、Change、live navigation、context budget、Routing Conformance、Ready 相关测试均进入 285 项 self-contained suite；没有提高历史 context budget 阈值。 |

# Review

Review Target：PR #125，base `5789add905917ef28584cade3cf9f5ed9e648bd2`，reviewed implementation head `40770fb62700910f25874b7c20e21dfacf6888d9`。

模式：L3 Deep Review；重新读取本轮用户要求、Agent_Skills 根 `AGENTS.md`、Maintenance、Entry、Router、Coding、Bootstrap/Runtime canonical Owner、Review Skill/References，并检查 PR 实际 changed files、真实安装链和 CI 日志。

独立风险重建重点：

- 更高优先级模式是否仍可能被解释为“可以不读项目 AGENTS”；
- managed 变薄后详细 Runtime 静默规则是否出现不可达或空洞；
- 项目大模型是否会反过来把治理实现复制进 marker 外 Overlay；
- 为删除直白术语是否破坏 Project Payload/Installer ownership、Source Mode 可见性或 exact-text Context；
- 旧回归是否通过恢复旧词汇或放宽 context budget 取巧；
- 本次是否误改 Runtime/MCP/Release 产品面并遗漏三平台验证。

Review 结果：`NO_FINDINGS_WITHIN_SCOPE`。实现把项目规则优先放在模式覆盖之前；模式覆盖明确只作用于通用治理取得/呈现；详细披露仍由未修改的 Entry/ref13/runtime progress rule 承担；Overlay 项目化表达进入 template/ref12；旧测试全部迁移为新契约反向保护，且 ref12 通过去重恢复历史 context budget，没有修改预算阈值。当前 diff 不包含 `runtime/**`、Builder、MCP server 或 Workflow，因此没有证据要求三平台 Runtime Package Tests。

测试充分性结论：当前测试能证明 managed/template/ref12 的 canonical 文本、真实 Bundle/Payload/Installer 生成结果、Runtime 公共披露规则、Source/Runtime 可见性、routing/content preservation、sidecarless ownership 和现有 context budget；不能证明未来任意宿主模型绝不违反自然语言指令，这属于模型/宿主行为边界，不能伪装为确定性保证。

当前无 BLOCKER/HIGH/MEDIUM Finding。

# 完成审计

- [x] upstream_re_read：完成前重新读取本轮用户要求、根 `AGENTS.md`、Maintenance、Entry/Router、Coding、ref12/ref13、Runtime progress rule、Review 规则和 PR 实际 diff。
- [x] change_coverage：确认“项目规则永远先读”“managed 外部契约”“内部 Owner 守恒”“项目化 Overlay”“不提高 context budget”均进入实现与测试。
- [x] reverse_audit：从真实 target `AGENTS.md` 反查 template/managed/Project Payload/Installer，再从 Runtime 用户可见输出反查 Entry/ref13/runtime progress rule；未发现缺口、第二 Owner 或项目规则被模式覆盖跳过的路径。
- [x] unresolved_cleared：R1–R5 全部 satisfied；外部依赖与三平台 package 层的 not_applicable 均有当前 changed scope 依据。

# 任务

- [x] 调查当前实现、历史 Change、managed block、ref12/ref13、Runtime progress rule 与既有回归。
- [x] 建立四维任务路由：Agent_Skills 源仓库维护 / Skill Mutation + Runtime Bootstrap / Python+Markdown+GitHub Actions / L3。
- [x] 新增会在旧 managed block 上失败的项目侧契约回归并取得 Red。
- [x] 重写 managed block，补项目化 Overlay 规则，并重新划分 ref12 与内部 Runtime Owner 职责。
- [x] 更新受影响旧回归，确保不再要求目标项目根入口暴露内部控制面说明。
- [x] 完整 Skill Tests 的 self-contained suite 取得 285/285 Green；当前唯一失败为 Change 尚未切到 Ready 的预期机器门禁。
- [x] 执行独立 Deep Review，无 BLOCKER/HIGH/MEDIUM Finding。
- [ ] Change 切到 Ready 后取得 PR final-head fresh CI，完成 Ready 状态转换并合并。
- [ ] merge 后取得 main fresh CI。
- [ ] main fresh CI 后将本 Change 标记 done 并归档。

# 验证

## Red

- Skill Tests #751（run `33397855286`，head `26d244d077c325e690f018f4c7105790201c5401`）：compile 与 CLI smoke 成功；新增项目侧契约在旧 managed 实现上使 self-contained tests 按预期失败，证明测试能捕获目标差异。

## Green 收敛

- 中间 Green run #758（run `33398436673`）暴露 8 个旧根入口字面契约和 3 个 context budget 回归。处理方式是迁移旧断言并压缩 ref12 重复说明，没有恢复“研发治理 MCP”等旧根入口词汇，也没有提高 context budget 阈值。
- Skill Tests #766（run `33399612646`，implementation head `40770fb62700910f25874b7c20e21dfacf6888d9`）：Python 3.14.7；compile success；CLI smoke success；self-contained `Ran 285 tests in 4.621s`、`OK`。唯一失败是 changed Change Ready Check 明确报告当前 `status=in_progress`，属于进入 Ready 前的预期治理门禁。

# 文档影响

- 已修改 ref12：把 managed block 的 canonical 职责收敛为项目侧行为契约，并把 Project Governance Bootstrap 的项目化表达写成长期规则。
- ref13 已重新读取并通过既有回归验证继续承担详细 Runtime disclosure Owner；正文不需要修改，避免制造第二次重复说明。
- `USAGE.md` 的下载、安装、升级、回退和日常使用步骤未改变，因此不制造无关文档差异。

# 交付

- 分支：`change/managed-block-project-facing-contract`，基于任务开始时 `main@5789add905917ef28584cade3cf9f5ed9e648bd2`；当前 compare `behind_by=0`。
- PR：#125，当前 Draft，mergeable=true；待本次 Ready 状态提交取得 fresh CI 后执行 Ready/merge。
- Release：不创建 tag 或正式 Release；本变更在未来正式 Runtime Release/升级时进入目标项目。
