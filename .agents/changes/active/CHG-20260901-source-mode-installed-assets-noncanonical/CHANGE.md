---
schema: coding-change/v1
id: CHG-20260901-source-mode-installed-assets-noncanonical
title: 明确 Source Mode 目标项目旧安装资产非 canonical
level: L3
status: in_progress
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

- [ ] Source Mode 明确要求读取目标项目项目自有 `AGENTS.md`/`CONTRIBUTING` 和真实项目事实，不能因忽略旧安装副本而忽略项目规则。
- [ ] 目标项目 `agent-skills:managed` block、Runtime/Project Payload/Skill Projection 等安装资产在 Source Mode 中被明确标记为 preserved/non-canonical：允许检查 marker、ownership、安装版本与 drift，但不能作为当前通用治理语义来源。
- [ ] Project Governance Bootstrap 在 Source Mode 中不会把旧 managed block 的 Runtime/MCP/披露/路由/加载说明复制或改写到项目 Overlay；发现安装版本漂移时只报告正式 Runtime upgrade 需要，不在治理校准中手工覆盖 installer-owned block。
- [ ] Runtime Mode 的当前路由、required Context、披露、失败关闭和完整性语义保持不变；不通过删减 Runtime 内部规则换取表面简洁。
- [ ] 新增回归在旧实现上失败、在新实现上通过；完整 self-contained Skill Tests 绿色。
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
| R1 | 网页 Source Mode 治理目标项目时使用 Agent_Skills 当前 canonical 规则，不被目标项目旧 Agent_Skills 安装副本覆盖 | user:current-request | not_satisfied | 待实现与测试 |
| R2 | 仍必须读取并遵守目标项目自己的规则和真实仓库事实 | user:current-request | not_satisfied | 待实现与测试 |
| R3 | 旧 managed/runtime 资产仅作为安装/ownership/drift 事实，不能成为 Source Mode 通用治理语义来源 | user:current-request | not_satisfied | 待实现与测试 |
| R4 | Project Governance Bootstrap 不手工修改 installer-owned block，版本漂移通过正式 Runtime upgrade 收敛 | user:current-request | not_satisfied | 待实现与测试 |
| R5 | 不能为了表面简洁降低 Runtime Mode 执行效果和内部治理规则强度 | user:current-request | not_satisfied | 待内容守恒与完整回归 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 新 Source Mode ownership 回归验证规则来源判定 |
| 接口 / 契约 | not_applicable | 不改变 MCP/Runtime/public schema |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改 Runtime/installer 实现 |
| 用户 / 工作流验收 | required | 模拟“目标项目含旧 managed/runtime 安装资产”的 Source Mode Bootstrap 规则链 |
| 跨组件关键路径 | not_applicable | 不修改跨组件运行接线 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要外部 Provider |
| 构建 / 打包 / 运行 | not_applicable | 不修改 binary 构建/Project Payload 实现；完整 Skill Tests 仍构建 Bundle/Payload |
| 文档 / 治理 / 其他 | required | Root/Router/ref12/ref13 内容守恒、live 引用与 full self-contained tests |

# 完成审计

- [ ] upstream_re_read：已重新读取用户当前要求、当前 root/Maintenance/Entry/Router/Coding 与命中 References，并从它们独立重建完成定义。
- [ ] change_coverage：已确认当前变更覆盖全部上游要求，没有把变更自身当作需求全集。
- [ ] reverse_audit：已验证 Source Mode 不吃旧安装规则，同时项目规则仍被读取；Runtime Mode 原执行语义未降低。
- [ ] unresolved_cleared：所有 `not_satisfied` 已清零；延期或不适用项均有正式依据。

# 任务

- [x] 调查当前 Source/Runtime/Bootstrap 事实与 AIMA_UGC 真实触发案例
- [x] 建立四维任务路由：跨项目治理 / Project Bootstrap / L3 / Source Mode
- [ ] 建立失败回归并确认 Red
- [ ] 最小修改 canonical Bootstrap/Router/References
- [ ] 运行 targeted 与完整 self-contained tests
- [ ] 完成内容守恒与独立 Review
- [ ] PR、main fresh CI 与 Change 归档

# 验证

## 计划

- 目标测试：`test_source_mode_installed_assets_noncanonical.py`
- 相关测试：managed bootstrap、shared root/router、project governance bootstrap、Runtime disclosure/installation 既有回归
- 静态/完整验证：Agent_Skills self-contained Skill Tests
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- 尚未执行。

# 文档影响

- Agent-facing canonical Bootstrap/Router/Reference 规则受影响；最终用户 `USAGE.md` 暂不需要改，因为最终用户安装/运行步骤没有变化。

# 交付

- 提交：进行中
- 拉取请求：待创建
- 发布：不需要；Source Mode 读取 main 即生效，Runtime 产品语义未变化。