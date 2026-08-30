from __future__ import annotations

import hashlib
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


class ReleaseSingleZipTest(unittest.TestCase):
    """验证正式 Release 最终只发布一个包含三平台文件与说明的 ZIP。"""

    def test_release_surface_is_single_distribution_zip(self) -> None:
        """Draft 与正式 Release 都只能暴露一个版本 ZIP，不再单独上传说明或 binary。"""
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "Build single distribution ZIP",
            'f"agent-skills-v{version}.zip"',
            'expected_package="agent-skills-v${RELEASE_TAG#v}.zip"',
            "release-package/agent-skills-v*.zip",
            "ZIP 成员集合不正确",
        ):
            self.assertIn(marker, workflow)
        self.assertNotIn('gh release upload "${RELEASE_TAG}" release-assets/*', workflow)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "需要 bash 验证 ZIP 组装脚本")
    def test_zip_contains_exact_runtime_files_usage_and_internal_checksums(self) -> None:
        """ZIP 只能含三平台二进制、说明和四项内部 checksum，不能夹带 identity/临时文件。"""
        script = _extract_workflow_run_block("Build single distribution ZIP")
        version = "2.0.0"
        expected_files = (
            f"agent-skills-mcp-v{version}-linux",
            f"agent-skills-mcp-v{version}-windows.exe",
            f"agent-skills-mcp-v{version}-macos",
            "USAGE.md",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets = root / "release-assets"
            assets.mkdir()
            for index, name in enumerate(expected_files):
                (assets / name).write_bytes(f"asset-{index}".encode("utf-8"))
            (assets / f"agent-skills-mcp-v{version}-linux.manifest.json").write_text("{}", encoding="utf-8")
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

            package = root / "release-package" / f"agent-skills-v{version}.zip"
            self.assertTrue(package.is_file())
            with zipfile.ZipFile(package) as archive:
                names = archive.namelist()
                self.assertEqual(names, [*expected_files, "SHA256SUMS"])
                checksum_lines = archive.read("SHA256SUMS").decode("utf-8").splitlines()
                self.assertEqual(len(checksum_lines), 4)
                for name in expected_files:
                    expected_hash = hashlib.sha256((assets / name).read_bytes()).hexdigest()
                    self.assertIn(f"{expected_hash}  {name}", checksum_lines)
                self.assertFalse(any("manifest.json" in name for name in names))
                self.assertNotIn("unexpected.tmp", names)

    def test_usage_tells_user_to_download_and_extract_one_zip(self) -> None:
        """最终用户说明应以单 ZIP 为获取、升级和回退入口。"""
        usage = USAGE.read_text(encoding="utf-8")
        for marker in (
            "agent-skills-v<VERSION>.zip",
            "解压",
            "ZIP 内",
            "SHA256SUMS",
        ):
            self.assertIn(marker, usage)


if __name__ == "__main__":
    unittest.main()
