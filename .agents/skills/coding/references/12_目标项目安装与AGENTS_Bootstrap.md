<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.13","触发":{"包含":{"维度":"意图","取值":["Runtime 安装","Runtime 升级","项目 Bootstrap"]}},"依赖":["coding.reference.02"]}
-->

# 目标项目安装与 AGENTS Bootstrap

这份规则处理一个边界：**如何通过正式 Runtime binary 把当前 Release 的 Agent_Skills 安装/升级到目标项目，并安全建立目标项目自己的 `AGENTS.md` Overlay，使后续研发会话先恢复项目真实事实；默认 Runtime Mode 通过项目级治理 MCP 取得当前任务所需完整约束，而系统、开发者或用户级更高优先级指令已经明确选择其他 Agent_Skills 执行模式时，由该模式负责取得治理正文；同时保留 Source Mode 对 Router / Skill / Reference 的完整明文维护能力。**

它不规定目标项目必须使用什么语言、框架、数据库、目录、CI 或部署方式，也不替代目标项目已有规则。

当前唯一正式安装通道：

```text
Runtime binary
→ 使用者只拿对应平台 agent-skills-mcp[.exe]
→ 在目标项目根运行
→ 项目级安装 Runtime + Skills 根级 shared files + 全部正式 Skill Core/运行资产
→ 不在目标项目安装 canonical Reference 或 Stub
→ 创建/更新目标项目 AGENTS managed block
→ managed block 只暴露项目事实恢复 + 默认 Runtime 治理入口 + 高优先级模式覆盖边界 + 用户可见进度边界
→ 不把内部 Router / Skill / Reference 导航作为 Runtime 日常用户入口
→ 建立项目级 MCP 配置
```

Runtime 的加密、Project Payload、managed installation manifest、Codex/Cursor/Claude Code 项目 MCP 和 binary 升级规则详见 [13_本地MCP_Runtime分发与原文上下文加载.md](13_本地MCP_Runtime分发与原文上下文加载.md)。

## 0. 两阶段 Bootstrap：安装与宿主大模型治理

目标项目接入必须区分两个阶段，不能把 binary 的确定性安装和大模型语义判断混成一件事：

```text
Runtime Installation Bootstrap
→ Runtime binary 安全安装/升级内部 shared runtime assets、Skill Core、项目 MCP 与 Agent Skills managed block
→ 没有 AGENTS 时创建结构模板和“状态：待校准”项目自有区
→ 不调用 LLM，不扫描整个仓库推断架构

用户在 Codex / Cursor / Claude Code 等宿主中提出自然语言研发任务
→ 宿主大模型读取项目 AGENTS 与当前项目真实事实
→ 没有更高优先级模式覆盖时，通过已配置的项目级治理 MCP 取得本任务需要的完整规则正文
→ 已有更高优先级 Agent_Skills 执行模式时，按该模式取得治理正文，managed block 不再强制冲突的 Runtime/MCP 取得路径
→ 首次接入 / 状态待校准 / 长期治理事实漂移时命中 Project Governance Bootstrap
→ 有界调查当前仓库真实实现
→ 只在 managed block 外创建/校准项目自己的 Overlay
→ 标记“状态：已校准”
→ 重新读取最终 AGENTS.md
→ 继续原始研发任务
```

因此，Runtime binary 本身不需要也不允许成为第二个 Coding Agent；**Project Governance Bootstrap 由当前项目所用的宿主大模型执行**。用户无需手工构造 Task Route 或调用内部语义扫描命令，普通开发/修复/重构等**自然语言研发任务**就可以触发这条前置规则。Runtime Mode 中宿主根据当前项目事实建立内部任务路由并加载本 Reference；Stable ID、依赖图和内部路由细节继续属于 Runtime 治理实现，不是用户日常过程输出。

项目自己的治理状态属于 `AGENTS.md` **managed block 外**内容。新建模板使用：

```text
<!-- agent-skills:project-governance:v1 -->
## 项目治理校准状态
- 状态：待校准 / 已校准
```

安装器不维护这个项目自有状态；宿主大模型只有在完成真实仓库调查和 Overlay 校准后才能改成“状态：已校准”。已有 `AGENTS.md` 第一次接入时没有该状态，也按首次治理处理。状态只是是否完成首次长期规则校准的导航，不是代码/Contract/CI 当前正确性的证明。

## 1. 何时读取

出现以下任务时必须读取本文件：

- 首次把 Agent_Skills 接入目标项目；
- 用新 Release 升级目标项目中的 Agent_Skills；
- 目标项目缺少根 `AGENTS.md`，需要建立项目 Overlay；
- 目标项目已有 `AGENTS.md`，需要安全补充/升级 Agent Skills managed block；
- 修复或审查 AGENTS managed block、Bootstrap 行为；
- 修改共享 [`.agents/skills/ENTRY.md`](../../ENTRY.md)、唯一 [`.agents/skills/router/SKILL.md`](../../router/SKILL.md) 的项目安装、内部 Runtime 可达性或 Source Mode 可达性；
- 修改正式 Skill 或 Skills 根级 shared runtime file 的 Project Payload 安装边界；
- 修改 Runtime Mode 的用户可见进度/治理细节披露边界；
- 判断哪些 `.agents` 内容属于 Agent_Skills 受管内容，哪些属于目标项目自有状态；
- 修改项目 Runtime、ownership manifest、宿主 MCP 配置或安装回滚。

普通只读分析、Review、文档审计或功能开发，如果用户没有授权项目规则写入，不因为发现 `AGENTS.md` 缺失就自动创建或修改文件。首次治理确有必要时，只在当前会话内完成最少充分的有界事实调查，明确 `AGENTS.md` 治理状态未持久化，然后**继续原始只读任务**；权限边界仍按 Coding 主规则执行。

## 2. 固定边界：分发 Skill，不复制源仓库 Bootstrap / Maintenance

Agent_Skills 源仓库根 `AGENTS.md` 是源码直读/维护模式的薄 Bootstrap，[`.agents/MAINTENANCE.md`](../../../MAINTENANCE.md) 只负责维护 Agent_Skills 源仓库本身。二者都**禁止直接复制成目标项目根 `AGENTS.md`**。

Source Mode 直接使用 Agent_Skills 明文源码时，先读取薄入口：

[`.agents/skills/ENTRY.md`](../../ENTRY.md)

Entry 无条件进入 [`.agents/skills/router/SKILL.md`](../../router/SKILL.md)。Entry 作为 Runtime Project Payload 的 Skills 根级 shared runtime file 安装，Router 则作为动态发现的正式 Skill Core 安装；但 **Runtime Mode 的目标项目根 `AGENTS.md` 不把这些内部文件作为用户可见日常导航**。Runtime 日常任务从项目根规则进入已配置的项目级治理 MCP，由 Runtime 内部完成路由并返回 required 完整原文。

Entry 不是正式 Skill，也不维护 Catalog；Router 是正式 Skill 和唯一跨 Skill 控制面，只选择上下文与 Handoff，不执行专业工作。

正式 Skill 从：

```text
.agents/skills/<skill-name>/SKILL.md
```

动态发现。Router 与当前专业 Skills 都来自这套动态 Catalog，这些名称不是安装器/Runtime 的永久白名单；Source Mode 的可读 Catalog 由唯一 Router 展示，Runtime MCP 公共返回面不需要再次枚举这一内部 Catalog。

目标项目中的下列内容不是普通安装/升级的清理目标：

```text
.agents/changes/
.agents/project-context.json
.agents/skills/<项目自有 Skill>/
.agents/skills/<未被 manifest 认领的根级文件>
.agents/<其他项目自有内容>/
AGENTS.md managed marker 外文本
其他项目自有 MCP / 宿主配置
```

Runtime 安装自己的：

```text
.agents/runtime/agent-skills-mcp[.exe]
.agents/agent-skills-install.json
.agents/skills/ENTRY.md
.agents/skills/<Runtime manifest 明确认领的正式 Skill>/
```

`.agents/runtime/` 是项目本地 Runtime，应被目标项目 `.gitignore` 忽略；install manifest 只承担 Agent_Skills ownership/version 导航，不是项目业务事实源。

### 普通 Runtime 与源仓库 Mutation 边界

**普通 Runtime** 的 `AGENTS` managed block 只承担目标项目正常研发入口：项目事实优先、默认项目级治理 MCP、首次治理校准、失败停止、权限边界和用户可见进度边界。若系统、开发者或用户级更高优先级指令已明确选择其他 Agent_Skills 执行模式，managed block 只对冲突的 Runtime/MCP 规则取得路径与 Runtime 披露限制让位；项目自己的 Overlay、事实和长期约束仍继续生效。Entry/Router/Core 继续作为受管内部运行资产存在，但不要求用户可见过程复述其文件身份、分类或路由实现。

源仓库中针对 Skill / Reference 的新增、修改、删除、重命名、拆分、合并、通用化和跨仓库同步，由 Agent_Skills 根 `AGENTS.md` 识别 **源仓库 Mutation** 维护意图，再进入 [`.agents/MAINTENANCE.md`](../../../MAINTENANCE.md)、Coding 与 ref16。普通目标项目只需要知道：安装器 manifest 明确认领的 `.agents` 运行资产不是项目自有规则，不应直接手工修改；项目自己的长期规则继续写在项目自己的正式事实源中。

## 3. 最终用户入口：项目级单 binary

最终使用者不需要访问 Agent_Skills 源仓库，也不需要为了**安装 Agent_Skills 或运行项目 MCP Runtime** 预先安装 Python、pip、venv 或外部安装脚本。

但正式 Coding Skill 自身仍包含 `scripts/coding.py`、`scripts/ready_check.py` 等 Python helper，并会在项目发现、Change 管理、Ready Check 等命中场景使用它们；这些脚本属于 Project Payload 的正式运行资产，不能因为“单 binary 安装”而删除。如果目标项目/宿主没有可用 Python，必须按 Coding Skill 对应规则使用明确的 manual fallback；某个机器门禁因此无法执行时要标记未验证，不能假装通过。

Windows：

```powershell
cd D:\work\MyProject
.\agent-skills-mcp.exe
```

Linux / macOS：

```bash
cd /work/MyProject
chmod +x ./agent-skills-mcp
./agent-skills-mcp
```

无参数运行等价于安装/升级当前工作目录。也可以显式：

```text
agent-skills-mcp install --target <目标项目根目录> --json
```

当前 Project Payload 使用 v2，install manifest 使用 v3 `managed_files` 逐文件 ownership。安装器只接受当前 v3 manifest；v1、v2、未知或损坏 schema 全部直接失败，不推断 ownership，也不保留旧 Stub 清理通路。

Runtime binary 负责：

1. 校验自身内嵌 Reference Bundle 与 Project Payload；
2. 读取动态正式 Skill Catalog，以及 Project Payload 显式 `shared_files`；
3. 读取旧 `.agents/agent-skills-install.json`：只接受 v3，并且只认领 `managed_files`；
4. 首次安装遇到未被认领的同名 Skill 或同名 shared file 时 fail closed；
5. 预检并逐文件更新新受管 Core/shared files，其中 shared file 是 [`.agents/skills/ENTRY.md`](../../ENTRY.md)，唯一 Router 是动态 Skill Core [`.agents/skills/router/SKILL.md`](../../router/SKILL.md)；
6. 安装/升级项目 `.agents/runtime/agent-skills-mcp[.exe]`；
7. 创建或安全增量更新根 `AGENTS.md`，managed block 只暴露项目事实恢复、默认项目级治理 MCP、明确的高优先级模式覆盖边界、首次治理校准和用户可见进度边界，不直接暴露内部 Router/Skill/Reference 导航；
8. 增量更新 `.gitignore`；
9. 建立 Codex / Cursor / Claude Code 项目级 MCP 入口和必要 bridge；
10. 写入新的 managed installation manifest；
11. 任一步失败时按安装前快照恢复本轮 touched managed files、Runtime、manifest 和受管文本。

目标项目不安装 canonical Reference 或 Stub；默认 Runtime Mode 由项目级 MCP 先取得公共 route contract、提交中文 Task Route，再按不透明路由令牌加载当前 required 的完整 canonical Context。宿主可以使用这些内部结果执行治理，但用户可见过程应描述真实工程活动，不复述内部资产身份和加载明细。

## 4. Bootstrap、Entry 与 Router 的唯一事实源

三个入口职责必须分开：

```text
coding/assets/AGENTS.template.md
→ 目标项目原本没有 AGENTS.md 时的项目 Overlay 外层模板

coding/assets/AGENTS.managed.md
→ 写入目标项目 AGENTS.md 的 Runtime 薄 Bootstrap
→ 负责项目事实优先 + 默认项目级治理 MCP + 高优先级模式覆盖边界 + 首次校准 + Runtime 用户可见披露边界 + 默认 Runtime MCP 不可用时 fail closed
→ 不直接暴露内部 Router / Skill / Reference 导航

.agents/skills/ENTRY.md
→ Skills 根级 shared runtime file
→ 只负责恢复项目事实、无条件进入 Router、失败关闭

.agents/skills/router/SKILL.md
→ Source Mode 唯一完整 Skill Catalog / Router
→ Runtime Mode 作为动态正式 Skill Core 安装
→ 负责专业 Skill 选择、Reference 加载、Handoff、失败和权限边界
→ 不生成项目执行计划、不创建子 Agent、不接管专业 Skill
```

Runtime binary 和源码维护用 Coding Bootstrap 都使用同一 canonical 规则体系，不维护第二套项目路由。`AGENTS.managed.md` 不能重新复制 Entry/Router 详细正文；也不能为了保密把 Entry/Router/Core 从 Project Payload 中随意删除，因为分发、ownership 与宿主兼容仍需要这些运行资产。

Bootstrap 只负责机械可证明的内容：

- 创建或安全增量更新根 `AGENTS.md`；
- 创建或增量更新 `.gitignore`；
- 确保 `.agents/project-context.json` 与 `/.agents/runtime/` 被显式忽略；
- 新建 `AGENTS.md` 时，根据当前扫描结果列出真实存在的高价值事实入口；
- 不根据这些入口猜测项目技术栈或架构。

Bootstrap **不会**：

- 自动创建 Change/RFC/ADR/OpenSpec；
- 自动修改 Schema/Migration；
- 自动决定框架、数据库、部署平台或 CI；
- 自动生成权威架构说明；
- 创建 `project-context.json`；
- 修改目标项目其他 `.agents` 内容；
- 代替 Coding Agent 对复杂项目语义做判断。

维护/调试 Bootstrap 本身时，可以直接运行 Coding CLI：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root . --json
```

这是源仓库维护入口，不是最终用户安装通道。正式 Runtime 安装已经通过 Project Payload v2 保证 Entry、Router 与 Coding 同版本落地；手工使用这个 helper 时仍必须先确认目标项目已经具备本 Release 的 [`.agents/skills/ENTRY.md`](../../ENTRY.md)、[`.agents/skills/router/SKILL.md`](../../router/SKILL.md) 与 Coding Skill，因为 helper 的运行资产校验与 Runtime 用户可见导航是两个不同边界。

## 5. 目标项目没有 AGENTS.md

没有根 `AGENTS.md` 时，使用 [`coding/assets/AGENTS.template.md`](../assets/AGENTS.template.md) 创建项目 Overlay 初版。

初版必须包含：

1. Agent Skills managed block；
2. managed block 明确默认 Runtime Mode 通过已配置的项目级治理 MCP 取得本次任务完整约束，并允许系统、开发者或用户级更高优先级指令显式选择其他 Agent_Skills 执行模式；无论采用哪种模式，都不直接暴露内部 Router/Skill/Reference 导航；
3. 项目 Overlay 的维护边界，且模式覆盖不得让项目自己的规则、事实、Contract、Schema、CI、部署和验收失效；
4. 初始化时真实存在的项目规则、Manifest/Lock/Build、需求/Spec、Contract/Schema、Migration、README/Architecture/Documentation 等事实入口导航；
5. 明确“事实入口存在”不等于“已经确认某个框架、数据库或架构”；
6. 项目特殊约束应由项目自己的规则/事实源维护；
7. 默认 Runtime Mode 的用户可见过程允许说明代码、测试、文档、Review、Git/CI 和交付等真实工程活动，但不主动披露内部治理文件、目录、分类、标识、路由或加载明细；更高优先级模式已经明确选择其他披露边界时，不再强制冲突的 Runtime 披露限制。

例如：

```text
发现 package.json
≠ 自动写入 React

发现 pyproject.toml
≠ 自动写入 FastAPI

发现 migration 文件
≠ 自动写入 PostgreSQL
```

项目语义仍由后续 Coding 任务读取真实文件和调用链后确认。

## 6. 目标项目已经有 AGENTS.md

已有 `AGENTS.md` 是项目资产，必须优先保护原文。

Bootstrap 只认：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

作为 AGENTS 自管边界。

### 6.1 当前没有 managed block

```text
已有 AGENTS.md 原始字节
→ 完整保留
→ 在文件末尾增加必要空行
→ 追加 Agent Skills managed block
```

不得为了统一格式重排标题、替换换行符、修正文案或格式化原有内容。

### 6.2 已经有一个完整 managed block

```text
marker 前原文：逐字保留
managed block：替换为当前版本
marker 后原文：逐字保留
```

### 6.3 marker 损坏

以下情况必须失败：

- 只有 start，没有 end；
- 只有 end，没有 start；
- end 出现在 start 前；
- start/end 重复。

禁止猜测“哪一段可能是旧 block”后覆盖。保留原文件不变并报告 marker 错误，由项目 Owner 先修复边界。

## 7. managed block 必须表达什么

[`coding/assets/AGENTS.managed.md`](../assets/AGENTS.managed.md) 是 managed block 唯一模板事实源，但它现在只承担 **Runtime 薄 Bootstrap**。至少保持：

1. 项目自己的规则和真实事实优先；
2. 本 managed block 定义 Agent_Skills 的默认 Runtime Mode：没有更高优先级模式覆盖时，使用当前项目已经配置的研发治理 MCP 获取本次任务需要的完整约束；
3. 如果系统、开发者或用户级更高优先级指令已经明确选择其他 Agent_Skills 执行模式，则只停止执行与该模式冲突的 Runtime/MCP 规则取得路径和 Runtime 用户可见披露限制；项目自己的规则、事实、Contract、Schema、CI、部署和验收边界仍继续生效；
4. Runtime Mode 不根据受管运行资产中的源码维护导航去直接读取、本地枚举或猜测治理规则；Source Mode 维护者直接使用明文仓库时不受 Runtime 用户可见隐藏边界限制；
5. 通用示例不能覆盖目标项目事实；
6. 首次接入、治理状态未校准或长期治理事实漂移时，在实质性代码修改前执行有界 Project Governance Bootstrap；
7. 用户可见处理过程可以正常说明项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git、CI 和交付状态；
8. 默认 Runtime Mode 的用户可见输出不得主动展示、枚举或复述治理系统内部分类、文件名、目录结构、规则标识、路由映射、内部凭据或加载明细；解释原因时说明工程步骤本身，不引用内部治理资产；更高优先级模式已有不同明确披露规则时，不再强制冲突的 Runtime 披露限制；
9. 安装器认领的 `.agents` 受管运行资产不是项目自有规则，不直接手工修改，项目长期规则维护在项目自身正式事实源；
10. 默认 Runtime Mode 下，项目级治理 MCP 不可用、必需约束不完整或与更高优先级规则存在无法安全解析的冲突时明确报告并停止依赖对应治理要求，不假装遵守；其他 Agent_Skills 执行模式的失败边界由对应更高优先级指令与 canonical 规则负责；
11. managed block 不复制 canonical Source 仓库地址、Source Mode 文件导航、Maintenance、Stable ID 或第二套路由规则；模式覆盖只表达优先级契约，不暴露维护者内部治理面。

原 managed block 曾直接承担的 Reference 触发、Runtime Task Route → required Context、Figma NOT_READY/READY Handoff、Review、Docs、Skill/Reference 失败停止、CI/Branch Protection/PR/Release/Migration/安全与授权边界、项目事实来源等完整可执行语义，仍由 [`.agents/skills/router/SKILL.md`](../../router/SKILL.md) 与各 Skill canonical 规则作为唯一正文 Owner 保存，并由 Runtime MCP 内部求值和加载。这里的变化只收窄 Runtime 用户可见入口，并增加“默认 Runtime / 高优先级显式模式覆盖”的薄契约；不删除任何治理语义，不改变 Source Mode 的明文导航能力，也不让项目 Overlay 失效。

## 8. `.gitignore` 规则

所有目标项目应显式忽略：

```gitignore
.agents/project-context.json
/.agents/runtime/
```

规则：

- `.gitignore` 不存在：创建最小规则；
- 已存在等价规则：不重复追加；
- 已有其他规则：原内容保留，只在末尾增量追加；
- `.gitignore` 是符号链接或不是普通文件：拒绝修改；
- 不为了加入这几行重新排序、去重或格式化项目已有规则。

## 9. Project Skill 与逐文件 ownership

动态发现回答“Release 有哪些正式 Skill”；目标项目可写边界由 install manifest v3 的 `managed_files` 决定。`skills` 和 `shared_files` 只是维护/ownership 导航，不能授权替换整个目录，也不要求通过 Runtime MCP 公共状态向用户枚举。

```text
managed_files
→ 相对 .agents/skills 的 Agent_Skills 受管文件
→ 新版本仍存在：原子升级
→ 新版本已删除：只删除该文件

同一 Skill 目录内未认领的 Reference / asset / 项目文件
→ 项目自有
→ 永远不因普通升级删除
```

当前 shared file 只有 `ENTRY.md`；Router 由正式 Skill 目录分发。首次安装若目标已有同名 shared Entry 或同名正式 Skill 目录且没有合法 manifest 证明 ownership，必须在任何写入前 fail closed；禁止通过文件名、内容相似或 hash 猜归属。

非 v3 manifest 不提供原地升级。安装器不会扫描、识别或清理旧 Stub，也不会根据旧目录结构猜测 ownership；需要从旧安装切换时，必须先由项目 Owner 备份并显式处理旧安装边界，再执行当前版本安装。

## 10. 安全与原子性

安装/Bootstrap 修改研发治理入口，失败边界必须严格：

- 目标 `.agents`、受管文件、Runtime、AGENTS/宿主配置路径出现符号链接时拒绝越界修改；
- Project Payload 先校验 schema、`skills`、`shared_files`、path / SHA / size / mode / `payload_digest`；
- Project Payload v2 必须明确包含 `shared_files: ["ENTRY.md"]` 和对应 `ENTRY.md` 条目，并通过动态 Catalog 包含 `router/SKILL.md`，避免入口或控制面缺失；
- 首次同名未认领 Skill/shared file/managed file 冲突在目标写入前发现；
- 不移动或替换整棵 Skill 目录，只逐文件原子写入；
- 写入前保存全部 touched managed files、Runtime、manifest 和受管文本的 bytes/权限快照；
- AGENTS、`.gitignore`、CLAUDE/Codex marker 和 JSON MCP 配置在写入前先验证编码/结构；
- 单文件写入使用同目录临时文件 + 原子替换；
- 任一步异常时恢复本轮 touched files、Runtime、manifest 和受管文本快照；
- 禁止用 `git reset --hard`、`git clean`、强制推送或历史重写实现安装回滚。

安装器不承诺普通文件系统跨多文件具备数据库式事务，但必须把可预检错误尽量前移，并把修改限制在可审计 managed 边界。

## 11. Greenfield 与已有项目

Greenfield / 空仓库：

```text
安装当前 Release 内部 shared Entry + 正式 Router / 专业 Skill
→ Bootstrap 创建 AGENTS.md
→ managed block 默认指向项目级治理 MCP，并允许更高优先级显式 Agent_Skills 模式覆盖，而不是暴露内部源码导航
→ 只列真实事实入口或明确当前未发现
→ 建立项目 MCP/宿主入口
→ 默认 Runtime Mode 由 MCP 取得本任务完整约束；已有明确模式覆盖时按该模式取得
→ Coding 按 Greenfield 规则确认目标、硬约束和最小工程基线
```

已有 v3 安装项目：

```text
依据 v3 managed_files 逐文件升级
→ 保留项目自有 Skill、Reference、未认领文件和其他 .agents 内容
→ 保留已有 AGENTS 原文
→ 追加/升级 Runtime 薄 managed block
→ 继续安装当前 Release 内部 shared Entry/Router/Core
→ 只更新 Agent_Skills 自管宿主边界
→ 默认日常任务通过项目级治理 MCP 取得完整约束；更高优先级明确模式覆盖时不强制冲突的 Runtime 取得/披露路径
→ Coding 继续以已有项目规则和真实实现为准
```

旧 schema/旧 Router 路径不在本版本兼容范围内，不自动迁移。Bootstrap 不是自动架构设计器。

## 12. Project Governance Bootstrap：有证据的项目 Overlay 语义校准

当首次接入、项目治理状态尚未校准、现有 `AGENTS.md` 与长期工程事实疑似漂移，或用户明确要求刷新项目规则，并且当前任务授权修改项目时，Coding Agent 在 Runtime Installation Bootstrap 之后执行 Project Governance Bootstrap。这个阶段由**宿主大模型**负责语义判断，不由 Runtime binary 自动改写项目规则。

固定顺序：

1. 重新读取安装/接入后的项目 `AGENTS.md` 以及适用的 `CONTRIBUTING` / 子目录规则；
2. 按 ref01 做有界事实调查，只读取与长期研发导航直接相关的最少充分代码、Manifest/lock、Contract/Schema/Migration、测试、CI、部署和正式文档；
3. 把现有 AGENTS 内容与新证据分成**规范性规则、描述性事实、未确认事项**；
4. 规范性规则若与当前实现冲突，先把它视为实现/配置偏离；**不能通过修改 `AGENTS.md` 让错误实现合法化**，不能因为代码没有遵守就自动删除或弱化规则；
5. 描述性事实只有在当前机器事实/代码/CI/运行证据足以证明过时时才做最小修正；不能仅凭文件名/目录名写入框架、数据库、架构、Owner、Contract、CI 或部署结论；
6. 多个高权威事实源冲突或证据不足时保留为未确认；如果会实质改变 Contract、Schema、数据、安全、部署或验收，继续核实或请求 Owner 决策，不猜一个正确；
7. 可确认的长期事实只在 managed block **之外**增量补充；不修改 managed block 内模板文本，不把 Router 专业路由正文复制到项目 Overlay；
8. 已有仍有效文本尽量保持原位置和语义；只做必要的 targeted 修正，不为了套固定模板重排整份已有 AGENTS；
9. 对新建模板，固定章节只是结构骨架；没有真实事实的章节保持为空或明确未确认，不为了“填满模板”发明制度；
10. 首次治理成功后，在项目自有区保留 `<!-- agent-skills:project-governance:v1 -->` 并把状态更新为“状态：已校准”；已有 AGENTS 没有该项目自有状态时可在 managed block 外增量建立；
11. **重新读取最终 `AGENTS.md`**，确认项目规则、事实描述、未确认事项和 Agent Skills managed block 边界没有互相覆盖；
12. 然后回到用户最初的自然语言请求，按最终规则**继续原始研发任务**；治理 Bootstrap 不是把原任务替换成只写文档。

后续普通开发不重复全量首次治理。每个任务仍做廉价事实/缓存失效检查；只有技术栈、模块 Owner、Contract/Schema、开发/验证入口、CI/Release/部署等长期工程事实变化时，才 targeted 调查并更新对应 Overlay。Runtime binary 本身仍不调用 LLM、不自动生成项目架构结论，也不修改项目自有治理状态。

## 13. 宿主差异

项目级配置只是让宿主找到同一个项目 Runtime：

```text
Codex
→ .codex/config.toml
→ workspace trust 由 Codex 自己决定

Cursor
→ .cursor/mcp.json

Claude Code
→ .mcp.json
→ CLAUDE.md 中 @AGENTS.md bridge
```

宿主已有同名 `agent-skills` MCP 但不属于 Agent_Skills managed ownership 时，安装器必须拒绝静默覆盖。宿主要求首次 trust/approval 时不得绕过。

## 14. 验证安装/Bootstrap

至少验证：

- 最终平台 artifact `status/self-test`；
- 在真实临时项目运行 binary，不依赖源仓库；
- 无参数当前目录安装；
- 显式 `install --target`；
- 重复升级幂等；
- 动态正式 Skill 都安装并包含 [`.agents/skills/router/SKILL.md`](../../router/SKILL.md)，薄 [`.agents/skills/ENTRY.md`](../../ENTRY.md) 不被误识别成 Skill；
- 目标 Project Payload 不出现 canonical Reference 或 Stub；
- Project Payload `shared_files` 显式认领 `ENTRY.md`，该文件原样进入目标项目；Router Core 由动态 Skill Catalog 原样分发；
- Source Mode 的根入口继续显式导航 Entry 与唯一 Router，Runtime 安装后的根 `AGENTS.md` 不出现 `.agents/skills/`、Entry/Router/Reference 文件名、Stable ID、canonical 仓库地址、GitHub App 或 Maintenance 等内部治理导航；
- Runtime 安装后的根 `AGENTS.md` 明确声明 Runtime 为默认模式；没有更高优先级模式覆盖时仍通过项目级治理 MCP 取得完整约束；
- 系统、开发者或用户级更高优先级指令已经明确选择其他 Agent_Skills 执行模式时，Runtime managed block 不再强制与该模式冲突的本地 Runtime/MCP 规则取得路径或 Runtime 披露限制；
- 无论是否存在模式覆盖，目标项目自己的规则、事实、Contract、Schema、CI、部署和验收边界仍继续生效；
- Runtime 安装后的根 `AGENTS.md` 仍明确允许显示代码修改、测试、文档同步、复核、Git/CI 和交付等真实工程过程；
- MCP `status/route_contract/submit/load/checkpoint` 公共 envelope 不公开 Skill Catalog、命中 Skill、Reference 身份/文件名/路径/hash/size、内部风险或加载计数；
- `load_required_context` 返回的 `完整原文` 与 canonical source 逐字一致，不能为了保密删除 routing metadata；
- install manifest v3 显式认领 `managed_files` 与 `shared_files`；
- 同名未认领 shared Entry 或正式 Skill 在任何目标写入前 fail closed；
- Entry/Router/Runtime/manifest 后续失败可以恢复旧受管状态；
- v1/v2/未知 schema 明确拒绝，安装器不存在旧 Stub 扫描或清理路径；
- Coding Python helper 作为 Project Payload 正式运行资产继续安装；
- `.agents/runtime/` 和 install manifest 正确；
- AGENTS 用户原文/managed marker 正确；
- 项目自有 Skill 和未认领根级文件保留；
- 同名未认领 Skill 冲突 fail closed；
- 删除旧受管项只依据旧 v3 `managed_files`，没有 schema 或目录级例外；
- Codex/Cursor/Claude 配置保留其他用户内容；
- 项目内 Runtime 通过真实 stdio MCP smoke；
- 安装失败可恢复本轮受管变化。

任何“安装完成”结论都必须来自本轮实际验证，不能用代码阅读或 Python 模块单测替代最终平台 artifact 证据。
