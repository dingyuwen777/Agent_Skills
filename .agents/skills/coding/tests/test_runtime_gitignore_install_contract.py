from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_installer import CACHE_IGNORE_RULE, _updated_gitignore, install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_IGNORE_RULE = "/.agents/runtime/"
RUNTIME_REFERENCE = ROOT / ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"
BOOTSTRAP_REFERENCE = ROOT / ".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md"
RUNTIME_README = ROOT / "runtime/README.md"
INSTALLER_SOURCE = ROOT / "runtime/agent_skills_runtime/project_installer.py"


class RuntimeGitignoreInstallContractTest(unittest.TestCase):
    """验证 Runtime 安装不认领目标项目的 Runtime ignore，只维护本地缓存 ignore。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical Source 构建真实 Project Payload，供安装级回归复用。"""
        cls.payload = build_project_payload(ROOT, build_bundle(ROOT))

    def _install(self, target: Path, artifact: Path) -> dict[str, object]:
        """使用真实 Project Payload 执行一次隔离项目安装。"""
        return install_project(target, self.payload, artifact, release_version="9.9.9")

    def test_gitignore_helper_adds_cache_only_for_new_file(self) -> None:
        """新建 .gitignore 时只能加入缓存规则，不能自动加入 Runtime ignore。"""
        updated = _updated_gitignore(None).decode("utf-8")
        self.assertIn(CACHE_IGNORE_RULE, updated)
        self.assertNotIn(RUNTIME_IGNORE_RULE, updated)
        self.assertNotIn("Agent Skills local runtime/cache", updated)

    def test_first_install_does_not_add_runtime_ignore_and_reinstall_is_idempotent(self) -> None:
        """首次与同 artifact 重复安装均不得把 Runtime 目录写入 .gitignore。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            artifact = root / "agent-skills.exe"
            artifact.write_bytes(b"runtime-gitignore-contract")

            first = self._install(target, artifact)
            first_gitignore = (target / ".gitignore").read_bytes()
            self.assertEqual(first["ownership_source"], "first-install")
            self.assertIn(CACHE_IGNORE_RULE.encode("utf-8"), first_gitignore)
            self.assertNotIn(RUNTIME_IGNORE_RULE.encode("utf-8"), first_gitignore)
            self.assertEqual(
                (target / ".agents/runtime/agent-skills.exe").read_bytes(),
                b"runtime-gitignore-contract",
            )

            second = self._install(target, artifact)
            self.assertEqual(second["ownership_source"], "same-artifact")
            self.assertEqual((target / ".gitignore").read_bytes(), first_gitignore)
            cursor = json.loads((target / ".cursor/mcp.json").read_text(encoding="utf-8"))
            self.assertIn(".agents${pathSeparator}runtime${pathSeparator}agent-skills.exe", cursor["mcpServers"]["agent-skills"]["command"])

    def test_existing_gitignore_without_runtime_rule_keeps_project_bytes_and_crlf(self) -> None:
        """已有项目规则保持原顺序/CRLF，只追加缓存 ignore，不追加 Runtime ignore。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            original = b"node_modules/\r\n*.log\r\n"
            (target / ".gitignore").write_bytes(original)
            artifact = root / "agent-skills.exe"
            artifact.write_bytes(b"runtime-existing-gitignore")

            self._install(target, artifact)
            updated = (target / ".gitignore").read_bytes()

            self.assertTrue(updated.startswith(original))
            self.assertNotIn(RUNTIME_IGNORE_RULE.encode("utf-8"), updated)
            self.assertEqual(updated.count(CACHE_IGNORE_RULE.encode("utf-8")), 1)
            self.assertNotIn(b"\n", updated.replace(b"\r\n", b""))

    def test_existing_project_owned_runtime_ignore_is_preserved_not_owned(self) -> None:
        """项目原本已有 Runtime ignore 时保持原样，不删除、不重复追加。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            original = b"node_modules/\n/.agents/runtime/\n*.log\n"
            (target / ".gitignore").write_bytes(original)
            artifact = root / "agent-skills.exe"
            artifact.write_bytes(b"runtime-project-owned-ignore")

            self._install(target, artifact)
            updated = (target / ".gitignore").read_bytes()

            self.assertTrue(updated.startswith(original))
            self.assertEqual(updated.count(RUNTIME_IGNORE_RULE.encode("utf-8")), 1)
            self.assertEqual(updated.count(CACHE_IGNORE_RULE.encode("utf-8")), 1)

    def test_installer_source_has_no_runtime_ignore_owner_constant(self) -> None:
        """安装器不再保留可把 Runtime 目录重新定义成自动 ignore 的 Owner 常量。"""
        source = INSTALLER_SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("RUNTIME_IGNORE_RULE", source)

    def test_canonical_install_contract_does_not_require_runtime_ignore(self) -> None:
        """Bootstrap/Runtime canonical Owner 与维护说明必须明确不自动写 Runtime ignore。"""
        bootstrap = BOOTSTRAP_REFERENCE.read_text(encoding="utf-8")
        runtime = RUNTIME_REFERENCE.read_text(encoding="utf-8")
        readme = RUNTIME_README.read_text(encoding="utf-8")

        for text in (bootstrap, runtime, readme):
            self.assertIn("不自动新增", text)
            self.assertIn("项目原本已有", text)
        self.assertNotIn("所有目标项目应显式忽略", bootstrap)
        self.assertNotIn("`.agents/runtime/` 是目标项目本地运行资产，应加入 `.gitignore`", runtime)
        self.assertNotIn("`.agents/runtime/` 为项目本地运行资产并加入 `.gitignore`", readme)


if __name__ == "__main__":
    unittest.main()
