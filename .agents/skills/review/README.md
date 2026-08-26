# Review Skill

`review` 是跨项目、跨语言的独立代码审查 Skill，从**独立审查者 + 测试专家**视角检查实现是否满足需求、Coding/项目规范是否被遵守、测试是否覆盖关键风险，以及证据是否足以支持“可合并/可交付”等结论。

它不维护第二套开发规范。同仓有 Coding 时必须读取 Coding，并把 Coding 作为唯一研发规范源。

## 1. 三种模式

- `review-only`：默认，只审查和运行已有授权验证，不自动改代码/测试/文档/提交；
- `review-and-test`：有测试修改授权时补最小长期测试，生产缺陷仍返回 Coding；
- `review-and-fix`：先 Review 形成 Finding，再返回 Coding 完整流程修复，取得新鲜证据后 re-review。

## 2. Review 不先相信什么

不把 PR 描述、Change checklist、作者结论、覆盖率数字或 CI 全绿当成完整需求/充分证据。复杂 Review 要独立执行：

```text
A1 上游要求 → 当前实现/变更
A2 当前实现/变更 → 测试/文档/运行证据
```

## 3. 测试专家方法

从可观察行为和失败风险反推证据。真实存在相应边界时区分：

- UI / Client Mock Acceptance；
- Backend / API / Persistence Integration；
- Contract / Generated Consumer；
- Real Cross-component Golden Path；
- External Dependency / Provider Probe。

这些层证明不同事实，不能互相冒充。CLI、Library、Mobile、Embedded、Data、IaC 使用自己的真实 Workflow/Runtime/Build/Device/Plan 证据。

## 4. Findings

有效 Finding 说明：严重度、位置、触发条件、影响、证据、测试缺口、最小修复方向和验证建议。没有足够证据时降级为待验证风险，不为凑数量报告个人风格偏好。

## 5. 常用请求

```text
使用 review-only 审查当前 PR。先恢复上游需求和 Coding/项目规则，再检查 diff、调用链、测试充分性和兼容风险，只报告 Findings。
```

```text
使用 review-and-test，从需求和失败风险反推应有证据；补最小长期测试，不用 Mock/Fake 冒充未运行真实边界。
```

```text
使用 review-and-fix。Review 先形成有证据 Finding；生产实现修改返回 Coding；修复并取得新鲜证据后再次 Review。
```
