<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.26","触发":{"全部":[{"包含":{"维度":"执行模式","取值":["实现","诊断"]}},{"包含":{"维度":"意图","取值":["测试策略","功能测试","黑盒测试","用户场景验收","探索式测试","回归测试","独立验证"]}}]},"依赖":["coding.reference.07"]}
-->

# Testing 专业职责与 Coding Handoff

本 Reference 只定义 **Coding 正在实现/诊断且同时存在独立测试意图** 时与 Testing Skill 的 Ownership/Handoff，不复制 Testing 的测试方法。纯 Testing-only 或 Review-and-test 不因为本 Reference 反向加载 Coding。

## 1. Coding 仍拥有开发验证治理

Coding 保留：

- `Red → Verify Red → Green → Refactor → Re-verify` 开发闭环；
- Requirement Traceability、Validation Matrix、Completion Audit；
- 判断当前交付有哪些独立失败边界必须被证明；
- 开发过程中与实现紧耦合的最小 Unit/Component/Regression 测试；
- 生产代码根因诊断与修复；
- Git/CI/PR/Release 的验证门禁。

因此“新增 Testing Skill”不意味着每写一个函数或每跑一个 targeted test 都必须离开 Coding。

[08_分层测试与验收策略.md](08_分层测试与验收策略.md) 只负责把 Coding 的通用 Validation Matrix 映射成 UI/API/Persistence/Contract/Golden Path/Probe 等**证据边界**，不再维护这些测试怎样设计、Fixture/Fake/Mock 怎样构造或场景怎样执行；这些专业方法只能由 Testing 当前 canonical rules 提供。

## 2. Testing 是测试工程方法 Owner

当 Coding 任务同时需要以下任一独立测试能力时，通过 Router 叠加 [`.agents/skills/testing/SKILL.md`](../../testing/SKILL.md)：

- Test Strategy / Test Gap 设计；
- Scenario-based Black-box Acceptance；
- User Journey / Workflow Acceptance；
- Exploratory Testing；
- 系统性 Integration / Contract / Golden Path / External Probe 测试设计；
- 独立功能测试、独立验证；
- Bug 的独立复现与 Regression；
- 测试资产、Fixture/Fake/Mock/Harness 的专业设计。

Coding 不在本 Reference 或其他 Coding Owner 中复制第二套 Testing 详细方法；Validation Matrix 继续描述“需要什么等级的证据”，Testing 描述“怎样设计和执行对应测试”。

## 3. Owner-gated 路由边界

Task Route 先由 Skill Core trigger 选择专业 Owner；只有 Owner 已命中，其 References 才根据项目形态、风险、范围等 refinement facts 直接匹配。显式 Reference dependency 可以跨 Skill 扩展 required Context。

因此：

```text
项目形态=前端Web/后端服务 + 风险=L2 + 意图=黑盒测试
→ Testing-only（没有 Coding 执行意图时）

执行模式=实现 + 项目形态=前端Web + 意图=用户场景验收
→ Coding + Testing
→ 本 Handoff Reference 生效
```

不能通过给 Testing-only 任务补一个虚假的 `执行模式=实现` 来“帮助路由”；Task Route 只能提交真实当前事实。

## 4. 常见组合

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

## 5. 失败与权限边界

- Testing Skill 或 required Reference 无法取得时，不能用 Coding 中的旧摘要/记忆冒充独立 Testing；
- Testing 发现缺陷不自动获得生产代码修改、commit、push、merge、release 或 deploy 权限；
- Coding 也不能因为 Validation Matrix 要求某层证据，就把未运行的 Mock/Fake 结果冒充该真实边界；
- 项目没有独立测试工程价值时，不为了“每个 Skill 都走一遍”机械叠加 Testing。
