---
schema: coding-change/v1
id: CHG-20260901-figma-capability-gap-inventory
title: Figma Design-to-Code 集中系统能力缺口清单
level: L2
status: in_progress
owner: dingyuwen777
branch: feat/figma-capability-gap-inventory
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas: [figma, governance, tests]
affected_paths: [.agents/skills/figma/SKILL.md, .agents/skills/figma/references/05_Design-to-Code交付门禁.md, .agents/skills/coding/tests/test_figma_skill.py]
contracts: []
data_changes: []
---

# 目标

把 Figma `baseline-ready / Design-to-Code` 已有的真实系统能力检查收敛成强制、集中、可决策的 **Capability Gap Inventory / 系统能力缺口清单**。在把设计交给 Coding 前，必须让用户一次看到本次审查范围内全部已发现的未实现、未批准、未来、过期、实现错误或待决策能力，避免缺口只散落在 Findings 中或开发到一半才暴露。

# 成功标准

- [ ] `baseline-ready / Design-to-Code` 在 Coding Handoff 前强制形成 Capability Gap Inventory；没有缺口时也明确输出 `none`。
- [ ] 清单按真实能力/Owner 去重，不因 Normal/Loading/Empty/Error 等状态稿重复同一能力而制造噪声，同时保留状态差异。
- [ ] 每个缺口至少包含 Figma 位置、用户能力、当前系统证据、正式事实 Owner、缺失/冲突层、分类、阻塞性和建议动作；项目不存在的层标记 `not_applicable`，不得为填表发明架构。
- [ ] 已批准但尚未实现的能力标记 `implementation_required`；只有当前任务已经批准扩大为真实跨层实现时才能进入 Coding 实施，否则先集中披露，不得由前端/Figma MCP 猜 API、永久 Mock 或伪造成功。
- [ ] 未批准设计假设、Future、design_outdated、implementation_issue_detected、decision_required 等沿用现有事实分类，不建立第二套冲突语义。
- [ ] Figma 主 Skill 正式输出显式暴露 Capability Gap Inventory，详细格式仍由 Design-to-Code Reference 唯一维护。
- [ ] 自包含回归测试验证上述规则，并保持现有 Figma/Router/Runtime 动态发现与内容守恒回归通过。

# 范围

- 修改 Figma 主 Skill 的 Baseline Ready / 正式输出薄入口。
- 修改 `05_Design-to-Code交付门禁.md`，建立 Capability Gap Inventory 的详细 Owner、格式、去重、阻塞与 Handoff 规则。
- 修改现有 `test_figma_skill.py` 增加行为守恒回归。
- 完成本仓库 L2 Change、Skill Tests、独立 Review、PR、main fresh CI 和独立归档。

# 非目标

- 不新增 Figma Reference，不修改 Reference Stable ID、metadata trigger、依赖或 Task Route schema。
- 不修改 Router、Runtime、Project Payload、Bundle、MCP、Installer、Release 或三平台 onefile 构建逻辑。
- 不把 AIMA_UGC、Vue、具体 API、业务字段、Provider、项目时区或 Design Token 写入通用 Skill。
- 不规定所有缺口必须由用户逐条手工编码；实现方式仍由目标项目 Coding 工作流与用户授权决定。

# 必须保持不变

- 现有 `READY / READY_WITH_NOTES / NOT_READY`、`implementation_required`、Annotation Development Readiness、Existing Implementation Delta、Implementation ↔ Figma Conformance、Bidirectional Design Sync 与 Figma Sync & Human Review 语义保持。
- Figma Skill 继续拥有设计审查和 Design-to-Code Ready 详细规则；Coding 不复制第二套 Figma 细则。
- 不改变 Runtime 路由词汇、Reference identity 和动态发现机制。
- Git 提交信息使用中文；所有完成结论必须有本轮新鲜证据。

# 关键决策

- Capability Gap Inventory 作为现有 UI → Real-System Preflight 的**集中输出层**，不建立新的能力判定体系。
- 去重键优先使用真实能力/正式 Owner + 用户语义；同一能力跨状态稿只保留一条主记录，并在记录内保留状态差异。
- `implementation_required` 只表示已批准但当前未实现；若本次没有批准扩大实现范围，清单必须先向用户集中披露并阻止伪实现。若本次任务已经明确包含真实全栈实现，则作为 Coding Handoff 输入继续实施，不要求再次逐项询问。
- 主 Skill 只保留硬触发与正式输出入口，详细字段、分类和失败处理留在 `05_Design-to-Code交付门禁.md`，避免重复漂移。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Figma 中后端/系统尚未实现的能力必须在前端实施前完整列出给用户 | user:current-request | not_satisfied | 尚未验证 |
| R2 | 缺口必须集中输出，不能只散落在 Findings 或开发中途才暴露 | user:approved-capability-gap-inventory | not_satisfied | 尚未验证 |
| R3 | 已批准未实现、未批准设计假设、未来/过期/实现错误/待决策必须沿用真实事实分类 | user:approved-capability-gap-inventory | not_satisfied | 尚未验证 |
| R4 | 不允许 Figma MCP/前端为缺失能力猜 API、永久 Mock 或伪造系统成功 | user:current-request | not_satisfied | 尚未验证 |
| R5 | 清单要完整但去重，避免同一能力因多个状态稿或重复节点造成噪声 | user:approved-capability-gap-inventory | not_satisfied | 尚未验证 |
| R6 | 允许提交、推送、PR；验证通过后允许合并和归档 | user:git-delivery-authorization | satisfied | 本轮用户已明确授权 Git/PR/merge/archive |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | `test_figma_skill.py` 新增 targeted regression，证明集中缺口清单、去重、阻塞/继续 Handoff 和 `none` 输出语义 |
| 接口 / 契约 | not_applicable | 不修改 public Runtime/Task Route/Reference Stable ID/metadata schema |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库、文件系统运行语义或外部 runtime dependency 变化 |
| 用户 / 工作流验收 | required | 从“Figma baseline-ready → Gap Inventory → Coding Handoff”规则文本与回归断言证明实现方/用户可见决策输出闭环 |
| 跨组件关键路径 | required | 全量 self-contained Skill Tests 证明 Figma Core/Reference、Router、Bundle/Project Payload 现有联动未破坏 |
| 外部依赖 / 供应方探测 | not_applicable | 不涉及外部 Provider 当前事实 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release；按仓库 CI 分责不触发三平台 package tests |
| 文档 / 治理 / 其他 | required | Ready Check、内容守恒 Review、PR Skill Tests、main fresh Skill Tests、Change 归档 |

# 完成审计

- [ ] upstream_re_read：已重新读取用户要求、Agent_Skills 根规则、Maintenance、Router、Coding/Figma canonical Owner 与 required References。
- [ ] change_coverage：已确认 Change 覆盖全部本轮要求，没有把 Change 自身当作需求全集。
- [ ] reverse_audit：已反查 `baseline-ready → Capability Gap Inventory → Coding Handoff` 与 `已支持/未实现/未批准/冲突` 分支，并复核验证矩阵。
- [ ] unresolved_cleared：所有 `not_satisfied` 已清零，未验证项和不适用项均有依据。

# 任务

- [x] 读取 canonical Source Mode 入口、Maintenance、Router、Coding、Figma 与 required References
- [x] 确认当前 main HEAD、Active Change 与本次 L2/PR/CI 门禁
- [ ] 先新增会因缺少 Capability Gap Inventory 而失败的回归测试并取得 Red 证据
- [ ] 修改 Figma Design-to-Code canonical 规则
- [ ] 取得 targeted / full self-contained Green 证据
- [ ] 完成 Requirement/内容守恒/独立 Review
- [ ] 更新 Change 到 ready_for_review 并通过 PR Skill Tests
- [ ] 合并并验证 main fresh Skill Tests
- [ ] 独立归档 Change 并完成归档 PR/main 验证

# 验证

## 计划

- Red：PR 上新增 targeted regression 后读取 `Skill Tests` 失败日志，确认失败原因是 Capability Gap Inventory 规则尚不存在。
- Green 1：规则实现后同一 PR 的 self-contained tests 中 `test_figma_skill.py` 与全量测试通过；此时 Change 仍可保持 in_progress，让 Ready Check 继续阻塞集成。
- Review：读取 PR diff，按 Review A1/A2、内容守恒、通用性、重复 Owner、测试充分性做独立复核。
- Green 2：把 Change 更新为 `ready_for_review` 并填入新鲜证据后，PR `Skill Tests` 全绿。
- Merge：REST merge + `expected_head_sha`；随后读取 main HEAD 并确认 main fresh `Skill Tests`。
- Archive：独立归档 PR 将 Change 更新为 `done` 并移动到 `archive/2026-09/...`，再验证归档 PR/main changed-scope CI。

## 新鲜证据

- 尚未执行。

# 文档影响

- `README.md` / `USAGE.md` / `runtime/README.md`：预计 `not_applicable`，本次是专业 Figma canonical 行为规则增强，不改变最终用户安装方法、Runtime 产品面或仓库人类入口；完成前复核。
- Figma Skill / Reference 属机器/Agent 消费治理正文，本身是本次正式事实 Owner，不按“纯说明文档”处理。

# 交付

- 提交：进行中
- 拉取请求：未创建
- 发布：不适用
