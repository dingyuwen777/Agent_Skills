from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle


ROOT = Path(__file__).resolve().parents[4]
REFERENCES = ROOT / ".agents/skills/coding/references"
RENAMES = {
    "13_目标项目安装与AGENTS_Bootstrap.md": ("12_目标项目安装与AGENTS_Bootstrap.md", "coding.reference.13"),
    "14_本地MCP_Runtime分发与原文上下文加载.md": ("13_本地MCP_Runtime分发与原文上下文加载.md", "coding.reference.14"),
    "15_Git交付依赖安全与宿主能力边界.md": ("14_Git交付依赖安全与宿主能力边界.md", "coding.reference.15"),
    "16_规则内容守恒与Skill维护.md": ("15_规则内容守恒与Skill维护.md", "coding.reference.16"),
    "17_前端与Design-to-Code实施规则.md": ("16_前端与Design-to-Code实施规则.md", "coding.reference.17"),
}


class CodingReferenceNumberingTest(unittest.TestCase):
    """验证 Coding Reference 文件编号连续，同时保持 Stable ID 与 live 导航可达。"""

    def _live_text_files(self) -> list[Path]:
        """收集会参与源码导航/维护的 live 文本，排除测试和临时 Change 自身。"""
        paths = [
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "runtime/README.md",
            ROOT / ".agents/MAINTENANCE.md",
        ]
        skill_root = ROOT / ".agents/skills"
        for path in skill_root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml", ".py"}:
                continue
            if "tests" in path.parts:
                continue
            paths.append(path)
        return sorted(set(paths))

    def test_reference_filename_prefixes_are_contiguous(self) -> None:
        """Coding references 的两位数字文件前缀必须从 01 连续增长且无缺口。"""
        names = sorted(path.name for path in REFERENCES.glob("*.md"))
        prefixes = [int(name.split("_", 1)[0]) for name in names]
        self.assertEqual(len(names), 17)
        self.assertEqual(prefixes, list(range(1, len(names) + 1)))

    def test_renamed_files_preserve_stable_reference_ids(self) -> None:
        """文件导航编号改变时，Runtime Stable Reference ID 不得随文件前缀漂移。"""
        bundle = build_bundle(ROOT)
        coding_entries = {
            str(entry["filename"]): str(entry["id"])
            for entry in bundle["references"]
            if str(entry["skill"]) == "coding"
        }
        for old_name, (new_name, stable_id) in RENAMES.items():
            self.assertNotIn(old_name, coding_entries)
            self.assertEqual(coding_entries.get(new_name), stable_id)

    def test_live_navigation_contains_no_old_reference_filenames(self) -> None:
        """所有 live 规则/维护导航必须切到新文件名，避免 Source Mode 改名后断链。"""
        offenders: dict[str, list[str]] = {}
        for path in self._live_text_files():
            text = path.read_text(encoding="utf-8")
            hits = [old_name for old_name in RENAMES if old_name in text]
            if hits:
                offenders[path.relative_to(ROOT).as_posix()] = hits
        self.assertEqual(offenders, {}, f"live 导航仍引用旧 Coding Reference 文件名：{offenders}")


if __name__ == "__main__":
    unittest.main()
