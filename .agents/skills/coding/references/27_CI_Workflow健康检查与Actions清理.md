<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI / Actions 健康检查

本 Reference 只负责**真实 CI 成本与永久验证资产冗余**；它不要求每个实现任务通读所有 Workflow。Coding Core 先执行三问轻量检查，只有命中真实风险时才进入这里深入。

## Start Cost / Evidence Check

正式实现前先判断本次 changed scope 是否存在以下任一风险：

1. **Broad Job**：局部修改会不会因为粗粒度 selector / fallback 被放大成明显更宽的昂贵 Job、suite 或平台矩阵；
2. **Duplicate Evidence**：PR、main、多个 Job/Workflow 是否对**同一 revision/environment/failure boundary**重复证明同一事实，而没有新的独立风险价值；
3. **Duplicate Setup/Install/Build**：多个 Job 是否重复支付可安全合并的相同 checkout/setup/install/build/package 成本。

三项都没有直接 Evidence 时记为 clean / not_applicable 并继续，不为“可能以后有问题”扫描全 CI。命中后再沿真实 Workflow、selector、required check consumer、Branch Protection/Ruleset 和运行时长收敛最小方案。

默认优化顺序：

```text
精确 target / owner / journey
→ domain/suite
→ shared/global fallback
→ low-frequency full safety net
```

changed-scope selector / path filter / scoped skip 必须有永久回归和 fail-safe；无法安全分类时 fail closed。CI/selector 自身变化使用 full current-head Evidence。required check identity、Change Ready 或平台保护等独立责任不能为了省 Runner 被移除；N/A 优先由 job-level condition / 0 Runner 表达。

## Ready Redundancy Check

Ready/merge 前只审查**本次新引入、扩大、直接触及或实际暴露**的永久验证资产冗余：

- test/group/CI/Job/Workflow/build-smoke-install 是否由不同 Owner / Contract / failure boundary / Evidence level 持有独立价值；
- 仅减少 YAML 行数但 Runner 时间/外部成本不变，不算 CI 性能优化；
- “少跑”不等于允许永久冗余：如果两个资产长期证明同一边界，应合并/删除 Owner 冗余，而不是只靠 selector 隐藏；
- 平台权限、required context、package target、不同 OS/runtime、真实 persistence/full-stack 等独立失败边界继续保留；
- 与本任务无直接因果关系的历史冗余记录 Finding，按 clean / not_applicable / blocked 处理，不自动扩大当前任务。

## Actions Control-Plane Cleanup

Source Workflow：disabled / deleted / orphaned / no-owner Workflow 可清；Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 留；capability-limited / cleanup gap 明确记录。Actions History 清理不替代 Workflow/Evidence 设计优化。
