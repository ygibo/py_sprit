"""Traceability:
- related_func: FUNC-BF-006-03
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-006-03_経路注記を受け取る.feature
"""

from __future__ import annotations

from py_sprit.domain.solution_visualization import RouteAnnotationGenerationResult
from tests.support import make_problem_inputs, make_solution


def test_returns_generated_route_annotation(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    generation = runtime.solution_visualization.generate_route_annotation(solution=solution)
    result = runtime.solution_visualization.return_route_annotation(generation)
    assert result.is_success is True
    assert result.available_route_annotation is not None


def test_does_not_return_route_annotation_when_generation_failed(runtime):
    result = runtime.solution_visualization.return_route_annotation(
        RouteAnnotationGenerationResult(
            is_success=False,
            next_state=None,
            generated_route_annotation=None,
            reason="生成済みの RouteAnnotation が存在しない",
        )
    )
    assert result.is_success is False

