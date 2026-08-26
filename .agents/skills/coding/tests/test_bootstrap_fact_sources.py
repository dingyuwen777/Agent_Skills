from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CODING_PATH = ROOT / ".agents/skills/coding/scripts/coding.py"


def _load_coding():
    """加载 Coding CLI 模块，以真实临时项目验证 Bootstrap 事实入口输出。"""
    spec = importlib.util.spec_from_file_location("coding_bootstrap_fact_sources", CODING_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 coding.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODING = _load_coding()


class BootstrapFactSourcesTest(unittest.TestCase):
    """验证多语言项目 Bootstrap 只列真实事实入口，不把文件名升级成技术栈结论。"""

    def test_polyglot_manifests_are_listed_without_affirmative_framework_inference(self) -> None:
        """Python/Node/Rust/Go 入口可同时进入导航，但不生成 FastAPI/React/PostgreSQL 等项目断言。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / ".agents/skills/coding"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Coding\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='example'\n", encoding="utf-8")
            (root / "package.json").write_text('{"name":"example"}\n', encoding="utf-8")
            (root / "Cargo.toml").write_text("[package]\nname='example'\nversion='0.1.0'\n", encoding="utf-8")
            (root / "go.mod").write_text("module example.invalid/project\ngo 1.25\n", encoding="utf-8")

            CODING.bootstrap_project(root)
            content = (root / "AGENTS.md").read_text(encoding="utf-8")

            for path in ("pyproject.toml", "package.json", "Cargo.toml", "go.mod"):
                self.assertIn(f"`{path}`", content)
            self.assertNotIn("本项目使用 FastAPI", content)
            self.assertNotIn("本项目使用 React", content)
            self.assertNotIn("数据库使用 PostgreSQL", content)
            self.assertIn("不能单凭文件名推出 React、FastAPI、PostgreSQL", content)


if __name__ == "__main__":
    unittest.main()
