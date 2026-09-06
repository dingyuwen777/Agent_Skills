---
schema: coding-change/v1
id: CHG-20260906-141857-user-doc-boundary
title: 重划 README 与 USAGE 的受众和使用说明边界
level: L2
status: done
owner: dingyuwen777
branch: docs/reorganize-readme-usage-227
created: 2026-09-06
updated: 2026-09-06
completion_gate: required
depends_on: []
affected_areas:
  - documentation
  - release-user-guide
affected_paths:
  - README.md
  - USAGE.md
  - .agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py
  - .agents/skills/coding/tests/test_project_governance_bootstrap.py
  - .agents/skills/coding/tests/test_release_only_repository_surface.py
  - .agents/skills/coding/tests/test_release_platform_zips.py
contracts:
  - README.md 继续作为维护者和项目管理员入口并承载接入维护说明
  - USAGE.md 继续作为 Release 随包人类说明但只面向已完成接入后的普通开发者
  - 普通开发者写入型任务统一止于 PR Ready 交由维护者审核
  - Release ZIP 成员结构和 Runtime MCP 路由协议及专业 Skill 语义保持不变
data_changes: []
---

# 目标

把维护/接入知识与普通开发者日常使用说明彻底分开：README 承担维护者需要的分发、安装、首次治理、状态/自检、升级/回退和网页 Source Mode；USAGE 假设项目已经完成开发环境配置和首次治理，只告诉普通开发者如何在 Codex、Cursor、Claude Code 等桌面 AI Agent 中完成典型研发任务，并统一在 PR Ready 后交给维护者审核。

# 成功标准

- [x] README 明确维护者/项目管理员受众，并承接仍有效的分发、安装、首次治理、状态/自检、升级/回退和网页端 Source Mode 说明。
- [x] USAGE 不再暴露 Agent_Skills、binary、Runtime/MCP、Source Mode、网页端、AGENTS 首次校准、安装、升级或回退等内部接入信息。
- [x] USAGE 覆盖功能开发、Bug、重构、黑盒测试、Review、Review+Fix、文档、Figma/Design-to-Code、版本变更和多人 Git 协作，并把普通开发者写入型任务统一停在 PR Ready。
- [x] 与旧人类文档职责绑定的永久测试已经迁移到新的文档 Owner；Runtime/Release/Bootstrap/ZIP/导航等实际机器验证责任没有删除或放宽。
- [x] 当前实现范围的 content-scope 自包含回归与文档职责复核已经取得 Green；最终 current-head required checks、merge、main-fresh、原生 Change Archive 和 Issue Closure 继续由平台交付门禁完成。

# 范围

修改根 README.md、USAGE.md，以及四个直接绑定旧人类文档 Contract 的永久回归测试。测试变化只迁移“哪份人类文档承担说明”的断言；真实 Runtime 生命周期、首次 Bootstrap、三平台 ZIP 组装、Project Payload、Release identity、Markdown 导航和其他机器责任继续由原测试执行。

# 非目标

不发布 Release/tag；不改变 Release ZIP 成员；不修改 Runtime、MCP Tool、Router、Skill、Reference、CI Workflow 或安装器实现；不修改 AIMA_UGC 或其他目标业务项目；不降低现有保护规则、Review、CI 或交付标准。

# 必须保持不变

项目事实优先、权限与授权边界、Review/Testing/Docs/Figma/Coding 的专业语义、PR/CI/guarded merge/main-fresh/Change Archive/Requirement Closure 责任保持不变。普通开发者文档只隐藏治理实现与接入细节，不隐藏真实项目调查、修改、测试、文档、Review、Git/CI 和交付结果。

# 关键决策

- `README.md` 是维护者/项目管理员入口，可以描述 Agent_Skills 源仓库、Release、binary、Runtime、首次治理、升级/回退、自检和 Source Mode。
- `USAGE.md` 的前提是项目已经配置完成，不要求普通开发者知道或维护 Agent_Skills 本身，只提供面向桌面 AI Agent 的自然语言研发用法。
- 普通开发者写入型任务统一 `任务分支 → 实现/验证/开发侧复核 → PR Ready → 维护者审核`；USAGE 不提供普通开发者自行 merge main、Release、Deploy 或生产操作指引。
- 安装/首次接入等知识从 USAGE 移除前已经在 README 或更专门维护者事实源获得等价承载；没有为了隐藏而删除仍有效知识。
- 第一轮 CI 暴露的旧 USAGE 断言属于本次明确改变的人类文档 Contract。修复采用测试 Owner 迁移，不把旧内部说明重新塞回 USAGE；底层 Runtime/Release/Bootstrap 行为断言继续保留。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | README 承担 binary 安装、首次治理、状态/自检、升级/回退和网页 Source Mode 等维护/接入说明 | #227 / AC1 | satisfied | README 第 1、2、6–10、12–13 节；第二轮 492 项回归中 README/Bootstrap/平台 ZIP/Runtime 生命周期契约测试均通过 |
| R2 | USAGE 只面向已完成接入后的普通桌面 Agent 开发者，不暴露内部接入实现 | #227 / AC2 | satisfied | USAGE 首段明确前提；`test_end_user_has_one_release_usage_document` 与 `test_readme_owns_first_bootstrap_while_usage_starts_after_governance` 对内部主题做负向断言并通过 |
| R3 | USAGE 覆盖典型开发场景，普通开发者写入型任务统一止于 PR Ready | #227 / AC3 | satisfied | USAGE 第 2–10、14 节覆盖功能/Bug/重构/测试/Review/Figma/文档/版本/Git；多个示例明确“提交 PR 给维护者审核，不要合并主分支” |
| R4 | 不制造第二套工程规则，不改变现有 Runtime/Release/Bootstrap 产品语义，只迁移直接相关测试 Owner | #227 / AC4 | satisfied | PR diff 无 Runtime/Workflow/Router/Skill/Reference 实现修改；Run 34016915132 为 content scope，492 tests 0 failure，真实 ZIP/安装/路由/加密/Release/Bootstrap 回归继续通过 |

AC5 的最终 current-head required checks、guarded merge、implementation main-fresh、repository-native Change Archive、archive governance fresh、Issue 验收写回/关闭和分支清理属于后续平台交付门禁，不由 pre-merge Change 自行伪造为已完成。

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 实际证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Run 34016915132：Python 3.14.7；`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`，492 tests，0 failure，退出 0 |
| 接口 / 契约 | required | Runtime/Release/Bootstrap/Project Payload/路由/ZIP/导航原有回归仍通过；生产 Runtime、Workflow、Router/Skill/Reference 无 diff |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改业务运行时或持久化语义；底层安装与 stdio 生命周期现有测试仍作为回归执行 |
| 用户 / 工作流验收 | required | 从普通开发者角色反查功能、Bug、重构、测试、Review、Figma、文档、版本与 Git 场景；所有写入型示例统一到 PR Ready |
| 跨组件关键路径 | not_applicable | 无生产组件接线变化 |
| 外部依赖 / 供应方探测 | not_applicable | 不调用外部 Provider 或在线模型 |
| 构建 / 打包 / 运行 | not_applicable | CI classifier 判定 `content`；三平台 package Jobs 按正式策略 skipped，不以文档变化触发无关 binary build；真实 ZIP 组装测试仍在 492 项中通过 |
| 文档 / 治理 / 其他 | required | Markdown 导航、README/USAGE 受众、首次治理 Owner、Runtime 生命周期说明 Owner、平台 ZIP 说明 Owner 均有永久回归；两阶段人工语义复核无 blocker |

# 完成审计

- [x] upstream_re_read：Ready 前重新读取用户本轮要求和 live Issue #227；Issue 已补充“普通开发者写入型任务止于 PR Ready”以及测试 Owner 迁移边界，没有把当前 Change/PR 当需求全集。
- [x] change_coverage：维护者任务反查到 README；普通开发者日常任务反查到 USAGE；旧 USAGE 的安装/首次治理/平台 ZIP/Runtime 生命周期断言全部迁到 README 或更专门维护事实源，没有知识丢失。
- [x] reverse_audit：从 README 的安装、首次治理、状态、自检、升级回退、网页 Source Mode 反查维护者入口；从 USAGE 的功能、Bug、重构、测试、Review、Figma、文档、版本、Git 场景反查普通开发者入口；USAGE 不包含 Agent_Skills/Runtime/MCP/Source Mode/AGENTS/安装等内部主题。
- [x] unresolved_cleared：首轮 6 个 Red 中 1 个 README 导航缺陷和 5 个旧文档 Contract 断言已修复；第二轮 492 项全部 Green。当前 Runtime Package Gate 的唯一失败是 Change 尚未 Ready 的预期治理拒绝，本次更新后由 current-head required CI 重新验证。

# 两阶段复核

Review Target：PR #230；base `7b5389f7f76d1cc48a6734006bcc00bd7b5a6c4d`；已验证实现 head `21d6082168144cee9f97837442ffffc040c95625`。本次 Change Ready 更新只记录已取得证据和审计结果，不修改 README/USAGE/测试实现语义。

阶段 A（需求符合性）：从用户原始要求与 live Issue #227 独立重建完成定义。确认 README 承担维护/接入，USAGE 只面向已配置项目普通开发者，普通开发者不看到内部 Agent_Skills 接入信息，所有写入型用法止于 PR Ready。未发现上游要求遗漏。

阶段 B（实现/测试/文档质量）：复核 PR 全 diff 与第一、二轮 CI。四个测试文件只迁移人类文档断言 Owner，实际 Runtime 生命周期、Bootstrap、三平台 ZIP、Release/Project Payload/路由和导航责任保留；没有删除失败测试、降低断言或修改生产 Runtime/CI。README/USAGE 链接和受众职责清晰，普通 USAGE 无内部接入泄露，无剩余阻塞 Finding。本复核不是伪造另一名人工 Reviewer 的 GitHub approval。

# 验证

## Red

PR Draft Run 34016595070，head `66b8c4baa6448c715a98a424cf26d1cfd0d4aac4`：自包含 492 项中 6 项失败。1 项为 README 真实 Markdown 导航缺陷；其余 5 项为永久测试继续强制旧 USAGE 安装/首次治理/平台 ZIP/Runtime 生命周期说明。失败被保留为本次 Contract 迁移的 Red 证据，没有通过恢复旧内部说明造 Green。

## Green

PR Draft Run 34016915132，head `21d6082168144cee9f97837442ffffc040c95625`，PR checkout merge ref `c8a3c5494f27bf71aff0ee5378953722e1711015`：

- Requirement Source `#227` 验证通过。
- classifier：`content`；日志明确 `Runtime content changed; semantic Skill Tests are required and binary package evidence is not applicable.`
- Agent Skills Gate job `101442206683`：success。
- Python `3.14.7`。
- `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`：492 tests，0 failure，`OK`，退出 0。
- Markdown 导航、README/USAGE 新职责、首次治理 Owner、平台 ZIP 说明 Owner、Runtime 生命周期 Owner、Project Payload、Routing、Runtime 加密/安装、Release 等回归均通过。
- Windows/macOS package Jobs 因 content scope 正确 skipped；未用其他平台或更弱证据冒充 binary package 验证。
- Runtime Package Gate job `101442252637` 只因本 Change 当时仍为 `active`、Completion Audit 尚未完成而失败；这是仓库预期的最终治理门禁，不是实现/测试失败。本次 Ready 更新后必须在当前新 head 重新取得 required checks。

# 文档影响

本任务本身就是人类文档职责调整。README 现在是维护者/项目管理员的唯一接入管理入口；USAGE 是普通开发者的桌面 AI Agent 日常使用说明。没有需要同步的其他专业 Skill/Runtime 文档事实，因为运行机制没有变化；四个永久测试已同步新的文档 Owner，避免未来回归到旧职责。

# 交付

Requirement-Source: #227

当前状态：实现与开发侧验证已完成，Change 已进入 `ready_for_review`。PR 仍需在本 Change 更新后的 current head 通过 required checks，再执行 GitHub Review/Ready、guarded merge、main-fresh、原生 Change Archive、Issue Acceptance/Closure 与分支清理。