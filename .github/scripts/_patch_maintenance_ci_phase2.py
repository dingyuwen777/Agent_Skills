from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MAINTENANCE = ROOT / ".agents/MAINTENANCE.md"

NEW_SECTION = r'''## 9. 开发与永久 CI 责任

测试必须自包含，**不能依赖另一个业务仓库**、外部 Blueprint、业务源码或私有测试 fixture 才成立。

普通 PR/main 的 CI 机器事实源是当前 [`.github/scripts/runtime_package_scope.py`](../.github/scripts/runtime_package_scope.py) 与 [`.github/workflows/skill-tests.yml`](../.github/workflows/skill-tests.yml)。前者虽然保留历史稳定文件名，但当前职责已经从“只判断 package scope”升级为**多轴 CI Evidence Selector**：同时给出 Runtime scope、semantic profile/test groups、Runtime dependency、compile/smoke 和 package Evidence 责任。**L3 ≠ 必然全测试或三平台打包**；风险等级决定治理强度，真正执行哪些测试/Runner 由 changed scope 的独立失败边界决定。

### 9.1 每次维护都必须做 changed-scope Evidence Check

Agent_Skills 的默认长期策略不是“CI 越多越安全”，而是：

```text
changed paths
→ 恢复真实 Owner / consumer / failure boundary
→ 选择最小充分 semantic test groups
→ 只准备这些测试需要的依赖 / compile / smoke
→ executable/package 风险存在时再升级平台 package Evidence
→ required Gate 聚合
```

每次新增或修改文件时都要主动判断：本次是否会机械拉起与变化无关的 test group、Runtime setup、compile/smoke、binary build、平台 Runner 或 Workflow。能由 selector 精确证明不相关的步骤必须跳过；**不能等用户再次发现 Actions 消耗过高才处理**。

当前 Runtime scope 继续保持 `change_only / governance / content / package`，但它只是一条轴，不再等价于“运行整套 Skill Tests”：

- `change_only`：只有 `.agents/changes/` carrier 独占变化时成立；只保留 Requirement/Change/Ready/required gate，不安装 Runtime 依赖、不跑 semantic/package；repository-native Archivist 在完成门禁、exact two-path allowlist 和 main 防漂移全部成立后生成的纯归档 commit 可以使用 `[skip ci]`，**不再重复 parent implementation revision 的功能性 CI**；普通用户/PR commit 不得复用该能力；
- `governance` / human docs：README、runtime README、Issue/PR template、Maintenance 和明确的仓库治理变化只运行 docs/governance/CI 直接 consumer Evidence；默认不安装 Runtime 依赖、不编译 Runtime、不跑 MCP、不构建 binary；
- `content`：canonical Skill/Reference/Entry/USAGE 等内容变化按 semantic Owner 选择 Evidence。Docs/Figma/Testing/Review 等专业 Skill 运行本 Owner tests + Router/Source-Runtime 等真实共享 consumer closure；Coding/Router/ENTRY/shared control-plane 因影响面更广可升级为 broad/full semantic。**content 不再机械等于全 492+ self-contained tests**；
- `package`：Runtime Python/source、加密/Bundle/Installer、MCP、Runtime/build requirements、Builder、核心 CI selector/workflow、Release workflow、`.gitattributes` 等 executable/package/platform boundary 变化；必须运行完整 semantic Evidence，并在 Linux、Windows、macOS 对应 Runner 完成 onefile、self-test、真实 stdio MCP 和项目安装验证。

测试文件本身默认只运行被修改测试及其真实 consumer closure；但 selector、核心 CI/Workflow、共享 fixture、Router/ENTRY、Runtime/package 和无法安全分类的机器路径必须 **fail-closed** 到 broad/full。新增机器路径如果没有显式映射，不能得到空 Evidence；要么同步 selector，要么由 unknown→full 兜底。

混合修改只允许向更强 Evidence **单调扩大**。分类依据是文件在产品/治理中的真实职责，不按 `.md`、`.py` 等扩展名粗暴判断：`runtime/README.md` 是 human docs，canonical Reference Markdown 是可执行治理内容，Runtime Python 是 package。Agent 不手工覆盖 selector 的安全回退。

### 9.2 Test Group 与 Runner 成本规则

永久测试资产按独立证明责任组织为逻辑 test group；**优先减少“何时运行”，不是先删测试文件**。仍有长期回归价值的 test 不因本次 scope 未命中而删除。

后续维护新增/修改测试时必须同步判断：

- 它直接保护哪个 Owner / Contract / failure boundary；
- 应属于哪个 semantic group，或为何必须进入 broad/full；
- 对应生产/治理路径是否能触发它；
- test-only 变化是否可以只运行该测试，而不是反向拉起全仓；
- selector / group 映射自身变化是否已经 fail-closed full。

CI 消重顺序固定为：

```text
无关 step
→ 无关 test group
→ 重复 setup/install/compile/build
→ 无关 platform job
→ 只重复治理检查的 runner job
→ 重复 workflow
```

只把 checkout/setup 命令藏进 composite action、模板或 helper，但实际 Runner 时间/次数不下降，**不算 CI 性能优化**。除非它同时统一真正独立的高风险 Contract，否则不为了 YAML 变短引入新 Action 层。

### 9.3 当前永久 Evidence 责任

`Agent Skills Gate` Core 负责：Requirement Source、changed-scope selector、selected semantic tests、必要 compile/smoke、Linux package（仅 package）和当前 Change Ready 结果。`Runtime Package Gate` 只聚合 Core + Windows/macOS + Change Ready 结果，**不得再次 checkout/setup Python/重复 ready_check**。Windows/macOS package 仅在 package + Ready/non-draft/main 条件真实要求时启动。

专业 Skill targeted Evidence 只能跳过已证明不相关的边界，不能用局部测试冒充 Runtime/package；反过来，纯人类文档也不能因为“同仓有 Runtime”就运行无关 binary Evidence。

永久 Workflow 仍保持三个唯一 Owner：

```text
skill-tests.yml
→ PR/main 的 changed-scope semantic + Runtime/package required Evidence

change-archive.yml
→ merge 后 Change carrier active→archive/status done
→ 自身 completion/exact allowlist/main drift 证明通过后 archive commit [skip ci]

release.yml
→ 手工正式 Release
→ 不使用日常 selector 快速路径
→ 对最终版本重新构建和验证 Linux/Windows/macOS artifact
```

不再寻找或额外触发已经移除的独立 `.github/workflows/runtime-package-tests.yml`。selector 保留旧路径只用于删除/意外恢复控制面时 fail-closed，不表示 Workflow 当前存在。

**正式 Release 不复用普通 CI binary，也不因为日常 CI targeted 就降低最终 artifact 证明。** 每次仍验证 Linux、Windows、macOS 最终 artifact、MCP/install、跨平台 identity、SHA256 和 ZIP 精确成员。

### 9.4 后续修改 CI 的硬门禁

修改 selector、test group、Workflow、required Gate 或 Archive skip 时必须：

1. 先做 Workflow Responsibility Audit / Evidence Preservation Mapping；
2. 为所有新降级路径补正反例永久回归；
3. CI/selector 自身变化用 full current-head Evidence 验证；
4. 从“哪些风险可能被漏跑”做反向 Review，而不是只看 Actions 绿色；
5. required check identity / Ruleset consumer 不得因 path filter 或 silent skip 变成 Pending/假绿；
6. unknown/shared/CI-self 无法证明安全时保持 full，不为节省分钟牺牲 fail-closed；
7. Evidence 已足够后遵守 Validation Stop Rule，不因为阶段切换、metadata/Change/PR 文本更新或 archive carrier 变化重复同一功能性测试。

删除旧产品能力时，可以删除只为该能力保活且已没有 consumer 的测试；但不能借 CI 精简删除现行 Runtime、内容守恒、安全或交付责任。每项删除/合并都必须能指出新的唯一 Evidence Owner，无法证明等价时保留。
'''


def main() -> int:
    """把旧 Section 9 替换为多轴 Evidence Selector 维护契约，并同步归档收尾语义。"""
    text = MAINTENANCE.read_text(encoding="utf-8")
    text, count = re.subn(
        r"## 9\. 开发与永久 CI 责任\n.*?(?=\n## 10\. Git 与 Release)",
        NEW_SECTION.rstrip(),
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise SystemExit(f"Section 9 替换数量异常：{count}")

    old = (
        "- implementation main fresh CI 与 Change Archive 可以按真实 GitHub Actions 独立运行；完整 Closure 前必须同时取得当前 implementation merge revision 的 required main-fresh Evidence、同一 Change 的 archive/done 结果，以及项目要求的 archive revision governance fresh Evidence；archive/done **不等价于 Requirement** 已完成；"
    )
    new = (
        "- implementation main fresh CI 与 Change Archive 可以按真实 GitHub Actions 独立运行；完整 Closure 前必须同时取得当前 implementation merge revision 的 required main-fresh Evidence，以及同一 Change 的 repository-native archive/done 结果。Archivist 纯 carrier commit 在 Section 9 的 completion/exact allowlist/main drift 门禁成立后使用 `[skip ci]`，**不要求为了归档 revision 再重复功能性 CI**；archive/done 仍不等价于 Requirement 已完成；"
    )
    if old not in text:
        raise SystemExit("未找到 Section 10 archive fresh 旧规则")
    text = text.replace(old, new, 1)

    old = (
        "- merge 后由 repository-native Change Archive 自动归档；Agent 等待/验证 archive/done 与 archive revision required governance fresh Evidence，再执行 Closure Audit、Acceptance 状态同步和 Requirement Closure。归档失败时保持 `blocked/incomplete`，不创建归档 PR、不手工 direct push main。"
    )
    new = (
        "- merge 后由 repository-native Change Archive 自动归档；Agent 等待/验证 archive Workflow 自检成功与 archive/done，并确认纯 carrier commit 没有越出允许路径后，再执行 Closure Audit、Acceptance 状态同步和 Requirement Closure。按 Section 9 合法使用 `[skip ci]` 的 archive revision 不再机械要求下游 CI；归档失败时保持 `blocked/incomplete`，不创建归档 PR、不手工 direct push main。"
    )
    if old not in text:
        raise SystemExit("未找到零人工交付 archive 旧规则")
    text = text.replace(old, new, 1)

    MAINTENANCE.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
