"""Traceability:
- related_func: FUNC-BF-002-03
- feature: docs/usecases/function/problem_definition/UC-FUNC-BF-002-03_問題モデルを確定する.feature
"""

from __future__ import annotations

from tests.support import make_problem_inputs


def test_検証済み構成要素から問題モデルを確定する(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(**make_problem_inputs())
    consistency = runtime.problem_definition.validate_problem_model(completeness.next_state)
    result = runtime.problem_definition.define_problem_model(consistency.next_state)
    assert result.is_success is True
    assert result.problem is not None


def test_未検証の構成要素を含むため確定できない(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(**make_problem_inputs())
    result = runtime.problem_definition.define_problem_model(completeness.next_state)
    assert result.is_success is False
    assert result.reason == "検証済みでない構成要素を含む"
