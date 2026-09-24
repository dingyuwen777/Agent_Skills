<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"review.reference.02","触发":{"包含":{"维度":"意图","取值":["代码审查","Review-only","Review-and-test","Review-and-fix","独立复核"]}},"依赖":["review.reference.01"]}
-->

# Findings 与严重度

Finding 使用 `severity + Scope + Delivery Effect + Action`；四者正交，severity 不授予扩大 Scope、修复或 Follow-up 权限。

## 1. severity

- **BLOCKER**：极高影响，在其实际交付边界内不能安全/正确继续，如数据损坏、严重安全/权限、核心行为、关键 Migration/兼容破坏。
- **HIGH**：重要正确性/交付风险，如需求缺失、Contract/Schema/事务/并发/权限/恢复/消费者兼容错误。
- **MEDIUM**：真实缺陷或重要测试/维护缺口，但通常不破坏核心工作流。
- **LOW**：不改变当前正确性但有明确维护/规范/测试价值。
- 纯风格偏好或无证据“也许更好”不形成 Finding。

## 2. Finding 三轴 Contract

| 轴 | 值 | 语义 |
| --- | --- | --- |
| Scope | `IN_SCOPE` | 当前 Requirement/Acceptance/已授权修复范围 |
|  | `OUT_OF_SCOPE` | 独立问题，不属于当前自动修复范围 |
|  | `REQUIREMENT_CHANGE` | 需改变 Requirement/Acceptance/Contract/Schema/Data/Scope/Authorization |
| Delivery Effect | `BLOCKING` | 当前 Completion Scope 不能安全/正确继续 |
|  | `NON_BLOCKING` | 不阻止当前 Completion Scope |
| Action | `AUTO_REPAIR` | **唯一自动返修组合**：Evidence + IN_SCOPE + BLOCKING + 已有修改授权 |
|  | `REPORT_ONLY` | 只报告 |
|  | `REQUIREMENT_DECISION` | 回上游 Owner |
|  | `FOLLOW_UP_CANDIDATE` | 独立后续候选，不等于持久对象/执行授权 |

**`OUT_OF_SCOPE + BLOCKING` 合法**：阻塞当前交付，但不能被 Parent/Worker 改成 IN_SCOPE + AUTO_REPAIR。

按 Router 终态映射：当前自动返修→`HANDOFF_CURRENT_SCOPE`；无法在范围内解除的 BLOCKING→`BLOCK_CURRENT_DELIVERY`；Requirement 变化→`REQUIREMENT_DECISION`；非阻塞报告→`REPORT_ONLY`；后续候选→`FOLLOW_UP_CANDIDATE`。Finding classification 仍由 Reviewer 按 Evidence 独立判断。

## 3. Follow-up Admission 与生命周期

`OUT_OF_SCOPE` 默认 `REPORT_ONLY / RECORD_ONLY`，**不自动创建 Issue/Change/Branch/PR/Agent，不自动执行、不递归派生**。只有 Evidence 足够、独立长期价值成立且非重复，才可标为 `FOLLOW_UP_CANDIDATE`。

```text
RECORD_ONLY
→ Follow-up Admission
→ FOLLOW_UP_CANDIDATE
→ Persistence Authorization Gate
→ 项目既有 backlog carrier
→ BACKLOG_ITEM
→ STOP
```

**Persistence Authorization Gate**：只有项目已有正式 carrier，且项目规则/长期授权/当前用户明确允许该持久化动作并完成去重，才可写 Issue/Change/其他 backlog。**当前任务 Git 权限**或 commit/push/PR/merge 授权不自动授权持久化 OUT_OF_SCOPE Follow-up；无 carrier/授权时保留 candidate。

`BACKLOG_ITEM` 仍**不自动执行**、不创建 Branch/Change/PR/Agent、不递归。未来处理必须作为**新 Requirement / 新 Task**重新恢复 facts、Scope、Authorization、Risk、Evidence/Completion Contract；旧 revision/decision_epoch/测试不自动继承。

## 4. Finding 最小结构

```text
[SEVERITY] <问题>
Scope: IN_SCOPE | OUT_OF_SCOPE | REQUIREMENT_CHANGE
Delivery Effect: BLOCKING | NON_BLOCKING
Action: AUTO_REPAIR | REPORT_ONLY | REQUIREMENT_DECISION | FOLLOW_UP_CANDIDATE
位置 / 触发条件 / 影响 / 证据
测试缺口（适用时）
修复或收口方向
验证建议
```

位置和触发条件必须可验证；证据不足写“风险/待验证假设”，不伪装确定 Bug。

## 5. Evidence 与测试缺口

证据强度常见为：当前可重复失败/回归 → 真实 Integration/Golden Path → Contract/Schema/调用链矛盾 → 静态可证明错误 → 合理风险假设。最后一类不能冒充确定 Bug。Test Gap 要说明现有证据证明了什么、什么仍可能绿色；Mock/Fake/Browser 不冒充未运行真实边界。测试失败也先区分实现、过期假设、Fixture/Mock、环境/外部依赖和竞态。

## 6. 去重与结论

同一根因默认合并；只有独立修复、severity/Scope/Delivery Effect/触发不同才拆分。

- `BLOCKED`：任意 unresolved `Delivery Effect=BLOCKING`；
- `CHANGES_REQUIRED`：IN_SCOPE + BLOCKING + AUTO_REPAIR；
- `UPSTREAM_DECISION_REQUIRED`：REQUIREMENT_CHANGE / REQUIREMENT_DECISION；
- `NON_BLOCKING_FINDINGS`：仅 NON_BLOCKING；
- `NO_FINDINGS_WITHIN_SCOPE`：当前审查范围未发现 Finding，仍报告范围/Evidence/未覆盖项。

这些状态不替代平台审批，也不自动授权修改、Follow-up 持久化或合并。
