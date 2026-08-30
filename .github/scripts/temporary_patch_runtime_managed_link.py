from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "runtime/agent_skills_runtime/project_installer.py"
OLD = '''    if text.count(source_link) != 1:\n        raise ValueError("AGENTS.managed.md Router 链接模板不符合预期")\n    return text.replace(source_link, project_link)\n'''
NEW = '''    return text.replace(source_link, project_link)\n'''

text = PATH.read_text(encoding="utf-8")
if text.count(OLD) != 1:
    raise SystemExit("Runtime managed link 目标片段不是唯一一次，停止修改")
PATH.write_text(text.replace(OLD, NEW), encoding="utf-8")
