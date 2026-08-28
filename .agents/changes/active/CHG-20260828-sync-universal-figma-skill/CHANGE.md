---
schema: coding-change/v1
id: CHG-20260828-sync-universal-figma-skill
title: 同步通用 Figma Skill 与 Design-to-Code 路由
level: L2
status: ready_for_review
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

- [x] `.agents/skills/figma/` 成为完整正式 Skill，保留 AIMA 当前 `SKILL.md`、README、OpenAI metadata 和 00–07 references 的有效规则语义。
- [x] Canvas、Prototype、Owner、状态、Ready、失败处理、写后复核、Findings 和 Design-to-Code Handoff 等高价值规则逐条可达，不因通用化被摘要、降级或删除。
- [x] 只把 Web/Backend/AIMA 隐含项目假设改成目标运行环境、真实系统能力和条件化数据源表达；不删除原风险、触发条件、例外或验证责任。
- [x] Coding 明确把 Figma 创建/修改/审查/Prototype/Ready 路由给 Figma Skill，同时保留 reference 17 负责 READY 后的生产代码实现。
- [x] Figma 设计细则只有 Figma Skill 一个 Owner；Coding 不恢复第二套 Canvas/Spacing/Annotation/Prototype 规范。
- [x] Bootstrap、根 README、`.agents/README.md` 和仓库维护规则反映当前第四个正式 Skill，同时继续声明正式 Skill 由 `.agents/skills/*/SKILL.md` 动态发现而不是硬编码四项名单。
- [x] 当前正式 Figma Skill 自动进入 Reference Bundle、Project Payload、Full Distribution、Runtime 项目安装和 ownership manifest；不修改动态 Catalog 为静态名单。
- [x] preservation / portability / routing / distribution 回归通过，且 Figma live 规则不包含 AIMA_UGC、TikHub 或具体 AIMA 页面/Stage/Blueprint 等业务事实。

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
| R1 | 将 AIMA_UGC 更新后的通用 Figma Skill 同步到 Agent_Skills | user:2026-08-28-sync-figma | satisfied | `.agents/skills/figma/` 已包含正式 `SKILL.md`、README、OpenAI metadata 和 00–07 references；AIMA 当前 main 与目标规则已做逐文件/关键段语义对照。 |
| R2 | 逐规则内容守恒，不总结缩短 Canvas、Prototype、Owner、状态、Ready、失败处理和写后复核 | user:2026-08-28-preserve-figma-rules | satisfied | `test_figma_skill.py` 锁定 Canvas/Prototype/Owner/状态/Readiness/失败处理，并进一步断言 4px 网格、24–32px、40–64px、64–80px、96–160px、每次写后 Canvas-level Review 和 Prototype 写入成功不能替代复核；PR run #160 self-contained 111 tests 为 OK。 |
| R3 | 通用化只移除项目假设，不降低约束强度 | user:2026-08-28-generalize-without-weakening | satisfied | ref00–06 与 AIMA 当前规则保持相同职责；ref07 仅把 Web/Backend 假设条件化为真实目标运行环境、真实系统能力/数据源，同时保留原 fallback 数值、Annotation、Canvas 写后复核、邻接修复与完成停止条件。 |
| R4 | 通用 Skill 不污染目标项目具体技术栈/业务事实 | AGENTS.md | satisfied | `test_live_universal_rules_do_not_depend_on_aima_product_paths` 与 `test_figma_skill_does_not_embed_aima_business_facts` 在 PR run #160 通过；根维护规则中的业务仓库专名残留已改为“任何外部业务仓库”。 |
| R5 | 正式 Skill 动态发现、Runtime/Full Kit/安装器不得新增静态全量名单 | AGENTS.md | satisfied | 未修改 Runtime/Installer 为静态名单；PR run #160 Full Distribution、Linux Runtime 和项目安装均报告 `skill_count: 4` / `coding, docs, figma, review`，Windows/macOS 项目级 single-binary 安装也成功。 |
| R6 | 规则重组需要 preservation/portability 回归和人工语义对照 | .agents/skills/coding/references/16_规则内容守恒与Skill维护.md | satisfied | 已执行 AIMA 当前 Figma → Agent_Skills Figma 的关键规则反向对照；`test_figma_skill.py`、动态 Skill 分发、Runtime exact-reference/Project Payload 等 preservation/portability 测试在 PR run #160 全部通过；独立 Review 未发现剩余 blocker。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 先建立 Figma 缺失时会失败的 Red 回归；实现后 PR run #160 执行 self-contained 111 tests，结果 `OK`，覆盖内容守恒、路由、Ownership、宿主中立化、动态 Catalog 与分发。 |
| 接口 / Contract | not_applicable | 本次不改变业务 API/ABI/CLI/Schema，也不改变 Runtime Tool Contract；正式 Skill 仍使用既有动态 `.agents/skills/*/SKILL.md` Catalog contract。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不新增数据库、队列、外部 Provider 或新的 Runtime 依赖；现有 Runtime 集成只验证分发兼容性。 |
| 用户 / Workflow Acceptance | required | Coding ref02 + Figma Skill + ref17 + Bootstrap managed block 已覆盖“全面检查/修复/baseline-ready/按 Figma 实现”；`NOT_READY` 明确阻止生产实现，READY 后进入 Coding Handoff；对应路由回归通过。 |
| 跨组件 Golden Path | required | PR run #160 验证两条真实链：`Skill source → Bundle/Project Payload → Full install`，以及 `onefile Runtime → project-only install/upgrade → project-local MCP status/smoke`；二者都自动包含 figma。 |
| External Dependency / Provider Probe | not_applicable | 本任务验证规则迁移和本地分发，不需要调用真实 Figma API；上游 Figma Skill 事实来自 GitHub 当前 main。 |
| Build / Package / Runtime | required | PR run #160：Full Distribution 成功；Linux onefile `status/self-test` 成功；真实 stdio MCP 成功；项目级 binary install/upgrade/no-args install 成功；Windows package/项目安装成功；macOS package/项目安装成功。 |
| Docs / Governance / Other | required | 根 `README.md`、`.agents/README.md`、Coding README/Bootstrap/维护规则已 targeted review；业务项目污染扫描与 preservation 测试通过；独立 Review 找到并移除了唯一无关措辞差异。 |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户“逐规则内容守恒”决定、Agent_Skills 当前 `AGENTS.md`、AIMA_UGC 当前 Figma Skill、Coding 02/16/17、Docs/Review 规则及当前 PR/CI 事实。
- [x] change_coverage：已从上游要求独立检查完整 Figma Skill、Canvas/Prototype/Owner/状态/Ready/失败处理、Coding 路由、Bootstrap/导航、动态分发和内容守恒测试，未把“目录已复制”误当成完整需求。
- [x] reverse_audit：已从 Figma Review/Repair/Ready/Handoff 用户意图反查到 Coding ref02 → Figma canonical rules → READY/NOT_READY → Coding ref17，并从正式 Skill 反查到 Bundle/Project Payload/Full install/三平台 Runtime 项目安装消费链。
- [x] unresolved_cleared：R1–R6 均已有实现、人工对照或 PR run #160 的新鲜证据；无 `not_satisfied`、无未批准延期，最终 Ready Check 将由本次 `ready_for_review` 状态提交后的永久 CI 再执行。

# 任务

- [x] 调查两个仓库当前 `main` 与适用规则
- [x] 建立四维任务路由：Agent Skill/Developer Tool + Feature/Rule Migration + Python/Markdown/GitHub Actions + L2
- [x] 建立失败测试并确认因 Figma Skill/路由缺失失败
- [x] 迁入完整 Figma Skill 并做最小宿主中立化
- [x] 接入 Coding/Bootstrap/README/AGENTS 路由与 Ownership
- [x] 验证动态 Bundle/Payload/Full Kit/Runtime 自动发现 figma
- [x] 完成 Docs targeted review 与内容守恒人工对照
- [x] 完成独立 Review 与跨平台 CI；本次状态提交后的永久 CI 负责最终机器 Ready Check
- [ ] 正常合并 main 后复核 main，并按仓库流程归档 Change

# 验证

## 计划

- Red：新增 `.agents/skills/coding/tests/test_figma_skill.py`，在尚无 Figma Skill/路由时由 self-contained tests 失败。
- Green：`python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- 动态分发：现有 `test_dynamic_skill_distribution.py` + 正式仓库 Figma Catalog/Payload 断言。
- Full/Runtime：永久 `Skill Tests` Workflow 的 Full Distribution、onefile Runtime、stdio MCP、项目级 binary 安装与 Windows/macOS package。
- Ready Check：`python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。

## 新鲜证据

- Red：初始 Figma preservation/routing/distribution tests 在正式 Figma Skill/路由尚不存在时实际失败，证明测试能捕获目标缺口；失败原因是 Figma Skill、reference、Bootstrap/Catalog 路由缺失，而不是环境故障。
- Green / PR run #160（HEAD `eb10919ed597ec5934b8fe3ce9c0ddd963391ebb`）：self-contained `Ran 111 tests`，结果 `OK`。
- Full Distribution / run #160：构建与临时目标安装成功，动态 skills 为 `coding, docs, figma, review`。
- Linux Runtime / run #160：onefile `status/self-test` 成功，`skill_count=4`、`reference_count=31`；真实 stdio MCP `ok=true`、`tool_count=5`。
- Project Runtime / run #160：项目级 single-binary 首次安装、重复升级、无参数当前目录安装、项目内 Runtime status 与 MCP smoke 全部成功。
- Windows / run #160：onefile build/self-test 与 project-only single-binary installation 成功。
- macOS / run #160：onefile build/self-test 与 project-only single-binary installation 成功。
- run #160 唯一失败为最终 Ready Check 检测到 Change 仍是 `in_progress`；技术/分发 Job 已全绿。本 Change 现已按 Requirement Traceability、Completion Audit、Docs targeted review 和独立 Review 更新为 `ready_for_review`，由下一次永久 CI 对最终 HEAD 重新执行完整门禁。

# 文档影响

- `targeted`：已复核并更新根 `README.md`、`.agents/README.md`、Coding/Figma 使用入口、根维护 `AGENTS.md` 和 Bootstrap managed block，使当前正式 Figma Skill、NOT_READY/READY Handoff 与动态发现事实一致。
- Docs/Review 正式规则本身没有因本次同步被改写；未发现 `code_issue_detected`。
- 没有新增第二套机器事实；具体项目的品牌、技术栈、数据字段、页面尺寸和系统能力仍由目标项目事实与正式 Figma 负责。

# 交付

- Branch：`feat/sync-universal-figma-skill`
- Commit：已在专用分支使用中文提交；最终合并前以 PR 当前 HEAD 和永久 CI 为准。
- PR：`#15 同步通用 Figma Skill 与 Design-to-Code 路由`，当前在进入最终 Ready/CI 阶段。
- 发布：不涉及产品 VERSION/tag/Release；不改变依赖、Runtime 版本、API/Schema/Migration 或部署协议。
