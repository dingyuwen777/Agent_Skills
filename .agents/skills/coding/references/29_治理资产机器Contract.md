<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.30","触发":{"任一":[{"包含":{"维度":"意图","取值":["Issue/工单治理"]}},{"包含":{"维度":"治理","取值":["存在活动变更","多个活动变更","要求变更记录","要求完成门禁"]}}]},"依赖":["coding.reference.18","coding.reference.25"],"最低风险":"L2"}
-->

# 治理资产机器 Contract

本 Reference 只拥有一个责任：把 Change 与 GitHub Requirement Source 已由 Ref18/Ref25 定义的稳定语义落实成宿主无关机器 Contract，并保证模板/Profile/validator 只有 canonical Owner。自然语言生命周期、Evidence、Carrier 与 Closure 仍由既有 Owner 负责，不在这里复制。

```text
canonical template / Issue Form / machine validator
→ Runtime Project Payload 受管投影
→ 项目 Carrier / CI adapter（可更强，不可复制通用规则）
→ candidate validation
→ 宿主写入
→ live readback
→ 同一 machine validation
```

因此 generator、GitHub Form、网页、CLI、Contents/Git Data API 都只是写入入口；ChatGPT、Codex、Cursor、Claude Code、DeepSeek 等宿主不同，合法治理资产的机器判据不能不同。required validation 失败即 fail closed，不能用模型判断、其他 CI 绿色或 prose 看似合理代替。

当前 canonical stdlib validator：

```text
.agents/skills/coding/scripts/governance_contract.py
```

无 import 集成的宿主调用其 CLI；目标项目可以直接调用 Runtime 安装后的同路径受管 projection，并只在仓库自有 adapter 中处理 Carrier、CI、平台 API 等项目事实。机器 Contract 只校验稳定身份、结构和 Acceptance；语义充分性仍归 Requirement Review、Completion Audit、Review。

## 1. Change：模板是唯一结构 Owner

Ref25 的历史兼容与当前新建必须机械区分：

```text
已有历史 identity
→ 日期级或当前秒级格式均可按既有 parser 读取

新建 / 本 PR 新增或修改实例
→ 只允许 CHG-YYYYMMDD-HHMMSS-kebab-case
```

低层 parser、`depends_on` 或显式 legacy `--id` 只代表历史 identity 可处理，**不授权新的日期级 Change 进入交付链**。正常新建使用 `new-change --slug`；其他宿主直接写文件也必须产生相同 current identity。PR 对新增/修改 Active Change 执行 new-instance validation；历史 archive 不批量改名、改正文或按新 Profile 迁移。

新实例结构直接以 canonical [`../assets/CHANGE.template.md`](../assets/CHANGE.template.md) 为 Profile：validator 动态读取有序一级标题；风险级别额外必需的二级结构由模板内 `governance:required-for=<level>` marker 定义，validator 不维护第二份标题清单。至少要求当前 schema、秒级 ID、目录/frontmatter identity 一致、L2/L3、模板结构完整/唯一/有序。`ready_check.py` 继续拥有 Traceability/Completion/Ready；new-instance validator 只回答“是否按当前 Contract 新建/修改”。

## 2. Requirement Source：canonical Issue Form 是默认 GitHub Profile Owner

Issue 公共生命周期仍归 Ref18。GitHub 默认 Profile 的唯一人工维护源位于：

```text
.agents/skills/coding/assets/issue-templates/
├── 01-requirement.yml
├── 02-bug.yml
├── 03-technical-change.yml
└── config.yml
```

Agent_Skills 自身和没有显式更强项目 Profile 的 Runtime 目标项目，其仓库根 `.github/ISSUE_TEMPLATE/*.yml` 都只是上述 canonical assets 的**原字节受管投影**，不得单独编辑。`governance_contract.py` 直接从 canonical Form 的 title prefix 与 field 自身 `validations.required=true` 的 textarea label 恢复机器 Profile，因此 Form 改名/增删 required 语义段时不需要同步维护第二份 `ISSUE_TYPE_PROFILES`。

machine validator 机械化：

- title 必须唯一匹配 canonical Form 的类型前缀；
- 类型对应 required textarea labels 必须在 live Issue 中存在且唯一；
- `- [ ] AC1：...` / `- [x] AC1：...` 稳定 task list；
- AC 从 1 连续且唯一；
- Closure 校验时所有适用 AC 已写回完成状态。

项目如果**正式声明了更强且项目自有** Issue/Ticket Profile，可以在 canonical minimum 上增加字段或改用其他平台载体；该 Overlay 必须显式属于项目，不能通过复制 Agent_Skills 默认 Form 后再把副本当第二个通用 Owner。AIMA_UGC 这类没有额外 Profile 需求的项目应直接使用 generated projection。

即使通过 API/Agent 绕过 Form UI，live Issue 仍必须满足同一 machine Contract；Comment-only Evidence 不能替代 body Acceptance Owner。

## 3. Mutation 写前、写后同检

Issue 创建/实质更新：

```text
canonical Contract + 显式项目 Overlay（如有）
→ candidate validate
→ write
→ read live Issue
→ same validate
→ resolved
```

Issue Closure：按 Ref18 完成 Evidence/Acceptance 回写后，以 `require_all_checked=true` 校验；reread 后再校验，之后才 close，并再次确认 closed 与 Acceptance 未漂移。

Change 创建/更新：

```text
canonical Change Template + project Carrier
→ generate/write candidate
→ new-instance validate
→ commit/PR changed-scope 再验证
→ Ready Check / Completion / Review
```

没有本地 shell 时改用宿主等价 API 写入与 readback；不得退回“模型自行确认格式”。

## 4. Project Payload 与首次安装投影

Change Template、canonical Issue Form assets、`governance_contract.py` 都位于 Coding 的现有 Runtime Project Payload 范围，**不为治理模板新增第二套分发清单或 Payload schema**。

干净首次安装时：

```text
Project Payload canonical issue-templates
→ preflight 目标 .github/ISSUE_TEMPLATE
├─ 目标不存在：原字节写入
├─ 已存在且字节完全一致：幂等通过
└─ 已存在但不同：fail closed，不覆盖项目文件
→ 与现有 install_project 共用事务失败边界
```

本 Contract **不自动承诺旧版本升级同步**。除非新的 Requirement Source 明确要求，否则 canonical Form 变化后如何迁移已有旧 Runtime 安装属于独立任务；不能为了假设的未来升级在当前首次安装路径增加 alias、双读写或猜测 ownership。

项目永久 CI 可以调用 installed canonical validator 的 `validate-projection` / 等价 import 检查根 Form 是否仍与 canonical asset 原字节一致；项目 adapter 只拥有 Carrier、CI 调用、平台 API 与显式更强 Overlay，不复制 title/heading/AC/Change ID 等通用规则。

## 5. 失败边界

- 新 Change / live Issue 不合规 → 阻塞 Ready/merge/closure；
- 根 Issue Form projection 与 canonical asset 漂移 → 阻塞项目治理 gate；
- 首次安装遇到不同内容同名 Form → fail closed，不覆盖；
- candidate 与 live 不一致 → 以 live 为事实重验，无法安全恢复则 `blocked/unresolved`；
- 项目明确更强 Profile → 遵守项目；项目无额外 Profile → 使用 canonical projection；
- 已关闭 Issue / 历史 archive 默认不迁移；
- Rule、template/Form、validator、CLI/CI/tests、受影响 Runtime/Project Payload 任一不同步 → 按 Mutation Impact Audit 保持 NOT_READY。

## 6. 完成判据

```text
canonical Rule
+ Change Template
+ canonical Issue Forms
+ validator
+ source/root/project projection parity
+ 实际项目/PR gate
+ 永久正反例
+ 受影响 Source/Runtime/Project Payload parity
+ Review
+ current-head / main-fresh required CI
```

完成证明不是“某个 Agent 这次生成正确”，而是任何宿主产生的不合规治理资产或手改 generated projection 都会被同一 Contract 稳定拒绝。