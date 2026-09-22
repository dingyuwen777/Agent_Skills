<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.30","触发":{"任一":[{"包含":{"维度":"意图","取值":["Issue/工单治理"]}},{"包含":{"维度":"治理","取值":["存在活动变更","多个活动变更","要求变更记录","要求完成门禁"]}}]},"依赖":["coding.reference.18","coding.reference.25"],"最低风险":"L2"}
-->

# 治理资产机器 Contract

本 Reference 只负责把 Change、Requirement Source、Pull Request 的稳定治理语义落实成**宿主无关机器 Contract**，并固定 canonical template/Profile/validator 的 Ownership。生命周期、Evidence、Carrier、Closure 与 Runtime 安装事务仍由既有 Owner 负责，不在这里复制。

```text
canonical template / Issue Form / PR Template / validator
→ candidate generation
→ pre-write validation
→ platform write
→ live readback
→ same validation
```

GitHub UI、CLI、MCP、API 或其他 Agent 都只是写入通路；宿主不同不能改变合法治理资产的机器判据。required validation 失败即 fail closed，不能先自由创建再靠后续补模板，也不能用模型判断或其他 CI 绿色代替。

canonical stdlib validator：

```text
.agents/skills/coding/scripts/governance_contract.py
```

无 import 集成的宿主调用其 CLI。目标项目只在自己的 adapter 中处理 Carrier、CI、平台 API 和显式更强 Overlay；机器 Contract 校验稳定身份、结构、Acceptance 与本地可判定的 Requirement-Source shape，语义充分性和远程来源真实性仍归 Requirement Review、Completion Audit、Review / live gate。

## 1. Change：模板是唯一结构 Owner

历史 identity 与当前新建必须机械区分：

```text
已有历史 identity
→ 日期级或当前秒级格式均可按既有 parser 读取

新建 / 本 PR 新增或修改实例
→ 只允许 CHG-YYYYMMDD-HHMMSS-kebab-case
```

历史 parser/legacy ID 只表示旧 identity 可读，不授权新日期级 Change。新建统一使用 current identity；PR 对新增/修改 Active Change 执行 new-instance validation，历史 archive 不批量迁移。

新实例结构直接以 canonical [`../assets/CHANGE.template.md`](../assets/CHANGE.template.md) 为 Profile：validator 动态读取有序一级标题；风险级别额外必需的二级结构由模板内 `governance:required-for=<level>` marker 定义，不维护第二份标题清单。至少要求当前 schema、秒级 ID、目录/frontmatter identity 一致、L2/L3、模板结构完整/唯一/有序。`ready_check.py` 继续拥有 Traceability/Completion/Ready。

## 2. Requirement Source：canonical Issue Forms 是 GitHub Profile Owner

GitHub 默认 Issue Forms 的唯一人工维护源：

```text
.agents/skills/coding/assets/issue-templates/
├── 01-requirement.yml
├── 02-bug.yml
├── 03-technical-change.yml
└── config.yml
```

使用默认 GitHub Profile 的仓库，其 `.github/ISSUE_TEMPLATE/*.yml` 都是 canonical assets 的**原字节受管投影**，不得独立编辑。validator 直接按 Form body 顺序恢复字段自身 `validations.required=true` 的 **checkboxes + textarea** label；Markdown 说明块不构成 Issue body section，也不维护第二份标题表。

### create

新建 Issue 使用 `validate-issue --mode create`：

- title 唯一匹配 canonical 类型前缀；
- required checkbox + textarea 构成 ordered Core；
- Core 完整、唯一、严格顺序；
- Core 前或 Core 中不能插入自由 section；
- Lifecycle Appendix 只能追加在完整 Core 后；
- required checkbox section 必须真实勾选；
- Acceptance 只从 canonical `验收标准` section 提取，AC1 起连续、唯一、文本非空；其他位置的 AC 文本不能意外满足 Contract。

### live / closure

`live` 用于 creation-time Contract 生效前的历史 open Issue 或实质更新，允许保持旧 Issue 没有新增 duplicate-search checkbox 的既有结构，但继续要求 canonical textarea、稳定 Acceptance 与来源语义。**历史兼容不得降低新建实例的 create Contract。**

`closure` 在 live Contract 上要求 Acceptance 全部按直接 Evidence 回写完成；close 后仍要 live reread 确认状态与 Acceptance 未漂移。已关闭历史 Issue 默认不批量迁移。

## 3. Pull Request：canonical PR Template 是唯一 Profile Owner

GitHub 默认 PR Template 的唯一人工维护源是 [`.agents/skills/coding/assets/PULL_REQUEST_TEMPLATE.md`](../assets/PULL_REQUEST_TEMPLATE.md)。根 `.github/PULL_REQUEST_TEMPLATE.md` 只是原字节 projection。PR Core headings 必须从 canonical Template 动态解析，validator 不维护第二份 heading list。

新建 PR 使用 `validate-pr --mode create`：

- canonical Core 完整、唯一、严格顺序；
- Core 前/中不能插入自定义二级 section；
- Final Review、Current-head Evidence 等 Lifecycle Appendix 只能在完整 Core 后；
- Requirement Source section 至少有一行 `Requirement-Source:`；
- 本地 validator 拒绝空值、`#<Issue>`、`TBD`、`TODO`、`待确认`、`无` 等占位值；
- 本地 validator **不假装验证远程 Issue/路径存在性**；真实来源是否存在、可访问、与 PR 范围一致继续由 live Requirement Source gate 判断。

Requirement Source 说明 PR 为什么存在；`Closes/Fixes/Resolves` 只表达 merge 是否足以自动关闭整个 Issue。需要 post-merge Evidence 时不得用 closing keyword 绕过 main-fresh、Archive 或 Closure Audit。

## 4. Mutation：写前写后同检

Issue 创建固定为：

```text
canonical Issue Profile
→ candidate
→ validate-issue --mode create
→ PASS
→ create/update through platform
→ live reread
→ validate-issue --mode create
```

PR 创建固定为：

```text
canonical PR Profile
→ candidate
→ validate-pr --mode create
→ PASS
→ create/update through platform
→ live reread
→ validate-pr --mode create
```

任何 pre-write FAIL 都禁止平台 write。后期补模板只能作为异常恢复路径，不能成为标准创建流程。Change 创建/更新继续使用 canonical Change Template + candidate validation + changed-scope/Ready/Completion/Review。无本地 shell 时使用宿主等价 API 写入与 readback，不得靠模型自证格式。

## 5. Canonical Governance Assets、Project Payload 与 Runtime projection

Coding canonical governance assets 为：

```text
coding/assets/issue-templates/*.yml
coding/assets/PULL_REQUEST_TEMPLATE.md
```

它们沿用现有 Project Payload / install-state 分发，不新增治理专用 Payload schema、asset manifest 或 ownership sidecar；根 `.github` projection 本身不进入 Payload 形成第二 Owner。

目标项目首次安装：

```text
target missing            → create incoming canonical
target == incoming        → safe adoption
target different          → fail closed
```

后续受管升级的 markerless ownership：

```text
previous Runtime install-state
→ 证明 previous canonical source path 属于 Agent_Skills
→ 读取写入前 previous canonical bytes A
→ 读取 root target projection X
→ X == A 才允许 A → incoming B
→ X != A => PROJECT_SIDE_PROJECTION_DRIFT / fail closed
```

新版本第一次增加某 projection（例如 PR Template）时，previous state 没有该 source ownership，因此仍走 missing/equal/different create/adopt/fail-closed；不能因为仓库已经安装 Agent_Skills 就认领历史同名文件。canonical projection 被删除时，target missing 已满足；target == previous canonical 才安全删除；project-side drift 拒绝删除。

ownership **不依赖 governance template marker**，也不生成 `governance-state.json`、`projection-state.json` 或等价 sidecar。具体 snapshot/apply/rollback 由 Runtime installer Owner 负责，不能再建立 server 外第二套 projection transaction。

Agent_Skills 源仓库自身使用：

```bash
python scripts/sync_repository_governance_assets.py
python scripts/sync_repository_governance_assets.py --check
```

保证根 Issue + PR projection 与 canonical assets 原字节一致。

## 6. 失败边界与完成判据

- 新 Change / Issue create / PR create 不合规 → 禁止继续对应 write/Ready/merge；
- candidate 与 live 不一致 → 以 live 为事实重验，无法安全恢复则 `blocked/unresolved`；
- source repository governance projection 漂移 → sync/check 阻塞；
- first install 不同内容同名文件 → collision fail closed；
- managed upgrade/root projection bytes 与 previous canonical 不一致 → `PROJECT_SIDE_PROJECTION_DRIFT`；
- installer 任一步失败 → root governance projections 与本轮 Runtime/Payload/Host writes 一并 rollback；rollback 失败必须聚合显式报告；
- Rule、canonical assets、validator、CLI/CI/tests、Runtime/Project Payload 任一不同步 → 按 Mutation Impact Audit 保持 NOT_READY。

```text
canonical Rule
+ Change Template
+ canonical Issue Forms
+ canonical PR Template
+ validator
+ source projection parity
+ Project Payload / install-state / Runtime projection parity
+ installer rollback
+ 实际 Issue/PR live validation
+ 永久正反例
+ Review
+ current-head / main-fresh required CI
```

完成证明要求同一 Contract 能稳定拒绝不合规治理资产、project-side drift 和不合法 creation candidate，并证明安全的 first install、managed upgrade、new projection、removal 与 rollback。
