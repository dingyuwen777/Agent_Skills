---
schema: coding-change/v1
id: CHG-20260904-225800-delivery-archive-lifecycle
title: 简化多人协作交付授权与 Change 自动归档生命周期
level: L3
status: proposed
owner: dingyuwen777
branch: chg/20260904-delivery-archive-lifecycle
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas:
  - delivery-authorization
  - change-lifecycle
  - requirement-traceability
  - skill-mutation
  - runtime-routing
affected_paths:
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/assets/CHANGE.template.md
  - .agents/skills/coding/scripts/ready_check.py
  - .agents/skills/coding/tests/test_ready_check.py
  - .agents/skills/coding/tests/test_delivery_archive_governance.py
contracts:
  - Delivery Authorization Contract
  - Repository-native Change Archive Contract
  - Stable Acceptance Binding Contract
  - Skill Mutation Impact Audit Contract
data_changes: []
---

# 目标

把多人协作和端到端交付收敛为一个最小且可执行的模型：开发者可完成到 PR Ready；只有当前真实身份具备目标分支 delivery authority 时才能 merge；Implementation PR merge 后由目标仓库自己的确定性基础设施归档 Change，Agent_Skills 负责验证而不再创建第二个归档 PR。

# 成功标准

- [ ] 团队开发、Maintainer 自开发、Maintainer Review 三类路径职责明确且不互相越权。
- [ ] 普通 Implementation 只需要一次有意义的 PR merge；Change archive 不再要求第二个 PR。
- [ ] Change 的 R 行与上游稳定 AC 一一可解析，模板与机器门禁不再漂移。
- [ ] Source/Runtime 路由和既有上下文预算不退化。

# 范围

- 调整 Coding 交付授权与 post-merge lifecycle 规则。
- 调整 Change Traceability 模板与 Ready validator。
- 增加覆盖授权、自动归档 Ownership、AC binding 和 mutation impact audit 的永久回归。

# 非目标

- 不规定目标仓库使用哪一种 Git 托管平台或具体 Workflow 实现。
- 不在通用 Skill 中写死用户名、仓库名或业务技术栈。
- 不引入新的 Delivery Skill。
- 不给自动归档授予生产代码、Release 或 Deploy 权限。

# 必须保持不变

- Review 独立性、current-head/current-base、required CI 和 guarded merge 门禁不降低。
- `active/` / `archive/YYYY-MM/` 仍是 Coding Change 的人类可读施工生命周期视图。
- Issue/Requirement Acceptance Criteria 仍是最终完成状态 Owner。
- Runtime/Source 使用同一 canonical rules 与路由身份；不提高 Context Budget 阈值。
- Release、Deploy、生产 Migration、force push 等高权限动作继续需要独立授权。

# 关键决策

- `develop-and-submit` 是团队开发的正式交付边界，终点为 PR Ready。
- 用户文字请求只表达 requested action；merge 的 effective authorization 必须由目标项目规则、当前 authenticated principal 与平台事实共同确认。
- Change archive 是 repository-native automation 的基础设施职责；Agent_Skills 不执行 archive commit/PR，也不在失败时静默接管。
- archive/done 表示该施工交付已进入目标分支并冻结，不等价于 Requirement Closure。
- post-merge merge SHA、main-fresh Run 等事实由 PR/Actions 拥有，不为完整性机械复制回 Change。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 新增 develop-and-submit，终点为 PR Ready | #207 / AC1 | not_satisfied | 尚未验证 |
| R2 | Requested Action 与 Effective Authorization 分离，无权限时 merge fail closed | #207 / AC2 | not_satisfied | 尚未验证 |
| R3 | merge 后由 repository-native automation 归档，Agent 不创建归档 commit/PR | #207 / AC3 | not_satisfied | 尚未验证 |
| R4 | 归档失败保持 blocked/incomplete，Agent 不接管掩盖故障 | #207 / AC4 | not_satisfied | 尚未验证 |
| R5 | archive 与 Requirement Closure 分离，post-merge 事实不重复复制 | #207 / AC5 | not_satisfied | 尚未验证 |
| R6 | 持久 gated Change 的 R 显式绑定上游稳定 AC，历史 untouched archive 兼容 | #207 / AC6 | not_satisfied | 尚未验证 |
| R7 | develop-and-submit 与 review-and-deliver 形成一次 Implementation PR merge 的交接 | #207 / AC7 | not_satisfied | 尚未验证 |
| R8 | Skill Mutation 增加 Rule→Template→Parser/Validator→CLI→CI→Tests→Runtime/Source 影响审计 | #207 / AC8 | not_satisfied | 尚未验证 |
| R9 | 永久回归覆盖新生命周期且不提高上下文预算 | #207 / AC9 | not_satisfied | 尚未验证 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Ready validator、授权与生命周期回归 |
| 接口 / 契约 | required | canonical Reference、Change schema/Source 语法和 routing contract |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改数据库或运行依赖 |
| 用户 / 工作流验收 | required | develop-and-submit / develop-and-deliver / review-and-deliver 三条真实协作路径 |
| 跨组件关键路径 | required | Router/Reference → Runtime required Context → Ready gate |
| 外部依赖 / 供应方探测 | not_applicable | 不需要真实外部 Provider |
| 构建 / 打包 / 运行 | required | Runtime content/package scope 与 Source/Runtime conformance |
| 文档 / 治理 / 其他 | required | Rule/Template/Validator/Tests 一致性与 Change Completion |

# 完成审计

- [ ] upstream_re_read：完成前重新读取 #207 当前 AC1–AC9。
- [ ] change_coverage：逐条确认 R1–R9 覆盖全部上游要求。
- [ ] reverse_audit：从三种交付模式、权限不足、archive 成功/失败、AC binding 和 Runtime/Source 反向审计。
- [ ] unresolved_cleared：所有 not_satisfied 清零，延期或不适用均有正式依据。

# 任务

- [x] 调查当前 Agent_Skills 规则、模板、validator 和回归事实。
- [ ] 建立 Red 回归。
- [ ] 实现交付授权与 repository-native archive Ownership。
- [ ] 实现稳定 AC binding 模板/validator。
- [ ] 增加 Skill Mutation impact audit。
- [ ] 运行 targeted + self-contained + routing/context conformance。
- [ ] 完成 A1/A2 Review 与 PR current-head CI。

# 验证

## 计划

- 目标测试：`test_ready_check.py`、`test_delivery_archive_governance.py`。
- 相关测试：PR traceability、routing conformance、source/runtime conformance、context budget。
- 静态检查：当前 Skill Tests / Runtime Package Gate。
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。

## 新鲜证据

- 尚未执行。

# 文档影响

- canonical Coding References、Change template 与 machine validator 需要同步；不新增第二套用户手册。

# 交付

- Requirement Source：#207
- 拉取请求：待创建
- 发布：本任务不自动执行正式 Release；源码合并后由现有 Release 生命周期决定。
