"""Traceability:
- related_func: FUNC-BF-002-02
- feature: docs/usecases/function/problem_definition/UC-FUNC-BF-002-02_問題モデル整合性を確認する.feature
"""

from __future__ import annotations

from py_sprit.domain.problem_definition import FleetSize
from tests.support import make_problem_inputs


def test_問題モデルが整合しているため検証済みになる(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(**make_problem_inputs())
    result = runtime.problem_definition.validate_problem_model(completeness.next_state)
    assert result.is_success is True


def test_Breakを含むためFleetSize_INFINITEを使えないことを確認する(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(
        **make_problem_inputs(with_break=True, fleet_size=FleetSize.INFINITE)
    )
    result = runtime.problem_definition.validate_problem_model(completeness.next_state)
    assert result.is_success is False
    assert result.reason == "Break を含むのに FleetSize が INFINITE である"
