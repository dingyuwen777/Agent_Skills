---
schema: coding-change/v1
id: CHG-20260826-universal-skill
title: Agent Skills 通用化与治理载体重构
level: L3
status: in_progress
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
- [x] Coding Change 默认 carrier 为 `.agents/changes`，同时支持已有顶层 `changes` 和显式 `--change-root`；发现 OpenSpec 时不会静默创建平行 Change。
- [x] `.agents/project-context.json` 明确为本地可失效缓存且 `.gitignore` 忽略。
- [x] 删除第 12 个规则映射 reference；内容守恒硬规则继续由 Coding 主规则和测试承担。
- [x] Web/API/Persistence 测试专项去固定数据库中心化，保留 Mock/Integration/Contract/Golden Path/External Probe 的完整证据职责。
- [x] Review/Docs 人类说明和示例不再依赖具体业务项目。
- [x] 自包含单元测试、脚本编译/帮助命令和 Ready Check 全部取得新鲜通过证据。
- [ ] 完成独立 Review 和 PR 集成。

# 范围

- 通用 Skill 规则、README、Agent metadata；
- Coding Change schema/carrier、project cache 语义；
- Coding CLI、Ready Check；
- Review/Docs 中与通用性直接相关的说明和测试分层；
- Agent_Skills 自包含测试。

# 非目标

- 不修改任何业务项目仓库；
- 不为未知第三方治理格式实现自动写入适配器；
- 不新增依赖、框架、数据库或 CI 平台；
- 不删除 TDD、根因调试、Traceability、Validation Matrix、Completion Audit、Review、Docs Impact、网络下载源和 Workflow Evidence Preservation 等既有高价值规则。

# 必须保持不变

- 代码注释统一中文；
- 所有新增或修改函数都有函数级中文说明；
- Git 提交信息中文；
- Agent 自有时间统一北京时间；
- 人类可读日志统一 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`，保留更高优先级外部 wire-format 例外；
- 当前仓库事实优先、用户工作保护、不静默升级/换路线/扩大范围、新鲜证据门禁。

# 关键决策

1. Change schema 直接切换到 `coding-change/v1`，不做历史 schema 兼容。
2. 删除第 12 个规则映射 reference，不迁移其“映射台账”职责；但内容守恒本身继续是 Coding 硬规则和测试断言。
3. `project-context.json` 是本地 disposable cache，不提交 Git。
4. Change 的追溯/验证/完成审计语义保持通用；carrier 优先项目既有治理，Coding fallback 使用 `.agents/changes`。
5. Greenfield 作为正式阶段，不把“没有仓库事实”误解为可以静默选择默认架构。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 不保留历史 schema 兼容，只使用当前版本 | user:current-request | satisfied | `coding.py`、`CHANGE.template.md`、Ready Check 和清洁度测试只接受 `coding-change/v1` |
| R2 | 删除第 12 个规则映射 reference | user:current-request | satisfied | Git tree 删除 `references/12_*`；主 Skill 无 live 链接；回归测试检查编号止于 11 |
| R3 | project-context.json 是本地可失效缓存且不提交 Git | user:current-request | satisfied | `.gitignore` + `README.md` + reference 01 + portability 测试 |
| R4 | 其余按已确认通用化方案执行且不丢已有高价值规则 | user:current-request | satisfied | `SKILL.md` 保留 TDD/根因/Traceability/Matrix/Audit/Review/Docs/Git/CI；测试逐项保护 |
| R5 | 新增 README 并讲明怎么使用 | user:current-request | satisfied | 根 `README.md` 覆盖安装、Coding/Review/Docs、Greenfield、Change、cache、CLI 和硬规则 |
| R6 | 五项特殊工程规则继续作为所有项目硬规则 | user:current-request | satisfied | 根 AGENTS、Coding SKILL、README、agent prompt、development guidance tests |
| R7 | 修改最终进入 main，不绕过仓库既有质量/Git 门禁 | AGENTS.md | not_satisfied | 待完成测试、Review、PR 合并和 main 最终确认 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Coding CLI、Change carrier、Ready Check、cache、portability 单测 |
| 接口 / Contract | required | `coding-change/v1` frontmatter/parser/template/Ready Check 一致；旧 schema 无兼容 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 本仓库无数据库/运行服务依赖；脚本仅 Python 标准库与文件/Git 子进程 |
| 用户 / Workflow Acceptance | required | CLI help、discover/status/conflicts/ready-check 的真实进程入口 |
| 跨组件 Golden Path | required | 模板/CLI 创建 Change → Ready Check 解析同一 schema 的最小真实链 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider/付费 API；GitHub 写操作属于交付通道而非产品外部依赖验证 |
| Build / Package / Runtime | required | `py_compile` + `unittest discover` + CLI `--help` |
| Docs / Governance / Other | required | README/AGENTS/Skill 引用、删除 reference、cache ignore、项目特定残留与规则完整性检查 |

# Completion Audit

- [ ] upstream_re_read：提交 Ready 前重新读取当前请求、AGENTS 和受影响 Skill 事实源。
- [ ] change_coverage：确认当前 Change 覆盖全部用户决定和已确认通用化范围。
- [ ] reverse_audit：确认 README/Skill/CLI/模板/测试相互一致，且项目特定规则没有从子规则重新注入。
- [ ] unresolved_cleared：所有 not_satisfied 清零；未验证项如实记录。

# 任务

- [x] 恢复 main 和当前仓库事实
- [x] 建立 L3 设计与通用化范围
- [x] 重构根 AGENTS/README/Skill 使用说明
- [x] 重构 Coding 主规则和关键 references
- [x] 重构 Change schema/carrier/cache 脚本
- [x] 重构 Review/Docs 通用措辞与示例
- [x] 重建自包含测试
- [x] 执行新鲜验证
- [ ] 完成 Completion Audit / Review
- [ ] 创建 PR、合并 main、归档 Change

# 验证

## 计划

- `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- `python -m py_compile .agents/skills/coding/scripts/coding.py .agents/skills/coding/scripts/ready_check.py`
- `python .agents/skills/coding/scripts/coding.py discover --help`
- `python .agents/skills/coding/scripts/coding.py status --help`
- `python .agents/skills/coding/scripts/coding.py conflicts --help`
- `python .agents/skills/coding/scripts/coding.py new-change --help`
- `python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- `python -m py_compile .agents/skills/coding/scripts/coding.py .agents/skills/coding/scripts/ready_check.py`：退出码 0。
- `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`：退出码 0，27 tests，0 failures/errors。
- `coding.py discover/status/conflicts/new-change --help` 与 `ready_check.py --help`：5 个入口全部退出码 0。
- AST 函数级文档注释审计：`missing_docstrings=[]`。
- live 非测试文本残留扫描：未发现旧 Change schema、业务项目名/路径、TikHub 或已删除第 12 reference 的 live 残留。
- `.gitignore` 精确包含 `.agents/project-context.json`。

# 文档影响

- `full`：本任务本身重构通用 Skill 的长期使用说明与治理边界，因此更新根 README、`.agents/README`、Coding/Review/Docs 使用说明和对应正式规则。

# 交付

- Commit：待创建
- PR：待创建
- CI：仓库当前没有受保护 required status checks；仍以本地自包含测试和 GitHub PR 状态为准
- 合并：待完成
- 发布：不适用
