---
schema: coding-change/v1
id: CHG-20260920-140000-validation-asset-ci-consolidation
title: 精简重复测试与平台 CI 验证资产
level: L3
status: ready_for_review
owner: dingyuwen777
branch: tech/validation-asset-ci-consolidation
created: 2026-09-20
updated: 2026-09-20
completion_gate: required
depends_on: []
affected_areas:
  - tests
  - ci
  - release
  - runtime-validation
affected_paths:
  - .agents/skills/coding/tests/
  - .github/scripts/runtime_package_scope.py
  - .github/workflows/skill-tests.yml
  - .github/workflows/release.yml
  - scripts/runtime_platform_smoke.py
contracts:
  - Validation Asset Redundancy Gate
  - Runtime Package Gate
  - three-platform package evidence
  - release artifact validation
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 main 已有 Validation Asset Redundancy Gate，但测试与 package CI 仍存在可证明的重复 Contract Evidence、职责混杂和 YAML 验证逻辑复制。
- **拟议修改**：删除/合并没有独立 failure boundary 的重复测试；保留独立 Evidence；抽取跨平台 Runtime smoke；把 PR/main package Evidence 重构为对称三平台 package Job/Matrix；Release 继续独立构建但复用同一 smoke 实现。
- **预期结果**：减少长期测试/CI 维护重复，避免职责混杂拉起无关 Evidence，缩短 package CI 关键路径，同时不降低三平台、真实 MCP、项目安装和 required-check 证明强度。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #281。用户已授权按既定精简方案实施并合并 main。

## 当前现状

- 永久 Workflow 只有 skill-tests.yml、change-archive.yml、release.yml 三个独立 Owner。
- coding tests 当前 87 个 test_*.py；full semantic 为 603 tests。
- skill-tests.yml 约 644 行，Release workflow 约 575 行。
- CI topology、Issue/Requirement、Release surface 在多个测试文件存在重复静态断言。
- test_runtime_cli_disclosure.py 只有一个 disclosure boundary test。
- Linux package Evidence 位于 Core，Windows/macOS 为独立 Job；三平台启动时机不对称。
- CI/Release 多处重复 self-test、real stdio MCP、project install shell 逻辑。

## 问题、根因或约束

根因是历史迭代中按需求逐步增加永久回归和平台 shell，导致：
1. 同一 Contract 被多个测试文件重复静态证明；
2. 一个测试文件同时承担 selector/topology/lifecycle 等不同责任；
3. package CI 拓扑不对称；
4. CI/Release 对同一 artifact smoke 维护多份实现。

## 不修改的后果

- Contract 修改需要同步多处重复断言；
- 测试职责混杂容易拉起无关 dependency / Runner；
- package CI wall-clock 受 Linux 串行位于 Core 影响；
- CI/Release smoke 实现容易漂移；
- Validation Asset Redundancy Gate 只能阻止未来新增，无法清理当前已经确认的冗余。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前永久 Workflow 仅 3 个 | main/.github/workflows | 三个 Workflow 不合并 |
| E2 | coding tests 87 个，full semantic 603 tests | main tests 目录 / #1638/#1639 | 不以测试数量为性能目标 |
| E3 | CI topology 在 4 个文件重复断言 | test_ci_ready_evidence_order / minimal_sufficiency / runtime_package_scope / archive_ci_runtime_lifecycle | 需要收敛 Owner |
| E4 | Issue title/section/Acceptance 在 governance_asset_contract / pr_requirement_source / acceptance_closure 重复 | current main tests | 需要按 Contract Owner 去重 |
| E5 | Release exact three ZIP / members 在多个测试重复 | release_only_repository_surface / release_platform_zips / release_productization | surface/workflow 分责 |
| E6 | runtime_cli_disclosure 仅 1 test 且同属 disclosure boundary | current main | 合入 disclosure Owner |
| E7 | skill-tests Linux package 串行位于 Core；Win/mac 独立 | skill-tests.yml | 改对称 package job/matrix |
| E8 | CI/Release 重复 self-test/MCP/install shell | skill-tests.yml / release.yml | 抽共享 smoke |

## 推断与待确认

- package matrix 的 wall-clock 改善需要由最终 Actions duration 观察；这是优化结果，不作为 correctness gate。
- Router historical tests 是否还能进一步合并：当前未证明全部等价，本次只对已确认重复的部分处理；未证明者保留。

# 目标、成功标准与非目标

## 目标

清理当前可证明的 Validation Asset 冗余，并让 package CI 三平台对称、smoke 实现单一化。

## 成功标准

- [ ] 删除/合并项都有新 Owner 映射，独立 Evidence 不丢。
- [ ] selector/group 映射无悬空测试文件。
- [ ] package CI Ready 时 Linux/Windows/macOS 对称执行，Draft/not-ready 不提前跑。
- [ ] Runtime Package Gate 保持稳定 identity 且三平台任一失败时 fail-closed。
- [ ] CI 与 Release 共用 artifact smoke 实现。
- [ ] full semantic / context budget / compile/CLI / three-platform package / Release contract 全绿。

## 范围

- P0：runtime CLI disclosure 单测合并；CI topology 重复断言；Issue/Requirement 重复断言。
- P1：Release test 去重；package jobs 对称化；共享 Runtime artifact smoke。
- Router 测试只做已能证明的重复整理；不能证明等价的历史/route/context failure boundary 保留。

## 非目标

- 不合并三个永久 Workflow。
- 不删除 Runtime Package Gate。
- 不删除历史 Actions Run。
- 不复用 PR package Evidence 作为 main-fresh Evidence。
- 不减少真实平台、real MCP、project install、Release rebuild。
- 不改变 Runtime/Router/MCP/Release 产品协议。

## 必须保持不变

- unknown/shared/CI-self fail-closed。
- Change Ready / Requirement Source / independent Review。
- Linux/Windows/macOS onefile + self-test + real stdio MCP + project install。
- Release 三平台独立最终构建与 identity/hash/ZIP contract。
- main-fresh / Change Archive / Issue Closure。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只处理可证明重复的 validation assets | E3-E8 | 不扩大成全仓测试重写 |
| 接口与契约 | Runtime Package Gate identity 不变 | #281 / AC8 | Branch Protection 不漂移 |
| 数据与迁移 | 不适用 | 无数据变化 | 无 |
| 错误与失败语义 | 任一 required platform smoke 失败即 package gate 失败 | 现有 contract | 保持 fail-closed |
| 兼容性 | Runtime/Release 产品行为不变 | #281 非目标 | 只变测试/CI 实现 |
| 部署与回滚 | 纯仓库 CI/Test 重构，可 revert PR | 无外部状态 | 可逆 |

# 修改方案与决策依据

## 最小充分方案

1. 建立 redundancy mapping，先处理测试文件/方法级去重。
2. 合并 test_runtime_cli_disclosure.py 到 disclosure boundary 并删除原文件。
3. 从非 Owner 文件删除 CI topology、Issue Contract、Release ZIP 的重复静态断言；同步 selector 映射。
4. 新增 scripts/runtime_platform_smoke.py：统一 artifact self-test、real stdio MCP、project-only install smoke；保留平台差异参数。
5. skill-tests.yml：Core 只负责 semantic/governance/Ready；新增对称 runtime-package matrix（Linux/Windows/macOS）；stable Runtime Package Gate 聚合 Core + matrix。
6. release.yml：各平台仍独立 build/upload，build 后调用同一 runtime_platform_smoke.py。
7. 新增/调整 CI contract tests，证明 matrix/Ready/gate/fail-closed 与 shared smoke wiring。
8. full current-head package Evidence → Review → guarded merge → main-fresh → archive/closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E3-E6 | 只删除明确重复 Contract Evidence，避免机械砍测试 |
| D2 | E7 | 三平台对称 job 能减少 Linux 串行关键路径并统一平台责任 |
| D3 | E8 | 共享 smoke 降低 CI/Release 验证实现漂移 |
| D4 | E1 | 三 Workflow 生命周期/权限不同，不合并 |

## 备选方案与取舍

- 只调 selector、不删永久重复测试：违反“少跑 ≠ 允许永久冗余”，不采用。
- 把三个 Workflow 合并：权限/生命周期/触发不同，会增加耦合，不采用。
- 直接复用 PR package Evidence 到 main-fresh：收益高但改变 freshness contract，本次不采用。
- 把所有 Runtime projection/disclosure/router 测试按名字合并：无法证明 failure boundary 等价，不采用。
- 只减少 YAML 行数而不共享执行实现：Runner/维护成本不实质下降，不作为目标。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 合并并删除 runtime_cli_disclosure 单测试文件 | #281 / AC1 | satisfied | test_runtime_disclosure_boundary.py 已承接 public install disclosure；test_runtime_cli_disclosure.py 已删除 |
| R2 | CI topology 测试按 selector/workflow owner 去重 | #281 / AC2 | satisfied | CI topology 由 test_ci_ready_evidence_order.py 独占；selector/archive/minimal_sufficiency 已删除重复 topology assertions |
| R3 | Issue/Requirement 重复断言按 Owner 收敛 | #281 / AC3 | satisfied | governance_asset_contract.py 已移除 Issue title/section/Acceptance/Closure 重复断言；PR source/closure Owner 保留 |
| R4 | Release exact ZIP 重复证明收敛 | #281 / AC4 | satisfied | release_only_repository_surface.py 已移除重复发布 ZIP 证明；release_platform_zips.py 独占 exact ZIP/member surface |
| R5 | selector 无悬空测试映射 | #281 / AC5 | satisfied | #1655 的 test_all_group_mappings_point_to_real_tests 通过；selector 不包含已删除 test_runtime_cli_disclosure.py |
| R6 | CI/Release 共用 Runtime artifact smoke | #281 / AC6 | satisfied | scripts/runtime_platform_smoke.py 已新增，skill-tests.yml 调用 1 处，release.yml 三平台各调用 1 处 |
| R7 | package Evidence 三平台对称 | #281 / AC7 | satisfied | skill-tests.yml 的 runtime-package matrix 对称包含 Linux/Windows/macOS；Core 不再持有 Linux build |
| R8 | stable Runtime Package Gate fail-closed | #281 / AC8 | satisfied | Runtime Package Gate 名称保持，仅聚合 agent-skills-core + runtime-package；Ready/package deferred fail-closed |
| R9 | 三 Workflow 独立，历史 Run 不批删 | #281 / AC9 | satisfied | 当前方案不改生命周期 Owner/历史 Run |
| R10 | 完整验证和交付闭环 | #281 / AC10 | not_applicable | pre-merge Change 不自证未来 merge/main-fresh/archive/Issue Closure；这些由 downstream delivery gate 持有 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| runtime disclosure tests | 合并单测试文件 | 去除单一 Contract 重复文件 | R1 |
| CI topology tests | 删除跨文件重复 assertion | 单一 Owner | R2 |
| governance/requirement tests | 删除非 Owner 重复断言 | 单一 Contract Owner | R3 |
| release tests | 去除 exact ZIP 重复证明 | surface/workflow 分责 | R4 |
| runtime_package_scope.py | 同步 test mapping | 防悬空 | R5 |
| scripts/runtime_platform_smoke.py | 新增共享 artifact smoke | CI/Release 单一验证实现 | R6 |
| skill-tests.yml | 三平台对称 package matrix | 平台责任一致/缩短关键路径 | R7-R8 |
| release.yml | 复用 shared smoke | 减少 shell 重复 | R6 |
| CI contract tests | 更新 matrix/shared smoke 回归 | 防拓扑回退 | R7-R8 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 删除/合并测试后 full semantic 与 direct owner tests |
| 接口 / 契约 | required | Runtime Package Gate / Release surface / Requirement contract |
| 集成 / 持久化 / 运行依赖 | required | runtime_platform_smoke real artifact subprocess/MCP/install |
| 用户 / 工作流验收 | not_applicable | 无最终用户产品行为变化 |
| 跨组件关键路径 | required | selector → core → package matrix → gate；Release build → shared smoke |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方外部服务 |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile + smoke + project install + release contract |
| 文档 / 治理 / 其他 | required | Change/Issue/Review/main-fresh/archive/closure |

## 验证计划

- 目标测试：受影响测试文件、runtime_package_scope、CI topology、Release tests。
- 相关回归：full self-contained tests + context budget。
- 静态检查或构建：py_compile shared script / workflow tests / selector mapping。
- 专项真实边界：Linux/Windows/macOS package artifact smoke；Release workflow contract。
- 就绪检查：ready_check current-head + required Skill Tests。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 误删独立 Evidence；matrix 条件导致平台漏跑；shared smoke 平台差异处理错误 | 逐项 Owner mapping + full three-platform gate |
| 兼容性 | 产品行为保持 | 只修改 tests/CI validation implementation |
| 数据 / Migration | 不适用 | 无数据 |
| 部署 / 运行 | 仅 GitHub Actions / test harness | 不影响分发 Runtime 运行协议 |
| 回滚 / 恢复 | revert implementation PR | 无外部状态迁移 |

# 文档、依赖、部署与发布影响

- **长期文档**：不新增用户文档；Change 记录 Owner mapping。若 workflow contract 名称变化需同步维护规则。
- **依赖 / Runtime**：不新增第三方依赖，不升级 Python/Runtime。
- **配置 / Secret**：不新增 Secret。
- **部署 / Release**：Release workflow 实现会复用 shared smoke，但正式 Release 语义不变；本任务不创建 Release。
- **兼容 / 消费方通知**：Branch Protection 继续消费 stable Runtime Package Gate；不要求用户迁移。

# 完成审计

- [x] upstream_re_read：已重读 #281、main bb705df7 与 reviewed head 7478e287；目标/非目标无漂移。
- [x] change_coverage：R1-R9 均有直接实现/回归证据；R10 downstream 交付由 merge 后门禁持有。
- [x] reverse_audit：已从 changed path → selector → semantic/core → package matrix → stable gate，以及 Release build → shared smoke 反查；未发现漏接线。
- [x] unresolved_cleared：R1-R9 satisfied、R10 pre-merge N/A；current-head 独立 Review 无 blocker；Validation Asset Redundancy Gate=clean。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main bb705df7 | canonical reread + redundancy audit | 已确认 | 当前重复候选和必须保留边界 |
| V2 | Draft PR #282 / #1640 rerun | Contract Red | Requirement Source/Change Contract 通过；matrix/shared-smoke 目标回归按预期失败 | 证明旧 CI 尚无对称 matrix/shared smoke |
| V3 | head 7478e287 / Skill Tests #1655 | full semantic + compile/CLI | 592 tests OK；compile/CLI smoke 通过；最终仅因 Change in_progress fail-closed | 测试去重后语义、Context/治理回归与新脚本可编译/可调用 |
| V4 | head 7478e287 / PR #282 | 独立 Review + Redundancy Audit | NO_FINDINGS_WITHIN_SCOPE；Gate=clean | 删除项均有唯一 Evidence Owner，三平台/gate/release 不变项完整 |

## 未验证内容与剩余风险

- Linux/Windows/macOS shared smoke 的真实 package Evidence 尚未执行（PR 仍 Draft）。
- merge/main-fresh/archive/Issue Closure 尚未完成。
- 正式 Release 未执行；本任务只验证 Release workflow contract，不创建 Release。

## 交付状态

- 提交：实现已在任务分支；reviewed head 7478e2875ce6db5286c1f0c4de6f1a47986b85d5
- 拉取请求：#282（Draft，待切 Ready 运行真实三平台 package）
- CI：Red #1640 rerun；Green semantic #1655（592 tests OK），三平台 package 待 Ready
- 合并：未执行
- Change 归档：未执行（merge 后 repository-native automation）
- 发布 / 部署：不适用；本任务不创建正式 Release。

## 备注

本次不以最终测试文件数量为成功标准；只能删除可证明没有独立长期 Evidence 价值的资产。
