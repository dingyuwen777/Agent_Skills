from __future__ import annotations

import unittest

from runtime.agent_skills_runtime.runtime_skill_projection import (
    project_runtime_agent_prompt,
    project_runtime_skill_core,
)


class RuntimeProjectionProjectLiteralTest(unittest.TestCase):
    """验证 project-facing 投影只去内部组织语义，不破坏项目自身技术字面量。"""

    def test_skill_projection_preserves_project_technical_literals(self) -> None:
        """框架名、环境变量、控制面和业务 Reference/Skill 术语必须保持原文。"""
        source = """---
name: frontend-helper
description: 维护 React Router 与 React Testing Library 的项目工程规则。
---

<!-- agent-routing:v1
{"协议":"fixture","Skill":"frontend-helper","触发":{}}
-->

# Frontend Helper

项目使用 React Router 和 React Testing Library。
Reference implementation 由现有代码提供；Alexa Skill 是业务领域概念。
启动命令读取 `$PORT`，Kubernetes 控制面和网络路由均属于项目真实技术事实。
Skill 提到了 Route；After Coding fixes 需要 Testing Regression。
内部执行由 Router 选择 Skill，并通过 Reference/Handoff 取得约束。
"""
        runtime = project_runtime_skill_core(source.encode("utf-8"), []).decode("utf-8")

        for preserved in (
            "React Router",
            "React Testing Library",
            "Reference implementation",
            "Alexa Skill",
            "$PORT",
            "Kubernetes 控制面",
            "网络路由",
        ):
            with self.subTest(preserved=preserved):
                self.assertIn(preserved, runtime)

        self.assertNotIn("agent-routing:v1", runtime)
        self.assertNotIn("由 Router 选择 Skill", runtime)
        self.assertNotIn("Reference/Handoff", runtime)
        self.assertNotIn("Skill 提到了", runtime)
        self.assertNotIn("After Coding fixes", runtime)
        self.assertNotIn("Testing Regression", runtime)

    def test_agent_prompt_removes_only_current_skill_assignment(self) -> None:
        """只去除当前条目 `$name` 激活；项目 `$PORT` 即使位于 Use 语句也必须原样保留。"""
        source = """interface:
  display_name: "Frontend"
  short_description: "fixture"
  default_prompt: "Use $coding. Run the current application with $PORT and complete validation."
"""
        runtime = project_runtime_agent_prompt(source.encode("utf-8"), "coding").decode("utf-8")

        self.assertNotIn("Use $coding", runtime)
        self.assertIn("$PORT", runtime)
        self.assertIn("current", runtime.lower())
        self.assertIn("validation", runtime.lower())

        port_source = """interface:
  display_name: "Frontend"
  short_description: "fixture"
  default_prompt: "Use $PORT for the current application and complete validation."
"""
        port_runtime = project_runtime_agent_prompt(port_source.encode("utf-8"), "coding").decode("utf-8")
        self.assertIn("Use $PORT", port_runtime)


if __name__ == "__main__":
    unittest.main()