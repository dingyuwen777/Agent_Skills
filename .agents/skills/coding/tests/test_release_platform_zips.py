from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
USAGE = ROOT / "USAGE.md"


def _extract_workflow_run_block(step_name: str) -> str:
    """从 Release Workflow 中提取指定步骤的 Shell 正文用于真实执行验证。"""
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    step_marker = f"      - name: {step_name}\n"
    step_start = workflow.find(step_marker)
    if step_start < 0:
        raise AssertionError(f"Release Workflow 缺少步骤：{step_name}")
    run_marker = "        run: |\n"
    run_start = workflow.find(run_marker, step_start)
    if run_start < 0:
        raise AssertionError(f"Release Workflow 步骤缺少 run block：{step_name}")
    run_start += len(run_marker)
    next_step = workflow.find("\n      - name:", run_start)
    run_end = len(workflow) if next_step < 0 else next_step
    return textwrap.dedent(workflow[run_start:run_end]).strip() + "\n"


class ReleasePlatformZipsTest(unittest.TestCase):
    """验证正式 Release 按 Windows、Linux、macOS 分别发布独立 ZIP。"""

    def test_release_surface_is_three_platform_distribution_zips(self) -> None:
        """Draft 与正式 Release 必须精确暴露三个平台 ZIP。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "Build platform distribution ZIPs",
            'f"agent-skills-v{version}-linux.zip"',
            'f"agent-skills-v{version}-windows.zip"',
            'f"agent-skills-v{version}-macos.zip"',
            'expected_packages=(\n            "agent-skills-v${RELEASE_TAG#v}-linux.zip"',
            'gh release upload "${RELEASE_TAG}" release-package/agent-skills-v*-linux.zip release-package/agent-skills-v*-windows.zip release-package/agent-skills-v*-macos.zip',
            "ZIP 成员集合不正确",
        ):
            self.assertIn(marker, workflow)
        self.assertNotIn('f"agent-skills-v{version}.zip"', workflow)
        self.assertNotIn('expected_package="agent-skills-v${RELEASE_TAG#v}.zip"', workflow)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "需要 bash 验证 ZIP 组装脚本")
    def test_each_zip_contains_only_platform_runtime_and_usage(self) -> None:
        """每个平台 ZIP 只能含当前平台二进制和 USAGE.md，不能夹带其他平台或维护资产。"""
        script = _extract_workflow_run_block("Build platform distribution ZIPs")
        version = "2.0.0"
        binaries = {
            "linux": "agent-skills",
            "windows": "agent-skills.exe",
            "macos": "agent-skills",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets = root / "release-assets"
            assets.mkdir()
            for index, (platform, binary) in enumerate(binaries.items()):
                platform_dir = assets / f"release-runtime-{platform}"
                platform_dir.mkdir()
                (platform_dir / binary).write_bytes(f"asset-{index}".encode("utf-8"))
            (assets / "USAGE.md").write_text("usage", encoding="utf-8")
            (assets / f"agent-skills-v{version}-linux.manifest.json").write_text("{}", encoding="utf-8")
            (assets / "unexpected.tmp").write_text("不要进入 ZIP", encoding="utf-8")

            env = os.environ.copy()
            env["RELEASE_VERSION"] = version
            result = subprocess.run(
                ["bash", "-euo", "pipefail", "-c", script],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            package_dir = root / "release-package"
            for platform, binary in binaries.items():
                package = package_dir / f"agent-skills-v{version}-{platform}.zip"
                self.assertTrue(package.is_file(), f"缺少平台 ZIP：{package.name}")
                with zipfile.ZipFile(package) as archive:
                    names = archive.namelist()
                    self.assertEqual(names, [binary, "USAGE.md"])
                    self.assertFalse(any("manifest.json" in name for name in names))
                    self.assertNotIn("unexpected.tmp", names)
                    for other_binary in binaries.values():
                        if other_binary != binary:
                            self.assertNotIn(other_binary, names)

    def test_usage_tells_user_to_download_current_platform_zip(self) -> None:
        """最终用户说明应以当前平台 ZIP 作为获取、升级和回退入口。"""
        usage = USAGE.read_text(encoding="utf-8")
        for marker in (
            "agent-skills-v<VERSION>-windows.zip",
            "agent-skills-v<VERSION>-linux.zip",
            "agent-skills-v<VERSION>-macos.zip",
            "下载与你操作系统匹配的 ZIP",
        ):
            self.assertIn(marker, usage)
        self.assertNotIn("agent-skills-v<VERSION>.zip", usage)
        self.assertNotIn("SHA256SUMS", usage)


if __name__ == "__main__":
    unittest.main()
