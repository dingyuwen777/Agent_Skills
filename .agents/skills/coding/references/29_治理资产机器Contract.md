<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.30","触发":{"任一":[{"包含":{"维度":"意图","取值":["Issue/工单治理"]}},{"包含":{"维度":"治理","取值":["存在活动变更","多个活动变更","要求变更记录","要求完成门禁"]}}]},"依赖":["coding.reference.18","coding.reference.25"],"最低风险":"L2"}
-->

# 治理资产机器 Contract

本 Reference 只负责把 Ref18/Ref25 已定义的 Change 与 Requirement Source 稳定语义落实成**宿主无关机器 Contract**，并固定模板/Profile/validator 的 canonical Ownership。生命周期、Evidence、Carrier、Closure 和 Runtime 安装事务仍由既有 Owner 负责，不在这里复制。

```text
canonical template / Issue Form / validator
→ 受管 projection
→ 项目 Carrier / CI adapter（可更强，不复制通用规则）
→ candidate validation
→ write
→ live readback
→ same validation
```

generator、GitHub Form、网页、CLI、Contents/Git Data API 都只是写入入口；ChatGPT、Codex、Cursor、Claude Code、DeepSeek 等宿主不同，合法治理资产的机器判据不能不同。required validation 失败即 fail closed，不能用模型判断、其他 CI 绿色或 prose 看似合理代替。

canonical stdlib validator：

```text
.agents/skills/coding/scripts/governance_contract.py
```

无 import 集成的宿主调用其 CLI；目标项目只在自己的 adapter 中处理 Carrier、CI、平台 API 和显式更强 Overlay。机器 Contract 只校验稳定身份、结构和 Acceptance，语义充分性仍归 Requirement Review、Completion Audit、Review。

## 1. Change：模板是唯一结构 Owner

历史 identity 与当前新建必须机械区分：

```text
已有历史 identity
→ 日期级或当前秒级格式均可按既有 parser 读取

新建 / 本 PR 新增或修改实例
→ 只允许 CHG-YYYYMMDD-HHMMSS-kebab-case
```

低层 parser、`depends_on` 或显式 legacy `--id` 只代表历史 identity 可处理，不授权新的日期级 Change 进入交付链。正常新建使用 `new-change --slug`；其他宿主直接写文件也必须产生相同 current identity。PR 对新增/修改 Active Change 执行 new-instance validation；历史 archive 不批量改名、改正文或按新 Profile 迁移。

新实例结构直接以 canonical [`../assets/CHANGE.template.md`](../assets/CHANGE.template.md) 为 Profile：validator 动态读取有序一级标题；风险级别额外必需的二级结构由模板内 `governance:required-for=<level>` marker 定义，不维护第二份标题清单。至少要求当前 schema、秒级 ID、目录/frontmatter identity 一致、L2/L3、模板结构完整/唯一/有序。`ready_check.py` 继续拥有 Traceability/Completion/Ready。

## 2. Requirement Source：canonical Issue Form 是 GitHub 默认 Profile Owner

GitHub 默认 Issue Form 的唯一人工维护源：

```text
.agents/skills/coding/assets/issue-templates/
├── 01-requirement.yml
├── 02-bug.yml
├── 03-technical-change.yml
└── config.yml
```

Agent_Skills 根和使用默认 GitHub Profile 的目标项目，其 `.github/ISSUE_TEMPLATE/*.yml` 都是 canonical assets 的**原字节受管投影**，不得独立编辑。`governance_contract.py` 从 Form 的 title prefix 与字段自身 `validations.required=true` 的 textarea label 恢复 Profile，因此 Form 改名或 required 段变化时不再同步维护第二份标题表。

machine validator 机械化：

- title 唯一匹配 canonical 类型前缀；
- 类型对应 required textarea labels 在 live Issue 中存在且唯一；
- `- [ ] AC1：...` / `- [x] AC1：...` 稳定 task list；
- AC 从 1 连续且唯一；
- Closure 时所有适用 AC 已写回完成状态。

项目若正式声明更强且项目自有的 Issue/Ticket Profile，可以在 canonical minimum 上增加字段或使用其他平台等价 Carrier；不能复制默认 Form 后把副本当第二个通用 Owner。API/Agent 绕过 Form UI 时，live Issue 仍必须满足同一 machine Contract；Comment-only Evidence 不能替代 body Acceptance Owner。

## 3. Mutation：写前写后同检

Issue 创建/实质更新：

```text
canonical Contract + 显式项目 Overlay（如有）
→ candidate validate
→ write
→ read live Issue
→ same validate
```

Issue Closure 按 Ref18 完成 Evidence/Acceptance 回写后，以 `require_all_checked=true` 校验；reread 后再校验，之后才 close，并再次确认 closed 与 Acceptance 未漂移。

Change 创建/更新：

```text
canonical Change Template + project Carrier
→ generate/write candidate
→ new-instance validate
→ commit/PR changed-scope 再验证
→ Ready Check / Completion / Review
```

没有本地 shell 时使用宿主等价 API 写入与 readback；不得退回“模型自行确认格式”。

## 4. Project Payload、首次安装与项目边界

Change Template、canonical Issue Forms、validator 都沿用 Coding 现有 Project Payload 分发，不新增治理专用 Payload schema或第二份清单。**具体安装事务、ownership、回滚和平台边界由 Ref13/Runtime Owner 负责**；本 Reference 只固定首次安装的治理结果：

```text
目标 Form 不存在 → 写入 canonical 原字节投影
目标 Form 已存在且完全一致 → 幂等通过
目标 Form 已存在但不同 → fail closed，不覆盖
```

本次 Contract 不自动承诺旧版本 projection 升级或迁移；没有新的 Requirement Source 时，不增加 alias、双读写或猜测 ownership。

项目永久 CI 可用 installed canonical validator 校验 projection parity。项目 adapter 只拥有 Carrier、CI 调用、平台 API 与显式更强 Overlay，不复制 title/heading/AC/Change ID 等通用规则。

## 5. 失败边界与完成判据

- 新 Change / live Issue 不合规 → 阻塞 Ready/merge/closure；
- Issue Form projection 漂移 → 阻塞治理 gate；
- 首次安装遇到不同内容同名 Form → fail closed；
- candidate 与 live 不一致 → 以 live 为事实重验，无法安全恢复则 `blocked/unresolved`；
- 已关闭 Issue / 历史 archive 默认不迁移；
- Rule、template/Form、validator、CLI/CI/tests、受影响 Runtime/Project Payload 任一不同步 → 按 Mutation Impact Audit 保持 NOT_READY。

```text
canonical Rule
+ Change Template
+ canonical Issue Forms
+ validator
+ projection parity
+ 实际项目/PR gate
+ 永久正反例
+ Source/Runtime/Project Payload parity
+ Review
+ current-head / main-fresh required CI
```

完成证明不是“某个 Agent 这次生成正确”，而是任何宿主产生的不合规治理资产或手改 generated projection 都会被同一 Contract 稳定拒绝。
