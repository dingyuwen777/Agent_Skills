from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class RuntimeStdioLifecycleTest(unittest.TestCase):
    """验证 Runtime stdio 生命周期，只在具备 Runtime 依赖的测试范围执行。"""

    def test_stdio_server_exits_after_host_closes_stdin(self) -> None:
        """宿主关闭 stdio 输入后，serve 进程必须结束而不是脱离宿主继续常驻。"""
        process = subprocess.Popen(
            [sys.executable, "-m", "runtime.agent_skills_runtime.server", "serve"],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIsNotNone(process.stdin)
        process.stdin.close()
        try:
            return_code = process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
            self.fail("stdio 已关闭但 Runtime serve 进程仍未退出")
        stdout = process.stdout.read() if process.stdout else b""
        stderr = process.stderr.read() if process.stderr else b""
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        self.assertEqual(stdout, b"", stdout.decode("utf-8", errors="replace"))
        self.assertEqual(return_code, 0, stderr.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
