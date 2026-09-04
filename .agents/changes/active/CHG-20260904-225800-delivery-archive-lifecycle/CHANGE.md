---
schema: coding-change/v1
id: CHG-20260904-225800-delivery-archive-lifecycle
title: 简化多人协作交付授权与 Change 自动归档生命周期
level: L3
status: ready_for_review
owner: dingyuwen777
branch: chg/20260905-repository-change-archive
created: 2026-09-04
updated: 2026-09-05
completion_gate: required
depends_on: []
affected_areas:
  - delivery-authorization
  - change-lifecycle
  - requirement-traceability
  - skill-mutation
  - runtime-routing
  - repository-archive-infrastructure
affected_paths:
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/references/28_SkillMutation影响面一致性审计.md
  - .agents/skills/coding/assets/CHANGE.template.md
  - .agents/skills/coding/scripts/ready_check.py
  - .agents/skills/coding/tests/test_ready_check.py
  - .agents/skills/coding/tests/test_delivery_archive_governance.py
  - .agents/skills/coding/tests/test_repository_change_archive_automation.py
  - .github/scripts/archive_change_after_merge.py
  - .github/workflows/change-archive.yml
contracts:
  - Delivery Authorization Contract
  - Repository-native Change Archive Contract
  - Stable Acceptance Binding Contract
  - Skill Mutation Impact Audit Contract
data_changes: []
---

# 目标

把多人协作和端到端交付收敛为一个最小且可执行的模型：开发者可完成到 PR Ready；只有当前真实身份具备目标分支 delivery authority 时才能 merge；Implementation PR merge 后由目标仓库自己的确定性基础设施归档 Change，Agent_Skills 负责验证而不再创建第二个归档 PR。Agent_Skills 仓库自身也必须遵守同一生命周期，因此补齐 repository-native Change Archive 基础设施，而不是在 #209 合并后人工搬运本 Change。

# 成功标准

- [x] 团队开发、Maintainer 自开发、Maintainer Review 三类路径职责明确且不互相越权。
- [x] 普通 Implementation 只需要一次有意义的 PR merge；Change archive 不再要求第二个 PR。
- [x] Change 的 R 行与上游稳定 AC 一一可解析，模板与机器门禁不再漂移。
- [x] Source/Runtime 路由使用 canonical metadata；永久回归覆盖新增授权值且不提高既有 Context Budget 阈值。
- [x] Agent_Skills 仓库自身具备确定性、幂等、fail-closed 的 repository-native Change Archive Workflow；平台 App 未配置时安全 no-op，不由 Agent 手工接管。

# 范围

- 调整 Coding 交付授权与 post-merge lifecycle 规则。
- 调整 Change Traceability 模板与 Ready validator。
- 增加覆盖授权、自动归档 Ownership、AC binding 和 mutation impact audit 的永久回归。
- 为 Agent_Skills 仓库补齐 `.agents/changes` 的 repository-native archive helper、Workflow 与永久回归。

# 非目标

- 不规定其他目标仓库使用哪一种 Git 托管平台或具体 Workflow 实现。
- 不在通用 Skill 中写死用户名、仓库名或业务技术栈。
- 不引入新的 Delivery Skill。
- 不给自动归档授予生产代码、Release 或 Deploy 权限。
- 不提交 GitHub App 私钥或个人 Token；平台 App/Environment/Ruleset 授权仍由仓库 Owner 在 GitHub Settings 管理。

# 必须保持不变

- Review 独立性、current-head/current-base、required CI 和 guarded merge 门禁不降低。
- `active/` / `archive/YYYY-MM/` 仍是 Coding Change 的人类可读施工生命周期视图。
- Issue/Requirement Acceptance Criteria 仍是最终完成状态 Owner。
- Runtime/Source 使用同一 canonical rules 与路由身份；不提高 Context Budget 阈值。
- Release、Deploy、生产 Migration、force push 等高权限动作继续需要独立授权。
- Archive automation 只能修改本 merged PR 对应的单一 Change source/target 和 `status`/`updated` 生命周期字段。

# 关键决策

- `develop-and-submit` 是团队开发的正式交付边界，终点为 PR Ready。
- 用户文字请求只表达 Requested Action；merge 的 Effective Authorization 必须由目标项目规则、当前 authenticated principal 与平台事实共同确认。
- Change archive 是 repository-native automation 的基础设施职责；Agent_Skills 不执行 archive commit/PR，也不在失败时静默接管。
- archive/done 表示该施工交付已进入目标分支并冻结，不等价于 Requirement Closure。
- post-merge merge SHA、main-fresh Run 等事实由 PR/Actions/Requirement Owner 承担，不为完整性机械复制回 Change。
- Agent_Skills 自身的归档 Workflow 使用专用 `Change Archivist` GitHub App token；Job 顶层保持只读权限。App 未配置时安全 no-op，并支持 `workflow_dispatch(pr_number)` 在平台配置后重跑。
- 归档必须绑定 merged PR 的 `merge_commit_sha` 原文；当前 main Active Change 与 merged revision 不一致、已有 archive 不同源、多个 Active Change、active/archive 双存在或 push 前 main 漂移时全部 fail closed。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 新增 develop-and-submit，终点为 PR Ready | #207 / AC1 | satisfied | ref23 新增正式 `develop-and-submit` 路径，明确 PR Ready 后 STOP；`test_develop_and_submit_authorization_routes_to_delivery_reference` 固化路由。 |
| R2 | Requested Action 与 Effective Authorization 分离，无权限时 merge fail closed | #207 / AC2 | satisfied | ref14/ref23 均明确 Requested Action、authenticated principal、Effective Authorization 与 `BLOCKED_BY_AUTHORIZATION`，并禁止借 bypass/Bot/其他 API 自行升级权限。 |
| R3 | merge 后由 repository-native automation 归档，Agent 不创建归档 commit/PR | #207 / AC3 | satisfied | ref14/ref23 明确 repository-native archive Owner；本仓库新增 `.github/workflows/change-archive.yml` 与 `.github/scripts/archive_change_after_merge.py`，以 merged revision + changed files 唯一绑定同一 `.agents/changes/active/<ID>`，不创建第二个 archive PR。实际 post-merge archive revision 仍由 GitHub/Issue Closure Owner 记录。 |
| R4 | 归档失败保持 blocked/incomplete，Agent 不接管掩盖故障 | #207 / AC4 | satisfied | ref23 明确失败/歧义/超时保持 `blocked/incomplete`；本仓库 Workflow 在 App 未配置时安全 no-op，helper 对 source drift、archive 不同源、多 Change、双路径和 main 漂移 fail closed；永久回归覆盖。 |
| R5 | archive 与 Requirement Closure 分离，post-merge 事实不重复复制 | #207 / AC5 | satisfied | ref14/ref23 明确 archive/done 只表示施工交付进入目标分支并冻结；Requirement Closure 继续由 Closure Audit/Acceptance Owner 决定，平台 post-merge 事实不机械复制回 Change。 |
| R6 | 持久 gated Change 的 R 显式绑定上游稳定 AC，历史 untouched archive 兼容 | #207 / AC6 | satisfied | CHANGE.template 明确 `#123 / AC1` / path#AC1；ready_check Acceptance binding parser 只对 Active Ready / 当前 changed archive 强制，新回归覆盖 generic source 拒绝、Issue AC 接受与 untouched archive 兼容。 |
| R7 | develop-and-submit 与 review-and-deliver 形成一次 Implementation PR merge 的交接 | #207 / AC7 | satisfied | ref23 明确 developer 到 PR Ready 停止、Maintainer review-and-deliver PASS 后只 guarded merge Implementation PR 一次，再进入 main-fresh/archive/Closure。 |
| R8 | Skill Mutation 增加 Rule→Template→Parser/Validator→CLI→CI→Tests→Runtime/Source 影响审计 | #207 / AC8 | satisfied | canonical Skill Mutation 专项 Reference 已接入；Rule/Template/validator/tests/runtime/source parity 逐层要求 affected / not_applicable 并 fail closed。 |
| R9 | 永久回归覆盖新生命周期且不提高上下文预算 | #207 / AC9 | satisfied | `test_delivery_archive_governance.py`、`test_ready_check.py` 与新增 `test_repository_change_archive_automation.py` 覆盖授权、稳定 AC、成功归档、同源幂等、merged revision/并发漂移、歧义和窄权限 Workflow；未提高 Context Budget 阈值。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Ready validator、授权生命周期和 repository archive helper 永久回归进入 current head，由 Skill Tests 执行。 |
| 接口 / 契约 | required | canonical References、Change Source 语法、routing contract、merged PR metadata/revision binding 和 App credential contract 均有机器实现/回归。 |
| 集成 / 持久化 / 运行依赖 | required | Workflow 在真实 checkout 上从 merged PR 获取 files/merge_commit_sha，校验 Ready gate、精确 staged allowlist，并在 push 前重新确认 current main。 |
| 用户 / 工作流验收 | required | develop-and-submit / develop-and-deliver / review-and-deliver 三条协作路径与单 Implementation merge → repository archive 已形成明确状态机。 |
| 跨组件关键路径 | required | Router metadata → Runtime evaluator → Ready gate；merged PR → archive helper → `.agents/changes` → Ready validator → guarded main push 均有直接接线。 |
| 外部依赖 / 供应方探测 | not_applicable | 不调用业务 Provider；GitHub App 私钥/Ruleset 是平台配置事实，由真实 post-merge archive 验证，不在源码伪造。 |
| 构建 / 打包 / 运行 | required | canonical Reference 继续进入 Bundle/Runtime Package；repository archive 脚本位于 `.github/`，不是分发给目标项目的 Skill payload。 |
| 文档 / 治理 / 其他 | required | Rule/Template/Validator/Tests 一致性保持；repository-specific Workflow 不改变通用 Skill 对其他托管平台的非目标边界。 |

# 完成审计

- [x] upstream_re_read：已重新读取 #207 AC1–AC9，并以当前 Requirement Source 为最终完成定义。
- [x] change_coverage：R1–R9 一一映射 AC1–AC9，没有把本 Change 作为第二套 Requirement。
- [x] reverse_audit：已从团队提交 PR、Maintainer 自交付、Review-and-deliver、权限不足、archive 成功/失败、App 未配置、merged revision 漂移、R→AC 与 Runtime routing 反向检查。
- [x] unresolved_cleared：实现范围内所有 R 均已有 current-head 代码/永久回归；实际 merge/main-fresh/archive revision/Closure 仍由 GitHub 与 Issue Owner 提供，不在 Change 伪造未来证据。

# 任务

- [x] 调查当前 Agent_Skills 规则、模板、validator 和回归事实。
- [x] 先加入能暴露旧模型缺口的永久回归，再实现新 Contract。
- [x] 实现交付授权与 repository-native archive Ownership。
- [x] 实现稳定 AC binding 模板/validator。
- [x] 增加 Skill Mutation impact audit。
- [x] 同步 Ready Check 既有回归到稳定 AC 语法。
- [x] 补齐 Agent_Skills 自身 repository-native Change Archive helper / Workflow / 永久回归。
- [x] 完成需求追溯与 Completion Audit；post-merge 平台证据由 Requirement Owner 继续承载。

# 验证

## 计划

- 目标测试：`test_ready_check.py`、`test_delivery_archive_governance.py`、`test_repository_change_archive_automation.py`。
- 相关测试：PR traceability、routing conformance、source/runtime conformance、context budget。
- 静态/运行门禁：当前 Skill Tests / Runtime Package Tests。
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。
- post-merge：确认 implementation main-fresh；Change Archive 成功后确认 active 消失、archive/done 存在及 archive revision fresh evidence，再 Closure #207。

## 新鲜证据

- current branch 包含 canonical 规则、模板、validator、repository-native archive 基础设施与永久回归；PR current-head / merge / main-fresh / archive fresh 由 GitHub Actions 与 Issue Closure Audit 提供。

# 文档影响

- canonical Coding References、Change template 与 machine validator 已同步；repository-native archive 是 Agent_Skills 仓库自身 `.github/` 基础设施，不作为通用 Skill payload 强制其他仓库复用。

# 交付

- Requirement Source：#207
- Implementation：#209 + 本次 repository archive follow-up PR。
- 发布：本任务不自动执行正式 Release；源码合并后由现有 Release 生命周期决定。
- 平台配置：专用 Change Archivist App / `change-archive-main` Environment / Ruleset bypass 是真实 GitHub Settings 事实；未配置时 Workflow 必须安全 no-op，Issue 保持 open。
