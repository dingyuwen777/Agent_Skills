---
schema: coding-change/v1
id: CHG-20260826-universal-skill
title: Agent Skills 通用化与治理载体重构
level: L3
status: ready_for_review
owner: ChatGPT
branch: refactor/universal-coding-skill
created: 2026-08-26
updated: 2026-08-26
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - review-skill
  - docs-skill
  - governance
  - portability
affected_paths:
  - AGENTS.md
  - README.md
  - .agents/
  - .github/workflows/skill-tests.yml
contracts:
  - coding-change/v1
data_changes: []
---

# 目标

把 Agent_Skills 从包含业务项目 Overlay 残留的 Skill 集合改造成可用于不同项目、语言和研发阶段的通用研发 Skill，同时完整保留已有高价值研发流程和用户明确指定的跨项目工程硬规则。

# 成功标准

- [x] 根 AGENTS 不再描述业务项目架构，而只约束 Agent_Skills 自身维护。
- [x] 新增根 README，讲清适用范围、安装/接入、Coding/Review/Docs 使用方式、Greenfield、Change、cache 和硬规则。
- [x] Coding 增加 Greenfield/Bootstrap 正式路由，语言和工具链继续来自真实项目事实。
- [x] Change 只使用 `coding-change/v1`，不保留历史 schema 兼容代码/说明。
- [x] Coding Change 默认 carrier 为 `.agents/changes`，同时支持已有顶层 `changes`；发现 OpenSpec 且没有已确认 Coding carrier 时不会静默创建平行 Change。
- [x] `.agents/project-context.json` 明确为本地可失效缓存且 `.gitignore` 忽略。
- [x] 删除第 12 个规则映射 reference；内容守恒硬规则继续由 Coding 主规则、当前 Change、Review 和回归测试承担。
- [x] UI/API/Persistence/External Dependency 测试专项改为条件式 profile，保留 Mock/Integration/Contract/Golden Path/External Probe 的完整证据职责，并保留 PostgreSQL 等项目实际使用时的专项知识。
- [x] Review/Docs 人类说明和示例不再依赖具体业务项目。
- [x] 自包含测试替代对业务仓库文件树的依赖，并新增唯一轻量 `Skill Tests` CI。
- [x] 第一轮真实 GitHub Runner 已证明脚本编译和 39 个自包含测试通过，且 Ready Gate 能正确拒绝 `in_progress` Change。
- [ ] 完成最终独立 Review、最终 CI 和 PR 合并到 main。

# 范围

- 通用 Skill 规则、README、Agent metadata；
- Coding Change schema/carrier、project cache 语义；
- Coding CLI、Ready Check；
- Review/Docs 中与通用性直接相关的说明和测试分层；
- Agent_Skills 自包含测试；
- 一个只验证本仓库 Skill 的轻量 GitHub Actions Workflow。

# 非目标

- 不修改任何业务项目仓库；
- 不为未知第三方治理格式实现自动写入适配器；
- 不新增产品依赖、框架、数据库、服务或部署拓扑；
- 不新增 Browser/数据库/外部 Provider 等与本仓库无关的 CI 层；
- 不删除 TDD、根因调试、Traceability、Validation Matrix、Completion Audit、Review、Docs Impact、网络下载源和 Workflow Evidence Preservation 等既有高价值规则。

# 必须保持不变

- 代码注释统一中文；
- 所有新增或修改函数都有函数级中文说明；
- Git 提交信息中文；
- Agent 自有时间统一北京时间；
- 人类可读日志统一 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`，保留更高优先级外部 wire-format 例外；
- 当前仓库事实优先、用户工作保护、不静默升级/换路线/扩大范围、新鲜证据门禁；
- 规则通用化不得用过度总结删除仍有效的触发条件、例外、失败处理、停止条件、验证责任或兼容边界。

# 关键决策

1. Change schema 直接切换到 `coding-change/v1`，不做历史 schema 兼容。
2. 删除第 12 个规则映射 reference，不再维护独立映射台账；内容守恒由主规则、当前 Change、独立 Review 与 portability/preservation 回归承担。
3. `project-context.json` 是本地 disposable cache，不提交 Git。
4. Change 的追溯/验证/完成审计语义保持通用；carrier 优先项目既有治理，Coding fallback 使用 `.agents/changes`；已有受支持顶层 `changes` 可沿用。
5. Greenfield 作为正式阶段，不把“没有仓库事实”误解为可以静默选择默认架构。
6. Agent_Skills 自身保留一个唯一轻量 CI，只运行标准库 Python 脚本编译、自包含 unittest 和 Ready Check；不把业务项目 CI 带入本仓库。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 不保留历史 schema 兼容，只使用当前版本 | user:current-request | satisfied | `coding.py`、`CHANGE.template.md`、Ready Check 只接受 `coding-change/v1`；`test_rvc_schema_is_rejected_without_compatibility` 已在 GitHub Runner 通过 |
| R2 | 删除第 12 个规则映射 reference | user:current-request | satisfied | Git tree 删除 `references/12_*`；主 Skill 无 live 路径引用；清洁度测试已在 GitHub Runner 通过 |
| R3 | project-context.json 是本地可失效缓存且不提交 Git | user:current-request | satisfied | `.gitignore` + 根 README + `.agents/README` + reference 01 + cache portability tests |
| R4 | 其余按已确认通用化方案执行且不丢已有高价值规则 | user:current-request | satisfied | Coding 主规则和关键 references 恢复原有详细流程后做增量迁移；TDD/根因/Traceability/Matrix/Audit/Review/Docs/Git/CI 仍可达；独立 diff Review 已纠正第一版过度精简问题 |
| R5 | 新增 README 并讲明怎么使用 | user:current-request | satisfied | 根 `README.md` 覆盖安装、Coding/Review/Docs、Greenfield、L1-L3、Change、cache、CLI 和硬规则 |
| R6 | 五项特殊工程规则继续作为所有项目硬规则 | user:current-request | satisfied | 根 AGENTS、Coding SKILL、routing、README、agent prompt 和 development guidance tests 均保留 |
| R7 | 最终通过正常 PR/CI 门禁集成到 main，不绕过检查 | user:current-request | satisfied | PR #1 已创建；`Skill Tests` 已实际运行并在 Change 为 `in_progress` 时正确阻塞，当前提交推进 `ready_for_review` 后将重新执行 |
| R8 | Skill 可用于不同项目形态、语言和研发阶段，包括 Greenfield | user:current-request | satisfied | `SKILL.md` + routing 覆盖 Greenfield/Library/CLI/Service/Web/Mobile/Data/Embedded/IaC/Monorepo；polyglot/empty-repo portability tests 已通过 |
| R9 | Agent_Skills 自身测试不得依赖 AIMA 等业务仓库文件树 | AGENTS.md | satisfied | 8 个测试模块均为自包含 fixture/文本/临时仓库测试；GitHub Runner 完整 unittest 39 tests 通过 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Coding CLI、Change carrier、Ready Check、cache、portability；GitHub Runner `unittest discover` 39 tests 通过 |
| 接口 / Contract | required | `coding-change/v1` frontmatter/parser/template/Ready Check 一致；旧 schema 显式拒绝测试通过 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 本仓库无产品数据库/运行服务；脚本只依赖 Python 标准库、文件系统和 Git 子进程 |
| 用户 / Workflow Acceptance | required | GitHub Actions 在真实 checkout 上执行 `py_compile`、完整 unittest 和 `ready_check.py`；首轮 Gate 正确拒绝 `in_progress` |
| 跨组件 Golden Path | required | 模板/CLI/parser/Ready Check 通过同一 `coding-change/v1` 串接；默认/顶层 carrier 与 OpenSpec 冲突行为均有进程/临时仓库测试 |
| External Dependency / Provider Probe | not_applicable | 无产品第三方 Provider/付费 API；GitHub 仅作为仓库交付和 CI 平台 |
| Build / Package / Runtime | required | GitHub Hosted Runner Ubuntu 24.04 / Python 3.12.3：两个脚本 `py_compile` 通过，39 tests 通过 |
| Docs / Governance / Other | required | README/AGENTS/Skill 引用、删除 reference、cache ignore、项目特定残留、五项硬规则和 Workflow 均由自包含测试与 PR diff Review 覆盖 |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户明确决定、根 AGENTS、Coding 主规则及受影响 Change/cache/测试/Docs/Review 事实源；五项硬规则按用户后续明确决定保留为通用核心。
- [x] change_coverage：已覆盖不兼容旧 schema、删除 ref12、本地 cache、根 README、Greenfield、项目 Overlay 分离、carrier 适配、自包含测试和最终 main 交付要求；第一版错误的 `--change-root` 说明已删除。
- [x] reverse_audit：已从 README → Skill → references → CLI/template → tests/CI 反向检查使用说明和真实能力；OpenSpec 不会被 CLI 静默改写，Persistence 专项不再反推固定 PostgreSQL。
- [x] unresolved_cleared：Ready 前语义未满足项已清零；PR 最终 Review/CI/merge 属于 `ready_for_review` 后的集成交付动作，并继续由 PR/Workflow 门禁阻止未经验证合并。

# 任务

- [x] 恢复 main 和当前仓库事实
- [x] 建立 L3 设计与通用化范围
- [x] 重构根 AGENTS/README/Skill 使用说明
- [x] 重构 Coding 主规则和关键 references
- [x] 重构 Change schema/carrier/cache 脚本
- [x] 重构 Review/Docs 通用措辞与示例
- [x] 重建自包含测试
- [x] 增加唯一轻量 Skill Tests CI
- [x] 执行第一轮真实 GitHub Runner 验证并确认 Ready Gate 正确阻塞 in_progress
- [x] 完成 Requirement Traceability 与 Completion Audit
- [ ] 完成最终独立 Review / 最终 CI
- [ ] 合并 main、归档 Change并确认最终 main

# 验证

## 计划

- `python3 -m py_compile .agents/skills/coding/scripts/coding.py .agents/skills/coding/scripts/ready_check.py`
- `python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- `python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`
- PR diff 人工两阶段 Review：需求完整性 → 代码/规则质量与内容守恒
- PR 最终 `Skill Tests` 必须为 success 后才允许合并

## 新鲜证据

- GitHub Actions `Skill Tests` run `32947553880`，PR head `f193056cef9f00f27d717509da6cf6b35f213cfa`，Ubuntu 24.04.4 / Python 3.12.3。
- `python3 -m py_compile ...coding.py ...ready_check.py`：成功。
- `python3 -m unittest discover ...`：`Ran 39 tests`，`OK`，0 failures/errors。
- 39 tests 包含 polyglot discovery、Greenfield empty repo、local cache invalidation、默认/顶层 carrier、OpenSpec 平行治理拒绝、当前 schema、新旧 schema 拒绝、Completion Audit/Source/Evidence/changed-since/Archive、Docs/Review/网络源/Workflow evidence preservation 等回归。
- 同一 run 的最终 Ready Check 按设计失败：当前 Change 当时仍为 `in_progress`，错误精确为“状态必须为 ready_for_review”；本提交将状态推进到 `ready_for_review`，下一轮 CI 用于验证最终 Gate。
- 第一版 diff Review 发现并修复了过度精简 HIGH 问题：Coding 主规则、关键 references、Docs/Review 方法和完整脚本逻辑已恢复原始细节后仅做目标语义迁移。

# 文档影响

- `full`：本任务本身重构通用 Skill 的长期使用说明与治理边界，因此更新根 README、`.agents/README`、Coding/Docs 使用说明、受影响正式规则和仓库维护规范；Review 正式方法本来已通用的部分保持原细节。

# 交付

- Branch：`refactor/universal-coding-skill`
- Commits：`c465763`（第一版，后经 Review 修正）、`8a7e154`（恢复规则细节）、`f193056`（新增自包含 CI）及本次 Ready 状态提交
- PR：#1 `将 Agent Skills 通用化并补齐自包含验证`，Open
- CI：首轮 `Skill Tests` 的编译与 39 tests 已通过，Gate 因 `in_progress` 正确失败；等待当前 Ready 提交的下一轮完整结果
- 合并：待最终 Review/CI 后执行
- 发布：不适用
