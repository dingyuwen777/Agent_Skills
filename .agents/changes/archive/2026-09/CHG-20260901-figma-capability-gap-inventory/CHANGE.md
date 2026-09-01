---
schema: coding-change/v1
id: CHG-20260901-figma-capability-gap-inventory
title: Figma Design-to-Code 集中系统能力缺口清单
level: L2
status: done
owner: dingyuwen777
branch: feat/figma-capability-gap-inventory
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas:
  - figma
  - governance
  - tests
affected_paths:
  - .agents/skills/figma/SKILL.md
  - .agents/skills/figma/references/05_Design-to-Code交付门禁.md
  - .agents/skills/coding/tests/test_figma_skill.py
  - .agents/skills/coding/tests/test_figma_capability_gap_review.py
contracts: []
data_changes: []
---

# 目标

把 Figma `baseline-ready / Design-to-Code` 已有的真实系统能力检查收敛成强制、集中、可决策的 **Capability Gap Inventory / 系统能力缺口清单**。在把设计交给 Coding 前，必须让用户一次看到本次审查范围内全部已发现的未实现、未批准、未来、过期、实现错误或待决策能力，避免缺口只散落在 Findings 中或开发到一半才暴露。

# 成功标准

- [x] `baseline-ready / Design-to-Code` 在 Coding Handoff 前强制形成 Capability Gap Inventory；没有缺口时也明确输出 `none`。
- [x] 清单按真实能力/Owner 去重，不因 Normal/Loading/Empty/Error 等状态稿重复同一能力而制造噪声，同时保留必要状态差异。
- [x] 每个缺口至少包含 Figma 位置、用户能力、当前系统证据、正式事实 Owner、缺失/冲突层、分类、阻塞性和最小动作；项目不存在的层标记 `not_applicable`，不得为填表发明架构。
- [x] 已批准但尚未实现的能力继续使用现有 `implementation_required` 语义；当前任务已经批准真实跨层实现时由 Coding 整体承接，不把逐项编码责任推回用户；未批准扩大范围时先集中披露并按实际阻塞性处理，不得猜 API、永久 Mock 或伪造成功。
- [x] 未批准设计假设、Future、实现/设计漂移与待决策等继续复用 Figma 现有事实分类和 Owner 规则，不建立第二套固定 taxonomy。
- [x] Figma 主 Skill 正式输出显式暴露 Capability Gap Inventory，详细格式由 Design-to-Code Reference 唯一维护。
- [x] 自包含回归测试验证上述规则，并保持现有 Figma、Router、Bundle/Project Payload、Runtime 内容守恒回归通过。
- [x] 功能 PR 已合并，合并后 `main` fresh Skill Tests 绿色，Change 已进入独立归档分支并封存为 `done`。

# 范围

- 修改 Figma 主 Skill 的 Baseline Ready / 正式输出薄入口。
- 修改 `05_Design-to-Code交付门禁.md`，建立 Capability Gap Inventory 的详细 Owner、字段、去重、阻塞与 Handoff 规则。
- 修改现有 `test_figma_skill.py` 增加基础行为守恒回归。
- 新增 `test_figma_capability_gap_review.py` 固化独立 Review 发现的状态差异、分类单一事实源和 Coding Handoff 内容守恒要求。
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

- Capability Gap Inventory 是现有 UI → Real-System Preflight 与系统能力判断的**集中输出层**，不是新的能力判定体系。
- 去重键优先使用真实能力/正式 Owner + 用户语义；同一能力跨状态稿只保留一条主记录，但必须保留会改变实现决定的状态差异。
- Inventory 的“分类”复用当前 Figma 事实语义，不新增一组与现有规则并行的标签体系。
- `implementation_required` 只表示已批准但当前未实现；本次已批准真实跨层实现时作为一个 Coding Handoff 工作单元继续实施，不再次要求用户逐项手工编码；未批准扩大范围时先集中披露并阻止伪实现。
- 主 Skill 只保留硬门禁与正式输出入口；字段、去重和 Handoff 细节由 `05_Design-to-Code交付门禁.md` 唯一维护，避免重复漂移。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Figma 中系统尚未实现或存在冲突的能力必须在前端实施前完整列出给用户 | user:current-request | satisfied | `ref05` 在 Coding Handoff 前强制集中 Inventory；`test_capability_gap_inventory_is_complete_deduplicated_and_pre_handoff`；Skill Tests #809/#814/#815 |
| R2 | 缺口必须集中输出，不能只散落在 Findings 或开发中途才暴露 | user:approved-capability-gap-inventory | satisfied | `ref05` 明确“Coding Handoff 前必须集中输出”且“不得等到 Coding 实施中途才首次披露”；Skill Tests #809/#814/#815 |
| R3 | Inventory 必须复用现有真实事实分类，不建立第二套冲突语义 | user:approved-capability-gap-inventory | satisfied | `ref05` 明确“分类复用现有语义，不新建第二套”；`test_inventory_preserves_state_differences_and_reuses_existing_classification`；Skill Tests #809/#814/#815 |
| R4 | 不允许 Figma MCP/前端为缺失能力猜 API、永久 Mock 或伪造系统成功 | user:current-request | satisfied | 既有 6.2 禁止发明生产 Contract，Inventory 未授权分支继续禁止伪实现/永久 mock；相关既有回归 + Skill Tests #809/#814/#815 |
| R5 | 清单完整但按真实能力/Owner 去重，并保留必要状态差异 | user:approved-capability-gap-inventory | satisfied | `ref05` 显式 8 字段 + “去重但保留必要状态差异”；两组 Capability Gap 回归；Skill Tests #809/#814/#815 |
| R6 | 已授权跨层实现时由 Coding 整体承接，不要求用户逐项手工编码 | user:approved-capability-gap-inventory | satisfied | `ref05` 明确“整体交给 Coding 实施，不逐项要求用户编码”；Review 回归；Skill Tests #809/#814/#815 |
| R7 | 允许提交、推送、PR；验证通过后允许合并和归档 | user:git-delivery-authorization | satisfied | 用户明确授权；Draft #130 因连接器 Ready mutation 兼容错误关闭并按仓库 fallback 重建 #136；#136 已 guarded merge，`main` fresh #815 绿色，当前独立归档分支承载最终归档 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 两组 Capability Gap targeted regressions；Skill Tests #809/#814/#815 均 291/291 通过 |
| 接口 / 契约 | not_applicable | 不修改 public Runtime、Task Route、Reference Stable ID 或 metadata schema |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库、文件系统运行语义或外部 runtime dependency 变化 |
| 用户 / 工作流验收 | required | `baseline-ready → Capability Gap Inventory → Coding Handoff` 的集中输出、8 字段、授权/未授权分支与 `none` 均有规则 + 回归证据 |
| 跨组件关键路径 | required | 全量 self-contained Skill Tests 覆盖 Figma、Router、Bundle/Project Payload、Runtime 内容守恒；#809/#814/#815 均 291/291 通过 |
| 外部依赖 / 供应方探测 | not_applicable | 不涉及外部 Provider 当前事实 |
| 构建 / 打包 / 运行 | not_applicable | 未修改 Runtime/Builder/MCP/Installer/Release；按永久 CI 分责不触发三平台 Runtime Package Tests |
| 文档 / 治理 / 其他 | required | Source Mode 规则重读、内容守恒 TDD、Standard Review A1/A2、Ready Check、PR Skill Tests、功能 merge 与 main fresh #815；归档移动由独立归档 PR 验证 |

# 完成审计

- [x] upstream_re_read：已重新读取本轮用户要求、Agent_Skills 根 `AGENTS.md`、`MAINTENANCE.md`、ENTRY、Router、Coding/Figma canonical Owner、内容守恒与 Review required References；归档写入前再次从 `main@8417ae324bce8c1bcf2c7e87974f960fd2df8a2f` 重读根治理入口。
- [x] change_coverage：已从用户目标反查 Change 与最终 diff，覆盖集中披露、字段、去重、状态差异、分类、Handoff、禁止伪实现和 `none`，没有把 Change 自身当需求全集。
- [x] reverse_audit：已从最终实现反查 `baseline-ready → Inventory → Coding Handoff`、已批准/未批准/冲突分支和测试映射；Review 发现的字段隐式与状态差异问题均先 Red 后修复。
- [x] unresolved_cleared：R1–R7 均为 satisfied；Runtime Package Tests、外部依赖与说明文档同步均有明确 not_applicable 依据；最终 Standard Review 无剩余 BLOCKER/HIGH/MEDIUM Finding；功能合并后的 main fresh CI 已确认。

# 任务

- [x] 读取 canonical Source Mode 入口、Maintenance、Router、Coding、Figma 与 required References
- [x] 确认当前 main HEAD、Active Change 与本次 L2/PR/CI 门禁
- [x] 先新增会因缺少 Capability Gap Inventory 而失败的回归并取得 Red 证据
- [x] 修改 Figma Design-to-Code canonical 规则
- [x] 取得 targeted / full self-contained Green 证据并保持 Router 上下文预算
- [x] 完成 Requirement/内容守恒/Standard Review A1/A2；修复 Review Findings 后重新 Green
- [x] 更新 Change 到 `ready_for_review`
- [x] Draft Ready 自动调用失败后按仓库 fallback 重建非 Draft PR #136
- [x] 最终 feature head Skill Tests #814 全绿，并完成 current-head Standard Review
- [x] guarded merge PR #136，功能 merge commit `8417ae324bce8c1bcf2c7e87974f960fd2df8a2f`
- [x] 合并后 main fresh Skill Tests #815：291/291 通过，Ready Check 通过
- [x] 从已验证 main 创建独立归档分支，并将 Change 更新为 `done` 后移动到 `archive/2026-09/`

# 验证

## 新鲜证据

- 初始 TDD Red：新增 Capability Gap 基础回归后，self-contained tests 为 289 通过 / 1 失败；失败原因是 canonical Figma 规则尚无 Capability Gap Inventory。
- Skill Tests #797：290/290 通过；基础 Capability Gap 回归、Router 历史上下文预算和 Ready Check 通过。
- Skill Tests #798：新增“8 个 Inventory 字段显式存在”回归后仅该回归失败，形成 Review Finding 1 的 Red 证据。
- Skill Tests #799：字段显式化修复后 290/290 通过；字段回归与 Router 上下文预算通过。
- Skill Tests #804：新增内容守恒 Review 回归后 291 个测试仅该回归失败，明确暴露“去重保留状态差异/分类单一事实源/Coding 整体承接”缺失。
- Skill Tests #809（commit `ce30cc15791add6eded206756907ae7ed67bf78a`）：291/291 通过；两组 Capability Gap 回归、Router 历史上下文预算、Bundle/Project Payload/Runtime 内容守恒均通过；`ready_check.py --changed-since e5a147f08fb4d501e1e28a71c35bf7a100bc7057` 通过。
- Standard Review A1/A2：基于未漂移的 main `e5a147f08fb4d501e1e28a71c35bf7a100bc7057` 与实现 head `ce30cc15791add6eded206756907ae7ed67bf78a` 重新检查需求→实现、实现→测试/证据/文档；Review Findings 已通过 TDD 修复，无剩余 BLOCKER/HIGH/MEDIUM。
- Skill Tests #812（commit `3be3fc46ab5e8cddf769dfdacc9c0efebd90d010`）：291/291 通过，Ready Check 通过；验证 `ready_for_review` Change head。
- Draft #130 的 Ready mutation 因连接器 GraphQL `Repository.fullDatabaseId` 字段兼容错误失败；复核确认 PR 仍为 Draft 后按 `.agents/MAINTENANCE.md` fallback 关闭 #130，并用完全相同 head/base 重建非 Draft PR #136。
- Skill Tests #813（PR #136，head `3be3fc46ab5e8cddf769dfdacc9c0efebd90d010`）：291/291 通过，changed-since Ready Check 通过；PR mergeable=true。
- Skill Tests #814（最终 feature head `725b12f41f41a489d1610209581bbe009e38c443`）：291/291 通过；两组 Capability Gap 回归、Router 历史上下文预算、Ready Check 全绿。
- Final current-head Standard Review：PR #136 review `5076551765` 锚定 `725b12f41f41a489d1610209581bbe009e38c443`；实现 Review head 后仅 Change 治理证据更新，无剩余 BLOCKER/HIGH/MEDIUM Finding。
- Merge：PR #136 以 expected-head `725b12f41f41a489d1610209581bbe009e38c443` guarded merge，merge commit `8417ae324bce8c1bcf2c7e87974f960fd2df8a2f`。
- Main fresh CI：`main@8417ae324bce8c1bcf2c7e87974f960fd2df8a2f`，Skill Tests #815 / run `33494139304` 完整成功；`Ran 291 tests in 4.710s`、`OK`；`ready_check.py --require-active-ready` 输出 `Ready Check 通过：carrier=.agents/changes，gated=23，strict=23。`

# 文档影响

- `README.md` / `USAGE.md` / `runtime/README.md`：`not_applicable`。本次仅增强专业 Figma canonical 行为规则，不改变仓库维护入口、最终用户安装/使用方式或 Runtime 产品面。
- Figma Skill / Reference 是本次机器/Agent 消费的正式事实 Owner，本次修改本身即规则同步；不额外创建重复说明文档。

# 兼容、安全与交付影响

- 兼容性：不改变 Router 词汇、Reference Stable ID、metadata、Task Route schema、Runtime API 或安装格式。
- 依赖：无新增或升级。
- 数据 / Migration：无。
- 部署 / Release：无；正式 Release 不在本次范围。
- 回滚：可回滚功能 merge commit `8417ae324bce8c1bcf2c7e87974f960fd2df8a2f` 以恢复本次 Figma Skill/Reference 与回归测试变化；无数据迁移或外部状态需要回滚。

# 交付

- 功能分支：`feat/figma-capability-gap-inventory`
- 原 Draft PR：#130，因连接器 Ready mutation 兼容错误按仓库 fallback 关闭
- 功能 PR：#136 `增强：Figma Design-to-Code 集中披露系统能力缺口`，已合并
- 最终 feature head：`725b12f41f41a489d1610209581bbe009e38c443`
- 功能 merge commit：`8417ae324bce8c1bcf2c7e87974f960fd2df8a2f`
- main fresh CI：Skill Tests #815 success，291/291 + Ready Check 通过
- 归档：独立归档分支 `chore/archive-figma-capability-gap-inventory`，本文件已更新为 `done` 并移动到 `archive/2026-09/`；归档 PR/merge 由该分支继续承载
- Release：不适用
