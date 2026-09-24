<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"review.reference.02","触发":{"包含":{"维度":"意图","取值":["代码审查","Review-only","Review-and-test","Review-and-fix","独立复核"]}},"依赖":["review.reference.01"]}
-->

# Findings 与严重度

Finding 必须把**影响大小、当前范围、当前交付影响、后续动作**分开表达，避免一个枚举同时承担互相独立的语义：

```text
severity
+ Scope
+ Delivery Effect
+ Action
```

其中 Scope / Delivery Effect / Action 是当前 Finding 的三轴决策模型；severity 只描述影响强度，不授予修复、扩大范围或创建后续任务的权限。

## 1. severity

- **BLOCKER**：问题本身影响极高；在它实际影响的交付边界内不能安全/正确继续，例如数据损坏、严重安全/权限缺陷、核心行为失败或已验证的关键 Migration/兼容破坏。
- **HIGH**：重要正确性/交付风险，如明确需求缺失、API/Contract/Schema/事务/并发/权限错误、关键状态/恢复缺陷、消费者不兼容或关键工作流失败。
- **MEDIUM**：真实缺陷或明显测试/维护缺口，但通常不破坏核心工作流，如边界输入、异常/资源、次要状态或重要非核心回归缺口。
- **LOW**：不改变当前正确性但有明确价值的局部维护、规范或测试可读性问题。

纯个人风格偏好、无证据“也许更好”的重构建议不能为了凑数量变成 Finding。severity 高也**不自动**说明问题属于当前 Scope；当前是否阻塞交付由 Delivery Effect 单独判断。

## 2. Finding 三轴 Contract

### Scope

- `IN_SCOPE`：Finding 属于当前 Requirement / Acceptance / 已授权修复范围。
- `OUT_OF_SCOPE`：Finding 是独立问题，不属于当前 Requirement 的自动修复范围。
- `REQUIREMENT_CHANGE`：解决它需要改变 Requirement/Acceptance、public Contract、Schema/Data、Scope、Authorization 或其他上游决定。

### Delivery Effect

- `BLOCKING`：在当前 Evidence 下，**当前 Completion Scope 不能安全或正确继续**。
- `NON_BLOCKING`：该 Finding 不阻止当前 Completion Scope 达成；可以报告，但不能因为“还能优化”驱动无限返修。

Scope 与 Delivery Effect 正交。**`OUT_OF_SCOPE + BLOCKING` 是合法组合**：问题不应被静默吸收进当前修复范围，但它可以真实阻塞当前 merge/release/deploy/交付，直到外部依赖问题解决、上游决定改变或新 Evidence 证明其不再阻塞。

### Action

- `AUTO_REPAIR`：只允许 Evidence 成立且 `Scope=IN_SCOPE`、`Delivery Effect=BLOCKING`，并已有对应修改授权时使用；这是**唯一自动返修组合**。
- `REPORT_ONLY`：只报告，不自动修改、不持久化新任务。
- `REQUIREMENT_DECISION`：返回上游 Requirement/Contract/Schema/Scope/Authorization Owner 决策。
- `FOLLOW_UP_CANDIDATE`：独立后续候选；只表示值得未来单独评估，不等于 Issue/Change/Backlog Item，也不自动执行。

不合法的组合不能靠 Parent/Worker 自行“修正”为更高权限动作。例如 `OUT_OF_SCOPE + BLOCKING` 不能为了消除 blocker 被改写成 `IN_SCOPE + AUTO_REPAIR`。

### Router terminal mapping

Review 形成三轴 Finding 后，按 Router 的 **Cross-Skill Terminal / Handoff Contract** 映射：

- `IN_SCOPE + BLOCKING + AUTO_REPAIR` → `HANDOFF_CURRENT_SCOPE`；
- 任意 unresolved `Delivery Effect=BLOCKING` 且当前不能在范围内修复 → `BLOCK_CURRENT_DELIVERY`；
- `REQUIREMENT_CHANGE` / `REQUIREMENT_DECISION` → `REQUIREMENT_DECISION`；
- `OUT_OF_SCOPE + NON_BLOCKING + REPORT_ONLY` → `REPORT_ONLY`；
- `FOLLOW_UP_CANDIDATE` → `FOLLOW_UP_CANDIDATE`。

Router 只拥有终态/交接语义；Finding 是否成立、三轴如何分类仍由 Reviewer 根据 Evidence 独立判断。

## 3. Follow-up Admission 与生命周期

`OUT_OF_SCOPE` 默认先结束为 `REPORT_ONLY / RECORD_ONLY`：**不自动创建 Issue**、**不自动创建 Change**、**不自动创建 Branch**、**不自动创建 PR**、**不自动创建 Agent**，也**不自动执行**或**不递归派生** Follow-up。

只有 Reviewer 已确认：

- Evidence 足够；
- 存在独立、长期跟踪价值；
- 不是已有事项的重复；
- 它不应被吸收进当前 Requirement；

才可以把 Action 标为 `FOLLOW_UP_CANDIDATE`。这一步仍然只是候选。

完整状态链：

```text
OUT_OF_SCOPE / 新独立问题
→ RECORD_ONLY
→ Follow-up Admission
→ FOLLOW_UP_CANDIDATE
→ Persistence Authorization Gate
→ 项目既有 backlog carrier
→ BACKLOG_ITEM
→ STOP
```

### Persistence Authorization Gate

把 candidate 写成 Issue/Change/其他持久 backlog 是新的外部副作用，必须同时满足：

1. 当前项目已经存在可复用的正式 backlog carrier；不得为了 Follow-up 发明平行任务系统；
2. 项目规则、长期授权或当前用户明确允许创建该类持久对象；
3. 目标对象与 Finding Evidence/范围一致，并完成重复检查。

**当前任务 Git 权限、当前范围的 commit/push/PR 权限，或当前任务“合并 main”的授权，都不能自动扩展为持久化 `OUT_OF_SCOPE` Follow-up 的权限。**

没有 carrier 或没有持久化授权时，candidate 保留在当前报告中，不能把权限缺口伪装成 `not_applicable`，也不能要求用户为了清单整洁必须建 Issue。

### BACKLOG_ITEM 不是新任务执行授权

成功持久化只得到 `BACKLOG_ITEM`，随后必须 **STOP**。它不自动创建 Branch/Change/PR/Agent，不自动进入 Coding，也不递归派生 Follow-up。

未来真正执行时：

```text
BACKLOG_ITEM
→ 新 Requirement / 新 Task
→ fresh fact recovery
→ fresh Scope / Authorization / Risk
→ fresh Evidence / Completion Contract
```

不得把原任务授权、旧 revision、旧 decision_epoch 或旧测试结果直接继承成新任务完成事实。

## 4. Finding 最小结构

```text
[SEVERITY] <问题>
Scope: IN_SCOPE | OUT_OF_SCOPE | REQUIREMENT_CHANGE
Delivery Effect: BLOCKING | NON_BLOCKING
Action: AUTO_REPAIR | REPORT_ONLY | REQUIREMENT_DECISION | FOLLOW_UP_CANDIDATE
位置: <文件/函数/范围>
触发条件: <怎样发生>
影响: <用户/数据/调用方结果>
证据: <代码/测试/Contract/日志/运行>
测试缺口: <为什么现有证据没挡住；不适用则说明>
修复方向: <最小方向；非当前修复时明确 report/upstream/follow-up>
验证建议: <怎样证明修复或解除 blocker>
```

位置必须足够定位。触发条件是必须项：把“可能有竞态”改成可验证的并发/状态前提，区分理论可能与真实可达。

## 5. Evidence 与测试缺口

Evidence 常见强度：

```text
当前可重复失败/回归测试
→ 真实运行/Integration/Golden Path
→ 明确 Contract/Schema/调用链矛盾
→ 静态路径可证明错误
→ 合理风险假设
```

最后一类不能伪装成确定 Bug。Test Gap 必须说明“现有测试证明了什么、什么错误仍可能绿色”，而不是只写“建议加测试”。Mock/Fake/Browser 证据不能冒充未运行的真实后端、持久化或外部依赖。

测试失败本身也不自动等于生产 Bug；先区分实现缺陷、过期测试假设、Fixture/Mock 漂移、环境/外部依赖变化和测试竞态。

## 6. 去重与结论

同一根因影响多个位置时合并一个 Finding，除非各位置需独立修复、severity、Scope、Delivery Effect 或触发条件不同。

```text
BLOCKED
→ 任意 unresolved Delivery Effect=BLOCKING
→ 无论 IN_SCOPE / OUT_OF_SCOPE / REQUIREMENT_CHANGE，都不得冒充当前交付可继续

CHANGES_REQUIRED
→ 存在 IN_SCOPE + BLOCKING + AUTO_REPAIR，需要当前范围返修

UPSTREAM_DECISION_REQUIRED
→ REQUIREMENT_CHANGE / REQUIREMENT_DECISION 阻塞当前结论

NON_BLOCKING_FINDINGS
→ 只有 Delivery Effect=NON_BLOCKING 的 Finding；说明范围和未验证边界

NO_FINDINGS_WITHIN_SCOPE
→ 当前审查范围未发现 Finding；仍报告审查范围、证据和未覆盖项
```

这些只是 Review 输出语言，不替代托管平台正式审批，也不自动授权修改、持久化 Follow-up 或合并。