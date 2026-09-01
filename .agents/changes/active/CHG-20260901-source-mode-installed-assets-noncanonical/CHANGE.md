---
schema: coding-change/v1
id: CHG-20260901-source-mode-installed-assets-noncanonical
title: 明确 Source Mode 目标项目旧安装资产非 canonical
level: L3
status: ready_for_review
owner: dingyuwen777
branch: chore/source-mode-installed-assets-noncanonical
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas:
  - source-mode
  - project-bootstrap
  - governance
  - tests
affected_paths:
  - AGENTS.md
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/tests/test_source_mode_installed_assets_noncanonical.py
contracts: []
data_changes: []
---

# 目标

在 ChatGPT 网页端或其他可直接读取 Agent_Skills canonical 源仓库的 Source Mode 中，明确区分“目标项目自己的规则/事实”和“目标项目里旧版本 Agent_Skills 安装资产”。Source Mode 必须继续读取并遵守目标项目项目自有规则和真实仓库事实，但通用 Agent_Skills 治理语义只来自当前 canonical Source；目标项目中的 installer-managed block、Runtime/Project Payload/Skill Projection 或 legacy 安装状态只能作为安装/ownership/drift 事实，不能覆盖或替代当前 canonical 治理规则。

# 成功标准

- [x] Source Mode 明确要求读取目标项目项目自有 `AGENTS.md`/`CONTRIBUTING` 和真实项目事实，不能因忽略旧安装副本而忽略项目规则。
- [x] 目标项目 `agent-skills:managed` block、Runtime/Project Payload/Skill Projection 等安装资产在 Source Mode 中被明确标记为 preserved/non-canonical：允许检查 marker、ownership、安装版本与 drift，但不能作为当前通用治理语义来源。
- [x] Project Governance Bootstrap 在 Source Mode 中不会把旧 managed block 的 Runtime/MCP/披露/路由/加载说明复制或改写到项目 Overlay；发现安装版本漂移时只报告正式 Runtime upgrade 需要，不在治理校准中手工覆盖 installer-owned block。
- [x] Runtime Mode 的当前路由、required Context、披露、失败关闭和完整性语义保持不变；不通过删减 Runtime 内部规则换取表面简洁。
- [x] 新增回归在旧实现上失败、在新实现上通过；完整 self-contained Skill Tests 绿色。
- [ ] 独立 Review 无未解决 BLOCKER/HIGH/MEDIUM Finding，PR fresh CI 与合并后 main fresh CI 绿色，随后 Change 独立归档。

# 范围

- 强化 Agent_Skills 根 Source Mode Bootstrap 的规则来源边界。
- 强化 Router Source Mode canonical 读取规则。
- 强化 Project Governance Bootstrap 对目标项目 managed block/旧安装资产的 ownership 与 drift 处理。
- 在 Runtime canonical Reference 的网页端边界中同步同一 Source Mode 语义。
- 增加专门 preservation/regression 测试。

# 非目标

- 不修改 Runtime evaluator、MCP Tool Contract、Routing Manifest、Task Route、Bundle、Project Payload schema、Runtime Skill Projection 算法或 installer 实现。
- 不改变 Runtime Mode 用户可见披露规则，不降低 required Context 完整性或执行效果。
- 不自动升级任何目标项目 Runtime，不在 Agent_Skills 本 Change 中直接修改 AIMA_UGC。
- 不把目标项目自身 `AGENTS.md`、CONTRIBUTING、Contract、Schema/Migration、CI、代码、测试、设计事实当作可忽略内容。

# 必须保持不变

- 目标项目事实与更具体项目规则始终优先于通用示例。
- Source Mode 继续直接读取当前 canonical `SKILL.md + references`，Runtime Mode 继续使用同一 canonical 语义的 Runtime 路由/加载链。
- installer-owned managed block 只能由正式安装/升级流程维护；Project Governance Bootstrap 只修改 marker 外项目 Overlay。
- Runtime 内部 disclosure、路由、完整性、fail-closed 和 exact-text 规则完整保留。

# 关键决策

1. **把目标项目旧 managed block 当作 Source Mode 当前规则继续执行**：会让网页端被旧 Runtime 版本反向降级，拒绝。
2. **Source Mode 完全忽略目标项目 `AGENTS.md`**：会丢失项目自有规则与事实，拒绝。
3. **Source Mode 对目标项目 `AGENTS.md` 做 ownership 分层**：marker 外项目自有规则/事实照常读取；installer-managed block 与 `.agents` Runtime 安装副本保留但不作为 canonical 通用治理语义；采用。
4. **治理校准时手工把 managed block 改成 canonical 最新模板**：破坏 installer ownership 和正式升级/回滚边界，拒绝；只检测 drift 并报告正式 Runtime upgrade。
5. **为避免暴露而继续删 Runtime 内部规则**：可能降低执行效果，拒绝；本次只修规则来源判定。

本 Change 不涉及数据迁移、部署或 Runtime binary 回滚。规则变更如需回退，回滚本 Change 的 canonical 文本与测试即可；目标项目 Runtime 仍由各自正式 Release/upgrade 流程管理。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 网页 Source Mode 治理目标项目时使用 Agent_Skills 当前 canonical 规则，不被目标项目旧 Agent_Skills 安装副本覆盖 | user:current-request | satisfied | 根 `AGENTS.md` 与 Router 明确 Source Mode canonical 来源；新回归 `test_source_mode_keeps_project_rules_but_rejects_installed_governance_as_canonical` 通过 |
| R2 | 仍必须读取并遵守目标项目自己的规则和真实仓库事实 | user:current-request | satisfied | 根 `AGENTS.md`、Router、ref13 均保留项目自有规则/真实事实优先；对应新回归通过 |
| R3 | 旧 managed/runtime 资产仅作为安装/ownership/drift 事实，不能成为 Source Mode 通用治理语义来源 | user:current-request | satisfied | Root/Router/ref12/ref13 均明确 non-canonical 安装资产边界；新 Source Mode 回归全绿 |
| R4 | Project Governance Bootstrap 不手工修改 installer-owned block，版本漂移通过正式 Runtime upgrade 收敛 | user:current-request | satisfied | ref12 明确 `不手工覆盖 installer-owned managed block` 与 `正式 Runtime upgrade`；Bootstrap 回归通过 |
| R5 | 不能为了表面简洁降低 Runtime Mode 执行效果和内部治理规则强度 | user:current-request | satisfied | 未修改 Runtime/MCP/Bundle/Payload/installer 实现；289 项 self-contained tests 中 Runtime routing/exact-text/disclosure/install/migration 回归全部通过 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 新 Source Mode ownership 回归验证规则来源判定，当前通过 |
| 接口 / 契约 | not_applicable | 不改变 MCP/Runtime/public schema |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改 Runtime/installer 实现 |
| 用户 / 工作流验收 | required | 模拟“目标项目含旧 managed/runtime 安装资产”的 Source Mode Bootstrap 规则链，当前通过 |
| 跨组件关键路径 | not_applicable | 不修改跨组件运行接线 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要外部 Provider |
| 构建 / 打包 / 运行 | not_applicable | 不修改 binary 构建/Project Payload 实现；完整 Skill Tests 仍覆盖 Bundle/Payload/Runtime 相关回归 |
| 文档 / 治理 / 其他 | required | Root/Router/ref12/ref13 内容守恒、live 引用、Context Budget 与 full self-contained tests 已通过 |

# 完成审计

- [x] upstream_re_read：已重新读取用户当前要求、当前 root/Maintenance/Entry/Router/Coding、ref12/ref13/ref14/ref15 与 Review 规则，并从上游独立重建完成定义。
- [x] change_coverage：已确认当前变更覆盖全部上游要求，没有把变更自身当作需求全集。
- [x] reverse_audit：已验证 Source Mode 不吃旧安装规则，同时项目规则仍被读取；Runtime Mode 路由、required Context exact-text、披露、完整性与 fail-closed 语义未降低。
- [x] unresolved_cleared：R1–R5 均已满足；没有未说明的延期或不适用项。

# 任务

- [x] 调查当前 Source/Runtime/Bootstrap 事实与 AIMA_UGC 真实触发案例
- [x] 建立四维任务路由：跨项目治理 / Project Bootstrap / L3 / Source Mode
- [x] 建立失败回归并确认 Red
- [x] 最小修改 canonical Bootstrap/Router/References
- [x] 运行 targeted 与完整 self-contained tests
- [x] 完成内容守恒与独立 Review
- [ ] PR、main fresh CI 与 Change 归档

# 验证

## 计划

- 目标测试：`test_source_mode_installed_assets_noncanonical.py`
- 相关测试：managed bootstrap、shared root/router、project governance bootstrap、Runtime disclosure/installation 既有回归
- 静态/完整验证：Agent_Skills self-contained Skill Tests
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Red：PR #128 早期 head `0d90e6e18af94d716ee41d7f15c0d5d904256c5b`，Skill Tests run `33466755067`；289 项中仅新增 Source Mode 防误用断言失败，证明旧规则缺口有效。
- Green：PR #128 head `d62b7271b8f3db531fcc427ddf4daefb68d302f7`，Skill Tests run `33467552491` 的 `Run self-contained tests` 成功，289 项全部通过；Workflow 总结论失败仅因为本 Change 当时仍为 `in_progress`，changed Change Ready gate 按预期阻断。
- Context Budget：未提高任何阈值；新增语义经去重后 `test_router_skill_migration.py` 通过。
- Deep Review：PR #128 review `5073848603`，reviewed base `0106475fa9387079a045a4e9be7e3ed71c2adf4f`、head `d62b7271b8f3db531fcc427ddf4daefb68d302f7`，`NO_FINDINGS_WITHIN_SCOPE`。

# 文档影响

- Agent-facing canonical Bootstrap/Router/Reference 规则受影响；最终用户 `USAGE.md` 不需要改，因为最终用户安装/运行步骤没有变化。

# 交付

- 提交：实现与 Ready 收敛已提交到 `chore/source-mode-installed-assets-noncanonical`
- 拉取请求：#128
- 发布：不需要；Source Mode 读取 main 即生效，Runtime 产品语义未变化。