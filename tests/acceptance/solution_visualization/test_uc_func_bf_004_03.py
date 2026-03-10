"""Traceability:
- related_func: FUNC-BF-004-03
- feature: docs/usecases/function/solution_visualization/UC-FUNC-BF-004-03_可視化成果物を受け取る.feature
"""

from __future__ import annotations

from py_sprit.domain.solution_visualization import VisualizationArtifactGenerationResult
from tests.support import make_problem_inputs, make_solution


def test_returns_generated_visualization_artifact(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    generation = runtime.solution_visualization.generate_visualization_artifact(solution=solution)
    result = runtime.solution_visualization.return_visualization_artifact(generation)
    assert result.is_success is True
    assert result.available_artifact is not None


def test_does_not_return_visualization_artifact_when_generation_failed(runtime):
    result = runtime.solution_visualization.return_visualization_artifact(
        VisualizationArtifactGenerationResult(
            is_success=False,
            next_state=None,
            generated_artifact=None,
            reason="生成済みの VisualizationArtifact が存在しない",
        )
    )
    assert result.is_success is False

