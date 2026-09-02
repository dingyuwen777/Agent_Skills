---
schema: coding-change/v1
id: "CHG-20260902-change-id-second-precision"
title: "Change ID 秒级生成与历史兼容"
level: L2
status: ready_for_review
owner: "Codex"
branch: "feat/change-id-second-precision"
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - "coding-governance"
affected_paths:
  - ".agents/skills/coding/SKILL.md"
  - ".agents/skills/coding/references/24_Change仓库归属与Carrier.md"
  - ".agents/skills/coding/scripts/coding.py"
  - ".agents/skills/coding/tests"
contracts:
  - "coding-change/v1"
data_changes: []
---

# 目标

让 Coding Change 的默认新建入口使用北京时间秒级、可排序且便于人工区分的 ID，同时保持所有既有日期级 ID、依赖关系和归档记录可读。

# 成功标准

- [x] `new-change --slug <kebab-case>` 自动生成 `CHG-YYYYMMDD-HHMMSS-<slug>`，目录名与 frontmatter `id` 一致。
- [x] 自动生成时间固定使用 `Asia/Shanghai`，不依赖宿主本地时区。
- [x] 旧 `CHG-YYYYMMDD-<slug>` 与新秒级 ID 均可被当前 schema、`depends_on` 和 Ready/状态流程读取。
- [x] 显式 `--id` 入口保持兼容；无效 slug、无效 ID 和重复目录继续失败关闭。
- [x] canonical 规则、示例、实现和自包含测试一致；不在外部项目或安装副本复制通用规则。

# 范围

- Coding Skill 中 Change 新建示例和新入口说明。
- Change Repository Ownership/Carrier Reference 的 ID 规则与兼容边界。
- `coding.py` 的 ID 生成、双格式校验、CLI 参数和错误信息。
- Change 生成、历史兼容、依赖兼容、无效输入和冲突失败测试。

# 非目标

- 不重命名任何现有 active/archive Change、Issue、PR、分支或历史引用。
- 不修改 `coding-change/v1` schema、frontmatter 字段、carrier、归档目录或状态机。
- 不修改 AIMA_UGC 项目 Overlay、顶层 carrier 或本地 Runtime/Project Payload 安装副本。
- 不改变 Runtime executable/package、安装、Release 或平台构建机制。

# 必须保持不变

- 既有 `CHG-YYYYMMDD-kebab-case` 对当前 schema 继续合法，历史记录不可改写。
- `new-change --id`、`create_change(change_id=...)`、`depends_on`、目录原子创建和重复 ID 失败语义保持。
- Change 自动时间继续使用北京时间；`created` / `updated` 保持日期字段，不在本次扩展 schema。
- 默认 carrier 与顶层既有 carrier 发现规则保持。

# 关键决策

- 通用 Change ID 由 Agent_Skills canonical Coding Owner 维护；AIMA_UGC 只提供兼容事实，不复制规则。
- 新格式采用 `CHG-YYYYMMDD-HHMMSS-kebab-case`，固定宽度保证目录按字典序排序；时间来自 `Asia/Shanghai`。
- 时间戳用于排序和区分，不作为覆盖保护；现有原子 `mkdir(exist_ok=False)` 与重复检查继续承担冲突失败边界。
- 新建默认增加 `--slug` 自动生成入口；显式 `--id` 继续接受旧/新两种格式，用于兼容既有调用和确定性引用。
- 通过同一 schema 的宽化读取实现无迁移兼容，不创建 schema v2，不批量改写历史。

# 需求追溯

从用户已确认决定、正式路线图、规格、阶段、功能完成定义、新建项目正式需求或约束，以及其他上游事实源独立提取要求。**当前变更不能把自身作为需求来源，也不能把本表当作上游需求全集。**

状态只允许使用以下机器枚举：

- `satisfied`：已有实现或验证证据；
- `explicitly_deferred`：已有正式批准的延期依据；
- `not_applicable`：有明确事实证明不适用；
- `not_satisfied`：尚未满足，进入 `ready_for_review` 前必须清零。

`来源` 优先写仓库相对事实源路径；本轮用户明确决定可写 `user:<简短标识>`；外部正式资料可写 `external:<可识别来源>` 或链接。`证据` 必须写实际实现、测试、运行或正式延期、不适用依据，就绪时不得保留占位内容。

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Change 文件夹名称精确到小时、分钟、秒 | user:change-id-second-precision | satisfied | `generate_change_id` 与 `test_slug_cli_generates_beijing_second_precision_id` 证明 `CHG-YYYYMMDD-HHMMSS-slug` |
| R2 | 按推荐方案修改 Agent_Skills，而不是 AIMA_UGC 或安装副本 | user:apply-recommended-owner | satisfied | `origin/main...004e561` 只修改 canonical Agent_Skills 的 Coding Owner、脚本、测试和本仓 Change |
| R3 | 历史日期级 ID 保持兼容且不得重命名 | external:https://github.com/dingyuwen777/Agent_Skills/issues/167 | satisfied | 双格式正则、显式 `--id`、混合 `depends_on` 测试通过；历史目录零改名 |
| R4 | 不直接在 main 开发，使用 Issue、Change、本地任务分支、早期 PR 和 CI 交付 | user:push-to-main | satisfied | Issue #167、分支 `feat/change-id-second-precision`、Change 和 PR #168 已建立；最终 merge/main CI 继续记录在交付区 |

# 验证矩阵

先按当前任务的**真实失败边界**选择通用验证维度。每层只使用机器值 `required` 或 `not_applicable`：`required` 写明本次要证明的范围，并在完成前补当前证据；`not_applicable` 必须说明该层为什么没有独立证明价值。

不要为了填模板机械执行所有层，也不要因为某一层已经绿色就推断另一层已经被证明。

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 18 项 Change 目标测试通过，覆盖北京时间、旧/新格式、slug、显式 ID、混合依赖、无时区时间、非法 ID 和同秒同 slug 冲突 |
| 接口 / 契约 | required | CLI help 显示互斥 `--slug/--id`；362 项自包含测试证明当前 schema、路由和 Bundle 一致 |
| 集成 / 持久化 / 运行依赖 | required | 临时仓库通过正式 CLI 创建真实目录和 CHANGE.md；原子 `mkdir(exist_ok=False)` 保持，外部服务不适用 |
| 用户 / 工作流验收 | required | `test_slug_cli_generates_beijing_second_precision_id` 核对正式入口、输出路径、目录和 frontmatter |
| 跨组件关键路径 | not_applicable | 本次只改变同一 Coding Owner 内的内容规则、CLI 和测试；CLI 到文件系统的组装行为已由用户工作流验收覆盖，无独立应用组件链路 |
| 外部依赖 / 供应方探测 | not_applicable | ID 生成与校验不调用第三方服务、硬件或远端环境 |
| 构建 / 打包 / 运行 | not_applicable | 不改变 Runtime/package/platform boundary；按仓库 scope 规则不运行三平台 binary package |
| 文档 / 治理 / 其他 | required | Core 50,913 bytes 未超 51,000 上限；路由预算测试、规则 Owner 测试及完整自包含套件通过 |

通用规则见 [`.agents/skills/coding/references/07_通用验证与证据策略.md`](../../../skills/coding/references/07_通用验证与证据策略.md)。

项目存在界面、接口、持久化或外部依赖专项边界时，在保持语义责任不变的前提下按 [`.agents/skills/coding/references/08_分层测试与验收策略.md`](../../../skills/coding/references/08_分层测试与验收策略.md) 映射为更具体层名，例如：

```text
用户 / 工作流验收
→ 浏览器 / 界面模拟验收

集成 / 持久化 / 运行依赖
→ 后端 / 接口 / 持久化集成

接口 / 契约
→ 契约 / 生成消费者

跨组件关键路径
→ 真实跨组件关键路径

外部依赖 / 供应方探测
→ 外部依赖 / 供应方探测
```

项目实际使用 PostgreSQL、MySQL、SQL Server、SQLite、文件系统、DynamoDB 等具体持久化方式时，集成验证必须证明对应真实语义；浏览器或界面模拟不能冒充真实后端、持久化；一条关键路径不能冒充全部状态；真实外部探测默认有界且不进入普通持续集成。

# 完成审计

进入 `ready_for_review` 前必须**重新读取上游事实源**，不要从当前变更的检查表反推需求。

按当前项目形态和任务边界执行正向、反向审计。例如：

- 前后端：后端能力 → 前端入口，前端动作 → 后端真实能力；
- 命令行：公共命令或参数 → 处理器 → 标准输出、标准错误、退出码、副作用；
- 程序库：公共接口 → 消费者；
- 异步：请求 → 状态 → 错误或恢复 → 最终结果；
- 数据结构或迁移：写入方 → 迁移 → 读取方或消费者；
- 打包或发布：源码 → 构建产物 → 安装或启动；
- 基础设施：配置 → 计划或渲染 → 运行或部署边界（在授权范围内）；
- 新建项目：目标或硬约束 → 工程基线 → 构建、测试、打包、启动 → 最小真实用户或消费者结果。

同时复核验证矩阵：每个 `required` 都有足够的新鲜证据，每个 `not_applicable` 都有真实依据。

- [x] upstream_re_read：已重读本轮用户要求、Issue #167、Maintenance、Coding Core、Reference 04/15/24 和真实脚本/测试。
- [x] change_coverage：用户要求的秒级目录名、canonical Owner、历史兼容和 main 交付路径均已进入当前 Change 或交付区。
- [x] reverse_audit：已从规则到 CLI/生成器/目录/frontmatter、从旧 ID 到 metadata/depends_on、从 canonical 内容到 Bundle/路由测试反向核对。
- [x] unresolved_cleared：需求追溯已无 `not_satisfied`；无延期项。

# 任务

- [x] 调查当前实现和事实源；确认 ID 格式 Owner、生成器、原子创建与 AIMA 兼容边界
- [x] 建立四维任务路由：CLI / Developer Tool + Skill Content，行为实现，Python 3.14，L2
- [x] 建立失败测试并确认因缺少秒级生成/新格式兼容而失败
- [x] 建立并维护验证矩阵
- [x] 完成最小实现
- [x] 同步受影响文档
- [x] 取得新鲜验证证据
- [x] 完成需求追溯与完成审计

# 验证

## 计划

- 验证矩阵：按 [`.agents/skills/coding/references/07_通用验证与证据策略.md`](../../../skills/coding/references/07_通用验证与证据策略.md) 选择通用维度；存在专项配置时再叠加专项策略
- 目标测试：Change ID 生成、CLI、旧/新格式、depends_on、重复冲突测试
- 相关测试：Coding Change、repository ownership、ready check、progressive disclosure 与 self-contained Skill Tests
- 静态检查或构建：Python compile/测试发现；Runtime scope 分类应为 content，不触发三平台 package
- 就绪检查：使用 Coding 自带 `coding-change/v1` 时运行 `python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Red：`python -m unittest discover -s .agents/skills/coding/tests -p "test_change*.py"`，退出码 1，运行 13 项，1 个失败、2 个错误；失败分别证明 Reference 24 尚无秒级/兼容规则、CLI 尚无 `--slug`、实现尚无 `generate_change_id`。测试在授权后的系统临时目录运行，排除了沙箱权限噪声。
- Green：`python -m py_compile ... && python -m unittest discover -s .agents/skills/coding/tests -p "test_change*.py"`，退出码 0；Review 补强无时区时间、非法显式 ID 和同秒同 slug 不覆盖测试后，目标套件 18 项全部通过。
- 内容预算：`test_coding_progressive_disclosure.py` 6 项、`test_router_skill_migration.py` 7 项，退出码均为 0；Coding Core 50,913 bytes，未超过 51,000 bytes。
- 完整套件：在干净 LF worktree `004e561` 设置 `PYTHONUTF8=1`，执行 Workflow 同等 `py_compile` 与 `python -m unittest discover -s .agents/skills/coding/tests -p "test_*.py"`，退出码 0，362 项通过、1 项按既有条件跳过。
- Runtime scope：`git diff --name-only origin/main...HEAD | python .github/scripts/runtime_package_scope.py --json` 输出 `content`；本次不要求三平台 binary package。
- 独立 Review：以 `9dbeb2b7...72351a8` 为初始 Target 执行 A1/A2、兼容、CLI、时间、原子冲突、内容预算和测试充分性复核；发现无时区时间、非法显式 ID 与同秒冲突缺少直接回归测试，已由 `004e561` 补齐。对 `9dbeb2b7...004e561` 复核后无剩余 blocker/high/medium/low Finding。

# 文档影响

- `coding/SKILL.md` 与 Reference 24 targeted 更新；README/USAGE/Runtime README 不负责内部 Change ID 细节，不修改。

# 交付

- Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/167
- 提交：`272c9ce` 建立 Red/治理基线；`72351a8` 完成秒级生成、兼容规则和测试；`004e561` 补强失败边界测试。
- 拉取请求：https://github.com/dingyuwen777/Agent_Skills/pull/168；当前实现与 Review 已就绪，待最终 Change 提交、PR CI 和 merge。
- 发布：本次不创建 Release；合并后按 content scope 验证 main。
