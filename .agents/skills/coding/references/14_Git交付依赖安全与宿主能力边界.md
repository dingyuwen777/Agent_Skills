<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.15","触发":{"任一":[{"包含":{"维度":"执行模式","取值":["Git","发布"]}},{"包含":{"维度":"意图","取值":["Git 交付","PR Ready","Release","依赖升级","安全与权限"]}},{"包含":{"维度":"能力","取值":["Git"]}}]},"依赖":["coding.reference.03","coding.reference.07","coding.reference.11"]}
-->

# Git、交付、依赖、安全与宿主能力边界

这份规则承接 Coding 主规则中与 Git、依赖、安全、最终交付报告和宿主能力边界直接相关的完整详细约束。主 `SKILL.md` 继续保留这些边界的硬触发入口；命中 Git / PR / Release / Delivery、依赖变化、安全边界、最终完成报告或宿主能力降级时，必须读取本文件，不能只凭主文件中的导航句补流程。

## 1. Git、依赖与安全的通用边界

### Git

- 修改前检查 branch、worktree、未提交修改；
- 不覆盖用户改动；
- 禁止 `git reset --hard`、`git clean -fd`、强制推送、未授权共享历史重写；
- 未经授权不创建分支、提交、推送、PR、合并、部署、删分支；
- CI 失败、冲突、保护规则或结果未确认时不强行推进；
- Git 提交信息必须中文；项目可增格式、前缀或工单号，不得覆盖中文要求；
- 本地 Git 路径可用时，开工顺序：`最新目标分支 → 本地任务分支 → 本地 Change / 失败测试 / 最小治理提交 → 首个本地提交 → 首次 push 创建远程跟踪分支 → 早期 PR`；不得先创建远程空分支。仅有托管平台 API 时按下文语义等价路径执行，不把本地 clone/commit 当作远端写入的固定前置条件。

### Requested Action 与 Effective Authorization

Git 能力存在不等于当前任务拥有全部 Git 权限。用户说出的目标动作只是 **Requested Action**；真正可执行的 **Effective Authorization** 必须由目标项目规则、当前 authenticated principal、托管平台当前保护规则/Ruleset 与宿主真实能力共同确认。

硬规则：

- 用户请求 merge、Release、Deploy、生产 Migration/数据动作不能提升当前 principal 的真实权限；
- Requested Action 超出 Effective Authorization 时，在安全且已授权范围内完成最大可交付结果，例如开发到 PR Ready，并把未执行动作明确报告为 `BLOCKED_BY_AUTHORIZATION`；
- 不得因为当前连接拥有 Admin token、bypass actor、Bot 或其他技术通路，就把这些能力当作当前任务的治理授权；
- 平台拒绝保护分支更新或 required gate 时停止，不通过换 API、force push 或其他身份绕过；
- 当前权限事实无法可靠确认时，对高权限写动作 fail closed。

### 语义等价能力发现与恢复

**单一路径失败不等于仓库不可写。** 任意模型都必须先从当前宿主实际工具目录、已连接 App、终端/Git 与已有 CI/Runner 中发现满足同一目标的等价能力；不能因为第一次 clone、push、Contents API 或某个封装失败，就直接报告 capability blocker。同目标、同范围、同副作用等级的授权按 Router 延续，不为更换等价传输路径重复确认。

固定顺序：

1. **界定目标与失败层。** 区分读取、更新文件、原子多文件提交、更新任务分支、PR 状态、受保护合并、验证等目标；保留真实错误，区分网络/DNS、工具或参数不匹配、结果不明、限流、并发冲突、授权/保护拒绝及 required gate 失败。单个 HTTP 状态或工具名称不足以证明整个仓库不可写。
2. **先回读结果，再换路径。** 超时、返回解析/查询错误或连接中断可能发生在副作用之后；先核对文件 blob、commit/ref、PR 或 run 的当前状态。已达到目标则继续，不重复提交、创建 PR 或合并。结果无法消歧时只阻塞该写动作，避免重复副作用。
3. **有界发现并选择最强可用路径。** 只比较当前宿主真实存在且与目标相关的候选；“最强”指保持同一语义目标、原子性、防漂移、审计和验证能力，不是使用更高权限或更大副作用。优先既有稳定入口；它不能满足要求或已失败时，选择能完整保持这些条件的替代入口。找到可用等价路径后立即推进，不为证明全面而把其他路径逐一试坏。
4. **执行后核验。** 核对真实 revision、文件/diff、分支/PR 与对应验证结果；工具目录里有写方法只是候选能力，实际写入并回读成功才证明本次写动作完成。没有任何分支更新时，孤立 blob/tree/commit 不得报告为已推送。

GitHub 常见候选仅用于能力发现，不是必须遍历的配额：

| 语义目标 | 可发现的等价路径 | 必须保持 |
| --- | --- | --- |
| canonical 读取 | 已授权 App 文件/对象读取；可用的 Git checkout | 正确仓库、当前 ref、完整原文与 Ownership；不退回安装副本/旧缓存 |
| 单文件更新 | 本地 Git；带当前 blob SHA 的 Contents 更新；Git tree/commit/ref | 明确任务分支、精确内容、并发保护和回读 |
| 原子多文件提交 | 本地 commit/push；基于当前 tree 的 Git Data API → 单一 commit → 非强制 ref 更新 | 保留未改文件及 mode；核对 parent/head 与完整 diff；有原子要求时不降级成逐文件半完成 |
| 验证 | 相同受支持环境的本地入口；仓库已有授权 CI/Runner | 相同目标 revision、命令、依赖/环境与证据范围；不把代码阅读当测试 |
| PR/合并 | 宿主提供的等价生命周期/REST 能力 | 下文 head guard、Review、CI、保护规则与对应动作授权全部保留 |

仅有 API 时，先基于核验的 base tree/parent 创建包含真实改动的 commit，再创建或非强制更新已授权任务分支；不得为适配工具恢复空分支、漏掉未改文件、覆盖并发提交或直写受保护 main。`force=false` 只防止非快进覆盖，不等于精确 expected-head 比较；任务要求更强 CAS/head guard 时必须另有等价保障，不能降级冒充。Contents 的 blob SHA 守卫也不能冒充整个分支的原子 head guard。

**不得把权限拒绝伪装成能力故障。** 已确认的授权、Branch Protection、Review/CI gate 拒绝不通过换 token、actor、API、强推或降低门禁绕过；限流遵守平台退避，不用轮换通道逃避限制。参数错误按当前 schema 修正；同类已确认失败不无界重试。路径变化若改变范围、副作用、费用或必要质量保障，先按现有授权/决策门禁处理。

只有完成相关能力发现，且每条能满足必要语义和门禁的路径都由实际错误、当前 schema/权限事实或缺失前提证明不可用时，才报告 **capability blocker**。无需执行已被事实排除的危险或无效尝试；报告最小受阻动作、已调查候选及依据、已完成结果和剩余条件，继续其他无依赖的已授权工作。

### GitHub PR 零人工交付兼容策略

GitHub 的 Draft 状态只是托管平台工作流状态，不能成为必须由用户手工点击才能继续的质量门禁。真正的门禁仍然是当前项目的 Change/需求追溯、Red / Green / Review / CI、真实 PR 状态、head SHA、Branch Protection/Ruleset 和 merge 前复核。

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

仅在 Requested Outcome 包含端到端交付、对应授权成立，且支持 GitHub REST merge 与 repository-native Change archive 时，下面完整闭环才适用；提交 PR 的任务只执行至 PR Ready，不因能力存在自动合并：

```text
宿主 Ready 能力可靠
→ 创建 Draft PR
→ Red / Green / Review / CI
→ 自动 Ready
→ 如果 Ready API 返回异常，先重读 PR 状态
   ├─ draft=false → 继续，不重建 PR
   └─ 仍为 Draft → 自动关闭 Draft，并以相同 head/base 创建普通 PR后重新跑 fresh CI
→ 重新确认 draft=false / CI / head SHA / mergeable / Effective Authorization
→ REST merge + expected_head_sha
→ implementation main fresh CI
→ repository-native Change archive
→ 验证 archive/done 与项目要求的 governance fresh Evidence
→ Closure Audit

宿主 Ready 能力已确认不可用
→ 创建普通 PR（逻辑未就绪）
→ Red / Green / Review / CI
→ 重新确认 draft=false / CI / head SHA / mergeable / Effective Authorization
→ REST merge + expected_head_sha
→ implementation main fresh CI
→ repository-native Change archive
→ 验证 archive/done 与项目要求的 governance fresh Evidence
→ Closure Audit
```

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
- 宿主不支持某一路径时先按本文件完成等价能力发现；必要路径确实不可用才说明具体降级与未验证风险，不把局部故障扩大为整个仓库不可写。

## 4. 触发与回到主流程

以下任务至少在 Coding 主规则完成事实恢复和风险路由后读取本文件：

- 创建/切换分支、commit、push、PR、merge、tag、Release、deploy、rollback；
- 修改 Manifest、lock、Runtime、包管理器或依赖；
- 涉及 Secret、认证授权、输入边界、生产数据、真实外部写入或其他安全风险；
- 准备声明 Ready、完成、可合并、可发布、可部署或形成最终交付报告；
- 当前宿主缺少持久文件、终端、Git、测试环境、device、数据库、容器或外部服务能力，需要明确降级边界。

本文件只承接详细边界，不替代主 `SKILL.md` 的四维任务路由、Change、TDD、Validation Matrix、Completion Audit、Docs 或 Review。需要网络下载源时仍按 [03_编程语言与工具链适配规则.md](03_编程语言与工具链适配规则.md)；修改永久 CI/Workflow 时仍按 [07_通用验证与证据策略.md](07_通用验证与证据策略.md) 的 Workflow Responsibility Audit / Evidence Preservation Mapping。