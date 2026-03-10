"""Traceability:
- related_func: FUNC-BF-004-01
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-004-01_可視化入力を受け付ける.feature
"""

from __future__ import annotations

from tests.support import make_problem_inputs, make_solution


def test_accepts_visualization_input_when_required_fields_are_present(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    result = runtime.solution_visualization.confirm_visualization_input(solution=solution)
    assert result.is_success is True


def test_accepts_visualization_input_without_visualization_options(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    result = runtime.solution_visualization.confirm_visualization_input(
        solution=solution,
        options=None,
    )
    assert result.is_success is True


def test_rejects_visualization_input_when_solution_is_missing(runtime):
    result = runtime.solution_visualization.confirm_visualization_input(solution=None)
    assert result.is_success is False

