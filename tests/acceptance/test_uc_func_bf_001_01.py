"""Traceability:
- related_func: FUNC-BF-001-01
- feature: docs/usecases/function/algorithm_execution/UC-FUNC-BF-001-01_探索開始要求を受け付ける.feature
"""

from __future__ import annotations

from tests.support import define_problem, make_initial_solution, make_problem_inputs


def test_問題モデルが探索可能なため探索開始要求が受理される(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    result = runtime.algorithm_execution.accept_search_request(problem=definition.problem)
    assert result.is_success is True


def test_初期解付きの探索開始要求が受理される(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    initial_solution = make_initial_solution(definition.problem)
    result = runtime.algorithm_execution.accept_search_request(
        problem=definition.problem,
        initial_solution=initial_solution,
    )
    assert result.is_success is True


def test_問題モデルが探索可能状態でないため探索開始不可を受け取る(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(**make_problem_inputs())
    result = runtime.algorithm_execution.accept_search_request(problem=completeness.next_state)
    assert result.is_success is False
    assert result.reason == "問題モデルが探索可能状態でない"
