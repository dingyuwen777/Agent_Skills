from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTALL_RUNTIME_PATH = ROOT / "scripts/install_runtime.py"


def _load_module(name: str, path: Path):
    """从指定路径加载 Runtime 安装脚本模块，便于隔离验证文件系统回滚。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALL_RUNTIME = _load_module("runtime_installer_under_test", INSTALL_RUNTIME_PATH)


class RuntimeInstallerRollbackTest(unittest.TestCase):
    """验证用户级 Runtime 安装的执行位修复与替换回滚。"""

    def setUp(self) -> None:
        """为每个 Runtime 安装回滚测试建立隔离 artifact 与目标目录。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.artifact = self.root / "new-runtime"
        self.artifact.write_bytes(b"new-runtime")
        if os.name != "nt":
            self.artifact.chmod(self.artifact.stat().st_mode | 0o111)
        self.install_dir = self.root / "installed"
        self.install_dir.mkdir()
        self.destination = self.install_dir / INSTALL_RUNTIME._target_filename(self.artifact)
        self.destination.write_bytes(b"old-runtime")

    def tearDown(self) -> None:
        """清理 Runtime 安装回滚测试的隔离目录。"""
        self.temp_directory.cleanup()

    def test_failed_post_switch_verification_restores_previous_runtime(self) -> None:
        """新 Runtime 已切换但最终自检失败时，安装器必须恢复原有可执行文件字节。"""
        original_verify = INSTALL_RUNTIME.verify_runtime
        calls: list[tuple[str, ...]] = []

        def fake_verify(command):
            """模拟源和暂存校验成功、最终目标校验失败的诊断边界。"""
            calls.append(tuple(str(item) for item in command))
            if len(calls) == 3:
                raise RuntimeError("模拟最终 Runtime 自检失败")
            return {
                "source_digest": "digest-new",
                "bundle_version": "fixture",
                "reference_count": 1,
            }

        INSTALL_RUNTIME.verify_runtime = fake_verify
        try:
            with self.assertRaisesRegex(RuntimeError, "模拟最终 Runtime 自检失败"):
                INSTALL_RUNTIME.install_runtime(self.artifact, self.install_dir)
        finally:
            INSTALL_RUNTIME.verify_runtime = original_verify

        self.assertEqual(self.destination.read_bytes(), b"old-runtime")
        self.assertEqual(len(calls), 3)

    @unittest.skipIf(os.name == "nt", "Windows 不使用 POSIX executable bit")
    def test_non_executable_source_is_staged_with_execute_permission_before_verification(self) -> None:
        """ZIP 解压后无执行位的 POSIX Runtime 应先在暂存副本恢复权限，再执行自检。"""
        artifact = self.root / "non-executable-runtime"
        artifact.write_bytes(b"runtime-from-zip")
        artifact.chmod(0o600)
        install_dir = self.root / "non-executable-installed"
        original_verify = INSTALL_RUNTIME.verify_runtime
        calls: list[Path] = []

        def fake_verify(command):
            """只有待验证文件已具备 executable bit 时才返回成功。"""
            path = Path(str(command[0]))
            calls.append(path)
            if not os.access(path, os.X_OK):
                raise RuntimeError("Runtime 在验证前没有 executable bit")
            return {
                "source_digest": "digest-zip",
                "bundle_version": "fixture",
                "reference_count": 1,
            }

        INSTALL_RUNTIME.verify_runtime = fake_verify
        try:
            result = INSTALL_RUNTIME.install_runtime(artifact, install_dir)
        finally:
            INSTALL_RUNTIME.verify_runtime = original_verify

        installed = Path(result["installed"])
        self.assertTrue(installed.is_file())
        self.assertTrue(os.access(installed, os.X_OK))
        self.assertEqual(installed.read_bytes(), b"runtime-from-zip")
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0], artifact)


if __name__ == "__main__":
    unittest.main()
