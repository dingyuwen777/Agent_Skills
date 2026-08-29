<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.13","触发":{"包含":{"维度":"意图","取值":["Runtime 安装","Runtime 升级","项目 Bootstrap"]}},"依赖":["coding.reference.02"]}
-->

# 目标项目安装与 AGENTS Bootstrap

这份规则处理一个边界：**如何通过正式 Runtime binary 把当前 Release 的 Agent_Skills 安装/升级到目标项目，并安全建立目标项目自己的 `AGENTS.md` Overlay，使后续研发会话稳定进入同一个 Agent Skills Router，再由 Router 进入 Coding / Review / Docs / Figma / References。**

它不规定目标项目必须使用什么语言、框架、数据库、目录、CI 或部署方式，也不替代目标项目已有规则。

当前唯一正式安装通道：

```text
Runtime binary
→ 使用者只拿对应平台 agent-skills-mcp[.exe]
→ 在目标项目根运行
→ 项目级安装 Runtime + Skills 根级 shared files + 全部正式 Skill Core/运行资产
→ 不在目标项目安装 canonical Reference 或 Stub
→ 创建/更新目标项目 AGENTS managed block
→ managed block 指向项目内唯一 .agents/skills/ROUTER.md
→ 建立项目级 MCP 配置
```

Runtime 的加密、Project Payload、managed installation manifest、Codex/Cursor/Claude Code 项目 MCP 和 binary 升级规则详见 [14_本地MCP_Runtime分发与原文上下文加载.md](14_本地MCP_Runtime分发与原文上下文加载.md)。

## 1. 何时读取

出现以下任务时必须读取本文件：

- 首次把 Agent_Skills 接入目标项目；
- 用新 Release 升级目标项目中的 Agent_Skills；
- 目标项目缺少根 `AGENTS.md`，需要建立项目 Overlay；
- 目标项目已有 `AGENTS.md`，需要安全补充/升级 Agent Skills managed block；
- 修复或审查 AGENTS managed block、Bootstrap 行为；
- 修改唯一 `.agents/skills/ROUTER.md` 的项目安装/Bootstrap 可达性；
- 修改正式 Skill 或 Skills 根级 shared runtime file 的 Project Payload 安装边界；
- 判断哪些 `.agents` 内容属于 Agent_Skills 受管内容，哪些属于目标项目自有状态；
- 修改项目 Runtime、ownership manifest、宿主 MCP 配置或安装回滚。

普通只读分析、Review、文档审计或功能开发，如果用户没有授权项目规则写入，不因为发现 `AGENTS.md` 缺失就自动创建或修改文件。权限边界仍按 Coding 主规则执行。

## 2. 固定边界：分发 Skill，不复制源仓库 Bootstrap / Maintenance

Agent_Skills 源仓库根 `AGENTS.md` 是源码直读/维护模式的薄 Bootstrap，`.agents/MAINTENANCE.md` 只负责维护 Agent_Skills 源仓库本身。二者都**禁止直接复制成目标项目根 `AGENTS.md`**。

目标项目安装后的跨 Skill 路由统一读取：

```text
.agents/skills/ROUTER.md
```

Router 是整个 Skill 系统的 Skills 根级 shared runtime file，不属于 `coding` 或其他任一 Skill，也不是第五个 Skill。

正式 Skill 从：

```text
.agents/skills/<skill-name>/SKILL.md
```

动态发现。当前仓库实际存在 `coding`、`review`、`docs`、`figma`，但这些名称不是安装器/Runtime 的永久白名单；当前 Catalog 的可读导航由唯一 Router 展示，不要求 Bootstrap 再维护第二份列表。

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
.agents/skills/ROUTER.md
.agents/skills/<Runtime manifest 明确认领的正式 Skill>/
```

`.agents/runtime/` 是项目本地 Runtime，应被目标项目 `.gitignore` 忽略；install manifest 只承担 Agent_Skills ownership/version 导航，不是项目业务事实源。

### 普通 Runtime 与源仓库 Mutation 边界

**普通 Runtime** 的 `AGENTS` managed block 和共享 Router 只承担目标项目正常研发入口：项目事实优先、动态 Skill 导航、Reference 加载、专业 Skill Handoff、失败停止和权限边界。它们不承载 **源仓库 Mutation**、canonical repository、源仓库 Maintenance 或跨仓库同步等维护者专用治理。

源仓库中针对 Skill / Reference 的新增、修改、删除、重命名、拆分、合并、通用化和跨仓库同步，由 Agent_Skills 根 `AGENTS.md` 识别维护意图，再进入 `.agents/MAINTENANCE.md`、Coding 与 ref16。普通目标项目只需要知道：安装器 manifest 明确认领的 `.agents` 运行资产不是项目自有规则，不应直接手工修改；项目自己的长期规则继续写在项目自己的正式事实源中。

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

当前 Project Payload 使用 v2，install manifest 使用 v3 `managed_files` 逐文件 ownership。安装器只兼容读取旧 v2 manifest 作为一次性迁移输入；v1、未知或损坏 schema 直接失败，不猜测 ownership。

Runtime binary 负责：

1. 校验自身内嵌 Reference Bundle 与 Project Payload；
2. 读取动态正式 Skill Catalog，以及 Project Payload 显式 `shared_files`；
3. 读取旧 `.agents/agent-skills-install.json`：v3 只认领 `managed_files`，v2 只允许已认领 Core/shared 同名升级与可识别旧 Stub 清理；
4. 首次安装遇到未被认领的同名 Skill 或同名 shared file 时 fail closed；
5. 预检并逐文件更新新受管 Core/shared files，其中唯一 Router 为 `.agents/skills/ROUTER.md`；
6. 安装/升级项目 `.agents/runtime/agent-skills-mcp[.exe]`；
7. 创建或安全增量更新根 `AGENTS.md`，managed block 只指向项目内 Router；
8. 增量更新 `.gitignore`；
9. 建立 Codex / Cursor / Claude Code 项目级 MCP 入口和必要 bridge；
10. 写入新的 managed installation manifest；
11. 任一步失败时按安装前快照恢复本轮 touched managed files、可识别旧 Stub、Runtime、manifest 和受管文本。

目标项目不安装 canonical Reference 或 Stub；Runtime Mode 由 Router/Skill 先取得公共 route contract、提交中文 Task Route，再按不透明路由令牌加载当前 required 的完整 canonical Context。

## 4. Bootstrap 与 Router 的唯一事实源

三个入口职责必须分开：

```text
coding/assets/AGENTS.template.md
→ 目标项目原本没有 AGENTS.md 时的项目 Overlay 外层模板

coding/assets/AGENTS.managed.md
→ 写入目标项目 AGENTS.md 的薄 Bootstrap
→ 只负责项目事实优先 + 指向唯一 Router + Router 不可用时 fail closed

.agents/skills/ROUTER.md
→ Skills 根级 shared runtime file
→ 唯一完整 Skill Catalog / Router
→ 负责 Coding 锚点、Reference 加载、Figma/Review/Docs Handoff、失败和权限边界
```

Runtime binary 和源码维护用 Coding Bootstrap 都使用这套同源语义，不维护第二套项目路由。`AGENTS.managed.md` 不能重新复制 Router 详细正文；Router 也不能复制各专业 Skill 的完整细则。

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

这是源仓库维护入口，不是最终用户安装通道。正式 Runtime 安装已经通过 Project Payload v2 保证 Router 与 Coding 同版本落地；手工使用这个 helper 时仍必须先确认目标项目已经具备本 Release 的 `.agents/skills/ROUTER.md` 与 Coding Skill。

## 5. 目标项目没有 AGENTS.md

没有根 `AGENTS.md` 时，使用 `coding/assets/AGENTS.template.md` 创建项目 Overlay 初版。

初版必须包含：

1. Agent Skills managed block；
2. managed block 指向项目内已经安装的 `.agents/skills/ROUTER.md`；
3. 项目 Overlay 的维护边界；
4. 初始化时真实存在的项目规则、Manifest/Lock/Build、需求/Spec、Contract/Schema、Migration、README/Architecture/Documentation 等事实入口导航；
5. 明确“事实入口存在”不等于“已经确认某个框架、数据库或架构”；
6. 项目特殊约束应由项目自己的规则/事实源维护。

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

`coding/assets/AGENTS.managed.md` 是 managed block 唯一模板事实源，但它现在只承担**薄 Bootstrap**。至少保持：

1. 项目自己的规则和真实事实优先；
2. 明确读取 `.agents/skills/ROUTER.md`；
3. 由 Router 决定本次 Skill / Reference 加载，不在 block 内复制第二套详细路由；
4. 通用示例不能覆盖目标项目事实；
5. 明确安装器认领的 `.agents` 受管运行资产不是项目自有规则，不直接手工修改，项目长期规则维护在项目自身正式事实源；
6. Router 缺失、不可读或与更高优先级规则存在无法安全解析的冲突时明确报告并停止依赖它的动作，不假装遵守。

原 managed block 曾直接承担的 Coding 锚点、Reference 触发、Runtime Task Route → required Context、Figma NOT_READY/READY Handoff、Review、Docs、Skill/Reference 失败停止、CI/Branch Protection/PR/Release/Migration/安全与授权边界、项目事实来源等完整可执行语义，已经按内容守恒迁入 `.agents/skills/ROUTER.md`，该 Router 是这些跨 Skill 语义的唯一正文 Owner。本 Reference 只定义 Bootstrap Contract，不再复制第二份 Router 正文。

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

动态发现回答“Release 有哪些正式 Skill”；目标项目可写边界由 install manifest v3 的 `managed_files` 决定。`skills` 和 `shared_files` 只是公开导航，不能授权替换整个目录。

```text
managed_files
→ 相对 .agents/skills 的 Agent_Skills 受管文件
→ 新版本仍存在：原子升级
→ 新版本已删除：只删除该文件

同一 Skill 目录内未认领的 Reference / asset / 项目文件
→ 项目自有
→ 永远不因普通升级删除
```

当前 shared file 仍只有 `ROUTER.md`。首次安装若目标已有同名正式 Skill 目录或 Router 且没有合法 manifest 证明 ownership，必须在任何写入前 fail closed；禁止通过文件名、内容相似或 hash 猜归属。

v2→v3 时，旧 v2 manifest 只证明其 Skill Core/shared file 的历史受管边界；`references/` 只清理具备旧 Runtime 固定 Stub 标记的文件。其他项目自有 Reference、Skill 和 `.agents` 内容保留。迁移成功后全部后续升级只按 v3 `managed_files`。

## 10. 安全与原子性

安装/Bootstrap 修改研发治理入口，失败边界必须严格：

- 目标 `.agents`、受管文件、Runtime、AGENTS/宿主配置路径出现符号链接时拒绝越界修改；
- Project Payload 先校验 schema、`skills`、`shared_files`、path / SHA / size / mode / `payload_digest`；
- Project Payload v2 必须明确包含 `shared_files: ["ROUTER.md"]` 和对应 `ROUTER.md` 条目，避免生成悬空导航；
- 首次同名未认领 Skill/shared file/managed file 冲突在目标写入前发现；
- 不移动或替换整棵 Skill 目录，只逐文件原子写入；
- 写入前保存全部 touched managed files、旧 Stub、Runtime、manifest 和受管文本的 bytes/权限快照；
- AGENTS、`.gitignore`、CLAUDE/Codex marker 和 JSON MCP 配置在写入前先验证编码/结构；
- 单文件写入使用同目录临时文件 + 原子替换；
- 任一步异常时恢复本轮 touched files、旧 Stub、Runtime、manifest 和受管文本快照；
- 禁止用 `git reset --hard`、`git clean`、强制推送或历史重写实现安装回滚。

安装器不承诺普通文件系统跨多文件具备数据库式事务，但必须把可预检错误尽量前移，并把修改限制在可审计 managed 边界。

## 11. Greenfield 与已有项目

Greenfield / 空仓库：

```text
安装当前 Release shared Router + 正式 Skill
→ Bootstrap 创建 AGENTS.md
→ managed block 指向项目内 .agents/skills/ROUTER.md
→ 只列真实事实入口或明确当前未发现
→ 建立项目 MCP/宿主入口
→ Router → Coding 按 Greenfield 规则确认目标、硬约束和最小工程基线
```

已有 v3 安装项目或可安全迁移的 v2 项目：

```text
依据 v3 managed_files 逐文件升级；v2 只清理可识别旧 Stub
→ 保留项目自有 Skill、Reference、未认领文件和其他 .agents 内容
→ 保留已有 AGENTS 原文
→ 追加/升级 managed block
→ managed block 继续指向当前 Release Router
→ 只更新 Agent_Skills 自管宿主边界
→ Router → Coding 继续以已有项目规则和真实实现为准
```

旧 schema/旧 Router 路径不在本版本兼容范围内，不自动迁移。Bootstrap 不是自动架构设计器。

## 12. 有证据的项目 Overlay 语义补全

如果当前任务本身就是“安装 / 初始化 Agent_Skills、创建或完善项目 AGENTS”，且用户授权修改项目规则，Coding Agent 在确定性 Bootstrap 后还要判断是否需要有证据的语义补全：

1. 重新读取 Bootstrap 后的项目 `AGENTS.md`；
2. 只读取与长期研发导航直接相关的最少充分事实源；
3. 可确认的长期事实可以在 managed block **之外**增量补充；
4. 已有内容不重复、不改写，不为了风格统一重排；
5. 不能仅凭文件名/目录名写入框架、数据库、架构、Owner、Contract、CI 或部署结论；
6. 多个事实源冲突时继续核实，不猜一个正确；
7. 不修改 managed block 内模板文本；
8. 不把 Router 专业路由正文复制到项目 Overlay；
9. Runtime binary 本身不调用 LLM 自动生成项目架构结论。

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
- 动态正式 Skill 都安装，且 `.agents/skills/ROUTER.md` 不被误识别成 Skill；
- 目标 Project Payload 不出现 canonical Reference 或 Stub；
- Project Payload `shared_files` 显式认领 `ROUTER.md`，该文件原样进入目标项目；
- 目标项目 managed block 指向这个真实存在的 Router，且不复制完整 Router；
- install manifest v3 显式认领 `managed_files` 与 `shared_files`；
- 同名未认领 shared Router 在任何目标写入前 fail closed；
- Router/Runtime/manifest 后续失败可以恢复旧受管状态；
- v2 只按固定标记清理旧 Stub，项目自有 Reference/资产保留；v1/未知 schema 明确拒绝；
- Coding Python helper 作为 Project Payload 正式运行资产继续安装；
- `.agents/runtime/` 和 install manifest 正确；
- AGENTS 用户原文/managed marker 正确；
- 项目自有 Skill 和未认领根级文件保留；
- 同名未认领 Skill 冲突 fail closed；
- 删除旧受管项只依据旧 v3 `managed_files`，v2 例外只限可证明旧 Stub；
- Codex/Cursor/Claude 配置保留其他用户内容；
- 项目内 Runtime 通过真实 stdio MCP smoke；
- 安装失败可恢复本轮受管变化。

任何“安装完成”结论都必须来自本轮实际验证，不能用代码阅读或 Python 模块单测替代最终平台 artifact 证据。
