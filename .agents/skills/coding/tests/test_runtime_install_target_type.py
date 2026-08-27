from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTALL_RUNTIME_PATH = ROOT / "scripts/install_runtime.py"


def _load_module(name: str, path: Path):
    """从指定路径加载 Runtime 安装器，便于隔离验证目标类型保护。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALL_RUNTIME = _load_module("runtime_installer_target_type", INSTALL_RUNTIME_PATH)


class RuntimeInstallerTargetTypeTest(unittest.TestCase):
    """验证用户级 Runtime 安装器不会把意外目录或特殊目标当成可替换文件。"""

    def test_existing_destination_directory_is_rejected_without_data_loss(self) -> None:
        """稳定目标名被目录占用时必须在切换前失败，并完整保留目录中的用户文件。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "runtime-source"
            artifact.write_bytes(b"fixture")
            install_dir = root / "bin"
            destination = install_dir / INSTALL_RUNTIME._target_filename(artifact)
            destination.mkdir(parents=True)
            sentinel = destination / "keep.txt"
            sentinel.write_text("keep-user-data\n", encoding="utf-8")
            original_verify = INSTALL_RUNTIME.verify_runtime

            def fake_verify(command):
                """隔离文件类型测试，不让伪 artifact 的可执行性干扰目标边界验证。"""
                return {
                    "source_digest": "a" * 64,
                    "bundle_version": "fixture",
                    "reference_count": 1,
                }

            INSTALL_RUNTIME.verify_runtime = fake_verify
            try:
                with self.assertRaisesRegex(ValueError, "不是普通文件"):
                    INSTALL_RUNTIME.install_runtime(artifact, install_dir)
            finally:
                INSTALL_RUNTIME.verify_runtime = original_verify

            self.assertTrue(destination.is_dir())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep-user-data\n")


if __name__ == "__main__":
    unittest.main()
