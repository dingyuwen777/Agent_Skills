<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"review.reference.02","触发":{"包含":{"维度":"意图","取值":["代码审查","Review-only","Review-and-test","Review-and-fix","独立复核"]}},"依赖":["review.reference.01"]}
-->

# Findings 与严重度

Finding 同时给出 `severity` 与 `disposition`；前者描述影响，后者决定当前任务是否返修。

## 1. severity

- **BLOCKER**：当前不能继续合并/发布/部署的确定问题，如数据损坏、严重安全/权限缺陷、核心行为失败或已验证的关键 Migration/兼容破坏。
- **HIGH**：当前任务必须解决的重要正确性/交付风险，如明确需求缺失、API/Contract/Schema/事务/并发/权限错误、关键状态/恢复缺陷、消费者不兼容或关键工作流失败。
- **MEDIUM**：真实缺陷或明显测试/维护缺口，但通常不阻断全部功能，如边界输入、异常/资源、次要状态或重要非核心回归缺口。
- **LOW**：不改变当前正确性但有明确价值的局部维护、规范或测试可读性问题。

纯个人风格偏好、无证据“也许更好”的重构建议不能为了凑数量变成 Finding。

## 2. disposition 与 Follow-up

| disposition | 当前行为 |
| --- | --- |
| `IN_SCOPE_BLOCKING` | **只有**此类进入自动返修 |
| `IN_SCOPE_NON_BLOCKING` | 当前相关但**不自动**返修 |
| `OUT_OF_SCOPE` | 默认 `RECORD_ONLY`，不扩当前 scope |
| `REQUIREMENT_CHANGE` | 需扩 Requirement/Contract/Schema/Scope/授权；回上游 |

severity 与 disposition 独立；高 severity 不自动授权扩大 scope。

### Follow-up Admission Gate

`OUT_OF_SCOPE` 到 `RECORD_ONLY` 即结束当前链路：**不自动创建 Issue**、**不自动创建 Change**、**不自动创建 Branch**、**不自动创建 PR**、**不自动创建 Agent**，也**不自动执行**或**不递归派生** Follow-up。

只有 Main/Parent 已确认 Evidence、存在独立跟踪价值、不是已有事项重复且当前授权允许时，才可转 `FOLLOW_UP_BACKLOG`；Backlog 只是候选，不自动开发。未来执行时重新作为新 Requirement/任务准入。

## 3. Finding 最小结构

```text
[SEVERITY] <问题>
Disposition: IN_SCOPE_BLOCKING | IN_SCOPE_NON_BLOCKING | OUT_OF_SCOPE | REQUIREMENT_CHANGE
位置: <文件/函数/范围>
触发条件: <怎样发生>
影响: <用户/数据/调用方结果>
证据: <代码/测试/Contract/日志/运行>
测试缺口: <为什么现有证据没挡住；不适用则说明>
修复方向: <最小方向>
验证建议: <怎样证明修复>
```

位置必须足够定位。触发条件是必须项：把“可能有竞态”改成可验证的并发/状态前提，区分理论可能与真实可达。

## 4. Evidence 与测试缺口

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

## 5. 去重与结论

同一根因影响多个位置时合并一个 Finding，除非各位置需独立修复、严重度或触发条件不同。

```text
BLOCKED
→ unresolved IN_SCOPE_BLOCKING 禁止继续

CHANGES_REQUIRED
→ 当前仍有必须解决的 IN_SCOPE_BLOCKING

NON_BLOCKING_FINDINGS
→ 仅 IN_SCOPE_NON_BLOCKING / OUT_OF_SCOPE；说明未验证边界

NO_FINDINGS_WITHIN_SCOPE
→ 当前审查范围未发现阻塞问题；仍报告范围、验证和未覆盖项
```

这些只是 Review 输出语言，不替代托管平台正式审批，也不自动授权合并。
