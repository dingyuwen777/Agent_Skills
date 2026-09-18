"""验证 Windows 双击无参数安装失败时错误窗口可读，同时保持自动化非阻塞。"""

from __future__ import annotations

import io
import unittest
from unittest.mock import patch

from runtime.agent_skills_runtime import server


class _InteractiveInput(io.StringIO):
    """模拟 Windows 控制台交互输入，并记录是否真的等待过用户。"""

    def __init__(self, value: str = "\n", *, read_error: OSError | None = None) -> None:
        """保存输入内容与可选读取异常。"""
        super().__init__(value)
        self.readline_calls = 0
        self._read_error = read_error

    def isatty(self) -> bool:
        """声明该输入来自交互式终端。"""
        return True

    def readline(self, *args, **kwargs) -> str:  # type: ignore[no-untyped-def]
        """记录等待次数，并按 fixture 返回输入或制造读取失败。"""
        self.readline_calls += 1
        if self._read_error is not None:
            raise self._read_error
        return super().readline(*args, **kwargs)


class _NonInteractiveInput(io.StringIO):
    """模拟 CI/重定向 stdin，禁止被安装失败路径阻塞。"""

    def __init__(self) -> None:
        """初始化空输入并记录读取次数。"""
        super().__init__("")
        self.readline_calls = 0

    def isatty(self) -> bool:
        """声明当前不是交互式终端。"""
        return False

    def readline(self, *args, **kwargs) -> str:  # type: ignore[no-untyped-def]
        """若错误路径错误地等待 stdin，则记录该行为。"""
        self.readline_calls += 1
        return super().readline(*args, **kwargs)


class RuntimeWindowsInstallErrorPauseTest(unittest.TestCase):
    """覆盖 Windows onefile 无参数安装失败的错误可见性 Contract。"""

    def _run_install_failure(
        self,
        argv: list[str],
        *,
        platform: str,
        frozen: bool,
        stdin: io.StringIO,
    ) -> tuple[int, str]:
        """在不进入真实安装器的情况下触发 CLI 安装失败并捕获 stderr。"""
        stderr = io.StringIO()
        with patch.object(server.sys, "platform", platform):
            with patch.object(server.sys, "frozen", frozen, create=True):
                with patch.object(server.sys, "stdin", stdin):
                    with patch.object(server.sys, "stderr", stderr):
                        with patch.object(
                            server,
                            "_load_embedded_material",
                            side_effect=ValueError("fixture install failure"),
                        ):
                            code = server.main(argv)
        return code, stderr.getvalue()

    def test_windows_frozen_no_args_interactive_failure_waits_after_error(self) -> None:
        """双击等价入口失败时必须先显示原错误，再等待一次 Enter。"""
        stdin = _InteractiveInput()

        code, stderr = self._run_install_failure(
            [],
            platform="win32",
            frozen=True,
            stdin=stdin,
        )

        self.assertEqual(code, 1)
        self.assertEqual(stdin.readline_calls, 1)
        self.assertIn("error: fixture install failure", stderr)
        self.assertIn("按 Enter", stderr)
        self.assertLess(stderr.index("error: fixture install failure"), stderr.index("按 Enter"))

    def test_windows_frozen_no_args_pause_read_failure_keeps_original_exit(self) -> None:
        """等待输入本身失败时仍返回原安装失败，不抛出第二异常。"""
        stdin = _InteractiveInput(read_error=OSError("fixture stdin failure"))

        code, stderr = self._run_install_failure(
            [],
            platform="win32",
            frozen=True,
            stdin=stdin,
        )

        self.assertEqual(code, 1)
        self.assertEqual(stdin.readline_calls, 1)
        self.assertIn("error: fixture install failure", stderr)

    def test_noninteractive_or_nonimplicit_invocations_never_wait(self) -> None:
        """CI、显式 install、POSIX 与源码模式都保持 fail-fast。"""
        cases = [
            ([], "win32", True, _NonInteractiveInput()),
            (["install"], "win32", True, _InteractiveInput()),
            ([], "linux", True, _InteractiveInput()),
            ([], "darwin", True, _InteractiveInput()),
            ([], "win32", False, _InteractiveInput()),
        ]
        for argv, platform, frozen, stdin in cases:
            with self.subTest(argv=argv, platform=platform, frozen=frozen, interactive=stdin.isatty()):
                code, stderr = self._run_install_failure(
                    argv,
                    platform=platform,
                    frozen=frozen,
                    stdin=stdin,
                )
                self.assertEqual(code, 1)
                self.assertEqual(stdin.readline_calls, 0)
                self.assertIn("error: fixture install failure", stderr)


if __name__ == "__main__":
    unittest.main()
