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
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
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
- 为 Agent_Skills 自身补齐 `.agents/changes` repository-native Change Archive helper / Workflow / 回归。

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
- 用户文字请求只表达 Requested Action；merge 的 Effective Authorization 必须由目标项目规则、当前 authenticated principal 与平台事实共同确认。
- Change archive 是 repository-native automation 的基础设施职责；Agent_Skills 不执行 archive commit/PR，也不在失败时静默接管。
- archive/done 表示该施工交付已进入目标分支并冻结，不等价于 Requirement Closure。
- post-merge merge SHA、main-fresh Run 等事实由 PR/Actions 拥有，不为完整性机械复制回 Change。
- Agent_Skills 自身使用同一窄权限 Change Archivist App 模型；平台 App/Environment/Ruleset bypass 未配置时只允许 safe no-op。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 新增 develop-and-submit，终点为 PR Ready | #207 / AC1 | satisfied | ref23 新增正式 `develop-and-submit` 路径，明确 PR Ready 后 STOP；永久回归固化路由。 |
| R2 | Requested Action 与 Effective Authorization 分离，无权限时 merge fail closed | #207 / AC2 | satisfied | ref14/ref23 明确 Requested Action、authenticated principal、Effective Authorization 与 `BLOCKED_BY_AUTHORIZATION`，并禁止借 bypass/Bot/其他 API 自行升级权限。 |
| R3 | merge 后由 repository-native automation 归档，Agent 不创建归档 commit/PR | #207 / AC3 | satisfied | ref14/ref23 明确 repository-native archive Owner；Agent_Skills 自身已通过 #210 合入 `.github/scripts/archive_change_after_merge.py` 与 `.github/workflows/change-archive.yml`，绑定 merged revision、单 Change、lifecycle-only 与精确 allowlist；平台 App 未配置时 safe no-op，不由 Agent 手工接管。 |
| R4 | 归档失败保持 blocked/incomplete，Agent 不接管掩盖故障 | #207 / AC4 | satisfied | ref23 与仓库 Archive Workflow 都明确失败/歧义/凭证未配置保持 blocked/incomplete 或 safe no-op，Agent 不自行接管归档。 |
| R5 | archive 与 Requirement Closure 分离，post-merge 事实不重复复制 | #207 / AC5 | satisfied | ref14/ref23 明确 archive/done 只表示施工交付进入目标分支并冻结；Requirement Closure 继续由 Closure Audit/Acceptance Owner 决定。 |
| R6 | 持久 gated Change 的 R 显式绑定上游稳定 AC，历史 untouched archive 兼容 | #207 / AC6 | satisfied | CHANGE.template 明确稳定 AC 绑定；ready_check parser 与回归覆盖 generic source 拒绝、Issue AC 接受与 untouched archive 兼容。 |
| R7 | develop-and-submit 与 review-and-deliver 形成一次 Implementation PR merge 的交接 | #207 / AC7 | satisfied | ref23 明确 developer 到 PR Ready 停止、Maintainer review-and-deliver PASS 后只 guarded merge Implementation PR 一次，再进入 main-fresh/archive/Closure。 |
| R8 | Skill Mutation 增加 Rule→Template→Parser/Validator→CLI→CI→Tests→Runtime/Source 影响审计 | #207 / AC8 | satisfied | canonical `coding.reference.29` 与专项影响审计已经合入。 |
| R9 | 永久回归覆盖新生命周期且不提高上下文预算 | #207 / AC9 | satisfied | `test_delivery_archive_governance.py`、`test_ready_check.py`、`test_repository_change_archive_automation.py`、Workflow Responsibility Audit 均已纳入；未提高 Context Budget 阈值。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Ready validator、授权/生命周期、repository-native archive helper 永久回归由 Skill Tests 执行。 |
| 接口 / 契约 | required | canonical References、Change Source、merged PR `merge_commit_sha` 与 archive CLI contract 已同步。 |
| 集成 / 持久化 / 运行依赖 | required | repository Change Archive Workflow 真实监听 merged PR/dispatch，配置缺失时 safe no-op；平台 App 配置后才允许 main 写入。 |
| 用户 / 工作流验收 | required | develop-and-submit / develop-and-deliver / review-and-deliver 与 merge→archive→Closure 状态机已形成。 |
| 跨组件关键路径 | required | Router metadata → Runtime evaluator → Ready gate；merged PR metadata → archive helper → `.agents/changes` carrier 已有真实 Workflow 接线。 |
| 外部依赖 / 供应方探测 | required | GitHub App/Environment/Ruleset 是平台依赖；凭证缺失已由 Change Archive 首次运行真实验证为 safe no-op。 |
| 构建 / 打包 / 运行 | required | #210 current-head 与 main-fresh `Agent Skills Gate` / `Runtime Package Gate` 负责；本次 scope 非 package，Windows/macOS package jobs 合法 skipped。 |
| 文档 / 治理 / 其他 | required | Rule/Template/Validator/Tests/Workflow Responsibility Audit 一致性已实现，third-party Actions 固定 commit SHA。 |

# 完成审计

- [x] upstream_re_read：已重读 #207 AC1–AC9，并以当前 Requirement Source 为最终完成定义。
- [x] change_coverage：R1–R9 一一映射 AC1–AC9，没有把本 Change 作为第二套 Requirement。
- [x] reverse_audit：已从团队提交 PR、Maintainer 自交付、Review-and-deliver、权限不足、archive 成功/失败、merged revision 漂移、R→AC 与 Runtime routing 反向检查。
- [x] unresolved_cleared：代码/规则/测试/仓库 Workflow 均已有真实实现；平台 App 凭证是外部配置边界，缺失时按规则保持 Issue open，不伪造 archive 成功。

# 任务

- [x] 调查当前 Agent_Skills 规则、模板、validator 和回归事实。
- [x] 先加入能暴露旧模型缺口的永久回归，再实现新 Contract。
- [x] 实现交付授权与 repository-native archive Ownership。
- [x] 实现稳定 AC binding 模板/validator。
- [x] 增加 Skill Mutation impact audit。
- [x] 同步 Ready Check 既有回归到稳定 AC 语法。
- [x] 补齐 Agent_Skills 自身 repository-native Change Archive helper / Workflow / 永久回归。
- [x] 完成需求追溯与 Completion Audit。
- [x] PR #210 current-head Skill Tests 与 L3 A1/A2 Review 通过并 guarded merge。
- [x] #210 implementation main-fresh `Agent Skills Gate` / `Runtime Package Gate` 通过。
- [ ] 配置专用 Change Archivist App / Environment / Ruleset bypass 后，dispatch #210 取得真实 archive/done + archive-fresh 证据。

# 验证

## 新鲜证据

- PR #210 exact head `1e623cc62f743ded6559202dbd2acc4fd780ae62`：Skill Tests #1199，`Agent Skills Gate` / `Runtime Package Gate` 均 success；L3 Review `NO_FINDINGS_WITHIN_SCOPE`。
- Implementation merge revision `9d81645e3fcfae9e5da60827c12acf3d9c35fbf8`：main-fresh `Agent Skills Gate` / `Runtime Package Gate` 均 success。
- Change Archive #1 已真实触发，但 `CHANGE_ARCHIVE_APP_ID` / `CHANGE_ARCHIVE_APP_PRIVATE_KEY` 为空，按契约 safe no-op；当前 Change 因此仍保持 active/ready。

# 交付

- Requirement Source：#207
- Implementation PR：#209、#210
- 当前外部阻塞：GitHub Settings 中的专用 Change Archivist App、`change-archive-main` Environment secrets 与 Ruleset bypass。配置后应对 merged PR #210 执行 Change Archive `workflow_dispatch`，不得手工归档。
