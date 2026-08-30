---
schema: coding-change/v1
id: "CHG-20260830-contiguous-coding-reference-numbering"
title: "Coding Reference 连续编号迁移"
level: L2
status: proposed
owner: "dingyuwen777"
branch: "chore/contiguous-coding-reference-numbering"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "Coding Reference 文件导航"
  - "Source Mode Markdown 链接"
  - "Runtime canonical Reference source path"
  - "Skill Mutation 测试与维护入口"
affected_paths:
  - ".agents/skills/coding/references/"
  - ".agents/skills/coding/SKILL.md"
  - ".agents/MAINTENANCE.md"
  - "AGENTS.md"
  - ".agents/skills/coding/tests/"
contracts:
  - "Coding Reference 文件导航编号"
  - "Stable Reference ID 保持不变"
data_changes: []
---

# 目标

把 Coding `references/` 当前 `01–11, 13–17` 的文件名前缀调整为连续 `01–16`，并同步所有 live 路径、Markdown 链接、测试和维护导航，保证改名后 Source Mode 不出现断链，同时保持 Runtime Stable Reference ID 不变。

# 成功标准

- [ ] Coding references 文件名前缀连续为 `01`–`16`，不存在编号缺口或重复。
- [ ] 原 `13`–`17` 五份 Reference 依次改名为 `12`–`16`，正文语义保持，仅更新必要的路径/导航措辞。
- [ ] `coding.reference.13`–`coding.reference.17` Stable ID、依赖和路由语义保持不变，不制造 Runtime Contract Migration。
- [ ] `AGENTS.md`、`.agents/MAINTENANCE.md`、Coding `SKILL.md`、相关 References 与 tests 中所有文件路径引用同步到新文件名。
- [ ] live 规则中不再残留五个旧文件名；Source Mode Markdown 导航全部指向真实文件。
- [ ] Runtime Bundle 仍能动态发现全部 References，并以原 Stable ID 正常编译/路由。

# 范围

- Coding Reference 文件名连续编号迁移。
- 与五个旧文件名直接相关的 live Markdown/测试路径同步。
- 增加连续编号、旧路径残留、Stable ID 守恒回归。

# 非目标

- 不修改任何 Reference 的 Stable ID。
- 不修改 Reference 触发条件、依赖、最低风险或自然语言规则语义。
- 不修改 Bundle/Project Payload/install/MCP/Task Route/Routing Manifest 协议版本。
- 不修改 Review/Docs/Figma 自己的 Reference 编号体系。
- 不发布新 Release/tag。

# 必须保持不变

- `coding.reference.13`–`coding.reference.17` 身份不变；文件名只承担人类阅读顺序。
- Source Mode 与 Runtime Mode 仍共享同一 canonical Reference 正文与 metadata。
- Runtime 目标项目仍不安装 Reference/Stub。
- 仓库 Public、main 未保护等当前仓库设置不在本 Change 范围。

# 关键决策

1. **只迁移文件导航编号，不迁移 Stable ID。** Runtime ref14 已明确 Stable ID 不由文件名前缀推导，文件改名默认不改变 Stable ID。
2. **连续映射固定为 `13→12, 14→13, 15→14, 16→15, 17→16`。** 不对 01–11 做无意义改名。
3. **旧路径残留作为回归失败。** live 规则中如果仍引用旧文件名，视为 Source Mode 断链风险。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Coding references 编号改为连续 | user:continuous-reference-numbering | not_satisfied | 待 Red/Green 与目录事实 |
| R2 | 同步对应文档内容/引用，改名后不能找不到 | user:continuous-reference-numbering | not_satisfied | 待 live-path scan 与链接/测试 Green |
| R3 | 不把纯文件改名升级成 Stable ID Contract Migration | repo:.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待 Stable ID 守恒测试 |
| R4 | 按仓库门禁合入 main 并取得 main 新鲜 CI | repo:.agents/MAINTENANCE.md | not_satisfied | 待 PR/merge/main CI/Change 清理 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 编号连续、旧路径残留、Stable ID 守恒测试 |
| 接口 / Contract | required | `coding.reference.13`–`17` 不变；Routing metadata 编译通过 |
| 集成 / Persistence / Runtime Dependency | required | `build_bundle` / routing conformance 证明 rename 后 Runtime 可发现 |
| 用户 / Workflow Acceptance | required | Source Mode live 导航的新路径真实存在，无旧文件名残留 |
| 跨组件 Golden Path | required | 全量 self-contained tests + Runtime build/MCP/install 永久 CI |
| External Dependency / Provider Probe | not_applicable | 无新的外部 Provider/远端依赖 |
| Build / Package / Runtime | required | 永久三平台 Runtime CI |
| Docs / Governance / Other | required | AGENTS/Maintenance/SKILL/Reference/test 路径同步与 Change/Ready |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户要求、AGENTS、Maintenance、ref14、ref16 与当前目录事实。
- [ ] change_coverage：核对五个 rename、所有 live 路径和相关测试均覆盖。
- [ ] reverse_audit：从 Coding SKILL/Maintenance/AGENTS 导航反查新路径可达，再从 Stable ID 反查 Runtime Bundle entry。
- [ ] unresolved_cleared：`not_satisfied` 清零；非目标/不适用有事实依据。

# 任务

- [x] 恢复最新 main、Maintenance、Router、Coding、ref14/ref16 与 references 目录事实。
- [ ] 写连续编号/旧路径/Stable ID Red tests，并确认当前缺口导致精确失败。
- [ ] 重命名 13–17 为 12–16，并同步所有 live 路径与测试。
- [ ] 跑全量 self-contained tests、Runtime 三平台 CI 与 Ready Check。
- [ ] 独立 Review / re-review、Requirement Traceability、Completion Audit。
- [ ] 非 Draft PR 正常合并，main fresh CI 后删除 Active Change。

# 验证

## 计划

- 目标回归：`python -m unittest .agents/skills/coding/tests/test_reference_numbering.py -v`
- 全量：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- Runtime：永久 CI 的 Linux/Windows/macOS onefile/status/self-test/MCP/install。
- Ready：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Baseline main：`520fa1144bd462fb704fe567ee139f27d251b5fe`（已清理误创建占位文件后的最新 main）。
- 当前目录事实：`01–11, 13–17`，缺少 `12_`。
- Red：待执行。

# 文档影响

- `AGENTS.md`、`.agents/MAINTENANCE.md`、Coding `SKILL.md` 与相关 Reference 的文件路径导航受影响。
- README/USAGE/runtime README 仅在存在具体旧文件名引用时同步；不为本次机械 rename 扩写用户说明。

# 交付

- Commit：待完成。
- PR：待创建。
- Release：不创建。
