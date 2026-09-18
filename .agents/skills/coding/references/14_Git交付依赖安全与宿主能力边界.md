<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.15","触发":{"任一":[{"包含":{"维度":"执行模式","取值":["Git","发布"]}},{"包含":{"维度":"意图","取值":["Git 交付","PR Ready","Release","依赖升级","安全与权限"]}},{"包含":{"维度":"能力","取值":["Git"]}}]},"依赖":["coding.reference.03","coding.reference.07","coding.reference.11"]}
-->

# Git、交付、依赖、安全与宿主能力边界

本文件是 Git / PR / Release / Delivery、依赖、安全、交付报告与宿主能力边界的详细 Owner；Coding 主 `SKILL.md` 保留硬触发入口。命中时必须读本文件，不凭导航补流程。

## 1. Git、依赖与安全的通用边界

### Git

- 修改前检查 branch、worktree、未提交修改；
- 不覆盖用户改动；
- 禁止 `git reset --hard`、`git clean -fd`、强制推送、未授权共享历史重写；
- 未经授权不创建分支、提交、推送、PR、合并、部署、删分支；
- CI 失败、冲突、保护规则或结果未确认时不强行推进；
- Git 提交信息必须中文；项目可增格式、前缀或工单号，不得覆盖中文要求；
- 本地 Git 路径可用时，开工顺序：`最新目标分支 → 本地任务分支 → 本地 Change / 失败测试 / 最小治理提交 → 首个本地提交 → 首次 push 创建远程跟踪分支 → 早期 PR`；不得先创建远程空分支。仅有托管平台 API 时按下文语义等价路径执行，不把本地 clone/commit 当作远端写入的固定前置条件。

### 既有本地实现的接管式 PR 交付

当协作者已经在本地完成一批实现，但此前的开发过程**没有完整按当前 Agent_Skills / 项目治理执行**，而当前目标是把这批既有实现按规则提交到远程 PR 时，不要求为了“流程看起来完整”丢弃或从头重写已有代码。应把当前实现视为**尚未完成交付验证的候选实现**，从当前事实重新进入治理与交付门禁。

固定顺序：

1. **先保护现有工作并恢复 Git 事实。** 检查当前 branch/worktree、目标 base、当前 head、已有 commits、未提交修改、完整 diff、与目标分支的 ahead/behind/冲突以及可见 Active Change；区分本任务改动、协作者其他改动和上游新变化。禁止为重新走流程使用 `reset --hard`、`clean`、force push、覆盖式 checkout 或其他破坏用户工作的手段。
2. **从上游事实重新建立预期，不从代码反推需求。** 重新读取项目规则、当前 Requirement Source、相关 Contract/Schema/配置/代码/测试/CI，从这些事实独立重建目标、成功标准、范围、非目标、不变项与风险，再对照当前 diff 判断已有实现实际完成了什么、遗漏了什么、是否包含无关改动。
3. **历史过程只能如实记录，不能倒填。** 如果此前没有真实执行 TDD、Change、Issue、Review、测试或其他证据，就明确它们当时没有发生；不得补写过去日期、伪造旧 Red/Green、把当前新建的治理记录说成开发前已经存在，或用“现在补齐”改写历史事实。
4. **按当前真实触发补治理，不机械补资产。** 重新判断当前风险等级、Requirement Source、Change、Validation Matrix、Docs、Review 和 Git/PR 门禁。只有当前项目规则、风险或交付阶段真实要求时才创建/认领 Issue、Change、测试或其他记录；新建记录描述“既有实现接管后的当前施工与验证”，不证明此前开发过程合规。
5. **把已有实现当作待验证候选，按当前 revision 补最小充分证据。** 优先复用现有测试、parser/check、真实入口和项目已有验证；只有现有 Evidence 无法保护当前真实行为、Contract 或具体回归缺口时才新增最小测试。发现确定问题直接在当前任务范围内修复，再重新验证。
6. **事后回归证据与开发时 TDD 必须区分。** 对 Bug 修复或行为变化，如果可以在不破坏现有工作、不重写共享历史且环境仍可复现的前提下验证修改前 base/revision 上目标测试失败、当前实现上通过，可以记录为 **`base Red → current Green` 的事后回归证据**；这只能证明回归和修复边界，**不能声称原开发过程已经执行 Red → Green TDD**。base 无法安全复现时不要为形式强行切换/重建环境，应记录该历史 Red 未验证，并使用当前可取得的最强直接证据。
7. **对当前 diff 做独立 Review 与文档影响审计。** 从 Requirement Source 和项目事实检查正确性、边界、错误处理、安全/权限、public Contract、数据/兼容、依赖、测试充分性、无关改动和长期文档；Finding 修复后 re-review，不能因为“代码已经写完”降低 Review 强度。
8. **处理目标分支新鲜性，但不默认重写历史。** merge 前仍需面向当前目标分支重新确认 base/head、冲突、required checks 和 reviewed revision；按项目既有策略选择 merge queue、更新分支或其他安全路径，不为了“同步 main”默认 rebase/force push。任何会改变已审 diff 的更新都使相关旧 Review/Evidence 按 Fresh Evidence Contract 重新判定。
9. **PR 必须如实描述接管事实。** PR 说明应明确这是“既有本地实现经过当前 Agent_Skills 接管、需求复核、补充验证和 Review 后的提交”，列出实际执行的验证、未验证项和剩余风险；不得写成“从开发开始就完整遵循了 Agent_Skills”。Requirement-Source、Change、CI 与 Review 继续按各自 Owner 的现行规则关联。
10. **普通协作者止于 PR Ready。** 达到当前项目要求的 PR Ready 后提交给维护者审核；没有额外授权时不自行 merge 主分支、Release、Deploy、生产 Migration/数据动作或删除共享分支。维护者后续 Review/merge 仍执行当前独立门禁，不因“接管式验证”降低标准。

这条路径的目标不是证明**过去的开发过程合规**，而是证明**当前准备提交 PR 的 revision**在现有规则下具备真实、可追溯、足够的新鲜 Evidence。它不改变正常从任务开始就按 Agent_Skills 开发的首选流程，也不把 Issue-first、Change-first 或新增测试变成所有任务的无条件要求。

### Requested Action 与 Effective Authorization

**Requested Action** 是用户请求，**Effective Authorization** 仍须结合项目规则、authenticated principal、当前保护规则/Ruleset 和宿主能力核验；Git 能力存在不授予任务权限。

硬规则：

- 用户请求 merge、Release、Deploy、生产 Migration/数据动作不能提升当前 principal 的真实权限；
- Requested Action 超出 Effective Authorization 时，在安全且已授权范围内完成最大可交付结果，例如开发到 PR Ready，并把未执行动作明确报告为 `BLOCKED_BY_AUTHORIZATION`；
- 不得因为当前连接拥有 Admin token、bypass actor、Bot 或其他技术通路，就把这些能力当作当前任务的治理授权；
- 平台拒绝保护分支更新或 required gate 时停止，不通过换 API、force push 或其他身份绕过；
- 当前权限事实无法可靠确认时，对高权限写动作 fail closed。

### 语义等价能力发现与恢复

**单一路径失败不等于仓库不可写。** 所有模型须先发现宿主等价能力；授权连续性按 Router，不因换路径重复确认。

1. 明确操作目标并保留错误；区分网络/DNS、工具/参数、结果不明、限流、并发与授权/保护/门禁拒绝，不只凭 HTTP 状态判断。
2. 超时、解析/查询错误或断连后先回读 blob/commit/ref、PR/run；已生效不重复，无法消歧只阻塞该写动作。
3. 查当前工具目录、App、终端/Git、已有 CI/Runner。优先稳定入口；失败/保障不足时选语义、原子性、防漂移、审计/验证最完整的可用路径，不升权限/副作用；找到即推进，不遍历试坏。
4. 回读 revision/diff/分支/PR/证据；工具存在非写成功，孤立对象非已推送。

候选非配额：App/Git 读取须保持仓库/ref、canonical 全文/Ownership，禁退安装副本/旧缓存；写入可用本地 Git、当前 blob SHA 守卫的 Contents 或 Git Data API，保持任务分支/精确内容/并发保护；验证可用本地/授权 CI，匹配 revision/命令/依赖/环境/证明范围，读代码不冒充测试。PR/merge 保留下文全部生命周期、授权和门禁。

API 基于核验的 base tree/parent，保留未改文件/mode，先建真实改动 commit 再创建/非强制更新任务分支；不造空分支、覆盖并发提交、直写受保护 main。有原子要求不降级为逐文件半完成；`force=false` 只防非快进，Contents blob SHA 也非分支 CAS/expected-head，需要精确 head guard 时不得降级。

真实授权/保护/Review/CI 拒绝不换 token、actor、API 或强推绕过；限流退避、不轮换规避；参数按当前 schema 修正，不无界重试。路径改变范围、副作用、费用或必要保障先过既有决策/授权门禁。

相关候选均由实际错误、当前 schema/权限或缺失前提证明不满足目标/门禁后，才报告 **capability blocker**：最小受阻动作、候选/排除依据、已完成结果、剩余条件；继续无依赖已授权工作；不做已被事实排除的危险/无效尝试。

### 模式与宿主无关的能力判据

治理读取通道与仓库执行通道分别核验：Source Mode 可通过已授权仓库连接器读取完整 canonical 源码，不要求本地 clone；Runtime 的本地 MCP 只加载同版本规则，不提供或授予 Git 写入。网页、CLI、模型厂商/新旧和工具名称均不能代替当前 schema、实际权限与操作结果。没有本地 shell 只排除依赖该 shell 的路径。

| 已确认事实 | 下一步与停止边界 |
| --- | --- |
| 本地 clone/push 因 DNS 或 transport 失败，App 的 read/commit/ref/PR 可满足同一保障 | 继续核验并使用托管路径；不得要求先恢复本地 Git 才开始 |
| 只有逐文件 Contents 写入，但任务要求多文件原子提交 | 查找同基线 Git Data / 其他原子能力；没有则只阻塞该原子写入，不放宽保障 |
| 写调用超时、响应解析失败或查询失败 | 先读真实 ref/PR/run 判定是否已生效；不得盲重试制造重复提交/PR |
| 当前 PR/push 已能触发正式 CI，宿主没有手动 dispatch | 读取对应 revision 的既有 Run/Job/日志；不把 dispatch 缺失等同于无法验证 |
| 权限/保护拒绝，或缺少当前动作必需的 revision guard | 保持相应 blocker；不改身份、force 或绕过 required gate |

能力发现记录只保留本任务必要的目标、实际能力、所选路径、保障和排除依据，不造新协议或永久工具清单。测试/Runner 只使用目标仓库正式允许的执行入口；不得为弥补宿主缺口擅自新增临时 Workflow、泄露凭据或扩大外部副作用。

### GitHub PR 零人工交付兼容策略

Draft 是平台状态，不是用户必须手工点击的质量门禁；真正门禁仍是项目 Change/需求追溯、Red / Green / Review / CI、PR/head、Branch Protection/Ruleset 与 merge 前复核。

处理 GitHub PR 时按以下顺序执行：

```text
先确认当前宿主是否具有已经验证可用的自动 Draft → Ready 能力
├─ 已验证可用
│  → 创建 Draft PR
│  → Red / Green / Review / CI
│  → 完成门禁后自动切换 Ready
│
└─ 未验证、不可用，或当前宿主已确认无法自动完成 Ready
   → 不创建 Draft PR
   → 直接创建普通 PR
   → 在 Agent 流程与 PR 描述中将其视为“逻辑未就绪”
   → Red / Green / Review / CI 未完成前禁止 merge
```

硬规则：

- 当前宿主的 Draft → Ready 能力没有经过当前工具版本验证时，不为了保持界面上的 Draft 形式引入人工依赖；优先使用普通 PR + 逻辑未就绪门禁；
- 一旦调用 Ready 返回 `Field 'fullDatabaseId' doesn't exist on type 'Repository'` 或等价宿主 GraphQL 返回查询错误，**不能直接推断 Ready mutation 失败**。先记录一次真实错误，再**先重新读取 PR 当前状态**；不得循环重试同一失败 GraphQL，也**不得要求用户手动点击 `Ready for review`**；
- **如果已经 `draft=false`**，按“Ready 副作用已生效、返回结果查询失败”处理；保留错误证据，继续重新确认 CI、mergeable、当前 head SHA、reviewed head 和保护规则，不关闭或重建 PR；
- **只有仍为 Draft**，才把自动 Ready 视为当前宿主不可用。若当前授权允许关闭/创建 PR，则自动关闭原 Draft PR，以**相同 head/base** 创建普通 PR；在新 PR 描述中保留原 PR 链接、Red/Green/Review 证据与迁移原因，并**重新运行新 PR 的 fresh CI**；不得把旧 PR 的绿色状态直接当作新 PR 的当前证据；
- 普通 PR 处于“逻辑未就绪”期间，不因为 `draft=false` 就提前请求合并；仍必须完成项目规定的 Requirement Traceability / Completion Audit、Review、CI、文档和其他 Ready 门禁；
- 真正准备合并前重新读取 PR，**重新确认 `draft=false`、CI 和当前 head SHA**；同时确认 mergeable、Branch Protection/Ruleset、required checks、当前 reviewed head 和 Effective Authorization 没有漂移；
- GitHub PR 的真正 merge 一律使用 GitHub **REST merge**；宿主接口支持时必须携带 `expected_head_sha`，把审查/验证过的 head 绑定到 merge 动作；如果当前 REST merge 能力无法提供等价 head guard，则停止并报告宿主能力缺口，不用不带防漂移条件的其他 merge 通路冒充等价；
- merge 成功后读取真实 merge commit / main HEAD，并执行本次 changed scope 应触发的 **main fresh CI**；PR CI、历史 CI 或 merge API 成功本身不能替代 main 新鲜验证；
- 目标项目已经建立 repository-native Change archive 时，Implementation PR 中的 Change 保持 `active/ready_for_review`；merge 后由目标仓库基础设施执行同一 Change ID 的 `active → archive/YYYY-MM` 与 `status → done`。Agent 只验证结果，**不执行归档 commit，不创建归档 PR**；自动归档失败时保持 `blocked/incomplete`，不得自行接管掩盖基础设施故障；
- archive/done 只表示施工交付已进入目标分支并被冻结，**不等价于 Requirement/Issue Closure**；merge/main-fresh/CI 等 post-merge 平台事实优先由 PR/Commit/Actions Owner 持有，不为完整性机械复制回 Change；
- 目标项目没有 repository-native archive 时，继续遵守其当前正式 Change Owner，不由通用 Skill 发明直接写默认分支机制；
- 对**非 GitHub** 托管平台，不强行使用 GitHub REST、`expected_head_sha` 或 GitHub Draft 语义；使用该平台等价的 PR/MR 生命周期和 **head/revision guard**，但仍保持“自动化交付不依赖用户手工按钮、merge 前重新验证当前 revision、merge 后 fresh CI”的同等安全责任。

仅在已授权端到端交付且 REST merge/原生归档能力成立时，才走以下闭环；仅提交 PR 则止于 PR Ready，不自动合并：

Draft/普通 PR 按上述条件汇合后：
`Review/CI/Ready → head/mergeable/权限复核 → REST merge + expected_head_sha → implementation main fresh CI → repository-native Change archive → archive/done 与 governance fresh Evidence → Closure Audit`。

### 依赖

- 先确认语言、Runtime、包管理器、Manifest、锁文件和实际版本；
- 优先标准库和现有依赖；
- 普通功能不顺手升级；
- 新依赖说明必要性、维护、许可证、体积/构建影响和替代方案；
- Manifest 改动同步仓库正式 lock；
- 不用删除 lock、切换包管理器或解析 `latest` 掩盖问题。

### 安全

- 不硬编码、打印、提交或上传 Secret/Token/密码；
- 不关闭认证、授权、证书、输入校验或既有安全门禁制造“通过”；
- 避免不安全反序列化、任意命令/动态代码执行、字符串拼接 SQL；
- 按任务风险校验路径、文件、网络、数据库、命令、模板、归档和用户输入；
- 外部服务、生产数据、真实环境写入必须受明确权限和数据边界约束。

## 2. 交付报告

最终报告至少包含：

1. 变更摘要与逐文件/按类别目的；
2. 本次项目形态、研发阶段、语言/工具链和风险等级；
3. 上游 Requirement Traceability 与成功标准完成状态；
4. Validation Matrix：每层 Scope、实际 Evidence、`not_applicable` 依据；
5. Completion Audit / 两阶段 Review 结果；
6. Contract/API/ABI/Schema/Migration/数据变化（无则明确无）；
7. 文档同步及判断依据；
8. 本轮实际执行命令/检查、退出码、通过/失败数量；
9. 未验证内容、阻塞和剩余风险；
10. 兼容性、依赖、Migration、部署、迁移和回滚影响；
11. Git 分支、提交、PR、CI、合并和分支清理的实际状态。

不要只回复“已完成”“已修复”或“测试通过”。

## 3. 能力边界

- 项目缓存是本地可失效导航，不是向量数据库、长期记忆或需求事实副本，也不是应提交到 Git 的团队事实；
- Change 是 Git 可见施工契约，不是原子锁、租约、看板、通知或在线状态服务；项目使用其他正式治理载体时，Coding 不假装拥有该载体没有提供的锁或状态能力；
- Completion Gate 是流程完整性门禁，不是自然语言需求证明器；它不能替代 Agent/Reviewer 从上游事实源做语义完整性审计；
- Validation Matrix 是风险到证据的语义映射，不是固定测试配额，也不是 `ready_check.py` 能自动证明充分性的清单；
- 语言/项目 profile 是发现和验证导航，不是授权升级技术栈或重构架构；
- 看不到未提交、未推送、未同步、无权限访问或另一客户端私有状态；
- 不能强制其他人/Agent 遵守 Owner、分支或影响范围；仓库 CI/Branch Protection 可以阻止不满足门禁的变更合入；
- 宿主不支持持久文件、目标工具链、脚本、Git、device、数据库或外部服务时，先区分具体失败路径并发现等价能力；必要路径确实不可用才报告具体降级与未验证风险，不把局部失败扩大为仓库不可写。

## 4. 触发与回到主流程

以下任务至少在 Coding 主规则完成事实恢复和风险路由后读取本文件：

- 创建/切换分支、commit、push、PR、merge、tag、Release、deploy、rollback；
- 修改 Manifest、lock、Runtime、包管理器或依赖；
- 涉及 Secret、认证授权、输入边界、生产数据、真实外部写入或其他安全风险；
- 准备声明 Ready、完成、可合并、可发布、可部署或形成最终交付报告；
- 当前宿主缺少持久文件、终端、Git、测试环境、device、数据库、容器或外部服务能力，需要明确降级边界。

本文件只承接详细边界，不替代主 `SKILL.md` 的四维任务路由、Change、TDD、Validation Matrix、Completion Audit、Docs 或 Review。需要网络下载源时仍按 [03_编程语言与工具链适配规则.md](03_编程语言与工具链适配规则.md)；修改永久 CI/Workflow 时仍按 [07_通用验证与证据策略.md](07_通用验证与证据策略.md) 的 Workflow Responsibility Audit / Evidence Preservation Mapping。