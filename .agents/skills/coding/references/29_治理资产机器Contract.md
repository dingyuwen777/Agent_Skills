<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.30","触发":{"任一":[{"包含":{"维度":"意图","取值":["Issue/工单治理"]}},{"包含":{"维度":"治理","取值":["存在活动变更","多个活动变更","要求变更记录","要求完成门禁"]}}]},"依赖":["coding.reference.18","coding.reference.25"],"最低风险":"L2"}
-->

# 治理资产机器 Contract

本 Reference 只拥有一个新增责任：把 Change 与 GitHub Requirement Source 已由 Ref18/Ref25 定义的**稳定语义**落实成宿主无关机器 Contract。自然语言生命周期、Evidence、Carrier 与 Closure 仍由既有 Owner 负责，不在这里复制。

```text
canonical Owner + machine validator/template
→ 项目 Profile/Carrier（可更强，不可更弱）
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

无 import 集成的宿主调用其 CLI；项目 adapter 可复用等价投影。机器 Contract 只校验稳定身份、结构和 Acceptance；语义充分性仍归 Requirement Review、Completion Audit、Review。

## 1. Change：历史读取与新实例分离

Ref25 的历史兼容与当前新建必须机械区分：

```text
已有历史 identity
→ 日期级或当前秒级格式均可按既有 parser 读取

新建 / 本 PR 新增实例
→ 只允许 CHG-YYYYMMDD-HHMMSS-kebab-case
```

低层 parser、`depends_on` 或显式 legacy `--id` 只代表历史 identity 可处理，**不授权新的日期级 Change 进入交付链**。正常新建使用 `new-change --slug`；其他宿主直接写文件也必须产生相同 current identity。PR 对新增 Change 执行 new-instance validation；历史 archive 不批量改名、改正文或按新 Profile 迁移。

新实例结构直接以 canonical [`../assets/CHANGE.template.md`](../assets/CHANGE.template.md) 为 Profile：validator 动态读取有序一级标题，不维护第二份完整章节表。至少要求当前 schema、秒级 ID、目录/frontmatter identity 一致、L2/L3、模板一级结构完整/唯一/有序；L3 还必须保留方案取舍入口（无备选时写不适用及依据）。`ready_check.py` 继续拥有 Traceability/Completion/Ready；new-instance validator 只回答“是否按当前 Contract 新建”。

## 2. Requirement Source：Form 与 API 同效

Issue 公共生命周期仍归 Ref18。machine validator 只机械化稳定默认 Profile：

- 标题类型 `[需求]` / `[缺陷]` / `[技术变更]`；
- 类型对应必需语义段；
- `- [ ] AC1：...` / `- [x] AC1：...` 稳定 task list；
- AC 从 1 连续且唯一；
- Closure 校验时所有适用 AC 已写回完成状态。

项目 GitHub Form 可以增加字段或项目化 wording，但不能弱于 canonical minimum。即使通过 API/Agent 绕过 Form UI，live Issue 仍必须满足同一 machine Contract；Comment-only Evidence 不能替代 body Acceptance Owner。

## 3. Mutation 写前、写后同检

Issue 创建/实质更新：

```text
Contract + 项目 Profile
→ candidate validate
→ write
→ read live Issue
→ same validate
→ resolved
```

Issue Closure：按 Ref18 完成 Evidence/Acceptance 回写后，以 `require_all_checked=true` 校验；reread 后再校验，之后才 close，并再次确认 closed 与 Acceptance 未漂移。

Change 创建/更新：

```text
current template/carrier
→ generate/write candidate
→ new-instance validate
→ commit/PR changed-scope 再验证
→ Ready Check / Completion / Review
```

没有本地 shell 时改用宿主等价 API 写入与 readback；不得退回“模型自行确认格式”。

## 4. Project Overlay、分发与失败边界

项目层只拥有自己的 Issue/Ticket Profile、Carrier、CI 接线及更强字段，不复制 Agent_Skills 完整规则。Runtime / Project Payload 若分发 machine tooling，必须与当前 canonical 同版本；Source Mode 仍从 canonical Source 取得治理正文。

- 新实例不合规 → 阻塞 Ready/merge/closure；
- candidate 与 live 不一致 → 以 live 为事实重验，无法安全恢复则 `blocked/unresolved`；
- 项目 Profile 更强 → 遵守项目；更弱 → canonical minimum 仍生效；
- 已关闭 Issue / 历史 archive 默认不迁移；
- Rule、template/Profile、validator、CLI/CI/tests、受影响 Runtime/Project Payload 任一不同步 → 按 Mutation Impact Audit 保持 NOT_READY。

## 5. 完成判据

```text
canonical Rule
+ validator
+ template / Issue Profile
+ 实际项目/PR gate
+ 永久正反例
+ 受影响 Source/Runtime/Project Payload parity
+ Review
+ current-head / main-fresh required CI
```

完成证明不是“某个 Agent 这次生成正确”，而是任何宿主产生的不合规新治理资产都会被同一 Contract 稳定拒绝。
