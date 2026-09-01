from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    """只收敛一个已确认重复段，保持语义和失败边界。"""
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one target, got {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    ".agents/skills/router/SKILL.md",
    "不得使用历史聊天、摘要、旧缓存或目标项目中的安装副本替代当前 canonical 文件。**目标项目中的安装副本**包括 `agent-skills:managed` block、Runtime / Project Payload / Runtime Skill Projection、legacy install-state 和其他 installer-owned 运行资产；Source Mode 可以读取它们的 marker、ownership、安装版本或 drift 作为安装状态事实，但 **managed block 不作为当前通用治理语义来源**，其中旧版本 Runtime/MCP/披露/路由/加载说明不得覆盖当前 canonical Source。目标项目 marker 外的**项目自有规则**、Contract、Schema/Migration、CI、代码、测试、正式设计和其他真实项目事实仍必须正常读取和遵守。Source Mode 不启动用户电脑上的本地 Runtime，也不调用 Runtime MCP。",
    "不得使用历史聊天、摘要、旧缓存或**目标项目中的安装副本**替代当前 canonical 文件。Source Mode 下，安装副本（含 managed block 和受管 Runtime 资产）只表示安装/ownership/drift，**不作为当前通用治理语义来源**；**项目自有规则**和真实事实仍必须读取。Source Mode 不启动用户电脑上的本地 Runtime，也不调用 Runtime MCP。",
)

replace_once(
    ".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md",
    """固定顺序：

1. 重新读取安装/接入后的项目 `AGENTS.md` 以及适用的 `CONTRIBUTING` / 子目录规则；目标项目自己的 marker 外规则仍是项目规范，不能因 Source Mode 而跳过；
2. 如果当前是 **Source Mode**，先按 ownership 拆分 `AGENTS.md`：`agent-skills:managed` block 和目标项目 `.agents` 中 installer-owned Runtime / Project Payload / Runtime Skill Projection 属于**保留但非 canonical**的安装资产；可以检查 marker、ownership、**安装版本与 drift**，但**不得把其中的 Runtime/MCP/披露/路由/加载说明作为当前通用治理语义**；
3. Source Mode 发现目标项目安装资产与当前 canonical Source 存在 drift 时，只记录安装版本漂移及其影响，并明确后续应通过**正式 Runtime upgrade**收敛；Project Governance Bootstrap **不手工覆盖 installer-owned managed block**，也**不得复制或改写到项目 Overlay**。Runtime Mode 则继续按当前已安装 Release 的正式 Runtime 规则取得约束；
4. 做有界事实调查，只读取长期研发导航直接相关的最少充分代码、Manifest/lock、Contract/Schema/Migration、测试、CI、部署和正式文档；
5. 把现有 marker 外项目 AGENTS 内容与新证据分成**规范性规则、描述性事实、未确认事项**；
6. 规范性规则若与当前实现冲突，先视为实现/配置偏离；**不能通过修改 `AGENTS.md` 让错误实现合法化**，也不能因为代码没遵守就自动弱化规则；
7. **描述性事实**只有在当前机器事实/代码/CI/运行证据足以证明过时时才最小修正；不能仅凭文件名发明框架、数据库、架构、Owner、Contract、CI 或部署结论；
8. 高权威事实源冲突或证据不足时保留为**未确认事项**；重要 Contract/Schema/数据/安全/部署冲突继续核实或请求 Owner 决策；
9. 可确认长期事实只在 **managed block 外**增量补充，并使用当前项目自己的模块、Contract、Schema、测试、CI、部署、业务和设计术语表达；**项目 Overlay 只描述项目自己的规则、事实和长期工程边界，不解释通用治理能力自身如何运行，也不把治理能力自身的执行、分发或实现说明写入项目规范**；
10. 已有仍有效文本尽量保持原位置和语义，只做必要 targeted 修正；新模板没有真实事实的章节保持为空或明确未确认；
11. 首次治理成功后把项目自有状态更新为“状态：已校准”；
12. **重新读取最终 `AGENTS.md`**，确认项目规则、事实、未确认事项和 managed block 边界没有互相覆盖；
13. 回到用户原始请求并**继续原始研发任务**。""",
    """固定顺序：

1. 重新读取安装/接入后的项目 `AGENTS.md` 以及适用的 `CONTRIBUTING` / 子目录规则。**Source Mode** 下按 ownership 区分：marker 外项目规则照常生效；managed block 与 installer-owned Runtime 是**保留但非 canonical**的安装资产，只检查 marker、ownership、**安装版本与 drift**，**不得把其中的 Runtime/MCP/披露/路由/加载说明作为当前通用治理语义**；
2. 做有界事实调查，只读取长期研发导航直接相关的最少充分代码、Manifest/lock、Contract/Schema/Migration、测试、CI、部署和正式文档；
3. 把现有 marker 外项目 AGENTS 内容与新证据分成**规范性规则、描述性事实、未确认事项**；
4. 规范性规则若与当前实现冲突，先视为实现/配置偏离；**不能通过修改 `AGENTS.md` 让错误实现合法化**，也不能因为代码没遵守就自动弱化规则；
5. **描述性事实**只有在当前机器事实/代码/CI/运行证据足以证明过时时才最小修正；不能仅凭文件名发明框架、数据库、架构、Owner、Contract、CI 或部署结论；
6. 高权威事实源冲突或证据不足时保留为**未确认事项**；重要 Contract/Schema/数据/安全/部署冲突继续核实或请求 Owner 决策；
7. 可确认长期事实只在 **managed block 外**增量补充，并使用当前项目自己的模块、Contract、Schema、测试、CI、部署、业务和设计术语表达；**项目 Overlay 只描述项目自己的规则、事实和长期工程边界，不解释通用治理能力自身如何运行，也不把治理能力自身的执行、分发或实现说明写入项目规范**。Source Mode **不得复制或改写到项目 Overlay**；发现 drift 只报告**正式 Runtime upgrade**，**不手工覆盖 installer-owned managed block**；
8. 已有仍有效文本尽量保持原位置和语义，只做必要 targeted 修正；新模板没有真实事实的章节保持为空或明确未确认；
9. 首次治理成功后把项目自有状态更新为“状态：已校准”；
10. **重新读取最终 `AGENTS.md`**，确认项目规则、事实、未确认事项和 managed block 边界没有互相覆盖；
11. 回到用户原始请求并**继续原始研发任务**。""",
)

replace_once(
    ".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md",
    """- marker 外 Overlay 使用项目自身术语，不复制通用治理能力自身的执行、分发或实现说明；
- Source Mode 对目标项目旧 managed/Runtime 安装资产只读取 marker、ownership、安装版本与 drift，不把旧 Runtime/MCP/披露/路由/加载语义当作当前 canonical 规则；发现 drift 时报告正式 Runtime upgrade 需要，不手工改 installer-owned block；
- 安装失败和 rollback failure 都有可验证、可诊断结果。""",
    """- marker 外 Overlay 使用项目自身术语，不复制通用治理能力自身的执行、分发或实现说明；
- 安装失败和 rollback failure 都有可验证、可诊断结果。""",
)

replace_once(
    ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md",
    "Source Mode 是明文维护/直读模式；在用户已经有源码访问权时，可以正常显示正在读取哪个 Skill/Reference、具体路径、路由判断和维护过程，不应用 Runtime Mode 的用户可见隐藏策略伪装源码事实。**目标项目旧版本 Agent_Skills 安装资产**（包括 managed block、Runtime / Project Payload / Runtime Skill Projection 与 legacy install-state）只提供 marker、ownership、安装版本和 drift 事实，**不能作为 Source Mode 当前通用治理规则来源**；**项目自己的规则和真实事实仍必须读取**。发现**安装版本漂移**时，Source Mode 只报告后续通过**正式 Runtime upgrade**收敛，不手工覆盖 installer-owned managed block，也不把旧安装语义复制到项目 Overlay。",
    "Source Mode 是明文维护/直读模式；在用户已经有源码访问权时，可以正常显示正在读取哪个 Skill/Reference、具体路径、路由判断和维护过程，不应用 Runtime Mode 的用户可见隐藏策略伪装源码事实。**目标项目旧版本 Agent_Skills 安装资产不能作为 Source Mode 当前通用治理规则来源；项目自己的规则和真实事实仍必须读取。安装版本漂移只报告正式 Runtime upgrade 需要。**",
)

replace_once(
    ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md",
    "网页端如果通过 GitHub 获得 Agent_Skills 源仓库读取权限，使用 Source Mode：先读取目标项目**项目自有规则和真实事实**与 Agent_Skills 根 AGENTS.md，再按 Router 和 canonical metadata 直接读取 required References。该路径是源码直接读取模式，不调用本地六个 MCP Tool，也不读取/修改目标项目的 Runtime 安装副本来取得通用治理规则；目标项目旧版本 Agent_Skills 安装资产即使可见，也**不能作为 Source Mode 当前通用治理规则来源**，仅可用于确认 marker、ownership、安装版本漂移以及是否需要后续正式 Runtime upgrade。因为这是 Source Mode，可以正常显示明文 Skill/Reference 和源码导航过程。",
    "网页端如果通过 GitHub 获得 Agent_Skills 源仓库读取权限，使用 Source Mode：先读取目标项目事实与 Agent_Skills 根 AGENTS.md，再按 Router 和 canonical metadata 直接读取 required References。该路径不调用本地六个 MCP Tool；目标项目安装资产只作安装状态事实，不能替代当前 canonical Source。Source Mode 可以正常显示明文 Skill/Reference 和源码导航过程。",
)
