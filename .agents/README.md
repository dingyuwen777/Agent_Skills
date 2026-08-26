# `.agents` 使用说明

`.agents/` 保存 Agent 工作流能力和本地辅助状态，不是产品业务代码目录，也不是另一套项目架构。

当前通用 Skills：

```text
.agents/skills/
├── coding/
├── review/
└── docs/
```

## 1. 三个 Skill 的职责

| Skill | 主要职责 |
| --- | --- |
| `coding` | 事实恢复、任务路由、需求/设计、开发、调试、验证、CI、Git、Release、交付 |
| `review` | 独立审查、Findings、测试充分性、主动验证、re-review |
| `docs` | 文档事实同步、审查、编写、更新和可读性治理 |

正常协作：

```text
项目本地规则
→ Coding 恢复事实和风险
→ 实现/验证
→ Docs Impact（有影响时进入 Docs）
→ 完成前 Review（有 Review Skill 时进入 Review）
→ PR / CI / Delivery
```

显式 Code Review / Audit：

```text
项目本地规则
→ Coding 只完成仓库事实、工具链、风险和权限路由
→ Review 成为主要工作流
```

文档任务：

```text
项目本地规则
→ Docs Review Only / Review + Fix / Write / Update
```

如果项目本地规则要求所有任务统一从 Coding 进入，则先遵守该 Overlay；这不表示 Coding 代替 Docs 写文档。

## 2. 项目 Overlay

目标项目可以有自己的 `AGENTS.md`、`CONTRIBUTING`、Spec、ADR 和 CI 规则。这些项目事实优先决定：

- 实际语言/Runtime/Compiler；
- Manifest/锁文件/包管理器；
- 架构、目录和模块边界；
- Contract/Schema/Migration；
- 数据库/外部依赖；
- 测试/构建/发布命令；
- Branch Protection/Release/部署流程。

通用 Skill 不反向假设这些事实。

## 3. `project-context.json`

```text
.agents/project-context.json
```

是目标项目本地可失效导航缓存：

- 不提交 Git；
- 不保存需求正文或架构结论；
- 当前仓库事实和运行结果优先；
- 每个独立任务开始、切换分支、同步/rebase 或候选事实源变化后重新检查；
- 只读任务未经写入授权时不创建缓存。

创建/刷新：

```bash
python .agents/skills/coding/scripts/coding.py discover --root .
```

## 4. Change

Coding 自带的当前 Change schema 是 `coding-change/v1`，不兼容旧 schema。

Change 的语义是需求、验证和完成门禁，不代表所有项目必须使用同一目录。项目已有正式治理体系时优先复用；使用 Coding 自带载体时默认放在 `.agents/changes/`，已有受支持的顶层 `changes/` 时可继续沿用。

常用命令：

```bash
python .agents/skills/coding/scripts/coding.py status --root .
python .agents/skills/coding/scripts/coding.py conflicts --root . --json
python .agents/skills/coding/scripts/coding.py new-change --help
python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

## 5. 正式规则在哪里

```text
Coding
→ skills/coding/SKILL.md
→ skills/coding/references/

Review
→ skills/review/SKILL.md
→ skills/review/references/

Docs
→ skills/docs/SKILL.md
→ skills/docs/references/
```

各 README 只负责说明“怎么使用”，不能替代正式规则。
