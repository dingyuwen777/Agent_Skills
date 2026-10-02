from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]


class DevelopmentGuidanceTest(unittest.TestCase):
    """验证 Coding 通用核心和用户定义的全局硬规则没有被通用化过程削弱。"""

    def _read(self, path: str) -> str:
        """读取仓库内 UTF-8 文本用于规则回归断言。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_global_engineering_invariants_are_hard_rules(self) -> None:
        """中文注释、函数说明、中文提交、北京时间和日志前缀必须继续存在。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        routing = self._read(".agents/skills/coding/references/02_跨项目研发任务路由.md")
        maintenance = self._read(".agents/MAINTENANCE.md")
        for text in (
            "中文注释与函数级说明是通用规则",
            "内部/private/helper 函数也必须写函数级中文注释或文档注释",
            "Git 提交信息统一中文",
            "Asia/Shanghai",
            "[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message",
        ):
            self.assertIn(text, skill)
        self.assertIn("跨项目用户级工程不变量", routing)
        self.assertIn("用户定义的全局工程硬规则", maintenance)

    def test_greenfield_and_existing_repo_flows_are_both_supported(self) -> None:
        """通用 Coding 必须同时支持空仓库 Bootstrap 和既有仓库事实恢复。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        routing = self._read(".agents/skills/coding/references/02_跨项目研发任务路由.md")
        self.assertIn("Greenfield / Repository Bootstrap", skill)
        self.assertIn("Greenfield / Repository Bootstrap / Prototype / Feasibility", routing)
        self.assertIn("Repository Onboarding / Fact Recovery", skill)
        self.assertIn("不能把 Skill 中的语言/框架示例当默认选择", routing)

    def test_systemic_analysis_considers_reuse_abstraction_and_capability_ownership(self) -> None:
        """分析问题时必须先看系统能力边界，再决定局部修复、复用、公共抽象或统一治理链。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        systemic = self._read(".agents/skills/coding/references/21_系统级分析与代码整洁收口.md")
        self.assertIn("系统级分析先于局部实现", skill)
        for fragment in (
            "调用链、数据流、状态流",
            "能力 Owner",
            "复用现有正确实现",
            "公共实现",
            "单一事实源",
            "统一能力治理链",
            "不要为抽象而抽象",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, systemic)

    def test_l2_feature_route_loads_systemic_analysis_reference(self) -> None:
        """普通 L2 功能开发必须自动加载系统级分析与整洁专项规则。"""
        manifest = compile_routing(ROOT)
        result = evaluate_route(
            manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {
                    "执行模式": ["实现"],
                    "阶段": ["功能开发"],
                    "风险": ["L2"],
                },
                "未知项": [],
                "依据": ["systemic analysis routing regression"],
            },
        )
        self.assertIn("coding.reference.22", result["必需Reference"])

    def test_affected_code_scope_must_finish_clean_without_unrelated_refactor(self) -> None:
        """开发收口必须清理受影响代码域，同时保护隐式依赖并禁止借机扩大范围。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        systemic = self._read(".agents/skills/coding/references/21_系统级分析与代码整洁收口.md")
        self.assertIn("受影响代码域必须整洁收口", skill)
        for fragment in (
            "死代码",
            "废弃分支",
            "重复 helper",
            "垃圾残留",
            "反射/动态加载",
            "插件注册",
            "Migration/回滚",
            "无法确认安全时不删除",
            "不把代码清理扩大成无关重构",
            "整体清晰、易读、可维护",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, systemic)

    def test_planning_architecture_and_conflict_guidance_are_preserved(self) -> None:
        """方案落地、架构设计、纵向切片、大型规划和意图冲突解决必须保持可达。"""
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        planning = self._read(".agents/skills/coding/references/30_方案落地架构设计与渐进式规划.md")
        collaboration = self._read(".agents/skills/coding/references/09_多人和多智能体并行协作.md")
        delivery = self._read(".agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md")
        usage = self._read("USAGE.md")

        for fragment in (
            "外部 / 既有方案先作为 Proposal",
            "Architecture / Codebase Design",
            "大型任务渐进式规划",
            "Locality / Leverage",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, planning)

        self.assertIn("Vertical Slice", planning)
        self.assertIn("Vertical Slice", collaboration)

        for fragment in ("Vertical Slice", "DAG", "frontier", "expand", "migrate batches", "contract"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, collaboration)

        for fragment in ("Merge/Rebase 冲突", "Primary Requirement Source", "ours/theirs", "abort"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, delivery)

        for fragment in (
            "先讨论方案，再决定是否实施",
            "已经从其他地方拿到方案，怎么落实到当前代码",
            "复杂功能怎么拆",
            "任务很大、现在还看不清完整路径",
            "Merge / Rebase 冲突",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, usage)

    def test_specialist_planning_context_is_loaded_only_for_plan_intent(self) -> None:
        """方案专项必须命中显式方案任务，同时不污染普通后端 L2 实现。"""
        manifest = compile_routing(ROOT)

        for signals in (
            {"执行模式": ["方案"], "意图": ["技术方案"], "风险": ["L2"]},
            {"执行模式": ["实现"], "意图": ["技术方案"], "风险": ["L2"]},
        ):
            with self.subTest(signals=signals):
                result = evaluate_route(
                    manifest,
                    {
                        "协议": TASK_ROUTE_PROTOCOL,
                        "信号": signals,
                        "未知项": [],
                        "依据": ["planning progressive disclosure regression"],
                    },
                )
                self.assertIn("coding.reference.31", result["必需Reference"])

        ordinary = evaluate_route(
            manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {
                    "执行模式": ["实现"],
                    "项目形态": ["后端服务"],
                    "阶段": ["功能开发"],
                    "风险": ["L2"],
                    "范围": ["API", "持久化"],
                },
                "未知项": [],
                "依据": ["ordinary backend l2 regression"],
            },
        )
        self.assertNotIn("coding.reference.31", ordinary["必需Reference"])

    def test_runtime_license_public_private_key_exception_is_narrow_and_explicit(self) -> None:
        """Public 仓库的产品私钥例外必须可达、范围固定且不得夸大安全保证。"""
        maintenance = self._read(".agents/MAINTENANCE.md")
        delivery = self._read(
            ".agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md"
        )
        for text in (maintenance, delivery):
            for fragment in (
                "Agent_Skills Runtime License 项目级安全例外",
                "dingyuwen777/Agent_Skills",
                "licensing/private_key.pem",
                "licensing/public_key.pem",
                "licensing/license_tool.py",
                "Public",
                "其他仓库",
                "Token",
                "密码",
                "Runtime binary",
                "Project Payload",
                "Release ZIP",
                "目标项目",
                "MCP 返回",
                "Builder JSON",
            ):
                with self.subTest(fragment=fragment):
                    self.assertIn(fragment, text)

        self.assertIn("不再以 `visibility=private` 为前提", maintenance)
        self.assertIn("不再要求 `visibility=private`", delivery)
        self.assertIn("任何读取仓库的人都可以自行签发", maintenance)
        self.assertIn("任何读取仓库的人都能自行生成/续期合法 License", delivery)
        self.assertIn("不得宣称该部署能防止用户伪造授权", maintenance)
        self.assertIn("不得宣称防伪造授权", delivery)

        for text in (maintenance, delivery):
            self.assertNotIn("仓库为 Public 时产品私钥必须不存在", text)
            self.assertNotIn("Public 状态必须保持签发 fail closed", text)

    def test_core_tdd_debugging_and_completion_rules_remain(self) -> None:
        """通用化不得删除 TDD、根因调试、Traceability 和 Completion Audit。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("Red\n→ Verify Red：实际确认因正确目标行为失败", skill)
        self.assertIn("连续三次修复假设失败", skill)
        self.assertIn("Requirement Traceability", skill)
        self.assertIn("Validation Matrix", skill)
        self.assertIn("Completion Audit", skill)
        self.assertIn("内容守恒优先于篇幅精简", skill)




    def test_commit_hygiene_keeps_process_noise_out_of_formal_history(self) -> None:
        """过程性状态默认不提交，同时保留有价值 checkpoint。"""
        delivery = self._read(".agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md")
        for marker in ("正式 commit 需有独立审查/回滚/bisect/审计价值", "临时 CI/debug/formatter/generated", "为取 Red 暂移治理文件", "可复现 Red", "不为减 commit 数重写共享历史"):
            self.assertIn(marker, delivery)

    def test_natural_language_dev_flow_requires_human_local_acceptance_before_pr(self) -> None:
        """默认用户可观察开发必须先 Local Ready / 用户验收，再进入首次 push / PR。"""
        core = self._read(".agents/skills/coding/SKILL.md")
        usage = self._read("USAGE.md")
        git_delivery = self._read(
            ".agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md"
        )
        finalization = self._read(
            ".agents/skills/coding/references/23_端到端交付与合并后收尾.md"
        )
        validation = self._read(
            ".agents/skills/coding/references/07_通用验证与证据策略.md"
        )
        testing = self._read(".agents/skills/testing/SKILL.md")

        for marker in (
            "## 1. 快速开始",
            "## 2. 一次正常开发任务怎么进行",
            "## 3. 交付状态与终点",
            "## 4. 常见任务指令",
            "## 5. 用户 / AI 分工与 PR、Review 协作",
            "## 6. 长任务与复杂任务",
            "## 7. 其他使用场景",
            "Local Ready for User Acceptance",
            "等待我本地验收",
            "本地验证通过，提交 PR",
            "不要 push，也不要创建 PR",
            "只 push 当前任务分支，不要直接 push main",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, usage)

        top_level = [
            line for line in usage.splitlines()
            if line.startswith("## ") and len(line) > 3 and line[3].isdigit()
        ]
        self.assertEqual(len(top_level), 7)
        self.assertEqual(
            top_level,
            [
                "## 1. 快速开始",
                "## 2. 一次正常开发任务怎么进行",
                "## 3. 交付状态与终点",
                "## 4. 常见任务指令",
                "## 5. 用户 / AI 分工与 PR、Review 协作",
                "## 6. 长任务与复杂任务",
                "## 7. 其他使用场景",
            ],
        )
        self.assertNotIn("按本文", usage)
        self.assertNotIn("## 18. 常用短指令速查", usage)
        self.assertNotIn("## 14. Git 和团队协作", usage)
        self.assertNotIn("## 标准开发流程（AI 自动执行）", usage)

        flow = usage.split("## 2. 一次正常开发任务怎么进行", 1)[1].split(
            "## 3. 交付状态与终点", 1
        )[0]
        ordered = (
            "AI 获取远程最新 main / 目标分支",
            "AI 保护已有本地工作，自动创建并命名本地任务分支",
            "本地实现",
            "AI 完成与风险相称的技术验证",
            "Local Ready for User Acceptance",
            "用户本人本地验收",
            "用户明确确认通过",
            "AI push / PR 前再次获取远程最新 main / 目标分支",
            "只 push 当前任务分支，不直接 push main",
            "创建或更新 PR",
            "required CI",
            "PR Ready",
        )
        positions = [flow.index(marker) for marker in ordered]
        self.assertEqual(positions, sorted(positions))

        for marker in (
            "Human Local Acceptance Gate（适用时）",
            "Local Ready for User Acceptance",
            "PENDING",
            "不得自动 push/PR",
        ):
            self.assertIn(marker, core)

        for marker in (
            "PENDING",
            "PASSED",
            "NOT_APPLICABLE",
            "USER_WAIVED",
            "Agent **不得自行把 PENDING 提升为 PASSED**",
            "PENDING 时首次 push / PR 必须停止",
            "Local Ready for User Acceptance",
            "push / PR 前重新核对目标分支 freshness",
        ):
            self.assertIn(marker, finalization)

        for marker in (
            "Human Local Acceptance Gate",
            "PENDING 禁止首次 push / PR",
            "push / PR 前目标分支 freshness",
            "不得用早期 PR 绕过 Human Gate",
        ):
            self.assertIn(marker, git_delivery)

        self.assertIn("不等于用户本人已经执行本地验收", validation)
        self.assertIn("不能替用户本人生成 `PASSED`", testing)

if __name__ == "__main__":
    unittest.main()
