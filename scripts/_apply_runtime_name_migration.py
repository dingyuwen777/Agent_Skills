#!/usr/bin/env python3
"""一次性把当前 live Runtime 产品名统一为 agent-skills，并修正 Release 同名平台资产布局。"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LEGACY_NAME = "agent-skills-" + "mcp"
CURRENT_NAME = "agent-skills"
SELF = Path(__file__).resolve()
WORKFLOW = ROOT / ".github" / "workflows" / "runtime-name-migration.yml"


def _replace(path: Path, old: str, new: str, *, count: int | None = None) -> None:
    """执行受控文本替换；关键结构缺失时直接失败，避免静默生成半迁移状态。"""
    text = path.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual == 0:
        raise RuntimeError(f"预期替换片段不存在：{path.relative_to(ROOT)}: {old[:80]!r}")
    if count is not None and actual != count:
        raise RuntimeError(
            f"替换次数不符合预期：{path.relative_to(ROOT)} expected={count} actual={actual}: {old[:80]!r}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def _replace_regex(path: Path, pattern: str, replacement: str, *, count: int = 1) -> None:
    """执行带精确次数约束的正则替换。"""
    text = path.read_text(encoding="utf-8")
    updated, actual = re.subn(pattern, replacement, text, count=count, flags=re.MULTILINE | re.DOTALL)
    if actual != count:
        raise RuntimeError(
            f"正则替换次数不符合预期：{path.relative_to(ROOT)} expected={count} actual={actual}: {pattern[:100]!r}"
        )
    path.write_text(updated, encoding="utf-8", newline="\n")


def _live_text_files() -> list[Path]:
    """列出当前正式产品/规则/测试表面，明确排除历史 Change。"""
    roots = [
        ROOT / "scripts",
        ROOT / "runtime",
        ROOT / ".github" / "workflows",
        ROOT / ".agents" / "skills",
    ]
    suffixes = {".py", ".md", ".yml", ".yaml", ".json", ".toml"}
    files = [ROOT / "USAGE.md", ROOT / ".agents" / "MAINTENANCE.md"]
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes and path.resolve() != SELF:
                files.append(path)
    return sorted(set(files))


def _replace_legacy_name() -> None:
    """先完成 live 表面的机械产品名替换。"""
    for path in _live_text_files():
        text = path.read_text(encoding="utf-8")
        if LEGACY_NAME in text:
            path.write_text(text.replace(LEGACY_NAME, CURRENT_NAME), encoding="utf-8", newline="\n")


def _rewrite_release_workflow() -> None:
    """保持三个 ZIP 的外层合同不变，并用平台子目录承载同名 agent-skills binary。"""
    path = ROOT / ".github" / "workflows" / "release.yml"

    for old, new in (
        ('name="agent-skills-v${RELEASE_VERSION}-linux"', 'name="agent-skills"'),
        ('$name = "agent-skills-v$env:RELEASE_VERSION-windows"', '$name = "agent-skills"'),
        ('name="agent-skills-v${RELEASE_VERSION}-macos"', 'name="agent-skills"'),
        ('path: release-assets/agent-skills-v*-linux', 'path: release-assets/agent-skills'),
        ('path: release-assets/agent-skills-v*-windows.exe', 'path: release-assets/agent-skills.exe'),
        ('path: release-assets/agent-skills-v*-macos', 'path: release-assets/agent-skills'),
    ):
        _replace(path, old, new, count=1)

    _replace(path, "          merge-multiple: true\n", "", count=1)

    old_expected = '''          expected=(
            "agent-skills-v${RELEASE_VERSION}-linux"
            "agent-skills-v${RELEASE_VERSION}-windows.exe"
            "agent-skills-v${RELEASE_VERSION}-macos"
            "USAGE.md"
          )'''
    new_expected = '''          expected=(
            "release-runtime-linux/agent-skills"
            "release-runtime-windows/agent-skills.exe"
            "release-runtime-macos/agent-skills"
            "USAGE.md"
          )'''
    _replace(path, old_expected, new_expected, count=1)

    old_sha = '''          check_sha() {
            local binary="$1"
            local expected_sha="$2"
            local actual_sha
            actual_sha="$(sha256sum "release-assets/${binary}" | awk '{print $1}')"
            test "${actual_sha}" = "${expected_sha}" || {
              echo "Release artifact SHA256 不一致：${binary}" >&2
              exit 1
            }
          }
          check_sha "agent-skills-v${RELEASE_VERSION}-linux" "${LINUX_ARTIFACT_SHA256}"
          check_sha "agent-skills-v${RELEASE_VERSION}-windows.exe" "${WINDOWS_ARTIFACT_SHA256}"
          check_sha "agent-skills-v${RELEASE_VERSION}-macos" "${MACOS_ARTIFACT_SHA256}"
          test -z "$(find release-assets -maxdepth 1 -name '*.manifest.json' -print -quit)"'''
    new_sha = '''          check_sha() {
            local binary_path="$1"
            local expected_sha="$2"
            local actual_sha
            actual_sha="$(sha256sum "${binary_path}" | awk '{print $1}')"
            test "${actual_sha}" = "${expected_sha}" || {
              echo "Release artifact SHA256 不一致：${binary_path}" >&2
              exit 1
            }
          }
          check_sha "release-assets/release-runtime-linux/agent-skills" "${LINUX_ARTIFACT_SHA256}"
          check_sha "release-assets/release-runtime-windows/agent-skills.exe" "${WINDOWS_ARTIFACT_SHA256}"
          check_sha "release-assets/release-runtime-macos/agent-skills" "${MACOS_ARTIFACT_SHA256}"
          test -z "$(find release-assets -name '*.manifest.json' -print -quit)"'''
    _replace(path, old_sha, new_sha, count=1)

    old_assets = '''          assets=(
            "agent-skills-v${RELEASE_VERSION}-linux"
            "agent-skills-v${RELEASE_VERSION}-windows.exe"
            "agent-skills-v${RELEASE_VERSION}-macos"
            "USAGE.md"
          )'''
    new_assets = '''          assets=(
            "release-runtime-linux/agent-skills"
            "release-runtime-windows/agent-skills.exe"
            "release-runtime-macos/agent-skills"
            "USAGE.md"
          )'''
    _replace(path, old_assets, new_assets, count=1)

    old_python = '''          packages = [
              ("linux", f"agent-skills-v{version}-linux.zip", f"agent-skills-v{version}-linux"),
              ("windows", f"agent-skills-v{version}-windows.zip", f"agent-skills-v{version}-windows.exe"),
              ("macos", f"agent-skills-v{version}-macos.zip", f"agent-skills-v{version}-macos"),
          ]
          source = Path("release-assets")
          package_dir = Path("release-package")
          for platform, package_name, binary in packages:
              expected = [binary, "USAGE.md"]
              package = package_dir / package_name
              with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                  for name in expected:
                      archive.write(source / name, arcname=name)
              with zipfile.ZipFile(package) as archive:
                  actual = archive.namelist()
              if actual != expected:
                  raise SystemExit(f"ZIP 成员集合不正确：{platform}: {actual}")'''
    new_python = '''          packages = [
              ("linux", f"agent-skills-v{version}-linux.zip", Path("release-assets/release-runtime-linux/agent-skills"), "agent-skills"),
              ("windows", f"agent-skills-v{version}-windows.zip", Path("release-assets/release-runtime-windows/agent-skills.exe"), "agent-skills.exe"),
              ("macos", f"agent-skills-v{version}-macos.zip", Path("release-assets/release-runtime-macos/agent-skills"), "agent-skills"),
          ]
          usage = Path("release-assets/USAGE.md")
          package_dir = Path("release-package")
          for platform, package_name, binary_path, binary in packages:
              expected = [binary, "USAGE.md"]
              package = package_dir / package_name
              with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                  archive.write(binary_path, arcname=binary)
                  archive.write(usage, arcname="USAGE.md")
              with zipfile.ZipFile(package) as archive:
                  actual = archive.namelist()
              if actual != expected:
                  raise SystemExit(f"ZIP 成员集合不正确：{platform}: {actual}")'''
    _replace(path, old_python, new_python, count=1)


def _rewrite_release_zip_test() -> None:
    """让 ZIP 真实执行测试模拟下载后的平台子目录和同名 binary。"""
    path = ROOT / ".agents" / "skills" / "coding" / "tests" / "test_release_platform_zips.py"
    old_binaries = '''        binaries = {
            "linux": f"agent-skills-v{version}-linux",
            "windows": f"agent-skills-v{version}-windows.exe",
            "macos": f"agent-skills-v{version}-macos",
        }'''
    new_binaries = '''        binaries = {
            "linux": "agent-skills",
            "windows": "agent-skills.exe",
            "macos": "agent-skills",
        }'''
    _replace(path, old_binaries, new_binaries, count=1)

    old_create = '''            for index, binary in enumerate(binaries.values()):
                (assets / binary).write_bytes(f"asset-{index}".encode("utf-8"))'''
    new_create = '''            for index, (platform, binary) in enumerate(binaries.items()):
                platform_dir = assets / f"release-runtime-{platform}"
                platform_dir.mkdir()
                (platform_dir / binary).write_bytes(f"asset-{index}".encode("utf-8"))'''
    _replace(path, old_create, new_create, count=1)


def _rewrite_release_surface_test() -> None:
    """把 Release 表面回归从版本化 raw binary 改为同名平台 binary + 不变 ZIP。"""
    path = ROOT / ".agents" / "skills" / "coding" / "tests" / "test_release_only_repository_surface.py"
    old = '''        for binary in (
            "agent-skills-v${RELEASE_VERSION}-linux",
            '"agent-skills-v$env:RELEASE_VERSION-windows"',
            "agent-skills-v${RELEASE_VERSION}-macos",
        ):
            self.assertIn(binary, workflow)'''
    new = '''        for binary in (
            'name="agent-skills"',
            '$name = "agent-skills"',
            "release-assets/release-runtime-linux/agent-skills",
            "release-assets/release-runtime-windows/agent-skills.exe",
            "release-assets/release-runtime-macos/agent-skills",
        ):
            self.assertIn(binary, workflow)
        for versioned_raw_binary in (
            "agent-skills-v${RELEASE_VERSION}-linux",
            '"agent-skills-v$env:RELEASE_VERSION-windows"',
            "agent-skills-v${RELEASE_VERSION}-macos",
        ):
            self.assertNotIn(versioned_raw_binary, workflow)'''
    _replace(path, old, new, count=1)


def _rewrite_product_name_test() -> None:
    """让新永久回归直接锁定平台子目录、同名 binary 和不变 ZIP 名。"""
    path = ROOT / ".agents" / "skills" / "coding" / "tests" / "test_runtime_binary_product_name.py"
    pattern = r'''    def test_release_keeps_three_platform_zip_names_and_uses_unversioned_binary_member\(self\) -> None:\n        """Release 仍是三平台 ZIP，但 ZIP 内 Runtime basename 固定为 agent-skills。"""\n.*?\n    def test_maintenance_declares_no_default_cross_version_upgrade_compatibility'''
    replacement = '''    def test_release_keeps_three_platform_zip_names_and_uses_unversioned_binary_member(self) -> None:
        """Release 仍是三平台 ZIP，但 ZIP 内 Runtime basename 固定为 agent-skills。"""
        release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        for marker in (
            'f"agent-skills-v{version}-linux.zip"',
            'f"agent-skills-v{version}-windows.zip"',
            'f"agent-skills-v{version}-macos.zip"',
            'Path("release-assets/release-runtime-linux/agent-skills")',
            'Path("release-assets/release-runtime-windows/agent-skills.exe")',
            'Path("release-assets/release-runtime-macos/agent-skills")',
            'expected = [binary, "USAGE.md"]',
        ):
            self.assertIn(marker, release)
        self.assertIn('name="agent-skills"', release)
        self.assertIn('$name = "agent-skills"', release)
        self.assertNotIn("merge-multiple: true", release)
        self.assertNotIn(LEGACY_BINARY_NAME, release)
        self.assertNotIn("agent-skills-v${RELEASE_VERSION}-linux", release)
        self.assertNotIn("agent-skills-v${RELEASE_VERSION}-macos", release)
        self.assertNotIn('agent-skills-v$env:RELEASE_VERSION-windows', release)

    def test_maintenance_declares_no_default_cross_version_upgrade_compatibility'''
    _replace_regex(path, pattern, replacement, count=1)


def _rewrite_usage() -> None:
    """最终用户说明保留三个平台 ZIP，但解压后的 binary 统一为 agent-skills。"""
    path = ROOT / "USAGE.md"
    for old, new in (
        ("agent-skills-v<VERSION>-windows.exe", "agent-skills.exe"),
        ("agent-skills-v<VERSION>-linux", "agent-skills"),
        ("agent-skills-v<VERSION>-macos", "agent-skills"),
    ):
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")

    pattern = r'''## 6\. 升级\n\n.*?\n## 7\. 回退'''
    replacement = '''## 6. 升级

Agent_Skills **默认不承诺不同版本之间的原地升级兼容**。切换到新版本时，以该版本的当前说明和干净安装行为为准；如果某个版本明确提供迁移路径，再按该版本说明执行。不要因为旧项目里存在历史 Runtime、旧配置或旧状态文件，就假定新版本会自动识别、迁移或删除它们。

切换到新版本：

1. 先备份项目规则、未提交工作和其他需要保留的本地状态；
2. 下载新版本中与你操作系统匹配的 `agent-skills-v<VERSION>-<platform>.zip`；
3. 解压 ZIP，在可恢复的项目副本或按该版本要求清理后的项目边界中运行 `agent-skills[.exe]`；
4. 运行 `status --json` 和 `self-test --json`；
5. 重新打开项目或新建一次 Agent 会话。

其中 `<platform>` 分别为 `windows`、`linux` 或 `macos`。如果新版本报告当前项目状态不受支持，停止并按该版本说明处理，不要强制覆盖或让新版本猜测旧安装 ownership。

## 7. 回退'''
    _replace_regex(path, pattern, replacement, count=1)


def _rewrite_maintenance() -> None:
    """固化 Agent_Skills 自维护默认不承担跨版本兼容义务。"""
    path = ROOT / ".agents" / "MAINTENANCE.md"
    marker = "## 3. 通用核心与项目 Overlay"
    text = path.read_text(encoding="utf-8")
    if "默认不承担跨版本升级兼容" in text:
        raise RuntimeError("Maintenance 已存在跨版本兼容策略，拒绝重复插入")
    section = '''### Agent_Skills 跨版本兼容策略

Agent_Skills 自身维护**默认不承担跨版本升级兼容**或向后兼容义务。除非当前 Requirement Source 明确要求，否则每次修改以当前目标分支 / 目标版本的**干净安装**和当前版本内行为为验收基线，不因为历史版本曾经存在某个 Runtime、二进制名、配置、sidecar、协议或目录，就自动增加兼容代码。

具体约束：

- 不为未明确要求的旧版本自动增加 `alias`、`fallback`、双文件、双读写、旧路径探测、旧协议 reader 或迁移分支；
- 已存在的兼容实现只是当前代码事实，不自动形成后续维护承诺；如果新的 Requirement 不要求保留，可以按当前目标版本的真实设计删除或改写；
- 如果 Requirement Source 明确要求兼容某个历史版本，必须把兼容范围、迁移/失败边界、回滚和对应验证写入当前 Change，不能使用“兼容所有旧版本”这类无边界承诺；
- 本策略**不能绕过当前任务明确要求保持的产品契约**、数据安全、回滚、Release 打包方式、公开协议或其他不变项。当前任务要求保持的行为必须继续由直接 Evidence 证明。

'''
    if marker not in text:
        raise RuntimeError("Maintenance 缺少预期第 3 节 marker")
    text = text.replace(marker, section + marker, 1)
    text = text.replace("│   ├── Linux Runtime binary", "│   ├── agent-skills")
    text = text.replace("│   ├── Windows Runtime binary", "│   ├── agent-skills.exe")
    text = text.replace("│   ├── macOS Runtime binary", "│   ├── agent-skills")
    path.write_text(text, encoding="utf-8", newline="\n")


def _rewrite_runtime_reference() -> None:
    """同步 canonical Runtime 规则中的不变 Release ZIP 与当前兼容策略。"""
    path = ROOT / ".agents" / "skills" / "coding" / "references" / "13_本地MCP_Runtime分发与原文上下文加载.md"
    text = path.read_text(encoding="utf-8")
    for old, new in (
        ("├── agent-skills-v<SemVer>-linux", "├── agent-skills"),
        ("├── agent-skills-v<SemVer>-windows.exe", "├── agent-skills.exe"),
        ("├── agent-skills-v<SemVer>-macos", "├── agent-skills"),
    ):
        if old not in text:
            raise RuntimeError(f"Runtime Reference 缺少 Release binary marker：{old}")
        text = text.replace(old, new, 1)
    heading = "## 18. 当前版本安装与未来不兼容迁移\n\n"
    policy = (
        "Agent_Skills 源仓库维护默认不承担跨版本升级兼容；除非 Requirement Source 明确要求，"
        "当前版本以干净安装和当前版本内行为为验收基线，不为历史 binary/config/schema 自动保留 alias、fallback 或双 reader。"
        "已有 legacy/previous ownership 路径只是当前实现事实，不构成下一次变更必须继续兼容的承诺。\n\n"
    )
    if heading not in text:
        raise RuntimeError("Runtime Reference 缺少第 18 节")
    text = text.replace(heading, heading + policy, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def _rewrite_runtime_readme() -> None:
    """明确源码维护说明中的当前 binary 输出和非默认兼容边界。"""
    path = ROOT / "runtime" / "README.md"
    text = path.read_text(encoding="utf-8")
    marker = "## 3. 项目安装边界\n\n"
    note = (
        "当前 Runtime 产品 basename 统一为 `agent-skills`：Windows 项目安装为 `.agents/runtime/agent-skills.exe`，"
        "Linux/macOS 安装为 `.agents/runtime/agent-skills`。该名称同时用于 Builder 默认产物与 Release ZIP 内 binary。\n\n"
    )
    if marker not in text:
        raise RuntimeError("Runtime README 缺少项目安装边界")
    text = text.replace(marker, marker + note, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def _verify_no_legacy_name() -> None:
    """迁移提交前再次确认当前 live 表面没有连续旧产品名。"""
    offenders = []
    for path in _live_text_files():
        if path.resolve() in {SELF, WORKFLOW.resolve()}:
            continue
        if LEGACY_NAME in path.read_text(encoding="utf-8"):
            offenders.append(path.relative_to(ROOT).as_posix())
    if offenders:
        raise RuntimeError(f"迁移后仍存在旧 Runtime 产品名：{offenders}")


def main() -> None:
    """执行一次性迁移并移除临时迁移资产。"""
    _replace_legacy_name()
    _rewrite_release_workflow()
    _rewrite_release_zip_test()
    _rewrite_release_surface_test()
    _rewrite_product_name_test()
    _rewrite_usage()
    _rewrite_maintenance()
    _rewrite_runtime_reference()
    _rewrite_runtime_readme()
    _verify_no_legacy_name()
    if WORKFLOW.exists():
        WORKFLOW.unlink()
    if SELF.exists():
        SELF.unlink()


if __name__ == "__main__":
    main()
