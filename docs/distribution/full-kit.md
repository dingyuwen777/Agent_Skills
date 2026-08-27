# Agent Skills Full Distribution Kit

这份文档面向**明确允许直接持有完整 Markdown Skill / canonical Reference 正文的使用者和维护者**。Full Distribution Kit 不要求安装本地 MCP Runtime；它把当前版本动态发现的全部正式 Skill 连同目标项目安装器一起分发。

**安全边界先说明：** Full Kit 包含 canonical `references/*.md` 明文，因此当前团队 Runtime 正式 GitHub Release **不默认发布 Full Kit**。团队成员只拿单平台 `agent-skills-mcp` binary 的分发方式见 [`runtime-kit.md`](runtime-kit.md)。需要生成或单独授权分发 Full Kit 时，由维护者显式执行 Builder，并自行控制资产访问范围。

## 1. 你会拿到什么

维护者构建入口：

```bash
python scripts/build_full_distribution.py --output-dir dist --json
```

输出文件名：

```text
agent-skills-full-kit-v<VERSION>.zip
```

解压后：

```text
agent-skills-full-kit-v<VERSION>/
├── README.md
├── VERSION
├── agent-skills-full-kit.json
├── scripts/
│   └── install.py
├── runtime/
│   └── agent_skills_runtime/    # 仅安装器需要的动态 Catalog/Payload helper
└── .agents/
    ├── README.md
    └── skills/
        ├── coding/
        ├── docs/
        ├── review/
        └── <当前版本其他正式 Skill>/
```

正式 Skill 不是固定三项。Builder 从：

```text
.agents/skills/*/SKILL.md
```

动态发现全部合法 Skill，因此未来新增 `security`、`testing` 等正式 Skill 后会自动进入 Full Kit。

Full Kit 中每个正式 Skill 都保留完整 `SKILL.md`、canonical `references/`、assets、scripts 和其他源分发所需资源；不会把 Reference 替换成 Runtime Stub。

Full Kit 不携带 Agent_Skills 源仓库自己的：

- 根 `AGENTS.md`；
- `.agents/changes/`；
- `.agents/project-context.json`；
- Git 历史、PR 状态或其他仓库维护状态。

## 2. 安装到目标项目

假设已经把 ZIP 解压，并且目标项目根目录是：

```text
D:\work\MyProject
```

Windows：

```powershell
python .\scripts\install.py --target "D:\work\MyProject" --json
```

Linux / macOS：

```bash
python3 ./scripts/install.py --target /work/MyProject --json
```

Full/source 安装器动态管理**当前 Kit 中全部正式 Skill**，但不会把 Full Kit 自己的仓库维护状态复制进目标项目，也不会清理目标项目已有 `.agents/changes/`、项目自有不同名 Skill 或其他 `.agents` 内容。

安装完成后调用刚安装的 Coding Bootstrap：

```text
目标项目没有 AGENTS.md
→ 创建项目自己的 AGENTS Overlay 初版

目标项目已有 AGENTS.md
→ 保留项目原文
→ 只增加或更新 Agent Skills managed block
```

managed block 会把后续研发任务路由到：

```text
目标项目规则
→ .agents/skills/coding/SKILL.md
→ 命中的 Coding references
→ 适用时 Review / Docs / 其他正式 Skill
```

## 3. 重复执行就是升级

拿到新版本 Full Kit 后，在同一个目标项目重新运行同一条安装命令：

```bash
python scripts/install.py --target <目标项目根目录> --json
```

升级时：

- 当前 Kit 动态发现的正式 Skill 更新到对应版本；
- 目标项目 `AGENTS.md` managed block 更新到当前模板；
- managed marker 外的项目原文保留；
- 目标项目 `.agents/changes/`、缓存和项目自有不同名 Skill 保留；
- Bootstrap 或 Skill 切换失败时按安装器回滚逻辑恢复本轮受影响的受管 Skill。

不要在目标项目里私自修改 Agent_Skills 受管 Skill 后期待下一次 Full 升级保留这些改动；项目自己的长期约束应写在项目 `AGENTS.md` 的项目维护区域、项目自己的 Skill 或正式事实源中。

Full/source 安装没有 Runtime managed installation manifest 那样完整的历史 ownership 能力。如果目标项目已经存在与当前 Kit 正式 Skill 同名但归属不明确的目录，执行者必须先确认授权/归属，不能借“Full 升级”名义清理项目资产。

## 4. Full Kit manifest

`agent-skills-full-kit.json` 记录：

- Kit schema；
- `release_version`；
- 动态正式 Skill 列表；
- `skill_count`；
- 每个 payload 文件的路径、大小和 SHA256。

这些元数据用于审计构建内容；安装器仍以解压后的实际文件和目标项目当前事实工作。

如果 Full Kit 通过受控渠道交付，分发者还应提供该 ZIP 的独立 checksum。不要把 Runtime 正式 Release 的 `SHA256SUMS` 当成未发布 Full Kit 的 checksum 事实。

## 5. Full 模式与 Runtime binary 怎么选

选择 Full Kit，当你明确接受：

- 使用者直接拿到 canonical Reference Markdown；
- 安装链依赖 Python；
- 不需要提高 Reference 的浏览/复制门槛；
- 使用环境和授权范围允许分发规则正文。

正式团队用户推荐 Runtime binary：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
```

Runtime binary：

- 不需要 clone Agent_Skills；
- 不需要 Python/pip/venv；
- 在目标项目根运行即可；
- 自动安装当前 Release 全部正式 Skill；
- canonical Reference 只落 Stub，正文通过项目本地 MCP 加载；
- 自动建立 Codex/Cursor/Claude Code 项目级 MCP。

不要把 Full Kit 与 Runtime binary 的安装步骤混在同一个普通升级流程里。选择哪条通道本身决定 canonical Reference 是否明文落盘。

## 6. 回滚

Full Kit 回滚：

1. 找到要恢复的旧版本 Full Kit；
2. 校验该受控分发资产的 checksum；
3. 对目标项目重新执行旧 Kit 的 `scripts/install.py`；
4. 检查目标项目 `AGENTS.md` managed block 和动态正式 Skill；
5. 用真实研发任务确认 Core → Reference → 其他 Skill 路由仍正常。

不要通过修改历史归档或移动历史 tag 来伪造回滚；正式修正版使用新产品版本。

Runtime binary 的项目级回滚方式不同，应按 `runtime-kit.md` 的 managed manifest / `source_digest` / `payload_digest` 规则执行。

## 7. 当前边界

Full Kit 是**完整 Markdown 兼容分发产品**，不是 Agent_Skills 源仓库开发快照，也不是当前团队 Runtime Release 的默认资产。

它不提供 Release Workflow、Change Archive 或完整仓库维护环境。需要维护/开发 Agent_Skills 本身时使用正式源仓库；需要保护 canonical Reference 并让团队只拿一个 binary 时使用 Runtime binary。
