---
schema: coding-change/v1
id: "CHG-20260830-clickable-markdown-navigation"
title: "统一 Markdown 可点击文档导航"
level: L2
status: ready_for_review
owner: "dingyuwen777"
branch: "chore/clickable-markdown-navigation"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "全仓 Markdown 文档导航"
  - "Skill / Reference 可达性"
  - "Markdown 导航格式永久回归"
affected_paths:
  - "AGENTS.md"
  - "README.md"
  - "USAGE.md"
  - "runtime/README.md"
  - ".agents/**/*.md"
  - ".agents/skills/coding/scripts/coding.py"
  - "runtime/agent_skills_runtime/project_installer.py"
  - ".agents/skills/coding/tests/"
contracts:
  - "Markdown 具体文档导航展示约定"
data_changes: []
---

# 目标

系统检查仓库当前全部 Markdown，把承担“读取/跳转到另一个真实仓库文档”职责的具体 Markdown 文件路径统一为可点击链接，同时在链接文字中保留完整可读路径，避免纯代码块或纯 inline-code 路径只能复制、不能直接打开。

# 成功标准

- [x] 全仓 Markdown 中用于文档导航的具体仓库 Markdown 路径统一使用可点击 Markdown link，并在 link label 中显示路径本身。
- [x] 用户截图对应的 Bootstrap / managed block 导航及同类写法全部处理，不只修单个 Reference。
- [x] 命令、目录树、glob、协议/流程图、生成路径、目标项目占位路径和代码示例不被机械转换成链接。
- [x] 所有新增链接目标均能解析到当前仓库真实 Markdown 文件，不制造死链。
- [x] 增加永久回归，后续新增“导航用途的真实 Markdown 路径但不可点击”时 CI 能失败并给出文件/行号。
- [x] 规则语义、Stable Reference ID、routing metadata、依赖、风险下限和 Runtime Contract 均保持不变。

# 范围

- 根 Markdown、人类说明、Maintenance/Router、四个 Skill、全部 canonical References、Markdown 模板/运行说明中的文档导航格式。
- 新增 Markdown 导航链接静态回归测试。
- 仅为链接成立而做的最小文案/列表/表格格式调整。
- `AGENTS.managed.md` 属于“源模板位置与目标项目根输出位置不同”的生成资产，因此 Coding Bootstrap 与 Runtime Installer 只增加相对链接上下文转换，不改变 managed block 的路由语义。

# 非目标

- 不把所有反引号路径都改成链接。
- 不把命令、目录树、状态机/流程图、glob、协议字段、Runtime 安装路径或目标项目自己的文件路径改成仓库链接。
- 不修改任何 Skill/Reference 的触发条件、依赖、最低风险或 Stable ID。
- 不修改 Runtime Bundle、Project Payload、install、MCP、Task Route、Routing Manifest 协议。
- 不升级依赖，不发布 Release/tag。

# 必须保持不变

- 链接化只改变 Markdown 可用性，不改变规则内容与执行语义。
- Source Mode 仍读取同一 canonical 文件；Runtime Mode 仍通过 MCP required Context，不因 Markdown link 改变路由机制。
- 用户可见路径文字继续显示，不用“点这里”之类隐藏目标路径的文案替代。
- Project Payload 的最小 fixture/兼容输入不因本次表现层改动新增“必须包含 Markdown link”的隐藏 Contract；存在 canonical 源链接时才做目标根相对链接转换。

# 关键决策

1. **显示路径 + 可点击同时满足。** 统一使用 ``[`path/to/file.md`](relative-target.md)``，而不是只显示标题。
2. **导航才链接化。** fenced code block 仍用于命令、流程、目录结构和数据示例；如果某个 block 的主要用途只是告诉读者“去读这个真实 Markdown 文件”，则改成普通 Markdown link。
3. **相对链接优先。** 链接 target 使用从当前 Markdown 文件可解析的仓库内相对路径，避免绑定 GitHub 域名/branch。
4. **永久回归以真实路径解析约束，避免机械误报。** 测试只认领当前仓库可解析的具体 Markdown 文件；含 glob/placeholder 的路径、目标项目 Overlay 和协议示例不作为违规。
5. **生成型 Markdown 必须按最终输出位置验证。** `AGENTS.managed.md` 在源资产位置显示 `../../ROUTER.md`，生成到项目根时转换为 `.agents/skills/ROUTER.md`；`CHANGE.template.md` 使用在模板源位置与生成 Change 位置都能解析的相对链接。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 检查所有文档中的同类纯路径导航 | user:scan-all-markdown-navigation | satisfied | Initial Red run `33295784345` 全仓扫描发现 100 处违规，集中在 19 份正式 Markdown；最终同一永久回归为 Green |
| R2 | 路径文字保留且可以直接点击打开文件 | user:clickable-path-label | satisfied | 3 条 Markdown 导航永久回归均通过；19 份 Markdown 的 link label 保留原路径文本，所有 repo-relative target 可解析 |
| R3 | 不因格式统一误改命令/示例/流程语义 | .agents/skills/coding/references/15_规则内容守恒与Skill维护.md | satisfied | PR diff 人工内容守恒 Review / re-review `NO_FINDINGS_WITHIN_SCOPE`；命令/流程/glob/协议示例未机械链接化；routing digest 仍为 `600a9f493fb669addf53eff1ee55533091c1ffe344e4883528392af81116dc7e` |
| R4 | 按仓库门禁完成 PR、main fresh CI 与 Change 清理 | .agents/MAINTENANCE.md | explicitly_deferred | Draft #48 Final Ready CI 已全绿但 Draft→Ready 因连接器 `Repository.fullDatabaseId` 缺陷失败；#48 已关闭未合并，非 Draft #49 已建立，仍需其最终 HEAD 永久 CI、正常 merge、main fresh CI 与独立 Active Change 清理 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Final Ready run `33296569104`：172 self-contained tests 全部 OK，含 3 条 Markdown 导航永久回归 |
| 接口 / Contract | required | Stable ID / trigger / dependency / risk floor 均未修改；routing digest 与基线相同；最小 Payload fixture 在修复过度约束后全部回归 Green |
| 集成 / Persistence / Runtime Dependency | required | Final Ready run `33296569104`：Bundle build/status/self-test、real stdio MCP、project install/repeat/no-args install 全部通过 |
| 用户 / Workflow Acceptance | required | link label 显示完整路径；目标解析测试证明仓库内 target 存在；Coding Bootstrap 与 Runtime Installer 均证明生成项目根 AGENTS 使用 `.agents/skills/ROUTER.md` 可点击链接 |
| 跨组件 Golden Path | required | Linux onefile → status/self-test → real MCP → project install/no-args install 全部 Green |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider、网络 Contract 或现时服务事实变化 |
| Build / Package / Runtime | required | Final Ready run `33296569104`：Skill Tests、Runtime Windows Package、Runtime macOS Package 三个 Job 全部 success |
| Docs / Governance / Other | required | 19 份生产 Markdown 完成路径链接化；内容守恒 Review `NO_FINDINGS_WITHIN_SCOPE`；Final Ready Check success；Draft #48 关闭未合并，非 Draft #49 接棒 |

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取用户“检查所有文档并统一修改”的要求、当前分支 AGENTS、Maintenance、Coding 两阶段复核、Skill 内容守恒和 Review Skill/审查执行/测试充分性规则。
- [x] change_coverage：Initial Red 定位的 100 处 / 19 份 Markdown 均由最终链接扫描覆盖；最终 changed files 与人工 diff 复核确认没有遗留一次性 normalizer/workflow。
- [x] reverse_audit：从每个 path-label link 反查当前仓库真实 Markdown target；对 `AGENTS.managed.md` / `CHANGE.template.md` 额外从最终生成位置反查；Runtime/Payload/Router 现有链保持 Green。
- [x] unresolved_cleared：R1–R3 satisfied；R4 仅为必须发生在 Ready 后的正式交付生命周期 `explicitly_deferred`；无 `not_satisfied`。

# 任务

- [x] 读取当前 main/feature 的 AGENTS、Maintenance、Router、Coding 和 Skill Mutation 内容守恒规则。
- [x] 新增全仓 Markdown 导航可点击性回归并确认精确 Red：run `33295784345` 只由新增导航扫描失败，列出 100 处 / 19 份 Markdown。
- [x] 根据 Red/人工审查统一修改所有同类导航表达。
- [x] 为生成型 managed block 增加第二条 Red：run `33296121055` 只暴露项目根 AGENTS 仍携带源相对链接；随后修正 Coding/Runtime 输出上下文。
- [x] 处理 run `33296262526` 暴露的 9 个既有 installer fixture 回归：修复 Runtime helper 过度 fail-closed，不修改/削弱那 9 个测试，也不新增 Payload Contract。
- [x] run `33296394119`：172 tests、Linux onefile/MCP/install、Windows/macOS package/install 全部 Green；Linux Job 唯一失败为当时 Change 仍 `proposed` 的 Ready Gate。
- [x] 完成独立 Review / re-review，结论 `NO_FINDINGS_WITHIN_SCOPE`。
- [x] Draft #48 Final Ready HEAD `a2a57d75d763d79967145f5343deebd20f28b8a8` 的 run `33296569104` 三个永久 Job 全部 success，含 172 tests 与 Ready Check；Draft→Ready 因连接器 GraphQL schema 缺陷失败，#48 已关闭且未合并。
- [ ] 非 Draft PR #49 在本次治理提交后的最终 HEAD 自行取得永久三平台 CI，随后正常合并；main fresh CI 后删除 Active Change。

# 验证

## TDD / 回归证据

1. **Initial Red — `33295784345`**
   - 171 tests；原有 169 tests 全部通过。
   - 新增 target-resolution 测试通过。
   - 只有“真实 Markdown 导航必须可点击”失败，输出 100 处违规 / 19 份 Markdown。
2. **Generated Markdown Red — `33296121055`**
   - 172 tests；只有生成项目根 `AGENTS.md` 的 Router link 仍为源目录相对路径这一条新回归失败。
3. **相邻回归发现 — `33296262526`**
   - Runtime helper 初版把 canonical link 变成最小 Payload fixture 的新强制 Contract，导致 9 个既有 installer/portability 用例统一 `ValueError`。
   - 修复生产 helper 为“存在源链接则转换，不存在则原样保留”；未修改这 9 个测试。
4. **Pre-Ready Green — `33296394119`**
   - `Ran 172 tests ... OK`；Linux onefile/MCP/install、Windows/macOS package/install 全部成功。
   - 唯一 Job 失败是 Ready Check 对当时 `status: proposed` 的预期拒绝。
5. **Final Draft Ready — `33296569104`**
   - HEAD `a2a57d75d763d79967145f5343deebd20f28b8a8`。
   - Skill Tests、Runtime Windows Package、Runtime macOS Package 三个 Job 全部 success。
   - 172 tests、Ready Check、Linux onefile/status/self-test/MCP/install 与 Windows/macOS package/install 全部通过。

## Markdown 覆盖事实

最终生产 Markdown 修改共 19 份：

- 根/维护：`AGENTS.md`、`README.md`、`.agents/MAINTENANCE.md`、`.agents/skills/ROUTER.md`、`runtime/README.md`；
- Coding Core / assets / references：Coding `SKILL.md`、`AGENTS.managed.md`、`CHANGE.template.md`、references 01/02/07/12/13/15/16；
- Docs：`docs/SKILL.md`、`docs/references/04_与Coding协作.md`；
- Review：`review/SKILL.md`、`review/references/01_审查执行流程.md`。

`USAGE.md` 和其余 Markdown 没有命中“当前仓库真实 Markdown 导航但不可点击”的规则，因此不制造无意义 diff。

# 独立 Review

Review Target：Draft PR #48 与同一实现分支；正式交付由非 Draft PR #49 承接。

模式：review-and-fix（用户已授权本次实现与交付）。

重点风险：

- 是否只改路径表现而丢失规则正文；
- 是否误把命令、目录树、flow/protocol/glob/目标项目路径改成源仓库链接；
- relative link 是否真实存在、是否越出仓库；
- 生成型模板在源位置可点击但输出位置失效；
- Runtime helper 是否借表现层变化扩大 Project Payload Contract；
- routing metadata / Stable ID / trigger / dependency / risk 是否漂移；
- 一次性 normalization 工具是否遗留正式仓库。

结论：`NO_FINDINGS_WITHIN_SCOPE`。

re-review 结果：

- 19 份 Markdown 的生产 diff 均保留原路径文字，只增加 link target 或把纯文档路径 fenced block 转成 link/list；未删除触发、例外、失败、验证或 Ownership 规则。
- 所有 path-label repo links 通过目标存在性/仓库边界回归。
- `AGENTS.managed.md` 源位置与 Coding/Runtime 生成项目根位置均有独立断言；`CHANGE.template.md` 链接 target 在模板位置和生成 Change 位置均可解析。
- Runtime 最小 Payload fixture 不再被要求携带 canonical Markdown link，9 个原有测试恢复 Green。
- Final Ready `routing_digest` 与变更前保持一致；`source_digest` 因 canonical Markdown bytes 改变而变化，属于预期。
- 临时 normalizer / temporary workflows / patch helpers 已全部删除，不在正式 changed files 中。

# 文档影响

- 本 Change 本身就是 Markdown 可用性统一，因此正式文档影响为 `full scoped navigation audit`，但不是机械全文改写：只处理当前仓库真实 Markdown 导航路径。
- README、Maintenance、Router、Skill/References、runtime README 已按扫描事实同步。
- `USAGE.md` 未命中同类问题，保持不变。

# Contract / Schema / Migration / 依赖

- Markdown 导航展示约定：新增“路径 label + repo-relative link”的维护约定，并由永久测试守护。
- Stable Reference IDs：不变。
- routing trigger / dependency / risk floor：不变。
- Bundle / Project Payload / install / MCP / Task Route / Routing Manifest 协议：不变。
- Runtime Installer 只对 canonical managed asset 中已存在的源链接做目标根相对链接转换，不新增 Payload schema/字段/兼容要求。
- Schema/Migration/数据：无。
- 依赖/lock：无变化。

# 交付

- Branch：`chore/clickable-markdown-navigation`。
- Draft PR #48：已关闭、未合并；原因是 Draft→Ready GitHub 连接器 GraphQL schema 缺陷，不是仓库/CI 拒绝。
- 非 Draft PR #49：`统一 Markdown 文档路径为可点击导航`，继续使用同一分支；必须在本次治理提交后的最终 HEAD 自行通过永久 CI 后才合并。
- Release：本 Change 不创建。
- Post-merge：必须验证 main fresh CI，再删除当前 Active Change；由 Git/PR 保留历史，不创建 Change archive。
