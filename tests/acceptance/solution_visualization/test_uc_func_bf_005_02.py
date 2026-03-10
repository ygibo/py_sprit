"""Traceability:
- related_func: FUNC-BF-005-02
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-005-02_経路地図を生成する.feature
"""

from __future__ import annotations

from tests.support import (
    make_problem_inputs,
    make_solution,
    make_solution_with_nonfinite_location,
)


def test_generates_route_map_when_coordinates_are_available(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    result = runtime.solution_visualization.generate_route_map(solution=solution)
    assert result.is_success is True
    assert result.generated_route_map is not None


def test_rejects_route_map_generation_when_coordinates_are_missing(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    broken_solution = make_solution_with_nonfinite_location(solution)
    result = runtime.solution_visualization.generate_route_map(solution=broken_solution)
    assert result.is_success is False

