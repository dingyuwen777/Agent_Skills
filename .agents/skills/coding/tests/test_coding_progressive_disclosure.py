from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CODING_ROOT = ROOT / ".agents/skills/coding"


class CodingProgressiveDisclosureTest(unittest.TestCase):
    """验证 Coding 主规则瘦身只移动详细规则，不丢失任何高价值语义或硬路由。"""

    def _read(self, relative: str) -> str:
        """读取 Coding Skill 下的 UTF-8 文本。"""
        return (CODING_ROOT / relative).read_text(encoding="utf-8")

    def test_main_skill_keeps_hard_invariants_and_routes(self) -> None:
        """主 SKILL 必须继续直接承载不可延迟的全局不变量、停止条件和 Review/Docs 硬路由。"""
        skill = self._read("SKILL.md")
        for marker in (
            "上位规则优先",
            "仓库事实优先",
            "权限边界明确",
            "保护用户工作",
            "完成结论必须有本轮新鲜证据",
            "中文注释与函数级说明是通用规则",
            "Git 提交信息统一中文",
            "所有时间相关默认采用北京时间",
            "日志前缀统一且可定位",
            "连续三次修复假设失败",
            "显式 Code Review / Audit",
            "任何 Coding 实现任务",
            ".agents/skills/docs/SKILL.md",
            "Requirement Traceability",
            "Validation Matrix",
            "Completion Audit",
        ):
            self.assertIn(marker, skill)

    def test_detailed_delivery_and_maintenance_rules_move_to_references_without_loss(self) -> None:
        """被移出主文件的 Git/交付/宿主与规则维护细节必须在专门 reference 中完整可达。"""
        skill = self._read("SKILL.md")
        ref15 = self._read("references/14_Git交付依赖安全与宿主能力边界.md")
        ref16 = self._read("references/15_规则内容守恒与Skill维护.md")
        self.assertIn("14_Git交付依赖安全与宿主能力边界.md", skill)
        self.assertIn("15_规则内容守恒与Skill维护.md", skill)
        for marker in (
            "未经授权不创建分支、提交、推送、PR、合并、部署、删分支",
            "Manifest 改动同步仓库正式 lock",
            "不硬编码、打印、提交或上传 Secret/Token/密码",
            "最终报告至少包含",
            "宿主不支持持久文件、目标工具链、脚本、Git、device、数据库或外部服务时",
        ):
            self.assertIn(marker, ref15)
        for marker in (
            "内容守恒优先于篇幅精简",
            "不能用一条抽象原则替代多条带条件、例外或失败处理的可执行规则",
            "只有逐项证明完全等价时才允许删除重复",
            "完成后从旧入口反向检查每条高价值规则是否仍可达",
        ):
            self.assertIn(marker, ref16)

    def test_github_pr_delivery_has_ready_fallback_and_rest_merge_guard(self) -> None:
        """GitHub PR 交付必须固化 Ready 宿主失败回退与 REST merge 的 head 防漂移门禁。"""
        skill = self._read("SKILL.md")
        delivery = self._read("references/14_Git交付依赖安全与宿主能力边界.md")
        self.assertIn("GitHub PR Ready/merge 宿主兼容策略", skill)
        for marker in (
            "创建 Draft PR",
            "Red / Green / Review / CI",
            "fullDatabaseId",
            "只请求用户在 GitHub 网页执行一次 `Ready for review`",
            "不得循环重试同一失败 GraphQL",
            "重新确认 `draft=false`、CI 和当前 head SHA",
            "REST merge",
            "expected_head_sha",
            "main fresh CI",
            "Change archive",
            "非 GitHub",
            "head/revision guard",
        ):
            self.assertIn(marker, delivery)

    def test_existing_specialized_references_own_network_parallel_and_workflow_details(self) -> None:
        """网络源、多人协作和 Workflow 证据守恒应回到已有职责 reference，主文件仍保留触发入口。"""
        skill = self._read("SKILL.md")
        ref03 = self._read("references/03_编程语言与工具链适配规则.md")
        ref07 = self._read("references/07_通用验证与证据策略.md")
        ref09 = self._read("references/09_多人和多智能体并行协作.md")
        self.assertIn("03_编程语言与工具链适配规则.md", skill)
        self.assertIn("07_通用验证与证据策略.md", skill)
        self.assertIn("09_多人和多智能体并行协作.md", skill)
        self.assertIn("任务明确面向**中国大陆网络**", ref03)
        self.assertIn("Evidence Preservation Mapping", ref07)
        self.assertIn("子 Agent 返回后，主 Agent 必须", ref09)
        self.assertIn("检查实际 diff 和工作区", ref09)
        self.assertIn("运行目标及整体相关验证", ref09)

    def test_main_skill_is_structurally_smaller_without_becoming_a_stub(self) -> None:
        """主文件应明显减少重复细节，但仍保留足够完整的研发主链而不是变成短摘要。"""
        lines = self._read("SKILL.md").splitlines()
        self.assertLessEqual(len(lines), 680)
        self.assertGreaterEqual(len(lines), 450)


if __name__ == "__main__":
    unittest.main()
