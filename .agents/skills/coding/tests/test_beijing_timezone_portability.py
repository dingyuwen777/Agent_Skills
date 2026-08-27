from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
CODING_PATH = ROOT / ".agents/skills/coding/scripts/coding.py"


class BeijingTimezonePortabilityTest(unittest.TestCase):
    """验证 Coding CLI 在宿主没有系统 IANA tzdb 和 site-packages 时仍能稳定使用北京时间。"""

    def test_discover_uses_local_shanghai_resource_without_system_tzdb(self) -> None:
        """清空系统 TZPATH 并禁用 site-packages 后，discover 仍应成功并输出明确 `+08:00` 时间。"""
        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment["PYTHONTZPATH"] = ""
            result = subprocess.run(
                [sys.executable, "-S", str(CODING_PATH), "discover", "--root", directory, "--json"],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("+08:00", result.stdout)
        self.assertNotIn("ZoneInfoNotFoundError", result.stderr)


if __name__ == "__main__":
    unittest.main()
