"""Traceability:
- related_func: FUNC-BF-006-02
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-006-02_経路注記を生成する.feature
"""

from __future__ import annotations

from dataclasses import replace
from math import nan

from tests.support import make_problem_inputs, make_solution


def test_generates_route_annotation_when_route_information_is_available(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=2))
    result = runtime.solution_visualization.generate_route_annotation(solution=solution)
    assert result.is_success is True
    assert result.generated_route_annotation is not None


def test_generates_route_annotation_without_visualization_options(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=2))
    result = runtime.solution_visualization.generate_route_annotation(
        solution=solution,
        options=None,
    )
    assert result.is_success is True


def test_rejects_route_annotation_generation_when_route_information_is_incomplete(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    route = solution.routes[0]
    broken_activity = replace(route.activities[0], arrival_time=nan)
    broken_route = replace(route, activities=(broken_activity,))
    broken_solution = replace(solution, routes=(broken_route,))
    result = runtime.solution_visualization.generate_route_annotation(
        solution=broken_solution,
    )
    assert result.is_success is False

