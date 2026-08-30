---
schema: coding-change/v1
id: CHG-20260831-requirement-pr-traceability
title: 固化需求来源、Issue 与 PR 可追溯协作门禁
level: L2
status: done
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

- [x] L2/L3 进入 PR 前必须解析可持久、团队可访问的 Requirement Source；项目已有 OpenSpec/RFC/ADR/Spec/Issue 等正式载体时优先复用，不平行造制度。
- [x] GitHub 项目在没有更强正式载体、且项目治理允许 Issue 作为需求索引时，可在已有 GitHub 写授权下先搜索等价 Issue，再创建最小 Issue；多个候选有实质歧义时禁止静默误关联。
- [x] PR 使用稳定的 `Requirement-Source:` 追溯字段；已有更强正式载体时直接引用项目既有稳定标识，不为建立追溯重复创建 Issue。
- [x] `Closes/Fixes/Resolves` 只表达“合并后整个 Issue 完成”，不得拿来替代一般需求追溯，多 PR 分拆时不得提前关闭 Issue。
- [x] PR 创建或更新后重新读取 PR 与 Requirement Source，确认引用真实存在、可访问且与当前实现范围一致；宿主无权限时明确降级，不伪造关联成功。
- [x] PR Review 将需求来源状态区分为 `resolved / partial / unavailable`；`partial/unavailable` 时可以继续代码质量 Review，但不得声明整体需求符合或可合并。
- [x] Review 绑定 `reviewed_base_sha + reviewed_head_sha`；base 或 head 漂移后必须针对当前目标分支状态重新做相应集成验证，并按风险 re-review，不能只因 PR head 未变沿用旧集成结论。
- [x] 不强制所有项目使用 rebase；以目标仓库 Branch Protection/Ruleset、up-to-date check、merge queue 或等价 merge-result validation 为实际集成机制。
- [x] CI 只适合强制 `Requirement-Source` 结构、来源存在性和最小结构；自然语言需求完整性与“PR 是否真正实现需求”继续由 Agent Review 语义审查负责。
- [x] Source Mode 与 Runtime Mode 都能在“代码审查 / Git 交付 / 多人协作”任务中自动加载本规则，无需用户知道内部 Reference 名称；`PR Ready` 与 `Git 交付` 共用同一 Reference trigger。
- [x] 不修改 Runtime evaluator、MCP、Bundle 协议、Project Payload 或既有 Stable Reference ID；新增 Reference 通过动态 Catalog 自动进入现有分发链。

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

新增单一 Coding Reference，而不是新增 `pr-review` Skill，也不把同一套 Issue/PR 规则复制到 Review、多人协作和 Git 三处。该 Reference 通过现有路由信号 `代码审查`、`PR Ready`、`Git 交付`、`多人协作` 自动命中；Review Skill 继续负责独立审查方法，Git Reference 继续负责通用 merge/交付动作，目标项目 Overlay 继续负责使用哪种正式需求载体、是否采用 GitHub Issue、PR Template、Required Check 与 Branch Protection。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 多人开发 PR 必须能够追溯到明确需求，Agent Review 不能从代码反推需求 | user:current-request | satisfied | `17_需求来源与PR追溯治理.md` 第 1/5/6 节建立上游来源、PR 快照与 fail-closed 规则；路由/正文回归进入 `test_pr_requirement_traceability.py`；Requirement Issue #79 与实现 PR #76 已形成实际闭环。 |
| R2 | GitHub 场景下 Agent 能自动寻找/在授权下创建 Issue，并在 PR 中建立稳定需求关联 | user:current-request | satisfied | 新 Reference 第 2/3 节规定“先搜索→唯一匹配复用→有歧义不静默选择→无匹配且有写授权才创建 Issue→PR 写 `Requirement-Source:`”；本 Change 在合并前实际搜索后创建 Issue #79 并关联 PR #76。 |
| R3 | `Requirement-Source` 与 `Closes/Fixes/Resolves` 语义必须分离，支持一个 Issue 拆多个 PR | user:current-request | satisfied | 新 Reference 第 3 节明确两种语义；PR #76 同时使用 `Requirement-Source: #79` 与 `Closes #79`，合并后 Issue #79 自动以 `completed` 关闭。 |
| R4 | PR Review 必须绑定 base/head revision；main 推进后重新验证当前集成状态 | user:current-request | satisfied | 新 Reference 第 5/7/8 节定义 revision snapshot/fresh validation；实现期间 main 两次推进，均检查无重叠、重新同步、重跑 CI；final review `5061508562` 绑定 base `4ffaef032106d54deadbd8e36ea7a159c15b1647` / head `2772c7f6ffb0e3f818e0967bf97606b61ee5c4bc`。 |
| R5 | 需求缺失时仍可做代码质量 Review，但不得给需求符合或可合并结论 | user:current-request | satisfied | 新 Reference 第 6 节定义 `resolved / partial / unavailable`，后两者允许有边界的代码质量 Review，但禁止整体需求符合/可合并结论；preservation 回归覆盖。 |
| R6 | 不把 GitHub Issue/Ruleset 强加给所有项目，不修改 Runtime 协议或既有 Stable ID | AGENTS.md | satisfied | `.agents/MAINTENANCE.md` 与新 Reference 第 2/3/4/7/10 节保持项目治理/平台等价机制优先；实现 diff 没有 Runtime/MCP/Bundle/Project Payload/依赖修改，既有 Stable ID 映射未改。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 首轮 Red `33325561885` 证明缺少规则时失败；首轮 Green `33325680763` 证明主体行为测试通过；二轮 Red `33326026571` 精确暴露“正式非 Issue 来源无默认追溯表达”缺口；二轮 Green `33326141862` 全部 self-contained tests 成功；final-base PR run `33326489339` 与 merge 后 main run `33326556157` 均全绿。 |
| 接口 / 契约 | required | PR final-base run `33326489339` 及 main run `33326556157` 的 compile、CLI smoke、self-contained tests、Change gate 均成功，证明 `agent-routing:v1`、Stable ID、dynamic compile/evaluate 与 Bundle 既有回归未被破坏。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改外部数据库、服务或 Runtime 进程。 |
| 用户 / 工作流验收 | required | `test_pr_requirement_traceability.py` 验证代码审查、Git 交付、多人协作自动加载 `coding.reference.18`，并验证 GitHub Issue 与正式非 Issue 载体两种追溯路径；实际 Issue #79 → PR #76 → Review → merge 链已运行。 |
| 跨组件关键路径 | required | PR final-base 和 main fresh Skill Tests 均成功，包括动态 Routing/Bundle/Project Payload 既有回归；本次未改 Runtime 实现。 |
| 外部依赖 / 供应方探测 | not_applicable | 规则本身不需要第三方 Probe；GitHub Issue/PR 动作用当前授权 GitHub 能力执行并回读验证。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release 路径；按 Maintenance 不触发三平台 Runtime Package Tests。 |
| 文档 / 治理 / 其他 | required | Change、canonical Reference、PR traceability 回归与 Reference numbering 均在 Skill Tests 覆盖；实现 PR #76、final review、Issue #79 关闭、merge commit 与 main fresh CI 均有 GitHub 新鲜证据。 |

# 完成审计

- [x] upstream_re_read：实现与每次 final review 前均重新读取当前目标分支 AGENTS、Maintenance、Router、Coding/Mutation/Review 及相关 References；Requirement Source 在规则落地后实际持久化为 Issue #79 并回读。
- [x] change_coverage：R1–R6 全部进入单一 canonical Owner；Issue 自动搜索/创建、正式非 Issue 来源直接追溯、关闭语义、需求状态、revision snapshot、base/head freshness 和机器/语义门禁分工均已覆盖。
- [x] reverse_audit：开发需求 → Requirement Source → Issue/正式载体 → Change → PR；PR Review → Requirement Source → base/head → diff/tests → current-base fresh validation → merge → main fresh CI，两条链均已实际闭合；Review/Git 细节仍回到既有 Owner。
- [x] unresolved_cleared：R1–R6 无 `not_satisfied`；所有 required Validation Matrix 项均有 Red/Green、final-base CI、Review、merge 与 main fresh CI 证据。

# 任务

- [x] 读取当前 main、AGENTS、Maintenance、Router、Coding、Mutation、Review、多人协作与 Git 规则，确认初始没有活动 Change。
- [x] 确认初始 main `73efb8b98663e21836a0b8f76008eb8994cab903` 的 Skill Tests run `33324142068` 成功。
- [x] 首轮 TDD：run `33325561885` 取得 Red；实现主体规则后 run `33325680763` 的 compile/CLI/self-contained tests 转绿。
- [x] 修正 Ready Check 发现的 Requirement Source 路径格式问题，不降低 Completion Gate；run `33325966892` 完整成功。
- [x] final re-review 发现正式非 Issue 载体追溯缺口，新增回归后 run `33326026571` 以 212 tests 中唯一 1 个目标失败取得第二轮 Red。
- [x] 最小修正规则，使 `Requirement-Source` 接受项目正式稳定标识并明确不重复创建 Issue；run `33326141862` 完整成功。
- [x] main 两次推进后均重新同步/复验；final exact head `2772c7f6ffb0e3f818e0967bf97606b61ee5c4bc` 对 base `4ffaef032106d54deadbd8e36ea7a159c15b1647` 的 Skill Tests run `33326489339` 全绿，review `5061508562` 无 BLOCKER/HIGH/MEDIUM。
- [x] PR #76 以 `expected_head_sha=2772c7f6ffb0e3f818e0967bf97606b61ee5c4bc` REST merge；merge commit `33f577136c8e52fc4c8ef313a975c5719a2f6172`。
- [x] merge 后 main 精确指向 `33f577136c8e52fc4c8ef313a975c5719a2f6172`，fresh Skill Tests run `33326556157` 全绿；Issue #79 由 `Closes #79` 自动关闭为 `completed`。
- [ ] 独立 archive PR fresh CI / Review / merge / post-archive main fresh CI。

# 验证

## 新鲜证据

- 基线：main `73efb8b98663e21836a0b8f76008eb8994cab903`，Skill Tests run `33324142068`，conclusion=`success`。
- 首轮 Red：PR #76 run `33325561885`，head `725afb905d1d80e5fea8311c948f572eeff2781e`；compile/CLI smoke 成功，self-contained tests 因目标 canonical Reference 尚不存在而失败。
- 首轮 Green 行为：run `33325680763`，head `a9685091b98301d91c86d6ead4c2cf02594a4a8e`；compile、CLI smoke、self-contained tests 成功；当时 changed Change gate 仍因 Change 未 Ready 正确失败。
- Ready 格式诊断：run `33325872632`，head `abf1cc8ad89a82fa2afe3e4377a1ce597036b9cd`；211 tests 全通过，changed Change gate 唯一错误为组合 Source 路径不存在；修正为真实 `AGENTS.md` 后 run `33325966892` 在 head `cbe5deaaa0431bcd75c6b9a05f3effeed6c72778` 完整成功。
- 第二轮 Red：run `33326026571`，head `b2b795cfc7bfa3bb7245b4e0f8bff7c53dd60907`；compile/CLI smoke 成功，212 tests 中唯一失败是“已有 Spec/OpenSpec 等正式载体时应能直接追溯稳定标识而不是被迫新建 Issue”。
- 第二轮 Green：run `33326141862`，head `0f7f00d458a69ce1f0d0af037597aaef84fe2c52`；compile、CLI smoke、全部 self-contained tests、changed Change gate 全部成功。
- 证据 head：run `33326216018` 在 `2c0779063b79c740ab460f841bfb882d7d90ed62` 全绿。
- 第一次 base 漂移：main 到 `41b4632bbc722fb141ae56cebbe8e49be0303f74` 后重新集成，run `33326347139` 在 head `8fdb73ec7c24e96fcbdc8fd8b2b30d61739bd5a4` 全绿。
- 第二次 base 漂移：main 到 `4ffaef032106d54deadbd8e36ea7a159c15b1647` 后重新集成；compare 仅本 Change 4 个预期文件；run `33326489339` 在 final head `2772c7f6ffb0e3f818e0967bf97606b61ee5c4bc` 全绿；review `5061508562` 绑定该 exact base/head，Requirement Source #79=`resolved`，无未解决 BLOCKER/HIGH/MEDIUM。
- 实现 merge：PR #76 于 merge commit `33f577136c8e52fc4c8ef313a975c5719a2f6172` 合入；GitHub 回读确认 PR merged=true；Issue #79 closed/completed。
- main fresh：merge commit `33f577136c8e52fc4c8ef313a975c5719a2f6172` 的 push Skill Tests run `33326556157` 完整成功；compile、CLI smoke、self-contained tests、active Change gate 均 success。
- 规则质量复核：最终生产范围仅新 Reference、新回归与 Reference 数量更新；无 Runtime 修改、无依赖变化、无无关重构。正式 Issue 与非 Issue 两类需求来源、权限边界、`resolved/partial/unavailable`、base/head snapshot、current-base freshness、Required Status Check 与 merge queue 机制中立性均已反向核对。

# 文档影响

本次规则变化属于 Agent/治理能力，canonical Owner 为 Coding Reference；不需要新增人类 README。`USAGE.md` 已经允许用户直接用自然语言发起 Code Review，本次不要求用户记忆内部 Reference、route JSON 或新命令，因此不重复扩写最终用户说明。

# Git / PR 状态

- requirement: Issue #79，closed/completed
- implementation branch: `change/requirement-pr-traceability`
- baseline main: `73efb8b98663e21836a0b8f76008eb8994cab903`
- final reviewed base: `4ffaef032106d54deadbd8e36ea7a159c15b1647`
- final reviewed head: `2772c7f6ffb0e3f818e0967bf97606b61ee5c4bc`
- final review: `5061508562`
- PR: #76，merged
- merge commit: `33f577136c8e52fc4c8ef313a975c5719a2f6172`
- main fresh CI: run `33326556157`，success
- archive branch: `archive/requirement-pr-traceability`
- archive PR / merge / post-archive main CI: pending
