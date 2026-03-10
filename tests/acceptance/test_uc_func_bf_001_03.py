"""Traceability:
- related_func: FUNC-BF-001-03
- feature: docs/usecases/function/algorithm_execution/UC-FUNC-BF-001-03_解を受け取る.feature
"""

from __future__ import annotations

from py_sprit.domain.algorithm_execution import SearchCompletionResult
from tests.support import define_problem, make_problem_inputs


def test_未割当配送要求を含む解を受け取る(runtime):
    definition = define_problem(runtime, **make_problem_inputs(vehicle_capacity=1, job_count=2))
    completion = runtime.algorithm_execution.execute_search(problem=definition.problem)
    returned = runtime.algorithm_execution.return_solution(completion)
    assert returned.is_success is True
    assert returned.best_solution is not None
    assert len(returned.unassigned_jobs) == 1


def test_未割当配送要求を含まない解を受け取る(runtime):
    definition = define_problem(runtime, **make_problem_inputs(vehicle_capacity=3, job_count=2))
    completion = runtime.algorithm_execution.execute_search(problem=definition.problem)
    returned = runtime.algorithm_execution.return_solution(completion)
    assert returned.is_success is True
    assert returned.best_solution is not None
    assert returned.unassigned_jobs == ()


def test_確定済みの解がないため解を受け取れない(runtime):
    returned = runtime.algorithm_execution.return_solution(
        SearchCompletionResult(
            is_success=False,
            next_state=None,
            best_solution=None,
            reason="候補解を返せない",
        )
    )
    assert returned.is_success is False
    assert returned.reason == "確定済みの解がないため解を受け取れない"
