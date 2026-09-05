---
name: router
description: Agent_Skills 的唯一跨 Skill 控制面。每个任务先进入本 Skill，再按当前项目事实选择专业 Skill 与必需 References；Router 只负责路由、上下文和 Handoff。Use before every other Agent_Skills skill in Source Mode and Runtime Mode.
---

<!-- agent-routing:v1
{"协议":"Agent Skills Skill路由/v1","Skill":"router","触发":{"包含":{"维度":"风险","取值":["L1","L2","L3"]}}}
-->

# Agent Skills Router

本 Skill 是 Agent_Skills **唯一的跨 Skill Catalog / Router 事实源**。项目事实来自目标项目，专业方法归各 Skill；Router **只输出** Skill、required References、最低风险、Handoff 和失败边界。

## Anti-Agent Boundary

Router **不生成项目级执行计划**，不创建子 Agent，**不拆分或调度开发任务**，不维护任务队列或 Worker，**不接管专业 Skill**，也不执行代码/设计/文档/测试/Git/CI/发布/部署；多 Skill 只声明并集、顺序与交接。

## 1. 项目事实与确定性执行边界

先读目标项目当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等规则，再按任务需要读真实代码、Manifest/lock、Contract、Schema/Migration、配置、测试、CI、正式文档和设计事实。**项目自己的**事实优先于通用示例；语言、Runtime、框架、数据库、Owner、API/ABI/CLI、Schema、Provider、部署、Design Token/业务字段都不得猜，**不能单凭文件名推出 React、FastAPI、PostgreSQL**。

### 1.1 核验、决策、授权、证据与完成

- **事实恢复 / 核验**：默认由 Agent 自行查；能查出的不问。只有条款明确要求“提请用户 / Owner 决策 / 批准”且答案会实质改变业务/public Contract、Schema/数据、安全/权限、不可逆动作或重大技术路线时才问；已固化决定**不重复确认**。
- **Non-material Ambiguity Default**：未达到上述门槛时不阻塞、不提问；按“**项目既有模式 → 最小范围 → 最小副作用 → 最可逆 → 最少新机制**”自行决定，证据推翻后局部 re-plan。
- **Authorization Continuity**：已明确且未撤销的授权仅在**同目标、同范围、同副作用等级**跨 Handoff 延续，不重复确认。只读 < 测试资产写 < 生产代码写 < commit/push/PR < merge < Release < Deploy/生产变更；更高等级**不得继承升级**，必须已有对应 Requested Action + Effective Authorization。
- **Fresh Evidence Contract**：Evidence 绑定当前 **environment / Contract / Scope 与被验证的相关实现 revision**，且未发生会影响当前结论的变化即可复用；**不是由当前 Agent 启动**本身**不构成重新执行理由**。只有相关实现/Contract/输入/依赖/配置/环境/外部事实变化、现有证据不覆盖结论，或 **required gate** 明确要求 current-head/current-revision 时才重跑对应层；Change/Issue/PR 描述、Evidence 记录、排版等**不影响已验证边界的载体变化**不使开发侧 Evidence 失效。
- `完整验证证据 / 完整命令 / 完整输出` 只表示完整执行并检查**已选择的风险匹配 Evidence**，**不表示运行全仓测试、全部测试层或所有平台验证**；仍按 targeted-first 单调升级。
- **阻塞按依赖边界传播**：只停止依赖缺失事实/Context/工具/环境/权限的动作和声明；其他已授权且无依赖工作继续。required gate 受阻时整体才 `blocked/incomplete`。
- **Requested Outcome = Completion Scope**：用户请求决定终点，**能力存在不等于继续追求更远阶段**。`review-only` 到 Findings/Evidence；`test-only` 到 Test Target/Evidence/Gaps；`develop-and-submit` 到 PR Ready；`develop-and-deliver` 才进入 post-merge；`Mutation Audit / Proposal` 到建议/影响面/验证方案。

## 2. 正式 Skill Catalog

正式 Skill 从 `.agents/skills/*/SKILL.md` 动态发现；下表只作当前导航，**不是分发白名单**。

| Skill | 职责 | 入口 |
| --- | --- | --- |
| `router` | Router/Handoff | [`.agents/skills/router/SKILL.md`](SKILL.md) |
| `coding` | 研发、调试、验证治理、Git/交付 | [`.agents/skills/coding/SKILL.md`](../coding/SKILL.md) |
| `testing` | Test Strategy、Black-box/Journey/Regression | [`.agents/skills/testing/SKILL.md`](../testing/SKILL.md) |
| `review` | 独立 Review、Findings、Evidence | [`.agents/skills/review/SKILL.md`](../review/SKILL.md) |
| `docs` | 技术文档 | [`.agents/skills/docs/SKILL.md`](../docs/SKILL.md) |
| `figma` | Figma/Prototype/Ready | [`.agents/skills/figma/SKILL.md`](../figma/SKILL.md) |

Runtime、Project Payload、manifest、测试和 Release 继续动态发现。Review 只判断测试充分性；测试工程方法归 Testing。

## 3. Owner-gated 固定入口

1. 恢复最少充分项目事实；
2. 任务对象/专业意图选 Owner；项目形态、风险、工具链、范围、治理、授权、Capability 只细化已命中 Owner；
3. 实现/调试/TDD/CI/Git/Release → Coding；测试策略/功能/黑盒/Journey/探索式/系统性 Regression/独立验证 → Testing；源码/PR/diff 审查 → Coding + Review；Figma → Figma；技术文档 → Docs。共享 `审查/验证`、`能力=测试/Figma/Git` 不自行制造无关 Owner；
4. 仅在已命中 Owner 内匹配 Reference；显式 dependency 可跨 Skill；
5. 命中 Reference 必须在执行前取得**完整原文**；
6. 不机械读全部 Skills/References。

## 4. 双模式同源路由

Source/Runtime 使用同一 canonical metadata、Stable Reference ID、依赖和风险下限，只改变 Context 取得通路。

Owner 选择时 `项目形态 / 风险 / 工具链 / 范围 / 治理 / 授权` 是 refinement，不独立制造 Owner。固定点：

```text
任务事实
→ Skill Core Owner 投影取并集
→ Owner 内 Reference 匹配
→ dependency closure（可跨 Skill）
→ 风险/Owner 扩展后重复至稳定
```

未知项只扩大相关候选，不导出全库；授权只是事实，不授予权限。

### 4.1 Source Mode

```text
任务事实 → canonical Owner → required References → 读取当前完整原文
```

不得用历史聊天、摘要、旧缓存替代 canonical Source；**目标项目中的安装副本**（含 managed block）**不作为当前通用治理语义来源**，项目自有规则仍读取。Source Mode 不调用本地 Runtime MCP。

### 4.2 Runtime Mode

```text
agent_skills_route_contract
→ agent_skills_start_task
→ agent_skills_submit_route
→ agent_skills_load_required_context(路由令牌)
→ 事实变化时追加 submit/load
→ agent_skills_checkpoint
```

Runtime evaluator 执行同一 fixed-point；`load_required_context` 只返回 required Context；`checkpoint` 不冒充 Traceability/Completion/Review/Docs/测试/CI。每个 Context 校验 **SHA256**、字节数和完整原文。

同一任务的 Router/Core/Runtime/Bundle/routing identity/Project Payload 必须同源同版本；协议/digest/路由/完整性失败时不得用旧记忆冒充，按第 1.1 节传播 blocker。

## 5. 低歧义组合示例

| 案例 | 命中原因与叠加 | Source Mode 读取 | Runtime Mode 任务信号 |
| --- | --- | --- | --- |
| L1 机械修改 | 行为/接口/数据不变 | Coding + L1 | `执行模式=实现；风险=L1` |
| L2 Feature | 新增可观察行为；先建立最小充分任务契约 | Coding；Journey 按需 Testing | `执行模式=实现；阶段=功能开发；风险=L2` |
| L3 public API | public Contract | Coding + 完成；按门禁 Review | `执行模式=方案,实现；风险=L3；范围=公共契约,API` |
| Schema Migration | Schema/历史数据 | Coding + Migration/回滚 | `执行模式=方案,实现；风险=L3；范围=Schema,Migration` |
| Bug / Failure / Incident | 根因；独立回归按需 | Coding；按需 Testing | `执行模式=诊断,实现；阶段=缺陷修复` |
| Refactor / Performance | 基线/根因 | Coding | `执行模式=诊断,实现；阶段=重构/性能优化` |
| Frontend | UI 实现 | Coding Frontend；按需 Testing | `执行模式=实现；项目形态=前端Web；范围=前端；风险=L2` |
| Testing only | 真实测试意图 | Testing | `意图=黑盒测试/功能测试/探索式测试/独立验证；能力=测试` |
| Figma review-only | 普通设计审查 | Figma | `执行模式=审查；意图=Figma review-only；授权=允许只读` |
| Figma review-and-fix | 设计写入 | Figma；生产实现再 Coding | `执行模式=实现；意图=Figma review-and-fix；授权=允许修改项目` |
| Figma baseline-ready | 正式基线 | Figma | `执行模式=方案；意图=Figma baseline-ready；风险=L2/L3` |
| Figma → Code | Ready 后实现 | Figma + Coding | `执行模式=实现；意图=设计转代码；范围=前端` |
| Docs not_applicable | 无文档影响 | 当前专业 Skill | 不提交 Docs 意图 |
| Docs targeted | 局部文档 | Coding + Docs | `执行模式=实现；意图=Docs targeted` |
| Docs full | 广域文档 | Coding + Docs | `执行模式=实现；意图=Docs full；风险=L2/L3` |
| 文档 Review | 文档目标 | Docs | `执行模式=审查；意图=文档审查` |
| Code Review / Audit | 源码/PR/diff | Coding + Review；Gap 时 Testing | `执行模式=审查；意图=代码审查` |
| Dependency / Runtime Upgrade | 版本/Runtime | Coding | `执行模式=实现；意图=依赖升级/Runtime 升级` |
| Git / PR / Release | 交付 | Coding；按需 Review | `执行模式=Git,验证；阶段=交付；意图=Git 交付` |
| Runtime / Project Payload | MCP/安装分发 | Coding + Runtime References | `执行模式=实现；风险=L3；范围=Runtime,MCP` |
| Skill Mutation Audit / Proposal | 只读检查/方案 | 根 AGENTS + Mutation 公共 Owner | `执行模式=只读分析；意图=Skill Mutation Audit；授权=允许只读`；宽泛 `Skill Mutation` 未明确写入前也按 Audit-compatible |
| Skill Mutation Apply | canonical 写入 | Maintenance + Mutation Apply 门禁 | `执行模式=实现；意图=Skill Mutation Apply；治理=要求完成门禁；风险=L2/L3` |
| Greenfield | 新仓库 | Coding + Project Discovery | `执行模式=方案；项目形态=Greenfield；阶段=仓库初始化；风险=L2` |
| 复杂多 Skill 叠加 | 多真实 Owner | 命中并集 | 提交真实模式/范围/意图/治理/授权 |

## 6. Bootstrap / Runtime 专项路由

- 触发：安装/升级 Agent_Skills、AGENTS Bootstrap/managed block、Bundle/Routing/MCP/Project Payload/分发变化。
- 必须动作：恢复 installation/ownership/schema/宿主事实，读取完整 canonical Reference。
- 不适用：普通业务任务。
- 交接：[`12_目标项目安装与AGENTS_Bootstrap.md`](../coding/references/12_目标项目安装与AGENTS_Bootstrap.md)（`coding.reference.13`）→ 需要 Runtime 时 [`13_本地MCP_Runtime分发与原文上下文加载.md`](../coding/references/13_本地MCP_Runtime分发与原文上下文加载.md)（`coding.reference.14`）。
- 返回：smoke 后回 Coding 验证/Review/Git。
- 失败关闭：关键事实**无法读取**/验证时阻塞依赖动作，**不得假装**完成。

## 7. Figma 路由

- 触发：Figma 创建/修改/审查/Prototype/基线/Design-to-Code。
- 必须动作：读取 [`.agents/skills/figma/SKILL.md`](../figma/SKILL.md)；普通 review-only 不机械要求 `READY`，baseline-ready 才输出 **READY / READY_WITH_NOTES / NOT_READY**。
- 不适用：无 Figma 事实。
- 交接：设计 → Figma；生产实现 → Coding。
- 返回：普通 Review 到 Findings；正式基线 Ready 后按需 Coding/Testing/Review。
- 失败关闭：Figma/required Context 不可得时不冒充审查/Ready，其他无依赖工作继续。

## 8. Testing 路由

- 触发：真实测试意图或独立 Test Gap。
- 必须动作：读取 Testing。
- 不适用：隔离 L1、普通开发期最小 TDD；**不为了“走完所有 Skill”机械叠加 Testing**。
- 交接：Coding/Review → Requirement、Test Target、Gap。
- 返回：生产缺陷 → Coding；回归 → Testing；合并判断 → Review。
- 失败关闭：缺 Testing Context 时不冒充测试证据，其他无依赖工作继续。

## 9. Review 路由

- 触发：Code Review/Audit、专业独立 Review 或项目门禁；Figma/Docs 的“审查”不自动成为 Code Review。
- 必须动作：读取 [`.agents/skills/review/SKILL.md`](../review/SKILL.md)，独立重建要求并审 Findings/Evidence。
- 不适用：无源码/PR/diff Review 或独立门禁的任务。
- 交接：Review Target/base/head/上游事实 → Review；Test Gap → Testing。
- 返回：Finding → Coding；Regression → Testing；再 re-review。
- 失败关闭：缺目标/关键事实时不宣称 Review 完成/可合并。

## 10. Docs 路由

- 触发：文档影响或用户显式文档任务。
- 必须动作：读取 [`.agents/skills/docs/SKILL.md`](../docs/SKILL.md)，判断 not_applicable/targeted/full。
- 不适用：已证明无人类文档事实变化。
- 交接：实现事实/Docs Impact → Docs。
- 返回：完成回原 Skill；实现缺陷 → Coding。
- 失败关闭：缺事实时不写推测文档。

## 11. 失败、冲突与权限

- 必需 Skill/Router/Reference **无法读取**时阻塞依赖动作，**不得假装**已遵守；局部缺口不等于整个任务停止；
- 冲突遵守更高优先级、更具体规则；
- 不绕过 CI、**Branch Protection**、PR、Release、Migration、安全门禁；
- **没有相应授权**时不获得修改、Git、发布、部署权限；
- 不强推、重写共享历史或破坏性清理。

## 12. Router 维护边界

Router 只拥有发现、Owner-gated 加载和 Handoff；Coding/Testing/Review/Docs/Figma/Runtime 的专业细节各归其 Owner。不能为了入口自包含把专业细则复制回 Router/ENTRY/managed block。