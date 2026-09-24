<!-- agent-skills:managed:start -->
## 项目研发治理入口

处理本项目研发任务时：

1. **无论采用哪种通用治理执行方式，都必须先读取并遵守当前目录及上级适用的项目规则**，再依据当前真实文件恢复本任务所需的技术栈、架构、Contract、Schema/Migration、CI、部署、设计和运行事实；不得用通用示例、历史聊天、缓存或猜测覆盖项目事实。
2. 在实质性工程任务形成执行计划前，读取 `.agents/skills/ENTRY.md` 作为当前项目工程约束入口，并使用项目已配置的治理能力取得本任务真正需要的完整约束。系统、开发者或用户级更高优先级指令若明确指定其他执行方式，**只改变通用治理约束的取得和呈现方式；不得因此跳过、替代或降低目标项目自身规则、Contract、Schema/Migration、CI、正式设计、部署和验收边界**。
3. 在计划前分别判断 **Delegation Value**（`NO_SPLIT | MAY_SPLIT | MUST_SPLIT`）与 **Independence Requirement**（`OPTIONAL | REQUIRED`）。前者只决定多 Agent 的并行/隔离收益：明显低风险、明显 `NO_SPLIT` 的小任务直接正常处理，不单独播报编排 banner；MAY/MUST、实际拆分或因宿主能力 fallback 时再向用户说明。后者来自真实 Review/Testing/项目门禁；`REQUIRED` 不能因为当前宿主没有 subagent 或任务适合单 Agent 就降级。
4. 实际拆分默认只由 Main/Parent 发起，child 不继续递归派生；同时活动的子 Agent 默认不超过 3 个，超出只在确有独立收益且宿主允许时由 Parent 明确扩展。同一 checkout/shared mutable state 默认单 Writer；多 Writer 仅在 worktree/environment、路径、Contract/Schema、共享状态和验证环境都隔离时并行。
5. Parent 集成 child 结果前核对当前 revision 和已确认决定；基于旧 revision/旧决定的结果必须重新验证，不能直接驱动修改或完成。child 对同一 transient 失败只做有限重试，重复失败回 Parent fallback/replan；Evidence 已充分或 child 已无价值时停止等待，并在宿主支持时取消。跨域或超范围问题默认 `REPORT_ONLY`；确有独立长期价值时最多形成 `FOLLOW_UP_CANDIDATE`。Candidate **不自动**创建 Issue/Change/Branch/PR/Agent，不自动执行或递归；把它**持久化**到项目既有 backlog 是新的外部动作，当前任务的 Git/写权限不自动授权该持久化。
6. 当前宿主没有可用 subagent/delegation、该能力被禁用或无法安全使用时，明确说明后可把 `MUST_SPLIT` 的实现工作降级为单 Agent正常执行；不得因此阻塞本可完成的工程任务，也不得伪称已经拆分。但若 `Independence Requirement=REQUIRED`，缺少独立复核能力只阻塞依赖该独立性的 Review/可合并/交付强结论，不能把 required independence 静默变成作者自证。
7. 首次接入、项目治理状态尚未校准，或长期项目事实疑似漂移时，在实质性生产代码修改前执行有界的项目治理校准：调查当前仓库真实实现，只维护本区块外的项目自有 Overlay；完成后重新读取最终 `AGENTS.md`，再继续用户原始任务。
8. 必需治理约束无法可靠取得、完整性无法确认，或与更高优先级规则存在无法安全解决的冲突时，只阻塞依赖该约束的动作并如实说明；不得用旧记忆、摘要或自行猜测替代。
9. 本区块由安装/升级流程维护。项目自己的长期规则继续写在本区块外；受管运行资产和宿主 execution adapters 只服务当前项目研发治理，不作为项目自有长期规则直接手工维护。

<!-- agent-skills:managed:end -->
