---
schema: coding-change/v1
id: CHG-20260831-project-facing-managed-bootstrap
title: 将 Runtime managed block 收敛为项目侧行为契约
level: L3
status: in_progress
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
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/tests/
contracts:
  - project-managed-bootstrap
  - runtime-user-visible-disclosure
data_changes: []
---

# 目标

把安装到目标项目根 `AGENTS.md` 的 Agent_Skills managed block 从“解释内部治理控制面如何运行”的实现说明，收敛为短、稳定、面向项目维护者的行为契约：始终先读取并遵守目标项目规则和真实事实；更高优先级的 Agent_Skills 执行模式只允许改变通用治理约束的取得和呈现方式，不得跳过、替代或降低目标项目自己的规则、Contract、Schema/Migration、CI、正式设计、部署和验收边界；真实工程过程继续可见，详细内部披露约束留在 Runtime/Entry/canonical Runtime Owner 中。

# 成功标准

- [ ] 目标项目 managed block 不再逐条枚举内部能力发现、选择、路由、上下文加载、内部文件/标识或各类用户可见通道名称。
- [ ] managed block 明确“无论采用哪种通用治理执行方式，都必须先读取并遵守目标项目适用规则和当前真实项目事实”。
- [ ] 更高优先级模式覆盖只改变通用 Agent_Skills 约束的取得/呈现方式，不能跳过项目 `AGENTS.md` / `CONTRIBUTING`、Contract、Schema/Migration、CI、正式设计、部署或验收边界。
- [ ] Runtime Mode 的详细用户可见披露约束继续由 Runtime 公共进度规则、shared Entry 和 Runtime canonical Reference 承担，语义不降低。
- [ ] 首次 Project Governance Bootstrap 生成/维护的项目 Overlay 只描述项目自己的规则和事实，不把通用治理能力自身的执行、分发或实现说明复制进项目规范。
- [ ] Runtime 安装 ownership、Project Payload、MCP Tool Contract、Task Route、Routing Manifest、Bundle、Stable ID、加密和 exact-text required Context 语义不变。
- [ ] 目标回归、完整 Skill Tests、独立 Deep Review、PR fresh CI、merge 后 main fresh CI 均取得新鲜证据。

# 范围

- 重写 `AGENTS.managed.md` 为项目侧行为契约。
- 补充 `AGENTS.template.md` 的项目化表达边界。
- 调整 Bootstrap canonical Reference 的 managed block 职责，避免未来再次把内部实现清单写回目标项目根入口。
- 在 Runtime canonical Reference 中明确详细披露规则的唯一 Owner 与 managed block 的薄契约边界。
- 更新/新增 Runtime disclosure、Project Governance Bootstrap 和内容守恒回归测试。

# 非目标

- 不改变 MCP Tool 名称、请求/响应 schema、Task Route、Routing Manifest、Bundle、Stable ID、Project Payload 或安装 ownership。
- 不修改 `runtime.py` 当前详细用户可见进度规则，除非测试证明现有语义不足；本任务预期保留其现状。
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
3. **managed block 只保留外部行为契约，详细内部规则留在 Runtime/Entry/ref13，项目大模型只维护 block 外项目 Overlay**：既减少目标项目暴露面，又保持运行约束和单一 Owner；采用。

## 兼容、迁移、部署与回滚

- 这是目标项目 Bootstrap/披露契约的 L3 语义调整，但不改 MCP/Bundle/Project Payload schema。
- 迁移：未来 Runtime Release 安装/升级时仅替换 installer 认领的 managed block；marker 外项目文本保持。
- 部署：本任务只合并 Agent_Skills main，不创建正式 Release。
- 回滚：回退本变更 commit/Release 即恢复旧 managed block；不涉及业务数据或 Schema 回滚。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | managed block 不应通过“禁止泄露”反向详细暴露内部治理实现 | user:managed-block-project-facing | not_satisfied | 待实现和回归验证 |
| R2 | 可以让项目宿主大模型把治理结果写成项目自己的自然规范，但 managed block 仍由安装器确定性维护 | user:managed-block-project-facing | not_satisfied | 待实现和回归验证 |
| R3 | 更高优先级模式只能改变通用治理约束取得/呈现方式，不能跳过目标项目 Agent/项目规则 | user:project-rules-always-read | not_satisfied | 待实现和回归验证 |
| R4 | Runtime 详细静默控制面约束必须继续有效，真实工程过程继续可见 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待内容守恒与 Runtime 回归验证 |
| R5 | managed block 只能做 Bootstrap，不重新生长成第二套 Router/Runtime 实现说明 | .agents/MAINTENANCE.md | not_satisfied | 待 ref12/ref13 Ownership 与测试验证 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | managed/bootstrap/disclosure targeted tests 证明旧实现 Red、新实现 Green，并验证项目规则永不被模式覆盖跳过 |
| 接口 / 契约 | required | managed bootstrap 与 Runtime disclosure contract 语义保持；MCP/Task Route/Bundle/Project Payload schema 不变并由既有回归证明 |
| 集成 / 持久化 / 运行依赖 | required | canonical Bundle + Project Payload + Installer 生成真实临时目标项目，核对最终根 `AGENTS.md` 与受管/项目自有边界 |
| 用户 / 工作流验收 | required | 安装后的项目入口对维护者只展示项目侧行为语义，同时保留工程过程可见性；高优先级模式不跳过项目规则 |
| 跨组件关键路径 | required | canonical assets → Project Payload → Installer → target `AGENTS.md`，以及 Runtime progress rule/detail Owner 的组合守恒 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖第三方服务、真实生产系统或现时外部数据 |
| 构建 / 打包 / 运行 | not_applicable | 本次不修改 runtime Python、Builder、MCP server 或 package/release workflow；按当前 path-scoped CI 由 Skill Tests 验证 Bundle/Payload/Installer |
| 文档 / 治理 / 其他 | required | ref12/ref13/managed/template Ownership、Change Ready、内容守恒和 live 引用检查 |

# 完成审计

- [ ] upstream_re_read：完成前重新读取本轮用户要求、根 `AGENTS.md`、Maintenance、ref12/ref13 与实际实现。
- [ ] change_coverage：确认“项目规则永远先读”“managed 外部契约”“内部 Owner 守恒”“项目化 Overlay”均进入实现与测试。
- [ ] reverse_audit：从最终目标项目 `AGENTS.md` 反查 Project Payload/Installer/managed template，再从 Runtime 用户可见输出反查 Entry/ref13/runtime progress rule，确认没有缺口或重复 Owner。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零，所有不适用有明确依据。

# 任务

- [x] 调查当前实现、历史 Change、managed block、ref12/ref13、Runtime progress rule 与既有回归。
- [x] 建立四维任务路由：Agent_Skills 源仓库维护 / Skill Mutation + Runtime Bootstrap / Python+Markdown+GitHub Actions / L3。
- [ ] 新增会在旧 managed block 上失败的项目侧契约回归并取得 Red。
- [ ] 重写 managed block，补项目化 Overlay 规则，并同步 ref12/ref13 Ownership。
- [ ] 更新受影响旧回归，确保不再要求目标项目根入口暴露内部控制面说明。
- [ ] 运行完整 Skill Tests / Ready Check 并取得新鲜证据。
- [ ] 执行独立 Deep Review，修复 BLOCKER/HIGH/MEDIUM Finding。
- [ ] PR fresh CI、merge、main fresh CI。
- [ ] 功能合并与 main fresh CI 后归档本 Change。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_managed_bootstrap_project_facing.py`
- 相关测试：`test_runtime_progress_privacy.py`、`test_runtime_disclosure_boundary.py`、`test_project_governance_bootstrap.py`、Project Payload/Installer/Bootstrap 相关测试
- 静态/完整验证：Skill Tests workflow 的 Python compile、CLI smoke、self-contained tests、routing/content preservation 和 changed Change Ready gate
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- 尚未执行。

# 文档影响

- `ref12` 与 `ref13` 是本次必须同步的 canonical 规则 Owner。
- `USAGE.md` 的安装操作方式不变；若现有文案未描述内部 managed 实现，则不制造无关差异。

# 交付

- 提交：进行中。
- 拉取请求：待创建。
- 发布：不创建 Release。
