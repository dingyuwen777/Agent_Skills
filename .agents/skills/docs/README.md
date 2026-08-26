# Docs Skill 使用说明

`docs` 解决：**怎样让技术文档与当前正确事实保持一致，同时让读者真正理解为什么这样设计、数据/调用/状态怎么流、实现在哪里。**

它不是 Markdown 美化器，也不是固定模板生成器。正式规则以 [`SKILL.md`](SKILL.md) 和 [`references/`](references/) 为准。

## 1. 什么时候使用

- 检查 README、Architecture、API Guide、运维/调试文档是否过期；
- 只做文档 Review；
- Review 后修正文档；
- 新写模块 README；
- 更新架构/API/调试/部署说明；
- 检查术语堆叠、因果缺失或基础读者难以理解；
- 检查是否复制完整 Schema/API/generated artifact 形成第二套事实；
- Coding 行为变化后的 Docs Impact 同步。

主要任务是实现、Bug、重构、PR/CI/Release 时用 Coding；主要任务是 Code Review 时用 Review。

## 2. 文档先回答什么

```text
为什么存在？
解决什么问题？
不解决什么？
输入和输出是什么？
数据、请求、事件、控制或状态怎么流？
当前实现在哪里？
关键边界和限制是什么？
怎么使用、验证或排障？
精确机器事实去哪里看？
```

然后再解释术语。

例如，不要只写“系统使用 Canonical Model”。更好的通用解释是：不同来源/协议的原始结构不一致，如果下游每个模块都分别理解这些格式，会产生重复耦合，因此先转换为统一内部结构；确认机制后再解释项目实际使用的命名。

## 3. 三种模式

### Review Only

只审查，不修改。检查事实正确性、关键遗漏、因果链、术语、第二套事实、历史流水账、路径/命令/链接、待实现能力误写等。

### Review + Fix

先完成 Review，再只修确认有问题且在授权范围内的文档。发现实现 Bug 时输出 `code_issue_detected` 并返回 Coding，不让文档追随错误实现。

### Write / Update

先确定目标读者、读者任务、事实源和不应复制的机器事实，再组织文档，不先套巨大固定模板。

## 4. Docs Impact

- `not_applicable`：当前变化不改变人类需要理解/使用/维护/部署/排障的事实；必须给具体依据；
- `targeted`：默认有影响模式，只读受影响事实源、直接消费者和承担该事实的文档；
- `full`：仅核心架构、主调用链、多模块 Contract、部署/恢复模型或文档治理本身发生广泛变化时使用；`full` 是完整覆盖受影响文档域，不是扫描所有 Markdown。

## 5. 避免第二套事实

已有 OpenAPI/JSON Schema/IDL、数据库 Schema/Migration、generated client、lock、完整函数签名/枚举等机器事实时，文档主要解释目的、语义、边界、用法和事实源位置，不手工复制一套需要双维护的镜像。

## 6. 与 Coding 协作

```text
Coding
→ Docs Impact
→ not_applicable：记录依据并结束
→ targeted/full：读取 Docs

Docs
→ 恢复正确事实
→ Review / Fix / Write
→ code_issue_detected：返回 Coding

Coding 修复并新鲜验证
→ Docs targeted re-review
```

如果项目本地规则要求所有仓库任务先经过 Coding 的事实/风险/Git 路由，先遵守项目 Overlay；这不表示 Coding 代替 Docs 写文档。

## 7. 常用请求

```text
使用 docs 检查当前技术文档和真实实现是否一致，只 Review 不修改。
```

```text
使用 docs targeted 检查并修正受这个功能影响的文档，只读取直接相关事实源和文档。
```

```text
使用 docs 做 full 文档审计，但先界定受影响文档域；检查核心架构、主调用链、模块 README 和相关运维说明，不机械扫描所有 Markdown。
```

```text
使用 docs 为这个模块补 README。面向第一次接手项目的人，解释职责、边界、输入输出、主要流动、实现位置、使用/调试方式和限制。
```
