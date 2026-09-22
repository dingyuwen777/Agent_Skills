from __future__ import annotations

import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / ".github/scripts/actions_hygiene.py"
MODULE = runpy.run_path(str(SCRIPT))
SCOPE_MODULE = runpy.run_path(str(ROOT / ".github/scripts/runtime_package_scope.py"))
CLASSIFY_PATH = SCOPE_MODULE["classify_path"]
BUILD_PLAN = MODULE["build_cleanup_plan"]
PATH_IN_HISTORY = MODULE["path_existed_in_head_history"]
RUN_HYGIENE = MODULE["run_hygiene"]
RUNTIME_GLOBALS = RUN_HYGIENE.__globals__
MAIN = MODULE["main"]
MAIN_GLOBALS = MAIN.__globals__
TRANSIENT_ERROR = MODULE["TransientGitHubApiError"]


class ActionsHygieneTest(unittest.TestCase):
    """验证 Actions Hygiene 只清理可证明失效且已完成的 Workflow 历史。"""

    def test_current_workflow_is_always_protected(self) -> None:
        """当前 main 仍存在的 Workflow 即使有 completed runs 也不得进入删除集合。"""
        path = ".github/workflows/skill-tests.yml"
        plan = BUILD_PLAN(
            {path},
            {path},
            [{"id": 1, "path": path, "name": "Skill Tests", "status": "completed"}],
        )
        self.assertEqual(plan["eligible_runs"], [])
        self.assertEqual(plan["protected_current_workflows"], [path])

    def test_pr_only_workflow_is_not_a_cleanup_candidate(self) -> None:
        """只在 PR branch 出现、没有进入 main 祖先历史的 Workflow 不得删除。"""
        path = ".github/workflows/pr-only.yml"
        plan = BUILD_PLAN(
            {".github/workflows/skill-tests.yml"},
            set(),
            [{"id": 2, "path": path, "name": "PR only", "status": "completed"}],
        )
        self.assertEqual(plan["eligible_runs"], [])
        self.assertEqual(plan["skipped_not_main_history"], [path])

    def test_active_run_skips_entire_obsolete_workflow(self) -> None:
        """候选 Workflow 只要还有未完成 run，就连已完成历史也暂不删除。"""
        path = ".github/workflows/old.yml"
        plan = BUILD_PLAN(
            {".github/workflows/skill-tests.yml"},
            {path},
            [
                {"id": 3, "path": path, "name": "Old", "status": "completed"},
                {"id": 4, "path": path, "name": "Old", "status": "in_progress"},
            ],
        )
        self.assertEqual(plan["eligible_runs"], [])
        self.assertEqual(plan["skipped_active_workflows"], {path: ["in_progress"]})

    def test_completed_obsolete_workflow_produces_stable_delete_plan(self) -> None:
        """已从 main 消失且只剩 completed runs 的 Workflow 应按 run id 稳定进入删除计划。"""
        path = ".github/workflows/old.yml"
        plan = BUILD_PLAN(
            {".github/workflows/skill-tests.yml"},
            {path},
            [
                {"id": 8, "path": path, "name": "Old", "status": "completed"},
                {"id": 7, "path": path, "name": "Old", "status": "completed"},
            ],
        )
        self.assertEqual([item["id"] for item in plan["eligible_runs"]], [7, 8])
        self.assertEqual(plan["candidate_workflows"], [path])

    def test_git_history_check_distinguishes_main_history_from_unmerged_path(self) -> None:
        """真实 Git HEAD 祖先历史必须能区分已合入后删除的 path 与从未合入的 path。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "ci@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(["git", "config", "user.name", "CI"], cwd=root, check=True)
            workflow = root / ".github/workflows/old.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("name: Old\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "add old workflow"], cwd=root, check=True)
            workflow.unlink()
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "remove old workflow"], cwd=root, check=True)

            self.assertTrue(PATH_IN_HISTORY(root, ".github/workflows/old.yml"))
            self.assertFalse(PATH_IN_HISTORY(root, ".github/workflows/pr-only.yml"))

    def test_first_parent_history_rejects_pr_only_merged_branch_path(self) -> None:
        """merge commit 含支线祖先时，只存在于支线且合并前删除的 Workflow 仍不得视为 main 历史。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "ci@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "CI"], cwd=root, check=True)
            (root / "README.md").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)

            subprocess.run(["git", "switch", "-qc", "feature"], cwd=root, check=True)
            workflow = root / ".github/workflows/pr-only.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("name: PR only\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "add pr-only workflow"], cwd=root, check=True)
            workflow.unlink()
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "remove pr-only workflow"], cwd=root, check=True)

            subprocess.run(["git", "switch", "-q", "main"], cwd=root, check=True)
            subprocess.run(["git", "merge", "--no-ff", "-qm", "merge feature", "feature"], cwd=root, check=True)

            self.assertFalse(PATH_IN_HISTORY(root, ".github/workflows/pr-only.yml"))

    def test_execute_deletes_snapshot_then_requires_fresh_zero_readback(self) -> None:
        """execute 必须基于初始快照删除，并以 fresh readback 的零残留作为成功条件。"""
        old_list = RUNTIME_GLOBALS["list_workflow_runs"]
        old_current = RUNTIME_GLOBALS["current_workflow_paths"]
        old_history = RUNTIME_GLOBALS["main_history_workflow_paths"]
        old_request = RUNTIME_GLOBALS["_api_request"]
        snapshots = [
            [{"id": 10, "path": ".github/workflows/old.yml", "name": "Old", "status": "completed"}],
            [],
        ]
        deletes: list[str] = []
        try:
            RUNTIME_GLOBALS["list_workflow_runs"] = lambda repository, token: snapshots.pop(0)
            RUNTIME_GLOBALS["current_workflow_paths"] = lambda root: {".github/workflows/skill-tests.yml"}
            RUNTIME_GLOBALS["main_history_workflow_paths"] = (
                lambda root, observed: {".github/workflows/old.yml"} & set(observed)
            )
            RUNTIME_GLOBALS["_api_request"] = (
                lambda token, method, path: deletes.append(path) if method == "DELETE" else None
            )
            payload = RUN_HYGIENE(
                ROOT,
                "dingyuwen777/Agent_Skills",
                "fixture-token",
                execute=True,
            )
        finally:
            RUNTIME_GLOBALS["list_workflow_runs"] = old_list
            RUNTIME_GLOBALS["current_workflow_paths"] = old_current
            RUNTIME_GLOBALS["main_history_workflow_paths"] = old_history
            RUNTIME_GLOBALS["_api_request"] = old_request

        self.assertEqual(deletes, ["/repos/dingyuwen777/Agent_Skills/actions/runs/10"])
        self.assertEqual(payload["deleted_run_count"], 1)
        self.assertEqual(payload["remaining_eligible_run_count"], 0)

    def test_execute_fails_when_fresh_readback_still_has_eligible_run(self) -> None:
        """DELETE 后 fresh readback 仍见 eligible run 时必须失败关闭，不能宣称清理完成。"""
        old_list = RUNTIME_GLOBALS["list_workflow_runs"]
        old_current = RUNTIME_GLOBALS["current_workflow_paths"]
        old_history = RUNTIME_GLOBALS["main_history_workflow_paths"]
        old_request = RUNTIME_GLOBALS["_api_request"]
        run = {"id": 11, "path": ".github/workflows/old.yml", "name": "Old", "status": "completed"}
        try:
            RUNTIME_GLOBALS["list_workflow_runs"] = lambda repository, token: [run]
            RUNTIME_GLOBALS["current_workflow_paths"] = lambda root: {".github/workflows/skill-tests.yml"}
            RUNTIME_GLOBALS["main_history_workflow_paths"] = (
                lambda root, observed: {".github/workflows/old.yml"} & set(observed)
            )
            RUNTIME_GLOBALS["_api_request"] = lambda token, method, path: None
            with self.assertRaisesRegex(RuntimeError, "fresh readback"):
                RUN_HYGIENE(
                    ROOT,
                    "dingyuwen777/Agent_Skills",
                    "fixture-token",
                    execute=True,
                )
        finally:
            RUNTIME_GLOBALS["list_workflow_runs"] = old_list
            RUNTIME_GLOBALS["current_workflow_paths"] = old_current
            RUNTIME_GLOBALS["main_history_workflow_paths"] = old_history
            RUNTIME_GLOBALS["_api_request"] = old_request

    def test_actions_hygiene_script_uses_governance_ci_profile(self) -> None:
        """只修改 Hygiene 脚本时应走治理证据，不误触发三平台 Runtime package。"""
        self.assertEqual(CLASSIFY_PATH(".github/scripts/actions_hygiene.py"), "governance")

    def test_cli_distinguishes_transient_and_hard_failures(self) -> None:
        """CLI 只把临时 GitHub API 错误映射为 75，硬错误必须保持普通失败。"""
        import sys

        old_run = MAIN_GLOBALS["run_hygiene"]
        old_token = MAIN_GLOBALS["_token"]
        old_argv = sys.argv[:]
        try:
            MAIN_GLOBALS["_token"] = lambda: "fixture-token"
            sys.argv = ["actions_hygiene.py", "--repository", "owner/repo"]

            def transient(*args, **kwargs):
                raise TRANSIENT_ERROR("temporary")

            MAIN_GLOBALS["run_hygiene"] = transient
            self.assertEqual(MAIN(), 75)

            def hard(*args, **kwargs):
                raise RuntimeError("hard")

            MAIN_GLOBALS["run_hygiene"] = hard
            self.assertEqual(MAIN(), 1)
        finally:
            MAIN_GLOBALS["run_hygiene"] = old_run
            MAIN_GLOBALS["_token"] = old_token
            sys.argv = old_argv

    def test_skill_tests_owns_hygiene_with_narrow_permissions(self) -> None:
        """永久清理必须复用 Skill Tests，并把 actions:write 限制在独立 main-only job。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        header, jobs = workflow.split("jobs:", 1)
        self.assertNotIn("actions: write", header)
        self.assertIn("  actions-hygiene:", jobs)
        hygiene = jobs.split("  actions-hygiene:", 1)[1]
        for fragment in (
            "name: Actions Hygiene",
            "github.event_name == 'push'",
            "refs/heads/main",
            "actions: write",
            "contents: read",
            "fetch-depth: 0",
            ".github/scripts/actions_hygiene.py",
            "--execute",
            "::warning::Actions Hygiene temporary GitHub API failure",
            "Actions Hygiene invariant/permission failure",
            'status}" -eq 75',
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, hygiene)


if __name__ == "__main__":
    unittest.main()
