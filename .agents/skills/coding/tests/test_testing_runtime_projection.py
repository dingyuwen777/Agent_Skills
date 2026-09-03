from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]


class TestingRuntimeProjectionTest(unittest.TestCase):
    """显式锁定 Testing Skill 在 Runtime Projection 中的核心 Ownership/Handoff 语义与 Reference identity 防披露。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从真实 canonical bundle 构建当前 Project Payload。"""
        cls.bundle = build_bundle(ROOT)
        cls.payload = build_project_payload(ROOT, cls.bundle)
        for entry in cls.payload["files"]:
            if str(entry["path"]) == "testing/SKILL.md":
                cls.runtime_testing = decode_payload_file(entry).decode("utf-8")
                break
        else:
            raise AssertionError("Project Payload 缺少 testing/SKILL.md")

    def test_testing_projection_preserves_professional_owner_semantics(self) -> None:
        """去身份化不能删除 Testing 的专业方法 Owner、黑盒、Regression 与回程语义。"""
        for marker in (
            "Testing 唯一负责的专业方法",
            "Scenario-based Black-box Acceptance",
            "User Journey",
            "Exploratory Testing",
            "Regression",
            "Handoff Coding",
            "test-only",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.runtime_testing)

    def test_testing_projection_hides_all_canonical_reference_identities(self) -> None:
        """Testing Runtime Core 仍不得暴露任一 canonical Reference 文件名、路径或 Stable ID。"""
        self.assertNotIn("references/", self.runtime_testing)
        for reference in self.bundle["references"]:
            for field in ("filename", "source_path", "id"):
                with self.subTest(field=field, value=reference[field]):
                    self.assertNotIn(str(reference[field]), self.runtime_testing)


if __name__ == "__main__":
    unittest.main()
