"""Traceability:
- related_func: FUNC-BF-004-02
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-004-02_可視化成果物を生成する.feature
"""

from __future__ import annotations

from tests.support import (
    make_problem_inputs,
    make_solution,
    make_solution_with_nonfinite_location,
)


def test_generates_visualization_artifact_when_coordinates_are_available(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    result = runtime.solution_visualization.generate_visualization_artifact(solution=solution)
    assert result.is_success is True
    assert result.generated_artifact is not None


def test_generates_visualization_artifact_without_visualization_options(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    result = runtime.solution_visualization.generate_visualization_artifact(
        solution=solution,
        options=None,
    )
    assert result.is_success is True


def test_rejects_visualization_artifact_generation_when_coordinates_are_missing(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    broken_solution = make_solution_with_nonfinite_location(solution)
    result = runtime.solution_visualization.generate_visualization_artifact(
        solution=broken_solution,
    )
    assert result.is_success is False

