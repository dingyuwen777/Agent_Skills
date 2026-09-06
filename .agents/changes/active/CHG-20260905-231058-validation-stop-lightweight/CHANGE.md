---
schema: coding-change/v1
id: CHG-20260905-231058-validation-stop-lightweight
title: 收敛测试停止条件与轻量变更执行边界
level: L2
status: ready_for_review
owner: dingyuwen777
branch: agent/validation-stop-lightweight-223
created: 2026-09-05
updated: 2026-09-06
completion_gate: required
depends_on: []
affected_areas:
  - validation-stop-rule
  - fresh-evidence
  - planning-clarification
  - mutation-semantics
  - temporary-artifact-cleanup
  - cross-model-determinism
  - equivalent-git-capability
affected_paths:
  - AGENTS.md
  - .agents/MAINTENANCE.md
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/21_系统级分析与代码整洁收口.md
  - .agents/skills/coding/references/28_SkillMutation影响面一致性审计.md
  - .agents/skills/testing/SKILL.md
  - .agents/skills/coding/tests/test_autonomy_clarification_evidence.py
  - .agents/skills/coding/tests/test_autonomy_validation_boundaries.py
  - .agents/skills/coding/tests/test_planning_contract.py
contracts:
  - Fresh Evidence Contract
  - Validation Stop Rule
  - No-New-Test Default
  - Authorization and Completion Scope
  - Task-owned Temporary Artifact Cleanup
  - Equivalent Git Capability Recovery
data_changes: []
---

# 目标

让不同能力模型使用同一套明确的默认、升级和停止条件：已授权且有安全路径就继续，只有真实新风险才扩大；低影响、可逆、行为/Contract 不变且只是澄清或复述既有实现时不新增永久测试；任务结束前清理本次产生且无后续价值的临时产物。Git 首选路径失败时先恢复实际能力，不把单个工具失败扩大为仓库不可写。

# Requested Outcome / 授权边界

沿用用户要求审阅、优化并继续原任务的范围及 PR #224。当前目标是实现、相称验证、Completion Audit、所需 Review 和 PR Ready；没有合并 `main` 的授权，不自行进入 merge、main-fresh、Change Archive、Issue Closure、Release 或 Deploy。

`ready_for_review` 是施工载体状态，不代表 GitHub 已有独立批准、current-head CI 已完成或已经合并。正式检查和审批仍按当前 PR/Actions 的真实状态判断。

# 成功标准

- [x] Fresh Evidence 只因与结论相关的变化或 required current-head gate 失效，Coding Core/完成前复核不再覆盖该规则。
- [x] 相称 Evidence 通过后有明确 Stop Rule，不重复/扩大验证。
- [x] Semantic Local/低影响可逆复述不新增永久测试。
- [x] behavior-preserving refactor 优先复用已有直接回归，不因“重构”标签自动写新测试。
- [x] L2 Planning 核心字段与条件字段分离，不逐项追问 N/A；独立重大决定可有界合并询问。
- [x] Plan Review Gate 保留重大审批，但局部可逆抽象不机械升级审批。
- [x] Mutation Apply 与 develop-and-submit/deliver 解耦，保留 Requested Outcome 与 Effective Authorization。
- [x] Semantic Local Impact Audit 支持 grouped N/A，不扫描无关机器资产。
- [x] 同一未漂移 head 的 Apply 写入前重读一次即可，不逐文件重复。
- [x] Testing 使用“建立问题模型”而非“先问”，Evidence 充分后停止重复。
- [x] 收尾只清理本任务自有、无后续用途的临时产物，不误删用户/既有文件。
- [x] 本轮续作不新增/修改测试，不调整 context budget；Maintenance 校准当前 CI 事实，不改 Workflow/Runtime。
- [x] Git 能力恢复要求先分类错误、回读副作用、发现等价路径并保留权限、原子性、防漂移及质量门禁。

# 非目标

- 不做 routing schema v2。
- 不修改 Runtime evaluator/executable、Bundle、Installer、MCP、CI Workflow 或 package 机制。
- 不降低 public Contract、Schema/数据、安全、不可逆动作、merge、Release、Deploy 的审批要求。
- 不扩大到无关 Skill、文档或技术债重构。
- 不通过文本检查宣称所有模型行为等价，不把单模型语义复核写成另一个模型或人工批准。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Fresh Evidence 有关变化失效 | #223 / AC1 | satisfied | Router Fresh Evidence Contract；续作 ea31cae 的 Coding Core §1/§4.13 与复核 Reference 证据门禁 diff，已移除无条件重跑要求 |
| R2 | Validation Stop Rule | #223 / AC2 | satisfied | Validation Stop Rule 保留；Core/复核统一核验证据后按失效或缺口运行，不因换阶段重跑 |
| R3 | No-New-Test Default | #223 / AC3 | satisfied | Validation/Mutation 原规则；Core §4.10 显式承接；续作 ea31cae 六文件 diff 没有测试文件变化 |
| R4 | Refactor 不自动新增测试 | #223 / AC4 | satisfied | Planning/Validation 的 behavior-preserving refactor 规则；Core §4.10 不再把所有 Refactor 默认为新增 Red |
| R5 | L2 Planning 条件字段 | #223 / AC5 | satisfied | Planning 最小核心 + 条件字段/N/A；Core §4.6 同步，§4.7 保持独立重大问题 Decision Package |
| R6 | Plan Review Gate 不误拦局部抽象 | #223 / AC6 | satisfied | Plan Review Gate 保留；helper/局部复用/可逆提取不机械审批 |
| R7 | 不自动扩大交付 | #223 / AC7 | satisfied | Mutation Apply 保留 Requested Outcome/Effective Authorization；Git Reference 的完整闭环改为端到端授权条件式 |
| R8 | Semantic Local grouped N/A | #223 / AC8 | satisfied | 28_SkillMutation影响面一致性审计规则保留；续作未改 metadata/Stable ID/dependency/模板/parser/Workflow/Runtime |
| R9 | Apply 重读去重复 | #223 / AC9 | satisfied | 根 AGENTS 与 Mutation Reference 保留同一未漂移 HEAD 的阶段级读取及失效条件 |
| R10 | Testing 问题模型/停止重复 | #223 / AC10 | satisfied | Testing 原实现保留；续作不修改 Testing Owner/触发或方法 |
| R11 | 临时产物清理 | #223 / AC11 | satisfied | Router Task-owned Cleanup + 整洁收口安全边界；本轮临时工作目录与既有交付文档分开认领 |
| R12 | 最小增量验证/不提高预算 | #223 / AC12 | satisfied | 原 #1265 Red、#1273/#1274 487 项 Green 保留为旧基线；续作六文件 diff 无测试/预算/运行机制修改；当前 required 检查由 PR Checks/Actions 持有，不用旧日志替代新 head 结论 |
| R13 | 等价 Git 能力恢复 | #223 / AC13 | satisfied | Git Reference 语义等价能力发现与恢复；Router 薄入口 + Core §4.1；真实本地 clone DNS 失败后，App 成功创建 blob/tree/commit，候选提交 ea31cae 已回读完整 diff |

# Validation Matrix

| 验证层 | 是否要求 | 范围 / 依据 | 当前证据 |
| --- | --- | --- | --- |
| 行为 / 单元 / 组件 | required | 复用既有 autonomy/validation/planning 与内容守恒检查，不为措辞新建测试 | 原基线 #1265 Red、#1273/#1274 487 项 Green；新内容 revision 的执行结果以本 PR current-head Actions 为准 |
| 接口 / 契约 | required | routing metadata、Owner、Stable ID、Source/Runtime 与上下文预算 | ea31cae 完整 diff：无 metadata/Stable ID/dependency 变更；现有路由/预算/原文守恒检查仍由 required CI 执行 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 未改 Runtime executable、持久化或外部产品依赖 | 六文件规则 diff 无对应运行实现 |
| 用户 / Workflow Acceptance | not_applicable | 无产品用户工作流变化；未执行跨模型效果试验 | 不把规则文字存在当作全模型效果证明 |
| 跨组件 Golden Path | not_applicable | 无产品跨组件链变化 | 不制造产品 E2E |
| 外部依赖 Probe | required | 本轮恢复 canonical Git 写入路径，限同一仓库任务分支 | 本地 clone exit 128/DNS；GitHub App blob/tree/commit 创建和 diff 回读成功；ref 更新/CI 的实际结果由 PR/Commit/Actions 持有 |
| Build / Package / Runtime | not_applicable | 未改 executable/package/platform；现有轻量编译与 CLI smoke 随 required CI | Maintenance 对齐四档 classifier 与统一 Workflow，保留 package/Release 三平台责任，不新增 binary 构建 |
| Docs / Governance / Other | required | live Issue、Change、内容守恒、Review、current-head CI | #223 AC1–AC13 已回读；实际 diff 与 canonical Owner 对照；本轮审查身份及独立批准边界见下节 |

# Independent Review

原 Review Target：PR #224，main@36b5049694fd385ad2386aaea74c5c7ab17fdb8b → 原实现 bc50a2a13cd2107599dfadd7dcd283db8d94687b。原记录中的两项 MEDIUM（Router 示例非法缩写、临时清理入口不可达）已修复，原结论为 NO_FINDINGS_WITHIN_SCOPE；该历史结果不自动覆盖续作。

续作对 9fc1ea0 → ea31cae 的六份规则执行了 A1/A2 语义复核：从 live Issue 与用户新增要求重建目标，再对照实际 diff；核对非强制 ref 与精确 head guard 的区别、结果不明先回读、真实权限拒绝不绕过、找到合法路径后停止搜索，以及证据复用/条件字段/CI Owner 的一致性。未发现需要扩大到 Runtime/Workflow/新测试机制的理由。

上述续作复核由当前 Agent 执行，不声称有另一个独立 Agent、人工 Reviewer 或 GitHub APPROVE。需要独立审批的正式门禁仍由当前 PR 实际状态判断，不由本 Change checkbox 替代。

# Completion Audit

- [x] upstream_re_read：重新读取 #223，保留 AC1–AC12 并接纳用户明确的 AC13；canonical 根入口、Maintenance、Router 与受影响专业规则可读。
- [x] change_coverage：AC1–AC13 已分别绑定正式 Owner、实际 diff 或适用执行证据；无自造上游需求。
- [x] reverse_audit：实际 diff 只有六份规则正文，未修改 metadata、测试、Runtime、Workflow 或依赖；逐项检查审批/保护/CI/清理边界未削弱。
- [x] unresolved_cleared：本轮已识别语义冲突由 ea31cae 修正；current-head required CI 与正式独立审批是独立平台门禁，强交付声明前必须继续核实真实结果，不以本记录代替。

# Docs Impact

`targeted`：维护入口的 CI 描述与当前 classifier/统一 Workflow 对齐，Mutation Reference 不再复制 scope 列表。Runtime 用户安装/使用方式、公开 CLI、Release 产物及最终用户操作不变，因此 README/USAGE/runtime README 无需同步。

# Temporary Artifact Cleanup

原实现经 GitHub/Actions 完成，无原任务临时产物。续作只认领本轮为 clone/核验创建的临时工作目录；收尾删除其中无后续用途的内容并核对路径。既有审阅修订稿与本轮最终交付文档是用户交付物，不作为临时文件删除；远端 Git 对象不冒充已更新任务分支，也不通过破坏性操作清理对象历史。
