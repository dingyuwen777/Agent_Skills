---
schema: coding-change/v1
id: CHG-20260828-sync-universal-figma-skill
title: 同步通用 Figma Skill 与 Design-to-Code 路由
level: L2
status: in_progress
owner: ChatGPT
branch: feat/sync-universal-figma-skill
created: 2026-08-28
updated: 2026-08-28
completion_gate: required
depends_on: []
affected_areas:
  - skills
  - routing
  - distribution
  - docs
  - tests
affected_paths:
  - ".agents/skills/figma/"
  - ".agents/skills/coding/SKILL.md"
  - ".agents/skills/coding/references/02_跨项目研发任务路由.md"
  - ".agents/skills/coding/references/16_规则内容守恒与Skill维护.md"
  - ".agents/skills/coding/references/17_前端与Design-to-Code实施规则.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/tests/"
  - "AGENTS.md"
  - "README.md"
  - ".agents/README.md"
contracts: []
data_changes: []
---

# 目标

把 AIMA_UGC 当前已经形成的跨项目 Figma 审查、修复、Prototype、Canvas、Design-to-Code Ready 规则同步到 Agent_Skills，形成正式第四个通用 Skill；同时保持 Agent_Skills 当前 Coding、Docs、Review、Runtime、Bootstrap 和动态分发架构不倒退。

# 成功标准

- [ ] `.agents/skills/figma/` 成为完整正式 Skill，保留 AIMA 当前 `SKILL.md`、README、OpenAI metadata 和 00–07 references 的有效规则语义。
- [ ] Canvas、Prototype、Owner、状态、Ready、失败处理、写后复核、Findings 和 Design-to-Code Handoff 等高价值规则逐条可达，不因通用化被摘要、降级或删除。
- [ ] 只把 Web/Backend/AIMA 隐含项目假设改成目标运行环境、真实系统能力和条件化数据源表达；不删除原风险、触发条件、例外或验证责任。
- [ ] Coding 明确把 Figma 创建/修改/审查/Prototype/Ready 路由给 Figma Skill，同时保留 reference 17 负责 READY 后的生产代码实现。
- [ ] Figma 设计细则只有 Figma Skill 一个 Owner；Coding 不恢复第二套 Canvas/Spacing/Annotation/Prototype 规范。
- [ ] Bootstrap、根 README、`.agents/README.md` 和仓库维护规则反映当前第四个正式 Skill，同时继续声明正式 Skill 由 `.agents/skills/*/SKILL.md` 动态发现而不是硬编码四项名单。
- [ ] 当前正式 Figma Skill 自动进入 Reference Bundle、Project Payload、Full Distribution、Runtime 项目安装和 ownership manifest；不修改动态 Catalog 为静态名单。
- [ ] preservation / portability / routing / distribution 回归通过，且 Figma live 规则不包含 AIMA_UGC、TikHub 或具体 AIMA 页面/Stage/Blueprint 等业务事实。

# 范围

- 从 `dingyuwen777/AIMA_UGC` 当前 `main` 的 `.agents/skills/figma/` 迁移完整规则集合。
- 对 Figma Skill 中仍带 Web/Full-stack 隐含假设的表达做最小宿主中立化，保留完整规则强度。
- 更新 Coding 的跨 Skill 路由、READY Handoff 和规则 Ownership。
- 更新 Agent_Skills 当前 Skill 导航、Bootstrap managed block、维护规范和自包含回归测试。
- 验证动态分发链自动包含新增正式 Skill。

# 非目标

- 不把 AIMA_UGC 的 `AGENTS.md`、Blueprint、Roadmap、业务字段、Provider、数据库版本、前端技术栈或部署方案迁入通用 Skill。
- 不用 AIMA 版本覆盖 Agent_Skills 当前 Coding、Docs、Review、Runtime、Installer、Change schema 或分发实现。
- 不删除或摘要 Figma 规则来追求文件更短。
- 不新增第二个 Figma-to-code 研发流程；生产代码实施继续由 Coding reference 17 和目标项目规则负责。
- 不升级 Runtime、依赖、产品版本或改变 Release 协议。

# 必须保持不变

- Agent_Skills 的动态正式 Skill 发现继续以 `.agents/skills/*/SKILL.md` 为唯一目录边界，不维护固定全量白名单。
- Coding 当前 Greenfield、四维路由、TDD、根因调试、Requirement Traceability、Validation Matrix、Completion Audit、Review/Docs、Git/CI/Release 与 Runtime/Bootstrap 规则完整保留。
- Docs 与 Review 不被 AIMA 旧版本反向覆盖。
- Runtime canonical Reference / Stub / Bundle / ownership / project-local MCP 契约保持兼容。
- 五项用户定义的全局工程硬规则保持不变。

# 关键决策

1. Figma 作为独立正式 Skill 迁入，而不是把完整设计规则塞回 Coding。
2. 逐规则内容守恒优先；通用化只改变项目假设、条件表达和规则归属，不以摘要换取篇幅。
3. Figma 负责设计事实、Canvas/Prototype、设计修复与 `READY / READY_WITH_NOTES / NOT_READY`；Coding reference 17 负责可实施基线后的真实代码映射、实现、测试与交付。
4. AIMA Figma reference 07 中 Web/Backend 倾向表达改为目标运行环境、真实数据源/Contract/SDK/系统能力，并保留 Web/API/Backend 作为适用时的具体 profile。
5. 动态分发实现不增加 `figma` 静态名单，只补真实产物回归证明自动发现。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 将 AIMA_UGC 更新后的通用 Figma Skill 同步到 Agent_Skills | user:2026-08-28-sync-figma | not_satisfied | 尚未实现 |
| R2 | 逐规则内容守恒，不总结缩短 Canvas、Prototype、Owner、状态、Ready、失败处理和写后复核 | user:2026-08-28-preserve-figma-rules | not_satisfied | 尚未实现 |
| R3 | 通用化只移除项目假设，不降低约束强度 | user:2026-08-28-generalize-without-weakening | not_satisfied | 尚未实现 |
| R4 | 通用 Skill 不污染目标项目具体技术栈/业务事实 | AGENTS.md | not_satisfied | 尚未验证 |
| R5 | 正式 Skill 动态发现、Runtime/Full Kit/安装器不得新增静态全量名单 | AGENTS.md | not_satisfied | 尚未验证 |
| R6 | 规则重组需要 preservation/portability 回归和人工语义对照 | .agents/skills/coding/references/16_规则内容守恒与Skill维护.md | not_satisfied | 尚未验证 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新增 Figma Skill 内容守恒、路由、Ownership、宿主中立化与动态 Catalog 回归；先 Red 后 Green |
| 接口 / Contract | not_applicable | 不改变业务 API/ABI/CLI/Schema；Skill 文件路径新增但动态 Catalog contract 不变 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不新增数据库/队列/第三方 Runtime 依赖 |
| 用户 / Workflow Acceptance | required | `全面检查 Figma`、`检查并修复`、`按 Figma 实现` 能分别映射 review/baseline/Coding Handoff，不把 NOT_READY 写进生产实现 |
| 跨组件 Golden Path | required | `Coding → Figma → READY → Coding ref17 → Review/Docs/Delivery` 与 `Skill source → Bundle/Payload → install` 两条链路 |
| External Dependency / Provider Probe | not_applicable | 本任务不需要调用真实 Figma API 来证明规则文件同步；源事实来自 GitHub 当前仓库 |
| Build / Package / Runtime | required | 现有 Full Distribution 和三平台 Runtime/项目安装 CI 必须继续通过并自动包含 figma |
| Docs / Governance / Other | required | 根导航、Bootstrap、Change、内容守恒和项目污染扫描必须一致 |

# Completion Audit

- [ ] upstream_re_read：重新读取本轮用户决定、Agent_Skills `AGENTS.md`、AIMA_UGC 当前 Figma Skill、Coding 02/16/17、动态分发实现和相关测试。
- [ ] change_coverage：确认当前 Change 覆盖完整 Figma Skill、Coding 路由、Bootstrap、导航、分发与测试，没有把“同步目录”误当成完整需求。
- [ ] reverse_audit：从 Figma Review/Repair/Ready/Handoff 场景和 Runtime/Full Distribution 消费链反向检查规则可达性与正式产物。
- [ ] unresolved_cleared：Ready 前所有 `not_satisfied` 清零；所有 required 验证有本轮新鲜证据。

# 任务

- [x] 调查两个仓库当前 `main` 与适用规则
- [x] 建立四维任务路由：Agent Skill/Developer Tool + Feature/Rule Migration + Python/Markdown/GitHub Actions + L2
- [ ] 建立失败测试并确认因 Figma Skill/路由缺失失败
- [ ] 迁入完整 Figma Skill 并做最小宿主中立化
- [ ] 接入 Coding/Bootstrap/README/AGENTS 路由与 Ownership
- [ ] 验证动态 Bundle/Payload/Full Kit/Runtime 自动发现 figma
- [ ] 完成 Docs targeted review 与内容守恒人工对照
- [ ] 完成独立 Review、Ready Check 和跨平台 CI
- [ ] 正常合并 main 后复核 main，并按仓库流程归档 Change

# 验证

## 计划

- Red：新增 `.agents/skills/coding/tests/test_figma_skill.py`，在尚无 Figma Skill/路由时由 self-contained tests 失败。
- Green：`python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- 动态分发：现有 `test_dynamic_skill_distribution.py` + 新增正式仓库 Figma Catalog/Payload 断言。
- Full/Runtime：永久 `Skill Tests` Workflow 的 Full Distribution、onefile Runtime、stdio MCP、项目级 binary 安装与 Windows/macOS package。
- Ready Check：`python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。

## 新鲜证据

- 尚未执行 Red CI。

# 文档影响

- `targeted`：根 `AGENTS.md`、`README.md`、`.agents/README.md`、Coding README/路由与 Bootstrap managed block 受影响；Docs/Review 正式规则本身不因同步而重写。

# 交付

- Commit：待完成
- PR：待创建
- 发布：不涉及产品 Release
