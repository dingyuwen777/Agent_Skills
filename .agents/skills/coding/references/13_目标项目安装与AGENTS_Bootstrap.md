# 目标项目安装与 AGENTS Bootstrap

这份规则处理一个边界：**如何把 Agent_Skills 安装/升级到目标项目，并建立目标项目自己的 `AGENTS.md` Overlay，使后续研发会话能够稳定进入 Coding 并按实际任务继续路由其他正式 Skill。**

它不规定目标项目必须使用什么语言、框架、数据库、目录、CI 或部署方式，也不替代目标项目已有规则。

当前存在两类安装通道：

```text
Runtime binary（最终团队用户推荐）
→ 使用者只拿对应平台 agent-skills-mcp[.exe]
→ 在目标项目根运行
→ 项目级安装 Runtime + 全部正式 Skill Project Payload + Stub + AGENTS + 宿主配置

Full/source 安装（维护者 / 明确允许 Reference 明文的环境）
→ 从 Agent_Skills 源或 Full Kit 运行 scripts/install.py
→ 完整复制动态发现的正式 Skill，包括 canonical References
→ 执行 Coding Bootstrap
```

Runtime 的加密、Project Payload、managed installation manifest、Codex/Cursor/Claude Code 项目 MCP 和 binary 升级规则详见 [14_本地MCP_Runtime分发与原文上下文加载.md](14_本地MCP_Runtime分发与原文上下文加载.md)。

## 1. 何时读取

出现以下任务时必须读取本文件：

- 把 Agent_Skills 首次接入一个目标项目；
- 目标项目已经有 `.agents/skills/`，需要升级到当前 Agent_Skills 版本；
- 目标项目缺少根 `AGENTS.md`，需要建立项目 Overlay；
- 目标项目已有根 `AGENTS.md`，需要补充或升级 Agent_Skills 研发入口；
- 修复或审查 Agent Skills managed block、安装器、Bootstrap 行为；
- 修改正式 Skill 的发现/安装边界；
- 需要判断哪些 `.agents` 内容属于 Agent_Skills 受管内容、哪些属于目标项目自有状态；
- 需要确认 Runtime binary 与 Full/source 安装对 AGENTS 的行为是否一致。

普通只读分析、代码 Review、文档审计或功能开发，如果用户没有授权项目规则写入，不因为发现 `AGENTS.md` 缺失就自动创建或修改文件。权限边界仍按 Coding 主规则执行。

## 2. 固定边界：分发 Skill，不复制 Agent_Skills 仓库自身 Overlay

Agent_Skills 源仓库根 `AGENTS.md` 只用于维护 Agent_Skills 自身，**禁止直接复制成目标项目根 `AGENTS.md`**。

正式 Skill 集合不得静态写死为 `coding/review/docs`。构建/安装时从：

```text
.agents/skills/<skill-name>/SKILL.md
```

动态发现全部正式 Skill。当前仓库实际存在 `coding`、`review`、`docs`，以后新增合法正式 Skill 后应自动进入分发，不要求修改安装器名单。

目标项目中的下列内容不是普通安装器的清理目标：

```text
.agents/changes/
.agents/project-context.json
.agents/skills/<项目自有 Skill>/
.agents/<其他项目自有内容>/
AGENTS.md managed marker 外文本
```

其中 `.agents/project-context.json` 是本地可失效缓存，应忽略 Git。安装器不得把源仓库缓存复制到目标项目，也不得为了升级主动删除目标项目已有缓存。

Runtime binary 还会安装项目本地：

```text
.agents/runtime/agent-skills-mcp[.exe]
.agents/agent-skills-install.json
```

前者是本地 Runtime，应被目标项目 `.gitignore` 忽略；后者只承担 Agent_Skills 安装 ownership/version 导航，不是项目业务事实源。

## 3. 推荐最终用户入口：项目级单 binary

最终团队使用者不需要访问 `Agent_Skills` 源仓库，也不需要 Python、pip、venv 或外部安装脚本。

Windows：

```powershell
cd D:\work\MyProject
.\agent-skills-mcp.exe
```

Linux/macOS：

```bash
cd /work/MyProject
chmod +x ./agent-skills-mcp   # 下载后缺少执行位时执行一次
./agent-skills-mcp
```

无参数运行等价于安装/升级当前工作目录。也可以显式：

```text
agent-skills-mcp install --target <目标项目根目录>
```

Runtime binary 负责：

1. 校验自身内嵌 Reference Bundle 与 Project Payload；
2. 读取动态正式 Skill Catalog；
3. 读取旧 `.agents/agent-skills-install.json`，只把旧 manifest 明确认领的 Skill 当成 Agent_Skills 自有；
4. 首次安装遇到未被认领的同名 Skill 时 fail closed；
5. 暂存全部新受管 Skill；
6. 安装/升级项目 `.agents/runtime/agent-skills-mcp[.exe]`；
7. 创建或安全增量更新根 `AGENTS.md`；
8. 增量更新 `.gitignore`；
9. 建立 Codex / Cursor / Claude Code 项目级 MCP 入口和 Claude 的 `@AGENTS.md` bridge；
10. 写入新的 managed installation manifest；
11. 失败时按安装前快照恢复本轮已经切换的受管内容。

Runtime binary 目标项目里的 canonical Reference 只安装同名 Stub，正文不落盘。完整 Runtime 规则见 Reference 14。

## 4. Full/source 安装入口

维护 Agent_Skills 源仓库、调试 Full 分发，或明确允许完整 Markdown Reference 明文分发时，可以从源仓库或 Full Kit 执行：

```bash
python scripts/install.py --target <目标项目根目录>
```

安装器负责：

1. 动态发现 `.agents/skills/*/SKILL.md` 下全部正式 Skill；
2. 校验 Skill 结构和目标受管路径；
3. 先把全部正式 Skill 完整复制到目标项目 `.agents` 下的临时暂存区；
4. 暂存成功后才替换对应目标 Skill；
5. 目标项目其他 `.agents` 内容不删除、不清理；
6. Skill 切换后调用刚安装的 Coding CLI `bootstrap`；
7. Bootstrap 失败时恢复本次切换前的受管 Skill；
8. 安装成功后输出实际动态发现的 Skill 集合与 AGENTS/.gitignore 处理状态。

重复执行同一个命令就是升级入口。受管正式 Skill 以当前源/Full Kit 版本为准；目标项目对这些受管目录做的本地私改会在升级时被替换，因此项目特殊规则应写在目标项目 `AGENTS.md`、项目自己的 Skill/文档或正式治理载体中，不应偷偷修改受管通用 Skill 后期待升级保留。

手工复制正式 Skill 仍然允许，但复制完成后必须执行 Bootstrap，或以等价且有证据的方式建立目标项目 Overlay。

## 5. Bootstrap CLI

Full/source 安装后可在目标项目根运行：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

需要机器读取结果时：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root . --json
```

Runtime binary 不要求目标机器有 Python；它使用同一套 `AGENTS.template.md` / `AGENTS.managed.md` 语义直接执行确定性 Bootstrap。两种通道必须保持 AGENTS managed block Contract 一致，不能各维护一套不同项目规则。

Bootstrap 只负责确定性、可机械证明的内容：

- 创建或安全增量更新根 `AGENTS.md`；
- 创建或增量更新 `.gitignore`，确保显式忽略 `.agents/project-context.json`；
- Runtime binary 额外忽略 `.agents/runtime/`；
- 新建 `AGENTS.md` 时，根据当前扫描结果列出真实存在的高价值事实入口；
- 不根据这些入口猜测项目具体技术栈或架构。

Bootstrap **不会**：

- 自动创建 Change/RFC/ADR/OpenSpec；
- 自动修改 Schema/Migration；
- 自动决定框架、数据库、部署平台或 CI；
- 自动生成完整架构说明；
- 创建 `project-context.json`；
- 修改目标项目其他 `.agents` 内容；
- 代替 Coding Agent 对复杂项目语义做人工判断。

## 6. 目标项目没有 AGENTS.md

没有根 `AGENTS.md` 时，使用 `assets/AGENTS.template.md` 创建项目 Overlay 初版。

初版必须包含：

1. Agent Skills managed block；
2. 项目 Overlay 的维护边界；
3. 初始化时当前真实存在的项目规则、Manifest/Lock/Build、需求/Spec、Contract/Schema、Migration、README/Architecture/Documentation 等事实入口导航；
4. 明确说明“事实入口存在”不等于“已经确认某个框架、数据库或架构”；
5. 项目特殊约束维护位置。

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

## 7. 目标项目已经有 AGENTS.md

已有 `AGENTS.md` 是项目资产，必须优先保护原文。

Bootstrap 使用：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

作为唯一 AGENTS 自管边界。

### 7.1 当前没有 managed block

行为：

```text
已有 AGENTS.md 原始字节
→ 完整保留
→ 在文件末尾增加必要空行
→ 追加 Agent Skills managed block
```

不得为了统一格式重排标题、替换换行符、修正文案、压缩规则或格式化 marker 之外的已有内容。

### 7.2 已经有一个完整 managed block

行为：

```text
marker 前原文：逐字保留
managed block：替换为当前版本
marker 后原文：逐字保留
```

这使 Agent_Skills 升级可以更新自己负责的入口规则，而不认领项目自己的其他内容。

### 7.3 marker 损坏

以下情况必须失败：

- 只有 start，没有 end；
- 只有 end，没有 start；
- end 出现在 start 前；
- start/end 重复出现。

禁止猜测“哪一段可能是旧 block”后覆盖，因为错误猜测可能删除用户规则。应保留原文件不变并报告 managed marker 错误，由项目 Owner 先修复边界。

## 8. managed block 必须表达什么

`assets/AGENTS.managed.md` 是当前唯一模板事实源。它至少保持以下语义：

1. 项目规则和通用 Skill 的职责分离；
2. 每个研发任务先读适用项目规则；
3. 随后必须读取 `.agents/skills/coding/SKILL.md`；
4. Coding 命中的 Reference 必须按触发条件读取；
5. 安装、升级、创建/补充项目 `AGENTS.md` 或修复 managed block 时读取本 Reference；
6. Runtime 模式命中 Reference 时必须通过 Stub → MCP 取得 `canonical_text`，不能把 Stub 当正文；
7. 只读取当前任务直接相关事实；
8. Coding 要求 Review 且 Review Skill 存在时读取 `.agents/skills/review/SKILL.md`；
9. Coding 判断文档影响且 Docs Skill 存在时读取 `.agents/skills/docs/SKILL.md`；
10. 未来其他正式 Skill 的触发/路由以当前 Core Skill 和项目规则为准，不在 AGENTS 模板维护静态全集；
11. Skill 缺失、不可读、Runtime Reference 加载失败或规则冲突时明确报告，不假装遵守；
12. 不绕过目标项目已有 CI、Branch Protection、PR、Release、Migration、安全或其他门禁；
13. 语言、框架、数据库、架构、Contract、Schema、CI、部署等项目事实必须来自当前目标项目。

不要为了缩短 managed block 删除这些可执行语义。需要改模板时同时更新本 Reference、Runtime 安装测试、README，并做内容守恒 Review。

## 9. `.gitignore` 规则

所有目标项目应显式忽略：

```gitignore
.agents/project-context.json
```

Runtime binary 还应显式忽略：

```gitignore
/.agents/runtime/
```

原因：Runtime binary 是机器/平台本地运行资产，不应因为安装 Agent_Skills 就把几十 MB 平台二进制提交进业务仓库。

Bootstrap / Runtime installer：

- `.gitignore` 不存在：创建最小规则；
- 已显式存在等价规则：不重复追加；
- 已有其他规则：原内容保留，只在末尾增量追加；
- `.gitignore` 是符号链接或不是普通文件：拒绝修改；
- 不为了加入这几行重新排序、去重或格式化项目已有 `.gitignore`。

安装器不尝试实现完整 Git ignore 语义解析；它只保证项目文件中存在明确、可审计的本地 Runtime/缓存忽略项。

## 10. 项目自有 Skill 与 Agent_Skills ownership

动态发现正式 Skill 解决的是“Release 里有哪些 Agent_Skills”，不能反过来把目标项目 `.agents/skills/` 下所有目录都当成可覆盖内容。

Runtime 项目安装使用 `.agents/agent-skills-install.json` 记录旧版本明确认领的 Skill。规则：

```text
Release 新 Skill + 目标不存在
→ 安装

Release Skill + 旧 manifest 明确认领
→ 升级替换

旧 manifest 明确认领 + 新 Release 已删除
→ 可以删除旧受管 Skill

目标已有同名 Skill + 旧 manifest 未认领
→ 项目自有/归属不明
→ 首次安装 fail closed

目标其他不同名 Skill
→ 永远不因普通 Agent_Skills 升级而清理
```

Full/source 安装没有 Runtime managed manifest 的同等历史 ownership 能力时，仍只能管理本次动态发现的同名正式 Skill，不能清空整个 `.agents/skills/`。如果目标已有同名 Skill 且归属不明确，执行者必须按当前授权和项目事实处理，不能借“升级”名义删除用户资产。

## 11. 安全与原子性

安装/Bootstrap 修改的是研发治理入口，失败边界要比普通文本复制严格：

- 目标 `.agents`、`.agents/skills`、受管 Skill、Runtime 目录、AGENTS/配置目标路径出现符号链接时拒绝越界修改；
- Skill 必须先完整暂存，再替换现有受管目录；
- Runtime Project Payload 必须先校验 path / SHA / size / mode；
- 首次同名未认领 Skill 冲突必须在目标写入前发现；
- 任一 Skill 切换失败时恢复当前项和此前已经切换的受管 Skill；
- Skill 已切换但 AGENTS/Runtime/宿主配置写入失败时恢复本轮可恢复快照；
- Bootstrap 在任何写入前先验证已有 `AGENTS.md` marker、AGENTS 文本编码和 `.gitignore` 文本编码；
- Runtime 项目安装还要预检 CLAUDE/Codex marker 和 JSON MCP 配置；
- 单文件写入使用同目录临时文件 + 原子替换；
- 不使用 `git reset --hard`、`git clean`、强制推送或其他破坏性方式实现安装。

安装器不能保证多个普通文本文件之间具有数据库式事务，但必须把可预先验证的错误在写入前发现，并把修改限制为可明确审计的 managed 边界。

## 12. Greenfield 与已有项目的差异

Greenfield / 空仓库：

```text
安装当前 Release 的全部正式 Skill
→ Bootstrap 创建 AGENTS.md
→ 只列出现有事实入口或明确当前未发现
→ Runtime 模式建立项目 MCP/CLAUDE bridge
→ 后续 Coding 按 Greenfield 规则确认目标、硬约束和最小工程基线
```

已有项目：

```text
安装/升级受管正式 Skill
→ 保留项目自有 Skill 和其他 .agents 内容
→ Bootstrap 保留已有 AGENTS 原文
→ 追加/升级 managed block
→ Runtime 模式只更新自己认领的 MCP/CLAUDE/Codex 边界
→ 后续 Coding 继续以已有项目规则和真实实现为准
```

Bootstrap 不是“自动架构设计器”。即使目标项目已经很复杂，也不把一次文件扫描结果自动写成权威架构结论。

## 13. Coding Agent 的项目 Overlay 语义补全

确定性 Bootstrap 的职责是保证**第一次接入安全、可重复、不会猜项目事实**。它生成的是可以立即工作的初版 Overlay，不代表项目语义已经被完整整理。

如果当前任务本身就是“安装 / 初始化 Agent_Skills、创建或完善目标项目 `AGENTS.md`”，并且用户已经授权修改项目规则，则执行该任务的 Coding Agent 在 Bootstrap 后还必须判断目标项目 Overlay 是否需要**有证据的语义补全**：

1. 重新读取 Bootstrap 后的目标项目 `AGENTS.md`，不要从模板反推项目事实；
2. 按项目发现规则只读取与长期研发导航直接相关的最少充分事实源，例如现有 `CONTRIBUTING`、根 README、Manifest/lock、版本文件、CI、正式架构/Spec/Contract/Schema/Migration 入口和真实代码目录；
3. 能从当前仓库直接确认的长期事实，可以在 **managed block 之外的项目自有区域**增量补充，例如真实 Runtime/包管理器入口、正式测试/构建入口、关键文档导航或项目已经明确的特殊约束；
4. 已有 `AGENTS.md` 已经清楚表达的内容不重复、不改写措辞，不为了统一风格重排原文；新增内容只补真实缺口；
5. 不能仅凭文件名、目录名或常见实践写入框架、数据库、架构、模块职责、Owner、Contract、CI 语义或部署结论；需要读内容和必要调用链才能确认；
6. 发现多个事实源互相矛盾时，不把某一个猜成正确答案；记录冲突并按 Coding 的事实优先级继续核实，只有需要 Owner/用户作出的真实上游决策才提请确认；
7. 语义补全不得修改 `<!-- agent-skills:managed:start -->` 与 `<!-- agent-skills:managed:end -->` 内的受管文本；该区域只由当前模板/Bootstrap 更新；
8. Runtime binary 本身只做确定性 Bootstrap，不调用 LLM 替使用者自动生成项目架构结论；需要语义补全时由后续实际 Coding Agent 基于目标项目事实执行。

这一步是“有证据的项目导航补全”，不是第二套项目架构文档。长期项目事实仍由当前项目自己的正式文件和机器实现负责。

## 14. 宿主差异不改变 AGENTS 事实源

Runtime binary 可以为不同宿主生成薄项目级配置，但不能为每个宿主复制一套研发规则：

```text
Codex
→ .codex/config.toml 项目 MCP
→ 项目 trust 由 Codex 自己决定

Cursor
→ .cursor/mcp.json 项目 MCP

Claude Code
→ .mcp.json 项目 MCP
→ CLAUDE.md 中 @AGENTS.md bridge
```

这些配置只是让宿主找到项目 Runtime。研发规则仍从同一个 `AGENTS.md`、Native Core Skill 和 Runtime Reference 原文链进入。

宿主已有同名 `agent-skills` MCP 配置但不属于 Agent_Skills managed ownership 时，安装器必须拒绝静默覆盖。宿主要求首次 trust/approval 时，安装器不得绕过。

## 15. 验证安装/Bootstrap

至少按当前安装通道验证：

### Runtime binary

- 最终平台 artifact `status/self-test`；
- 在真实临时项目运行 binary，无 Python/源仓库依赖；
- 无参数当前目录安装；
- 显式 `install --target`；
- 重复升级幂等；
- 动态正式 Skill 都安装；
- canonical Reference 目标只出现 Stub；
- `.agents/runtime/` 和 install manifest 正确；
- AGENTS 用户原文/managed marker 正确；
- 项目自有 Skill 保留；
- 同名未认领 Skill 冲突 fail closed；
- 删除旧受管 Skill 只依据旧 manifest；
- Codex/Cursor/Claude 项目配置保留其他用户内容；
- 项目内 Runtime 能通过真实 stdio MCP smoke。

### Full/source

- 动态正式 Skill 全部复制；
- canonical References 保持完整 Markdown；
- Bootstrap 创建/更新 AGENTS；
- `.agents/changes/`、缓存、项目自有 Skill 和其他 `.agents` 内容不被清理；
- 重复安装幂等；
- Bootstrap 失败恢复本轮受管 Skill。

任何“安装完成”结论都必须来自本轮实际验证，不用单元测试或代码阅读替代最终平台 artifact 证据。
