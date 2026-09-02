<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.25","触发":{"任一":[{"包含":{"维度":"风险","取值":["L3"]}},{"包含":{"维度":"治理","取值":["存在活动变更","多个活动变更","要求变更记录","要求完成门禁"]}}]},"依赖":["coding.reference.04"]}
-->

# Change 仓库归属与 Carrier

本 Reference 只负责**已经确定需要持久施工契约之后**的 Repository Ownership、Carrier、ID 与元数据机械规则。是否需要创建/认领 Change、Requirement Traceability、Validation Matrix、Completion Audit、状态与归档语义仍由 [04_轻量变更管理.md](04_轻量变更管理.md) 负责。

把这些细节放在独立 Owner 中，是为了避免只做 Review、Git 交付或普通轻量 L2 的任务在没有真实 Change 操作时预付目录/schema 上下文；一旦命中 L3 或真实持久治理事实，本 Reference 必须与 ref04 一起加载，不能因为渐进披露而省略 Ownership 门禁。

## Change Repository Ownership

Change 的 Repository Ownership 由“谁被修改 / 谁被治理”决定，不由“规则从哪里加载”决定。每个 Coding Change 或项目等价持久施工契约必须只属于一个**唯一被治理仓库**。所有 carrier 路径、`affected_paths`、`contracts`、`data_changes` 以及仓库相对 Evidence 都**相对于该仓库根**解释；不得借另一个仓库的 Change carrier 承载当前仓库的施工范围。

使用 Agent_Skills 开发外部项目时，**Agent_Skills 只是治理规则来源**，不因此成为外部项目 Change 的 Owner。外部项目若确实需要持久施工契约，先复用该外部项目自己的正式治理载体；只有它没有可复用机制时，才在该外部项目自己的 Coding carrier 下建立 Change。**不得把外部项目 Change 写入 Agent_Skills** 的 `.agents/changes/`，也不得因为 Source Mode 正在读取 Agent_Skills canonical 规则就改变外部项目的 Change Ownership。

维护 Agent_Skills 源仓库本身时，被治理仓库才是 `dingyuwen777/Agent_Skills`；只有 Agent_Skills 自身实现、规则、Runtime、测试、CI 或发布治理的 Change 才进入 Agent_Skills 自己的 Change carrier。Skill 来源仓库与 Change Owner 在这个场景恰好相同，是因为“**谁被修改**”就是 Agent_Skills，而不是因为 Agent_Skills 提供了规则。

**一次任务实际修改多个仓库**时，先对每个仓库独立判断是否真的达到持久施工契约条件；只调查、只读取或仅作为事实来源的仓库不因此自动创建 Change。对**每个需要持久施工契约的仓库**，分别在该仓库自己的正式治理载体中创建或认领施工单元。可以通过 **Issue / PR / Change ID** 建立跨仓关联和顺序依赖，但**不得用一个 Change 跨仓**拥有另一个仓库的 `affected_paths`、Contract、数据变化、测试证据或交付状态，也不得把两个仓库的独立完成门禁折叠成一个“总 Change”。

这是 Ownership 与路径解析语义，**不新增 `change_repository`** frontmatter 字段，也不改变 `coding-change/v1` schema。当前被治理仓库由实际 repository root + 该仓库 carrier 确定；`coding.py --root <repo>` 继续以显式传入的 repository root 解析 Change carrier。若无法确认当前动作实际修改哪个仓库，先恢复仓库事实和 Mutation Target，而不是猜一个 carrier 后写入。

## Coding Change carrier、目录和 ID

Coding 自带 Change 使用当前唯一 schema：

```text
coding-change/v1
```

**不读取、不迁移、不兼容旧 Change schema。** 发现旧格式时应按目标项目自己的历史/迁移策略显式处理，不能让工具默默接受后继续。

默认 carrier：

```text
.agents/changes/
├── active/
│   └── CHG-YYYYMMDD-short-name/
│       └── CHANGE.md
└── archive/
    └── YYYY-MM/
        └── CHG-YYYYMMDD-short-name/
            └── CHANGE.md
```

如果目标仓库已经正式使用顶层：

```text
changes/active/
changes/archive/
```

承载同一类 Coding Change，工具沿用该现有 carrier，不为通用化强制搬迁。

如果仓库存在 OpenSpec 等不同治理体系、又不存在已确认的 Coding carrier，`new-change` 必须拒绝静默创建平行目录，并要求先按项目规则确定承载方式。

ID 使用 `CHG-YYYYMMDD-kebab-case`。一个 Change 默认只有一个 Owner 和一个主分支；协作者写进任务或决策区，不并列多个模糊 Owner。

## 必需元数据

Coding 自带 `coding-change/v1` 保持 frontmatter 扁平，便于没有 YAML 依赖的工具读取：

- `schema`；
- `id`、`title`、`level`、`status`；
- `owner`、`branch`、`created`、`updated`；
- `completion_gate`；
- `depends_on`；
- `affected_areas`、`affected_paths`；
- `contracts`、`data_changes`。

新模板固定：

```text
schema: coding-change/v1
completion_gate: required
```

它表示**一旦选择 Coding Change 作为持久施工契约**，该 Change 在进入 Ready/Archive 时必须通过 Requirement Traceability 与 Completion Audit 门禁；不是说所有 L2 都必须先创建这个文件。

不要用自然语言“可能改很多地方”代替影响元数据。路径尽量写仓库相对目录或文件；Contract 和数据资源使用仓库既有正式名称。

元数据必须来自仓库事实或已确认设计。仓库没有适用的 Contract、数据资源、模块 Owner 或 Migration 时，对应列表使用 `[]`，不得为显得完整而造名称。只有本次需求明确建立新接口或数据资源、且其名称和边界已通过设计门禁时，才记录计划中的新对象。

`coding.py` 对当前 schema、必需字段、状态、依赖 ID 和安全相对路径执行严格校验。任一 Active Change 损坏或使用不受支持的结构时，状态与冲突检查会失败并要求先修正记录；不要把无法解析的记录静默当成“无冲突”。
