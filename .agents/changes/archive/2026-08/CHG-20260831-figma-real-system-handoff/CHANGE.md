---
schema: coding-change/v1
id: CHG-20260831-figma-real-system-handoff
title: 强化 Figma 真实系统映射与 Design-to-Code 交付门禁
level: L2
status: done
owner: dingyuwen777
branch: change/figma-real-system-handoff
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - figma-skill
  - design-to-code
  - governance
  - tests
affected_paths:
  - .agents/skills/figma/SKILL.md
  - .agents/skills/figma/references/02_业务能力与真实系统映射.md
  - .agents/skills/figma/references/05_Design-to-Code交付门禁.md
  - .agents/skills/coding/tests/test_figma_skill.py
contracts: []
data_changes: []
---

# 目标

把“Figma 只表达设计意图，生产实现必须服从目标项目真实 Contract、Capability、Runtime 和时间语义”的边界固化为可执行门禁，避免 Design-to-Code 过程中凭设计猜 API、硬编码示例选项或日期、用前端假成功掩盖后端能力缺口，同时让 Annotation 足以消除实现歧义但不过度堆积。

# 成功标准

- [x] 明确禁止把 Figma、Design Context、Annotation 或生成代码中的 endpoint、字段、枚举、状态码和持久化结构直接当生产 Contract。
- [x] 找不到真实 API/能力时必须区分“已批准但尚未实现”“未批准设计假设”“事实 Owner 冲突”，不得静默猜接口或做假前端。
- [x] DatePicker、DateRange、Today/Now、最近 N 天等时间 UI 必须映射目标项目 authoritative clock、timezone 和日期区间 Contract；设计日期默认只作示例，不得硬编码。
- [x] Design-to-Code 前对关键动态控件执行 UI → Real-System Preflight；映射不明时不得 READY。
- [x] Annotation 只承载实现无法从设计结构和正式事实源可靠推导的关键边界；避免复制完整 OpenAPI/Schema 和逐控件重复说明。
- [x] 保留既有 Canvas/Spacing/24–32px 安全距离、Prototype、Ready、系统能力映射和 Coding Handoff 规则，不建立第二套重复 Owner。
- [x] 自包含规则回归覆盖以上高价值门禁并实际经历 Red → Green。

# 范围

- 在 Figma 主 Skill 增加 Contract/API、运行时时间语义和 Annotation Sufficiency 三个高层硬门禁入口，不复制 Reference 细则。
- 增强 Figma `02_业务能力与真实系统映射.md` 的 Contract/Capability、后端缺口和 runtime time semantics 规则。
- 增强 Figma `05_Design-to-Code交付门禁.md` 的 UI → Real-System Preflight、禁止接口发明、后端缺口分支和 Annotation Sufficiency 规则。
- 在现有 Figma preservation 测试中增加对应回归断言。

# 非目标

- 不新增新的 Figma Skill 或重复 Reference。
- 不修改具体业务项目、Figma 文件、后端 API 或前端页面。
- 不规定所有项目必须使用 HTTP API、前后端架构或某个固定时区。
- 不修改 Runtime、Bundle、MCP、Installer、Release、Routing Stable ID 或 Project Payload 协议。
- 不复制 Coding 的 TDD、CI、Git、PR、Release 详细流程到 Figma Skill。

# 必须保持不变

- 目标项目当前 Contract、SDK、generated client、Service、Store、Runtime 和正式业务 Owner 优先于设计示例。
- Figma 现有 `READY / READY_WITH_NOTES / NOT_READY`、Fresh Screenshot、Machine Audit、Prototype、Canvas-level Review 和 Annotation 间距规则保持可达。
- 设计没有当前系统能力支持时，不允许用 mock、死链、空页面或前端伪成功冒充完成。
- 通用规则不能写入 AIMA_UGC、TikHub、具体业务字段或页面等项目特定事实。

# 关键决策

不新建 Reference。Contract/Capability 与时间语义属于现有 `figma.reference.02` 的真实系统映射职责；Design-to-Code 预检、接口发明禁止、缺口裁决和 Annotation 充分性属于现有 `figma.reference.05` 的交付门禁职责。Canvas/Spacing/Annotation 视觉安全距离继续由 `figma.reference.07` 唯一维护，本次不复制其数值规则。A1 Review 发现主 Skill 仍需保留三个不可延迟的高价值入口，因此只在主 Skill 增加最小导航句，详细语义仍由 ref02/ref05 单一维护。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Figma 动态数据和下拉选项必须接目标项目真实数据源，不能把设计示例硬编码 | user:current-request | satisfied | `figma.reference.02` 动态 Capability 规则 + `figma.reference.05` UI → Real-System Preflight；PR #73 final head CI run 33323874021 与 main fresh CI run 33323927108 全绿。 |
| R2 | 设计或生成工具不得凭猜测创造 API；发生前后端冲突时按真实 Contract/批准需求/Owner 分类裁决 | user:current-request | satisfied | `figma.reference.02` Contract/Capability 裁决 + `figma.reference.05` 禁止接口发明/能力缺口分支 + Figma 主 Skill 高层入口；PR #73 与 main fresh CI 全绿。 |
| R3 | 日期选择器和 Today/Now 等时间语义必须随真实运行时和项目时间 Contract 动态计算 | user:current-request | satisfied | `figma.reference.02` DatePicker/DateRange runtime time semantics + Figma 主 Skill 时间入口；PR #73 与 main fresh CI 全绿。 |
| R4 | Figma Annotation 必须足够支撑开发，但避免过量、重叠和重复正式 Contract | user:current-request | satisfied | `figma.reference.05` Annotation Sufficiency + Figma 主 Skill 高层入口；视觉间距、归属、24–32px fallback、无重叠和 zoom-out 可读性继续由既有 `figma.reference.07` 唯一维护。 |
| R5 | 保持现有 Figma Ownership、Canvas 可读性和 Coding Handoff，不建立重复规则体系 | .agents/MAINTENANCE.md | satisfied | 最终 diff 只修改本 Change、Figma 主 Skill/ref02/ref05 与 preservation tests；ref05 显式链接 ref07，Coding 生产实现 Owner 未复制；main fresh CI active Change gate 成功。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | `test_figma_skill.py` 新增 3 组 preservation 回归。Red：run 33323008616、33323453187；PR Green：run 33323874021；main fresh Green：run 33323927108。 |
| 接口 / 契约 | not_applicable | 不修改 Runtime/API/schema 机器契约；只规定设计与目标项目既有 Contract 的事实优先关系。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改或运行具体业务项目、数据库或外部 Provider。 |
| 用户 / 工作流验收 | required | A1/A2 从“Figma → baseline-ready → Coding Handoff”反向审查动态控件、时间、后端缺口和 Annotation 是否存在明确停止/交接规则；无 P0/P1 Finding。 |
| 跨组件关键路径 | required | 现有 `test_figma_skill.py` 同时验证 Figma routing、READY/NOT_READY → Coding、Bundle/Project Payload 动态发现；PR #73 与 main fresh CI 成功。 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要访问外部业务系统；规则测试自包含。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release 路径；按仓库 Maintenance 不触发三平台 Runtime Package Tests。 |
| 文档 / 治理 / 其他 | required | PR #73 final run 33323874021 中 changed Change gate 成功；merge 后 main run 33323927108 中 compile、CLI smoke、self-contained tests、active Coding Change gate 全部成功。 |

# 完成审计

- [x] upstream_re_read：重新读取本轮用户要求、根 AGENTS、Maintenance、Router、Coding、完成定义/两阶段复核/规则内容守恒规则、Review Skill 与受影响 Figma Skill/ref02/ref05/ref07；未从历史摘要替代当前仓库事实。
- [x] change_coverage：R1–R5 全部 `satisfied`；动态数据、API 发明、后端缺口、时间语义、Annotation 充分性分别落在现有唯一 Owner，A1 发现的主 Skill 高层入口遗漏已补齐。
- [x] reverse_audit：Design-to-Code 用户意图 → Figma baseline-ready → ref02 真实系统事实 → ref05 预检/交接 → READY/NOT_READY → Coding 生产实现；Canvas/Spacing/Annotation 视觉间距继续由 ref07 单一维护。
- [x] unresolved_cleared：无 `not_satisfied`、无延期项；所有 required Validation Matrix 项已有本轮新鲜证据，A2/规则质量 Review 无 P0/P1 blocker；实现 PR 与 main fresh CI 均成功。

# 任务

- [x] 调查当前 Agent_Skills、Figma Skill、Design-to-Code Coding 规则和现有回归测试。
- [x] 建立四维任务路由：Skill Mutation / Figma Design-to-Code / L2 / 规则与测试。
- [x] 先新增 ref02/ref05 preservation 测试并在 run 33323008616 确认 Red。
- [x] 最小增强 ref02/ref05，不复制 ref07 或 Coding 详细规则。
- [x] 对 Markdown 导航回归失败做根因调查；确认是新增真实 `.md` 路径未使用可点击链接，修复链接而未放宽测试。
- [x] A1 Review 发现 Figma 主 Skill 缺少高层入口，新增专门失败测试并在 run 33323453187 确认第二次 Red。
- [x] 只在 Figma 主 Skill 增加 Contract/API、时间语义、Annotation Sufficiency 三个最小入口；commit diff 复核无其它漂移。
- [x] 运行全部 self-contained Skill Tests、compile、CLI smoke 和 changed Change gate；多轮 PR Green 均成功。
- [x] 执行 Requirement A1/A2、内容守恒、项目中立性和规则质量 Review；无 P0/P1 Finding。
- [x] Draft PR #72 自动 Ready 返回 `fullDatabaseId` GraphQL 查询错误，重读仍为 Draft 后按仓库规则关闭 #72，并创建普通 PR #73 重新执行 fresh CI。
- [x] 普通 PR #73 final head `6134f1baa42ac63a6b97d60ca98d7ef30efaee78` fresh CI run 33323874021 全绿，Review 锚定同一 head，使用 `expected_head_sha` 正常合并。
- [x] 实现 merge commit `ecdec20183118a7cd19d1b89984cb699fb90aef4` 上执行 main fresh CI run 33323927108，全部 Skill Tests 与 active Change gate 成功。
- [x] 从验证后的 exact main SHA 创建独立归档分支，将本 Change 更新为 `done` 并移动到 `archive/2026-08/`；归档 PR 继续独立执行 CI/merge 门禁。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_figma_skill.py`
- 相关测试：`.agents/skills/coding/tests/` 全部 self-contained tests、Markdown 导航、Routing/Bundle/Project Payload 现有回归。
- 静态检查或构建：由 `.github/workflows/skill-tests.yml` 执行现有 compile/CLI smoke/规则解析；本次不触发 Runtime Package Tests。
- 就绪检查：PR CI 使用 `python .agents/skills/coding/scripts/ready_check.py --root . --changed-since <base-sha>`；实现 merge 后 main push 使用 active Change gate；归档 PR 使用 changed Change/归档治理门禁。

## 新鲜证据

- Red 1：Skill Tests run `33323008616`，head `f3d935e3a36bffcdea5f125757a27da12611d377`，compile/CLI smoke 成功，self-contained tests 因新增真实系统门禁尚不存在而失败。
- 中间回归：run `33323122283` 在 self-contained tests 失败；读取 `test_markdown_navigation_links.py` 后确认根因是新 ref05 中真实 Markdown 路径使用不可点击 inline code，改为可点击链接，未删除或放宽测试。
- Green 1：run `33323354605`，head `5cf47ef8a872efab354a162eac3ad9cd1079c62f`，compile、CLI smoke、全部 self-contained tests、changed Change gate 全部成功。
- Red 2：A1 发现主 Skill 高层入口遗漏后新增失败测试；run `33323453187`，head `b2aca6970fa555ce8b2c2b48402ff0967d9fc73d`，compile/CLI smoke 成功，self-contained tests 失败。
- Green 2：run `33323640915`，head `97ed7dd9f6bd867c330e611990b1145e470c9b3d`，job `99289842292`；compile、CLI smoke、全部 self-contained tests、changed Change gate 全部成功。
- Draft PR #72 final head：run `33323743279`，head `7aec2683505717603170333b511ffa58860e7bb9`，job `99290117103`；compile、CLI smoke、全部 self-contained tests、changed Change gate 全部成功。
- PR 生命周期：Draft → Ready API 返回 `Field 'fullDatabaseId' doesn't exist on type 'Repository'`；立即重读 #72 仍为 Draft，按既有零人工交付规则关闭 #72、创建普通 PR #73，并重新执行 fresh CI。
- 普通 PR #73 intermediate fresh CI：run `33323810251`，same code head `7aec2683505717603170333b511ffa58860e7bb9`，success。
- 普通 PR #73 final reviewed head：`6134f1baa42ac63a6b97d60ca98d7ef30efaee78`，run `33323874021` / job `99290479097`，compile、CLI smoke、全部 self-contained tests、changed Change gate 成功。
- 实现合并：PR #73 使用 `expected_head_sha=6134f1baa42ac63a6b97d60ca98d7ef30efaee78` merge 成功，main merge commit `ecdec20183118a7cd19d1b89984cb699fb90aef4`。
- main fresh CI：run `33323927108` / job `99290624599`，head `ecdec20183118a7cd19d1b89984cb699fb90aef4`；compile、CLI smoke、全部 self-contained tests、active Coding Change gate 全部成功。
- diff 复核：主 Skill commit `97ed7dd9...` 仅新增 3 个高层入口；实现 PR changed files 限于本 Change、Figma Skill/ref02/ref05 和 Figma preservation tests。

# Review

## A1：上游要求 → Change

重新从用户当前要求独立重建 R1–R5。初次审查发现原 Change 未把“主 Skill 保留不可延迟高层入口”写入 affected path/实施范围；已新增失败测试并补齐最小主入口。复核后无 requirement omission。

## A2：Change → Skill / Tests

- 动态数据、Select 示例与真实来源：ref02 + ref05 Preflight 覆盖。
- 禁止虚构 API/Contract 与冲突分类：ref02 + ref05 覆盖，主 Skill 保留硬入口。
- DatePicker/Today/Now：ref02 明确 authoritative clock/timezone/date contract，主 Skill 保留 runtime time 入口。
- Annotation：ref05 负责充分性与不过度，ref07 继续唯一负责间距、无重叠、归属和 Canvas 可读性。
- Routing Stable ID/触发条件未改变；现有 baseline-ready/设计转代码触发已经覆盖新增语义，无需修改 Router/metadata。
- 测试只做规则 preservation/可达性，不冒充真实业务 API/数据库集成；Runtime/业务项目验证不适用。

结论：无 P0/P1 Finding；没有需要阻塞合并的测试充分性、Ownership、兼容或项目中立性问题。

# 文档影响

- 不影响 README、USAGE 或 runtime/README。
- 正式规则更新 Figma `SKILL.md`、ref02、ref05；ref07 的既有 Annotation/Canvas 视觉规则无需修改，避免重复 Owner。
- 无需新增人类文档。

# 交付

- 实现分支：`change/figma-real-system-handoff`
- 旧 Draft PR：#72，Ready API 不可用且重读仍为 Draft 后已关闭，未合并。
- 实现 PR：#73，已通过 REST merge + `expected_head_sha` 合并。
- 实现 merge commit：`ecdec20183118a7cd19d1b89984cb699fb90aef4`。
- main fresh CI：Skill Tests run `33323927108` / job `99290624599`，success。
- Change：本记录已更新为 `done`，由独立归档分支移入 `archive/2026-08/`，归档 PR 继续承担移动本身的 CI/merge 验证。
- 发布：不适用；本次不修改 Runtime/Release 产品面。
