---
schema: coding-change/v1
id: CHG-20260829-unify-skill-router-bootstrap
title: 统一 Skill Router 与源码/Runtime 双入口 Bootstrap
level: L3
status: in_progress
owner: ChatGPT
branch: refactor/unify-skill-router-bootstrap
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - agent-entry
  - skill-routing
  - runtime-bootstrap
  - project-payload
  - documentation
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/MAINTENANCE.md"
  - ".agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/assets/AGENTS.template.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/tests/"
  - "README.md"
  - "runtime/README.md"
contracts:
  - "Agent Skills Router contract"
  - "Target project AGENTS Bootstrap contract"
  - "Project Payload runtime asset contract"
data_changes: []
---

# 目标

把当前分散在 Agent_Skills 根 `AGENTS.md` 与目标项目 `AGENTS.managed.md` 中的 AI 入口职责重新分层，形成一套长期只维护一次的 Skill Router：

```text
AGENT_SKILLS_ROUTER.md
→ 唯一 Skill Catalog / Router 事实源

Agent_Skills/AGENTS.md
→ ChatGPT 网页端 / GitHub 直读源码时的薄 Bootstrap

AGENTS.managed.md
→ Runtime binary 安装到目标项目根 AGENTS.md 的薄 Bootstrap

.agents/MAINTENANCE.md
→ 仅在开发、审查、测试、交付或发布 Agent_Skills 源仓库本身时加载的维护规则
```

两种实际使用方式最终都进入同一个 Router，再由 Router 进入正式 `SKILL.md` 与命中的 References：

```text
ChatGPT + GitHub 直读 Agent_Skills
→ 根 AGENTS.md
→ canonical Router
→ Skill

Release Runtime / Codex / Cursor / Claude Code
→ 目标项目 AGENTS managed block
→ 项目内同一 Router
→ Skill / Runtime Stub / MCP canonical Reference
```

# 成功标准

- [ ] 根 `AGENTS.md` 不再承载 Agent_Skills 源仓库完整维护规范，而是成为稳定 AI Bootstrap；源码直读另一个目标项目时，它先要求遵守目标项目规则/事实，再进入唯一 Router。
- [ ] 当前根 `AGENTS.md` 中仍有效的 Agent_Skills 源仓库维护规则按内容守恒迁入 `.agents/MAINTENANCE.md`，维护任务通过根 Bootstrap 显式加载，不因迁移丢失事实优先、内容守恒、Runtime、Change/Review/CI/Git/Release、安全或完成报告门禁。
- [ ] 新增 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md` 作为唯一完整 Skill Router，覆盖当前 managed block 的项目事实优先、Coding 锚点、按需 Reference、Runtime Stub/MCP + SHA、Figma、Review、Docs、失败停止、权限/CI 门禁等语义。
- [ ] Router 能服务源码直读与 Runtime 安装两种模式：canonical Reference 文件可直接读取；安装态 Reference Stub 必须按 Stub 调用 `agent_skills_load_context` 并校验 SHA256。
- [ ] `AGENTS.managed.md` 降为薄 Bootstrap，只负责把目标项目 Agent 引到同一个 Router，不再维护第二套 Coding/Figma/Review/Docs/Reference 详细路由。
- [ ] Runtime Project Payload 自动包含 Router 运行资产；onefile 项目安装后目标项目中的 managed block 指向真实存在的 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`。
- [ ] 现有动态正式 Skill 发现保持不变：`.agents/skills/*/SKILL.md` 是正式 Skill 集合事实，不为当前四个 Skill 引入 Runtime 静态白名单；Router 可以展示当前 Catalog，但明确它不是分发白名单。
- [ ] `AGENTS.template.md`、ref13、ref14、根 `README.md`、`runtime/README.md` 与新职责一致，不再声称根 `AGENTS.md` 只用于维护源仓库或 `AGENTS.managed.md` 自己拥有完整 Router。
- [ ] 永久测试能阻止未来再次在根 `AGENTS.md` 与 `AGENTS.managed.md` 复制完整 Router，并证明 Router 被 Project Payload 分发、Bootstrap 生成结果指向 Router、关键旧规则仍可达。
- [ ] 不修改 Runtime CLI/MCP Tool schema、Reference 加密格式、installation manifest schema、正式 Skill 目录发现算法或 Release 资产合同。

# 范围

- 重构根 `AGENTS.md`、`AGENTS.managed.md` 和目标项目 Bootstrap 文档职责。
- 新增唯一 canonical Router 运行资产。
- 新增 Agent_Skills 源仓库维护规则承载文件。
- 同步 ref13/ref14、README、Runtime README 与相关回归测试。
- 必要时只对 Bootstrap/Project Payload 做最小代码改动；若现有动态 Payload 已能正确携带 Router，则不为形式修改 Runtime 代码。

# 非目标

- 不改变 Coding / Review / Docs / Figma 各自专业规则 Owner。
- 不新增第五个 Skill 或独立 Router Skill。
- 不改变 Reference Bundle/MCP Tool Contract、加密算法、Stable Reference ID 或 manifest schema。
- 不改变最终用户 `USAGE.md`、Release 资产集合或发布版本号。
- 本 Change 不创建实际 Release，也不改变 GitHub 仓库可见性。
- 不把 Agent_Skills 根 `AGENTS.md` 复制到目标项目。

# 必须保持不变

- 当前正式 Skill 继续从 `.agents/skills/*/SKILL.md` 动态发现，当前 `coding/review/docs/figma` 名称不是 Runtime 静态白名单。
- Coding 仍是当前目标项目研发入口的核心锚点；Review/Docs/Figma 保持单一详细规则 Owner 与 Coding Handoff。
- 目标项目技术栈、架构、Contract、Schema/Migration、CI、部署和设计业务事实只能来自目标项目当前规则与真实文件，不能由通用 Skill 反向推断。
- 目标项目已有 `AGENTS.md` marker 外文本逐字保护；损坏/重复 marker fail closed；安装回滚、ownership、安全边界不降低。
- Runtime Stub 仍不复制 canonical Reference 摘要正文；canonical text/hash 内容守恒不降低。
- 当前根 `AGENTS.md` 中针对 Agent_Skills 自身的事实优先、内容守恒、Runtime 维护、Change/Review/CI/Git/Release 等有效规则必须继续可达。
- Git 不强推、不重写共享历史；提交信息使用中文；不绕过永久 CI/PR 门禁。

# 关键决策

## L3 方案比较

### 方案 A：根 AGENTS 与 managed block 各维护完整 Router

优点：两个入口自包含。

缺点：新增 Skill、改变路由、调整 Stub/MCP 或跨 Skill Contract 时必须同步两份正文，最容易发生规则漂移；已经与用户希望只维护一套路由冲突。

结论：不采用。

### 方案 B：直接让根 `AGENTS.md` 与 `AGENTS.managed.md` 使用同一份完整文本

优点：表面上只维护一份内容。

缺点：两种宿主语义不同。根入口需要区分“用 Agent_Skills 帮助外部项目”和“维护 Agent_Skills 自身”；目标项目 managed block 必须只管理自身 marker 边界，不能带入源仓库维护规则。强行同文会让职责重新混杂。

结论：不采用。

### 方案 C：唯一 canonical Router + 两个薄 Bootstrap + 独立 Maintenance

```text
AGENT_SKILLS_ROUTER.md
       ↑              ↑
root AGENTS.md   AGENTS.managed.md
       │              │
source direct     Runtime-installed project

Agent_Skills maintenance task
→ root AGENTS.md
→ .agents/MAINTENANCE.md
→ same Router / Skills
```

优点：Router 只维护一次；源码直读和 Runtime 项目安装都能使用；源仓库维护规则有独立 Owner；现有 Project Payload 能自然携带 coding assets；不需要建立新 Skill 或远程依赖。

代价：增加一个明确的 Router 资产文件，并需要同步 ref13/ref14/测试对职责的描述。

结论：采用。

## 兼容、迁移、部署与回滚

- 源码直读：合入后根 `AGENTS.md` 立即成为新 Bootstrap，ChatGPT/GitHub 读取根入口后进入 Router；维护 Agent_Skills 时额外进入 `.agents/MAINTENANCE.md`。
- 已安装目标项目：不会被源仓库合并自动改写；用户下一次用新 Runtime binary 安装/升级时，Project Payload 带入 Router，并只替换自身 managed block。
- 旧 Release：保持原行为，不修改已有二进制或 tag。
- Runtime schema/CLI/MCP/manifest 不迁移；如果现有 Payload 构建已按排除规则自动包含 Router，不新增代码级 Migration。
- 回滚源码：正常 Git revert/后续 PR 恢复旧入口，不重写历史。
- 回滚目标项目：继续使用安装器现有快照/ownership 回滚边界或使用上一正式 Release；不得通过删除用户 `AGENTS.md` 或清理项目自有 `.agents` 内容回滚。

## 安全、性能与运维

- 不引入网络读取、远程 KMS、新 Secret 或生产环境写入。
- Router 是小型 Markdown 运行资产，对 Payload 体积影响可忽略，但必须进入 `payload_digest`。
- canonical References 仍由加密 Bundle 承载；新增 Router 不把 Reference 正文泄露到目标项目。
- 仓库源码保密仍由 GitHub repository access control 决定，本 Change 不改变该事实。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 根 AGENTS 应成为 ChatGPT/GitHub 直接使用 Agent_Skills 时的稳定 Skill Library 入口 | user:本轮已确认设计 | not_satisfied | 待实现并验证根 Bootstrap |
| R2 | `AGENTS.managed.md` 在 Runtime 分发中保留，但只作为目标项目薄 Bootstrap，不再维护第二套完整 Router | user:本轮已确认设计 | not_satisfied | 待实现并验证安装结果 |
| R3 | Skill Router 只能有一个 canonical 事实源，两个入口都指向它 | user:本轮已确认设计 | not_satisfied | 待新增 Router 与防复制回归 |
| R4 | 当前根 AGENTS 的源仓库维护规则迁到独立 `.agents/MAINTENANCE.md`，内容守恒 | user:本轮已确认设计 | not_satisfied | 待迁移并做旧入口反向检查 |
| R5 | Router 必须同时支持源码直接 Reference 和 Runtime Stub → MCP canonical Reference 两种加载模式 | user:本轮已确认设计 | not_satisfied | 待 Router 文本与 Project Payload/安装测试 |
| R6 | 不破坏动态 Skill Catalog、Project Payload、AGENTS marker/ownership/rollback、CI/PR 质量门禁 | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | not_satisfied | 待相关测试与 CI |
| R7 | 规则迁移不能降低触发、例外、失败处理、验证、安全与兼容边界 | `.agents/skills/coding/references/16_规则内容守恒与Skill维护.md` | not_satisfied | 待 preservation 回归与人工内容守恒 Review |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新增 Router 单一事实源/内容守恒测试；更新 Bootstrap 行为测试，证明薄入口与失败边界 |
| 接口 / Contract | required | 验证 AGENTS Bootstrap、Router 路径和 Project Payload 资产合同；不改变 MCP/manifest schema |
| 集成 / Persistence / Runtime Dependency | required | 构建 Project Payload 并验证 Router 真正进入安装态 Skill；onefile 项目安装由永久 CI 覆盖 |
| 用户 / Workflow Acceptance | required | 验证源码直读入口 `AGENTS.md → Router` 与目标项目 `managed block → Router` 两条可观察导航链 |
| 跨组件 Golden Path | required | Runtime binary → Project Payload → target AGENTS managed block → installed Router 的关键接线由现有 onefile/project install CI 证明 |
| External Dependency / Provider Probe | not_applicable | 不依赖第三方服务、硬件或远端业务环境；GitHub CI 属交付基础设施而非本任务业务 Provider Probe |
| Build / Package / Runtime | required | Linux/Windows/macOS onefile build/self-test/project install 与 real stdio MCP 永久 CI 必须继续绿色 |
| Docs / Governance / Other | required | ref13/ref14、README/runtime README、L3 Change、A1/A2、Ready Check 与内容守恒人工审查 |

# Completion Audit

- [ ] upstream_re_read：重新读取本轮用户确认、根 AGENTS、Coding SKILL、ref13/ref14/ref16/ref10/ref11/ref15，独立重建完成定义。
- [ ] change_coverage：确认双入口、唯一 Router、Maintenance、Runtime 分发、迁移兼容和防重复维护全部进入 Change。
- [ ] reverse_audit：从源码直读与 Runtime 安装两端反向追到 Router/Skill/Reference，并复核 Payload、marker、动态 Skill 与验证层级。
- [ ] unresolved_cleared：全部 `not_satisfied` 清零；所有不适用项都有事实依据。

# 任务

- [x] 调查当前实现和事实源，确认根 AGENTS 与 managed block 当前职责及 Runtime/源码 Bootstrap 消费关系。
- [x] 建立四维任务路由：Infra/Developer Tool + Governance/Runtime Bootstrap 重构；Python/Markdown/GitHub Actions；L3。
- [ ] 建立会因缺少唯一 Router、Maintenance 迁移或 Payload 分发而失败的 Red 回归。
- [x] 建立 Validation Matrix。
- [ ] 新增 canonical Router，并把根 AGENTS / managed block 收敛为薄 Bootstrap。
- [ ] 逐规则内容守恒迁移源仓库维护规则到 `.agents/MAINTENANCE.md`。
- [ ] 同步 ref13/ref14、README、runtime README 和必要 Bootstrap 模板描述。
- [ ] 运行目标测试、自包含全量测试、Ready Check 与三平台永久 CI。
- [ ] 完成 Review A1/A2、代码质量 Review、Requirement Traceability 与 Completion Audit。

# 验证

## 计划

- Red：新增 `test_skill_router_single_source.py`，在 Router/Maintenance 尚不存在时必须失败。
- Target：`test_skill_router_single_source.py`、`test_project_bootstrap.py`、`test_dynamic_skill_distribution.py`、`test_release_only_repository_surface.py`、single-binary project install 相关测试。
- Full：`python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- Ready：`python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。
- CI：`.github/workflows/skill-tests.yml` 的 Linux self-contained/onefile/MCP/install/Ready + Windows/macOS package/install。

## 新鲜证据

- 尚未执行 Red/Green。

# 文档影响

- `README.md`：改为说明根 AGENTS 是 AI Bootstrap、`.agents/MAINTENANCE.md` 是源仓库维护规则、Router 是唯一 Skill 路由源。
- `runtime/README.md`：说明 Router 是 Project Payload 正式运行资产，managed block 只做指针。
- ref13/ref14：同步 Bootstrap/Runtime Contract，不能继续把旧职责描述当事实。
- `USAGE.md`：最终用户操作不变，预计无文档影响。

# 交付

- Commit：开发中。
- PR：待创建。
- 发布：本 Change 不创建 Release。
