# Agent_Skills

`Agent_Skills` 是一组面向软件研发的通用 Agent Skills。它不规定某一种语言、框架、数据库或项目架构，而是让 AI / Coding Agent 在不同项目、不同研发阶段和不同技术栈中，先恢复当前真实事实，再按风险选择需求、实现、调试、测试、Review、文档、Git 和交付流程。

当前正式 Skill：

| Skill | 主要职责 | 正式入口 |
| --- | --- | --- |
| `coding` | Greenfield、仓库事实恢复、需求/设计、功能开发、Bug、重构、验证、CI、Git、Release 与交付 | [`.agents/skills/coding/SKILL.md`](.agents/skills/coding/SKILL.md) |
| `review` | 独立 Code Review、Findings、测试充分性审查和 re-review | [`.agents/skills/review/SKILL.md`](.agents/skills/review/SKILL.md) |
| `docs` | 技术文档事实同步、审查、编写、更新和可读性治理 | [`.agents/skills/docs/SKILL.md`](.agents/skills/docs/SKILL.md) |

最重要的边界是：

```text
Agent_Skills
→ 规定“怎样可靠工作”

目标项目 AGENTS.md / CONTRIBUTING / Contract / 代码 / 测试 / 文档
→ 规定“这个项目具体是什么”
```

不要把本仓库根 `AGENTS.md` 复制到业务项目覆盖项目自己的规则。目标项目真正需要安装的是 `.agents/skills/` 下的 Skill，并通过目标项目自己的 `AGENTS.md` 建立入口。

## 1. 安装 / 接入

### 1.1 推荐：一键安装 / 升级

从 `Agent_Skills` 源仓库执行：

```bash
python scripts/install.py --target <目标项目根目录>
```

Windows 示例：

```powershell
python scripts/install.py --target D:\work\MyProject
```

安装器只管理：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

它不会把本仓库根 `AGENTS.md`、`.agents/changes/` 或 `.agents/project-context.json` 复制到目标项目，也不会删除目标项目自己的 `.agents/changes/`、自有 Skill 或其他 `.agents` 内容。

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
→ Coding 再按任务加载 references / Review / Docs
```

目标项目没有 `AGENTS.md` 时会创建最小 Overlay；已有 `AGENTS.md` 时只增量维护下面的受管区：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

marker 外项目原文保持不变；marker 不完整、重复或顺序错误时安装器拒绝猜测性覆盖。

安装、升级和 Bootstrap 的完整规则见：

[`13_目标项目安装与AGENTS_Bootstrap.md`](.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md)

### 1.2 手工安装

仍可以直接复制：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

复制后建议在目标项目执行一次：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

不同宿主是否自动发现 Skill 取决于宿主当前能力；如果宿主要求显式注册 Skill，应按该宿主当前机制配置。无论宿主怎样加载，项目事实仍来自目标项目当前仓库。

## 2. 怎么用 Coding

普通研发任务可以直接描述目标，不需要记复杂命令。例如：

```text
使用 coding，基于当前仓库真实实现完成这个任务。
先恢复项目形态、研发阶段、实际语言/工具链和 L1-L3 风险；
只读取与任务直接相关的代码、Contract、Schema/Migration、配置、依赖、测试和文档；
按适用规则实现和验证，完成前进入 Review，最后只报告本轮新鲜证据支持的状态。
```

Coding 会按当前任务在 `references/` 中选择最少充分规则，不要求机械通读所有 reference。

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

## 7. 两种正式分发方式

### Full Distribution Kit

适合直接分发三个完整 Markdown Skill，不需要本地 MCP Runtime 的场景。

正式用户说明：

[`docs/distribution/full-kit.md`](docs/distribution/full-kit.md)

正式 Release 资产：

```text
agent-skills-full-kit-v<VERSION>.zip
```

解压后直接运行 Kit 内的：

```bash
python scripts/install.py --target <目标项目根目录>
```

### Runtime Distribution Kit

适合希望目标项目只保留 Native Core `SKILL.md` + Reference Stub，而详细 canonical Reference 通过本地 MCP 在运行时加载的场景。

正式用户说明：

[`docs/distribution/runtime-kit.md`](docs/distribution/runtime-kit.md)

三个正式平台资产：

```text
agent-skills-mcp-runtime-kit-v<VERSION>-linux.zip
agent-skills-mcp-runtime-kit-v<VERSION>-windows.zip
agent-skills-mcp-runtime-kit-v<VERSION>-macos.zip
```

Runtime 源码、构建原理和维护者本地调试说明继续放在：

[`runtime/README.md`](runtime/README.md)

这两份文档职责不同：`runtime/README.md` 面向维护 Runtime 源码的人；`docs/distribution/runtime-kit.md` 面向拿到 Release Kit 后安装使用的人。

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

Workflow 校验 tag 与 `VERSION` 一致后，重新构建 Full Kit 和 Linux / Windows / macOS Runtime Kit，生成 `SHA256SUMS`，最后自动创建输入 tag 和 GitHub Release。同名历史 tag / Release 不覆盖、不移动。

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
│   │   ├── full-kit.md          # Full Kit 最终用户说明
│   │   └── runtime-kit.md       # Runtime Kit 最终用户说明
│   └── maintainers/
│       └── releasing.md         # Release 维护者流程
├── .agents/
│   ├── README.md                # Agent 目录导航
│   ├── skills/
│   │   ├── coding/
│   │   ├── review/
│   │   └── docs/
│   └── changes/
├── runtime/
│   ├── README.md                # Runtime 源码/构建维护说明
│   ├── agent_skills_runtime/
│   └── requirements*.txt
├── scripts/                     # 稳定公开安装/构建/验证脚本
└── .github/workflows/
    ├── skill-tests.yml
    └── release.yml
```

当前 `scripts/` 只有少量稳定公开入口，因此保持平铺，不为了视觉分类额外增加无价值目录层级。Skill 自身的 `SKILL.md / references / assets / scripts / tests` 也继续留在各自 Skill 内，保持自包含。

## 10. 常用入口

```bash
# 安装 / 升级三个 Skill
python scripts/install.py --target <目标项目根目录>

# 目标项目 Bootstrap
python .agents/skills/coding/scripts/coding.py bootstrap --root .

# 项目发现缓存
python .agents/skills/coding/scripts/coding.py discover --root .

# Coding 状态 / Change
python .agents/skills/coding/scripts/coding.py status --root .
python .agents/skills/coding/scripts/coding.py new-change --help

# Ready Gate
python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

## 11. 进一步阅读

- [`.agents` 目录说明](.agents/README.md)
- [Coding 使用说明](.agents/skills/coding/README.md)
- [Coding 正式规则](.agents/skills/coding/SKILL.md)
- [Review 使用说明](.agents/skills/review/README.md)
- [Docs 使用说明](.agents/skills/docs/README.md)
- [Full Kit 用户说明](docs/distribution/full-kit.md)
- [Runtime Kit 用户说明](docs/distribution/runtime-kit.md)
- [Runtime 维护说明](runtime/README.md)
- [Release 维护说明](docs/maintainers/releasing.md)
