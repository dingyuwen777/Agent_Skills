from __future__ import annotations

import base64
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.crypto import encrypt_bundle, generate_bundle_key
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


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

    def test_embedded_payload_contains_all_skills_and_only_reference_stubs(self) -> None:
        """构建时必须把全部动态 Skill payload 与加密 Reference 一起嵌入 binary material。"""
        bundle = build_bundle(ROOT)
        project_payload = build_project_payload(ROOT, bundle)
        serialized_bundle = json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        key = generate_bundle_key()
        envelope = encrypt_bundle(serialized_bundle, key)

        with tempfile.TemporaryDirectory() as directory:
            package_root = Path(directory)
            BUILD_RUNTIME._write_embedded_payload(package_root, key, envelope, project_payload, "1.2.3")
            embedded = _load_module("embedded_payload_fixture", package_root / "_embedded_payload.py")

        restored_payload = json.loads(base64.b64decode(embedded.PROJECT_PAYLOAD_B64).decode("utf-8"))
        self.assertEqual(restored_payload["skills"], project_payload["skills"])
        self.assertEqual(restored_payload["payload_digest"], project_payload["payload_digest"])
        self.assertEqual(embedded.RELEASE_VERSION, "1.2.3")
        paths = {str(entry["path"]): entry for entry in restored_payload["files"]}
        for skill in project_payload["skills"]:
            self.assertIn(f"{skill}/SKILL.md", paths)

        canonical_by_path = {
            f"{entry['skill']}/references/{entry['filename']}": entry for entry in bundle["references"]
        }
        for path, reference in canonical_by_path.items():
            self.assertIn(path, paths)
            stub_text = decode_payload_file(paths[path]).decode("utf-8")
            self.assertIn(reference["id"], stub_text)
            self.assertIn(reference["sha256"], stub_text)
            self.assertIn("agent_skills_load_context", stub_text)
            self.assertNotIn(reference["content"], stub_text)

    def test_runtime_builder_has_no_external_runtime_kit_install_path(self) -> None:
        """正式 Runtime Builder 不得继续生成 Python 安装脚本或外部 payload Kit。"""
        source = BUILD_RUNTIME_PATH.read_text(encoding="utf-8")

        self.assertNotIn("build_distribution_kit", source)
        self.assertNotIn("install_runtime.py", source)
        self.assertNotIn("install_runtime_target.py", source)
        self.assertNotIn("runtime-kit", source)
        self.assertIn("PROJECT_PAYLOAD_B64", source)
        self.assertIn("build_project_payload", source)


if __name__ == "__main__":
    unittest.main()
