# Agent Skills Full Distribution Kit

这份文档面向**直接使用完整 Markdown Skill 的使用者**。Full Distribution Kit 不要求访问 Agent_Skills 源仓库，也不要求安装本地 MCP Runtime；它把当前版本的 `coding / review / docs` 三个完整 Skill 连同目标项目安装器一起分发。

## 1. 你会拿到什么

正式 GitHub Release 中的 Full Kit 文件名：

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
└── .agents/
    ├── README.md
    └── skills/
        ├── coding/
        ├── review/
        └── docs/
```

其中三个 Skill 都包含完整 `SKILL.md`、references、assets、scripts 和项目实际需要的 Skill 资源；不会把 canonical Reference 替换成 Runtime Stub。

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

安装器只管理目标项目中的：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

它不会把 Full Kit 自己的仓库维护状态复制进目标项目，也不会删除目标项目已有 `.agents/changes/`、项目自有 Skill 或其他 `.agents` 内容。

安装完成后还会调用刚安装的 Coding Bootstrap：

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
→ 适用时 Review / Docs
```

## 3. 重复执行就是升级

拿到新版本 Full Kit 后，在同一个目标项目重新运行同一条安装命令即可升级三个受管 Skill：

```bash
python scripts/install.py --target <目标项目根目录> --json
```

升级时：

- 三个受管 Skill 更新到当前 Full Kit 版本；
- 目标项目 `AGENTS.md` managed block 更新到当前模板；
- managed marker 外的项目原文保留；
- 目标项目 `.agents/changes/` 和项目自有 Skill 保留；
- Bootstrap 或 Skill 切换失败时按安装器回滚逻辑恢复本轮受影响的受管 Skill。

不要在目标项目里私自修改三个受管 Skill 后再期待下一次升级保留这些改动；项目自己的长期约束应写在项目 `AGENTS.md` 的项目维护区域或项目正式事实源中。

## 4. 校验正式 Release

正式 Release 同时提供 `SHA256SUMS`。下载 ZIP 后先核对：

```text
下载的 ZIP SHA256
=
SHA256SUMS 中同名文件的值
```

然后再解压、安装。

`agent-skills-full-kit.json` 还记录：

- Kit schema；
- `release_version`；
- 三个受管 Skill；
- 每个 payload 文件的路径、大小和 SHA256。

这些元数据用于审计分发内容；安装器仍以解压后的实际文件和目标项目当前事实工作。

## 5. Full 模式与 Runtime 模式怎么选

选择 Full Kit，当你更看重：

- 安装链最简单；
- Agent 可以直接读取完整 references；
- 不需要提高 Reference Markdown 的浏览/复制门槛。

如果希望目标项目只保留 Native Core `SKILL.md` + Reference Stub，并让详细 Reference 通过本地 MCP 在运行时加载，应改用与你操作系统对应的 Runtime Kit：

```text
agent-skills-mcp-runtime-kit-v<VERSION>-linux.zip
agent-skills-mcp-runtime-kit-v<VERSION>-windows.zip
agent-skills-mcp-runtime-kit-v<VERSION>-macos.zip
```

Runtime Kit 的安装、MCP 注册、升级和回滚以该 Kit 自带 `README.md` 为准。不要把 Full Kit 与 Runtime Kit 的安装步骤混在同一个目标项目升级过程中。

## 6. 回滚

正式 Release 的 tag 和资产是历史事实。需要回滚时：

1. 找到要恢复的旧版本 Full Kit；
2. 校验该版本 `SHA256SUMS`；
3. 对目标项目重新执行旧 Kit 的 `scripts/install.py`；
4. 检查目标项目 `AGENTS.md` managed block 和三个受管 Skill；
5. 用一个真实研发任务确认 Coding → reference → Review/Docs 路由仍正常。

不要通过修改旧 Release 资产或移动旧 tag 来伪造回滚；修正版使用新的产品版本。

## 7. 当前边界

Full Kit 是**分发产品**，不是 Agent_Skills 源仓库的开发快照。因此它不提供 Runtime Builder、Release Workflow、Change Archive 或仓库维护脚本。需要维护/开发 Agent_Skills 本身时应使用正式源仓库；需要直接接入目标项目时使用本 Kit 即可。
