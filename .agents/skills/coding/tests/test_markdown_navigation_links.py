from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime import project_installer


ROOT = Path(__file__).resolve().parents[4]
CODING_PATH = ROOT / ".agents/skills/coding/scripts/coding.py"
INLINE_MD = re.compile(r"`([^`\n]+\.md)`")
PATH_LINK = re.compile(r"\[`([^`\n]+\.md)`\]\(([^)]+)\)")
FENCE = re.compile(r"^```(?P<lang>[^`]*)\s*$")
PROJECT_ENTRY_LINK = "[`.agents/skills/ENTRY.md`](.agents/skills/ENTRY.md)"
PROJECT_ROUTER_LINK = "[`.agents/skills/router/SKILL.md`](.agents/skills/router/SKILL.md)"


def _load_coding_module():
    """加载 Coding Bootstrap 模块，验证模板在目标项目根的最终 Markdown 语义。"""
    spec = importlib.util.spec_from_file_location("coding_markdown_navigation", CODING_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 Coding 模块：{CODING_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODING = _load_coding_module()


class MarkdownNavigationLinksTest(unittest.TestCase):
    """验证仓库内承担导航职责的 Markdown 路径既显示路径又可直接点击。"""

    def _markdown_files(self) -> list[Path]:
        """收集当前仓库正式 Markdown，排除临时 Active Change 自身。"""
        result: list[Path] = []
        for path in ROOT.rglob("*.md"):
            relative = path.relative_to(ROOT).as_posix()
            if relative.startswith(".agents/changes/"):
                continue
            if "/" not in relative and relative not in {"AGENTS.md", "README.md", "USAGE.md"}:
                continue
            result.append(path)
        return sorted(result)

    def _resolve_candidate(self, source: Path, raw: str) -> Path | None:
        """把明确属于当前仓库的 Markdown 路径解析到真实文件；目标项目占位路径不参与。"""
        value = raw.strip().replace("\\", "/")
        if any(token in value for token in ("<", ">", "*", "{", "}")):
            return None
        candidates: list[Path] = []
        if value.startswith((".agents/", "runtime/", "scripts/")) or value == "USAGE.md":
            candidates.append(ROOT / value)
        if value.startswith(("coding/", "docs/", "figma/", "review/")):
            candidates.append(ROOT / ".agents/skills" / value)
        if value.startswith("references/"):
            candidates.append(source.parent / value)
        if re.fullmatch(r"\d{2}_.+\.md", value) or value == "SKILL.md":
            candidates.append(source.parent / value)
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix == ".md":
                return candidate.resolve()
        return None

    @staticmethod
    def _inline_token_is_linked(line: str, start: int, end: int) -> bool:
        """判断当前 inline-code token 是否已经位于 Markdown link label 中。"""
        open_bracket = line.rfind("[", 0, start + 1)
        if open_bracket < 0:
            return False
        close_and_target = line.find("](", end)
        if close_and_target < 0:
            return False
        closing = line.find(")", close_and_target + 2)
        return closing >= 0

    def test_concrete_repository_markdown_navigation_is_clickable(self) -> None:
        """真实仓库 Markdown 路径不能继续作为不可点击的 inline code 或纯路径 code block。"""
        offenders: list[str] = []
        for path in self._markdown_files():
            relative = path.relative_to(ROOT).as_posix()
            lines = path.read_text(encoding="utf-8").splitlines()
            in_fence = False
            fence_start = 0
            fence_lines: list[str] = []
            fence_lang = ""

            for line_number, line in enumerate(lines, start=1):
                fence_match = FENCE.match(line)
                if fence_match:
                    if not in_fence:
                        in_fence = True
                        fence_start = line_number
                        fence_lines = []
                        fence_lang = fence_match.group("lang").strip().casefold()
                    else:
                        non_empty = [item.strip() for item in fence_lines if item.strip()]
                        if fence_lang in {"", "text"} and non_empty:
                            resolved = [self._resolve_candidate(path, item) for item in non_empty]
                            if all(item is not None for item in resolved):
                                offenders.append(
                                    f"{relative}:{fence_start} 纯文档路径 fenced block 应改为可点击链接：{non_empty}"
                                )
                        in_fence = False
                        fence_lines = []
                        fence_lang = ""
                    continue

                if in_fence:
                    fence_lines.append(line)
                    continue

                for match in INLINE_MD.finditer(line):
                    candidate = match.group(1)
                    if self._resolve_candidate(path, candidate) is None:
                        continue
                    if self._inline_token_is_linked(line, match.start(), match.end()):
                        continue
                    offenders.append(
                        f"{relative}:{line_number} 真实 Markdown 路径未链接：{candidate}"
                    )

        self.assertEqual(
            offenders,
            [],
            "发现不可点击的仓库 Markdown 导航：\n" + "\n".join(offenders),
        )

    def test_path_label_links_resolve_to_real_markdown(self) -> None:
        """显示 Markdown 路径的仓库内链接必须实际指向存在的 Markdown 文件。"""
        offenders: list[str] = []
        for path in self._markdown_files():
            relative = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            for match in PATH_LINK.finditer(text):
                target = match.group(2).strip()
                if target.startswith(("http://", "https://", "#")):
                    continue
                target_path = (path.parent / target.split("#", 1)[0]).resolve()
                try:
                    target_path.relative_to(ROOT.resolve())
                except ValueError:
                    offenders.append(f"{relative} 链接越出仓库：{target}")
                    continue
                if not target_path.is_file() or target_path.suffix != ".md":
                    offenders.append(f"{relative} 链接目标不存在：{target}")
        self.assertEqual(offenders, [], "发现无效 Markdown 文档链接：\n" + "\n".join(offenders))

    def test_source_keeps_router_links_while_runtime_generated_agents_hide_internal_navigation(self) -> None:
        """Source Mode 保留真实 Router 链接，Runtime 生成的根规则不得暴露内部导航。"""
        source_root_agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        managed_path = ROOT / ".agents/skills/coding/assets/AGENTS.managed.md"
        managed = managed_path.read_text(encoding="utf-8")
        self.assertIn(PROJECT_ENTRY_LINK, source_root_agents)
        self.assertIn(PROJECT_ROUTER_LINK, source_root_agents)
        self.assertNotIn(PROJECT_ROUTER_LINK, managed)
        self.assertNotIn(".agents/skills/", managed)
        self.assertNotIn("研发治理 MCP", managed)
        self.assertNotIn("Runtime Mode", managed)
        self.assertIn("无论采用哪种通用治理执行方式", managed)
        self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", managed)
        self.assertIn("只改变通用治理约束的取得和呈现方式", managed)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = root / ".agents/skills"
            coding = skills / "coding"
            coding.mkdir(parents=True)
            (coding / "SKILL.md").write_text("# Coding\n", encoding="utf-8")
            (skills / "ENTRY.md").write_text("# Entry\n", encoding="utf-8")
            router = skills / "router"
            router.mkdir()
            (router / "SKILL.md").write_text("# Router\n", encoding="utf-8")
            CODING.bootstrap_project(root)
            generated = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn(PROJECT_ENTRY_LINK, generated)
            self.assertNotIn(PROJECT_ROUTER_LINK, generated)
            self.assertNotIn(".agents/skills/", generated)
            self.assertNotIn("研发治理 MCP", generated)
            self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", generated)
            self.assertIn("只改变通用治理约束的取得和呈现方式", generated)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload_files = {
                "ENTRY.md": b"# Entry\n",
                "coding/assets/AGENTS.managed.md": managed_path.read_bytes(),
                "coding/assets/AGENTS.template.md": (
                    ROOT / ".agents/skills/coding/assets/AGENTS.template.md"
                ).read_bytes(),
            }
            generated = project_installer._updated_agents_content(
                root,
                None,
                payload_files,
            ).decode("utf-8")
            self.assertNotIn(PROJECT_ENTRY_LINK, generated)
            self.assertNotIn(PROJECT_ROUTER_LINK, generated)
            self.assertNotIn(".agents/skills/", generated)
            self.assertNotIn("研发治理 MCP", generated)
            self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", generated)
            self.assertIn("只改变通用治理约束的取得和呈现方式", generated)


if __name__ == "__main__":
    unittest.main()