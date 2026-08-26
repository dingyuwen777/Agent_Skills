---
name: review
description: 面向不同项目形态、编程语言和工具链的独立代码审查与测试充分性验证工作流。Review 不维护第二套编码规范；同仓存在 Coding Skill 时，先读取 Coding 并以其为唯一研发规范源，再独立重建需求与风险、审查 diff/实现/测试/文档、从测试专家视角设计最少充分验证、输出有证据的 Findings。支持 review-only、review-and-test、review-and-fix，并在修复时返回 Coding、修复后 re-review。Use for code review, pull request review, audit, test adequacy analysis, independent verification, regression-risk analysis, and review-driven fix loops across languages and project types.
---

# Review

Review 作为**独立审查者 + 测试专家**回答：

```text
上游要求到底是什么？
实现真的满足了吗？
现有测试真正证明了什么？
还存在哪些可触发、可解释、可验证的问题？
这些问题是否阻塞合并、发布或交付？
```

核心链路：

```text
恢复当前事实与 Review Target
→ 读取适用项目规则
→ 同仓有 Coding 时读取 Coding 作为唯一研发规范源
→ 独立重建需求、风险和应有证据
→ 审查实现 / diff / 测试 / 文档
→ 主动验证高风险假设
→ 输出 Findings 与证据边界
→ 有修复授权时返回 Coding 修复
→ 新鲜验证
→ Review re-review
```

Review **不复制** Coding 的编码、TDD、Git、兼容、安全、Contract、Schema/Migration、Validation Matrix、时间、日志或注释规范。详细方法位于 `references/`。

## 1. 规则事实源

### 同仓存在 Coding

如果存在 `.agents/skills/coding/SKILL.md`，正式 Review 前必须读取，并把它及本任务触发 references 作为唯一研发规范源。Review 只增加：独立重建要求、重新判断风险、测试充分性审计、Findings 严重度与证据、三种权限模式和 re-review。

Coding 存在但无法读取时必须报告阻塞，不得宣称已经按 Coding 规范完成 Review。

### 同仓没有 Coding

依据：系统/用户指令 → AGENTS/CONTRIBUTING/项目本地规范 → 当前需求/Spec/Contract/Schema/代码/测试/locks/CI → Review 方法。不得发明不存在的 Coding 规则。

### 与 Docs

Review 发现文档缺陷时：只读模式作为 Finding；已授权修文档且有 Docs Skill 时按 Docs；Docs 发现实现问题仍返回 Coding。

## 2. 三种模式

### `review-only`（默认）

允许读取目标代码/diff/PR/需求/测试/配置/CI 和必要事实源，运行已授权的非破坏性验证，输出 Findings、风险、测试缺口和未验证项。

不自动获得生产代码修改、永久测试新增、文档修改、commit/push/PR/merge/release/deploy 权限。

### `review-and-test`

已有测试修改授权时，可为已确认风险增加最小长期验证/回归测试。新增测试不能降低门禁、绕过真实依赖或用 Mock 冒充未运行边界。测试暴露生产缺陷时停止在 Review 模式改实现，转入 Coding 修复链。

### `review-and-fix`

只有已明确授权修复实现时：

```text
先完成 Review 并形成 Finding
→ 建立/确认失败证据
→ 返回 Coding
→ 重新读取 Coding
→ 按 Coding 完整门禁修复
→ 取得新鲜 Green
→ 回到 Review re-review
```

## 3. Review Target

开始前明确：PR/MR、branch vs base diff、commit range、working tree、module/file、已实现功能、测试充分性审计或全局质量/安全审计。

至少记录：

```text
Review Target
Base / Head
授权模式
上游需求/变更/Spec
项目形态与真实工具链
风险等级与影响边界
触发的 Coding references（若有）
允许执行的测试/外部动作
```

不能只看一个文件推断整个调用链，也不能默认 PR 描述等于完整需求。

## 4. 独立重建

复杂 Review 做两个方向：

```text
A1 上游要求 → 当前变更/实现
A2 当前变更/实现 → 测试/文档/运行证据
```

不把 PR 描述、Change checkbox、作者说明或 CI 全绿当需求全集；从用户决定、正式 Spec/Roadmap/Contract/Schema 和当前机器事实重建预期；从入口向下追调用链，也从 user/consumer 结果反向追能力。

## 5. 测试专家审查

读取 [03_测试专家审查方法.md](references/03_测试专家审查方法.md)。核心不是问“有没有测试”，而是：

```text
需求有哪些可观察行为？
最高风险失败模式是什么？
现有测试分别证明哪些真实边界？
哪些风险没有证据？
最小增加哪一层验证最能证伪关键假设？
```

对真实 Web/UI/API/Persistence/Generated Contract/跨组件/External Provider 边界，分别区分 UI/Client Mock Acceptance、Backend/API/Persistence Integration、Contract/Generated Consumer、Real Cross-component Golden Path、External Dependency/Provider Probe。CLI/Library/Mobile/Embedded/IaC 没有这些边界时不制造它们。

## 6. Findings

读取 [02_Findings与严重度.md](references/02_Findings与严重度.md)。每个确定 Finding 至少说明：严重度、位置/影响范围、问题、触发条件、实际影响、证据、测试缺口、修复方向、验证建议。

没有足够证据时写成风险/待验证假设，不伪装成确定 Bug。纯风格偏好只有项目已有明确规范或形成实际维护风险时才成为 Finding。

## 7. 执行顺序

读取 [01_审查执行流程.md](references/01_审查执行流程.md)：

```text
1. 恢复规则与 Review Target
2. 读取 diff 及直接调用链
3. 独立重建上游要求
4. 识别高风险不变量/失败模式
5. 审查现有测试与证据等级
6. 运行最少充分验证
7. 形成 Findings
8. 复查误报和证据边界
9. 按模式报告/补测试/返回 Coding 修复
10. 修复后 re-review
```

Review 优先找高影响问题，不以 Finding 数量衡量质量。

## 8. 证据边界

必须区分已确认事实、证据支持 Finding、合理未验证风险、未执行验证。

禁止：只看代码声称测试通过；用旧 CI 冒充当前 HEAD；用 Mock/Fake 冒充真实 Persistence/Runtime/External；用单条 Golden Path 声称所有状态；用 External Probe 替代稳定回归；因 CI 绿跳过 Requirement Completeness；为完成感引入无关重构/依赖/测试框架。

## 9. 完成输出

至少给：Review Target/Base/Head、模式与授权、关键事实源、Findings、测试充分性结论、实际验证与证据等级、未验证项、是否阻塞合并/发布；如果修复，再给 Coding 修复摘要和 re-review 结果。

没有 Finding 时也不能只写 `LGTM`，要说明范围、证据和未覆盖边界。
