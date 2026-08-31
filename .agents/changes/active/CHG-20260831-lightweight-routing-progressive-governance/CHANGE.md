---
schema: coding-change/v1
id: CHG-20260831-lightweight-routing-progressive-governance
title: 轻量代码任务路由与渐进治理
level: L2
status: in_progress
owner: dingyuwen777
branch: feat/lightweight-routing-progressive-governance
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas: [router, coding, routing, governance, tests]
affected_paths: [.agents/skills/router/SKILL.md, .agents/skills/coding/SKILL.md, .agents/skills/coding/references/02_跨项目研发任务路由.md, .agents/skills/coding/references/10_完成定义追溯门禁.md, .agents/skills/coding/references/11_两阶段复核与完成前验证.md, .agents/skills/coding/references/18_最小充分治理与升级门禁.md, .agents/skills/coding/tests/test_minimal_sufficient_governance.py, .agents/skills/coding/tests/test_routing_conformance.py]
contracts: [Agent Skills Skill路由/v1, Agent Skills Reference路由/v1]
data_changes: []
---

# 目标

让 Agent_Skills 对简单代码任务按真实风险和交付事实选择最小充分流程，而不是把 Coding、文档、独立 Review、Completion Audit、Git/PR 等能力机械串成固定流水线；同时完整保留现有 L1/L2/L3、Docs、Review、Completion、Git、CI 与 L3 深度治理能力，并在出现真实升级信号时自动进入对应流程。

# 成功标准

- [ ] 仓库内隔离 L1 实现默认只要求最小事实恢复、最小修改与 targeted validation，不自动进入 Change、Docs、独立 Review 或完整 Completion Audit。
- [ ] 普通轻量 L2 仍要求最小充分任务契约与风险匹配验证，但不因 `风险=L2` 单一事实自动加载完整 Completion Gate / 两阶段 Review；出现持久 gated、交付、显式 Review、L3 等事实时能够升级。
- [ ] 非仓库、无持久交付/外部副作用的一次性 snippet / scratch code 有明确 fast path，不为它创建项目治理工件或扫描仓库文档。
- [ ] Docs 与独立 Review 保持条件式能力：有文档影响/审查门禁时仍自动命中，无影响时不机械加载。
- [ ] L3、公共 Contract、Schema/Migration、安全、发布等现有深度门禁不降级。
- [ ] Source Mode 与 Runtime evaluator 对相同信号保持同源 metadata 语义；Routing Conformance 覆盖轻量正例和升级反例。
- [ ] Skill Tests 在 PR 与合并后的 main 新鲜运行均通过；当前 Change 完成独立 Review、归档并从 active 清理。

# 范围

- 调整 Router 对简单代码、L1、轻量 L2、Docs/Review/Completion 条件路由的表述。
- 调整 Coding Core 的默认闭环、风险表和完成/Review 触发说明，使其与“最小充分治理”一致。
- 调整受影响 Reference 的路由 metadata 与正文，使完整 Completion/两阶段 Review 只在真实 gated/交付/审查事实下进入。
- 保留并强化最小充分治理的升级规则。
- 增补 self-contained routing/governance 回归测试。

# 非目标

- 不删除 Coding、Docs、Review、Figma、Change、Completion Audit、Git/CI/Release 能力。
- 不改变 L1/L2/L3 风险定义，不新增 L0。
- 不修改 Runtime 协议、Task Route 顶层 schema、Bundle 加密、Project Payload、MCP、Installer 或 Release 产品结构。
- 不升级 Python、依赖或 GitHub Actions 运行环境。
- 不修改目标业务项目规则。

# 必须保持不变

- `agent-routing:v1` 仍是每个正式 Skill/Reference 的唯一机器路由块；Stable Reference ID 不因正文/触发调整而变化。
- Source Mode 与 Runtime Mode 仍共享同一 canonical metadata/evaluator 语义，required canonical text 完整性规则不变。
- L3、公共 API/ABI/CLI/数据格式、Schema/Migration、跨模块 Contract、认证授权、安全、部署恢复、重大依赖/破坏性兼容变化继续保留持久施工契约、兼容/迁移/回滚、深度验证和独立 Review。
- 用户工作保护、权限边界、不静默升级/扩大范围、新鲜证据门禁不变。
- Docs/Review 仍由各自 Skill 作为唯一详细 Owner，Coding/Router 不复制第二套专业细则。

# 关键决策

- 不新增风险等级；继续用 L1/L2/L3 决定风险强度，用最小充分治理决定流程重量。
- 不通过删除能力减负，而通过 trigger、依赖和 progressive disclosure 减少无关 Context 与流程。
- 一次性 snippet fast path 只适用于没有目标仓库持久修改、没有公共/数据/安全边界、没有外部副作用/正式交付要求的代码；发现这些事实后立即回到正常 Coding 路由。
- 普通轻量 L2 保留语义级完成核对和 Validation Matrix 思维，但不自动生成/加载完整 gated Completion 流程。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 简单代码不应机械走编码、文档、审查全部流程 | user:current-request | not_satisfied | 待实现与路由测试 |
| R2 | 应修改 Agent_Skills canonical 规则，而不是只靠外部提示补丁 | user:current-request | not_satisfied | 待写入 canonical Router/Coding/References |
| R3 | 不删除任何现有选择/能力，保证实际使用效果 | user:current-request | not_satisfied | 待内容守恒 Review 与回归测试 |
| R4 | 修改完成后按仓库门禁推送并合并到 main | user:current-request | not_satisfied | 待 PR CI、merge、main fresh CI 与归档 |
| R5 | Skill Mutation 必须保持 Stable ID、同源路由、内容守恒和必要 conformance | .agents/skills/coding/references/15_规则内容守恒与Skill维护.md | not_satisfied | 待 metadata/conformance/内容守恒验证 |
| R6 | Agent_Skills 源仓库 L2/L3 维护必须使用正式 Change、独立 Review、PR/CI、main 新鲜验证并归档 | .agents/MAINTENANCE.md | not_satisfied | 当前 Change 已建立；其余待执行 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | routing/governance 单元回归证明 L1/轻量 L2 fast path 与升级条件 |
| 接口 / 契约 | required | `agent-routing:v1` metadata 可编译、Stable ID/依赖无悬空、Runtime evaluator 输出符合预期 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改数据库、文件运行语义、外部服务或 Runtime 安装行为 |
| 用户 / 工作流验收 | required | 以典型自然任务信号映射验证 snippet、L1、轻量 L2、gated L2、L3、Review/Docs/Git 路由 |
| 跨组件关键路径 | required | canonical metadata → compile_routing/evaluate_route → required References 的同源路由链 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方 API/硬件/远端运行事实需要验证 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/Package 路径；按仓库 CI 分责不触发三平台 onefile |
| 文档 / 治理 / 其他 | required | Change Ready、内容守恒、live references、Skill Tests、独立 Review、PR/main CI、归档 |

# 完成审计

- [ ] upstream_re_read：已重新读取用户当前要求、根 AGENTS、Maintenance、Entry、Router、Coding、Skill Mutation 与受影响 canonical References。
- [ ] change_coverage：已确认本 Change 覆盖轻量路由、能力保留、测试、Review、PR/main CI 和归档要求。
- [ ] reverse_audit：已从 snippet/L1/轻量 L2/gated L2/L3/Docs/Review/Git/Release 反向验证路由，并复核 Validation Matrix。
- [ ] unresolved_cleared：所有 `not_satisfied` 已清零；无未批准延期。

# 任务

- [x] 确认 main HEAD、维护规则、当前最小充分治理实现和现有回归测试
- [x] 建立专用分支与正式 L2 Change
- [ ] 完整读取本次受影响 canonical References 与测试
- [ ] 先补会锁住轻量/升级行为的回归测试
- [ ] 修改 Router、Coding Core 与最小必要 References
- [ ] 执行 targeted routing/governance tests 与 full self-contained Skill Tests
- [ ] 执行独立 Review 和内容守恒反向审计
- [ ] 更新 Change 为 ready_for_review 并通过 Ready Check / PR CI
- [ ] 合并功能 PR 到 main，确认 main fresh CI
- [ ] 独立归档 Change 并合并归档 PR，确认最终 main 与 active 清理

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_minimal_sufficient_governance.py`、`.agents/skills/coding/tests/test_routing_conformance.py`
- 相关测试：routing metadata/compiler、dynamic bundle/project payload、Skill mutation preservation、Ready Check
- 静态/构建：仓库 `skill-tests.yml` 当前定义的 self-contained suite
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- 尚未执行。

# 文档影响

- `targeted`：Router/Coding/References 本身即为 canonical 治理文档；预计无需修改 README/USAGE/runtime README，因为最终用户安装方式与 Runtime 产品行为不变。完成前重新核对。

# 交付

- 提交：当前分支通过 GitHub Contents API 产生中文提交；最终汇总待补。
- 拉取请求：待创建。
- 发布：不涉及 Release。
