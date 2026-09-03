---
schema: coding-change/v1
id: CHG-20260903-094627-testing-skill-separation
title: 拆分独立 Testing Skill 并重构 Review Coding 测试职责
level: L2
status: active
owner: dingyuwen777
branch: change/testing-skill-separation
created: 2026-09-03
updated: 2026-09-03
completion_gate: required
depends_on: []
affected_areas:
  - skill-routing
  - testing-governance
  - review-governance
  - coding-governance
  - runtime-dynamic-distribution
affected_paths:
  - .agents/skills/testing/SKILL.md
  - .agents/skills/testing/references/
  - .agents/skills/router/SKILL.md
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/review/references/03_测试专家审查方法.md
  - .agents/skills/coding/references/25_Testing专业职责与Handoff.md
  - .agents/skills/coding/tests/test_testing_skill.py
  - .agents/skills/coding/tests/test_review_skill.py
  - README.md
  - USAGE.md
contracts: []
data_changes: []
---

# 目标

将已经散落在 Coding 与 Review 中、且正在扩展到用户场景黑盒、探索式、Integration/Workflow/Regression 的测试工程能力抽成独立 `testing` Skill，并建立 Coding / Testing / Review 单一 Owner 与可执行 Handoff。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/175

# 范围

- 新增动态发现的正式 `testing` Skill 与最少充分 canonical References。
- Testing 拥有 Test Strategy、Scenario-based Black-box Acceptance、User Journey、Exploratory Testing、Integration/Workflow/Golden Path/External Probe 测试方法、Regression 与测试资产方法。
- Coding 保留开发期 TDD、Validation Matrix/证据治理、生产实现和根因修复；新增与 Testing 的条件式 Handoff。
- Review 保留独立需求/实现审查、测试充分性和 Evidence 判断；专业测试设计/新增/系统性执行交给 Testing。
- Router 增加 Testing 的动态 Catalog、组合路由和 Coding/Review/Testing Handoff。
- 新增永久 routing/ownership/preservation 回归并更新受影响维护者/用户说明。

# 非目标

- 不新增静态 Skill allowlist；Runtime/Project Payload 继续动态发现。
- 不把所有 Coding 任务机械升级为 Testing；隔离 L1、普通开发期最小 TDD 仍可只走 Coding。
- 不把所有用户场景复制成昂贵 Real Full-stack/E2E。
- 不改变 Runtime/MCP/Bundle/Project Payload 协议、安装 schema、Release artifact contract。
- 不因为 Testing 发现缺陷自动获得生产代码、Git、merge、release 或 deploy 权限。
- 不改变具体业务项目的框架、数据库、Provider、测试工具或 CI 技术选型。

# 必须保持不变

- Coding 的 `Red → Verify Red → Green → Refactor → Re-verify`、Requirement Traceability、Validation Matrix、Completion Gate 和新鲜证据门禁继续有效。
- Review-only 默认不获得测试资产/生产实现/Git/PR/merge/release/deploy 修改权限。
- Mock/Fake、Integration、Golden Path、External Probe 的证据等级不得被夸大。
- 项目不是 Web/PostgreSQL/Provider 时，不机械要求 Browser/PostgreSQL/Provider Probe。
- Source Mode / Runtime Mode 使用同一 canonical Skill/Reference 与动态路由语义。
- Runtime/Project Payload 不增加正式 Skill 静态名单。

# 关键决策

- 采用独立 `testing` Skill，而不是继续把黑盒/探索式测试堆进 Review，因为 Testing 已具备独立输入、工作流、输出，并会被 Coding/Review/交付验证复用。
- Coding 仍拥有“开发时怎样证明实现”和 TDD，不要求每个 targeted unit test 都 Handoff Testing；Testing 只在存在独立测试工程价值时叠加。
- Review 的 `review-and-test` 改成“Review 识别 Test Gap → Testing 设计/执行 → Review 复核 Evidence”，而不是 Review 自己维护第二套测试方法。
- 用户可见 L2/L3 Feature/Bug 在存在真实公开入口且无明确不适用依据时，应有至少一个从公开入口出发的 Workflow/Black-box 证据；但状态空间仍按成本和风险分层。
- Black-box 按公开入口抽象，不等于 Browser；CLI、Library/SDK、API、Data、Mobile/Desktop、Infra 分别映射到自己的真实调用者入口。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 新增正式 Testing Skill 与最少充分 References | Issue #175 | satisfied | `testing/SKILL.md` + refs 01-03 已落地任务分支 |
| R2 | Router 自动命中 Testing，不要求用户记 Skill 名称 | Issue #175 | satisfied | Testing metadata + Router Testing 路由 + `test_testing_skill.py` 路由回归；待 CI 新鲜执行 |
| R3 | 用户可见 L2/L3 支持 Scenario-based Black-box / User Journey | Issue #175 | satisfied | Testing Core + ref02；永久回归断言关键语义；待 CI 新鲜执行 |
| R4 | Exploratory Testing 覆盖顺序/重复/失败/时间/状态/数据等真实风险 | Issue #175 | satisfied | testing ref02 按风险定义 Scenario 族与 Charter |
| R5 | Black-box 跨 Web/CLI/Library/API/Data/Mobile/Desktop/Infra 通用 | Issue #175 | satisfied | testing refs 01-02 的项目形态映射 |
| R6 | Testing 可处理测试资产，生产缺陷返回 Coding | Issue #175 | satisfied | Testing Core test-and-add/test-and-fix + ref03 Handoff |
| R7 | Review 保留充分性/Evidence 审查，不复制测试方法 | Issue #175 | satisfied | Review Core/ref01/ref03 已重构；`test_review_skill.py` 更新 |
| R8 | Coding 保留 TDD/Validation 治理，并与 Testing 分工 | Issue #175 | satisfied | coding ref25；不修改原 TDD/Validation canonical Owner |
| R9 | Runtime/Project Payload 动态发现 Testing，无静态 allowlist | Issue #175 | satisfied | 现有动态 Catalog 实现不变 + 新 `test_testing_skill.py` 检查当前正式 Catalog；待完整 Runtime Package CI |
| R10 | Source/Runtime 路由与 progressive disclosure 保持一致 | Issue #175 | satisfied | 新 Skill/Reference 使用现有 agent-routing metadata；Runtime compiler/evaluator 无协议变更；待 CI 验证 |
| R11 | 文档与当前正式 Skill Catalog/自然语言用法同步 | Issue #175 | not_satisfied | README/USAGE 待本分支同步 |
| R12 | 完整 Skill Tests、Runtime Package、独立 Review、PR/main fresh、Change archive 与 Issue Closure 完成 | Issue #175 | not_satisfied | 待 PR/CI/Review/merge/main fresh/post-merge finalization |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | `test_testing_skill.py` + `test_review_skill.py`；待 PR CI 新鲜执行 |
| 接口 / Contract | required | 当前 Routing Manifest/Public Route Contract 动态加入 Testing 与意图词汇；不改变协议 schema；待回归执行 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改业务 DB/filesystem/queue/runtime dependency 语义 |
| 用户 / Workflow Acceptance | required | Runtime evaluator 用真实 Task Route 信号验证 黑盒/User Journey/Review-and-test/Regression Handoff；待 CI 执行 |
| 跨组件 Golden Path | not_applicable | 本次不改业务应用组件接线；Runtime package 由独立 Build/Package 层验证 |
| 外部依赖 Probe | not_applicable | 不依赖第三方业务 Provider 当前事实 |
| Build / Package / Runtime | required | Runtime/Project Payload 动态分发与 package gate；待 PR/main fresh CI |
| Docs / Governance / Other | required | Change、Router/Skill Ownership、README/USAGE、A1/A2 Review、ready_check；待完成 |

# TDD / Preservation

- 现有 `test_review_skill.py` 会把测试方法锁在 Review；本次先识别为职责变更所需更新的 preservation 回归，并新增 `test_testing_skill.py` 固定新的正确 Ownership。
- Runtime 的动态 Skill discovery / Project Payload 机制保持实现不变；新增 Testing 应由现有目录发现自动进入 Bundle/route contract，若需要修改静态白名单则视为实现失败。
- Stable Reference ID 均为新 `testing.reference.*` / `coding.reference.25`，未复用或改写已有 ID；Review ref01/ref03 Stable ID 保持不变。

# Review

## A1 Requirement Review

待实现与文档同步后重新读取 Issue #175，并逐项反查 R1-R12，不能以本 Change 自身作为 Requirement Source。

## A2 Implementation / Content Preservation Review

待 PR 当前 HEAD 建立后独立检查：旧 Review 的 Findings/review-only/re-review 权限边界是否保留；Coding TDD/Validation 是否未被削弱；Testing 是否没有反向接管生产修复；Runtime dynamic discovery 是否仍无静态名单。

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# Git / 交付

- Requirement Source：Issue #175。
- 任务分支：`change/testing-skill-separation`。
- 当前宿主 GitHub App 只提供远程仓库操作，无法建立本地 checkout/首个本地 commit；因此本次使用 GitHub Contents API 在任务分支形成提交。该宿主能力差异必须在最终交付中披露，不能声称满足本地分支优先的物理执行顺序。
- 实现 PR、PR fresh CI、guarded merge、main fresh、Change archive、Closure Audit 与 Issue close 待后续真实完成。