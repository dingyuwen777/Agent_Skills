---
schema: coding-change/v1
id: CHG-20260828-sync-universal-figma-skill
title: 同步通用 Figma Skill 与 Design-to-Code 路由
level: L2
status: done
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
| R1 | 将 AIMA_UGC 更新后的通用 Figma Skill 同步到 Agent_Skills | user:2026-08-28-sync-figma | satisfied | `.agents/skills/figma/` 已包含正式 `SKILL.md`、README、OpenAI metadata 和 00–07 references；AIMA 当前 main 与目标规则已做逐文件/关键段语义对照；实现已由 PR #15 合并到 main。 |
| R2 | 逐规则内容守恒，不总结缩短 Canvas、Prototype、Owner、状态、Ready、失败处理和写后复核 | user:2026-08-28-preserve-figma-rules | satisfied | `test_figma_skill.py` 锁定 Canvas/Prototype/Owner/状态/Readiness/失败处理，并直接断言 4px 网格、24–32px、40–64px、64–80px、96–160px、每次写后 Canvas-level Review 和 Prototype 写入成功不能替代复核；Ready run #162 与 main run #163 的 self-contained tests 均通过。 |
| R3 | 通用化只移除项目假设，不降低约束强度 | user:2026-08-28-generalize-without-weakening | satisfied | ref00–06 与 AIMA 当前规则保持相同职责；ref07 仅把 Web/Backend 假设条件化为真实目标运行环境、真实系统能力/数据源，同时保留原 fallback 数值、Annotation、Canvas 写后复核、邻接修复与完成停止条件。 |
| R4 | 通用 Skill 不污染目标项目具体技术栈/业务事实 | AGENTS.md | satisfied | `test_live_universal_rules_do_not_depend_on_aima_product_paths` 与 `test_figma_skill_does_not_embed_aima_business_facts` 在 Ready run #162 和 main run #163 通过；根维护规则中的业务仓库专名残留已改为“任何外部业务仓库”。 |
| R5 | 正式 Skill 动态发现、Runtime/Full Kit/安装器不得新增静态全量名单 | AGENTS.md | satisfied | 未修改 Runtime/Installer 为静态名单；Ready run #162 与 main run #163 均验证 Full Distribution、Linux Runtime、项目安装和 Windows/macOS 项目级 single-binary，动态 skills 为 `coding, docs, figma, review`。 |
| R6 | 规则重组需要 preservation/portability 回归和人工语义对照 | .agents/skills/coding/references/16_规则内容守恒与Skill维护.md | satisfied | 已执行 AIMA 当前 Figma → Agent_Skills Figma 的关键规则反向对照；`test_figma_skill.py`、动态 Skill 分发、Runtime exact-reference/Project Payload 等 preservation/portability 测试在 Ready run #162 与 main run #163 通过；独立 Review 未发现剩余 blocker。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 先建立 Figma 缺失时会失败的 Red 回归；最终 Ready run #162 在 feature HEAD 执行 self-contained 111 tests 并 `OK`，main run #163 再次通过同一层，覆盖内容守恒、路由、Ownership、宿主中立化、动态 Catalog 与分发。 |
| 接口 / Contract | not_applicable | 本次不改变业务 API/ABI/CLI/Schema，也不改变 Runtime Tool Contract；正式 Skill 仍使用既有动态 `.agents/skills/*/SKILL.md` Catalog contract。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不新增数据库、队列、外部 Provider 或新的 Runtime 依赖；现有 Runtime 集成只验证分发兼容性。 |
| 用户 / Workflow Acceptance | required | Coding ref02 + Figma Skill + ref17 + Bootstrap managed block 已覆盖“全面检查/修复/baseline-ready/按 Figma 实现”；`NOT_READY` 明确阻止生产实现，READY 后进入 Coding Handoff；对应路由回归在 Ready/main CI 通过。 |
| 跨组件 Golden Path | required | Ready run #162 与 main run #163 都验证 `Skill source → Bundle/Project Payload → Full install`，以及 `onefile Runtime → project-only install/upgrade → project-local MCP status/smoke`；二者都自动包含 figma。 |
| External Dependency / Provider Probe | not_applicable | 本任务验证规则迁移和本地分发，不需要调用真实 Figma API；上游 Figma Skill 事实来自 GitHub 当前 main。 |
| Build / Package / Runtime | required | Ready run #162 与 main run #163 均完成 Full Distribution、Linux onefile `status/self-test`、真实 stdio MCP、项目级 binary install/upgrade/no-args install，以及 Windows/macOS onefile 和项目安装验证，三个永久 Job 全部 success。 |
| Docs / Governance / Other | required | 根 `README.md`、`.agents/README.md`、Coding README/Bootstrap/维护规则已 targeted review；业务项目污染扫描与 preservation 测试通过；独立 Review 找到并移除了唯一无关措辞差异；Ready Check 在 feature 与 main 均通过。 |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户“逐规则内容守恒”决定、Agent_Skills 当前 `AGENTS.md`、AIMA_UGC 当前 Figma Skill、Coding 02/16/17、Docs/Review 规则及 PR/main CI 事实。
- [x] change_coverage：已从上游要求独立检查完整 Figma Skill、Canvas/Prototype/Owner/状态/Ready/失败处理、Coding 路由、Bootstrap/导航、动态分发和内容守恒测试，未把“目录已复制”误当成完整需求。
- [x] reverse_audit：已从 Figma Review/Repair/Ready/Handoff 用户意图反查到 Coding ref02 → Figma canonical rules → READY/NOT_READY → Coding ref17，并从正式 Skill 反查到 Bundle/Project Payload/Full install/三平台 Runtime 项目安装消费链。
- [x] unresolved_cleared：R1–R6 均有实现、人工对照、Ready run #162 和 main run #163 的新鲜证据；无 `not_satisfied`、无未批准延期，PR #15 已正常合并到 main。

# 任务

- [x] 调查两个仓库当前 `main` 与适用规则
- [x] 建立四维任务路由：Agent Skill/Developer Tool + Feature/Rule Migration + Python/Markdown/GitHub Actions + L2
- [x] 建立失败测试并确认因 Figma Skill/路由缺失失败
- [x] 迁入完整 Figma Skill 并做最小宿主中立化
- [x] 接入 Coding/Bootstrap/README/AGENTS 路由与 Ownership
- [x] 验证动态 Bundle/Payload/Full Kit/Runtime 自动发现 figma
- [x] 完成 Docs targeted review 与内容守恒人工对照
- [x] 完成独立 Review 与 Ready HEAD 跨平台 CI / Ready Check
- [x] Draft PR 转 Ready并确认当前 HEAD CI 全绿
- [x] PR #15 正常合并 main，并确认 merge commit `61b917d410df3274104d5d9f63b31dab45a7db36`
- [x] main push `Skill Tests` run #163（`33180498028`）三平台全绿
- [x] 从已验证 main 创建独立归档分支，标记 done 并移动 Change 到 archive

# 验证

## Red / 中间 Green

- Red：初始 Figma preservation/routing/distribution tests 在正式 Figma Skill/路由尚不存在时实际失败，证明测试能捕获目标缺口；失败原因是 Figma Skill、reference、Bootstrap/Catalog 路由缺失，而不是环境故障。
- 中间 run #160（HEAD `eb10919ed597ec5934b8fe3ce9c0ddd963391ebb`）：self-contained `Ran 111 tests`，技术/分发 Job 已绿；最后 Ready Gate 正确发现 Change 当时仍未满足治理状态，未被绕过。

## Ready HEAD

```text
Ready head = 2aec73c420ae24544fd8a31fe4b13af0a16b9d7e
GitHub Actions Skill Tests run = 33180046815（run #162）
workflow conclusion = success
Skill Tests = success
Runtime macOS Package = success
Runtime Windows Package = success
Ready Check = carrier=.agents/changes, gated=8, strict=8
```

`Skill Tests` 在 Ready HEAD 实际覆盖：

- Compile helper scripts and Runtime；
- maintained CLI smoke；
- self-contained `111 tests / OK`；
- Full Distribution Kit，动态 skills = `coding, docs, figma, review`；
- Linux onefile Runtime `status/self-test`；
- real stdio MCP contract，`ok=true`、`tool_count=5`；
- project-only single-binary 首次安装、重复升级、无参数当前目录安装；
- 项目内 Runtime status 与 MCP smoke；
- active Coding Change Ready gate；
- Windows/macOS onefile build/self-test 与 project-only installation。

Ready HEAD Runtime 证据：

```text
source_digest = 44c0d91d81019353e3fca7bd000f823a6a34e669f6045c5047fbfde8dbb8e95e
payload_digest = e6ba987706c59f6979aa17a7837e5ba98e4e8ccb07faf9f2e876747e7393089c
skill_count = 4
reference_count = 31
```

## Main 再验证

```text
实现 PR = #15，同步通用 Figma Skill 与 Design-to-Code 路由
merge commit = 61b917d410df3274104d5d9f63b31dab45a7db36
main push Skill Tests run = 33180498028（run #163）
workflow conclusion = success
Skill Tests = success
Runtime macOS Package = success
Runtime Windows Package = success
```

main run #163 重新执行 self-contained tests、Full Distribution、Linux onefile Runtime、真实 stdio MCP、project-only binary installation、Ready Check 和 Windows/macOS 平台构建/安装，没有用 PR 旧结果替代主分支集成证据。

# 文档影响

Docs Impact: targeted。

- 已复核并更新根 `README.md`、`.agents/README.md`、Coding/Figma 使用入口、根维护 `AGENTS.md` 和 Bootstrap managed block，使当前正式 Figma Skill、NOT_READY/READY Handoff 与动态发现事实一致。
- Docs/Review 正式规则本身没有因本次同步被改写；未发现 `code_issue_detected`。
- 没有新增第二套机器事实；具体项目的品牌、技术栈、数据字段、页面尺寸和系统能力仍由目标项目事实与正式 Figma 负责。

# Review

A1 上游要求 → Change/实现：重新从用户“逐规则内容守恒”、Agent_Skills 根规则和 AIMA 当前 Figma 源规则建立完成定义；Canvas、Prototype、Owner、状态、Ready、失败处理、Annotation、写后复核、跨 Skill Ownership 和动态分发均进入 R1–R6，没有用当前 Change 自身替代上游要求。

A2 实现 → 测试/文档/运行证据：Figma `SKILL.md` + 00–07 references 是唯一详细设计规则 Owner；Coding ref02/ref16/ref17 只承担路由、Ownership 和 READY 后生产实现；Bootstrap/README 只维护入口；preservation/portability、Bundle/Project Payload、Full/Runtime 和三平台 CI 分别证明对应边界。

已修复 Findings：

1. 根维护规则曾直接写入业务仓库专名，导致通用 live-cleanliness 测试失败；已改为“任何外部业务仓库”，未放宽测试。
2. Coding ref02 曾混入一处与 Figma 同步无关的普通措辞修改；已恢复原文，保持 diff 全部可追溯到本 Change。
3. 原 preservation 测试只检查高价值关键词；已补强为直接锁定 4px spacing candidate grid、Annotation `24–32px`、Canvas `40–64 / 64–80 / 96–160px` fallback、每次写后 Canvas-level Review、邻接修复与 Prototype 失败处理。

最终未发现阻塞合并的正确性、通用性、兼容性、内容守恒、分发或测试充分性问题。

# Git / PR / 归档状态

- 实现 Branch：`feat/sync-universal-figma-skill`
- Ready head：`2aec73c420ae24544fd8a31fe4b13af0a16b9d7e`
- 实现 PR：#15 `同步通用 Figma Skill 与 Design-to-Code 路由`，已正常合并
- Merge commit：`61b917d410df3274104d5d9f63b31dab45a7db36`
- Ready CI：Skill Tests run #162（`33180046815`）success
- Main CI：Skill Tests run #163（`33180498028`）success
- 归档 Branch：`chore/archive-sync-universal-figma-skill`
- 归档：本文件由独立归档分支移入 `.agents/changes/archive/2026-08/`；归档 PR/合并状态以 Git 历史为最终事实
- Release：不适用；VERSION、Runtime Contract、Release asset、依赖和 API/Schema/Migration 均未变化
