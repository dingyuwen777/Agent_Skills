<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.15","触发":{"任一":[{"包含":{"维度":"执行模式","取值":["Git","发布"]}},{"包含":{"维度":"意图","取值":["Git 交付","PR Ready","Release","依赖升级","安全与权限"]}},{"包含":{"维度":"能力","取值":["Git"]}}]},"依赖":["coding.reference.03","coding.reference.07","coding.reference.11"]}
-->

# Git、交付、依赖、安全与宿主能力边界

本文件是 Git / PR / Release / Delivery、依赖、安全、交付报告与宿主能力边界的详细 Owner；Coding 主 `SKILL.md` 保留硬触发入口。命中时必须读本文件，不凭导航补流程。

## 1. Git、依赖与安全的通用边界

### Git

- 开工核验 branch/worktree/未提交修改并保护用户工作；无授权不建/删分支、commit/push/PR/merge/deploy；禁 `git reset --hard`、`git clean -fd`、force push、未授权改共享历史；CI 失败、冲突、保护或结果未确认则停。提交信息中文，项目格式可叠加。
- 本地 Git 可用：最新目标分支→任务分支→Change/失败测试/最小治理提交→首个提交→首次 push 建跟踪分支→早期 PR；禁远端空分支。仅托管 API 时保持等价保障，本地 clone/commit 非固定前置。
- 既有实现未完整遵循治理而现要提 PR：保留工作，以当前 revision 为待验证候选；按 Requirement Source、base/head/diff 和既有 Owner 补本次 required 门禁，不伪造历史 TDD/Issue/Change/Review/测试；可安全复现的 `base Red→current Green` 仅作事后回归证据；Issue/Change/测试仍按既有触发，PR 如实披露，普通协作者止于 PR Ready。

### Requested Action 与 Effective Authorization

Requested Action 是用户请求；Effective Authorization 还受项目规则、当前 principal、保护/Ruleset 与宿主能力约束，能力存在不等于授权。

- merge/Release/Deploy、生产 Migration/数据等请求不提升真实权限；超权时做到安全且已授权的最大交付（如 PR Ready），未执行动作标记 `BLOCKED_BY_AUTHORIZATION`。
- Admin/bypass/Bot 等技术通路不等于任务授权；权限/保护/required gate 拒绝时不换身份/API、force 绕过；高权限写入的真实权限无法确认时 fail closed。

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