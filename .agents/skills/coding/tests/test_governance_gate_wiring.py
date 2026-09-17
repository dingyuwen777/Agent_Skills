"""锁定治理资产机器 Contract 与正式 PR gate / 分发面的接线。"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_pr_gate_validates_live_issue_and_new_change_contract() -> None:
    """正式 PR gate 必须同时校验 live Issue 实例与本 PR 新增 Change。"""
    text = (ROOT / ".github/scripts/check_pr_requirement_source.py").read_text(encoding="utf-8")
    assert "GOVERNANCE_CONTRACT.validate_issue_instance" in text
    assert "validate_new_changes_since" in text
    assert "GOVERNANCE_CONTRACT.validate_new_change_file" in text
    assert "--diff-filter=A" in text


def test_machine_contract_is_part_of_coding_project_payload_surface() -> None:
    """新增 machine validator 位于 Coding scripts，必须进入现有动态 Project Payload 分发面。"""
    contract = ROOT / ".agents/skills/coding/scripts/governance_contract.py"
    assert contract.is_file()
    payload_source = (ROOT / "runtime/agent_skills_runtime/project_payload.py").read_text(encoding="utf-8")
    assert "scripts" in payload_source
    assert "coding" in payload_source


def test_new_reference_routes_machine_contract_before_governance_delivery() -> None:
    """新 Reference 必须有稳定 ID、Issue/Change 治理触发和现有 Owner 依赖。"""
    text = (ROOT / ".agents/skills/coding/references/29_治理资产机器Contract.md").read_text(
        encoding="utf-8"
    )
    assert '"标识":"coding.reference.30"' in text
    assert '"Issue/工单治理"' in text
    assert '"要求完成门禁"' in text
    assert '"coding.reference.18"' in text
    assert '"coding.reference.25"' in text
