---
schema: coding-change/v1
id: CHG-20260903-094627-testing-skill-separation
title: 拆分独立 Testing Skill 并重构 Review Coding 测试职责
level: L2
status: ready_for_review
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
- Router 增加 Testing 的动态 Catalog、组合路由和 Coding/Review/Testing Handoff，同时保持渐进式披露与既有上下文预算。
- 新增永久 routing/ownership/preservation 回归并更新受影响维护者/用户说明。

# 非目标

- 不新增静态 Skill allowlist；Runtime/Project Payload 继续动态发现。
- 不把所有 Coding 或 Review 任务机械升级为 Testing；隔离 L1、普通开发期最小 TDD、没有真实 Test Gap 的 Review 仍按最少充分路径执行。
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
- Router 仍是薄控制面，不把 Testing 专业方法复制回 Router，也不破坏既有轻量路由上下文预算。

# 关键决策

- 采用独立 `testing` Skill，而不是继续把黑盒/探索式测试堆进 Review，因为 Testing 已具备独立输入、工作流、输出，并会被 Coding/Review/交付验证复用。
- Coding 仍拥有“开发时怎样证明实现”和 TDD，不要求每个 targeted unit test 都 Handoff Testing；Testing 只在存在独立测试工程价值时叠加。
- Review 的 `review-and-test` 改成“Review 识别 Test Gap → Testing 设计/执行 → Review 复核 Evidence”，而不是 Review 自己维护第二套测试方法。
- 用户可见 L2/L3 Feature/Bug 在存在真实公开入口且无明确不适用依据时，应有至少一个从公开入口出发的 Workflow/Black-box 证据；但状态空间仍按成本和风险分层。
- Black-box 按公开入口抽象，不等于 Browser；CLI、Library/SDK、API、Data、Mobile/Desktop、Infra 分别映射到自己的真实调用者入口。
- “Testing 可独立被 Router 命中”的验收含义是测试意图可以直接命中 Testing 与 Testing References，不要求伪造 Coding 实现意图；在现有保守并集/UNKNOWN 路由语义下，其他真实项目事实仍可同时命中其他 Skill，但不得改变 Testing 的测试方法 Ownership。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 新增正式 Testing Skill 与最少充分 References | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | `.agents/skills/testing/SKILL.md` 与 refs 01-03 已落地，并由动态 Skill Catalog 发现 |
| R2 | Router 自动命中 Testing，不要求用户记 Skill 名称 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | Testing metadata + Router Testing 路由 + `test_testing_skill.py`；Skill Tests #1021 中纯测试意图与组合 Handoff 回归通过 |
| R3 | 用户可见 L2/L3 支持 Scenario-based Black-box / User Journey | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | Testing Core + ref02 + 永久回归；Skill Tests #1021 通过 |
| R4 | Exploratory Testing 覆盖顺序/重复/失败/时间/状态/数据等真实风险 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | testing ref02 定义 Scenario 族与 Exploratory Charter；内容守恒回归通过 |
| R5 | Black-box 跨 Web/CLI/Library/API/Data/Mobile/Desktop/Infra 通用 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | testing refs 01-02 按公开入口与项目形态映射，不把 Black-box 等同 Browser |
| R6 | Testing 可处理测试资产，生产缺陷返回 Coding | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | Testing Core test-and-add/test-and-fix + ref03 Handoff；生产缺陷 → Coding → Testing Regression 闭环已固化 |
| R7 | Review 保留充分性/Evidence 审查，不复制测试方法 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | Review Core/ref01/ref03 + `test_review_skill.py`；Review-and-test → Testing 的路由回归通过 |
| R8 | Coding 保留 TDD/Validation 治理，并与 Testing 分工 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | coding Handoff Reference 保留 Red/Green、Validation、生产修复；Stable ID 使用 `coding.reference.26`，不复用既有 ID |
| R9 | Runtime/Project Payload 动态发现 Testing，无静态 allowlist | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | Runtime Package Tests #311 success；现有动态 Catalog/Project Payload 无静态 Testing 白名单 |
| R10 | Source/Runtime 路由与 progressive disclosure 保持一致 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | Skill Tests #1021 的 routing conformance、Runtime Bundle/Projection、Router context budget 全部通过；372 tests OK |
| R11 | 文档与当前正式 Skill Catalog/自然语言用法同步 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | `README.md` 已列入 Testing 正式职责；`USAGE.md` 已说明自然语言功能/黑盒测试及 Review→Testing→Coding→Regression→re-review 流程 |
| R12 | 合并前完成自包含测试、Runtime Package、Requirement Source 与独立 A1/A2 Review | https://github.com/dingyuwen777/Agent_Skills/issues/175 | satisfied | Skill Tests #1021：`Ran 372 tests in 5.882s` / `OK`；Requirement Source success；Runtime Package Tests #311 success；A1/A2 已完成并无未解决 pre-merge blocker |
| R13 | 合并后完成 main fresh、Change archive、Issue Closure Audit、Issue close 与分支清理 | https://github.com/dingyuwen777/Agent_Skills/issues/175 | explicitly_deferred | 这些动作依赖 PR #176 已合并后的真实 main SHA；不得在 merge 前伪造完成，合并后按 Maintenance 继续执行并回填最终证据 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | passed | GitHub Actions Skill Tests #1021：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`，372 tests，0 failures/errors |
| 接口 / Contract | passed | Routing Manifest/Public Route Contract 动态加入 Testing 与测试意图词汇；routing metadata/Stable ID/协议回归全部通过 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改业务 DB/filesystem/queue/runtime dependency 语义 |
| 用户 / Workflow Acceptance | passed | Runtime evaluator 回归覆盖黑盒/User Journey/Review-and-test/Regression/Coding+Testing Handoff 与非机械触发 |
| 跨组件 Golden Path | not_applicable | 本次不改业务应用组件接线；Runtime 分发由 Build/Package 层证明 |
| 外部依赖 Probe | not_applicable | 不依赖第三方业务 Provider 当前事实 |
| Build / Package / Runtime | passed | Runtime Package Tests #311 success；content scope 正确进入 Runtime Package Gate，三平台 binary job 按当前 scope 策略跳过 |
| Docs / Governance / Other | passed | Requirement Source success；README/USAGE 已同步；A1/A2 Review PASS；Router context budget、内容守恒、Reference ID 与 Source/Runtime conformance 均在 372 tests 内通过 |

# TDD / Preservation

- 初始实现暴露真实失败：新增 Coding Handoff Reference 错用了已被现有 Change Carrier Owner 占用的 `coding.reference.25`，导致 Runtime fail-closed 并引发 50 个同源错误；根因修复后改用新的 `coding.reference.26`，未重写既有 Stable ID。
- 随后剩余失败暴露 Router 过度增长和纯 Testing 回归语义过强；没有抬高上下文预算或削弱 evaluator，而是把 Testing 方法下沉回 Testing Owner，并把验收校准为 Issue #175 的“测试意图直接命中 Testing/Testing References”。
- 独立 A2 复核发现旧 Review 中的请求语义、真实 Integration 边界、Fixture/并发真实性、禁止任意 sleep/盲目更新 snapshot 等测试方法在职责拆分后表达变薄；已迁移到 `testing/references/01_测试策略与分层证据.md` 并增加永久内容守恒断言。
- Router 瘦身过程中曾触发旧高价值边界措辞回归；已用最短表达恢复 Anti-Agent、Source Mode 安装副本边界、L2 最小充分任务契约和 Runtime ref12/ref13 Handoff，同时 context budget 回归继续通过。
- 当前 PR HEAD 的自包含测试最终为 372 tests / 0 failures / 0 errors；没有通过删除断言、提高阈值、扩大容差或跳过失败场景换取绿色。

# Review

## A1 Requirement Review — PASS

重新读取 Requirement Source Issue #175，并从上游需求而不是本 Change 反查当前实现：独立 Testing Skill、动态发现、Black-box/User Journey/Exploratory、跨项目形态映射、测试资产与缺陷 Handoff、Review 测试充分性职责、Coding TDD/Validation 职责、progressive disclosure、Runtime 动态分发和 README/USAGE 同步均已有直接证据。未发现仍未覆盖的 pre-merge Requirement；合并后收尾单独列为 R13 `explicitly_deferred`。

## A2 Implementation / Content Preservation Review — PASS

以 `main` 上未修改的 Review Skill/ref01/ref02/ref03 作为独立审查基线，对 PR 当前职责拆分做反向内容守恒复核。已发现并修复四类问题：Stable ID 冲突、Router 上下文膨胀、过强的纯 Testing 排他断言、旧 Review 测试方法迁移不完整；另在 Router 瘦身后补回被永久回归识别出的高价值边界措辞。当前 372 条永久测试全部通过，Review-only 权限/Findings/re-review、Coding TDD/Validation、Testing 测试方法与生产缺陷 Handoff、Runtime dynamic discovery 均未发现未解决 blocker。

# Completion Audit

- [x] upstream_re_read: 已重新读取 Issue #175、当前目标分支根 `AGENTS.md` / Maintenance / Router，以及 `main` 上未修改的 Review Skill/ref01/ref02/ref03 作为独立需求与内容守恒基线。
- [x] change_coverage: R1-R12 的合并前要求均有当前文件或 GitHub Actions 直接证据；只有必须依赖真实 merge/main SHA 的 R13 明确 `explicitly_deferred`。
- [x] reverse_audit: 已从旧 Review/Coding/Router 反查 Stable ID、测试方法、权限、TDD/Validation、progressive disclosure、Source/Runtime 路由与 context budget；发现的冲突、膨胀和内容变薄均已修复并进入永久回归。
- [x] unresolved_cleared: 当前 PR HEAD 的 372 条自包含测试和 Runtime Package Gate 已通过，A1/A2 无未解决 pre-merge blocker；剩余仅为合并后 finalization，已单独列入 R13 而未冒充完成。

# Git / 交付

- Requirement Source：Issue #175。
- 任务分支：`change/testing-skill-separation`。
- 实现 PR：#176。
- 当前宿主 GitHub App 只提供远程仓库操作，无法建立本地 checkout/首个本地 commit；因此本次使用 GitHub Contents API 在任务分支形成提交。该宿主能力差异必须在最终交付中披露，不能声称满足本地分支优先的物理执行顺序。
- 当前 pre-merge 新鲜证据：Skill Tests #1021 中 372 tests / OK；Requirement Source success；Runtime Package Tests #311 success；A1/A2 PASS。
- 下一步由同一 `ready_check.py --changed-since <base>` 验证本 Change 的 `ready_for_review` / Traceability / Completion Audit；通过后才允许 guarded merge。
- merge 后必须继续执行 main fresh、Change `done` + archive、Issue Closure Audit / close #175 和已合并分支清理；这些动作在当前时点尚未完成。