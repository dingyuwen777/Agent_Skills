---
schema: coding-change/v1
id: CHG-20260831-runtime-silent-control-plane
title: Runtime 用户可见进度隐藏内部治理控制面
level: L3
status: done
owner: dingyuwen777
branch: change/runtime-silent-control-plane
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - runtime-distribution
  - project-bootstrap
  - user-visible-disclosure
  - tests
affected_paths:
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/ENTRY.md
  - runtime/agent_skills_runtime/runtime.py
  - .agents/skills/coding/tests/test_runtime_progress_privacy.py
contracts:
  - runtime-user-visible-disclosure
data_changes: []
---

# 目标

强化 Runtime Mode 的用户可见信息披露边界：保留真实工程处理过程，但把 Skill 发现/选择/加载、Router 判断、Reference 解析/加载、Task Route、MCP required Context 加载等治理控制面变成静默内部过程，不再主动转写成用户可见进度。

# 成功标准

- [x] Runtime 安装到目标项目后的最早 managed 入口，在任何内部路由/上下文加载前就明确建立“控制面静默”规则。
- [x] progress update、commentary、tool preamble、intermediate summary、final response、error explanation 等所有 Agent 可控制的用户可见文本都受同一披露边界约束。
- [x] 明确禁止把“已读取/已加载/命中内部治理能力”“内部路由把任务分成……”“正在加载内部规则/约束”等控制面动作作为模型生成进度播报。
- [x] 继续允许展示项目调查、需求/风险判断、代码修改、测试、文档同步、Review、Git/CI、Release 与交付状态。
- [x] Runtime 共享入口明确后续规则中的选择、加载、输出和 Handoff 只属于内部控制面结果，不等于用户可见进度；Source Mode 维护者仍可正常查看和讨论这些事实。
- [x] 共享入口明确模型可控文本与宿主 UI 自动活动标签的边界，不宣称 Prompt/Skill/Runtime 能隐藏宿主自身 UI。
- [x] Project Payload、Runtime Bundle、MCP Tool Contract、Task Route、Routing Manifest、安装 ownership、动态 Skill Catalog、canonical Reference exact-text/hash 语义不变。
- [x] PR final head、功能合并后的 main 与三平台 Runtime Package Tests 均取得新鲜绿色证据。

# 实施方案与取舍

本 Change 最终采用“三层强化、单一语义”的最小方案：

1. **最早项目入口**：从读取 managed block 起、第一次用户可见进度更新前就建立控制面静默边界，并覆盖 progress/commentary/tool preamble/intermediate/final/error 等所有 Agent 可控文本。
2. **共享早期入口**：明确后续任何规则中的“输出/选择/加载/Handoff”在 Runtime Mode 只表示内部控制面结果，不能被模型转写成用户进度；同时保留 Source Mode 明文维护可见性并声明宿主 UI 边界。
3. **Runtime 公共进度提示**：每次公共 Runtime/MCP 返回继续携带用户可见进度规则，使长任务在后续工具调用后仍重复得到“真实工程过程可见、内部控制面静默”的约束。

没有修改 Router 正文或详细 Runtime canonical Reference。原因不是跳过 Requirement，而是避免把同一披露策略复制成多个 Owner：共享早期入口已经显式约束“后续任何规则”的选择/输出/加载/Handoff；现有详细 Runtime Reference 本身已经正确区分 Source Mode 与 Runtime Mode，并继续作为模式感知披露的详细事实源。回归测试同时检查该既有边界未被削弱。

# 非目标

- 不改为 AGENTS + MCP 单入口架构。
- 不移除 Runtime Project Payload 中的 Entry、Router 或专业 Skill Core。
- 除公共“用户可见进度规则”文本外，不修改 Runtime 执行逻辑；不修改 MCP Tool Contract、Task Route schema、Routing Manifest、Bundle 加密、Stable ID、source/routing/payload digest 或安装 manifest。
- 不隐藏目标项目自己的代码、测试、文档、配置、Git/CI 路径或真实工程过程。
- 不承诺隐藏 Codex/Cursor/Claude 等宿主 UI 自身自动生成的 Skill/Tool activity label、调用事件或 trace；本 Change 只约束 Agent/Prompt/Skill/Runtime 能控制的用户可见文本。
- 不新增依赖、Schema、Migration、外部 Provider 或新的分发产品面。

# 必须保持不变

- Source Mode 维护者可以正常查看和讨论 Skill、Reference、路径、Stable ID、路由和加载事实。
- Runtime Mode 仍使用当前 Shared Entry + Native Router/专业 Core + Project-local MCP Runtime + Encrypted Canonical References 架构。
- 完整 canonical Context 不因用户可见保密而删改正文、routing metadata、Stable ID 或原始字节。
- 项目事实优先、required Context fail-closed、权限边界、Change/Review/CI/PR/Release 门禁保持不变。
- 用户可见过程仍可以解释真实工程步骤本身的原因和验证证据。
- 既有 Runtime 公共进度提示的稳定语义（包括“用户可见进度”“不得主动复述”）继续兼容，不能为了新措辞删除旧 contract 断言。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Runtime 用户可见过程不再主动播报 Skill 名称、文件/目录或内部路由/加载明细 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | satisfied | 最早 managed 入口覆盖所有 Agent 可控用户文本并使用泛化禁止示例；共享入口约束后续控制面；Runtime 公共进度提示在每次 MCP 返回持续强化。目标回归、真实 MCP 和三平台安装均通过。 |
| R2 | 控制面静默规则必须在第一次用户可见进度更新前生效 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | satisfied | managed block 明确“从读取起立即生效、第一次用户可见进度更新之前应用”；测试从真实 Project Payload 读取该 managed 资产，结合既有安装回归和三平台安装证明其进入目标项目 Bootstrap 链。 |
| R3 | Router 的内部选择/Handoff 不得被解释成用户可见进度 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | satisfied | 共享早期入口明确 Skill 发现/选择/加载、Router 判断、required Context 与 Handoff 只服务内部执行，并声明后续任何规则中的“输出/选择/加载/Handoff”只表示内部控制面结果、不得转写成用户进度。 |
| R4 | 真实工程调查、修改、测试、文档、Review、Git/CI/Release/交付过程继续可见 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | satisfied | managed block 与 Runtime 公共进度提示显式保留这些工程活动；目标测试逐项断言允许面。 |
| R5 | Source Mode 可讨论内部事实，且不宣称能隐藏宿主 UI 自动活动标签 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | satisfied | 共享入口明确 Source Mode 可讨论内部导航/路由事实，并声明宿主 UI 自动 activity label / trace 不受 Prompt/Skill/Runtime 文本直接控制、不能宣称隐藏；既有双模式披露回归继续通过。 |
| R6 | Runtime/Project Payload/MCP/Bundle/安装语义不变 | https://github.com/dingyuwen777/Agent_Skills/issues/100 | satisfied | PR final head `bef3008f940da1c94ccb7260027a0bb35281fcba` 的 Skill Tests #636 与 Runtime Package Tests #59 全部成功；功能 merge commit `4e154fad79797c873993c862a10e417bdced486a` 的 main Skill Tests #637 与 Runtime Package Tests #60 也全部成功。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / 完成证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red：Skill Tests #627（run `33362757712`，head `5a26658958ec5a336b8478078c38fa7e5d218d3a`）共 252 tests，精确只有新增的 6 个目标测试因旧规则缺少最早生效/全渠道/Entry/宿主边界等语义失败；旧回归全部通过。Final Green：Skill Tests #636（run `33364152186`）compile、CLI smoke、全部 self-contained tests 与 changed Change Ready gate 成功。 |
| 接口 / Contract | required | 公共 Runtime 字段/Tool schema 未变；Green 过程中旧测试与真实 stdio smoke 分别暴露稳定短语“用户可见进度”和“不得主动复述”必须保留，均通过恢复旧字面 contract + 叠加新语义修复，没有删除或放宽旧断言。 |
| 集成 / Persistence / Runtime Dependency | required | 不改持久化或外部依赖，但变更 Runtime 公共提示与 Project Payload，因此 PR final head 和 main 都执行真实三平台 Runtime Package Tests并全绿。 |
| 用户 / Workflow Acceptance | required | 测试同时断言禁止内部治理播报和允许项目调查、风险判断、代码、测试、文档、Review、Git/CI、Release、交付等工程进度；失败时使用泛化治理不可用表达。 |
| 跨组件 Golden Path | required | managed 规则 → Project Payload → 项目 Bootstrap；Entry → 后续内部选择/Handoff；Runtime status/route/start 等公共返回 → 用户可见进度规则，均有 self-contained preservation/behavior、真实 stdio 与安装证据。 |
| 外部依赖 Probe | not_applicable | 不依赖第三方 Provider 或网络现时数据。 |
| Build / Package / Runtime | required | PR Runtime Package Tests #59（run `33364152158`）和 main Runtime Package Tests #60（run `33364338029`）均在 Linux、Windows、macOS 完成 build/self-test → real stdio MCP → project-only single-binary installation。 |
| Docs / Governance / Other | required | 重新读取 Issue #100；检查既有模式边界、旧披露回归和 stdio smoke；Change 与实际实现范围同步。最终用户操作步骤未变化，因此不做无关用户手册修改。 |

# Review

Review Target：PR #101，base `6a7c593749d9d85d1c074b85d42b24c9814ff545`，最终 PR head `bef3008f940da1c94ccb7260027a0bb35281fcba`。

模式：独立需求符合性 + 测试充分性 + 实现质量 Review；用户明确授权修复并合并到主分支。

独立风险重建重点：

- 保密规则是否太晚，第一次进度仍可泄露；
- 后续 Router/Handoff 是否会覆盖早期边界；
- 为“禁止泄露”是否反而把内部术语写进目标项目根入口；
- 是否误伤正常工程进度；
- 是否破坏旧 Runtime 公共文本 contract、真实 stdio MCP 或三平台安装；
- 是否错误宣称能控制宿主 UI；
- 是否为了本需求改成更重的单入口架构或降低现有门禁。

审查结果：`NO_FINDINGS_WITHIN_SCOPE`。最终 diff 只强化最早披露边界、共享入口和 Runtime 公共进度提示，并增加对应测试；没有协议/schema/dependency/安装 ownership 变化。旧披露测试阻止了把内部导航直接塞入目标项目 managed block；两次兼容失败又分别阻止删除旧“用户可见进度”和“不得主动复述”稳定语义，修复后旧回归、PR final-head 和 main 三平台真实链全部通过。

测试充分性结论：当前仓库能证明约束已进入 Project Payload、公共 Runtime 响应、真实 stdio MCP 与三平台安装，并且旧合同未回退；不能用确定性测试证明任意 LLM 在所有宿主上绝不违反自然语言约束，也不能证明宿主 UI 自身不会显示自动 Skill/Tool activity。两者属于明确产品/模型边界，不是本实现伪装成已解决的事项。

当前无 BLOCKER/HIGH/MEDIUM Finding。

# Completion Audit

- [x] upstream_re_read：完成前重新读取 Issue #100、当前披露实现、既有详细模式边界、旧披露测试与真实 stdio smoke contract；未把 PR 描述或历史讨论当作需求全集。
- [x] change_coverage：R1–R6 均有明确实现落点与 PR/main 新鲜证据；没有为了满足 checklist 修改不必要的 Router/Reference/用户手册。
- [x] reverse_audit：从用户可见 progress/commentary/tool preamble/intermediate/final/error 反向追踪到最早 managed 入口 → 共享 Entry 对后续 Router/Handoff 的内部化约束 → Runtime 每次 MCP 返回持续强化 → Project Payload/stdio/install 验证，未发现可由本仓库规则控制但未覆盖的披露缺口。
- [x] unresolved_cleared：Requirement Traceability 全部 `satisfied`；无 TBD/TODO/not_satisfied。剩余边界仅为 LLM 指令遵循概率和宿主 UI 自身展示，均已明确写入非目标与 Review 结论。

# 任务

- [x] 恢复当前仓库事实与适用维护/研发/披露规则。
- [x] 创建 Requirement Source Issue #100 与 L3 Change。
- [x] 新增 Runtime 进度披露目标测试并取得干净 Red（Skill Tests #627）。
- [x] 最小强化最早入口、共享入口和 Runtime 公共进度规则，并完成旧 contract 兼容修复。
- [x] PR final-head Skill Tests #636 与 Runtime Package Tests #59 全绿。
- [x] 独立 Requirement Review、测试充分性 Review、内容守恒/安全边界 Review 无阻塞 Finding。
- [x] PR #101 使用 expected head guard 合并到 main，merge commit 为 `4e154fad79797c873993c862a10e417bdced486a`。
- [x] main Skill Tests #637（run `33364337983`）成功。
- [x] main Runtime Package Tests #60（run `33364338029`）三平台全部成功。
- [x] 满足归档前置条件，进入独立 Change archive PR。

# 文档影响

本 Change 修改的是 Runtime/Agent 治理行为和安装到目标项目的早期入口，不改变最终用户安装、升级、命令或 Release 下载步骤，因此用户手册无需更新。现有详细 Runtime 分发规范原本已经具备 Source/Runtime 双模式信息披露边界，本 Change 通过早期入口和公共提示把该原则前移并持续强化，没有复制第二套详细规则。

# Git / PR / 发布状态

- Requirement Source：Issue #100。
- 功能分支：`change/runtime-silent-control-plane`。
- 功能 PR：#101，已合并。
- 功能 merge commit：`4e154fad79797c873993c862a10e417bdced486a`。
- main 新鲜验证：Skill Tests #637 与 Runtime Package Tests #60 均成功。
- Release：本 Change 不创建新版本；实现将在下一次正常 Release 中进入 Project Payload/Runtime。
- Change 状态：`done`，由独立归档 PR 移出 active 并保存本记录。
