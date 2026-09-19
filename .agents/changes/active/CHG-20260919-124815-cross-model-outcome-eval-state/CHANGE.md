---
schema: coding-change/v1
id: CHG-20260919-124815-cross-model-outcome-eval-state
title: 提升跨模型一致性、真实效果评测与长任务连续性
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/cross-model-outcome-eval-state
created: 2026-09-19
updated: 2026-09-19
completion_gate: required
depends_on: []
affected_areas:
  - skill-governance
  - runtime-mcp
  - agent-outcome-eval
  - figma-progressive-disclosure
  - multi-agent-collaboration
  - ci-validation
affected_paths:
  - .agents/MAINTENANCE.md
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/28_SkillMutation影响面一致性审计.md
  - .agents/skills/figma/SKILL.md
  - .agents/skills/figma/references/
  - runtime/agent_skills_runtime/runtime.py
  - runtime/agent_skills_runtime/server.py
  - runtime/README.md
  - scripts/agent_outcome_eval.py
  - evals/
  - .agents/skills/coding/tests/
  - .github/scripts/runtime_package_scope.py
  - README.md
  - USAGE.md
contracts:
  - Agent Skills MCP工具契约/v4
  - Agent Skills 任务状态/v1
  - Agent Skills Outcome Eval/v1
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 Agent_Skills 已能稳定约束路由、治理和交付，但还缺少跨模型统一的真实任务效果评测、可恢复长任务语义状态；Figma Core 已膨胀到不利于渐进披露的规模。
- **拟议修改**：保持现有 Router/Coding/Testing/Review/Docs/Figma Owner，不增加 Planner/Research/SEP-2640；新增 model-neutral Outcome Eval/Trace Contract，扩展现有六 Tool 的 Task State，按内容守恒把 Figma Core 详细规则迁入按需 References，并增加跨模型一致性、Rule Effectiveness 与 Delegation Contract。
- **预期结果**：GPT、DeepSeek、GLM 或其他模型可以采用不同推理方式，但同一任务必须使用同一治理 Contract，并可用同一 Eval Suite 比较效果；长任务可以显式恢复关键状态；Figma 等专业规则按需加载且不损失细节。

# 背景、现状与问题

## 背景

Requirement Source 为 #266。维护者明确要求全面系统修改 Agent_Skills，使不同能力模型对同一治理体系的最终使用效果保持一致，同时保持渐进式披露，并明确排除 SEP-2640 Compatibility 与通用 Research/Analysis Skill。

## 当前现状

- 当前正式 Owner 为 Router → Coding / Testing / Review / Docs / Figma。
- Runtime 已有中文 Task Route、private evaluator、encrypted Reference Bundle、required-context lazy load、六个 MCP Tool 和 route capability。
- agent_skills_checkpoint 当前只检查 required Context 是否加载完成并维护阶段，不保存目标、决定、Vertical Slice、Evidence、blocker 等问题求解状态。
- 仓库已有 routing conformance、Source/Runtime parity、context budget、Runtime/Installer/Release 等大量确定性回归。
- 当前 figma/SKILL.md 为 909 行，详细规则大量常驻 Core；现有 References 已按事实源、系统映射、组件、Prototype、Design-to-Code、Findings、布局等专业域拆分。
- 当前没有 model-neutral 的真实 Agent Outcome Run/Trace/Scoring Contract，无法用同一套任务结果系统比较不同模型。
- 当前 Router 没有“模型身份”路由维度；这是正确基础，应保持模型/宿主差异只影响能力/阻塞与 Eval metadata，而不分叉治理规则。

## 问题、根因或约束

1. **效果不可量化**：现有测试更擅长证明治理实现没有漂移，不能证明某次 Skill 修改真的提高了 Agent 任务完成质量。
2. **长任务语义状态缺口**：Runtime 有治理 Context 连续性，但没有显式 Problem-solving State；上下文压缩或 Runtime 重建后只能靠宿主聊天历史恢复。
3. **Core 膨胀**：为了“内容不丢”持续把详细规则保留在 Core，会让所有 Figma 模式预付无关上下文；直接总结删除又会破坏效果。
4. **模型能力变化**：更强模型可能不再需要某些补偿型 heuristic，较弱模型又可能仍需要；如果把模型品牌写进治理路由，会形成不可维护的多套规则。
5. **真实模型外部依赖**：仓库 CI 不能凭空拥有 GPT/DeepSeek/GLM Provider 凭据，因此必须把“统一 Eval Contract”与“某模型已经真实验证兼容”的声明分开。

## 不修改的后果

- Skill 继续主要依靠文本存在性与确定性路由测试判断质量，难以回答“是否真的更会解决问题”。
- 长任务在上下文压缩/跨阶段时容易丢失已经确认的决定、失败实验和剩余 blocker。
- Figma Core 继续增长，不同上下文能力模型更容易出现漏读、注意力稀释或路由后仍加载过量内容。
- 后续模型升级可能只会继续叠加规则而无法安全删除无效 heuristic。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前 main HEAD 为 7d252cd5dd1ad76d8577f0826201b5d3676cb89c，仓库写权限可用 | GitHub App main branch / repo permission readback | 从当前 main 建独立分支，不直写 main |
| E2 | #266 使用 canonical Requirement Issue Profile，含 AC1–AC10、范围/非目标/不变项/验证要求 | live Issue #266 | 本 Change 逐条绑定 AC，不把自身当需求全集 |
| E3 | Runtime 稳定公开 MCP Tool 当前恰好六个；checkpoint 只返回 task/pass/phase/progress | canonical Ref13 + runtime.py/server.py | Task State 通过现有 start/checkpoint 扩展，不新增第七 Tool |
| E4 | figma/SKILL.md 当前 909 行；现有 00–07 References 已按专业域拆分 | canonical Figma Skill/References | 使用逐段原文迁移 + metadata 路由，不摘要删规则 |
| E5 | Runtime Router 的正式 ROUTE_DIMENSIONS 不包含模型身份 | runtime/agent_skills_runtime/routing.py | 模型名称不进入治理路由；只进入 Eval run metadata |
| E6 | 本宿主本地 git clone 因 DNS 无法访问 github.com，但已连接 GitHub App 可读写 canonical 仓库 | 本轮 clone 失败 + GitHub App branch 创建成功 | 使用带 blob/head guard 的 GitHub 等价能力，不把本地 Git 失败当仓库不可写 |
| E7 | 现有维护规则要求 Runtime Contract 变化执行三平台 package/smoke，Skill Mutation 做 Source/Runtime parity 与内容守恒 | canonical Maintenance / Ref13 / Ref15 / Ref28 | 本次不得只跑文本测试 |
| E8 | 当前用户明确排除 SEP-2640 与 Research/Analysis Skill | #266 非目标 | 两项不进入实现范围 |

## 推断与待确认

- 不需要额外业务 Owner 决策。Task State 字段和 Eval Contract 属于本次已明确工程目标；实现细节可在不改变 #266 语义的前提下按最小兼容方案自行确定。
- 真实 GPT/DeepSeek/GLM 在线运行需要对应宿主/Provider 能力；仓库本次实现统一 Eval Contract、case、grader 与比较工具，但没有真实 run artifact 的模型必须保持“未验证”，不能伪造兼容结论。

# 目标、成功标准与非目标

## 目标

建立一个不依赖模型品牌分叉的统一 Agent 工程 Contract，使不同模型在同一项目事实下获得同一 required governance context、接受同一权限/验证/完成门禁，并通过同一 Outcome Eval 判断真实任务效果；同时使长任务状态可恢复、Figma Core 渐进披露而内容守恒。

## 成功标准

- [ ] #266 / AC1：模型身份不进入治理路由，跨模型使用同一 canonical Contract。
- [ ] #266 / AC2：存在 model-neutral Outcome Eval Suite、grader/compare 工具和真实运行输入 Contract。
- [ ] #266 / AC3：存在 Trace/Run Artifact Contract，未知指标明确 unavailable，不编造。
- [ ] #266 / AC4：六 MCP Tool 不变，Runtime 支持结构化可恢复 Task State。
- [ ] #266 / AC5：start_task 恢复 + checkpoint 更新/读取 Task State，并保持 capability/context fail-closed。
- [ ] #266 / AC6：Figma Core 显著收窄，移出文本完整迁移到明确 Reference Owner，代表模式 Context Budget 不回归。
- [ ] #266 / AC7：Rule Effectiveness Gate 区分 invariant/policy/heuristic/technique，并把 heuristic 与真实失败/Eval 绑定。
- [ ] #266 / AC8：Multi-Agent 增加最小 Delegation Contract，不新增 Planner/Worker 控制面。
- [ ] #266 / AC9：README/USAGE/runtime 文档同步；SEP-2640、Research/Analysis Skill 保持非目标。
- [ ] #266 / AC10：targeted + required CI、独立 Review、guarded merge、main-fresh、repository-native archive、Requirement Closure 全部取得真实 Evidence。

## 范围

- canonical Skill/Reference 的跨模型一致性、渐进披露和内容守恒；
- Runtime Task State Contract；
- Agent Outcome Eval/Trace/Compare 工具与 fixtures；
- 受影响永久测试与 CI changed-scope；
- 维护者/最终用户说明同步；
- 完整 GitHub PR → merge → post-merge 收尾。

## 非目标

- SEP-2640 Compatibility；
- 通用 Research/Analysis Skill；
- Provider SDK 接入或在仓库内保存第三方 API Key；
- 按模型品牌复制 Skill/Reference；
- 静默升级 Runtime/依赖/包管理器；
- 改变目标业务项目 Contract/Schema/部署；
- 用摘要/删减替代详细规则迁移。

## 必须保持不变

- Source Mode canonical Ownership、Runtime encrypted Bundle、required-context private evaluator、Project Payload/Installer ownership；
- 六 MCP Tool 的数量和职责边界；
- L1/L2/L3、Authorization Continuity、Fresh Evidence、Requirement/Validation/Completion/Review/CI/Git/Release 门禁；
- Figma Ready/Prototype/Owner/Canvas/Design-to-Code 规则的触发、例外、失败处理和验证责任；
- Release 三平台 ZIP 产品面；
- 用户排除项。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 不新增顶层 Skill；跨模型 Contract 归 Router/Coding/Maintenance，Outcome Eval 为维护机器资产，Task State 归 Runtime，Figma 细则继续归 Figma References | E3–E5、#266 | 避免第二控制面 |
| 接口与契约 | 六 Tool 名称保持；start_task/checkpoint 增加可选 Task State，MCP Tool Contract 升级为 v4；新增 Task State v1 与 Outcome Eval v1 | E3、#266 AC4/5 | 需要 Contract/Runtime/package 回归 |
| 数据与迁移 | 无业务数据/Schema；Task State 为显式宿主 handoff 数据，不落隐藏 sidecar | #266、Runtime sidecarless 边界 | 不新增 Migration |
| 错误与失败语义 | 非法/过大 Task State fail closed；无真实模型 run 则兼容状态 unverified；Eval 缺少 metrics 用 unavailable | #266 AC2–5 | 禁止伪造兼容与指标 |
| 兼容性 | 当前版本无状态 start/checkpoint 调用继续可用；不承诺旧二进制跨版本协议兼容 | Maintenance 当前兼容策略 | 当前版本内平滑使用 |
| 部署与回滚 | 不 Deploy/Release；合并回滚使用 revert Implementation PR；Runtime 正式 Release 仍由后续独立 release 流程 | 仓库 Release 规则 | 本次只合并 main |

## 备选方案与取舍

1. **按模型维护独立 Skill/Profile**：拒绝。短期可补弱模型，但会让项目事实和治理语义随模型品牌漂移，无法保证统一验收，也会显著增加上下文和维护成本。
2. **只增加更多自然语言规则，不做 Outcome Eval/Task State**：拒绝。无法证明真实效果，也无法解决长任务恢复。
3. **把 Figma Core 直接摘要到 300–500 行**：拒绝。会丢失条件、例外、失败处理与可执行细节。
4. **推荐方案**：统一 canonical Contract + model-neutral Outcome Eval；Task State 通过现有六 Tool 可选字段扩展；Figma 详细段落逐段原文迁移到按需 Reference，并用 routing/context-budget/preservation 证明同效。

# 修改方案与决策依据

## 最小充分方案

1. **跨模型一致性 Contract**
   → Router/Coding/Maintenance 明确模型/宿主不能成为治理规则分叉依据；
   → 模型差异只进入 capability blocker 与 Outcome Eval metadata；
   → 验证同一 Task Route 的 deterministic routing 和无模型维度。
2. **Outcome Eval / Trace**
   → 新增 model-neutral eval suite、run artifact、criterion/evidence、metrics unavailable 语义；
   → 提供 validate/score/compare CLI；
   → fixtures 验证 pass/fail/unverified/cross-model divergence。
3. **Durable Task State**
   → 新增 Agent Skills 任务状态/v1 validator；
   → start_task 可选恢复；checkpoint 可选更新并返回；
   → 保持六 Tool、route capability、required-context、无 sidecar。
4. **Figma Progressive Disclosure**
   → 按现有章节边界把 Core 详细段落逐段原文搬到对应 Reference；
   → 更新 Reference metadata 使 review-only/review-and-fix/baseline/design-to-code 仍加载其真正必需细则；
   → Core 只保留模式/路由/Owner/Handoff/不可延迟硬门禁；
   → 增加 old→new preservation 与 context-budget regression。
5. **Rule Effectiveness / Multi-Agent**
   → Mutation 规则增加 invariant/policy/heuristic/technique 分类与 Eval 退役门禁；
   → Multi-Agent 增加最小 Delegation Contract。
6. **CI/Docs**
   → changed-scope selector 把 eval/runtime/figma contract 变化映射到最小充分 tests/package；
   → README/USAGE/runtime README 同步当前真实使用方式。
7. **交付**
   → 更新 Change 为 ready_for_review；
   → 创建 PR、fresh CI、独立 Review；
   → expected_head_sha guarded merge；
   → main fresh、repository-native archive、#266 AC Evidence 写回与关闭、任务分支清理。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E5 | 模型不是项目事实维度，保持同 Route/Contract 才能真正比较模型能力 |
| D2 | E3 | 扩展现有 start/checkpoint 可获得长任务状态，不引入第七 MCP Tool/第二控制面 |
| D3 | E4 | Figma 已有专业 Reference Owner，可逐段迁移而不是摘要删除 |
| D4 | E7 | Runtime Contract 变化必须由真实 package/MCP/三平台 Evidence 证明 |
| D5 | #266 AC2/3 | Outcome Eval 需要标准化 run/trace，不能用关键词/单元测试冒充真实模型效果 |
| D6 | #266 非目标 | 不实现 SEP-2640，不新增 Research/Analysis Skill |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 跨模型同一治理 Contract，模型身份不分叉路由 | #266 / AC1 | not_satisfied | 尚未实现 |
| R2 | model-neutral Outcome Eval 与跨模型比较 | #266 / AC2 | not_satisfied | 尚未实现 |
| R3 | Trace/Run Artifact Contract 与 unavailable 语义 | #266 / AC3 | not_satisfied | 尚未实现 |
| R4 | 六 Tool 下可恢复结构化 Task State | #266 / AC4 | not_satisfied | 尚未实现 |
| R5 | start/checkpoint 恢复/更新 + fail-closed | #266 / AC5 | not_satisfied | 尚未实现 |
| R6 | Figma 渐进披露且详细规则内容守恒 | #266 / AC6 | not_satisfied | 尚未实现 |
| R7 | Rule Effectiveness Gate | #266 / AC7 | not_satisfied | 尚未实现 |
| R8 | Multi-Agent Delegation Contract | #266 / AC8 | not_satisfied | 尚未实现 |
| R9 | 文档同步，明确两个非目标 | #266 / AC9 | not_satisfied | 尚未实现 |
| R10 | 完整测试/Review/CI/merge/post-merge closure | #266 / AC10 | not_satisfied | 尚未验证 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Router/Coding/Maintenance | 跨模型一致性与规则效力边界 | 统一 Contract，不复制模型规则 | R1/R7 |
| Figma Core + References | 原文迁移、metadata/Owner 调整 | 渐进披露且内容守恒 | R6 |
| runtime.py / server.py / Runtime docs | Task State v1、MCP v4 可选参数 | 长任务恢复 | R4/R5 |
| evals/ + scripts/agent_outcome_eval.py | case/run/trace/score/compare | 真实 Outcome Eval 基础 | R2/R3 |
| Multi-Agent Reference | Delegation Contract | 机器化现有协作原则 | R8 |
| tests / CI selector | 永久正反例与 changed-scope | 防止后续回归 | R1–R10 |
| README / USAGE / runtime README | 使用与维护说明 | 让最终用户/维护者正确使用 | R9 |

执行过程中保持最小闭环：

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 行为变化建立失败证据或说明测试例外
- [ ] 完成最小实现，不静默扩大范围
- [ ] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Task State validator/start/checkpoint、Outcome Eval validate/score/compare、Figma preservation helper/回归 |
| 接口 / 契约 | required | MCP Tool Contract v4、Task State v1、Outcome Eval v1、六 Tool list、Reference routing metadata |
| 集成 / 持久化 / 运行依赖 | required | RuntimeStore + stdio MCP smoke；不新增隐藏持久化 sidecar |
| 用户 / 工作流验收 | required | Runtime long-task resume workflow；Outcome Eval fixture workflow；Figma review/baseline/design-to-code 代表路由 |
| 跨组件关键路径 | required | canonical Source → bundle/project projection → Runtime MCP → task state/context；Skill Core → required References |
| 外部依赖 / 供应方探测 | not_applicable | 本次不调用真实模型 Provider；无对应凭据时必须保持模型兼容 unverified，不能伪造 Probe |
| 构建 / 打包 / 运行 | required | changed-scope 要求的 Linux/Windows/macOS onefile package/status/self-test/MCP/install |
| 文档 / 治理 / 其他 | required | Issue/Change Contract、内容守恒、context budget、routing conformance、README/USAGE/runtime docs、Review/CI/archive/closure |

## 验证计划

- 目标测试：新增 Task State、Outcome Eval、cross-model consistency、Figma progressive disclosure/preservation、Delegation/Rule Effectiveness 回归。
- 相关回归：routing conformance、context budget、Source/Runtime context conformance、Runtime routing/bundle/project projection/MCP/install、Figma Skill、Skill Mutation、portability。
- 静态检查或构建：Python compile/unittest；changed-scope selector；Runtime package scope。
- 专项真实边界：不进行真实 GPT/DeepSeek/GLM Provider Probe；真实 run artifact 缺失时只标记 unverified。
- 就绪检查：governance_contract + ready_check + PR Requirement Source + independent Review。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | Figma 迁移漏规则、Task State 扩大 MCP surface、Eval 被误当真实模型已验证 | old→new 内容守恒、六 Tool invariant、显式 unverified |
| 兼容性 | 当前版本无状态 start/checkpoint 保持可调用；模型不分叉规则 | 可选参数 + deterministic routing |
| 数据 / Migration | 不适用 | 无业务 Schema/数据；Task State 不做磁盘 sidecar |
| 部署 / 运行 | Runtime binary 行为变化但本次不 Release/Deploy | PR/main package Evidence；正式 Release 另走 release workflow |
| 回滚 / 恢复 | revert Implementation PR | 无生产数据或不可逆迁移 |

# 文档、依赖、部署与发布影响

- **长期文档**：更新 README、USAGE、runtime/README 与 canonical Skill/References。
- **依赖 / Runtime**：不新增/升级第三方依赖；Runtime MCP Contract 由 v3 升 v4，Task Route/Bundle/Project Payload 协议保持当前版本，除非实现事实要求最小同步。
- **配置 / Secret**：不新增 Provider Secret；真实 Outcome Run 由外部宿主提供，仓库 fixture 不含真实凭据/业务私密数据。
- **部署 / Release**：本次合并 main，不创建 tag/Release/Deploy；Runtime package 仅作为验证证据。
- **兼容 / 消费方通知**：USAGE/runtime README 说明 Task State 为可选能力；旧式当前版本调用不需要提供状态。

# 完成审计

进入 ready_for_review 前重新读取 #266、当前 main/base/head、实际 diff、受影响 canonical Owner、当前测试/CI 和独立 Review Evidence。

- [ ] upstream_re_read：待实现完成后重新读取 #266 与所有上游事实源。
- [ ] change_coverage：待逐条核对 AC1–AC10 与最终 diff/Evidence。
- [ ] reverse_audit：待从模型→route/context→执行→Evidence、Task State resume、Figma Core→Reference、Source→Runtime、PR→main/closure 反查。
- [ ] unresolved_cleared：待所有 not_satisfied 清零或取得正式 N/A/deferred 依据。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 7d252cd5 | GitHub canonical Source / #266 / Runtime/Figma 事实恢复 | 已完成调查 | 确认当前基线与变更边界 |
| V2 | 当前宿主 | local git clone | DNS 失败；GitHub App branch 创建成功 | 本地 Git transport 不可用，但 canonical GitHub App 写路径可用 |

## 未验证内容与剩余风险

- 尚未实现任何生产/治理修改。
- 尚未运行候选分支测试/CI。
- 尚未执行真实 GPT/DeepSeek/GLM Outcome Run；本次不会伪造该 Evidence。

## 交付状态

- 提交：Change 初始提交进行中。
- 拉取请求：尚未创建。
- CI：尚未运行候选分支 CI。
- 合并：尚未执行。
- Change 归档：尚未执行；merge 后由 repository-native automation 负责。
- 发布 / 部署：不适用；用户只要求合并 main，未授权 Release/Deploy。

## 备注

本 Change 允许分多个实现 commit，但最终 Requirement Scope 不因分批施工而缩小。
