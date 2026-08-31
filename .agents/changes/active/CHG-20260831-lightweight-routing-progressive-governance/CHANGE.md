---
schema: coding-change/v1
id: CHG-20260831-lightweight-routing-progressive-governance
title: 轻量代码任务路由与渐进治理
level: L2
status: ready_for_review
owner: dingyuwen777
branch: feat/lightweight-routing-progressive-governance
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - router
  - coding
  - routing
  - governance
  - tests
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/02_跨项目研发任务路由.md
  - .agents/skills/coding/references/10_完成定义追溯门禁.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/references/18_最小充分治理与升级门禁.md
  - .agents/skills/coding/references/19_CI审查升级门禁.md
  - .agents/skills/coding/tests/test_minimal_sufficient_governance.py
  - .agents/skills/coding/tests/test_routing_conformance.py
  - .agents/skills/coding/tests/test_router_skill_migration.py
contracts:
  - Agent Skills Skill路由/v1
  - Agent Skills Reference路由/v1
data_changes: []
---

# 目标

让简单代码任务按真实风险和交付事实选择最小充分流程，不再把 Coding、Docs、独立 Review、Completion Audit、Git/PR 机械串成固定流水线；同时保留全部现有能力，并在真实升级信号出现后自动进入对应流程。

# 成功标准

- [x] 隔离 L1 实现默认只要求最小事实恢复、最小修改与 targeted validation，不自动进入 Change、Docs、独立 Review或完整 Completion Audit。
- [x] 普通轻量 L2 保留最小充分任务契约与风险匹配验证，不因 `风险=L2` 单一事实自动加载完整 Completion Gate / 两阶段 Review。
- [x] 一次性 snippet / scratch code 有明确 fast path，出现仓库持久修改、公共/数据/安全边界或正式交付后立即回到正常 Coding 路由。
- [x] Docs 与独立 Review 保持条件式能力；有真实影响/门禁时命中，无影响时不机械加载。
- [x] L3、公共 Contract、Schema/Migration、安全、CI/Release 等深度门禁不降级。
- [x] Source Mode 与 Runtime evaluator 保持同源 metadata 语义，Routing Conformance 覆盖轻量正例和升级反例。

# 范围

- 调整 Router/Coding Core 的简单代码与轻量 L2 表述。
- 调整 Completion/Review Reference metadata，使完整流程按 gated/交付/审查事实进入。
- 保留并强化最小充分治理升级规则。
- 为 CI/Workflow 高风险治理保留完成前审查升级。
- 增补 self-contained routing/governance 回归。

# 非目标

- 不删除 Coding、Docs、Review、Figma、Change、Completion、Git/CI/Release 能力。
- 不改变 L1/L2/L3 风险定义，不新增 L0。
- 不修改 Runtime Task Route schema、Bundle/Payload/MCP/Installer/Release 产品结构或依赖版本。
- 不修改业务项目规则。

# 必须保持不变

- Stable Reference ID 与 Source/Runtime 同源 evaluator 语义保持。
- L3/public Contract/Schema/Migration/安全/部署/破坏性兼容继续保留持久治理、迁移/回滚、深度验证与独立 Review。
- 用户工作保护、权限边界、不静默升级/扩大范围、新鲜证据门禁保持。
- Docs/Review 仍由对应 Skill 作为详细 Owner。

# 关键决策

风险等级决定需要证明什么；治理深度决定需要多少持久记录和独立流程。普通 targeted validation 不等于独立两阶段 Review。减负通过条件触发和 progressive disclosure 实现，不通过删除能力实现。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 简单代码不机械走编码、文档、审查全部流程 | user:current-request | satisfied | L1/snippet/轻量 L2 路由回归通过 |
| R2 | 修改 Agent_Skills canonical，而不是外部提示补丁 | user:current-request | satisfied | Router/Coding/References canonical 已修改 |
| R3 | 不删除选择并保证使用效果 | user:current-request | satisfied | gated L2/L3/Docs/Review/Git/Release 正向回归保留；270 个 self-contained tests 已通过 |
| R4 | Skill Mutation 保持 Stable ID、同源路由与 conformance | .agents/skills/coding/references/15_规则内容守恒与Skill维护.md | satisfied | metadata compiler、Bundle/Runtime parity、routing conformance 已通过 |
| R5 | 源仓库维护通过正式 Change、PR/CI、Review、main fresh CI 与归档 | .agents/MAINTENANCE.md | satisfied | 当前 Change 已 Ready；PR/CI/Review/main/归档状态继续由交付区记录，不作为 Ready 前业务 Requirement |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | snippet/L1/轻量 L2/gated L2/L3/Review/Delivery routing tests |
| 接口 / 契约 | required | agent-routing metadata、Stable ID、依赖闭包、Source/Runtime parity |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变业务 persistence/runtime dependency |
| 用户 / 工作流验收 | required | 自然任务信号到 required Context 的 evaluator 回归 |
| 跨组件关键路径 | required | canonical metadata → compile/evaluate → Bundle/Runtime required Context |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方 Provider 当前事实 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime binary/Builder/Installer；按仓库 CI 分责不触发三平台 package |
| 文档 / 治理 / 其他 | required | Change Ready、内容守恒、live references、Skill Tests、Review、PR/main CI、归档 |

# 完成审计

- [x] upstream_re_read：已重新读取用户要求、根 AGENTS、Maintenance、Entry、Router、Coding、Skill Mutation 与受影响 canonical References。
- [x] change_coverage：已覆盖轻量路由、能力保留、测试、Review、PR/main CI 和归档要求。
- [x] reverse_audit：已从 snippet/L1/轻量 L2/gated L2/L3/Docs/Review/Git/Release 反向验证路由并复核 Validation Matrix。
- [x] unresolved_cleared：Requirement Traceability 无 `not_satisfied`；交付状态单独如实记录。

# 任务

- [x] 确认 main HEAD、维护规则和现有最小充分治理实现
- [x] 建立专用分支与正式 L2 Change
- [x] 补充轻量/升级路由回归
- [x] 修改 Router、Coding Core 与最小必要 References
- [x] 运行 PR self-contained Skill Tests；当前最新完整测试阶段为 270 tests / 0 failures
- [ ] 取得最终 head 的 PR CI 绿色与独立 Review
- [ ] 合并到 main 并确认 main fresh CI
- [ ] 独立归档 Change 并确认 active 清理

# 验证

## 计划

- 目标测试：minimal sufficient governance、routing conformance、router migration/context budget。
- 相关测试：metadata/compiler、dynamic Bundle/Project Payload、Skill mutation preservation、Ready Check。
- 永久 CI：`.github/workflows/skill-tests.yml`。
- Runtime Package Tests：not_applicable，本次不修改 Runtime/Builder/MCP 安装/Release 路径。

## 新鲜证据

- PR run 33384727508：self-contained tests `Ran 270 tests`，`OK`；Ready Check 因本 Change frontmatter 列表写法不符合当前 parser 而失败。
- 已将 `affected_areas/affected_paths/contracts` 改为当前 schema 接受的 YAML 列表写法；等待新 head PR CI 复验。

# 文档影响

- `targeted`：Router/Coding/References 本身就是 canonical 治理事实，已同步；README/USAGE/runtime README 的用户安装与产品行为未变化，不需要修改。

# 交付

- 分支：feat/lightweight-routing-progressive-governance
- PR：#118
- PR CI：等待当前 head 新鲜运行
- Review：待最终 head 独立 Review
- main merge / main fresh CI / Change archive：待执行
- Release：不涉及
