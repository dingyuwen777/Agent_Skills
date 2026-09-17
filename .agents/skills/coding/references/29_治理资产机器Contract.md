<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.30","触发":{"任一":[{"包含":{"维度":"意图","取值":["Issue/工单治理"]}},{"包含":{"维度":"治理","取值":["存在活动变更","多个活动变更","要求变更记录","要求完成门禁"]}}]},"依赖":["coding.reference.18","coding.reference.25"],"最低风险":"L2"}
-->

# 治理资产机器 Contract

本 Reference 负责把 Change 与 GitHub Requirement Source 的**稳定治理语义**落实成宿主无关的机器 Contract。自然语言规则继续由 Change、Requirement Source、Git/Review 等现有 Owner 负责；本文件不复制第二套业务流程，只规定：**任何宿主只要创建、实质更新、交付或关闭这些治理资产，都必须通过同一机器验证。**

目标是让 ChatGPT 网页端、Codex、Cursor、Claude Code、DeepSeek Harness、其他本地 Agent 或托管 API 的差别只停留在“如何读写”，不能改变“什么治理资产算合法”。

## 1. 单一 Contract 与宿主边界

治理资产的约束链固定为：

```text
canonical 自然语言 Owner
→ canonical machine validator / template / metadata
→ 项目 Profile / Carrier Overlay（可以更强，不能更弱）
→ 宿主生成或写入
→ 写后读取真实实例
→ 同一 machine Contract 验证
```

硬规则：

- generator、GitHub Form、网页表单都只是**便利入口**，不是合法性的最终 Owner；
- Agent 直接使用 GitHub API、Contents API、Git Data、文件写入或其他宿主能力时，不能因为绕过 UI / generator 就降低 Contract；
- 机器 Contract 验证失败时 fail closed：不得以“内容看起来合理”“CI 其他部分绿色”或“这是不同模型生成的”继续进入 Ready / merge / closure；
- 项目可以通过 Issue Form、Ticket schema、carrier、CI 等增加更强字段和门禁，但不得删除 canonical minimum；
- 不比较 prose 是否逐字一致，只机器化稳定身份、必需语义段、Acceptance、生命周期和结构；完整性/方案质量仍由 Requirement Review、Completion Audit 与独立 Review 判断。

当前 canonical stdlib validator：

```text
.agents/skills/coding/scripts/governance_contract.py
```

没有 Python import 集成的宿主可以调用其 CLI；能够直接加载模块的项目 adapter 可以复用同一函数。Runtime / Project Payload 分发必须让正式安装后的 machine tooling 与当前 canonical 同版本；Source Mode 仍从当前 canonical Source 取得规则，不把目标项目安装副本当 canonical。

本 Reference 只在**真实治理资产操作**出现时加载：创建/更新/关闭 Issue/工单，或当前任务已经存在/要求持久 Change、完成门禁。普通 Git Delivery / PR 交付如果没有这些事实，继续由既有 Requirement/Git Owner 与 CI 的机器 gate 承担，不为了说明同一门禁而预加载 carrier 细节或扩大上下文。

## 2. Coding Change：历史可读与当前新建必须分离

`coding-change/v1` 的**历史解析兼容**与**新建实例 Contract**是两件事：

```text
读取已有历史
→ 允许已经存在的 CHG-YYYYMMDD-kebab-case
→ 也允许当前 CHG-YYYYMMDD-HHMMSS-kebab-case

新建 / 本 PR 新增 / 当前 changed 新实例
→ 只允许 CHG-YYYYMMDD-HHMMSS-kebab-case
```

因此：

- `coding.py` 的宽松历史 parser、`depends_on` 兼容或显式 legacy `--id` 能力，只表示**可以读写/处理已知历史身份**；它们不能被解释为“新交付 Change 允许继续创建日期级 ID”；
- 正常新建必须优先使用 `new-change --slug`；其他宿主直接创建文件时也必须产出同样的秒级 identity；
- PR / delivery 对本次新增的 Change 必须调用 current/new machine validation；新的 date-only Change 即使 `ready_check.py` 能按历史 schema 解析，也必须在 new-instance gate 失败；
- archived 历史 Change 不批量重命名、不回写正文、不为了新 Contract 重跑新实例校验；历史不可变边界继续由项目 carrier / archive Owner 负责。

### 当前 Change Profile

新 `coding-change/v1` 的结构事实源是 canonical [`../assets/CHANGE.template.md`](../assets/CHANGE.template.md)。validator 从模板**动态提取有序一级标题**，不在代码中维护第二份完整章节列表；因此模板结构升级后，generator 与 new-instance validation 同步收敛。

新实例至少必须满足：

- `schema: coding-change/v1`；
- current 秒级 Change ID，且目录 ID 与 frontmatter `id` 一致；
- 持久 Change 风险为 L2/L3；
- canonical 模板全部一级结构存在、唯一且顺序一致；
- L3 额外保留真实方案取舍入口，例如 `备选方案与取舍`；没有有意义备选时可以写“不适用 + 事实依据”，不能删结构来规避 L3 责任。

`ready_check.py` 继续负责 Requirement Traceability / Completion Audit / Ready 与历史兼容；new-instance validator 负责“这是不是按**当前** Contract 新建的治理资产”。两者责任互补，不互相替代。

## 3. GitHub Requirement Source：UI Form 与 API 必须同效

GitHub Issue 的公共 Contract 继续由 [17_需求来源与PR追溯治理.md](17_需求来源与PR追溯治理.md) 拥有。machine validator 对三类默认 Profile 固定验证：

```text
[需求]
[缺陷]
[技术变更]
```

每类只机器校验稳定语义：

- 标准类型标题前缀；
- 当前 Profile 的必需语义段；
- `- [ ] AC1：...` / `- [x] AC1：...` 形式的 task list；
- Acceptance ID 必须从 AC1 连续、唯一；
- closure validation 时所有仍适用 AC 必须已完成正式处置并写回最终状态。

项目 Issue Form 是项目/平台 UI Profile：可以增加字段，也可以对 wording 做项目化，但如果继续使用 canonical GitHub Requirement Source Contract，就必须保持等价的 machine semantics。没有安装 Form、通过 API 创建、由 Agent 自动创建或修改 Issue，都不能成为绕过理由。

## 4. Mutation 前后都验证，而不是只在 CI 最后兜底

### Issue 创建 / 实质更新

```text
读取当前 Requirement Source Contract + 项目 Profile
→ 生成 candidate title/body
→ candidate machine validation
→ 写 GitHub
→ 重新读取 live Issue
→ 对 live title/body 执行同一 machine validation
→ 通过后才可把 Requirement Source 视为 resolved
```

### Issue Closure

```text
重新读取 live Issue
→ Requirement → Evidence Closure Audit
→ 回写 body Acceptance task list
→ machine validation(require_all_checked=true)
→ 重新读取 live Issue
→ 再次 machine validation(require_all_checked=true)
→ close
→ 再次读取确认 closed + Acceptance 仍存在
```

Comment-only Evidence 不能代替 body Acceptance Owner；机器 validator 也不能替代 Evidence Sufficiency 的人工/专业判断。

### Change 创建 / 实质更新 / PR Ready

```text
当前 canonical template + carrier
→ generator 或宿主直接生成
→ new-instance machine validation
→ 写入 / 提交
→ PR changed-scope 再验证 current identity/profile
→ Ready Check + Completion Audit + Review
```

如果宿主没有本地 shell，使用等价 API 写入后仍必须读取真实 blob / PR / Issue，并用可用的 machine validator/项目 adapter 验证；不能因为 CLI 不可用退回“模型自行判断格式”。

## 5. 项目 Overlay 与分发

目标项目可以把 canonical machine Contract 投影到：

- `.github/ISSUE_TEMPLATE/*.yml`；
- 项目 Requirement Source checker；
- 项目 Change carrier checker；
- required CI；
- 非 GitHub 平台的 ticket/work-item schema。

项目层只拥有自己的 Profile、Carrier、CI 接线和更严格字段，不复制 Agent_Skills 的完整自然语言规则。Runtime / Project Payload 安装资产属于正式分发结果；需要升级它们时走正式 install/upgrade，不手改目标项目受管 `.agents` 来冒充 canonical 更新。

## 6. 失败与兼容边界

- 新实例 machine validation 失败：阻塞该治理资产的 Ready / merge / closure；不自动改写历史。
- live readback 与 candidate 不一致：以 live 实例为事实，重新校验；无法安全恢复则 `blocked/unresolved`。
- 项目 Profile 比 canonical 更强：遵守项目 Profile；项目 Profile 更弱：canonical minimum 仍必须满足。
- 历史 archive / 已关闭历史 Issue：默认不批量迁移，除非用户或正式 Owner 明确发起独立历史审计。
- validator、template、Issue Form、parser、CLI、CI、Runtime/Project Payload 任一受影响层不同步时，按 Skill Mutation Impact Audit 保持 NOT_READY。

## 7. 完成判据

一次治理资产 Contract 变更只有在以下链路都成立时才完成：

```text
canonical Rule
+ machine validator
+ template / Issue Profile
+ parser / CLI
+ 项目 adapter / CI（真实消费者）
+ 永久正反例
+ Source/Runtime/Project Payload 受影响 parity
+ 独立 Review
+ current-head / main-fresh required CI
```

任何单一宿主“这次生成对了”都不是完成证据；完成标准是不同写入路径生成的不合规实例会被同一 Contract 稳定拒绝。
