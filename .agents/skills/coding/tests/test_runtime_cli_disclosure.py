"""验证 Runtime CLI 成功输出不泄露内部治理资产身份。"""

from __future__ import annotations

import unittest

from runtime.agent_skills_runtime import server


class RuntimeCliDisclosureTest(unittest.TestCase):
    """覆盖最终用户直接运行 Runtime binary 时的公开安装结果。"""

    def test_public_install_result_hides_internal_install_identity(self) -> None:
        """安装器内部可保留完整结果，但 CLI 只能输出用户完成安装所需的最小信息。"""
        internal = {
            "ok": True,
            "target": "D:/work/project",
            "release_version": "2.1.0",
            "source_digest": "source-secret",
            "payload_digest": "payload-secret",
            "skills": ["coding", "docs", "review"],
            "shared_files": ["ROUTER.md"],
            "removed_skills": ["legacy-skill"],
            "removed_shared_files": ["OLD_ROUTER.md"],
            "removed_managed_files": ["coding/SKILL.md"],
            "runtime": ".agents/runtime/agent-skills-mcp.exe",
            "manifest": ".agents/agent-skills-install.json",
            "hosts": ["codex", "cursor", "claude-code"],
        }

        public = server._public_install_result(internal)

        self.assertEqual(
            public,
            {
                "ok": True,
                "target": "D:/work/project",
                "release_version": "2.1.0",
                "hosts": ["codex", "cursor", "claude-code"],
            },
        )
        serialized = str(public)
        for forbidden in (
            "coding",
            "docs",
            "review",
            "ROUTER.md",
            ".agents/runtime",
            "agent-skills-install.json",
            "source-secret",
            "payload-secret",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
