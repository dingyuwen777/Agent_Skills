<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"review.reference.02","触发":{"包含":{"维度":"意图","取值":["代码审查","Review-only","Review-and-test","Review-and-fix","独立复核"]}},"依赖":["review.reference.01"]}
-->

# Findings 与严重度

Finding 同时给出 `severity` 与 `disposition`，两者独立。

## 1. 严重度

### `BLOCKER`

当前不能继续合并、发布或部署的确定问题，例如：

- 明确的数据损坏或不可逆错误；
- 已确认的严重安全或权限问题；
- 核心业务行为完全错误；
- 关键 Migration 或兼容路径会直接破坏现有数据或消费者；
- 当前验证已经证明目标无法工作。

### `HIGH`

重要正确性或交付风险，应在当前任务解决，例如：

- 用户明确需求没有实现；
- API、Contract、Schema、事务、并发或权限存在重要错误；
- 关键错误路径、幂等、恢复或状态机有可触发缺陷；
- 前后端或生产者/消费者真实不兼容；
- 关键用户工作流无法完成；
- 测试把 Mock/Fake 证据错误当成真实依赖闭环，导致重要风险完全未验证。

### `MEDIUM`

真实缺陷或明显测试/维护缺口，但通常不等于立即阻断全部功能，例如：

- 边界输入处理错误；
- 异常信息、资源释放、次要状态转换不正确；
- 会造成局部错误或较难排障；
- 重要但非核心场景缺少回归测试；
- 明确违反项目编码规范并形成实际维护风险。

### `LOW`

低风险但有明确价值的改进，例如：

- 局部可维护性问题；
- 已有项目规范下的命名、注释或组织偏差；
- 不会改变当前正确性的轻量测试可读性问题。

纯个人风格偏好、无证据“也许以后会更好”的重构建议，不应为了凑数量变成 Finding。

## 2. disposition：当前任务如何处理

| disposition | 当前返修行为 |
| --- | --- |
| `IN_SCOPE_BLOCKING` | **只有**此类进入自动返修 |
| `IN_SCOPE_NON_BLOCKING` | **不自动**返修 |
| `OUT_OF_SCOPE` | 默认 `RECORD_ONLY`；不扩当前 scope |
| `REQUIREMENT_CHANGE` | 需扩 Requirement/Contract/Schema/Scope/授权；回上游 |

高 severity 不自动授权扩 scope。

### Follow-up Admission Gate

`OUT_OF_SCOPE` 默认是 `RECORD_ONLY`：**不自动创建 Issue**、**不自动创建 Change**、**不自动创建 Branch**、**不自动创建 PR**、**不自动创建 Agent**、**不自动执行**，也**不递归派生**新的 Follow-up。

只有 Parent/Main 确认存在直接 Evidence、独立工程/业务价值、不是已有事项重复、值得长期跟踪且当前授权允许时，才可把它登记为 `FOLLOW_UP_BACKLOG`。进入 Backlog 仍不自动启动 Coding/Change/Agent；后续只有成为独立 Requirement 并重新通过正常准入后才执行。

### Follow-up Admission Gate

`OUT_OF_SCOPE` 默认到 `RECORD_ONLY` 即结束当前链路：**不自动创建 Issue**、**不自动创建 Change**、**不自动创建 Branch**、**不自动创建 PR**、**不自动创建 Agent**，也**不自动执行**或**不递归派生**新的 Follow-up。

只有 Main/Parent 已确认真实 Evidence、具有独立跟踪价值、不是已有事项重复且当前授权允许时，才可转为 `FOLLOW_UP_BACKLOG`。Backlog 只是后续候选，不自动启动开发；未来真正执行时必须作为新的 Requirement/任务重新准入。

## 3. 每个 Finding 的最小结构

建议使用：

```text
[HIGH] <一句话问题>
Disposition: IN_SCOPE_BLOCKING | IN_SCOPE_NON_BLOCKING | OUT_OF_SCOPE | REQUIREMENT_CHANGE

位置：<文件/函数/行或影响范围>
触发条件：<怎样发生>
影响：<用户/数据/调用方会看到什么>
证据：<代码路径、测试失败、Contract、日志、运行结果>
测试缺口：<为什么现有测试没挡住；不适用则说明>
修复方向：<最小方向，不强行替作者重设计>
验证建议：<什么测试/检查能证明修复>
```

如果精确行号不可稳定获得，可以使用函数、组件、Route、模块或 diff hunk 作为位置，但必须足够让开发者找到问题。

## 4. 触发条件是必须项

不要只写：

> 这里可能有竞态。

要写成能够被验证的条件，例如：

```text
两个执行者同时读取同一可执行记录，并在缺少现有项目要求的串行化机制时都进入同一副作用路径，可能产生重复结果。
```

触发条件让 Finding 可被测试，也能区分“理论可能”与真实可达路径。

## 5. 证据等级

按强到弱常见为：

```text
当前可重复失败 / 回归测试
→ 当前真实运行 / Integration / Golden Path 证据
→ 明确 Contract / Schema / 调用链矛盾
→ 静态代码路径可证明的逻辑错误
→ 合理风险假设
```

最后一类不能伪装成确定 Bug。可以写成待验证风险，并说明还需要什么实验或事实确认。

## 6. 测试缺口怎么写

测试缺口不是泛泛写“建议增加测试”。应说明现有测试实际断言了什么，以及什么错误仍然可能在测试绿色时发生。

例如：

```text
现有测试只断言成功状态和按钮出现，没有断言请求 payload 中的关键 scope；字段写错时该测试仍可能绿色。
```

或：

```text
Browser Mock 已覆盖失败提示，但没有运行真实 API/Persistence；因此不能单独证明服务器真实守卫和持久化行为。
```

这样开发者知道应该补哪一层证据。

## 7. 不要把测试失败本身直接等同生产 Bug

测试失败可能来自：

- 生产实现缺陷；
- 测试假设过期；
- Fixture/Mock 漂移；
- 环境不稳定；
- 外部依赖变化；
- 测试本身竞态或脆弱。

Review 必须先判断根因，再形成 Finding。

## 8. 重复问题合并

同一根因影响多个位置时，优先一个 Finding 描述根因和受影响范围，而不是复制多条相同问题。

只有每个位置需要独立修复、严重度不同或触发条件不同，才拆开。

## 9. Review 结论

可以使用：

```text
BLOCKED
→ 未解决的 IN_SCOPE_BLOCKING 禁止继续

CHANGES_REQUIRED
→ 当前仍有必须解决的 IN_SCOPE_BLOCKING

NON_BLOCKING_FINDINGS
→ 仅 IN_SCOPE_NON_BLOCKING / OUT_OF_SCOPE；说明未验证边界

NO_FINDINGS_WITHIN_SCOPE
→ 当前审查范围没有发现问题；必须同时报告范围、验证和未覆盖项
```

这些是 Review 输出语言，不替代代码托管平台的正式审批状态，也不自动授权合并。
