---
schema: coding-change/v1
id: CHG-20260926-085300-doc-ownership-governance
title: 防止技术文档 Owner 交叉与长期膨胀
level: L2
status: ready_for_review
owner: yuwen.ding
branch: tech/315-doc-ownership-governance
created: 2026-09-26T08:53:00+08:00
updated: 2026-09-26
completion_gate: required
depends_on: []
affected_areas:
  - docs
  - review
  - governance
  - ci
affected_paths:
  - .agents/skills/docs/SKILL.md
  - .agents/skills/docs/references/03_审查编写与修复流程.md
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/coding/tests/test_docs_skill.py
  - .agents/skills/coding/tests/test_review_skill.py
  - .github/workflows/skill-tests.yml
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
  - .agents/skills/coding/tests/test_runtime_package_scope.py
contracts: []
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 Docs 已有“避免第二套事实”和“不为完整制造文档”的原则，但没有把“新文档准入”和“反向审计旧文档”固化成显式硬门禁，长期使用仍可能出现多个 Markdown 同时承担完整解释 Owner。
- **拟议修改**：在 Docs canonical Owner 增加单一解释 Owner、New Document Admission Gate、Document Growth Gate、临时文档 Lifecycle/Exit Gate；在 Review canonical Owner 增加 Reverse Documentation Audit；用当前 semantic tests 固化可达性与项目无关性。
- **预期结果**：Agent 默认先找已有 Owner 再决定是否新建文档；Review 不只检查新增内容正确性，还主动识别因当前变更而应收缩、合并或退出的旧文档。

# 背景、现状与问题

## 背景

Issue #315 要求把“防止文档内容交叉”的治理方案落入 Agent_Skills canonical Docs / Review 规则，并完成端到端交付。

## 当前现状

当前 Docs Skill 已经明确：

- 不制造第二套事实；
- 不为完整而制造文档；
- 默认 targeted，不机械全仓读取；
- 当前说明与历史记录分开。

当前 Review Skill 已经明确：

- 独立重建需求；
- 从影响面而不是文件数判断风险；
- 审查测试充分性与文档/实现证据。

但现有规则仍缺少两个明确动作：

1. 新建文档前没有强制执行“已有 Owner 搜索 → 准入判断”；
2. 已有文档没有显式 Growth Gate，单一文件可能持续吸收独立职责而无限膨胀；
3. docs diff Review 没有强制执行“当前新增后，旧文档是否因此应收缩/退出”的反向审计。

## 问题、根因或约束

根因是“文档创建和 Review 都偏正向”：容易回答“这篇新文档写得对不对”，但没有同等强度回答“是否根本不该新建”“旧文档是否已经失去完整解释 Owner 身份”。

如果只增加“避免重复”的抽象口号，模型仍可能在不同目录重复解释同一事实，因此需要可执行 Gate 和测试。

## 不修改的后果

- 目标项目长期积累平行说明；
- 机器事实被多篇 Markdown 重复镜像；
- Migration/Roadmap/Runbook 完成后继续滞留 live docs；
- Review 只修新文档自身，不主动降低旧文档冗余；
- 单个 Owner 文档即使没有跨文档重复，也可能逐步变成多读者任务、多生命周期的巨型容器；
- 不同模型对“是否应该新建文档”的行为不一致。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Docs 已有“不为完整而制造文档”“不会制造第二套事实”“targeted-first” | canonical Docs SKILL main | 新规则应增强现有 Owner，不建立第二套文档治理 Skill |
| E2 | Docs Write/Update 当前先问读者/事实源，但未要求证明现有 Owner 无法承载 | docs.reference.03 main | 需要 New Document Admission Gate |
| E3 | Review 当前从上游/风险/测试审查，但未明确反向文档审计 | Review SKILL/reference.01 main | Reverse Documentation Audit 应归 Review Owner |
| E4 | Maintenance 要求 Skill Mutation 保持内容守恒、项目事实不得泛化 | .agents/MAINTENANCE.md + coding.reference.15 | 不能把 AIMA 的具体 docs 目录升级为通用默认 |
| E5 | raw UTF-8 的 Docs/Review professional paths 会命中 content_targeted；但 Git 默认 quotePath 会把中文文件名转义，实际 PR 曾被误判为 unknown/package | runtime_package_scope.py + PR #316 Skill Tests 日志 | selector 本身无需改，必须修 Workflow 向 selector 提供原始 UTF-8 路径 |
| E6 | `git -c core.quotePath=false diff --name-only` 可让当前 line-based selector 接收真实 Unicode repo path | Git 行为 + 当前 workflow 数据流 | 最小修复在 changed-scope 输入边界，不改变 Runtime/routing protocol |

## 推断与待确认

- 修复 Workflow 后本 PR 因修改 CI control-plane 本身会按现有 fail-closed 规则运行一次 full semantic + 三平台 package；这是本次 CI 修改的验证成本，不代表未来普通中文 Docs/Review Reference 仍应触发 package。

# 目标、成功标准与非目标

## 目标

把“先找 Owner、再决定新建；已有文档有增长边界；文档修改后反向检查旧 Owner”变成跨模型可执行的 canonical Docs/Review 规则，同时保持项目无关和 targeted-first。

## 成功标准

- [ ] Issue #315 AC1–AC12 全部满足。
- [ ] Docs/Review semantic tests 对新规则提供直接回归。
- [ ] 当前 PR required CI 与独立 Review 通过。
- [ ] merge 后 main-fresh、Change Archive、Issue Closure 完成。

## 范围

修改 Docs/Review canonical 规则与相关语义测试；同时修复 Skill Tests changed-scope 的 Unicode Git path 输入边界并增加机器回归，以及本 Change/PR/Issue 治理载体。

## 非目标

- 不修改 Runtime、License、Release、路由协议；允许修复 Skill Tests changed-scope Workflow 的 Git path 输入。
- 不新增项目特定 docs taxonomy；
- 不实现语义相似度/向量重复检测；
- 不自动删除目标项目文档。

## 必须保持不变

- Docs 默认 targeted-first；
- Review-only 不获得修改授权；
- 文档与机器事实冲突时仍先判断正确 Owner；
- 项目自己的文档结构、命名和历史规则优先；
- Source/Runtime 的 canonical Context 加载机制不变。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与 Owner | Docs owns admission/lifecycle；Review owns independent reverse audit | E1-E4 | 不把两套规则复制到 Coding |
| 接口与契约 | 不改 Runtime/路由协议；修 CI path input | E5/E6 | 无 package protocol 迁移；Workflow 自身变化按现有 fail-closed package gate 验证 |
| 数据与迁移 | 不适用 | 无数据/Schema | 无迁移 |
| 错误与失败语义 | Gate 无法证明时默认不新建/不删除，保留现有 Owner | 内容守恒 | fail closed |
| 兼容性 | 保持现有 Docs/Review 触发和 targeted-first | E1-E5 | 现有项目行为只增强不降级 |
| 部署与回滚 | 不适用；Git 回滚 PR | 纯 canonical content/test | 无部署副作用 |

# 修改方案与决策依据

## 最小充分方案

1. Docs SKILL：增加 Single Explanation Owner + New Document Admission Gate + Document Growth Gate + Temporary Document Exit Gate。
2. docs.reference.03：把 Gate 落成 Review/Write 的实际执行步骤和知识迁移决策树。
3. Review SKILL：把文档变化加入 Reverse Documentation Audit 触发。
4. review.reference.01：定义反向审计清单、Scope/授权/正常交叉引用边界。
5. test_docs_skill / test_review_skill：增加项目无关的语义回归，防止规则以后被精简掉。
6. skill-tests.yml：关闭 Git `core.quotePath` 转义，使 Unicode Reference path 以原始 UTF-8 进入 selector；补 Workflow + selector 回归。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 不新增独立 ownership Skill | E1/E3 | Docs/Review 已是专业 Owner，新增 Skill 会制造治理交叉 |
| D2 不把目录 taxonomy 写死 | E4 | 项目结构属于目标项目 Overlay |
| D3 不做全文相似度门禁 | #315 非目标 | 词汇相似不等于 Owner 重复，容易误伤正常引用 |
| D4 普通专业 Skill 继续使用 targeted semantic tests | E5/E6 | Unicode 路径应先被正确分类；本 PR 仅因修改 Workflow control-plane 本身按现有规则升级一次 package evidence |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 单一解释 Owner | #315 / AC1 | satisfied | Docs SKILL `Single Explanation Owner` 已定义唯一完整解释 Owner 与最小上下文导航 |
| R2 | New Document Admission Gate | #315 / AC2 | satisfied | Docs SKILL + docs.reference.03 已定义 targeted Owner 搜索与准入决策树 |
| R3 | 已有 Owner 可承载则不建平行文档 | #315 / AC3 | satisfied | `已有 Owner 可以合法承载时更新已有 Owner` 已进入 Write/Update 核心规则 |
| R4 | 临时文档 Lifecycle/Exit Gate | #315 / AC4 | satisfied | Docs SKILL + docs.reference.03 已定义退出条件、知识迁移与历史 Owner 边界 |
| R5 | Docs 流程实际执行 Owner/知识迁移/Lifecycle 且 targeted-first | #315 / AC5 | satisfied | Write/Update、targeted owner search、Growth/Lifecycle Gate 已串入实际流程 |
| R6 | Review Reverse Documentation Audit | #315 / AC6 | satisfied | Review SKILL + review.reference.01 已加入 changed docs 的反向审计 |
| R7 | 不把正常交叉引用当重复 | #315 / AC7 | satisfied | Review/Docs 均明确按维护责任判断，不使用词汇/主题相似度判重 |
| R8 | Review Scope/授权/Handoff 边界不降低 | #315 / AC8 | satisfied | Reverse Audit 保持 targeted、review-only 只报告、已授权修文档 Handoff Docs |
| R9 | 语义回归且项目无关 | #315 / AC9 | satisfied | test_docs_skill/test_review_skill 新增 canonical marker 与 `AIMA` 非泛化断言 |
| R10 | changed-scope CI + independent Review | #315 / AC10 | explicitly_deferred | Ready 后由 PR current-head Skill Tests 与独立 Review 执行；本状态不冒充已通过 |
| R11 | merge/main-fresh/archive/closure | #315 / AC11 | explicitly_deferred | 属于 Ready 后 Delivery Gate；用户已授权端到端交付，实际完成后再 Closure |
| R12 | Document Growth Gate：单文件增长受读者任务/Owner/生命周期/导航约束，不用任意统一行数机械切块 | #315 / AC12 | satisfied | Docs Growth Gate + Review Growth 反查已实现，并保留项目 quantitative budget 优先 |
| R13 | Unicode professional Reference path 不因 Git quotePath 被误判 unknown/package | #315 / AC13 | satisfied | Skill Tests 使用 `git -c core.quotePath=false diff`；Workflow/selector 双回归已增加 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Docs SKILL | Admission / Owner / Growth / Lifecycle Gate | 核心专业 Owner | R1-R5/R12 |
| docs.reference.03 | 执行流程与知识迁移 | 让规则可操作 | R2-R5 |
| Review SKILL | Reverse audit 入口 | independent review 可达 | R6-R8 |
| review.reference.01 | 反向审计步骤和边界 | 避免误报/越权 | R6-R8 |
| test_docs_skill.py | Docs 语义回归 | 防退化 | R1-R5/R9 |
| test_review_skill.py | Review 语义回归 | 防退化 | R6-R9 |
| skill-tests.yml | changed-scope 使用 raw UTF-8 path | 修复中文 Reference 误判 package | R13 |
| test_ci_workflow_minimal_sufficiency.py / test_runtime_package_scope.py | 固化 Workflow + selector Unicode contract | 防 quotePath 回归 | R13 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | docs_skill / review_skill semantic tests |
| 接口 / 契约 | not_applicable | 不改 Runtime/路由协议 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无运行依赖变化 |
| 用户 / 工作流验收 | not_applicable | 无产品 UI/CLI |
| 跨组件关键路径 | required | Source canonical → Runtime targeted semantic routing 由现有 selector/router tests 覆盖 |
| 外部依赖 / 供应方探测 | not_applicable | 无外部依赖 |
| 构建 / 打包 / 运行 | required | 不改 Runtime product surface，但修改 CI Workflow control-plane；按既有 fail-closed 规则执行 full semantic + Linux/Windows/macOS package evidence |
| 文档 / 治理 / 其他 | required | Change Ready、PR Requirement Source、Skill ownership/content preservation、Review |

## 验证计划

- 目标测试：test_docs_skill.py、test_review_skill.py；
- 相关回归：changed-scope router tests、Unicode Workflow/selector contract；因 Workflow 自身变化执行 full semantic + 三平台 package；
- 静态检查：现有 Skill Tests workflow；
- 就绪检查：coding ready_check / Agent Skills Gate；
- 独立 Review：按 #315 AC1–AC11 重新重建需求并审 final diff。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 规则过重导致普通 Docs 任务变成全仓审计 | 保持 targeted-first，只扩与 Owner 冲突有直接证据的文档集合 |
| 兼容性 | 增强现有 Docs/Review，不改变触发协议 | 不改 routing metadata |
| 数据 / Migration | 不适用 | 无数据 |
| 部署 / 运行 | 不适用 | 无 Runtime 修改 |
| 回滚 / 恢复 | 回滚 PR | 无外部副作用 |

# 文档、依赖、部署与发布影响

- **长期文档**：不修改 README/USAGE，因为这是内部 canonical Skill 行为，不新增最终用户操作面。
- **依赖 / Runtime**：不修改。
- **配置 / Secret**：不修改。
- **部署 / Release**：不适用。
- **兼容 / 消费方通知**：Source/Runtime 使用同一 canonical Skill/Reference 机制自动获得新规则，不需要目标项目手工同步第二份说明。

# 完成审计

- [x] upstream_re_read：已重新读取 #315（含 AC12/AC13）与最终 Docs/Review canonical rules、Skill Tests selector/workflow。
- [x] change_coverage：已按 AC1–AC13 重建；AC1–AC9/AC12/AC13 有实现证据，AC10/AC11 明确留给 Ready 后 CI/Review/Delivery。
- [x] reverse_audit：最终规则仍只由 Docs/Review canonical Owner 承担；额外 CI diff 只修 Unicode path 输入与回归，未新增治理 Skill/Reference、项目 taxonomy 或 Runtime 协议副本。
- [x] unresolved_cleared：Requirement Traceability 无 not_satisfied；PR current-head CI/独立 Review/Delivery 作为明确的后置门禁保留。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 15198b9 | canonical read | confirmed | 当前基线与 Owner |
| V2 | branch 358cc12 | base→head diff audit | confirmed | 仅 Docs/Review rules、两项 semantic tests 与 Change 发生变化；无 Runtime/License/Release/路由协议修改 |
| V3 | branch 358cc12 | canonical marker audit | confirmed | Admission/Growth/Lifecycle/Reverse Audit 均可达，且四份通用规则未包含 AIMA 项目事实 |
| V4 | branch 358cc12 | test assertion preflight | confirmed | 新增 test_docs_skill/test_review_skill 断言目标字符串均在当前 canonical 文件中可定位 |

## 未验证内容与剩余风险

- final current-head Skill Tests（含 Workflow control-plane full/package）与独立 Review尚待当前新 Head 完成；merge/main-fresh/archive/closure 仍由 R11 约束。

## 交付状态

- 提交：canonical rules 与 semantic tests 已提交到任务分支
- 拉取请求：Ready 后立即建立/更新
- CI：由 PR current-head required checks 执行
- 合并：仅在 Review/CI Green 后 guarded merge
- Change 归档：merge 后由 repository-native Change Archive 执行
- 发布 / 部署：不适用

## 备注

无。
