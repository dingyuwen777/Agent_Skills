from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class DocsSkillIntegrationTest(unittest.TestCase):
    """验证 Docs 正式规则保持通用、事实优先，并可独立于辅助 README 使用。"""

    def _read(self, path: str) -> str:
        """读取仓库中的正式文档规则。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_docs_skill_is_project_agnostic_and_self_describing(self) -> None:
        """删除 Docs README 后，主 SKILL 仍必须完整表达 Docs 的入口、事实和失败路由。"""
        skill = self._read(".agents/skills/docs/SKILL.md")
        for marker in (
            "为什么存在",
            "第二套事实",
            "code_issue_detected",
            "既可以独立用于文档 Review / 编写 / 更新",
            "not_applicable",
            "targeted",
            "full",
        ):
            self.assertIn(marker, skill)
        self.assertFalse((ROOT / ".agents/skills/docs/README.md").exists())

    def test_first_principles_examples_cover_multiple_project_shapes(self) -> None:
        """Docs 写作示例应覆盖通用数据流、CLI 和设备控制流，而不是固定业务链。"""
        writing = self._read(".agents/skills/docs/references/02_第一性原理技术写作.md")
        self.assertIn("外部来源", writing)
        self.assertIn("CLI 参数", writing)
        self.assertIn("设备协议输入", writing)
        self.assertIn("术语后置", writing)
        self.assertIn("Greenfield / Bootstrap Guide", writing)

    def test_repository_file_references_keep_path_and_clickable_link(self) -> None:
        """Docs 必须让承担导航职责的真实仓库文件跨类型保持完整路径展示和可点击链接。"""
        skill = self._read(".agents/skills/docs/SKILL.md")
        writing = self._read(".agents/skills/docs/references/02_第一性原理技术写作.md")
        workflow = self._read(".agents/skills/docs/references/03_审查编写与修复流程.md")

        self.assertIn("仓库内具体文件引用必须同时可定位、可点击", skill)
        self.assertIn("不论文件类型", skill)
        self.assertNotIn("仓库内具体文档引用必须同时可定位、可点击", skill)

        self.assertIn("仓库内具体文件引用：路径可见且链接可点", writing)
        self.assertIn("link label 使用完整仓库相对路径", writing)
        self.assertIn("link target 使用从当前文档位置可解析的相对路径", writing)
        self.assertIn("不得只写不可点击的 inline-code 路径", writing)
        self.assertIn("最终输出位置重新验证", writing)
        for suffix in ("`.md`", "`.py`", "`.json`", "`.yaml`", "`.yml`", "`.toml`", "`.sql`"):
            self.assertIn(suffix, writing)
        for role in ("源码", "测试", "配置", "Contract", "Schema", "Migration", "脚本"):
            self.assertIn(role, writing)

        self.assertIn("真实仓库文件", workflow)
        self.assertIn("不可点击的 inline-code 路径", workflow)
        self.assertIn("`.py`", workflow)
        self.assertIn("`.json`", workflow)
        self.assertIn("`.yaml`", workflow)
        self.assertIn("`.toml`", workflow)
        self.assertIn("`.sql`", workflow)
        self.assertIn("误把命令、目录树、glob、占位路径", workflow)

    def test_repository_file_link_rule_keeps_non_navigation_exceptions(self) -> None:
        """扩展到代码/配置文件后仍不得把命令、glob、占位路径和代码字面量机械链接化。"""
        skill = self._read(".agents/skills/docs/SKILL.md")
        writing = self._read(".agents/skills/docs/references/02_第一性原理技术写作.md")
        workflow = self._read(".agents/skills/docs/references/03_审查编写与修复流程.md")

        for marker in ("命令", "glob", "占位路径", "目录树", "协议/流程示例", "生成路径", "代码字面量"):
            self.assertIn(marker, writing)
        self.assertIn("不机械链接化", skill)
        self.assertIn("不机械链接化", workflow)


    def test_new_document_admission_and_lifecycle_gates_are_canonical(self) -> None:
        """Docs 必须先找 Owner 再准入新文档，并为阶段性文档保留退出与知识迁移。"""
        skill = self._read(".agents/skills/docs/SKILL.md")
        workflow = self._read(".agents/skills/docs/references/03_审查编写与修复流程.md")

        for marker in (
            "Single Explanation Owner",
            "New Document Admission Gate",
            "已有 Owner 可以合法承载时更新已有 Owner",
            "独立读者任务",
            "Document Growth Gate",
            "Temporary Document Lifecycle / Exit Gate",
            "targeted-first",
            "没有项目阈值时，通用 Agent_Skills 不发明统一的 500/800/1000 行硬上限",
        ):
            self.assertIn(marker, skill)

        for marker in (
            "new_document_admitted",
            "new_document not_admitted",
            "targeted owner search",
            "Document Growth Gate：已有文档也要有增长边界",
            "规模只作为风险信号",
            "按长度机械切块",
            "临时文档的知识迁移与退出",
            "无法证明知识迁移完成时",
        ):
            self.assertIn(marker, workflow)

        self.assertNotIn("AIMA", skill)
        self.assertNotIn("AIMA", workflow)

    def test_owner_overlap_is_not_defined_by_topic_similarity(self) -> None:
        """Docs 必须区分正常交叉引用与多个位置承担完整解释 Owner。"""
        skill = self._read(".agents/skills/docs/SKILL.md")
        workflow = self._read(".agents/skills/docs/references/03_审查编写与修复流程.md")

        self.assertIn("维护责任是否重复", skill)
        self.assertIn("最小上下文", skill)
        self.assertIn("词汇是否相似", skill)
        self.assertIn("主题词相似", workflow)
        self.assertIn("完整解释职责", workflow)

    def test_coding_routes_docs_without_copying_second_rulebook(self) -> None:
        """Coding 有 Docs Impact 硬路由，但详细文档方法仍由 Docs 承担。"""
        coding = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("Docs Impact", coding)
        self.assertIn(".agents/skills/docs/SKILL.md", coding)
        self.assertIn("code_issue_detected", coding)


if __name__ == "__main__":
    unittest.main()
