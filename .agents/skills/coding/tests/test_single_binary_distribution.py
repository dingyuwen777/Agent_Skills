from __future__ import annotations

import base64
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.crypto import recover_root_material
from runtime.agent_skills_runtime.encrypted_bundle import EncryptedBundleStore, encrypt_runtime_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime import server


ROOT = Path(__file__).resolve().parents[4]
BUILD_RUNTIME_PATH = ROOT / "scripts/build_runtime.py"


def _load_module(name: str, path: Path):
    """从指定路径加载脚本或构建生成模块。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD_RUNTIME = _load_module("single_binary_builder_under_test", BUILD_RUNTIME_PATH)


class SingleBinaryDistributionTest(unittest.TestCase):
    """验证 Runtime 正式分发已收敛为自包含 binary，而不是外部 Runtime Kit。"""

    def test_embedded_payload_contains_v3_container_and_no_reference_stubs(self) -> None:
        """Project Payload 继续分发 Skill Core；canonical Reference 只进入 v3 加密容器而不落 Stub。"""
        bundle = build_bundle(ROOT)
        project_payload = build_project_payload(ROOT, bundle)
        root_material, container = encrypt_runtime_bundle(bundle)

        with tempfile.TemporaryDirectory() as directory:
            package_root = Path(directory)
            BUILD_RUNTIME._write_embedded_payload(
                package_root,
                root_material,
                container,
                project_payload,
                "1.2.3",
            )
            generated_source = (package_root / "_embedded_payload.py").read_text(encoding="utf-8")
            embedded = _load_module("embedded_payload_fixture", package_root / "_embedded_payload.py")

        self.assertNotIn("RUNTIME_ROOT_B64", generated_source)
        self.assertIn("RUNTIME_ROOT_SHARES_B64", generated_source)
        root_shares = base64.b64decode(embedded.RUNTIME_ROOT_SHARES_B64, validate=True)
        self.assertNotEqual(root_shares, root_material)
        self.assertEqual(recover_root_material(root_shares), root_material)

        restored_payload = json.loads(base64.b64decode(embedded.PROJECT_PAYLOAD_B64).decode("utf-8"))
        restored_store = EncryptedBundleStore.open(
            base64.b64decode(embedded.BUNDLE_CONTAINER_B64, validate=True),
            recover_root_material(root_shares),
        )
        self.assertEqual(restored_payload["skills"], project_payload["skills"])
        self.assertEqual(restored_payload["payload_digest"], project_payload["payload_digest"])
        self.assertEqual(restored_store.skills, project_payload["skills"])
        self.assertEqual(restored_store.source_digest, project_payload["source_digest"])
        self.assertEqual(restored_store.decryption_count, 0)
        self.assertEqual(embedded.RELEASE_VERSION, "1.2.3")
        self.assertIsNone(embedded.SOURCE_COMMIT)
        paths = {str(entry["path"]): entry for entry in restored_payload["files"]}
        for skill in project_payload["skills"]:
            self.assertIn(f"{skill}/SKILL.md", paths)

        self.assertFalse(any("/references/" in path for path in paths))
        payload_text = json.dumps(restored_payload, ensure_ascii=False)
        self.assertNotIn("路由清单", payload_text)
        for reference in bundle["references"]:
            self.assertNotIn(reference["content"], payload_text)
            self.assertNotIn(reference["content"].encode("utf-8"), container)

    def test_runtime_builder_has_no_external_runtime_kit_install_path(self) -> None:
        """正式 Runtime Builder 不得继续生成 Python 安装脚本、外部 Kit 或完整 root 单常量。"""
        source = BUILD_RUNTIME_PATH.read_text(encoding="utf-8")

        self.assertNotIn("build_distribution_kit", source)
        self.assertNotIn("install_runtime.py", source)
        self.assertNotIn("install_runtime_target.py", source)
        self.assertNotIn("runtime-kit", source)
        self.assertIn("BUNDLE_CONTAINER_B64", source)
        self.assertIn("RUNTIME_ROOT_SHARES_B64", source)
        self.assertNotIn("RUNTIME_ROOT_B64", source)
        self.assertIn("PROJECT_PAYLOAD_B64", source)
        self.assertIn("build_project_payload", source)

    def test_embedded_source_commit_preserves_null_and_rejects_invalid_identity(self) -> None:
        """非 Git build 的 null 不能变成字符串，非法 commit 也不能进入公开 Runtime identity。"""
        self.assertIsNone(server._normalise_source_commit(None))
        self.assertEqual(server._normalise_source_commit("a" * 40), "a" * 40)
        with self.assertRaises(ValueError):
            server._normalise_source_commit("None")

    def test_generated_entrypoint_forces_utf8_before_chinese_cli_json(self) -> None:
        """onefile 入口必须在调用 server.main 前固定 UTF-8，避免 Windows 中文 JSON 键损坏。"""
        with tempfile.TemporaryDirectory() as directory:
            entrypoint = Path(directory) / "entrypoint.py"
            BUILD_RUNTIME._write_entrypoint(entrypoint)
            text = entrypoint.read_text(encoding="utf-8")

        self.assertIn('sys.stdout.reconfigure(encoding="utf-8")', text)
        self.assertIn('sys.stderr.reconfigure(encoding="utf-8")', text)
        self.assertLess(text.index("reconfigure"), text.index("main()"))


if __name__ == "__main__":
    unittest.main()
