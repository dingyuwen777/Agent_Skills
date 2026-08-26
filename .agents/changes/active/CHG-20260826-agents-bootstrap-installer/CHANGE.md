---
schema: coding-change/v1
id: "CHG-20260826-agents-bootstrap-installer"
title: "目标项目 AGENTS Bootstrap 与 Agent Skills 安装升级入口"
level: L3
status: ready_for_review
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
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/tests"
  - "scripts/install.py"
  - "README.md"
  - ".agents/README.md"
  - "AGENTS.md"
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

- [x] 提供一个从 Agent_Skills 仓库执行的安装/升级脚本，可把 `coding`、`review`、`docs` 三个 Skill 同步到任意目标项目的 `.agents/skills/`，且不复制 Agent_Skills 自身 `.agents/changes/`、本地缓存或其他仓库维护数据。
- [x] `coding.py` 增加 `bootstrap --root <target>` 入口，用于创建或增量补充目标项目根 `AGENTS.md`，并确保 `.agents/project-context.json` 被目标项目忽略。
- [x] 目标项目没有 `AGENTS.md` 时，Bootstrap 创建一个可维护的项目 Overlay 初版；初版包含 Agent Skills 统一入口、当前真实事实入口导航和维护说明，但不根据 Manifest 名称猜测框架、数据库、架构或业务事实。
- [x] 目标项目已经有 `AGENTS.md` 时，Bootstrap 保留原文，仅增加或更新 Agent Skills 自管区；不得整体重写、压缩、重排或删除用户已有规则。
- [x] Agent Skills 自管区使用稳定 managed markers，重复执行不会重复插入；升级时只替换 managed markers 内的内容，marker 外原文保持不变。
- [x] 已有 `AGENTS.md` 出现不完整/冲突的 managed marker 时，工具拒绝猜测性覆盖并给出明确错误，而不是损坏原文。
- [x] Bootstrap 对 `.gitignore` 的处理同样幂等：没有 `.agents/project-context.json` 时补充，已经存在等价忽略项时不重复；不得清理或重写其他 ignore 规则。
- [x] Coding 正式规则新增目标项目安装/Bootstrap 路由：有写权限且任务要求安装/初始化时，缺失 `AGENTS.md` 可创建；已有文件只能增量接入；普通只读分析/Review 不因发现缺失而越权创建文件；由 Coding Agent 执行初始化时，再基于真实仓库证据增量补充项目自有 Overlay 缺口。
- [x] 根 README 与 `.agents/README.md` 说明首次安装、重复升级、managed block、项目 Overlay、本地缓存和“确定性 Bootstrap + Agent 语义补全”的边界。
- [x] CI 对新增安装脚本和 Bootstrap 测试实际生效，`scripts/**` 已进入 workflow paths，`scripts/install.py` 进入 `py_compile`，两个公开 CLI 进入永久 smoke。
- [x] 自包含测试覆盖空仓库、无 `AGENTS.md`、已有 `AGENTS.md`、重复 Bootstrap、managed block 升级、损坏 marker、`.gitignore` 幂等、非 Python/多语言项目、不复制 Change/缓存、安装中途回滚、Bootstrap 失败回滚和仓库派生文本 Markdown 结构转义等关键边界。

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
- 现有 `SKILL.md` 与 references 01–11 的触发条件、例外、失败处理、停止条件、验证责任、安全和兼容边界不得因为本次接入能力而被概括、降级或丢失；本次使用新增 reference 13 承载新规则。

# 关键决策

## 方案比较

### 方案 A：仅要求用户手工复制 `.agents/skills/` 并手工写 `AGENTS.md`

优点：实现最少。

缺点：首次接入步骤依赖人工记忆；不同项目的入口文本容易漂移；升级时无法稳定维护；无法保证已有 `AGENTS.md` 的增量接入和幂等性。

### 方案 B：只让大模型自由读取仓库后生成/重写 `AGENTS.md`

优点：能理解项目语义。

缺点：对已有规则的保护不可确定；重复执行容易漂移；首次运行前 Agent 甚至可能不知道应读取 `.agents/skills/coding/SKILL.md`；不适合作为安装 Contract。

### 方案 C：确定性 Bootstrap + Skill 语义补全（采用）

由脚本负责可机械证明的安装、managed block、`.gitignore`、事实入口导航和幂等更新；由 Coding Skill 在“当前任务本身就是安装/初始化且已有项目规则写权限”时，继续读取真实仓库事实并增量补充项目自有 Overlay 的缺失语义。脚本不猜项目架构，Skill 不承担第一次安装必须成功的文件同步职责。

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
- 初始化扫描实际发现的高价值事实入口；
- 明确禁止把自动发现的 Manifest 名称直接解释成框架、数据库、架构事实。

确定性脚本只写结构、已知 Skill 路径和真实事实入口导航，不自动生成未经语义确认的项目架构描述。项目名和事实入口路径属于仓库派生文本，写入 Markdown 前必须转成安全单行显示，避免换行、反引号、HTML 边界等改变 `AGENTS.md` 的指令结构。

## Agent 语义补全

如果用户只是手工执行 `scripts/install.py`，确定性初版即为正确结果；普通 Python 脚本不能伪装成已经理解项目架构。

如果当前安装/初始化任务由 Coding Agent 执行且用户已授权修改项目规则，则 Bootstrap 后还必须：

- 重新读取当前 `AGENTS.md`；
- 只读取长期研发导航所需的最少充分真实事实源；
- 能从当前仓库直接确认的长期项目事实，只在 managed block 外的项目自有区域增量补充；
- 已有清楚内容不重写、不为了统一风格换措辞；
- 事实源冲突时先核实，不静默选择一个猜成正确；
- 后续安装器升级只更新受管 Skill 和 managed block，不覆盖项目自有语义。

## 安装升级

根 `scripts/install.py` 只同步：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

目标 `.agents/skills/` 中这三个受管 Skill 可按源仓当前版本更新；目标项目其他 `.agents/` 内容不删除、不清理。

复制采用目标 `.agents` 下的暂存目录，完整暂存后才逐 Skill 切换；任一 Skill 切换失败时恢复当前项和此前项；三个 Skill 已切换但 Bootstrap 失败时恢复安装前的三个受管 Skill。复制完成后调用目标项目中已安装的 Coding CLI Bootstrap。

## Migration / 兼容

- 这是新增入口，不删除现有手工复制方式；现有用户仍可继续按 README 的手工方式安装。
- 已有目标项目 `AGENTS.md` 不需要迁移全文，只由 managed block 增量接入。
- 已有 `.agents/skills/` 在安装器再次执行时升级受管三个 Skill；其他项目自有目录不受影响。
- 不修改 Change schema 或历史 archived Change。

## 回滚

- 回滚安装器/Bootstrap 代码不会自动删除任何目标项目 `AGENTS.md` 内容；目标项目中的 managed block 是普通文本，可由项目 Owner 显式删除。
- 安装器在切换受管 Skill 前保留旧目录；切换中途失败和 Bootstrap 失败均恢复本轮受管 Skill 变化，并由真实临时文件系统测试验证。
- Bootstrap 对单文件使用同目录临时文件 + 原子替换；所有可预先发现的 `AGENTS.md` marker/UTF-8 与 `.gitignore` UTF-8 错误在写入前完成验证。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 没有 `AGENTS.md` 时根据目标项目接入需要创建初版 | user:current-request | satisfied | `assets/AGENTS.template.md` + `bootstrap_project()`；`test_bootstrap_creates_agents_for_greenfield_without_inventing_stack`、`test_polyglot_manifests_are_listed_without_affirmative_framework_inference`；Runner 32955916054 通过 |
| R2 | 已有 `AGENTS.md` 时在原文基础上补充而不是覆盖 | user:current-request | satisfied | managed marker 增量算法；CRLF/前后字节保留、managed block 更新、幂等与坏 marker 回归测试；Runner 32955916054 通过 |
| R3 | 创建或修改后的 `AGENTS.md` 必须明确研发过程使用 `.agents/skills/coding/SKILL.md`，并由 Coding 路由 Review/Docs | user:current-request | satisfied | `.agents/skills/coding/assets/AGENTS.managed.md` 明确 Coding/reference/Review/Docs 路由；安装/升级另指向 reference 13 |
| R4 | 接入流程可以由代码/Skill 自动完成，而不是每个项目手工维护 | user:current-request | satisfied | `scripts/install.py --target` + `coding.py bootstrap`；真实文件系统首次安装/升级/回滚/Bootstrap 失败链测试和 CLI smoke 通过 |
| R5 | 不得因实现本功能而过度总结、压缩或丢失现有 Skill/reference 原文规则信息 | user:preserve-original-detail | satisfied | PR #3 changed-files/compare 证明 `.agents/skills/coding/SKILL.md` 与 references 01–11 未被修改；新增规则独立放在 reference 13；独立 Review #5029100108 无阻塞 Finding |
| R6 | 所有 Agent_Skills 仓库开发、验证、Git 和交付遵守当前根 `AGENTS.md` | AGENTS.md | satisfied | 从最新 main 建专用分支与 L3 Change；中文提交；未绕过 PR/CI/Ready；Runner 32955916054 的 compile/CLI smoke/59 tests 通过，Ready 在 `in_progress` 时按设计阻塞；独立 Review 已完成 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | managed block、AGENTS 创建/更新、marker 错误、gitignore、安装目录同步、事实入口转义等由 59 个完整自包含测试中的目标测试覆盖；Runner 32955916054 `Ran 59 tests ... OK` |
| 接口 / Contract | required | `coding.py bootstrap` 与 `scripts/install.py --target` 公开 CLI 已进入永久 CI smoke；managed marker 与生成文件 Contract 有直接断言；Runner 32955916054 smoke 成功 |
| 集成 / Persistence / Runtime Dependency | required | 使用真实临时文件系统执行 copy/rename/backup/rollback/subprocess Bootstrap/AGENTS/.gitignore，不以 Mock 冒充文件系统；安装中途失败和 Bootstrap 失败均有回归测试 |
| 用户 / Workflow Acceptance | required | `InstallerTest` 从源 Agent_Skills 到临时目标项目执行真实安装链，检查三个 Skill、AGENTS、gitignore、自有 `.agents` 保留和重复升级结果 |
| 跨组件 Golden Path | required | `scripts/install.py` → 复制后的目标 `coding.py` 子进程 → `bootstrap --json` → 最终 AGENTS/.gitignore 的真实链路由首次安装与升级测试覆盖 |
| External Dependency / Provider Probe | not_applicable | 本功能不依赖第三方 API、远端环境、付费 Provider 或真实外部服务；GitHub Runner 仅用于当前仓库 CI 证据，不属于产品外部依赖行为 |
| Build / Package / Runtime | required | Runner 32955916054：Python 3.12.3；`py_compile coding.py ready_check.py scripts/install.py` 成功；两个 CLI `--help` smoke 成功 |
| Docs / Governance / Other | required | 根 README、`.agents/README.md`、根维护 AGENTS、reference 13、assets、CI paths/compile/smoke 与实现一致；`test_migration_cleanliness` 锁住 ref12 不回归/ref13 live/通用规则与五项硬规则；独立 Review 确认未压缩旧规则 |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户明确要求、根 `AGENTS.md`、Coding 的 Greenfield/Change/通用验证/设计实施/完成定义/两阶段 Review 规则与 Review Skill，并以这些上游事实独立重建完成定义。
- [x] change_coverage：已逐项核对无 AGENTS、已有 AGENTS、Skill 强制入口、自动安装/升级、原文保护、语义补全、CI/回滚和“不丢失原规则”要求；未发现仍漏在 Change 外的用户要求。
- [x] reverse_audit：已从 `scripts/install.py` → 暂存/切换/回滚 → 已复制 `coding.py bootstrap` → `AGENTS.md`/`.gitignore`，以及从目标 `AGENTS.md` → Coding/reference → Review/Docs 做双向核对；补齐 CLI smoke、回滚和 Markdown 结构转义缺口。
- [x] unresolved_cleared：Requirement Traceability 已无 `not_satisfied`；所有 required 验证层已有本轮证据；外部依赖层有明确不适用依据。

# 任务

- [x] 调查当前实现和事实源；确认 `main` 基线、根 `AGENTS.md`、Coding/Review 直接相关规则、现有 CLI、测试与 CI。
- [x] 建立四维任务路由：通用 Developer Tool / Repository Bootstrap；Feature/Contract；Python 工具链；L3。
- [x] 建立 L3 Change 和专用分支。
- [x] 为 Bootstrap 行为增加失败/边界测试，并经过第一轮真实 CI Red/修正。
- [x] 增加 AGENTS 初版模板与 managed block 模板。
- [x] 在 `coding.py` 增加安全、幂等 `bootstrap` CLI。
- [x] 增加根 `scripts/install.py` 安装/升级入口。
- [x] 使用独立 reference 13 固化目标项目安装、Bootstrap 与 Coding Agent 语义补全规则，不重写旧 reference。
- [x] 更新 README 与 `.agents/README.md`，保留原有文档信息并增量增加安装/升级说明。
- [x] 更新 GitHub Actions 覆盖 `scripts/**`、`scripts/install.py` 编译与公开 CLI smoke。
- [x] 增加真实文件系统安装中途回滚、Bootstrap 失败回滚和仓库派生 Markdown 转义测试。
- [x] 执行本轮完整自包含测试、py_compile、CLI smoke 和临时项目安装 Golden Path。
- [x] 执行 Requirement A1/A2、Completion Audit 与独立 Review；Review #5029100108 当前无阻塞 Finding。
- [ ] PR #3 从 Draft 转为 Ready，并取得 `ready_for_review` Change 下的全绿 CI。
- [ ] 按仓库保护正常合并到 `main`，确认 main 新鲜 CI。
- [ ] 在实现合并与 main CI 成功后，通过独立归档 PR 将本 Change 移至 archive 并标记 `done`。

# 验证

## 计划

- `python3 -m py_compile .agents/skills/coding/scripts/coding.py .agents/skills/coding/scripts/ready_check.py scripts/install.py`
- `python3 .agents/skills/coding/scripts/coding.py bootstrap --help`
- `python3 scripts/install.py --help`
- `python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- 使用真实临时目录覆盖：Greenfield、已有 AGENTS、已有 managed block、坏 marker、LF/CRLF、gitignore、重复执行、多语言事实入口、安装升级、非受管 `.agents` 内容保护、切换中途回滚、Bootstrap 失败回滚和仓库派生文本结构转义。
- `python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- GitHub Actions `Skill Tests` run `32954008175`：第一轮 `py_compile` 成功；单元测试因测试自身错误使用 `assertNotIn("FastAPI")` 失败。实现实际保留的是“不能单凭文件名推出 React/FastAPI/PostgreSQL”的安全规则；已修正测试，不删除该规则。
- 后续 Review 发现并修复安装器多 Skill 部分切换回滚缺口、永久 CLI smoke 缺口、Bootstrap 失败恢复测试缺口、reference 测试命名失真、Coding Agent 语义补全规则缺口和仓库派生文本进入 AGENTS Markdown 的结构注入风险。
- GitHub Actions `Skill Tests` run `32955916054`，head `68bf6323be814e768c5bb41726b7aaa2897ba366`：Ubuntu 24.04.4 / Python 3.12.3；`py_compile` 成功；`coding.py bootstrap --help` 与 `scripts/install.py --help` 成功；完整自包含测试 `Ran 59 tests in 0.954s`、`OK`。当时唯一失败是 Active Change 状态仍为 `in_progress`，Ready Check 按设计返回 `状态必须为 ready_for_review`，证明门禁未被绕过。
- PR #3 独立 Review `5029100108`：A1/A2 与代码质量复核完成，当前无阻塞 Finding；Review 中发现的问题均在当前实现中修复并由回归测试覆盖。

# 文档影响

- `README.md`：增量增加正式一键安装/升级、Bootstrap、managed block、手工安装兼容和 CLI 说明；原有 Coding/Review/Docs、Greenfield、L1-L3、Change、cache、五项硬规则与维护原则保留。
- `.agents/README.md`：增量增加目标项目 Overlay、首次接入/升级和受管/非受管目录边界；明确 Agent Skills Bootstrap 与 Greenfield 工程 Bootstrap 是不同层。
- `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md`：新增正式安装/升级/Overlay 规则以及 Coding Agent 语义补全第二阶段；不重写 references 01–11。
- `.agents/skills/coding/assets/AGENTS.managed.md` / `AGENTS.template.md`：新增目标项目受管入口与初版 Overlay 模板。
- `AGENTS.md`：只增量补充 Agent_Skills 本仓库对安装器/Bootstrap 的维护与测试门禁，原有通用核心、五项硬规则、Change/Git/交付规则保留。

# 交付

- Branch：`feature/agents-bootstrap-installer`。
- PR：#3 `增加目标项目 AGENTS Bootstrap 与一键安装升级`，当前 Draft，等待本次 `ready_for_review` Change 更新后的全绿 CI 后转为 Ready。
- 独立 Review：#5029100108，无当前阻塞 Finding。
- Merge：尚未执行，不绕过 CI/PR/Branch Protection。
- Change Archive：必须在实现合并到 `main` 且 main 新鲜 CI 成功后，通过独立归档 PR 完成。
- Release：本仓库当前没有要求额外 Release；本任务以合并至 `main`、主分支 CI 与 Change 归档闭环为完成标准。
