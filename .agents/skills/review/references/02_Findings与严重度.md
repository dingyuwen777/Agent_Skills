<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"review.reference.02","触发":{"包含":{"维度":"意图","取值":["代码审查","Review-only","Review-and-test","Review-and-fix","独立复核"]}},"依赖":["review.reference.01"]}
-->

# Findings 与严重度

Finding=`severity + Scope + Delivery Effect + Action`，四者正交。

## 1. severity

`BLOCKER/HIGH/MEDIUM/LOW` 只描述影响强度；无证据风格偏好不成 Finding，severity 不授权扩大 Scope/修复/Follow-up。

## 2. Finding 三轴 Contract

- **Scope**：`IN_SCOPE | OUT_OF_SCOPE | REQUIREMENT_CHANGE`；
- **Delivery Effect**：`BLOCKING | NON_BLOCKING`；
- **Action**：`AUTO_REPAIR | REPORT_ONLY | REQUIREMENT_DECISION | FOLLOW_UP_CANDIDATE`。
- **唯一自动返修组合**：Evidence + IN_SCOPE + BLOCKING + AUTO_REPAIR + 已有修改授权。
- **`OUT_OF_SCOPE + BLOCKING` 合法**：阻塞交付，不得改成 IN_SCOPE 自动修。
- Router 映射：返修→HANDOFF_CURRENT_SCOPE；阻塞→BLOCK_CURRENT_DELIVERY；上游变化→REQUIREMENT_DECISION；报告→REPORT_ONLY；候选→FOLLOW_UP_CANDIDATE。classification 由 Reviewer 判定。

## 3. Follow-up Admission 与生命周期

OUT_OF_SCOPE 默认 `REPORT_ONLY / RECORD_ONLY`：**不自动创建 Issue、不自动创建 Change、不自动创建 Branch、不自动创建 PR、不自动创建 Agent、不自动执行、不递归派生**。Evidence 足够、独立价值且非重复才成为 `FOLLOW_UP_CANDIDATE`。

```text
RECORD_ONLY → Follow-up Admission → FOLLOW_UP_CANDIDATE
→ Persistence Authorization Gate → 项目既有 backlog carrier → BACKLOG_ITEM → STOP
```

持久化要求既有 carrier + 项目规则/长期授权/用户明确授权 + 去重。**当前任务 Git 权限**或 commit/push/PR/merge 不授权 OUT_OF_SCOPE 持久化；无授权保留 candidate。`BACKLOG_ITEM` **不自动执行**或派生，未来按**新 Requirement / 新 Task**恢复 facts/Scope/Authorization/Risk/Evidence，旧 revision/decision_epoch/测试不继承。

## 4. Finding 最小结构

```text
[SEVERITY] 问题
Scope / Delivery Effect / Action
位置 / 触发条件 / 影响 / 证据
测试缺口（适用）/ 收口方向 / 验证建议
```

位置/触发必须可验证；证据不足写风险/待验证假设。

## 5. Evidence 与测试缺口

可重复失败/回归 > 真实 Integration/Golden Path > Contract/Schema/调用链矛盾 > 静态证明 > 风险假设；最后一类不冒充 Bug。Test Gap 写清现有证据边界，Mock/Fake/Browser 不冒充未运行真实边界。

## 6. 去重与结论

同根因默认合并。任意 unresolved BLOCKING→`BLOCKED`；IN_SCOPE+BLOCKING+AUTO_REPAIR→`CHANGES_REQUIRED`；REQUIREMENT_CHANGE→`UPSTREAM_DECISION_REQUIRED`；仅 NON_BLOCKING→`NON_BLOCKING_FINDINGS`；无 Finding→`NO_FINDINGS_WITHIN_SCOPE`。状态不替代平台审批或授权。
