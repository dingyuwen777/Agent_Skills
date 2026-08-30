---
schema: coding-change/v1
id: CHG-20260831-figma-real-system-handoff
title: 强化 Figma 真实系统映射与 Design-to-Code 交付门禁
level: L2
status: in_progress
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
  - .agents/skills/figma/references/02_业务能力与真实系统映射.md
  - .agents/skills/figma/references/05_Design-to-Code交付门禁.md
  - .agents/skills/coding/tests/test_figma_skill.py
contracts: []
data_changes: []
---

# 目标

把“Figma 只表达设计意图，生产实现必须服从目标项目真实 Contract、Capability、Runtime 和时间语义”的边界固化为可执行门禁，避免 Design-to-Code 过程中凭设计猜 API、硬编码示例选项或日期、用前端假成功掩盖后端能力缺口，同时让 Annotation 足以消除实现歧义但不过度堆积。

# 成功标准

- [ ] 明确禁止把 Figma、Design Context、Annotation 或生成代码中的 endpoint、字段、枚举、状态码和持久化结构直接当生产 Contract。
- [ ] 找不到真实 API/能力时必须区分“已批准但尚未实现”“未批准设计假设”“事实 Owner 冲突”，不得静默猜接口或做假前端。
- [ ] DatePicker、DateRange、Today/Now、最近 N 天等时间 UI 必须映射目标项目 authoritative clock、timezone 和日期区间 Contract；设计日期默认只作示例，不得硬编码。
- [ ] Design-to-Code 前对关键动态控件执行 UI → Real-System Preflight；映射不明时不得 READY。
- [ ] Annotation 只承载实现无法从设计结构和正式事实源可靠推导的关键边界；避免复制完整 OpenAPI/Schema 和逐控件重复说明。
- [ ] 保留既有 Canvas/Spacing/24–32px 安全距离、Prototype、Ready、系统能力映射和 Coding Handoff 规则，不建立第二套重复 Owner。
- [ ] 自包含规则回归覆盖以上高价值门禁并实际经历 Red → Green。

# 范围

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

不新建 Reference。Contract/Capability 与时间语义属于现有 `figma.reference.02` 的真实系统映射职责；Design-to-Code 预检、接口发明禁止、缺口裁决和 Annotation 充分性属于现有 `figma.reference.05` 的交付门禁职责。Canvas/Spacing/Annotation 视觉安全距离继续由 `figma.reference.07` 唯一维护，本次不复制其数值规则。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Figma 动态数据和下拉选项必须接目标项目真实数据源，不能把设计示例硬编码 | user:current-request | not_satisfied | 尚未实现和验证 |
| R2 | 设计或生成工具不得凭猜测创造 API；发生前后端冲突时按真实 Contract/批准需求/Owner 分类裁决 | user:current-request | not_satisfied | 尚未实现和验证 |
| R3 | 日期选择器和 Today/Now 等时间语义必须随真实运行时和项目时间 Contract 动态计算 | user:current-request | not_satisfied | 尚未实现和验证 |
| R4 | Figma Annotation 必须足够支撑开发，但避免过量、重叠和重复正式 Contract | user:current-request | not_satisfied | 尚未实现和验证 |
| R5 | 保持现有 Figma Ownership、Canvas 可读性和 Coding Handoff，不建立重复规则体系 | .agents/MAINTENANCE.md | not_satisfied | 尚未完成内容守恒复核 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | `test_figma_skill.py` 增加 preservation 回归；先确认旧规则因缺少新硬门禁而 Red，再在规则更新后 Green。 |
| 接口 / 契约 | not_applicable | 不修改 Runtime/API/schema 机器契约；只规定设计与目标项目既有 Contract 的事实优先关系。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改或运行具体业务项目、数据库或外部 Provider。 |
| 用户 / 工作流验收 | required | 从“Figma → baseline-ready → Coding Handoff”反向检查动态控件、时间、后端缺口和 Annotation 是否存在明确停止/交接规则。 |
| 跨组件关键路径 | required | 验证 Figma ref02 → ref05 → READY/NOT_READY → Coding 现有 Design-to-Code Owner 的链路仍可达。 |
| 外部依赖 / 供应方探测 | not_applicable | 不需要访问外部业务系统；规则测试必须自包含。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/Release 路径，不需要三平台 binary 构建。 |
| 文档 / 治理 / 其他 | required | 内容守恒、Ownership、项目中立性、Markdown 导航和 changed Change Ready Check。 |

# 完成审计

- [ ] upstream_re_read：重新读取用户要求、根 AGENTS、Maintenance、Router、Coding、规则内容守恒 Reference 和受影响 Figma References。
- [ ] change_coverage：逐项确认动态数据、API 发明、后端缺口、时间语义、Annotation 充分性均有唯一 Owner。
- [ ] reverse_audit：从 Design-to-Code 请求反向检查 Figma baseline-ready → ref02/ref05 → Coding Handoff，且 Canvas 间距仍由 ref07 单一维护。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零，验证矩阵 required 项均有本轮新鲜证据。

# 任务

- [x] 调查当前 Agent_Skills、Figma Skill、Design-to-Code Coding 规则和现有回归测试。
- [x] 建立四维任务路由：Skill Mutation / Figma Design-to-Code / L2 / 规则与测试。
- [ ] 先新增目标 preservation 测试并确认 Red。
- [ ] 最小增强 ref02 / ref05，不复制 ref07 或 Coding 详细规则。
- [ ] 运行目标测试与全部 self-contained Skill Tests。
- [ ] 执行内容守恒、项目中立性和独立 Review。
- [ ] 更新需求追溯与完成审计，进入 `ready_for_review` 并完成 PR/CI/merge/main fresh CI。
- [ ] main 验证后通过独立归档 PR 移动本 Change 到 `archive/2026-08/...`。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_figma_skill.py`
- 相关测试：`.agents/skills/coding/tests/` 全部 self-contained tests、Markdown 导航、Routing/Bundle/Project Payload 现有回归。
- 静态检查或构建：由 `.github/workflows/skill-tests.yml` 执行现有 compile/CLI smoke/规则解析；本次不触发 Runtime Package Tests。
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- 尚未执行 Red/Green。

# 文档影响

- 不影响 README、USAGE 或 runtime/README；正式规则只更新 Figma Skill References。无需新增人类文档。

# 交付

- 提交：进行中
- 拉取请求：待创建
- 发布：不适用
