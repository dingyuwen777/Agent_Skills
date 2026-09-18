---
schema: coding-change/v1
id: CHG-20260918-165459-figma-owner-prototype-acceptance
title: Figma 系统化 Owner 与无代码 Prototype 验收通用规则
level: L2
status: done
owner: dingyuwen777
branch: feature/figma-owner-prototype-acceptance
created: 2026-09-18T16:54:59+08:00
updated: 2026-09-18
completion_gate: required
depends_on: []
affected_areas:
  - figma
  - governance
affected_paths:
  - .agents/skills/figma/SKILL.md
  - .agents/skills/figma/references/03_设计系统与组件复用审计.md
  - .agents/skills/figma/references/04_Prototype状态与交互审计.md
  - .agents/skills/figma/references/05_Design-to-Code交付门禁.md
  - .agents/skills/coding/tests/test_figma_skill.py
contracts:
  - figma-skill-semantic-contract
data_changes: []
---

# 变更摘要

- 要解决的问题：现有 Figma Skill 对系统化设计层级保护和“正式 Prototype 可在不写代码前完整验收交互”的要求不够明确。
- 拟议修改：增强既有 Figma SKILL 与 03/04/05 References，并补最小内容守恒测试；不新增平行 Reference，不改 routing metadata / Stable ID / Runtime。
- 预期结果：Figma baseline-ready 会同时检查 Design Owner 层级完整性和 Prototype Interaction Completeness。

# 背景、现状与问题

## 背景

Requirement Source 为 Issue #264。需求来自真实设计审查经验，但本变更只抽取跨项目通用方法，不携带任何业务项目事实。

## 当前现状

- 03 Reference 已有 Owner-first、不得 Detach、受影响消费者复核。
- 04 Reference 已覆盖 Reaction / Variable / Flow，但未明确 enabled 控件全覆盖与无代码验收。
- 05 Reference 已有 NOT_READY / READY Checklist 与 Design-to-Code Gate。
- test_figma_skill.py 已承担高价值 Figma 规则内容守恒。

## 问题、根因或约束

现有规则仍允许两个歧义：一是正式 Screen/State Frame 可能被直接改成第二 Owner；二是静态页面视觉完成但 enabled 按钮无 Reaction 时，缺少明确 READY 阻塞语义。

## 不修改的后果

设计系统会逐步产生页面级平行实现，正式原型也可能只能看不能验收，导致 Design-to-Code 前才暴露交互缺口。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 | 支撑决策 |
| --- | --- | --- | --- |
| E1 | 03 已有 Owner-first Gate | 03_设计系统与组件复用审计.md | 增强既有 Owner |
| E2 | 04 已维护 Prototype Reaction/Flow | 04_Prototype状态与交互审计.md | 交互完整性归 04 |
| E3 | 05 已维护 baseline-ready | 05_Design-to-Code交付门禁.md | READY 门禁归 05 |
| E4 | 现有测试保护 Figma 高价值语义 | test_figma_skill.py | 增加最小内容守恒断言 |
| E5 | 上游 AC 已稳定 | Issue #264 | 需求追溯来源 |

## 推断与待确认

无。

# 目标、成功标准与非目标

## 目标

把系统化 Design Owner 层级保护与无代码 Prototype 验收写成 Figma Skill 通用硬门禁。

## 成功标准

- [ ] Issue #264 AC1–AC9 全部满足。
- [ ] Figma SKILL 保持薄入口，详细规则仍由 03/04/05 唯一维护。
- [ ] routing metadata / Stable ID / dependency 不变。
- [ ] 最小相关测试与 required CI 通过。
- [ ] 内容守恒 Review 无业务项目事实和第二 Owner。

## 范围

- Figma SKILL、03/04/05 References、test_figma_skill.py。

## 非目标

- 不新增 Reference。
- 不改 Coding/Testing/Review 详细规则。
- 不改 Runtime/Bundle/Installer/Project Payload/Release。
- 不引入任何业务项目名、字段、Provider 或页面尺寸。

## 必须保持不变

- Figma 详细设计规则唯一 Owner。
- Coding 继续负责生产代码与交付。
- Prototype Representative State 不等于真实系统成功。
- Figma 设计层级与代码组件架构不要求机械 1:1。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只改既有 Figma Owner + 测试 | E1-E4 | 不造新 Reference |
| 接口与契约 | 语义增强，route metadata 不变 | E1-E3 | Semantic Local |
| 数据与迁移 | 不适用 | 无数据变化 | 无 Migration |
| 错误与失败语义 | enabled 死控件可阻塞 baseline-ready | #264 / AC4 | READY 更明确 |
| 兼容性 | 保持旧规则并增强 | 内容守恒 | 无旧能力删除 |
| 部署与回滚 | Markdown + test，可 Git 回滚 | 无 Runtime 变化 | 无部署 |

# 修改方案与决策依据

## 最小充分方案

1. 03 增加按项目语义映射的 Ownership Ladder：Foundation/Token → Shared → Page Template/Pattern → Feature/Page Public Owner → Formal Screen/State Consumer。
2. 04 增加 Prototype Interaction Completeness / No-code Acceptance Gate：所有视觉上可操作且 enabled 的控件必须有有效 Reaction；关键用户流程必须可从入口走到代表性终态并有返回/关闭路径。
3. 05 把两项要求加入 NOT_READY 和 Baseline Ready Checklist。
4. Figma SKILL 只增加薄硬门禁入口，不复制详细清单。
5. test_figma_skill.py 增加最小内容守恒断言。

## 证据到决策

| 决策 | 依据证据 | 原因 |
| --- | --- | --- |
| D1 不新增 Reference | E1-E3 | 现有 03/04/05 已是正确 Owner |
| D2 交互完整性归 04 | E2 | 避免第二套 Prototype 规则 |
| D3 READY 门禁归 05 | E3 | baseline-ready 唯一 Owner |
| D4 增加最小测试 | E4 | 防止后续精简回退 |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 建立 Design Ownership Ladder | #264 / AC1 | satisfied | 03 Reference 已定义 Foundation/Token → Shared → Page Template/Pattern → Feature/Page Public → Formal Screen/State Consumer，并允许按项目真实层级跳过/映射 |
| R2 | 禁止正式页面制造第二 Owner | #264 / AC2 | satisfied | 03 Owner-first 明确 Formal Screen/State 只消费真实 Owner，禁止 Detach/复制/重画/外覆制造第二 Owner，并要求复核受影响消费者 |
| R3 | 正式 Prototype 支持无代码验收 | #264 / AC3 | satisfied | 04 新增 Prototype Interaction Completeness / No-code Acceptance Gate，要求从 Starting Point 在不依赖前端代码时走通关键任务 |
| R4 | enabled 控件必须有 Reaction | #264 / AC4 | satisfied | 04 明确 enabled + 可操作外观必须有有效 Reaction；disabled/readonly 可无动作但必须显式；reactions=[] 属 Finding |
| R5 | 主/次级/低频操作及返回路径完整 | #264 / AC5 | satisfied | 04 覆盖主操作、次级/低频管理、筛选/分页/展开收起、Open/Close/Back、Confirm/Cancel/Retry，并要求返回/关闭/取消可达 |
| R6 | 保持 Representative State 边界 | #264 / AC6 | satisfied | 04 保留并强化 Representative State ≠ 真实执行结果；系统不存在的能力不得用假 Reaction 伪造 |
| R7 | baseline-ready 纳入硬门禁 | #264 / AC7 | satisfied | 05 NOT_READY 与 Baseline Ready Checklist 已纳入 Design Ownership Ladder、enabled Reaction 与 No-code Acceptance |
| R8 | SKILL 薄入口，03/04/05 唯一维护 | #264 / AC8 | satisfied | SKILL 只增加硬门禁入口；03/04/05 分别继续唯一维护 Owner、Prototype、READY 细则；未新增 Reference |
| R9 | route metadata 不变且测试/CI 通过 | #264 / AC9 | satisfied | 03/04/05/SKILL routing block 与 main 精确相同；PR #265 head 40f3fb8 的 Skill Tests #1473 success：562/562 semantic tests、context budget、Linux/macOS/Windows onefile Runtime build/self-test、stdio MCP Contract 与 project-only install 均通过 |

# 计划改动

| 文件 / 模块 | 计划修改 | 对应要求 |
| --- | --- | --- |
| figma/SKILL.md | 增加薄硬门禁入口 | R7-R8 |
| 03 Reference | 系统化 Owner 层级链 | R1-R2 |
| 04 Reference | 无代码验收与交互完整性 | R3-R6 |
| 05 Reference | NOT_READY / Checklist / Handoff | R7 |
| test_figma_skill.py | 内容守恒断言 | R9 |

- [x] 调查当前实现和事实源
- [x] 建立验证矩阵
- [x] 完成最小规则修改
- [x] selected semantic tests：562/562 passed；上下文预算保护通过
- [x] 完成 Requirement Traceability 与 Completion Audit；仅 R9 final required CI 有正式 deferred 依据
- [x] 独立 Review 与 Ready PR required CI 完成：Review Finding“Page-private 被过度约束”已修复，Skill Tests #1473 全绿

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | not_applicable | 无生产行为代码变化 |
| 接口 / 契约 | not_applicable | route metadata / Stable ID 不变 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无 Runtime/持久化变化 |
| 用户 / 工作流验收 | not_applicable | 无产品运行时用户流程 |
| 跨组件关键路径 | not_applicable | 无 Runtime 组装变化 |
| 外部依赖 / 供应方探测 | not_applicable | 无外部依赖 |
| 构建 / 打包 / 运行 | not_applicable | 无 Runtime/Package 变化 |
| 文档 / 治理 / 其他 | required | Figma canonical 语义、内容守恒、route metadata 不变、required CI |

## 验证计划

- 目标测试：.agents/skills/coding/tests/test_figma_skill.py
- 相关回归：仓库 selector 选择的 Figma/portability/routing tests
- 静态检查或构建：按当前 CI selector
- 专项真实边界：人工内容守恒 Review
- 就绪检查：ready_check.py --require-active-ready

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 处理 |
| --- | --- | --- |
| 主要风险 | 规则过度绝对化或重复 | 用“按项目语义映射”“enabled/视觉可操作”“Representative State”限制 |
| 兼容性 | 保持 | 不改 route metadata / Stable ID |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不适用 | 无 Runtime/Release 变化 |
| 回滚 / 恢复 | Git 回滚 | Markdown/Test 可逆 |

# 文档、依赖、部署与发布影响

- 长期文档：Figma canonical Skill/References 本身就是正式规则 Owner；README/USAGE 不受影响。
- 依赖 / Runtime：不变。
- 配置 / Secret：不变。
- 部署 / Release：不适用。
- 兼容 / 消费方通知：无 public Runtime Contract 变化。

# 完成审计

- [x] upstream_re_read：已重新读取 Issue #264、Figma Skill/03/04/05、Maintenance 与 Mutation 规则。
- [x] change_coverage：AC1–AC9 全部有当前实现、route identity、semantic tests 或 package evidence。
- [x] reverse_audit：selected routing/skill tests 通过；Figma review/fix/baseline-ready → Router → Skill → References 可达，03/04/05 保持唯一 Owner。
- [x] unresolved_cleared：R1–R9 全部 satisfied，无 not_satisfied / explicitly_deferred / 未说明阻塞项。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 检查 | 结果 | 证明 |
| --- | --- | --- | --- | --- |
| V1 | main@46a872c | canonical Figma Skill / References / test / Maintenance 定向读取 | 已恢复现状 | 范围和唯一 Owner 已确认 |
| V2 | PR #265 head bcef845 | Skill Tests #1468 selected self-contained tests | 562 tests passed / 0 failed | Figma 内容守恒、routing、portability、context budget 等选中语义通过 |
| V3 | main ↔ branch | 03/04/05/SKILL agent-routing block 精确比较 + 项目特定词扫描 | routingUnchanged=true；AIMA_UGC/TikHub/采集策略/声音广场/docs/blueprint 均 0 命中；live Figma rules 总长度比 main 少 1349 字符 | Stable ID/路由身份未变，规则未携带业务事实且未膨胀 Runtime Context |
| V4 | PR #265 head 40f3fb8 | Skill Tests #1473 | success：Agent Skills Gate、Runtime Package Gate、Linux/macOS/Windows package jobs 全绿 | 562/562 semantic tests、context budget、三平台 Runtime package/self-test、stdio MCP Contract、project-only install 均通过 |
| V5 | PR #265 Review | Issue #264 → diff → tests/content conservation 独立 A1/A2 Review | NO_FINDINGS_WITHIN_SCOPE；Review 中发现的 Page-private 过度约束已修复并 re-review | 通用规则未机械组件化、未携带业务事实、未产生第二 Owner |

## 未验证内容与剩余风险

规则实现、独立 Review 与 required CI 已完成。剩余只有 Git 交付决策：用户尚未授权 merge，因此 PR 保持 Ready 等待合并指令。

## 交付状态

- 提交：a16bffb（Change 初始化）+ 5b23376（规则实现）+ bcef845（上下文预算收敛）
- 拉取请求：Draft PR #265
- CI：Ready PR head 40f3fb8 的 Skill Tests #1473 success；Agent Skills Gate / Runtime Package Gate / Linux/macOS/Windows package 全绿
- 合并：required CI/Review 已完成，但用户未授权 merge；PR #265 保持 Ready，等待明确合并指令
- Change 归档：仅在 implementation merge 后由 repository-native automation 处理
- 发布 / 部署：不适用

## 备注

Requirement Source：Issue #264。