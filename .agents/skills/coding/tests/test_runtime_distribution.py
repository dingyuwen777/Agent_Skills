from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTALL_PATH = ROOT / "scripts/install.py"


def _load_module(name: str, path: Path):
    """从指定路径加载脚本模块用于真实文件系统安装测试。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALL = _load_module("runtime_distribution_installer", INSTALL_PATH)


class RuntimeDistributionTest(unittest.TestCase):
    """验证 runtime 模式只分发 Core + Stub，且在任何写入前锁定 Runtime/source digest。"""

    def _source_root(self) -> Path:
        """构造带最小 Bootstrap 能力和 canonical References 的 Agent_Skills fixture。"""
        source = Path(self.source_directory.name)
        managed = (
            "<!-- agent-skills:managed:start -->\n"
            "## Runtime Fixture\n"
            "<!-- agent-skills:managed:end -->\n"
        )
        for skill in ("coding", "review", "docs"):
            skill_root = source / ".agents/skills" / skill
            (skill_root / "references").mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
            (skill_root / "references/01_秘密规则.md").write_text(
                f"# {skill} secret\nTHIS_CANONICAL_BODY_MUST_NOT_BE_DISTRIBUTED_{skill}\n",
                encoding="utf-8",
            )
        coding = source / ".agents/skills/coding"
        (coding / "assets").mkdir()
        (coding / "assets/AGENTS.managed.md").write_text(managed, encoding="utf-8")
        (coding / "scripts").mkdir()
        (coding / "scripts/coding.py").write_text(
            "import argparse, json\n"
            "from pathlib import Path\n"
            "p=argparse.ArgumentParser(); p.add_argument('command'); p.add_argument('--root'); p.add_argument('--json',action='store_true'); a=p.parse_args()\n"
            "root=Path(a.root); (root/'AGENTS.md').write_text('# Target\\n',encoding='utf-8'); (root/'.gitignore').write_text('.agents/project-context.json\\n',encoding='utf-8')\n"
            "print(json.dumps({'agents':'created','gitignore':'created'}))\n",
            encoding="utf-8",
        )
        return source

    def _runtime_command(self, source: Path, digest_override: str | None = None) -> list[str]:
        """创建只实现 status/self-test 的测试 Runtime 命令，模拟已安装 onefile artifact。"""
        bundle = INSTALL._load_runtime_bundle(source)
        digest = digest_override or bundle["source_digest"]
        script = Path(self.source_directory.name) / "fake_runtime.py"
        script.write_text(
            "import json\n"
            f"payload={{'ok': True, 'source_digest': {digest!r}, 'bundle_version': 'fixture', 'reference_count': 3}}\n"
            "print(json.dumps(payload))\n",
            encoding="utf-8",
        )
        return [sys.executable, str(script)]

    def setUp(self) -> None:
        """为每个 Runtime 分发测试建立隔离源和目标目录。"""
        self.source_directory = tempfile.TemporaryDirectory()
        self.target_directory = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        """清理 Runtime 分发测试的隔离目录。"""
        self.target_directory.cleanup()
        self.source_directory.cleanup()

    def test_runtime_mode_preserves_core_and_replaces_reference_body_with_stub(self) -> None:
        """runtime 模式必须逐字保留 Core SKILL，但目标 references 只能是同名 MCP stub。"""
        source = self._source_root()
        target = Path(self.target_directory.name)
        custom = target / ".agents/changes/active/keep.txt"
        custom.parent.mkdir(parents=True)
        custom.write_text("keep\n", encoding="utf-8")

        result = INSTALL.install_skills(source, target, mode="runtime", runtime_command=self._runtime_command(source))

        self.assertEqual(result["mode"], "runtime")
        self.assertEqual(custom.read_text(encoding="utf-8"), "keep\n")
        for skill in ("coding", "review", "docs"):
            source_skill = source / ".agents/skills" / skill
            target_skill = target / ".agents/skills" / skill
            self.assertEqual((target_skill / "SKILL.md").read_bytes(), (source_skill / "SKILL.md").read_bytes())
            stub = (target_skill / "references/01_秘密规则.md").read_text(encoding="utf-8")
            self.assertIn(f"{skill}.reference.01", stub)
            self.assertIn("agent_skills_load_context", stub)
            self.assertNotIn("THIS_CANONICAL_BODY_MUST_NOT_BE_DISTRIBUTED", stub)
        self.assertTrue((target / "AGENTS.md").is_file())

    def test_runtime_digest_mismatch_fails_before_target_mutation(self) -> None:
        """旧 Runtime/source digest 不匹配时必须在创建目标 `.agents` 前失败。"""
        source = self._source_root()
        target = Path(self.target_directory.name)
        sentinel = target / "keep.txt"
        sentinel.write_text("unchanged\n", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "source_digest"):
            INSTALL.install_skills(
                source,
                target,
                mode="runtime",
                runtime_command=self._runtime_command(source, "0" * 64),
            )

        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged\n")
        self.assertFalse((target / ".agents").exists())

    def test_default_full_mode_still_copies_canonical_reference_text(self) -> None:
        """不传 mode 的旧安装入口仍必须保持完整 Markdown 分发语义。"""
        source = self._source_root()
        target = Path(self.target_directory.name)

        result = INSTALL.install_skills(source, target)

        self.assertEqual(result["mode"], "full")
        target_reference = target / ".agents/skills/docs/references/01_秘密规则.md"
        self.assertIn("THIS_CANONICAL_BODY_MUST_NOT_BE_DISTRIBUTED_docs", target_reference.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
