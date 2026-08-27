# Agent_Skills

`Agent_Skills` 是一组面向软件研发的通用 Agent Skills。目标不是规定某一种语言、框架或架构，而是让 AI/Coding Agent 在不同项目、不同研发阶段和不同技术栈中，都先恢复真实项目事实，再按风险选择需求、实现、调试、测试、Review、文档、Git 和交付流程。

当前包含：

| Skill | 作用 |
| --- | --- |
| `coding` | Greenfield/仓库事实恢复、需求/设计、功能开发、Bug 修复、重构、验证、CI、Git、Release 与交付 |
| `review` | 独立 Code Review、Findings、测试充分性审查和 re-review |
| `docs` | 技术文档事实同步、审查、编写、更新和可读性治理 |

## 1. 适用范围

Coding 不预设项目一定是 Python、Web、后端或数据库应用。它按当前仓库事实识别项目形态和真实工具链，也支持尚未建立完整工程事实的 Greenfield 项目，可用于：

- Library / SDK；
- CLI / Developer Tool；
- Service / Backend / API；
- Frontend / Web UI；
- Full-stack Application；
- Mobile / Desktop；
- Data / Batch / ETL / ML；
- Embedded / Systems；
- Infra / IaC / Build / Release Tooling；
- Monorepo / Polyglot；
- Greenfield / Repository Bootstrap / Prototype / Feasibility；
- Documentation / Configuration / Migration-only 任务。

语言 profile 已覆盖常见 Python、JavaScript/TypeScript、Go、Rust、Java/Kotlin、.NET、C/C++、Swift、Dart/Flutter、PHP、Ruby、Elixir、Container/IaC；未列出的语言继续使用同一套 Runtime/Compiler → Manifest → Lock → Build/Test → Package/Runtime → CI/Release 事实发现算法。

## 2. 最重要的边界：通用 Skill ≠ 项目事实

推荐结构：

```text
目标项目/
├── AGENTS.md / CONTRIBUTING / 项目自己的规则
└── .agents/
    └── skills/
        ├── coding/
        ├── review/
        └── docs/
```

项目自己的 `AGENTS.md` 是 Overlay：它可以规定实际语言、版本、架构、数据库/持久化、目录、业务 Contract、CI、部署方式和项目特殊约束。

`Agent_Skills` 的通用规则负责：

```text
先恢复项目事实 / Greenfield 约束
→ 判断项目形态 / 研发阶段 / 真实工具链 / L1-L3 风险
→ 选择最少但充分流程
→ 最小兼容实现
→ 与风险匹配的验证
→ Completion Audit / Review
→ 只交付新鲜证据支持的结论
```

不要把本仓库根 `AGENTS.md` 复制到目标项目覆盖其已有项目规则；根 `AGENTS.md` 只用于维护 Agent_Skills 自身。需要分发的是 `.agents/skills/` 下的 Skill 内容。

## 3. 安装 / 接入

### 3.1 推荐：一键安装 / 升级

从 `Agent_Skills` 源仓库执行：

```bash
python scripts/install.py --target <目标项目根目录>
```

例如：

```bash
python scripts/install.py --target D:\work\MyProject
```

安装器只管理：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

它不会把本仓库根 `AGENTS.md`、`.agents/changes/` 或 `project-context.json` 复制到目标项目，也不会删除目标项目已有 `.agents/changes/`、项目自有 Skill 或其他 `.agents` 内容。

三个受管 Skill 会先复制到目标项目 `.agents` 下的暂存区，完整暂存后再切换。切换完成后，安装器调用目标项目中刚安装的 Coding CLI：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

Bootstrap 负责建立目标项目自己的 `AGENTS.md` Overlay：

- 目标项目没有 `AGENTS.md`：根据当前实际可见的项目事实入口创建初版；
- 已有 `AGENTS.md`：保留原文，只追加 Agent Skills managed block；
- 已有完整 managed block：只更新 managed block，marker 外原文字节保持不变；
- managed marker 缺失、重复或顺序错误：拒绝猜测性覆盖，原文件保持不变；
- `.gitignore` 中没有 `.agents/project-context.json`：增量补充；已有明确等价规则时不重复写入。

managed block 使用固定边界：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

managed block 会明确要求后续研发任务先读取项目规则，再必须读取 `.agents/skills/coding/SKILL.md`；Coding 按实际任务继续路由 `references/`、Review 和 Docs。安装/升级、创建/补充项目 `AGENTS.md` 或修复 managed block 时，还要求读取 `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md`。

Bootstrap 只把扫描结果作为事实入口导航，不根据 `package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod` 等文件名猜测 React、FastAPI、PostgreSQL 或其他具体技术路线。项目语义仍由 Coding 在后续任务中依据当前真实文件、调用链、Contract、Schema/Migration、测试和运行结果确认。

同一个安装命令可以重复执行用于升级：受管三个 Skill 更新到当前 Agent_Skills 版本，目标项目 `AGENTS.md` 的 managed block 同步更新，项目自己维护的 marker 外内容保留。

### 3.2 手工安装仍然支持

最直接的方式仍然可以把需要的 Skill 复制或同步到目标仓库：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

三个 Skill 可以一起使用；Coding 会在适用时路由 Review 和 Docs。也可以只安装单个 Skill，但功能边界会相应降级：

- 没有 Review Skill：Coding 继续执行自身完成前 Review；
- 没有 Docs Skill：Coding 继续执行自身文档影响判断与同步规则；
- Review 单独使用时，如果同仓存在 Coding，Review 会先读取 Coding 作为研发规范源；不存在时则只依据项目本地规则和 Review 方法。

如果手工复制三个 Skill，建议复制完成后在目标项目执行：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

这样可以建立或增量补充项目 `AGENTS.md`，避免只有 `.agents/skills/` 但新的 Coding Agent 不知道应该从哪里进入通用 Skill。

不要假设所有宿主工具都自动扫描同一路径；宿主若要求显式注册 Skill，应按该宿主当前官方能力把这个目录配置为可读 Skill。无论宿主如何加载，项目事实仍来自目标仓库本身。

目标项目还应忽略本地缓存：

```gitignore
.agents/project-context.json
```

`bootstrap` 会补充这一条，但不会创建 `project-context.json`；缓存仍只在实际执行 `discover` 且具备写权限时创建。

## 4. 怎么用 Coding

普通研发请求可以直接写：

```text
使用 coding，基于当前仓库真实实现完成这个任务。
先读取适用项目规则，恢复项目形态、研发阶段、实际语言/工具链和 L1-L3 风险；
只读取与任务直接相关的代码、Contract、Schema/Migration、配置、依赖、测试和文档；
按适用的 TDD/根因调试/Validation Matrix/Completion Audit/Review/Git 门禁执行，最后只用本轮新鲜证据报告完成状态。
```

### Greenfield 项目

仓库还没有代码/Manifest/CI 时：

```text
使用 coding 按 Greenfield / Repository Bootstrap 模式工作。
先确认目标、硬约束、成功标准、非目标和必须保持不变；
对真正影响接口、数据、兼容、部署和长期维护的技术选择比较可行方案，关键决策确认后建立最小工程基线；
不要假装已有项目事实，也不要为了显得完整一次性创建未来可能用不到的框架、数据库、服务或 CI 层。
```

Prototype / Spike 也必须明确探索范围、验证方式以及哪些安全/数据边界不能因为“只是原型”而放宽。

### Bug

```text
使用 coding 修复这个问题。
先稳定复现，读取完整错误和调用链，提出一个可证伪根因假设并用最小实验验证；
确认根因后建立回归失败用例，再做单一最小修复并重新验证。
```

### 只做方案

```text
使用 coding 基于当前仓库给落地方案，只分析和设计，不修改代码、分支或 PR。
先恢复实际版本、调用链、公共边界、依赖和测试，再比较方案。
```

## 5. 怎么用 Review

```text
使用 review-only 审查当前 PR/分支/实现。
先恢复 Review Target、上游要求、项目规则、真实工具链和影响边界；
独立重建需求，检查 diff/调用链/测试充分性，并输出有证据的 Findings；
不要把 Mock/Fake 冒充真实 Persistence、Runtime、外部依赖或跨组件证据。
```

有明确测试修改授权时可用 `review-and-test`；有实现修复授权时用 `review-and-fix`，但生产代码修改仍返回 Coding 完整流程，修复后再 re-review。

## 6. 怎么用 Docs

```text
使用 docs 检查当前技术文档是否与真实代码、Contract、Schema/Migration、配置、测试和运行方式一致。
先界定 not_applicable / targeted / full 文档影响；
写作先解释为什么存在、解决什么问题、数据/调用/状态怎么流、真实实现在哪，再解释必要术语；
不要复制完整 Schema/OpenAPI/generated code 形成第二套事实。
```

`full` 只代表“完整覆盖受影响文档域”，不是机械扫描仓库全部 Markdown。

## 7. L1 / L2 / L3

- `L1`：行为不变机械修改，或边界明确、影响隔离的极小修复；
- `L2`：新功能、行为变化、重要 Bug、多文件修改、多人并行或需要正式追踪；
- `L3`：public API/ABI/CLI/格式、Schema/Migration、跨模块 Contract、架构、认证授权、安全、部署恢复、重大依赖、不可逆数据行为或破坏性兼容变化。

代码行数少不等于 L1。Greenfield 中会长期锁定公共接口、核心数据模型、主要架构或运行/部署方式的选择也可能是 L3。

## 8. Change 与 Completion Gate

当前 Coding 自带 Change schema：

```text
coding-change/v1
```

**不兼容、不读取、不迁移任何历史 Change schema。** 如果目标项目仍保存旧格式，必须由该项目显式决定归档、转换或删除；Coding 工具不会静默接受。

重要工作保留这些语义：

```text
上游需求/决定
→ Requirement Traceability
→ 当前变更契约
→ Validation Matrix
→ 实现/测试/文档
→ Completion Audit
→ Review
→ Ready / Delivery
```

**载体不是固定项目架构。** 目标项目已有正式 Change/RFC/ADR/Spec/OpenSpec/Issue 机制时优先复用，只要能承载这些语义；Coding CLI 不会擅自改写未知第三方格式。

需要 Coding 自带载体时默认使用：

```text
.agents/changes/
├── active/
└── archive/
```

目标项目已经正式使用顶层 `changes/active` / `changes/archive` 承载同类 Coding Change 时可继续沿用。检测到 OpenSpec 等不同治理体系、但没有已确认 Coding carrier 时，`new-change` 会拒绝静默创建平行 Change。

## 9. `project-context.json`

```text
.agents/project-context.json
```

是**目标项目本地可失效导航缓存**：

- 只帮助找到规则、Manifest、锁文件、需求/架构/Contract/Migration/文档入口；
- 不复制需求正文，不保存架构结论；
- `cache_hit` 不表示普通源码没变化；
- 当前代码和实际运行结果始终优先；
- 该文件不提交 Git，应加入目标项目 `.gitignore`、本地 exclude 或等价忽略机制；
- 生成时间使用带 `+08:00` 偏移的北京时间。

刷新：

```bash
python .agents/skills/coding/scripts/coding.py discover --root .
```

只读任务没有写项目授权时，不应为了缓存创建文件；在当前会话做等价有界发现即可。

## 10. 用户定义的全局工程硬规则

这些规则会随 Coding Skill 一起作用于所有目标项目：

1. 代码注释统一使用中文（专有名词、标识符、协议、库、标准名和必须原样保留的外部文本除外）；
2. 所有新增或修改的函数，包括 public/exported 与 internal/private/helper，都必须有函数级中文注释或文档注释；
3. Git 提交信息统一使用中文；
4. Agent 自有/默认解释的时间统一使用北京时间 `Asia/Shanghai`；
5. 除更高优先级外部 wire-format Contract 强制其他序列化形式外，人类可读日志统一使用 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`。

这些是 Skill 作者的跨项目硬规则，不应在“通用化”时被误删成项目特定偏好。

## 11. 常用 CLI

```bash
python scripts/install.py --target <目标项目根目录>
python .agents/skills/coding/scripts/coding.py bootstrap --root .
python .agents/skills/coding/scripts/coding.py discover --root .
python .agents/skills/coding/scripts/coding.py status --root .
python .agents/skills/coding/scripts/coding.py conflicts --root . --json
python .agents/skills/coding/scripts/coding.py new-change --help
python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

`install.py` 从 Agent_Skills 源仓库执行；其余 Coding CLI 从已经安装 Skill 的目标项目执行。CLI 是工作流辅助工具，不替代 Agent 对需求完整性、测试充分性和业务语义的判断。`status` 会显示实际使用的 Coding Change carrier。

## 12. 维护原则

修改 Skill 时优先保持原有高价值细节。允许重新组织、条件化、去项目化，但不得因为“更简洁”降低：

- 触发条件；
- 例外；
- 失败处理；
- 停止条件；
- 验证责任；
- 安全边界；
- 兼容与迁移要求；
- 权限和 Git 边界。

`12_规则保留映射.md` 已按当前治理决定删除，不再维护独立映射文档。后续规则重组应在当前 Change/Review 中记录受影响高价值规则，并通过 portability/preservation 回归、旧入口反向检查和人工语义 Review 证明内容守恒。

任何自动测试只能防止明显回归，不能替代人工逐节检查规则语义是否仍完整。

## 13. 进一步阅读

- [`.agents` 总说明](.agents/README.md)
- [Coding 使用说明](.agents/skills/coding/README.md)
- [Coding 正式规则](.agents/skills/coding/SKILL.md)
- [目标项目安装与 AGENTS Bootstrap](.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md)
- [Review 使用说明](.agents/skills/review/README.md)
- [Docs 使用说明](.agents/skills/docs/README.md)

## 14. 本地 MCP Runtime 分发

如果你的目标是**尽量保持当前 Skill 执行效果，同时不把完整 Reference Markdown 直接放进每个目标项目**，使用 Runtime 模式。它保留 Native Core `SKILL.md`，把详细 `references/*.md` 逐字打进本地 MCP 的加密 Bundle；目标项目只留下同名 stub，Agent 命中 Reference 后通过 `agent_skills_load_context` 取得 canonical 原文。

这不是把复杂 Skill 摘要成 Policy，也不是对机器 Owner 的强加密。AES-256-GCM + onefile 的主要价值是阻止普通使用者直接浏览/批量复制完整 Markdown，同时让模型仍然获得原始 Reference 文本。

完整打包、安装、Codex/Cursor/Claude Code 配置、目标项目接入、升级和回滚说明见：

- [Runtime 使用说明](runtime/README.md)
- [Runtime 正式规则](.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md)

最短流程：

```text
1. 安装 runtime/requirements-build.txt
2. python scripts/build_runtime.py --output-dir dist --json
3. python scripts/install_runtime.py --artifact <dist/agent-skills-mcp[.exe]> --json
4. 把已安装 Runtime 作为全局 stdio MCP 注册到 Codex/Cursor/Claude Code
5. python scripts/install.py --mode runtime --runtime-command <agent-skills-mcp> --target <目标项目>
6. 在目标项目按原来的 AGENTS → Coding → Reference / Review / Docs 流程开发
```

旧命令 `python scripts/install.py --target <目标项目>` 仍等价于 `--mode full`，继续完整复制 Markdown，保证现有用户兼容。

## 15. 正式 Release 与版本化分发

仓库根 [`VERSION`](VERSION) 是正式产品版本的唯一事实源。正式发布**不会因为 VERSION push 自动触发**：维护者在 GitHub Actions 中手工运行 [`.github/workflows/release.yml`](.github/workflows/release.yml)，Branch 选择 `main`，并输入与 `VERSION` 一致的 tag，例如 `v1.0.0`。Workflow 随后在该 `main` SHA 上重新构建正式资产、自动创建输入 tag 和 GitHub Release；PR 临时构建产物不会直接变成正式 Release，也不需要提前手工创建 tag。

每个正式版本至少提供：

```text
agent-skills-full-kit-v<VERSION>.zip
agent-skills-mcp-runtime-kit-v<VERSION>-linux.zip
agent-skills-mcp-runtime-kit-v<VERSION>-windows.zip
agent-skills-mcp-runtime-kit-v<VERSION>-macos.zip
SHA256SUMS
```

### Full Kit

`agent-skills-full-kit-v<VERSION>.zip` 面向完整 Markdown 分发。解压后可以直接从 Kit 根执行：

```bash
python scripts/install.py --target <目标项目根目录>
```

Full Kit 只携带三个正式 Skill、安装器、版本和必要使用资料，不携带 Agent_Skills 源仓库自己的根 `AGENTS.md`、`.agents/changes/` 或 `project-context.json`。

### Runtime Kit

Runtime Kit 按平台下载，不要把某个平台 onefile 当成跨平台二进制。解压后的完整使用方式见 [runtime/DISTRIBUTION.md](runtime/DISTRIBUTION.md)：先安装用户级 Runtime，再注册 stdio MCP，再用 Kit 内 `install_runtime_target.py` 给目标项目安装 Native Core + Reference Stub。

下载 Release 后先用 `SHA256SUMS` 校验 ZIP，再安装或升级。正式 tag/Release 不覆盖、不移动；需要修正版时递增 `VERSION`，不要替换旧版本资产。

维护者手工 tag 发布流程、失败恢复和发布后验证见 [RELEASING.md](RELEASING.md)；版本用户可观察变化见 [CHANGELOG.md](CHANGELOG.md)。
