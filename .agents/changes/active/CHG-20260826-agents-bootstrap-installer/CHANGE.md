---
schema: coding-change/v1
id: "CHG-20260826-agents-bootstrap-installer"
title: "目标项目 AGENTS Bootstrap 与 Agent Skills 安装升级入口"
level: L3
status: in_progress
owner: "ChatGPT"
branch: "feature/agents-bootstrap-installer"
created: 2026-08-26
updated: 2026-08-26
completion_gate: required
depends_on: []
affected_areas:
  - "Coding Skill"
  - "Project Bootstrap"
  - "Installation and Upgrade"
  - "Target Project Overlay"
  - "CI"
affected_paths:
  - ".agents/skills/coding/SKILL.md"
  - ".agents/skills/coding/scripts/coding.py"
  - ".agents/skills/coding/assets"
  - ".agents/skills/coding/tests"
  - "scripts/install.py"
  - "README.md"
  - ".agents/README.md"
  - ".github/workflows/skill-tests.yml"
contracts:
  - "目标项目根 AGENTS.md Overlay"
  - "Agent Skills managed block"
  - "coding.py bootstrap CLI"
  - "scripts/install.py 安装/升级 CLI"
data_changes: []
---

# 目标

为 Agent_Skills 增加正式、可重复、可升级的目标项目接入能力，使用户不再需要手工复制 `.agents/skills/` 后再手工编写目标项目 `AGENTS.md`。

目标项目接入后必须形成以下稳定关系：

```text
目标项目 AGENTS.md
→ 明确要求研发任务读取并使用 .agents/skills/coding/SKILL.md
→ Coding 按当前项目事实和任务类型路由 references / review / docs
```

安装和 Bootstrap 必须区分“通用 Skill”与“目标项目 Overlay”：Agent_Skills 根 `AGENTS.md` 继续只用于维护 Agent_Skills 自身，不复制到目标业务项目；目标项目 `AGENTS.md` 负责项目真实语言、工具链、架构、目录、Contract、Schema/Migration、CI、部署和项目特殊约束。

# 成功标准

- [ ] 提供一个从 Agent_Skills 仓库执行的安装/升级脚本，可把 `coding`、`review`、`docs` 三个 Skill 同步到任意目标项目的 `.agents/skills/`，且不复制 Agent_Skills 自身 `.agents/changes/`、本地缓存或其他仓库维护数据。
- [ ] `coding.py` 增加 `bootstrap --root <target>` 入口，用于创建或增量补充目标项目根 `AGENTS.md`，并确保 `.agents/project-context.json` 被目标项目忽略。
- [ ] 目标项目没有 `AGENTS.md` 时，Bootstrap 创建一个可维护的项目 Overlay 初版；初版包含 Agent Skills 统一入口、项目事实导航占位/说明，但不根据 Manifest 名称猜测框架、数据库、架构或业务事实。
- [ ] 目标项目已经有 `AGENTS.md` 时，Bootstrap 保留原文，仅增加或更新 Agent Skills 自管区；不得整体重写、压缩、重排或删除用户已有规则。
- [ ] Agent Skills 自管区使用稳定 managed markers，重复执行不会重复插入；升级时只替换 managed markers 内的内容，marker 外原文保持不变。
- [ ] 已有 `AGENTS.md` 出现不完整/冲突的 managed marker 时，工具拒绝猜测性覆盖并给出明确错误，而不是损坏原文。
- [ ] Bootstrap 对 `.gitignore` 的处理同样幂等：没有 `.agents/project-context.json` 时补充，已经存在等价忽略项时不重复；不得清理或重写其他 ignore 规则。
- [ ] Coding Skill 正式规则新增目标项目 Bootstrap 自检：有写权限且任务要求安装/初始化时，缺失 `AGENTS.md` 可创建；已有文件只能增量接入；普通只读分析/Review 不因发现缺失而越权创建文件。
- [ ] 根 README 与 `.agents/README.md` 说明首次安装、重复升级、managed block、项目 Overlay 与本地缓存边界。
- [ ] CI 对新增安装脚本和 Bootstrap 测试实际生效，不出现 `scripts/install.py` 未进入 workflow paths/compile/test 范围的缺口。
- [ ] 自包含测试覆盖空仓库、无 `AGENTS.md`、已有 `AGENTS.md`、重复 Bootstrap、managed block 升级、损坏 marker、`.gitignore` 幂等、非 Python/多语言项目、不复制 Change/缓存等关键边界。

# 范围

- 新增 Agent_Skills 到目标项目的安装/升级入口。
- 新增目标项目 `AGENTS.md` Bootstrap 模板和 managed block 模板。
- 在现有 Coding CLI 上增加 Bootstrap 能力，复用现有项目发现基础，不建立第二套项目扫描器。
- 只对 Coding Skill 中与目标项目安装/Bootstrap 直接相关的规则做增量补充。
- 增加对应自包含测试与 CI 覆盖。
- 更新用户入口文档。

# 非目标

- 不把 Agent_Skills 根 `AGENTS.md` 复制为目标项目 `AGENTS.md`。
- 不让脚本自动判定 FastAPI、Vue、React、Spring、PostgreSQL 等项目技术选型。
- 不自动生成完整架构文档、Blueprint、ADR、Contract、Migration 或 CI 设计。
- 不把 `project-context.json` 变成提交到 Git 的项目事实数据库。
- 不自动修改目标项目已有 OpenSpec/RFC/ADR/Change 等治理载体。
- 不删除或覆盖目标项目 `.agents/changes/`。
- 不把三个 Skill 合并成单一大文件。
- 不改变 `coding-change/v1` schema。
- 不删除、压缩或重写现有 Coding/Review/Docs 高价值规则正文。

# 必须保持不变

- 通用 Skill 规定“怎样可靠工作”，目标项目规定“这个项目具体是什么”的边界保持不变。
- Agent_Skills 根 `AGENTS.md` 继续只治理 Agent_Skills 仓库自身。
- `coding`、`review`、`docs` 保持独立职责；Coding 在适用时路由 Review/Docs。
- `coding-change/v1`、Requirement Traceability、Validation Matrix、Completion Audit、Ready Check 语义保持不变。
- `.agents/project-context.json` 继续是目标项目本地可失效缓存，不提交 Git。
- 现有 Change carrier 识别、OpenSpec/外部治理保护和 mixed schema 防污染行为保持不变。
- 用户定义的五项跨项目工程硬规则保持完整：中文代码注释、所有新增/修改函数具有函数级中文说明、中文 Git 提交、默认北京时间、统一人类可读日志前缀。
- 现有 `SKILL.md` 与 references 的触发条件、例外、失败处理、停止条件、验证责任、安全和兼容边界不得因为本次接入能力而被概括、降级或丢失。

# 关键决策

## 方案比较

### 方案 A：仅要求用户手工复制 `.agents/skills/` 并手工写 `AGENTS.md`

优点：实现最少。

缺点：首次接入步骤依赖人工记忆；不同项目的入口文本容易漂移；升级时无法稳定维护；无法保证已有 `AGENTS.md` 的增量接入和幂等性。

### 方案 B：只让大模型自由读取仓库后生成/重写 `AGENTS.md`

优点：能理解项目语义。

缺点：对已有规则的保护不可确定；重复执行容易漂移；首次运行前 Agent 甚至可能不知道应读取 `.agents/skills/coding/SKILL.md`；不适合作为安装 Contract。

### 方案 C：确定性 Bootstrap + Skill 语义补全（采用）

由脚本负责可机械证明的安装、managed block、`.gitignore` 和幂等更新；由 Coding Skill 在后续项目任务中依据真实仓库事实理解项目语义。脚本不猜项目架构，Skill 不承担第一次安装必须成功的文件同步职责。

这是满足“安全保留已有规则 + 可自动安装升级 + 不伪造项目事实”三个硬约束的最小机制。

## AGENTS.md managed block

使用稳定 marker：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

- 无 marker：保留原文，在文件末尾增量追加 managed block；
- 完整 marker：只替换 marker 内自管内容；
- marker 重复、只有 start、只有 end、顺序错误：拒绝修改并报告错误；
- marker 外内容必须逐字保留。

## 新建 AGENTS.md

空仓库或缺失 `AGENTS.md` 时创建最小项目 Overlay 初版，包含：

- 项目 Agent 规则说明；
- Agent Skills managed block；
- 当前项目事实/事实源导航的维护说明；
- 明确禁止把自动发现的 Manifest 名称直接解释成框架、数据库、架构事实。

确定性脚本只写结构和已知 Skill 路径，不自动生成未经语义确认的项目架构描述。

## 安装升级

根 `scripts/install.py` 只同步：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

目标 `.agents/skills/` 中这三个受管 Skill 可按源仓当前版本更新；目标项目其他 `.agents/` 内容不删除、不清理。

复制完成后调用目标项目中已安装的 Coding CLI Bootstrap。安装器必须支持重复执行并保持幂等结果。

## Migration / 兼容

- 这是新增入口，不删除现有手工复制方式；现有用户仍可继续按 README 的手工方式安装。
- 已有目标项目 `AGENTS.md` 不需要迁移全文，只由 managed block 增量接入。
- 已有 `.agents/skills/` 在安装器再次执行时升级受管三个 Skill；其他项目自有目录不受影响。
- 不修改 Change schema 或历史 archived Change。

## 回滚

- 回滚安装器/Bootstrap 代码不会自动删除任何目标项目 `AGENTS.md` 内容；目标项目中的 managed block 是普通文本，可由项目 Owner 显式删除。
- 安装升级过程必须避免先删除全部目标 Skill 再复制导致失败后目录为空；实现应使用可控的逐 Skill 替换/临时目录策略，或在测试中证明失败边界不会误删目标项目非受管内容。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 没有 `AGENTS.md` 时根据目标项目接入需要创建初版 | user:current-request | not_satisfied | 尚未实现 |
| R2 | 已有 `AGENTS.md` 时在原文基础上补充而不是覆盖 | user:current-request | not_satisfied | 尚未实现 |
| R3 | 创建或修改后的 `AGENTS.md` 必须明确研发过程使用 `.agents/skills/coding/SKILL.md`，并由 Coding 路由 Review/Docs | user:current-request | not_satisfied | 尚未实现 |
| R4 | 接入流程可以由代码/Skill 自动完成，而不是每个项目手工维护 | user:current-request | not_satisfied | 尚未实现 |
| R5 | 不得因实现本功能而过度总结、压缩或丢失现有 Skill/reference 原文规则信息 | user:preserve-original-detail | not_satisfied | 尚未完成 Review |
| R6 | 所有 Agent_Skills 仓库开发、验证、Git 和交付遵守当前根 `AGENTS.md` | AGENTS.md | not_satisfied | 尚未完成 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Bootstrap managed block、AGENTS 创建/更新、marker 错误、gitignore、安装目录同步均需自包含单元/临时目录测试 |
| 接口 / Contract | required | `coding.py bootstrap` 与 `scripts/install.py --target` 是公开 CLI；验证参数、退出码、生成文件 Contract 和重复执行兼容性 |
| 集成 / Persistence / Runtime Dependency | required | 使用真实临时文件系统执行复制、覆盖、目录保留、Bootstrap 与 gitignore 修改，不用纯 Mock 冒充文件系统行为 |
| 用户 / Workflow Acceptance | required | 从模拟 Agent_Skills source 到空/已有项目执行真实安装命令，检查最终 `.agents/skills/`、`AGENTS.md`、`.gitignore` |
| 跨组件 Golden Path | required | 根安装器 → 已复制 Coding CLI → Bootstrap → 目标项目最终状态的关键链路 |
| External Dependency / Provider Probe | not_applicable | 本功能不依赖第三方 API、远端环境或付费 Provider |
| Build / Package / Runtime | required | `py_compile` 新增脚本与现有脚本，CLI `--help`/实际临时项目运行成功 |
| Docs / Governance / Other | required | README、`.agents/README.md`、SKILL 增量规则、Change、CI paths/commands 一致；确认未压缩原规则 |

# Completion Audit

- [ ] upstream_re_read：重新读取本轮用户明确要求、根 `AGENTS.md`、Coding Bootstrap/Greenfield/Change/Review 规则。
- [ ] change_coverage：逐项核对无 AGENTS、已有 AGENTS、Skill 强制入口、自动安装、原文保护是否全部进入 Change 与实现。
- [ ] reverse_audit：从 `scripts/install.py` → Skill 同步 → `coding.py bootstrap` → `AGENTS.md`/`.gitignore` 结果，以及从目标 `AGENTS.md` → Coding/Review/Docs 路由反向核对。
- [ ] unresolved_cleared：所有 not_satisfied 清零，Required 层具备本轮新鲜证据。

# 任务

- [x] 恢复 `main`、根 `AGENTS.md`、Coding Skill、Bootstrap/Change/验证/Review 直接相关事实。
- [x] 建立 L3 Change 和专用分支。
- [ ] 为 Bootstrap 行为先增加失败测试/边界测试。
- [ ] 增加 AGENTS 初版模板与 managed block 模板。
- [ ] 在 `coding.py` 增加安全、幂等 `bootstrap` CLI。
- [ ] 增加根 `scripts/install.py` 安装/升级入口。
- [ ] 更新 Coding Skill，明确目标项目 Bootstrap 自检与权限边界。
- [ ] 更新 README 与 `.agents/README.md`，保留原有文档信息并增量增加安装/升级说明。
- [ ] 更新 GitHub Actions 覆盖 `scripts/install.py` 与新增测试。
- [ ] 执行本轮完整自包含测试、py_compile、CLI/临时项目 Golden Path。
- [ ] 执行 Completion Audit、Ready Check、独立 Review。
- [ ] 创建 PR、确认 CI、按仓库保护正常合并到 `main`。
- [ ] 确认 `main` 新鲜 CI 后独立归档本 Change。

# 验证

## 计划

- `python3 -m py_compile .agents/skills/coding/scripts/coding.py .agents/skills/coding/scripts/ready_check.py scripts/install.py`
- `python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- `python3 .agents/skills/coding/scripts/coding.py bootstrap --help`
- `python3 scripts/install.py --help`
- 使用临时目录覆盖：Greenfield、已有 AGENTS、已有 managed block、坏 marker、gitignore、重复执行、安装升级与非受管 `.agents` 内容保护。
- `python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- 尚未执行实现后验证。

# 文档影响

- `README.md`：增加正式一键安装/升级与 Bootstrap 使用说明，不删除现有手工安装、Coding/Review/Docs/L1-L3/Change/cache/CLI 等内容。
- `.agents/README.md`：增加目标项目 Overlay 与受管/非受管目录边界说明。
- `.agents/skills/coding/SKILL.md`：只增量增加 Bootstrap 自检/安装入口规则，不压缩现有规则。

# 交付

- Commit：建立目标项目 AGENTS Bootstrap 变更契约。
- PR：待创建。
- 发布：本仓库当前没有要求额外 Release；完成后以合并至 `main` 与主分支 CI 为准。
