"""Traceability:
- related_func: FUNC-BF-005-03
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-005-03_経路地図を受け取る.feature
"""

from __future__ import annotations

from py_sprit.domain.solution_visualization import RouteMapGenerationResult
from tests.support import make_problem_inputs, make_solution


def test_returns_generated_route_map(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    generation = runtime.solution_visualization.generate_route_map(solution=solution)
    result = runtime.solution_visualization.return_route_map(generation)
    assert result.is_success is True
    assert result.available_route_map is not None


def test_does_not_return_route_map_when_generation_failed(runtime):
    result = runtime.solution_visualization.return_route_map(
        RouteMapGenerationResult(
            is_success=False,
            next_state=None,
            generated_route_map=None,
            reason="生成済みの RouteMap が存在しない",
        )
    )
    assert result.is_success is False

