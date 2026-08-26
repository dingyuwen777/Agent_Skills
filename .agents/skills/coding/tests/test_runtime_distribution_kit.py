from __future__ import annotations

import importlib.util
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path
import zipfile

from runtime.agent_skills_runtime.catalog import build_bundle, public_manifest


ROOT = Path(__file__).resolve().parents[4]
BUILD_RUNTIME_PATH = ROOT / "scripts/build_runtime.py"


def _load_module(name: str, path: Path):
    """从指定路径加载脚本模块，用于验证 Runtime Kit 的独立分发入口。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD_RUNTIME = _load_module("runtime_kit_builder_under_test", BUILD_RUNTIME_PATH)


class RuntimeDistributionKitTest(unittest.TestCase):
    """验证最终 Runtime Kit 不含 canonical Reference 正文且脱离私有源仓库可安装目标项目。"""

    def setUp(self) -> None:
        """为每个 Runtime Kit 测试创建隔离构建、解压和目标目录。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.output = self.root / "dist"
        self.output.mkdir()

    def tearDown(self) -> None:
        """清理 Runtime Kit 测试创建的临时目录。"""
        self.temp_directory.cleanup()

    def _fake_runtime(self, source_digest: str) -> Path:
        """创建只实现 status/self-test 的可执行测试 Runtime，避免单测重新运行 PyInstaller。"""
        artifact = self.output / "agent-skills-mcp"
        artifact.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            f"payload={{'ok': True, 'source_digest': {source_digest!r}, 'bundle_version': {source_digest[:16]!r}, 'reference_count': 1}}\n"
            "print(json.dumps(payload))\n",
            encoding="utf-8",
            newline="\n",
        )
        artifact.chmod(artifact.stat().st_mode | stat.S_IXUSR)
        return artifact

    def _extract_kit(self, kit_zip: Path) -> Path:
        """解压 Distribution Kit 并返回唯一顶层目录。"""
        extract_root = self.root / "extracted"
        extract_root.mkdir()
        with zipfile.ZipFile(kit_zip) as archive:
            archive.extractall(extract_root)
        children = [path for path in extract_root.iterdir() if path.is_dir()]
        self.assertEqual(len(children), 1)
        return children[0]

    def test_distribution_kit_contains_core_stubs_but_no_canonical_reference_body(self) -> None:
        """Kit 必须包含 Core/Stub/安装器，但任何目标 Stub 都不能复制 canonical Reference 原文。"""
        bundle = build_bundle(ROOT)
        artifact = self._fake_runtime(bundle["source_digest"])
        artifact_manifest = public_manifest(bundle)
        artifact_manifest["artifact"] = artifact.name
        artifact_manifest["artifact_sha256"] = BUILD_RUNTIME._sha256_file(artifact)
        manifest_path = self.output / "agent-skills-mcp.manifest.json"
        manifest_path.write_text(json.dumps(artifact_manifest), encoding="utf-8")

        result = BUILD_RUNTIME.build_distribution_kit(
            ROOT,
            self.output,
            artifact,
            manifest_path,
            bundle,
            "agent-skills-mcp",
        )

        kit_zip = Path(result["distribution_kit"])
        self.assertTrue(kit_zip.is_file())
        kit_root = self._extract_kit(kit_zip)
        self.assertTrue((kit_root / "install_runtime.py").is_file())
        self.assertTrue((kit_root / "install_runtime_target.py").is_file())
        self.assertTrue((kit_root / artifact.name).is_file())
        self.assertTrue((kit_root / "payload/.agents/skills/coding/SKILL.md").is_file())

        for entry in bundle["references"]:
            stub = kit_root / "payload/.agents/skills" / entry["skill"] / "references" / entry["filename"]
            stub_text = stub.read_text(encoding="utf-8")
            self.assertIn(entry["id"], stub_text)
            self.assertIn(entry["sha256"], stub_text)
            self.assertIn("agent_skills_load_context", stub_text)
            self.assertNotEqual(stub_text, entry["content"])
            self.assertNotIn(entry["content"], stub_text)

        kit_metadata = json.loads((kit_root / "agent-skills-runtime-kit.json").read_text(encoding="utf-8"))
        self.assertEqual(kit_metadata["source_digest"], bundle["source_digest"])
        self.assertGreater(len(kit_metadata["payload_files"]), len(bundle["references"]))

    def test_extracted_kit_installs_target_without_private_source_repository(self) -> None:
        """成员只拿解压后的 Kit 也必须能完成目标项目 Core+Stub+AGENTS Bootstrap。"""
        bundle = build_bundle(ROOT)
        artifact = self._fake_runtime(bundle["source_digest"])
        artifact_manifest = public_manifest(bundle)
        artifact_manifest["artifact"] = artifact.name
        artifact_manifest["artifact_sha256"] = BUILD_RUNTIME._sha256_file(artifact)
        manifest_path = self.output / "agent-skills-mcp.manifest.json"
        manifest_path.write_text(json.dumps(artifact_manifest), encoding="utf-8")
        result = BUILD_RUNTIME.build_distribution_kit(
            ROOT,
            self.output,
            artifact,
            manifest_path,
            bundle,
            "agent-skills-mcp",
        )
        kit_root = self._extract_kit(Path(result["distribution_kit"]))
        target_installer = _load_module("extracted_runtime_target_installer", kit_root / "install_runtime_target.py")
        target = self.root / "target-project"
        target.mkdir()

        install_result = target_installer.install_target(
            kit_root,
            target,
            runtime_command=[sys.executable, str(kit_root / artifact.name)],
        )

        self.assertEqual(install_result["source_digest"], bundle["source_digest"])
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertTrue((target / ".agents/skills/coding/SKILL.md").is_file())
        target_stub = target / ".agents/skills/docs/references/01_事实源与同步判断.md"
        self.assertIn("agent_skills_load_context", target_stub.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
