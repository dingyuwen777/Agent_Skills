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
GITHUB_SCRIPTS = ROOT / ".github" / "scripts"
if str(GITHUB_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(GITHUB_SCRIPTS))

import check_pr_requirement_source as subject  # noqa: E402


TECHNICAL_BODY = """## 动机 / 根因
当前治理资产可以因宿主差异发生漂移。

## 当前状态
PR gate 只验证部分来源事实。

## 目标状态
Requirement Source 由同一机器 Contract 验证。

## 范围
PR Requirement Source 与治理门禁。

## 非目标
不修改业务功能。

## 兼容与迁移
无数据迁移；历史记录保持不变。

## 风险与回滚
误判时 revert 当前 PR。

## 验收标准
- [ ] AC1：真实 Issue 满足当前 Profile
- [ ] AC2：不合规 Issue 稳定失败

## 验证要求
运行 targeted unit tests。

## 上游事实源 / 相关资料
canonical Coding 规则。
"""


class RequirementSourceValidationTests(unittest.TestCase):
    """覆盖 Requirement Source 的合法来源、拒绝路径和 CLI fast path。"""

    def _issue(
        self,
        *,
        body: str | None = None,
        title: str = "[技术变更] 稳定治理门禁",
    ) -> dict[str, object]:
        """返回满足当前机器 Contract 的 GitHub Issue 假响应。"""
        return {
            "title": title,
            "body": TECHNICAL_BODY if body is None else body,
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
        """当前 checkout 中真实存在的仓库相对正式文件可以作为来源。"""
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

    def test_repository_directory_is_rejected(self) -> None:
        """目录不能冒充可审查的 Requirement Source 文件。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "specs").mkdir()
            with self.assertRaisesRegex(subject.RequirementSourceError, "仓库文件"):
                subject.validate_requirement_sources(
                    "Requirement-Source: specs",
                    root,
                    lambda _: self._issue(),
                )

    def test_coding_change_path_cannot_be_requirement_source(self) -> None:
        """Coding Change 是施工契约，不能通过仓库路径绕过上游 Requirement Source 规则。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / ".agents" / "changes" / "active" / "CHG-test" / "CHANGE.md"
            change.parent.mkdir(parents=True)
            change.write_text("# Change\n", encoding="utf-8")
            with self.assertRaisesRegex(subject.RequirementSourceError, "施工契约"):
                subject.validate_requirement_sources(
                    "Requirement-Source: .agents/changes/active/CHG-test/CHANGE.md",
                    root,
                    lambda _: self._issue(),
                )

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
        """真实 GitHub Issue 且实例满足当前机器 Contract 时通过来源门禁。"""
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

    def test_empty_issue_body_is_rejected(self) -> None:
        """真实 Issue 仍必须有非空正文，空载体不能满足机器追溯。"""
        payload = self._issue(body="")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "标题或正文"):
                subject.validate_requirement_sources(
                    "Requirement-Source: #131",
                    Path(directory),
                    lambda _: payload,
                )

    def test_issue_without_standard_type_prefix_is_rejected(self) -> None:
        """API 直接创建的 Issue 也必须保留标准 Requirement Source 类型身份。"""
        payload = self._issue(title="Stabilize CI gates")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "标题"):
                subject.validate_requirement_sources(
                    "Requirement-Source: #131",
                    Path(directory),
                    lambda _: payload,
                )

    def test_issue_missing_machine_profile_section_is_rejected(self) -> None:
        """只有局部摘要与 AC 的 Issue 不能冒充完整 Requirement Source。"""
        payload = self._issue(body="## 验收标准\n- [ ] AC1：完成治理改造")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "必需语义段"):
                subject.validate_requirement_sources(
                    "Requirement-Source: #131",
                    Path(directory),
                    lambda _: payload,
                )

    def test_issue_acceptance_must_use_contiguous_task_list(self) -> None:
        """Requirement Source 的最终 Acceptance Owner 必须是连续可回写 task list。"""
        payload = self._issue(body=TECHNICAL_BODY.replace("AC2：", "AC3："))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(subject.RequirementSourceError, "连续"):
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
                    str(ROOT / ".github" / "scripts" / "check_pr_requirement_source.py"),
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
        self.assertIn("需要 post-merge evidence", template)
        self.assertIn("不得使用 `Closes` / `Fixes` / `Resolves`", template)
        self.assertIn("Closure Audit", template)


if __name__ == "__main__":
    unittest.main()
