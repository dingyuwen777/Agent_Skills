<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.32","触发":{"包含":{"维度":"意图","取值":["Agent效果评测"]}},"依赖":["coding.reference.02"]}
-->

# 跨模型一致性、Rule Effectiveness 与 Agent Outcome Eval

本 Reference 负责一件事：**让不同模型、不同宿主在 Agent_Skills 下接受同一可观察工程 Contract，并用真实任务 Outcome 而不是模型品牌或规则文本数量判断效果。**

它不创建模型专属 Skill，不新增 Planner/Worker 控制面，也不把模型名称加入 Task Route。具体项目技术栈、业务事实和宿主能力仍来自当前项目；模型/宿主名称只作为 Eval/Trace 标签。

## 1. Model-neutral Execution Contract

同一任务事实必须得到同一治理语义：

- 相同项目事实、Requirement、Contract、Schema、风险、授权和 Requested Outcome；
- 相同 canonical Skill/Reference、最低风险、验证责任、Review/Docs/Testing/Figma Handoff；
- 相同 Git/CI/PR/Release/数据安全与完成门禁；
- 相同“没有 Evidence 就不能宣称完成”的 Fresh Evidence Contract。

模型可以在**不改变上述可观察边界**的前提下使用不同内部推理方式、搜索顺序、工具组合、并行度或表达风格。模型更强或更弱都不能成为降低要求、跳过 required gate、扩大权限或改变业务 Contract 的理由。

### 模型事实与宿主事实必须分开

以下只是评测标签，不参与 Router：

- Provider / model family / model version；
- reasoning effort、temperature 或其他模型执行参数；
- 供应商宣传的能力等级。

以下如果真实存在，继续按当前 Router 作为项目/宿主事实处理：

- 当前宿主是否真的有 Git/Figma/Browser/Test/Multi-Agent 等能力；
- 工具能否读写目标仓库、外部服务或本地文件；
- 当前授权是否允许修改、提交、合并、发布、部署；
- 项目真实工具链、版本、平台和 CI。

因此：

model difference ≠ governance branch  
host capability difference → 使用已有能力/工具链/授权维度细化

不得增加 GPT/DeepSeek/GLM 专属 Reference 来“补偿”模型，除非未来 Requirement 明确建立一个**外部 Provider/宿主真实 Contract**，且该规则描述的是工具/协议事实而不是模型聪明程度。

## 2. Outcome Eval 是 Skill 效果的优先证据

规则存在、关键词回归、路由正确和 CI Green 都不能单独证明 Agent 更会解决问题。对会影响 Agent 行为的方法性变更，优先建立或复用真实任务 Outcome Eval。

canonical machine assets：

.agents/evals/agent_outcome_eval.py  
.agents/evals/cases.json  
.agents/evals/fixtures/sample_runs.jsonl

当前机器协议：

- Agent Skills Outcome Eval Cases/v1
- Agent Skills Outcome Run/v1
- Agent Skills Outcome Report/v1

Eval case 必须描述**可观察结果和禁止结果**，而不是“模型是否复述了某条规则”。至少持续覆盖：

- L2 Feature；
- 根因未知 Bug；
- Review / Testing；
- 方案与长任务；
- Figma / Design-to-Code；
- Git Delivery；
- L1 负例 / 防过度治理。

新增真实高价值失败模式时，优先把它加入最小 case corpus；不要为了提高 case 数量复制同义场景。

## 3. Run / Trace Contract

真实模型运行应记录当前宿主能够可靠取得的事实：

- 用例；
- 模型标签、宿主标签；
- 是否为真实模型运行；
- 受验源码 revision；
- Task Route / 路由结果的安全摘要；
- Context 大小/加载等可得统计，不记录 private canonical plaintext；
- model/tool/user/evidence/error/retry 轨迹摘要；
- 每条验收的状态与直接 Evidence；
- 禁止结果是否发生及 Evidence；
- 最终结果；
- tool calls、retry、用户干预、耗时、tokens、cost 等可得指标。

无法取得的指标必须显式写 unavailable，不猜数字。Trace 只保存完成评测需要的最少安全摘要；Secret、Token、密码、敏感 Raw、PII、完整私有治理正文不得为了 Eval 进入仓库。

真实 run artifact 默认是**输入 Evidence**，不是必须提交 Git 的长期资产。仓库维护 machine contract、case、deterministic fixture、grader 和永久回归；包含真实项目/模型数据的 run 是否保存、保存到哪里由当前项目与安全边界决定。

## 4. Verified Compatibility 的严格边界

deterministic fixture 只证明 evaluator/grader 可重复工作，不能证明任何真实模型兼容。

一个 model + host 组合只有在：

1. 对当前所有 兼容必测 case 有真实模型运行；
2. 每个 case 达到相同最低分；
3. 没有阻塞禁止项；
4. 直接 Evidence 足以支持对应验收；
5. 受验 Agent_Skills revision 可追溯；

时，才允许在 Eval report 中标记 verified。

没有实际运行 GPT、DeepSeek、GLM 或其他模型时，只能写 unverified / 未验证；不得根据模型能力宣传、历史聊天、单次成功或 deterministic fixture 宣称“已经保证跨模型一致”。

模型升级、宿主升级、重大 Runtime/Router/Skill Mutation 后，如果旧 Evidence 不再覆盖当前 revision/Contract，按 Fresh Evidence Contract 重跑受影响 case，而不是自动继承 verified。

## 5. Rule Effectiveness Gate

维护 Skill/Reference 时，把规则按**语义职责**区分为四类，用于决定“能否随模型升级减弱”，而不是形成新的 Runtime schema 或项目业务字段。

### invariant

无论模型多强都不能静默降低，例如：

- 权限与授权边界；
- public Contract / Schema / 数据安全；
- 用户工作保护；
- Fresh Evidence；
- required CI / Review / Completion gate；
- canonical Ownership 与内容守恒。

### policy

维护者/团队明确要求长期成立的工作约定，例如：

- 项目正式 Git/PR 流程；
- 提交语言、时间基准或组织级编码要求；
- 明确的审计与交付政策。

模型能力变化不能自行取消 policy；只能由新的 Requirement Source 明确改变。

### heuristic

为降低已观察到的 Agent 失败概率而增加的方法性指导，例如：

- 容易在某类任务提前过度规划；
- 容易把 Mock 冒充真实边界；
- 容易在冲突中机械 ours/theirs；
- 容易漏掉某种反向审计。

新增或显著强化 heuristic 时，优先关联真实失败、Review Finding、Eval case 或可证伪风险。没有直接历史失败也可以基于明确高风险机制增加，但必须说明依据，不能只写“最佳实践”。

### technique

可选解决技巧或分析方法，例如某种设计比较、调试实验、任务拆法。只有场景真实命中时按需加载，不把 technique 升格成所有任务的全局硬步骤。

## 6. 模型升级后的规则清理

模型升级不是自动删规则的授权。只有 heuristic / technique 才允许进入效果复核：

旧规则 + 当前模型/宿主  
→ 同一 Outcome Eval case  
→ 候选降级/条件化/删除  
→ 再跑相同 case + 关键负例  
→ 结果不回归且内容守恒/路由可达  
→ 才能修改 canonical

invariant / policy 不走“模型更强所以删除”路径；如需改变，必须有新的上游 Requirement/Owner 决定。

不得通过以下方式制造“上下文更小”：

- 摘要掉例外、失败处理或停止条件；
- 删除验证责任；
- 抬高 Context Budget；
- 把详细规则换成“请遵循最佳实践”；
- 只因某个强模型一次成功就删除弱模型需要的可执行边界。

## 7. 渐进式披露与跨模型同效

渐进式披露的目标是**让所有模型在需要时获得完整、明确、可执行的 Context，同时避免无关任务常驻整库规则**。

重组 Skill 时：

1. Core 只保留无法延迟的不变量、模式选择、硬停止条件和 Reference 触发入口；
2. 详细方法按真实任务条件迁入唯一 Owner Reference；
3. 原触发、例外、失败/停止、验证、安全、兼容逐项迁移；
4. Source/Runtime 使用同一 metadata/evaluator；
5. Context Budget 只能通过减少无关常驻 Context、消除已证明等价重复或更精确路由改善；
6. 不通过摘要或抬阈值制造 Green。

强模型可以更好地利用薄 Core，但弱模型仍会在命中场景时得到**完整 Reference 原文**；这才是跨模型一致性与渐进披露同时成立的条件。

## 8. Eval 驱动的 Mutation 门禁

Skill Mutation Audit / Apply 至少判断：

- 本次改变的是 invariant / policy / heuristic / technique 中哪一类？
- 是否改变可观察 Agent 行为？
- 是否已有对应 Outcome Eval case？
- 没有 case 时，本次变化是否值得新增最小 case？
- 新/旧规则在同一 case 下是否存在明确非回归证据？
- 负例是否证明不会把轻任务过度治理？
- 未运行的模型是否被错误描述为已验证？

Semantic Local 且不改变 Agent 行为时，不为形式增加 Outcome Eval；Routing/Runtime/方法性规则变化才按真实风险增加对应 case/fixture/集成 Evidence。

Outcome Eval 不替代现有 unit/contract/routing/runtime/CI 测试。两者分别回答：

机器 Contract 有没有坏  
vs  
Agent 在真实任务上是否更有效

只有两条证据轴都满足当前完成结论时，才能用“跨模型效果保持/改善”描述一次高价值 Skill Mutation。
