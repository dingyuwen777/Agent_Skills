---
schema: coding-change/v1
id: CHG-20260831-requirement-pr-traceability
title: 固化需求来源、Issue 与 PR 可追溯协作门禁
level: L2
status: in_progress
owner: dingyuwen777
branch: change/requirement-pr-traceability
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - requirement-traceability
  - pull-request-review
  - multi-developer-collaboration
  - tests
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
  - .agents/skills/coding/tests/test_reference_numbering.py
contracts: []
data_changes: []
---

# 目标

把多人协作场景中的“正式需求来源 → GitHub Issue/其他正式载体 → Change/施工契约 → PR → Agent Review → 合并”固化成通用、可执行、可验证的 Agent Skills 规则，使开发 Agent 能主动解析或建立可追溯 Requirement Source，Review Agent 能在不猜需求的前提下独立恢复上游事实，并把审查结论绑定到明确的 base/head revision。

# 成功标准

- [ ] L2/L3 进入 PR 前必须解析可持久、团队可访问的 Requirement Source；项目已有 OpenSpec/RFC/ADR/Spec/Issue 等正式载体时优先复用，不平行造制度。
- [ ] GitHub 项目在没有更强正式载体、且项目治理允许 Issue 作为需求索引时，可在已有 GitHub 写授权下先搜索等价 Issue，再创建最小 Issue；多个候选有实质歧义时禁止静默误关联。
- [ ] PR 使用稳定的 `Requirement-Source:` 追溯字段；`Closes/Fixes/Resolves` 只表达“合并后整个 Issue 完成”，不得拿来替代一般需求追溯，多 PR 分拆时不得提前关闭 Issue。
- [ ] PR 创建或更新后重新读取 PR 与 Requirement Source，确认引用真实存在、可访问且与当前实现范围一致；宿主无权限时明确降级，不伪造关联成功。
- [ ] PR Review 将需求来源状态区分为 `resolved / partial / unavailable`；`partial/unavailable` 时可以继续代码质量 Review，但不得声明整体需求符合或可合并。
- [ ] Review 绑定 `reviewed_base_sha + reviewed_head_sha`；base 或 head 漂移后必须针对当前目标分支状态重新做相应集成验证，并按风险 re-review，不能只因 PR head 未变沿用旧集成结论。
- [ ] 不强制所有项目使用 rebase；以目标仓库 Branch Protection/Ruleset、up-to-date check、merge queue 或等价 merge-result validation 为实际集成机制。
- [ ] CI 只适合强制 `Requirement-Source` 结构、来源存在性和最小结构；自然语言需求完整性与“PR 是否真正实现需求”继续由 Agent Review 语义审查负责。
- [ ] Source Mode 与 Runtime Mode 都能在“代码审查 / Git 交付 / PR Ready / 多人协作”任务中自动加载本规则，无需用户知道内部 Reference 名称。
- [ ] 不修改 Runtime evaluator、MCP、Bundle 协议、Project Payload 或既有 Stable Reference ID；新增 Reference 通过动态 Catalog 自动进入现有分发链。

# 范围

- 新增一个 Coding canonical Reference，唯一承载 Requirement Source Resolution、GitHub Issue 索引、PR traceability、Review revision snapshot 与 merge-time freshness 的详细规则。
- 新增 self-contained preservation/routing 回归测试。
- 更新 Coding Reference 连续编号测试以接纳新增第 17 个文件，同时保持既有 Stable ID 不变。

# 非目标

- 不为所有目标项目自动安装 `.github/pull_request_template.md`、Issue Form、CODEOWNERS、Branch Protection、Ruleset 或 CI Workflow。
- 不规定所有项目必须使用 GitHub Issue；项目已有正式需求治理时继续以项目事实为准。
- 不把 Coding Change 自身升级成上游 Requirement Source。
- 不修改 Review Findings 严重度模型、Change schema、Runtime 路由协议或 GitHub API 实现。
- 不把具体业务项目、AIMA、Figma 页面、业务字段或具体 Issue 编号写入通用 Skill。

# 必须保持不变

- 当前 Change 仍是施工契约而不是自身需求全集；Requirement Traceability 继续服从现有 Completion Gate。
- 只读 Review 不自动获得 Issue/PR 写权限；创建 Issue、修改 PR、merge 等外部动作仍受用户与宿主授权约束。
- GitHub 只是托管平台 profile；非 GitHub 项目使用等价 issue/ticket/MR/revision 语义，不被强行改造成 GitHub 流程。
- Branch Protection/Ruleset/required checks 由目标仓库负责强制；Agent Skills 负责读取、检查和按规则停机，不冒充平台强制能力。
- 现有 `coding.reference.15` 的 REST merge + `expected_head_sha`、main fresh CI 和零人工 PR 策略保持不变。

# 关键决策

新增单一 Coding Reference，而不是新增 `pr-review` Skill，也不把同一套 Issue/PR 规则复制到 Review、多人协作和 Git 三处。该 Reference 通过现有路由信号 `代码审查`、`PR Ready`、`Git 交付`、`多人协作` 自动命中；Review Skill 继续负责独立审查方法，Git Reference 继续负责通用 merge/交付动作，目标项目 Overlay 继续负责是否采用 GitHub Issue、PR Template、Required Check 与 Branch Protection。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 多人开发 PR 必须能够追溯到明确需求，Agent Review 不能从代码反推需求 | user:current-request | not_satisfied | 待新增 canonical Reference 与回归测试。 |
| R2 | GitHub 场景下 Agent 能自动寻找/在授权下创建 Issue，并在 PR 中建立稳定需求关联 | user:current-request | not_satisfied | 待新增 Requirement Source Resolution 与 `Requirement-Source:` 规则。 |
| R3 | `Requirement-Source` 与 `Closes/Fixes/Resolves` 语义必须分离，支持一个 Issue 拆多个 PR | user:current-request | not_satisfied | 待新增 PR traceability 规则。 |
| R4 | PR Review 必须绑定 base/head revision；main 推进后重新验证当前集成状态 | user:current-request | not_satisfied | 待新增 reviewed base/head snapshot 与漂移处理规则。 |
| R5 | 需求缺失时仍可做代码质量 Review，但不得给需求符合或可合并结论 | user:current-request | not_satisfied | 待新增 `resolved/partial/unavailable` fail-closed 结论边界。 |
| R6 | 不把 GitHub Issue/Ruleset 强加给所有项目，不修改 Runtime 协议或既有 Stable ID | AGENTS.md + .agents/MAINTENANCE.md | not_satisfied | 待完成项目中立性、动态 Catalog 与内容守恒 Review。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 新增 `test_pr_requirement_traceability.py`，覆盖规则正文与 canonical routing。 |
| 接口 / 契约 | required | `agent-routing:v1` metadata、Stable Reference ID、依赖和现有 Runtime compile/evaluate 必须继续可解析。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改外部数据库、服务或 Runtime 进程。 |
| 用户 / 工作流验收 | required | 从“自然语言开发/审查 PR”反向验证自动命中规则以及需求缺失 fail-closed 输出边界。 |
| 跨组件关键路径 | required | canonical Reference → dynamic routing → Bundle/Runtime 现有测试链由 Skill Tests 验证。 |
| 外部依赖 / 供应方探测 | not_applicable | 规则本身不需要调用真实第三方服务；GitHub 外部动作只定义权限和验证责任。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release 路径，不触发三平台 package workflow。 |
| 文档 / 治理 / 其他 | required | changed Change gate、Reference numbering、Markdown/routing/content preservation 与独立 Review。 |

# 完成审计

- [ ] upstream_re_read：重新读取本轮用户确认结果、AGENTS、Maintenance、Router、Coding、Mutation、多人协作、Completion、Git 与 Review 当前规则。
- [ ] change_coverage：R1–R6 全部进入 canonical Owner，且没有把项目特定治理强加为全局默认。
- [ ] reverse_audit：开发需求 → Requirement Source → Issue/正式载体 → Change → PR；PR Review → source → base/head → diff/tests → merge freshness；两条链均可达。
- [ ] unresolved_cleared：无 `not_satisfied`，required Validation Matrix 均有本轮新鲜证据。

# 任务

- [x] 读取当前 main、AGENTS、Maintenance、Router、Coding、Mutation、Review、多人协作与 Git 规则，确认当前没有活动 Change。
- [x] 确认 main `73efb8b98663e21836a0b8f76008eb8994cab903` 的 Skill Tests run `33324142068` 成功。
- [ ] 先新增会因目标 Reference 尚不存在而失败的 self-contained 回归测试，取得 Red 证据。
- [ ] 新增 `17_需求来源与PR追溯治理.md`，保持单一 Owner 和项目中立。
- [ ] 更新 Reference numbering 测试，不改变现有 Stable ID。
- [ ] 运行 PR Skill Tests 取得 Green，并完成 A1/A2、内容守恒、路由和 Review 复核。
- [ ] 合并实现 PR，确认 main fresh CI。
- [ ] 将本 Change 更新为 `done` 并归档到 `archive/2026-08/`，通过独立归档 PR 完成交付。

# 验证

## 计划

- Red：新增 `test_pr_requirement_traceability.py` 后，在规则文件尚不存在时运行 Skill Tests，预期 self-contained tests 因缺少 canonical Reference/route 而失败。
- Green：实现 Reference + numbering 更新后，PR Skill Tests 必须完整成功。
- Review：核对 Requirement Source/Issue/PR 语义、权限边界、`resolved/partial/unavailable`、base/head snapshot、up-to-date/merge queue 机制中立性和 Runtime 动态发现。
- main：实现合并后读取确切 main SHA，并确认对应 fresh Skill Tests 成功。
- archive：仅治理文件归档，使用独立 PR 和真实 changed-scope CI。

## 新鲜证据

- 基线：main `73efb8b98663e21836a0b8f76008eb8994cab903`，Skill Tests run `33324142068`，conclusion=`success`。

# 文档影响

本次规则变化属于 Agent/治理能力，canonical Owner 为 Coding Reference；不需要新增人类 README。若最终用户说明因实际使用入口发生变化再更新 `USAGE.md`，但当前自然语言 Code Review 入口已经存在，因此本 Change 不为重复示例扩大文档范围。

# Git / PR 状态

- branch: `change/requirement-pr-traceability`
- baseline main: `73efb8b98663e21836a0b8f76008eb8994cab903`
- PR: 待创建
- merge: 未执行
- main fresh CI: 未执行
- archive: 未执行
