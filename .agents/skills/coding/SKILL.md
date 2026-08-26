---
name: coding
description: 面向不同项目形态、研发阶段和编程语言的可靠软件研发工作流。先恢复仓库当前事实，再按项目形态、研发阶段/任务类型、编程语言/工具链和风险等级 L1-L3 组合路由；依据真实 Contract、Schema、数据、模块边界和项目规则执行需求设计、功能开发、Bug 修复、重构、Review、CI、Git 与交付验证。保留本地可失效项目导航、Change/Requirement Traceability、Completion Audit、Red-Green-Refactor、根因调试、分层验证、多人协作和新鲜证据门禁。Use for greenfield bootstrap, repository onboarding, planning, implementation, debugging, refactoring, review, verified delivery, release work, and parallel human or agent coding across languages and project types.
---

# Coding

把自然语言研发请求转化为一个可追溯、可验证的交付闭环：

```text
恢复当前仓库事实 / Greenfield 约束
→ 四维任务路由
→ 明确需求与风险
→ 选择最少但充分的流程和证据
→ 最小兼容实现
→ 新鲜验证
→ Completion Audit / Review
→ 只交付证据真正支持的结论
```

本 Skill 不是 Python、Web、Backend、PostgreSQL 或任何固定框架专用流程。它的固定部分是“怎样可靠研发”；具体语言、Runtime、Compiler、框架、数据库、目录、包管理器、CI、Release 和部署方式必须来自当前项目事实，Greenfield 项目则来自本轮已经确认的上游决定。

详细规则分布在 `references/`。**命中触发条件时，对应 reference 是本 Skill 的规范组成部分，必须在执行相关动作前读取；不能只读主文件后凭印象补流程。**

`references/` 使用两位数字前缀表达研发流程阅读顺序。编号只用于导航，不代表固定文档数量或固定编号上限。每个任务只读取命中的最少充分规则，不机械通读全部 reference。

**内容守恒优先于篇幅精简。** 对 Skill、reference、模板、脚本或项目 Overlay 做重组、通用化、拆分、合并、改名或精简时，只允许改变组织方式，不允许降低仍有效的规则语义、触发条件、例外、失败处理、停止条件、验证责任、安全边界或兼容要求。不能把多条带条件/例外/失败处理的可执行规则压成一句抽象原则；无法证明完全等价时保留原细节。

## 0. 强制执行模型：先路由，再工作

每个独立任务在制定实现计划前先按 [02_跨项目研发任务路由.md](references/02_跨项目研发任务路由.md) 建立四维路由：

```text
项目形态
× 研发阶段 / 任务类型
× 编程语言 / 工具链
× 风险等级 L1 / L2 / L3
→ 本次必须读取的 references
→ 本次 Validation Matrix
→ 本次 Change / Review / Git 门禁
```

至少回答：

```text
执行模式是什么？
项目实际是什么形态？
当前是 Greenfield、既有仓库开发、Review、Release 还是其他阶段？
使用什么真实语言、Runtime/Compiler、Manifest、锁文件、构建与测试工具？
任务风险是 L1、L2 还是 L3？
会影响哪些模块、接口、数据、配置、用户行为、运行时或外部依赖？
哪些验证维度 required，哪些有事实依据地 not_applicable？
用户授权了哪些文件、Git / PR / Release / 外部环境动作？
```

不要根据文件扩展名、个人经验或“常见最佳实践”反推项目：

```text
package.json ≠ npm ≠ React ≠ Browser test
pyproject.toml ≠ uv ≠ FastAPI ≠ PostgreSQL
Cargo.toml ≠ Web Service
CMakeLists.txt ≠ Linux-only
```

继续读取项目规则、版本文件、Manifest/lock、workspace、CI、真实代码和调用链后再判断。

## 1. 跨项目不变量

1. **上位规则优先。** 先遵守系统、开发者、用户以及目标路径适用的 `AGENTS.md`、`CONTRIBUTING` 或同等仓库规则。本 Skill 不能降低更高优先级约束；项目本地规则是通用 Skill 的 Overlay。
2. **当前事实优先。** 既有仓库以当前文件、运行结果和用户已确认决定为事实；缓存只作导航，不作事实副本。Greenfield 项目没有仓库事实时必须明确“尚未建立”，不能用个人习惯伪装成既有设计。
3. **权限边界明确。** 只在明确授权范围内写文件或执行外部动作。分析、Review、审计或答疑不自动授权创建缓存、Change、分支、提交、PR、合并、部署或生产写入。
4. **保护用户工作。** 保留用户未提交修改；禁止覆盖式检出、强推、破坏性清理、未授权历史重写和把无关用户改动混入本任务。
5. **不静默扩大变化。** 不擅自升级依赖/Runtime、切换包管理器或框架、改 public API/ABI/格式、改变数据语义、扩大范围或进行无关重构。
6. **完成结论必须有本轮新鲜证据。** 没有实际执行的验证证据，不得宣称完成、修复、通过、可合并、可发布或可部署。
7. **从目标和根因推导机制。** 从可观察目标、硬约束、当前事实和根因选择最小充分方案；“最佳实践”只是候选证据，不能覆盖仓库事实或成为引入复杂度的理由。
8. **不发明项目事实。** 只执行仓库真实存在或本次明确建立的边界、Contract、Schema、Owner、Migration、测试和发布机制。经有界调查未发现时标记不适用；任务确实需要新建时按设计门禁建立，不把模板当成已有事实。
9. **独立能力建立独立验证闭环。** 对具有明确输入输出、独立业务价值、独立失败边界，或无需启动完整系统即可验证的能力，优先复用生产入口建立最小验证闭环；不要机械要求“一模块一个测试文件”或“一功能一个测试文档”。
10. **L2/L3 必须向上追溯。** 当前 Change 不是自身需求全集。必须从用户已确认决定和上游正式事实源建立 Requirement Traceability；进入 `ready_for_review` 前重新读取上游完成定义并执行 Completion Audit。CI 全绿不能替代需求完整性审计。
11. **验证按风险而不是固定技术栈分层。** L2/L3 先按 [07_通用验证与证据策略.md](references/07_通用验证与证据策略.md) 建立技术栈无关 Validation Matrix。若真实存在 Web/UI、API/Service、Persistence、Generated Contract、跨组件或外部依赖，再叠加 [08_分层测试与验收策略.md](references/08_分层测试与验收策略.md) 的专项规则；这些细节不强加给 CLI、Library、Mobile、Embedded、IaC 等项目。
12. **中文注释与函数级说明是通用硬规则。** 代码注释统一使用中文；专有名词、标识符、协议、库、标准名和必须保持原样的外部文本可以保留原语言。所有新增或修改的函数——包括 public/exported 与 internal/private/helper——都必须有与复杂度匹配的函数级中文注释或文档注释；简单函数可用一句简短说明，复杂规则还要解释 `why / invariant / risk / compatibility`，禁止逐行翻译语法。
13. **重要功能可观测性匹配现有体系。** 仓库已有 logger/event/telemetry，且功能涉及关键生命周期、异步任务、外部 I/O、重试/部分失败、状态转换或后期排障价值时，补最小充分观测；禁止 Secret/Token/密码/敏感 Raw/PII，禁止 INFO 高频刷屏，日志不能代替正式业务事实。
14. **Git 提交信息统一中文。** 所有 Git 提交信息使用中文；命令、路径、标识符、版本号等必要技术内容可以保留原文。项目可以增加格式/前缀，但不能取消中文要求。
15. **所有 Agent 自有时间默认采用北京时间。** Agent 新建或默认解释的时间戳、日期、缓存、Change 元数据、报告、脚本默认时间和用户可见时间统一使用 `Asia/Shanghai`（UTC+8）。外部协议、原始数据或既有机器 Contract 明确其他时区时保持原始语义，只在展示/人类日志边界明确转换。
16. **人类可读日志前缀统一且可定位。** 除非更高优先级外部 wire-format Contract 强制其他序列化形式，人类可读日志统一使用 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`；时间为北京时间、毫秒三位、source 与 line 来自真实调用点、LEVEL 大写。结构化日志必须提供等价的北京时间、source、line、level 字段。

## 2. 四维任务路由

### 2.1 项目形态

从真实项目选择一个或多个：

- Library / SDK；
- CLI / Developer Tool；
- Service / Backend / API；
- Frontend / Web UI；
- Full-stack Application；
- Mobile / Desktop；
- Data / Batch / ETL / ML；
- Embedded / Systems；
- Infra / IaC / Build / Release Tooling；
- Monorepo / Polyglot；
- Documentation / Configuration / Migration-only 当前任务。

### 2.2 研发阶段 / 任务类型

先确定主阶段：

- Greenfield / Repository Bootstrap / Initial Architecture；
- Repository Onboarding / Fact Recovery；
- Requirement / Design / Technical Decision；
- Feature / Behavior Implementation；
- Bug / Failure / Incident Diagnosis；
- Refactor / Performance / Maintainability；
- Code Review / Audit；
- Integration / PR / Release / Delivery；
- Maintenance / Dependency / Runtime Migration；
- Security / Permission / Irreversible Data Operation；
- Prototype / Spike / Feasibility（明确非生产边界）。

同一任务可以跨相邻阶段，但不能为赶进度跳过上游门禁。

### 2.3 编程语言 / 工具链

读取 [03_编程语言与工具链适配规则.md](references/03_编程语言与工具链适配规则.md)。Profile 只负责导航：

```text
版本事实
→ Manifest / Workspace
→ 锁文件 / Dependency policy
→ Build / Test / Lint / Format / Static analysis
→ Package / Artifact / Runtime
→ CI / Release
```

不得因为 profile 提供示例命令就跳过仓库实际命令调查，也不得擅自升级或更换工具链。未列语言使用同一发现算法。

### 2.4 风险等级

使用最低但充分的等级；发现隐藏复杂度时升级，不静默降级。

| 等级 | 适用范围 | 正式追踪 | 设计门禁 |
| --- | --- | --- | --- |
| L1 | 行为不变机械修改，或边界明确、影响隔离的极小修复 | 通常不需要 Coding Change | 简短计划后执行，仍需验证 |
| L2 | 新功能、行为变化、重要 Bug、多文件修改、多人并行或需要追踪 | 使用项目既有治理或 Coding Change | 明确目标、成功标准、范围、非目标、不变项、验证 |
| L3 | public API/ABI、Schema/Migration、跨模块 Contract、架构、认证授权、安全、部署恢复、重大依赖或破坏性兼容变化 | 使用项目既有治理或 Coding Change | 比较 2–3 个真实方案；关键上游决策确认后实现 |

公共配置字段、CLI flag、序列化格式、数据库列、权限语义、不可逆数据操作即使只改几行也可能是 L2/L3。

## 3. 按触发条件读取资源

| 触发条件 | 必须读取 |
| --- | --- |
| 首次进入既有仓库、缓存缺失或可能过期 | [01_项目发现与可失效缓存.md](references/01_项目发现与可失效缓存.md) |
| Greenfield 或需要识别项目形态/研发阶段/组合流程 | [02_跨项目研发任务路由.md](references/02_跨项目研发任务路由.md) |
| 需要确认语言、Runtime、Manifest、锁文件、构建、下载源或包管理 | [03_编程语言与工具链适配规则.md](references/03_编程语言与工具链适配规则.md) |
| L2/L3、需要需求追踪或已有正式变更记录 | [04_轻量变更管理.md](references/04_轻量变更管理.md) |
| 当前变更使用 Completion Gate | [10_完成定义追溯门禁.md](references/10_完成定义追溯门禁.md) |
| Feature、Bug、重构、性能、失败调查 | [05_设计实施与根因调试.md](references/05_设计实施与根因调试.md) |
| 规划或审计验证证据、永久 CI/Workflow | [07_通用验证与证据策略.md](references/07_通用验证与证据策略.md) |
| Web/UI、API/Service、Persistence、Generated Contract、Full-stack、External Provider 等专项边界真实存在 | [08_分层测试与验收策略.md](references/08_分层测试与验收策略.md) |
| 跨模块、跨消费者、Contract/Schema/Migration/Owner/数据边界 | [06_仓库边界数据交换与条件式约束.md](references/06_仓库边界数据交换与条件式约束.md) |
| 多人、多 Agent、多个分支或并行变更 | [09_多人和多智能体并行协作.md](references/09_多人和多智能体并行协作.md) |
| Review、Ready、交付或准备表达完成结论 | [11_两阶段复核与完成前验证.md](references/11_两阶段复核与完成前验证.md) |

不要要求用户重复提供能从仓库、缓存或工具确认的信息；只读取当前任务真正需要的事实和 reference。

## 4. 统一工作流

### 4.1 建立权限和宿主能力边界

先判断：

```text
只读分析 / 诊断 / 方案 / 实现 / Review / Git / Release / 运维
```

确认宿主是否具有持久文件系统、终端、目标语言工具链、Git、测试环境、数据库/容器/device、CI、外部服务和多 Agent 能力。

- 无持久文件系统：不能承诺跨会话缓存或 Git 协作记录；
- 不能执行脚本/测试：按人工流程继续，明确未验证项；
- 用户未授权写项目：只在会话内建立临时导航，不创建缓存/Change/分支；
- 外部系统/生产环境无授权：只读调查或使用已批准 sandbox/fake，不执行真实写入。

### 4.2 Greenfield / Bootstrap

Greenfield 不存在可恢复的仓库事实时，不能把“按当前仓库实现”变成空话。先明确：

```text
目标与目标用户
成功标准
范围 / 非目标
硬约束
数据/安全/合规/兼容要求
运行环境和部署约束
预算/性能/SLO（确实存在时）
必须保持的外部协议或已有资产
```

然后：

1. 区分用户已决定、可从外部一手资料验证、仍需业务 Owner 决策的事项；
2. 只对会改变接口、数据、兼容、部署、长期维护或验收的上游选择提出决策；
3. 复杂选择至少比较保留最小方案在内的 2–3 个真实方案；
4. 关键决定闭环后建立最小工程基线：版本、Manifest/lock、目录、测试、构建和必要 CI；
5. 不一次性引入未来可能用不到的数据库、消息系统、微服务、插件层、兼容层或发布机制；
6. 基线建立后立即回到正常事实优先流程。

Prototype/Spike 必须标清非生产、临时放宽项、不能放宽的安全/数据边界、退出判据和生产化前需要补齐的验证。

### 4.3 既有仓库定位与事实恢复

定位真实仓库根。先读从 root 到目标路径适用的规则，再检查：

- branch、HEAD、worktree、未提交/未跟踪修改；
- README / Requirements / Architecture；
- Manifest / Runtime version / Lock；
- Build / Test / CI；
- Config；
- Contract / Schema / Migration；
- 入口、调用链、数据流、错误处理；
- generated artifact；
- 模块 Owner / public boundary；
- 相关历史变更。

绝不覆盖、回滚、格式化或混入无关用户修改。

### 4.4 本地可失效项目导航

缓存路径：

```text
.agents/project-context.json
```

它是**本地 disposable cache，不提交 Git**。目标项目应将其加入 `.gitignore`。

实现任务在项目写入已授权且终端/Python 可用时可运行：

```text
python <skill>/scripts/coding.py discover --root <repo>
```

- `cache_hit`：候选事实源未出现可见失效信号；仍需读取本次需求、目标实现和测试；
- `created/refreshed`：检查索引发现的规则、需求、架构、Contract、Migration、配置、依赖和测试入口；
- 脚本失败：保留原错误，按 [01](references/01_项目发现与可失效缓存.md) 人工流程继续。

缓存只保存路径、分类、轻量指纹和少量可直接提取信息；不复制需求正文。`generated_at` 使用带 `+08:00` 偏移的北京时间。

只读任务未经写入授权时不创建或刷新缓存。

### 4.5 变更治理与 Change Carrier

L2/L3 的 Requirement Traceability、Validation Matrix、Completion Audit 是通用语义，但**不是所有项目都必须新增同一目录**。

先读取 [04_轻量变更管理.md](references/04_轻量变更管理.md)：

1. 项目已有能够承载这些语义的正式 Change/RFC/Spec/OpenSpec/Issue 流程：优先复用；
2. Coding CLI 只理解 `coding-change/v1`，不擅自改写未知第三方格式；
3. 使用 Coding 自带载体时默认 `.agents/changes/`；
4. 目标项目已使用受支持的顶层 `changes/active` / `changes/archive` 时可继续沿用；
5. 发现既有治理但无法无损映射时，不静默新建平行治理；先明确 carrier 或使用项目原生门禁。

Coding CLI 可显式指定：

```text
--change-root <repo-relative-path>
```

当前 schema 只有：

```text
coding-change/v1
```

不读取、不迁移、不兼容旧 schema。

### 4.6 L1/L2/L3 任务契约

编码前明确：

```text
背景与当前事实
目标
可观察成功标准
范围
非目标
必须保持不变
输入 / 输出
影响边界
复用点
预计文件
兼容性
数据 / Migration
依赖
验证
文档
部署 / 回滚（适用时）
Git 授权
```

L1 可在工作说明内维护。L2/L3 使用项目选定的治理载体。

### 4.7 真正需要用户/Owner 决策的事项

只有仓库/正式资料/一手事实无法确认且会实质改变以下内容时才提请决策：

- 业务语义和用户验收；
- public API/ABI/CLI/文件格式/Contract；
- Schema/Migration/数据保留删除；
- 权限/认证/隐私/安全；
- 外部 Provider operation/费用；
- 调度/SLO/RPO/RTO；
- 破坏性兼容；
- 不可逆操作；
- 重大技术路线。

顺序：

```text
先查仓库事实和必要一手资料
→ 给明确推荐
→ 有实质取舍时列 2–3 个真实方案和影响
→ 只问最上游的一个问题
→ 用户/业务 Owner 决策
→ 同步正式事实源和变更记录
```

已经固化的决定不重复问。

### 4.8 可验证计划

每一步：

```text
[步骤]
→ 修改范围：[文件 / 模块]
→ 预期结果：[可观察行为 / Contract]
→ 依赖：[前置事实或步骤]
→ 验证方式：[实际命令 / 检查]
```

实现前明确：

- 复用现有实现/模式；
- 新增/修改每个函数需要的函数级中文说明；
- 复杂规则的定点中文注释；
- 日志/事件观测点与统一人类日志格式；
- 最小失败测试或明确 TDD 例外；
- 各独立失败边界需要哪类证据；
- 目标测试、相关测试、静态检查、构建、运行和发布验证；
- 哪些步骤真正可以并行。

只并行互不依赖且不修改同一文件、接口、Schema、lock 或共享状态的任务。

### 4.9 Validation Matrix

L2/L3 使用 [07](references/07_通用验证与证据策略.md)：

```text
行为 / Unit / Component
接口 / Contract
集成 / Persistence / Runtime Dependency
用户 / Workflow Acceptance
跨组件 Golden Path
外部依赖 Probe
Build / Package / Runtime
Docs / Governance / Other
```

每层只写 `required` 或 `not_applicable`。`required` 必须写 Scope 和当前 Evidence；`not_applicable` 必须写真实依据。

真实存在 Web/UI、API/Service、Persistence/Runtime、Generated Contract、跨组件或 External Provider 时，再读 [08](references/08_分层测试与验收策略.md)。

### 4.10 按研发阶段实施

#### Feature / 行为变化 / Bug / Refactor

读取 [05_设计实施与根因调试.md](references/05_设计实施与根因调试.md)，默认：

```text
Red
→ Verify Red
→ Green
→ Verify Green
→ Refactor
→ Verify Again
```

Bug 必须有回归证据。测试验证真实行为，不只验证 Mock 被调用。

#### 文档 / 纯配置 / 生成物 / 无合理自动 Red

允许 TDD 例外，但必须明确原因和替代验证，例如 parser/schema、link/reference、generated diff、build、dry-run/plan、package/open、实际运行、repository consistency。不要伪造 Red。

#### 失败 / Bug / 性能 / 异常

先根因调查：

```text
完整错误和调用栈
→ 稳定复现
→ 近期变更与环境差异
→ 数据流和组件边界
→ 仓库内正常参照与差异
→ 一个可证伪根因假设
→ 单变量最小实验
→ 失败回归用例
→ 单一修复
```

连续三次修复假设失败时停止叠补丁，重新审视架构、前提和观测手段并报告阻塞。

#### 最小、精准、兼容

- 只写当前需求最少代码；
- 标准库和现有依赖优先；
- 不增加未要求功能、CLI、配置、兼容层、抽象或未来占位；
- 不顺手重构、改名、格式化无关文件；
- 每处 diff 可追溯到需求或验证；
- 删除只因本次修改而失效的内容；
- 默认保持 public API/ABI/import/CLI/config/default/env/data/file/persistence/startup/error compatibility；
- breaking change 必须先设计版本、Migration、兼容期、部署、回滚和验证。

#### 注释、时间与日志

所有新增或修改函数必须有函数级中文注释/文档注释；复杂逻辑补 `why/invariant/risk/compatibility`。Agent 自有时间使用 `Asia/Shanghai`。人类可读日志使用 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`，除非更高优先级外部 wire-format Contract 强制其他序列化；结构化日志提供等价字段。

### 4.11 跨模块、Contract、Schema 与数据边界

任务跨模块、跨消费者、接口/事件/数据，或仓库已有明确 Owner/Contract/Schema/Migration 时读取 [06](references/06_仓库边界数据交换与条件式约束.md)。

只在仓库真实存在的边界上：

- 找生产者/消费者；
- 找 public Contract；
- 找数据/写 Owner；
- 找 Migration/兼容机制；
- 找契约/集成测试；
- 评估 generated artifact；
- 评估部署/回滚。

未发现时不发明 Interface/Facade/Factory/BaseRepository、第二套 Client、第二套 Schema 或平行数据源。

### 4.12 同步当前事实和文档

代码变化后检查：

```text
README / Architecture / ADR / Spec
API / Contract / Schema / Migration
generated artifact
config / env example
build / startup / deploy
module responsibility / call chain
logging / security / operations
debug / testing instructions
user-visible behavior
roadmap / release state（项目实际维护时）
```

文档与实现冲突时先判断正确事实来源。正式文档描述现在是什么；Change/ADR/Git 保存为什么变。未实现功能不能写成当前已支持。

#### Docs Skill 路由

如果存在 `.agents/skills/docs/SKILL.md`：

- 无文档影响：记录 `Docs Impact: not_applicable` 与具体依据，不加载无关文档；
- 有影响或任务本身是文档 Review/编写/更新：读取 Docs，由 Docs 选择 `targeted`（默认）或 `full`；
- Docs 报告 `code_issue_detected`：返回 Coding 完整流程修实现，取得新鲜验证后再做 Docs targeted re-review。

没有 Docs Skill 时仍执行 Coding 自己的文档影响判断和同步。

### 4.13 Completion Audit、两阶段 Review 与新鲜验证

使用 Completion Gate 的 L2/L3 变更，在 `ready_for_review` 前：

```text
重新读取上游正式事实源
→ 不看当前变更 checklist，独立重建完成定义
→ 比较“上游要求 → 当前变更”查 requirement omission
→ 比较“当前变更 → 实现 / 测试 / 文档”
→ 执行适用的反向能力审计
→ 复核 Validation Matrix 的层级与证据等级
→ 清零 not_satisfied
```

反向审计按真实边界选择：

- public API → consumer；
- CLI command → handler/output/exit；
- backend capability → UI/consumer entry；
- producer → event → consumer；
- schema → migration → reader/writer；
- package API → downstream consumer；
- deployment config → runtime startup/health。

使用 Coding Change 时机器门禁：

```text
python <skill>/scripts/ready_check.py --root <repo> --require-active-ready
```

必要时加 `--change-root`。机器门禁只验证可机器判断的结构、状态、Source、占位符和 Audit checkbox，不能证明业务语义完整或 Validation Matrix 充分。

完成 Audit 后读取 [11](references/11_两阶段复核与完成前验证.md)：

```text
上游 Requirement Completeness Review
→ 当前变更/Spec 需求符合性
→ 实现和测试证据
→ Code Quality / 安全 / 兼容 / 可维护性 / 无关改动
```

每个完成结论都重新执行能证明它的命令/检查，并读取完整输出、退出码和失败数量。

## 5. 多 Agent / 多人协作

只有互不依赖且不修改同一文件、接口、Schema、lock 或共享状态的工作才并行。派发时给最少充分上下文：目标、范围、事实源、禁止项、验收和输出格式。

主 Agent 必须复核子任务实际 diff、当前 HEAD/变更冲突、测试是否真的运行、证据范围是否被夸大以及是否混入无关改动。详细见 [09](references/09_多人和多智能体并行协作.md)。

## 6. Git、依赖与安全

### Git

- 修改前检查 branch、worktree、未提交修改；
- 不覆盖用户改动；
- 禁止 `git reset --hard`、`git clean -fd`、强制推送、未授权共享历史重写；
- 未经授权不创建分支、提交、推送、PR、合并、部署、删分支；
- CI 失败、冲突、保护规则或结果未确认时不强行推进；
- 所有 Git 提交信息使用中文。

### 依赖

- 先确认语言、Runtime、包管理器、Manifest、lock 和实际版本；
- 优先标准库和现有依赖；
- 普通功能不顺手升级；
- 新依赖说明必要性、维护、许可证、体积/构建影响和替代方案；
- Manifest 改动同步正式 lock；
- 不删除 lock、切换包管理器或解析 `latest` 掩盖问题。

### 安全

- 不硬编码、打印、提交或上传 Secret/Token/密码；
- 不关闭认证、授权、证书、输入校验或既有安全门禁制造“通过”；
- 避免不安全反序列化、任意命令/动态代码执行、字符串拼接 SQL；
- 按任务风险校验路径、文件、网络、数据库、命令、模板、归档和用户输入；
- 外部服务、生产数据、真实环境写入必须受明确权限和数据边界约束。

## 7. Review Skill 集成

如果存在 `.agents/skills/review/SKILL.md`：

- 显式 Code Review / Audit：Coding 完成事实恢复、四维路由、风险/工具链/权限确认后立即进入 Review；
- 任何 Coding 实现任务：实现、目标验证和 Docs Impact 闭环后，完成前读取 Review 做独立审查；
- Review 默认只审，不自动获得实现修改授权；
- Review 发现实现缺陷且已授权修复：返回 Coding 完整流程，取得新鲜证据后 re-review；
- Review Skill 存在但无法读取：必须报告阻塞，不得宣称 Review 完成。

没有 Review Skill 时继续执行 Coding 自身 [11](references/11_两阶段复核与完成前验证.md) 的两阶段 Review。

## 8. 网络下载源与永久 Workflow 治理

### 网络下载源感知执行环境

涉及 Runtime/Compiler/SDK、系统包、依赖安装、Docker/OCI build、CI bootstrap、部署/恢复环境准备时必须读取 [03](references/03_编程语言与工具链适配规则.md) 并确认目标执行环境：

- 中国大陆网络且新增/修改下载行为：联网核验当前稳定、可信、生态匹配的国内镜像/代理；候选不是永久白名单；
- GitHub Hosted Runner、海外服务器或其他海外网络：不因为开发者位于中国就机械切国内源；
- 镜像/代理只能改变传输路径，不能静默改变 canonical identity、版本锁、checksum/hash/digest/签名、安全更新或 SBOM/provenance；
- 候选不可验证时使用另一个已验证候选、项目既有可信源或官方 fallback；禁止为下载成功关闭 TLS/GPG/完整性检查。

### 永久 CI/Workflow 优化证据守恒

新增/修改永久 CI、Workflow、测试门禁、构建/发布流水线，或要求精简/加速时必须读取 [07](references/07_通用验证与证据策略.md) 并做 Workflow Responsibility Audit；对应专项边界存在时再读 [08](references/08_分层测试与验收策略.md)。

删除、合并、迁移或大幅收缩永久 Job/Step 前建立：

```text
原证明责任
→ 原位置
→ 新位置
→ 证据等级是否保持
→ 等价/更强依据
```

只有独立失败边界仍由等价或更强证据负责时，才能通过 event/path filter、changed-scope、fast path、安全缓存、artifact reuse、并行、PR/main/release 分责或 Golden Path 收敛降低成本。Workflow 重命名/拆分/合并还要检查 Branch Protection/Ruleset、release gate、脚本和外部平台对 check name 的实时引用。

## 9. 交付报告

最终报告至少包含：

1. 变更摘要与逐文件/按类别目的；
2. 项目形态、研发阶段、语言/工具链和风险等级；
3. 上游 Requirement Traceability 与成功标准状态；
4. Validation Matrix：Scope、实际 Evidence、`not_applicable` 依据；
5. Completion Audit / 两阶段 Review 结果；
6. Contract/API/ABI/Schema/Migration/数据变化；
7. 文档同步及判断依据；
8. 本轮实际执行命令/检查、退出码、通过/失败数量；
9. 未验证内容、阻塞和剩余风险；
10. 兼容性、依赖、Migration、部署和回滚影响；
11. Git 分支、提交、PR、CI、合并和分支清理实际状态。

禁止只回复“已完成”“已修复”或“测试通过”。

## 10. 能力边界

- `project-context.json` 是本地可失效导航缓存，不是向量数据库、长期记忆或需求事实副本，也不提交 Git；
- Coding Change 是可选治理载体，不是原子锁、租约、看板或在线状态服务；
- Completion Gate 是流程完整性门禁，不是自然语言需求证明器；
- Validation Matrix 是风险到证据的语义映射，不是固定测试配额；
- 语言/项目 profile 是发现和验证导航，不授权升级技术栈或重构架构；
- 看不到未提交、未推送、未同步、无权限访问或另一客户端私有状态；
- 宿主不支持持久文件、目标工具链、Git、device、数据库或外部服务时，只执行实际支持的流程并明确降级与未验证风险。
