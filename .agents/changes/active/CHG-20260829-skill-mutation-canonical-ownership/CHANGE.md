---
schema: coding-change/v1
id: CHG-20260829-skill-mutation-canonical-ownership
title: 建立 Skill Mutation canonical ownership 与跨仓库同步路由
level: L3
status: in_progress
owner: ChatGPT
branch: refactor/skill-mutation-canonical-ownership
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - agent-entry
  - skill-routing
  - canonical-ownership
  - cross-repository-workflow
  - runtime-bootstrap
  - documentation
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/MAINTENANCE.md"
  - ".agents/skills/ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/references/16_规则内容守恒与Skill维护.md"
  - ".agents/skills/coding/tests/"
contracts:
  - "Skill Mutation intent routing contract"
  - "Canonical Skill Repository ownership contract"
  - "Target project vs universal Skill ownership boundary"
data_changes: []
---

# 目标

把 `dingyuwen777/Agent_Skills` 固化为通用 Agent Skill 的 canonical source repository，使用户在任意目标项目会话中提出下列意图时，不在业务项目或 Runtime 安装副本中维护第二份 Skill 正文，而是自动切换到 Agent_Skills 维护链：

```text
更新 / 修改 / 删除 / 新增 / 重命名 Skill
更新 / 修改 / 删除 / 新增 Reference
规则迁移 / 拆分 / 合并 / 通用化
调整 Router / Skill Ownership / Skill assets / scripts / tests
```

目标项目继续提供本次规则需求的真实背景和证据；Agent_Skills 负责 canonical 通用规则的写入、Review、CI、PR、merge 和 archive。

# 成功标准

- [ ] 根 `AGENTS.md` 明确：外部项目模式下若用户提出 Skill Mutation 意图，当前动作目标切换为 Agent_Skills Maintenance Mode，并重新读取 Agent_Skills 当前分支事实源；普通项目开发仍不读取 Maintenance。
- [ ] `.agents/skills/ROUTER.md` 成为 Skill Mutation 意图识别和 canonical repository ownership 的唯一跨 Skill Router Owner，覆盖新增、修改、删除、重命名、迁移、拆分、合并、通用化和 Reference/asset/script/test 等维护意图。
- [ ] Router 明确：目标项目中的 Runtime 安装副本、Reference Stub、缓存或历史聊天都不是 canonical Skill 写入目标；canonical 明文来自 `dingyuwen777/Agent_Skills` 当前源码仓库。
- [ ] Router 明确 universal vs project-specific 边界：可跨项目复用的研发规则进入 Agent_Skills；项目技术栈、业务字段、Provider、Schema、部署、品牌/设计业务事实留在目标项目 Overlay/正式事实源。
- [ ] 用户明确说“更新 Skill”等 Skill 本身操作时默认按 canonical Agent_Skills 处理；用户明确限定“只改当前项目规则 / 项目自有 Skill”时不得越权同步到 Agent_Skills；Ownership 无法从仓库事实安全判断时 fail closed，不猜测。
- [ ] `.agents/MAINTENANCE.md` 明确 Skill Mutation 的标准维护链：重新读当前 main/AGENTS/Maintenance/Router/Coding/ref16/受影响 Skill；L2/L3 Change；内容守恒；测试；独立 Review；CI；PR；main 新鲜 CI；archive。
- [ ] `AGENTS.managed.md` 继续保持薄 Bootstrap，只增加“Skill Mutation 不修改本地安装副本，按 Router 切 canonical repo”的指针，不复制详细 Mutation 规则。
- [ ] ref13/ref14 明确目标项目 managed block 和 Project Payload 只是分发/入口，不成为 canonical Skill mutation owner；Runtime schema、CLI、MCP Tool Contract 不改变。
- [ ] ref16 明确新增/删除/重命名 Skill、Reference 与跨仓库同步属于内容守恒维护，并定义新 Skill/删除 Skill 的 live 引用、动态发现、Payload/Bundle/Router Catalog、测试与失败边界。
- [ ] 永久测试证明上述入口、Ownership、project-specific 防污染和 Runtime 分发副本边界；Project Payload 继续原样携带更新后的 Router/managed block。

# 非目标

- 不把 ChatGPT Custom Instructions 作为 canonical Skill 规则事实源。
- 不让 Runtime/MCP 自动写 GitHub；它仍只负责安装、分发和 canonical Reference 原文加载。
- 不把项目特定技术栈、业务规则或设计事实迁入通用 Skill。
- 不新增固定 Skill 白名单；正式 Skill 仍由 `.agents/skills/*/SKILL.md` 动态发现。
- 不改变 Runtime Bundle / Project Payload / install manifest schema、MCP Tool schema、加密格式或 Release 资产集合。
- 不为历史 Runtime 版本增加兼容逻辑。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 任意项目会话中说“更新 Skill”等操作时自动切换到 Agent_Skills canonical 仓库 | user:current-request | pending | Red/Green 后补 |
| R2 | 修改/删除规则、Reference、新增/删除/重命名 Skill 都属于同一 Mutation 路由 | user:current-request | pending | Red/Green 后补 |
| R3 | Agent_Skills 作为独立 Skill 仓库维护，项目本地不维护第二份 canonical 明文 | user:current-request | pending | Red/Green 后补 |
| R4 | 项目特定事实不能污染通用 Skill | user:current-request + current Router/Maintenance | pending | Red/Green 后补 |
| R5 | Runtime 安装态继续可用且不变成 Skill 写入 Owner | ref13/ref14 | pending | Red/Green 后补 |

# Validation Matrix

| Layer | Required | Scope |
| --- | --- | --- |
| 行为 / Unit / Component | required | Mutation Router、root/managed Bootstrap、Maintenance/ref16 ownership 回归 |
| 接口 / Contract | required | canonical repo ownership、project-specific boundary、Runtime distribution-only boundary |
| 集成 / Runtime Dependency | required | Project Payload exact Router/managed asset；onefile project install 继续通过 |
| 用户 / Workflow Acceptance | required | 外部项目 → Agent_Skills → Mutation → canonical Skill；以及项目自有规则不越权同步 |
| 跨组件 Golden Path | required | Router/Skill/Reference + Runtime payload/install + Git/Review/CI delivery |
| External Dependency / Provider Probe | not_applicable | 无业务 Provider 或生产外部依赖 |
| Build / Package / Runtime | required | Linux/Windows/macOS 永久 onefile/package/install |
| Docs / Governance / Other | required | A1/A2、内容守恒、Docs targeted、Ready Check、archive |

# TDD / Review 计划

1. 先新增会因当前缺少 Mutation Contract 而失败的 preservation/portability 测试；
2. 通过 PR CI 取得 Red；
3. 只修改 Owner 文件，不把详细规则复制到 managed block；
4. Target → Full → three-platform CI；
5. 独立 Review 重点审查：项目特定规则污染、安装副本被误当 canonical、无写权限时假装同步、删除/重命名 Skill 留下 live 引用、Custom Instructions 被误当上位事实源；
6. Requirement Traceability / Completion Audit 全部 satisfied 后切 `ready_for_review`；
7. 正常合并、main 新鲜 CI、独立归档。

# 当前事实

- 基线：`main@e64eb3644c21342920fe24a3d171c776254a80b6`。
- 当前唯一 Router：`.agents/skills/ROUTER.md`。
- 当前正式 Skill：通过 `.agents/skills/*/SKILL.md` 动态发现。
- 当前目标项目 managed block：薄 Bootstrap，只指向 Router。
- 当前 Runtime：Project Payload v2 + install manifest v2；本 Change 不改 schema。
- 当前 active Change：本 Change 创建前为 0。
