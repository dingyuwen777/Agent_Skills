本文件仅记录 Red 阶段预期失败，Green 后删除。

预期失败：
- 原始 CHANGE.template.md frontmatter 存在独立 `$depends_on` 等占位行，GitHub YAML 解析失败；
- 模板仍包含 Requirement Traceability、Validation Matrix、Completion Audit 等英文人类标签；
- `coding.py` 仍把列表字段渲染为多行 YAML，尚未切换为模板可直接解析的内联列表值。
