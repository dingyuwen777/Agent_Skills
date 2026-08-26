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
- [x] Coding Change 默认 carrier 为 `.agents/changes`；只有已存在且全部 `CHANGE.md` 都属于当前 schema 的顶层 `changes` 才会被认作受支持 carrier；OpenSpec、空顶层 changes、外部 schema 或 mixed schema 都不会被静默污染。
- [x] `.agents/project-context.json` 明确为本地可失效缓存且 `.gitignore` 忽略。
- [x] 删除第 12 个规则映射 reference；内容守恒硬规则继续由 Coding 主规则、当前 Change、Review 和回归测试承担。
- [x] UI/API/Persistence/External Dependency 测试专项改为条件式 profile，保留 Mock/Integration/Contract/Golden Path/External Probe 的完整证据职责，并保留 PostgreSQL 等项目实际使用时的专项知识。
- [x] Review/Docs 人类说明和示例不再依赖具体业务项目。
- [x] 自包含测试替代对业务仓库文件树的依赖，并新增唯一轻量 `Skill Tests` CI。
- [x] 最终独立 Review 已完成，期间发现并修复“过度精简”和“Change carrier 污染”两个 HIGH 问题；修复后未发现新的 BLOCKER/HIGH。
- [x] PR 最新代码 head `6a33ec510a452311288250deb32be0a7934b0190` 的 `Skill Tests` 已在真实 GitHub Runner 全绿：两个脚本编译通过、43/43 tests 通过、Ready Check 通过。
- [ ] PR 合并到 main，并在合并后按实际集成结果归档本 Change、再次验证 main。

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
4. Change 的追溯/验证/完成审计语义保持通用；项目既有治理优先，Coding fallback 使用 `.agents/changes`。顶层 `changes` 只有在已存在 Change 且全部现有 `CHANGE.md` 都是 `coding-change/v1` 时才允许作为受支持 Coding carrier；mixed/foreign/empty 顶层治理均拒绝隐式写入。
5. Greenfield 作为正式阶段，不把“没有仓库事实”误解为可以静默选择默认架构。
6. Agent_Skills 自身保留一个唯一轻量 CI，只运行标准库 Python 脚本编译、自包含 unittest 和 Ready Check；不把业务项目 CI 带入本仓库。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 不保留历史 schema 兼容，只使用当前版本 | user:current-request | satisfied | `coding.py`、`CHANGE.template.md`、Ready Check 只接受 `coding-change/v1`；`test_rvc_schema_is_rejected_without_compatibility` 在最终 CI 通过 |
| R2 | 删除第 12 个规则映射 reference | user:current-request | satisfied | Git tree 删除 `references/12_*`；主 Skill 无 live 路径引用；清洁度测试在最终 CI 通过 |
| R3 | project-context.json 是本地可失效缓存且不提交 Git | user:current-request | satisfied | `.gitignore` + 根 README + `.agents/README` + reference 01 + cache portability tests |
| R4 | 其余按已确认通用化方案执行且不丢已有高价值规则 | user:current-request | satisfied | Coding 主规则和关键 references 恢复原有详细流程后做增量迁移；TDD/根因/Traceability/Matrix/Audit/Review/Docs/Git/CI 仍可达；第一轮 Review 已纠正过度精简 |
| R5 | 新增 README 并讲明怎么使用 | user:current-request | satisfied | 根 `README.md` 覆盖安装、Coding/Review/Docs、Greenfield、L1-L3、Change、cache、CLI 和硬规则 |
| R6 | 五项特殊工程规则继续作为所有项目硬规则 | user:current-request | satisfied | 根 AGENTS、Coding SKILL、routing、README、agent prompt 和 development guidance tests 均保留 |
| R7 | 最终通过正常 PR/CI 门禁集成到 main，不绕过检查 | user:current-request | satisfied | PR #1 Open/mergeable；最新代码 head `6a33ec5` 的 `Skill Tests` run `32949316192` success；当前证据同步提交后仍需再次通过同一 CI 才合并 |
| R8 | Skill 可用于不同项目形态、语言和研发阶段，包括 Greenfield | user:current-request | satisfied | `SKILL.md` + routing 覆盖 Greenfield/Library/CLI/Service/Web/Mobile/Data/Embedded/IaC/Monorepo；polyglot/empty-repo portability tests 通过 |
| R9 | Agent_Skills 自身测试不得依赖 AIMA 等业务仓库文件树 | AGENTS.md | satisfied | 8 个测试模块均为自包含 fixture/文本/临时仓库测试；最终 GitHub Runner 完整 unittest 43 tests 通过 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Coding CLI、Change carrier、Ready Check、cache、portability；GitHub Runner `unittest discover` 43 tests 通过 |
| 接口 / Contract | required | `coding-change/v1` frontmatter/parser/template/Ready Check 一致；旧 schema 显式拒绝测试通过 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 本仓库无产品数据库/运行服务；脚本只依赖 Python 标准库、文件系统和 Git 子进程 |
| 用户 / Workflow Acceptance | required | GitHub Actions 在真实 PR merge checkout 上执行 `py_compile`、完整 unittest 和 `ready_check.py`；最终均成功 |
| 跨组件 Golden Path | required | 模板/CLI/parser/Ready Check 使用同一 `coding-change/v1`；默认、current top-level、empty、foreign、mixed、OpenSpec carrier 行为均有真实临时仓库回归 |
| External Dependency / Provider Probe | not_applicable | 无产品第三方 Provider/付费 API；GitHub 仅作为仓库交付和 CI 平台 |
| Build / Package / Runtime | required | GitHub Hosted Runner Ubuntu 24.04.4 / Python 3.12.3：两个脚本 `py_compile` 通过，43 tests 通过 |
| Docs / Governance / Other | required | README/AGENTS/Skill 引用、删除 reference、cache ignore、项目特定残留、五项硬规则、Workflow 和 carrier 治理均由自包含测试与 PR diff Review 覆盖 |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户明确决定、根 AGENTS、Coding 主规则及受影响 Change/cache/测试/Docs/Review 事实源；五项硬规则按用户后续明确决定保留为通用核心。
- [x] change_coverage：已覆盖不兼容旧 schema、删除 ref12、本地 cache、根 README、Greenfield、项目 Overlay 分离、carrier 适配、自包含测试和最终 main 交付要求；第一版错误的 `--change-root` 说明已删除。
- [x] reverse_audit：已从 README → Skill → references → CLI/template → tests/CI 反向检查使用说明和真实能力；OpenSpec、空/foreign/mixed 顶层 changes 不会被 CLI 静默污染，Persistence 专项不再反推固定 PostgreSQL。
- [x] unresolved_cleared：Ready 前语义未满足项已清零；PR merge 与归档属于 `ready_for_review` 后的集成交付动作，并继续由 PR/Workflow 和合并后 main 复验约束。

# 任务

- [x] 恢复 main 和当前仓库事实
- [x] 建立 L3 设计与通用化范围
- [x] 重构根 AGENTS/README/Skill 使用说明
- [x] 重构 Coding 主规则和关键 references
- [x] 重构 Change schema/carrier/cache 脚本
- [x] 重构 Review/Docs 通用措辞与示例
- [x] 重建自包含测试
- [x] 增加唯一轻量 Skill Tests CI
- [x] 完成 Requirement Traceability 与 Completion Audit
- [x] 完成最终独立 Review；修复所有 BLOCKER/HIGH
- [x] 最新代码 head 完成最终 CI：编译、43 tests、Ready Check 全绿
- [ ] 合并 main、按真实集成结果归档 Change并确认最终 main

# 验证

## 计划

- `python3 -m py_compile .agents/skills/coding/scripts/coding.py .agents/skills/coding/scripts/ready_check.py`
- `python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- `python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`
- PR diff 人工两阶段 Review：需求完整性 → 代码/规则质量与内容守恒
- PR 最终 `Skill Tests` 必须为 success 后才允许合并
- 合并后 main 再执行/确认 `Skill Tests`，随后单独归档 Change 并再次验证 main

## 新鲜证据

- GitHub Actions `Skill Tests` run `32949316192`，PR code head `6a33ec510a452311288250deb32be0a7934b0190`，PR merge checkout `8303f242ab2937e53f0b1fd19688a1cefc16da6e`，Ubuntu 24.04.4 / Python 3.12.3。
- `python3 -m py_compile .agents/skills/coding/scripts/coding.py .agents/skills/coding/scripts/ready_check.py`：成功。
- `python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`：`Ran 43 tests in 0.840s`，`OK`，0 failures/errors。
- 最终 43 tests 包含 polyglot discovery、Greenfield empty repo、local cache invalidation、默认/current top-level/empty/foreign/mixed/OpenSpec carrier、当前/旧 schema、Completion Audit/Source/Evidence/changed-since/Archive、Docs/Review/网络源/Workflow evidence preservation 等回归。
- `python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`：`Ready Check 通过：carrier=.agents/changes，gated=1，strict=1。`
- 独立 Review 第一轮发现 HIGH：第一版规则/脚本过度精简；已恢复原始详细流程后做最小语义迁移。
- 独立 Review 第二轮发现 HIGH：顶层 `changes` 可能被无 schema 证据静默认领；已修为只有 current schema 证据才可认领。
- 独立 Review 最后一轮进一步收紧 mixed-carrier：只有顶层现有 `CHANGE.md` 全部为 `coding-change/v1` 才认作 Coding carrier；新增 mixed schema 回归并在上述 43 tests 中通过。
- 修复后最终 Review 未发现新的 BLOCKER/HIGH；未通过测试、局部自检或旧日志没有被用来替代本轮 GitHub Runner 证据。

# 文档影响

- `full`：本任务本身重构通用 Skill 的长期使用说明与治理边界，因此更新根 README、`.agents/README`、Coding/Docs 使用说明、受影响正式规则和仓库维护规范；Review 正式方法本来已通用的部分保持原细节。

# 交付

- Branch：`refactor/universal-coding-skill`
- PR：#1 `将 Agent Skills 通用化并补齐自包含验证`，Open / mergeable
- Latest code head：`6a33ec510a452311288250deb32be0a7934b0190`
- CI：`Skill Tests` run `32949316192` success；编译、43 tests、Ready Check 全绿
- Review：两阶段独立 Review 已完成，所有已发现 BLOCKER/HIGH 已修复，当前无未解决 BLOCKER/HIGH
- 合并：待本次纯证据同步提交再次通过 `Skill Tests` 后执行
- 发布：不适用
