<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"testing.reference.03","触发":{"任一":[{"包含":{"维度":"阶段","取值":["缺陷修复","审查"]}},{"包含":{"维度":"意图","取值":["回归测试","Review-and-test","独立验证"]}}]},"依赖":["testing.reference.01"]}
-->

# 缺陷复现、回归与 Handoff

Testing 对缺陷的职责是建立可靠失败证据、验证修复结果和保护回归，不维护第二套生产代码修复规则。

## 1. 先复现，再谈修复

确定性 Bug/Review Finding 在进入 Coding 修复前，优先取得与风险匹配的失败证据：

```text
Requirement / expected behavior
→ Preconditions
→ Action / Input
→ Actual failure
→ Repeatability
→ Evidence boundary
```

如果问题来自真实外部依赖、硬件或不可控环境，必须区分：

- 产品代码缺陷；
- 测试环境缺陷；
- 网络/权限问题；
- 供应商或外部系统当前故障。

无法稳定复现时可以保留风险假设，但不能伪装成已确认 Bug。

## 2. 回归测试选择

优先选择**能稳定制造原错误且成本最低**的层：

- 纯业务规则错误 → Behavior/Unit/Component；
- public Contract 漂移 → Contract/Consumer；
- DB/file/queue/runtime 语义 → Integration；
- 用户操作或状态错误 → Workflow/Black-box；
- 跨组件接线错误 → Real Golden Path；
- 第三方当前协议事实 → 有界 External Probe。

同一个 Bug 不要求在所有层复制一遍。只有独立失败边界需要额外层。

## 3. 修复回路

Testing 发现生产缺陷后：

```text
失败证据已确认
→ Handoff Coding
→ Coding 根因诊断 / Red-Green / 最小修复
→ Coding 新鲜 Green
→ 返回 Testing
→ 原路径 Regression
→ 邻近高风险场景复测
→ 需要合并判断时 Handoff Review
```

Testing 默认不直接修改生产实现；用户显式授权完整 fix loop 时，也应通过 Coding 的 canonical 规则执行实现修改。

## 4. 回归测试必须证明什么

Bug 修复的永久测试应尽量满足：

- 修复前能因目标缺陷失败；
- 修复后通过；
- 断言业务可观察行为，不依赖无关内部实现；
- 不靠 sleep、随机时间或未控制网络制造“偶尔 Green”；
- 不通过降低断言、跳过 test、删除 fixture 或盲目更新 snapshot 制造 Green；
- 对历史合法行为有兼容风险时增加必要的反向/旧值回归。

## 5. 一次性调查与永久回归

一次性脚本/实验适合快速证伪环境、Provider 或疑似根因；只有存在长期回归价值时才进入正式 tests。

永久测试应复用项目既有 framework、fixture 和 test command，不为了 Testing 引入重复测试框架或平行 CI。

## 6. Re-test 范围

修复后至少复核：

- 原失败场景；
- 修复直接影响的相邻合法行为；
- 修复新增/改变的 Contract、状态、异常或副作用；
- 必要时的公开 Journey / Golden Path 接线。

如果修复范围明显扩大，停止滚雪球式补测，返回 Coding/Requirement Source 重新界定范围。

## 7. Testing → Review 的证据包

需要 Review 做合并/发布判断时，至少交付：

```text
原 Requirement / Finding
失败证据
修复后 Regression Evidence
实际运行的测试层
仍未运行的边界
测试资产变化
外部依赖/环境限制
```

Review 根据这些证据判断充分性；Testing 不替 Review 给出独立代码质量结论。