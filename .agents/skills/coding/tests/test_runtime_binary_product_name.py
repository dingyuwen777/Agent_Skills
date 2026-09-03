from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[4]
LEGACY_BINARY_NAME = "agent-skills-" + "mcp"
CURRENT_BINARY_NAME = "agent-skills"


class RuntimeBinaryProductNameTest(unittest.TestCase):
    """锁定 Runtime 当前产品名、安装路径、Release 包装和维护兼容策略。"""

    def test_live_runtime_surfaces_use_agent_skills_and_drop_legacy_binary_name(self) -> None:
        """当前 live 源码/规则/CI/用户文档不得继续把旧名当正式 Runtime 名称。"""
        roots = [
            ROOT / "scripts",
            ROOT / "runtime",
            ROOT / ".github",
            ROOT / ".agents" / "skills",
        ]
        files = [ROOT / "USAGE.md", ROOT / ".agents" / "MAINTENANCE.md"]
        suffixes = {".py", ".md", ".yml", ".yaml", ".json", ".toml"}
        for root in roots:
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in suffixes:
                    files.append(path)
        offenders: list[str] = []
        for path in sorted(set(files)):
            text = path.read_text(encoding="utf-8")
            if LEGACY_BINARY_NAME in text:
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual([], offenders, f"live 表面仍存在旧 Runtime 名：{offenders}")

    def test_builder_and_installer_use_exact_current_binary_basename(self) -> None:
        """Builder 默认名与项目安装名必须统一为 agent-skills。"""
        builder = (ROOT / "scripts" / "build_runtime.py").read_text(encoding="utf-8")
        installer = (ROOT / "runtime" / "agent_skills_runtime" / "project_installer.py").read_text(encoding="utf-8")
        self.assertIn('name: str = "agent-skills"', builder)
        self.assertIn('default="agent-skills"', builder)
        self.assertIn('"agent-skills.exe" if artifact.suffix.lower() == ".exe" else "agent-skills"', installer)
        self.assertNotIn(LEGACY_BINARY_NAME, builder)
        self.assertNotIn(LEGACY_BINARY_NAME, installer)

    def test_release_keeps_three_platform_zip_names_and_uses_unversioned_binary_member(self) -> None:
        """Release 仍是三平台 ZIP，但 ZIP 内 Runtime basename 固定为 agent-skills。"""
        release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        for platform in ("windows", "linux", "macos"):
            self.assertIn(f"agent-skills-v${{VERSION}}-{platform}.zip", release)
        self.assertIn('name="agent-skills"', release)
        self.assertIn('$name = "agent-skills"', release)
        self.assertNotIn(LEGACY_BINARY_NAME, release)
        self.assertNotRegex(release, r"agent-skills-v\$\{?RELEASE_VERSION\}?-(?:linux|macos)")
        self.assertNotRegex(release, r"agent-skills-v\$env:RELEASE_VERSION-windows")

    def test_maintenance_declares_no_default_cross_version_upgrade_compatibility(self) -> None:
        """Agent_Skills 自维护默认以当前版本为准，兼容层只能由显式 Requirement 触发。"""
        maintenance = (ROOT / ".agents" / "MAINTENANCE.md").read_text(encoding="utf-8")
        required = (
            "默认不承担跨版本升级兼容",
            "干净安装",
            "Requirement Source 明确要求",
            "alias",
            "fallback",
            "不能绕过当前任务明确要求保持的产品契约",
        )
        for marker in required:
            self.assertIn(marker, maintenance)


if __name__ == "__main__":
    unittest.main()
