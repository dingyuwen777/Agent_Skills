# Agent_Skills

`Agent_Skills` 是一组面向软件研发的通用 Agent Skills。它不规定某一种语言、框架、数据库或项目架构，而是让 AI / Coding Agent 在不同项目、不同研发阶段和不同技术栈中，先恢复当前真实事实，再按风险选择需求、实现、调试、测试、Review、文档、Figma、Git 和交付流程。

当前仓库实际存在的正式 Skill：

| Skill | 主要职责 | 正式入口 |
| --- | --- | --- |
| `coding` | Greenfield、仓库事实恢复、需求/设计、功能开发、Bug、重构、验证、CI、Git、Release 与交付 | [`.agents/skills/coding/SKILL.md`](.agents/skills/coding/SKILL.md) |
| `review` | 独立 Code Review、Findings、测试充分性审查和 re-review | [`.agents/skills/review/SKILL.md`](.agents/skills/review/SKILL.md) |
| `docs` | 技术文档事实同步、审查、编写、更新和可读性治理 | [`.agents/skills/docs/SKILL.md`](.agents/skills/docs/SKILL.md) |
| `figma` | Figma 设计事实、Canvas/Prototype、设计系统/可用性审查、修复、Ready 验收与 Design-to-Code 实施交接 | [`.agents/skills/figma/SKILL.md`](.agents/skills/figma/SKILL.md) |

这张表描述**当前仓库事实**，不是 Runtime/Release 的静态白名单。构建和分发会从：

```text
.agents/skills/*/SKILL.md
```

动态发现全部合法正式 Skill。以后新增 `security`、`testing`、`architecture` 等正式 Skill 时，不需要再修改 Runtime、安装器或 Release Workflow 的 Skill 名称列表。

最重要的边界是：

```text
Agent_Skills
→ 规定“怎样可靠工作”

目标项目 AGENTS.md / CONTRIBUTING / Contract / 代码 / 测试 / 文档 / Design Guide / 当前正式 Figma
→ 规定“这个项目具体是什么”
```

不要把本仓库根 `AGENTS.md` 复制到业务项目覆盖项目自己的规则。目标项目真正需要的是当前 Release 的正式 Skill、目标项目自己的 `AGENTS.md` Overlay，以及 Runtime 模式下的项目本地 MCP。

## 1. 安装 / 接入

### 1.1 推荐：最终团队用户只拿一个 binary

正式团队 Runtime Release 面向最终使用者只提供与当前操作系统匹配的 binary：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
SHA256SUMS
```

团队成员**不需要**：

```text
clone Agent_Skills
Python / pip / venv
install_runtime.py
install_runtime_target.py
用户级 / 全局 Runtime
Runtime Kit ZIP
```

Windows 示例：

```powershell
cd D:\work\MyProject
.\agent-skills-mcp-v<VERSION>-windows.exe
```

Linux / macOS 示例：

```bash
cd /work/MyProject
/path/to/agent-skills-mcp-v<VERSION>-linux
```

无参数运行默认安装/升级当前工作目录。也可以显式指定：

```text
agent-skills-mcp install --target <目标项目根目录> --json
```

Runtime binary 会在当前项目内完成：

```text
动态发现当前 Release 全部正式 Skill
→ 安装 Native Core / 运行资产
→ canonical Reference 只安装同名 Stub
→ 安装项目 .agents/runtime/agent-skills-mcp[.exe]
→ 创建/更新 AGENTS.md managed block
→ 增量更新 .gitignore
→ 建立 Codex / Cursor / Claude Code 项目级 MCP 配置
→ 写入 .agents/agent-skills-install.json ownership manifest
```

项目 Runtime 只属于当前项目，不污染其他项目。项目 `.agents/runtime/` 会被增量加入 `.gitignore`，避免把平台 binary 误提交到业务仓库。

完整最终用户说明：

[`docs/distribution/runtime-kit.md`](docs/distribution/runtime-kit.md)

完整安装、ownership、AGENTS 和 Runtime Contract：

- [`13_目标项目安装与AGENTS_Bootstrap.md`](.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md)
- [`14_本地MCP_Runtime分发与原文上下文加载.md`](.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md)

### 1.2 Full / source 安装：维护者与明确允许 Reference 明文的场景

从 `Agent_Skills` 源仓库或受控 Full Distribution Kit 执行：

```bash
python scripts/install.py --target <目标项目根目录>
```

Windows 示例：

```powershell
python scripts/install.py --target D:\work\MyProject
```

该模式会动态发现并完整复制当前版本全部正式 Skill，**包括 canonical `references/*.md` 明文**。它适合维护者、调试或明确允许规则正文分发的环境，不是“团队成员只拿 binary”的推荐路径。

安装器不会把本仓库根 `AGENTS.md`、`.agents/changes/` 或 `.agents/project-context.json` 复制到目标项目，也不会为了升级清理目标项目自己的 `.agents/changes/`、项目自有不同名 Skill 或其他 `.agents` 内容。

安装完成后会调用目标项目中刚安装的 Coding CLI：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

Bootstrap 负责建立目标项目自己的 Agent Skills 入口：

```text
目标项目已有规则
→ 保留原文
→ 仅在 managed block 中接入 Agent Skills
→ 后续任务先进入 Coding
→ Coding 再按任务加载 references / Review / Docs / Figma / 其他正式 Skill
```

目标项目没有 `AGENTS.md` 时会创建最小 Overlay；已有 `AGENTS.md` 时只增量维护：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

marker 外项目原文保持不变；marker 不完整、重复或顺序错误时安装器拒绝猜测性覆盖。

Full Distribution 说明：

[`docs/distribution/full-kit.md`](docs/distribution/full-kit.md)

### 1.3 项目自有 Skill 和宿主配置不会被整体接管

动态 Skill 发现解决的是“当前 Agent_Skills Release 有哪些正式 Skill”，不是“目标项目 `.agents/skills/` 下什么都可以覆盖”。

Runtime 项目安装使用：

```text
.agents/agent-skills-install.json
```

证明上一版本由 Agent_Skills 明确认领的 Skill。首次安装遇到未被 manifest 认领的同名 Skill 时会 fail closed；升级删除 Skill 也只允许删除旧 manifest 明确认领而新 Release 已移除的项。

项目中其他自有 Skill、AGENTS managed marker 外文本、其他 MCP server 和宿主配置字段保持。Codex 的项目 `.codex/config.toml` 仍受 Codex 自身 workspace trust 安全机制约束；Agent Skills 不绕过宿主 trust/approval。

## 2. 怎么用 Coding

普通研发任务可以直接描述目标，不需要记复杂命令。例如：

```text
使用 coding，基于当前仓库真实实现完成这个任务。
先恢复项目形态、研发阶段、实际语言/工具链和 L1-L3 风险；
只读取与任务直接相关的代码、Contract、Schema/Migration、配置、依赖、测试和文档；
按适用规则实现和验证，完成前进入 Review，最后只报告本轮新鲜证据支持的状态。
```

Coding 会按当前任务在 `references/` 中选择最少充分规则，不要求机械通读所有 Reference。Runtime 模式命中 Reference 时，项目里的同名文件只是 Stub；Agent 必须通过 `agent_skills_load_context` 取得并校验 canonical 原文后继续工作。

### Greenfield

空仓库、工程基线尚未建立或只做 Prototype / Feasibility 时，仍使用 Coding，但事实来源不同：

```text
用户目标 / 已确认决定 / 运行环境 / 硬约束
→ 区分已决定与待决定技术边界
→ 对真正影响长期结果的选择比较方案
→ 建立最小工程基线
→ build / test / package / run
→ Docs / Review / Delivery
```

Greenfield 不表示 Agent 可以自由猜技术栈；没有现成代码事实时，用户已确认决定和目标环境就是上游事实。

## 3. 怎么用 Review

显式 Code Review / Audit 可以写：

```text
使用 review-only 审查当前 PR/分支/实现。
先恢复 Review Target、上游要求、项目规则、真实工具链和影响边界；
独立重建需求，检查 diff、调用链和测试充分性，输出有证据的 Findings。
```

Review 默认只报告，不自动获得修改、提交或合并权限。需要修复生产实现时返回 Coding 完整流程，修复后再 re-review。

## 4. 怎么用 Docs

文档任务可以写：

```text
使用 docs 检查当前技术文档是否与真实代码、Contract、Schema/Migration、配置、测试和运行方式一致。
先界定 not_applicable / targeted / full 文档影响，再只读取受影响事实源和文档域。
```

`full` 表示完整覆盖受影响文档域，不是机械扫描仓库全部 Markdown。Docs 发现实现本身有问题时会返回 Coding，而不是修改文档去迎合错误实现。

## 4.1 怎么用 Figma

Figma 任务也不需要记住长检查清单。安装后可以直接描述目标：

```text
全面检查这个 Figma：<链接>
全面检查并修好这个 Figma：<链接>
对照当前仓库全面验收这个 Figma：<链接>
按这个 Figma 替换当前对应页面：<链接>
```

有目标实现仓库时，Coding 的任务路由会进入 `.agents/skills/figma/SKILL.md`。Figma 负责设计事实、Canvas/Section/Annotation、Prototype、真实系统能力映射、组件/业务逻辑复用审计和 `READY / READY_WITH_NOTES / NOT_READY`；用户要求 Figma-to-code 时必须先通过 `baseline-ready`，`NOT_READY` 不进入生产实现。达到可实施 Readiness 后，已确认设计事实交回 Coding 的前端/Design-to-Code 规则，继续按目标项目真实技术栈实现、测试、Review、CI、Git 与交付。

Figma 规则不把某个项目的 Vue/React、数据库、品牌、页面尺寸或业务字段当成通用标准；这些具体事实仍来自目标项目当前 Design Guide/Design System、代码、Contract、运行状态和正式 Figma。

## 5. Change、风险与完成门禁

Coding 的风险等级：

- `L1`：行为不变机械修改，或影响隔离的极小修复；
- `L2`：新功能、行为变化、重要 Bug、多文件修改、多人并行或需要正式追踪；
- `L3`：public API/ABI/CLI/格式、Schema/Migration、跨模块 Contract、架构、安全、部署恢复、重大依赖或不可逆数据行为。

需要 Coding 自带 Change 时使用当前 schema：

```text
coding-change/v1
```

默认 carrier：

```text
.agents/changes/
├── active/
└── archive/
```

目标项目已有能够承载 Requirement Traceability、Validation Matrix、Completion Audit 等语义的正式 RFC / ADR / Spec / OpenSpec / Issue 流程时，优先使用项目现有机制，不平行再造一套治理。

重要单元的基本关系是：

```text
上游需求/决定
→ Requirement Traceability
→ 当前 Change
→ Validation Matrix
→ 实现 / 测试 / 文档
→ Completion Audit
→ Independent Review
→ Ready / PR / CI / Delivery
```

CI 全绿不能替代需求完整性审计。

## 6. 本地可失效导航缓存

目标项目中的：

```text
.agents/project-context.json
```

是 Coding 生成的**本地可失效导航缓存**，只帮助定位规则、Manifest、锁文件、文档和其他事实入口，不是需求、架构或代码事实副本。

它应被目标项目忽略，不提交 Git。刷新入口：

```bash
python .agents/skills/coding/scripts/coding.py discover --root .
```

缓存命中也不表示源码没有变化；任何具体结论仍需回到当前代码、Contract、Schema/Migration、测试和实际运行结果确认。

## 7. 两种分发方式

### Runtime Binary：团队推荐

适合：

- 最终使用者不访问 Agent_Skills 源仓库；
- 不希望 canonical Reference Markdown 直接落盘；
- 希望一个 binary 在目标项目根完成安装/升级；
- 需要 Codex / Cursor / Claude Code 共用当前项目 Runtime。

正式团队 Release 资产：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
SHA256SUMS
```

最终用户说明：

[`docs/distribution/runtime-kit.md`](docs/distribution/runtime-kit.md)

Runtime 源码、构建和维护说明：

[`runtime/README.md`](runtime/README.md)

### Full Distribution Kit：受控兼容分发

适合明确允许使用者直接获得完整 Markdown Skill / canonical Reference 的场景。

维护者构建：

```bash
python scripts/build_full_distribution.py --output-dir dist --json
```

用户说明：

[`docs/distribution/full-kit.md`](docs/distribution/full-kit.md)

由于 Full Kit 包含 canonical Reference 明文，**当前团队 Runtime 正式 Release 不默认同时发布 Full Kit**。如果未来要对外提供 Full Kit，应作为独立授权和安全决策处理。

## 8. 版本与 Release

根 [`VERSION`](VERSION) 是正式产品版本的唯一事实源。

正式发布不会因为 `VERSION` push 自动触发。维护者从 GitHub Actions 手工运行 `.github/workflows/release.yml`：

```text
Actions
→ Release
→ Run workflow
→ Branch: main
→ Tag: v<VERSION>，例如 v1.0.0
```

Workflow 校验 tag 与 `VERSION` 一致后，在 Linux / Windows / macOS 对应 Runner 上重新构建平台 onefile，并实际执行：

```text
status/self-test
→ 真实 stdio MCP smoke
→ binary 安装真实临时项目
→ 项目内 Runtime MCP smoke
```

三个平台候选都成功后，最终 Publish Job 才创建 tag / GitHub Release，并发布三平台 binary + `SHA256SUMS`。同名历史 tag / Release 不覆盖、不移动。

维护者完整发布流程：

[`docs/maintainers/releasing.md`](docs/maintainers/releasing.md)

版本用户可观察变化：

[`CHANGELOG.md`](CHANGELOG.md)

## 9. 仓库结构

```text
Agent_Skills/
├── README.md                    # 仓库总入口
├── AGENTS.md                    # 维护本仓库时的上位规则
├── CHANGELOG.md                 # 正式版本用户可观察变化
├── VERSION                      # 产品版本事实源
├── docs/
│   ├── distribution/
│   │   ├── full-kit.md          # Full 明文兼容分发说明
│   │   └── runtime-kit.md       # Runtime binary 最终用户说明（保留路径兼容）
│   └── maintainers/
│       └── releasing.md         # Release 维护者流程
├── .agents/
│   ├── README.md                # Agent 目录导航
│   ├── skills/
│   │   ├── coding/
│   │   ├── review/
│   │   ├── docs/
│   │   ├── figma/
│   │   └── <未来其他正式 Skill>/
│   └── changes/
├── runtime/
│   ├── README.md                # Runtime 源码/构建维护说明
│   ├── agent_skills_runtime/
│   │   ├── skill_catalog.py
│   │   ├── project_payload.py
│   │   ├── project_installer.py
│   │   └── ...
│   └── requirements*.txt
├── scripts/                     # 源安装、构建、验证脚本
└── .github/workflows/
    ├── skill-tests.yml
    └── release.yml
```

当前 `scripts/` 只有少量稳定维护入口，因此保持平铺，不为了视觉分类额外增加无价值目录层级。Skill 自身的 `SKILL.md / references / assets / scripts / tests` 继续留在各自 Skill 内，保持自包含。

## 10. 常用入口

最终团队用户：

```text
# 在目标项目根运行当前平台 binary
agent-skills-mcp[.exe]
```

维护者 / Full/source：

```bash
# 完整 Markdown 安装 / 升级当前动态正式 Skill
python scripts/install.py --target <目标项目根目录>

# 目标项目 Bootstrap
python .agents/skills/coding/scripts/coding.py bootstrap --root .

# 项目发现缓存
python .agents/skills/coding/scripts/coding.py discover --root .

# Coding 状态 / Change
python .agents/skills/coding/scripts/coding.py status --root .
python .agents/skills/coding/scripts/coding.py new-change --help

# 构建当前平台 Runtime binary
python scripts/build_runtime.py --output-dir dist --json

# Ready Gate
python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

## 11. 进一步阅读

- [`.agents` 目录说明](.agents/README.md)
- [Coding 使用说明](.agents/skills/coding/README.md)
- [Coding 正式规则](.agents/skills/coding/SKILL.md)
- [Review 使用说明](.agents/skills/review/README.md)
- [Docs 使用说明](.agents/skills/docs/README.md)
- [Figma 使用说明](.agents/skills/figma/README.md)
- [Figma 正式规则](.agents/skills/figma/SKILL.md)
- [Runtime binary 最终用户说明](docs/distribution/runtime-kit.md)
- [Full 明文兼容分发说明](docs/distribution/full-kit.md)
- [Runtime 维护说明](runtime/README.md)
- [Release 维护说明](docs/maintainers/releasing.md)
