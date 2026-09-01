"""验证 Agent_Skills 自身 PR Requirement Source 机器门禁。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_pr_requirement_source as subject  # noqa: E402


class RequirementSourceValidationTests(unittest.TestCase):
    """覆盖 Requirement Source 的合法来源、拒绝路径和 CLI fast path。"""

    def _issue(self, *, body: str | None = None) -> dict[str, object]:
        """返回满足当前最小机器结构的 GitHub Issue 假响应。"""
        return {
            "title": "治理变更",
            "body": body or "## 目标\n完成治理改造\n\n## 验收标准\n- Gate 可验证",
        }

    def test_extracts_multiple_requirement_sources_without_duplicates(self) -> None:
        """同一 PR 可以引用多个稳定来源，重复行不应重复校验。"""
        body = """
        Requirement-Source: #131
        Requirement-Source: AGENTS.md
        Requirement-Source: #131
        """
        self.assertEqual(
            subject.extract_requirement_sources(body),
            ("#131", "AGENTS.md"),
        )

    def test_missing_requirement_source_is_rejected(self) -> None:
        """只有关闭关键字或普通 PR 描述时必须失败。"""
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "缺少"):
                subject.validate_requirement_sources(
                    "Closes #131",
                    Path(directory),
                    lambda _: self._issue(),
                )

    def test_placeholder_requirement_source_is_rejected(self) -> None:
        """PR 模板占位文本不能成为可合并证据。"""
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "占位"):
                subject.validate_requirement_sources(
                    "Requirement-Source: #<Issue>",
                    Path(directory),
                    lambda _: self._issue(),
                )

    def test_existing_repository_path_is_accepted(self) -> None:
        """当前 checkout 中真实存在的仓库相对正式路径可以作为来源。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "specs").mkdir()
            (root / "specs" / "design.md").write_text("# Design\n", encoding="utf-8")
            sources = subject.validate_requirement_sources(
                "Requirement-Source: specs/design.md",
                root,
                lambda _: self._issue(),
            )
            self.assertEqual(sources, ("specs/design.md",))

    def test_repository_path_escape_is_rejected(self) -> None:
        """相对路径不能通过 `..` 越过仓库根目录。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root.parent / "outside.md").write_text("secret", encoding="utf-8")
            with self.assertRaisesRegex(subject.RequirementSourceError, "路径逃逸"):
                subject.validate_requirement_sources(
                    "Requirement-Source: ../outside.md",
                    root,
                    lambda _: self._issue(),
                )

    def test_valid_issue_source_is_accepted(self) -> None:
        """真实 GitHub Issue 且包含目标与验收结构时通过。"""
        seen: list[int] = []

        def loader(issue_number: int) -> dict[str, object]:
            """记录被校验的 Issue 编号并返回合法假响应。"""
            seen.append(issue_number)
            return self._issue()

        with tempfile.TemporaryDirectory() as directory:
            sources = subject.validate_requirement_sources(
                "Requirement-Source: #131",
                Path(directory),
                loader,
            )
        self.assertEqual(sources, ("#131",))
        self.assertEqual(seen, [131])

    def test_pull_request_cannot_be_used_as_issue_requirement_source(self) -> None:
        """GitHub `/issues` API 返回 PR 载体时必须拒绝作者自证。"""
        payload = self._issue()
        payload["pull_request"] = {"url": "https://api.github.test/pulls/1"}
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "Pull Request"):
                subject.validate_requirement_sources(
                    "Requirement-Source: #131",
                    Path(directory),
                    lambda _: payload,
                )

    def test_issue_without_acceptance_structure_is_rejected(self) -> None:
        """只有标题和背景、没有验收语义的 Issue 不足以通过机器结构门禁。"""
        payload = self._issue(body="## 目标\n只描述目标，不写完成判断")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "验收"):
                subject.validate_requirement_sources(
                    "Requirement-Source: #131",
                    Path(directory),
                    lambda _: payload,
                )

    def test_non_pr_event_uses_explicit_fast_path(self) -> None:
        """main push 不应伪造 PR 需求来源，而应明确 not_applicable 并成功。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_path = root / "event.json"
            event_path.write_text(json.dumps({"ref": "refs/heads/main"}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "check_pr_requirement_source.py"),
                    "--root",
                    str(ROOT),
                    "--event-path",
                    str(event_path),
                ],
                cwd=ROOT,
                env={**os.environ, "GITHUB_TOKEN": ""},
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not_applicable", result.stdout)

    def test_repository_pr_template_keeps_traceability_contract(self) -> None:
        """Agent_Skills 自身 PR 模板必须保留稳定字段及关闭语义说明。"""
        template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
        self.assertIn("Requirement-Source:", template)
        self.assertIn("Closes", template)
        self.assertIn("不要用关闭关键字替代", template)


if __name__ == "__main__":
    unittest.main()
