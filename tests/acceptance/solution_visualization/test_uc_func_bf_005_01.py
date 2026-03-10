"""Traceability:
- related_func: FUNC-BF-005-01
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-005-01_経路地図の確認対象を受け付ける.feature
"""

from __future__ import annotations

from tests.support import make_problem_inputs, make_solution


def test_accepts_route_map_review_target_when_vehicle_route_exists(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=2, job_count=2))
    result = runtime.solution_visualization.accept_route_map_review_target(solution=solution)
    assert result.is_success is True


def test_rejects_route_map_review_target_when_vehicle_route_is_missing(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    result = runtime.solution_visualization.accept_route_map_review_target(
        solution=solution,
        vehicle_id="missing-vehicle",
    )
    assert result.is_success is False

