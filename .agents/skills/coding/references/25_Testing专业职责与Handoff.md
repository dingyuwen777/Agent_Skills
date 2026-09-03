<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.25","触发":{"任一":[{"包含":{"维度":"意图","取值":["测试策略","功能测试","黑盒测试","用户场景验收","探索式测试","回归测试","Review-and-test","独立验证"]}},{"包含":{"维度":"能力","取值":["测试"]}}]},"依赖":["coding.reference.07"]}
-->

# Testing 专业职责与 Coding Handoff

本 Reference 只定义 Coding 与独立 Testing Skill 的 Ownership/Handoff，不复制 Testing 的测试方法。

## 1. Coding 仍拥有开发验证治理

Coding 保留：

- `Red → Verify Red → Green → Refactor → Re-verify` 开发闭环；
- Requirement Traceability、Validation Matrix、Completion Audit；
- 判断当前交付有哪些独立失败边界必须被证明；
- 开发过程中与实现紧耦合的最小 Unit/Component/Regression 测试；
- 生产代码根因诊断与修复；
- Git/CI/PR/Release 的验证门禁。

因此“新增 Testing Skill”不意味着每写一个函数或每跑一个 targeted test 都必须离开 Coding。

## 2. Testing 是测试工程方法 Owner

当任务需要以下任一能力时，通过 Router 进入 [`.agents/skills/testing/SKILL.md`](../../testing/SKILL.md)：

- Test Strategy / Test Gap 设计；
- Scenario-based Black-box Acceptance；
- User Journey / Workflow Acceptance；
- Exploratory Testing；
- 系统性 Integration / Contract / Golden Path / External Probe 测试设计；
- 独立功能测试、独立验证；
- Review-and-test；
- Bug 的独立复现与 Regression；
- 测试资产、Fixture/Fake/Mock/Harness 的专业设计。

Coding 不在本 Reference 或其他 Coding Owner 中复制第二套 Testing 详细方法；Validation Matrix 继续描述“需要什么等级的证据”，Testing 描述“怎样设计和执行对应测试”。

## 3. 常见组合

### 普通开发期 TDD

```text
Coding
→ 最小 Red
→ 实现
→ Green
```

如果没有独立测试工程风险，不强制叠加 Testing。

### 用户可见 L2/L3 Feature

```text
Coding 实现 + 开发期测试
→ Testing 用户 Journey / 黑盒 / 必要分层验证
→ Review（项目门禁或显式要求时）
```

### 用户可见 Bug

```text
Testing 或 Coding 取得原始失败证据
→ Coding 修复
→ Testing 原用户路径 Regression（存在独立用户工作流风险时）
→ Review re-review（适用时）
```

### Review 发现测试缺口

```text
Review
→ Handoff Testing 设计/执行缺失验证
→ Testing 返回 Evidence / Defect
→ 有生产缺陷则 Coding 修复
→ Testing Regression
→ Review re-review
```

## 4. 失败与权限边界

- Testing Skill 或 required Reference 无法取得时，不能用 Coding 中的旧摘要/记忆冒充独立 Testing；
- Testing 发现缺陷不自动获得生产代码修改、commit、push、merge、release 或 deploy 权限；
- Coding 也不能因为 Validation Matrix 要求某层证据，就把未运行的 Mock/Fake 结果冒充该真实边界；
- 项目没有独立测试工程价值时，不为了“每个 Skill 都走一遍”机械叠加 Testing。