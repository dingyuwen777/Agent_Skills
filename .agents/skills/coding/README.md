# Coding Skill 使用说明

`coding` 用来把软件研发请求变成**基于当前事实、可追溯、可验证、可正常交付**的结果。它不绑定某个语言、框架、数据库或项目阶段。

正式规则以 [`SKILL.md`](SKILL.md) 和命中的 [`references/`](references/) 为准；本 README 只解释如何使用。

## 1. 什么时候用

- Greenfield / 新项目工程基线；
- 第一次接手既有仓库；
- 需求分析和技术方案；
- 功能开发；
- Bug / 故障诊断和修复；
- 重构、性能和可维护性修改；
- Code Review / Audit 前的仓库事实和风险入口；
- API/数据/前后端/Worker/CLI/Library/设备等跨边界集成；
- PR、CI、合并和交付；
- Release、部署、回滚；
- 依赖/Runtime Migration；
- 安全和不可逆数据操作。

## 2. 为什么不能直接开始改代码

同一句“改一个字段”可能是：

```text
内部变量改名
→ L1

public API 字段改名
→ 兼容风险，至少 L2/L3

持久化 Schema 字段改名
→ Migration、历史数据、部署和回滚，通常 L3
```

所以先判断：项目形态、研发阶段、真实语言/工具链、L1-L3 风险、影响边界和授权。

## 3. Greenfield

空仓库/新项目没有可恢复的技术事实。Coding 会先确认目标、约束、成功标准、非目标、数据/安全/部署边界，再对真正影响长期结果的技术选择做方案比较；关键决定闭环后只建立最小工程基线，不一次性引入未来可能用不到的技术。

## 4. 既有仓库

正常顺序：

```text
项目本地 AGENTS/CONTRIBUTING
→ Coding 四维路由
→ 读取最少充分代码 / Contract / Schema/Migration / 配置 / 测试 / 文档
→ 实现/调试
→ Validation Matrix
→ Docs Impact
→ Completion Audit
→ Review
→ PR / CI / Delivery
```

不要因为已经读过旧聊天、旧 Change 或旧文档就跳过当前事实恢复。

## 5. L1/L2/L3

- `L1`：行为不变机械修改或极小隔离修复；
- `L2`：新功能、行为变化、重要 Bug、多文件修改、多人并行或需要正式追踪；
- `L3`：public API/ABI/CLI/格式、Schema/Migration、跨模块 Contract、架构、认证授权、安全、部署恢复、重大依赖或破坏性兼容变化。

## 6. Change

当前 Coding 自带 schema：`coding-change/v1`。不兼容历史 schema。

Requirement Traceability、Validation Matrix、Completion Audit 是通用语义；目录不是所有项目的固定架构。项目已有正式治理时优先复用；需要 Coding 自带载体时默认 `.agents/changes/`，已有受支持顶层 `changes/` 时可沿用。

```bash
python .agents/skills/coding/scripts/coding.py new-change --help
python .agents/skills/coding/scripts/coding.py status --root .
python .agents/skills/coding/scripts/coding.py conflicts --root . --json
python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

## 7. 本地项目导航缓存

```text
.agents/project-context.json
```

这是本地可失效缓存，**不提交 Git**。它只帮助找到事实源，不替代真实文件。

```bash
python .agents/skills/coding/scripts/coding.py discover --root .
```

只读任务没有写入授权时不创建缓存。

## 8. Review / Docs

安装 Review 时：显式 Review/Audit 会在 Coding 恢复事实后进入 Review；实现任务完成前也会进入独立 Review。

安装 Docs 时：Coding 先做 Docs Impact；无影响记录依据，有影响时由 Docs 选择 targeted/full。Docs 确认实现 Bug 时返回 Coding 修复，再做 targeted re-review。

## 9. 五项全局工程硬规则

- 代码注释统一使用中文；
- 所有新增或修改函数，包括 internal/private/helper，都要有函数级中文说明；
- Git 提交信息使用中文；
- Agent 自有时间使用 `Asia/Shanghai`；
- 人类可读日志统一使用 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`，除非更高优先级外部 wire-format Contract 强制其他序列化。

这些规则是 Coding Skill 自身的跨项目约束，不属于某个业务项目残留。

## 10. 常用请求

### 功能开发

```text
使用 coding，基于当前仓库真实实现完成这个功能。
先读取项目规则和事实，判断 L1-L3；按适用 TDD、Validation Matrix、Docs Impact、Completion Audit 和 Review 完成开发与验证。
```

### Bug

```text
使用 coding 修复这个问题。
先稳定复现和定位根因，不猜修复；确认根因后建立回归失败证据，做最小修复并重新验证原始症状和相关回归。
```

### 只做方案

```text
使用 coding 基于当前仓库给落地方案，只分析和设计，不修改代码、分支或 PR。
先确认真实模块边界、Contract、Schema、依赖和测试。
```

### Greenfield

```text
使用 coding 按 Greenfield / Repository Bootstrap 模式建立项目。
先闭环目标、约束、成功标准和关键技术决策，再建立最小工程基线，不预设语言、框架或数据库。
```
