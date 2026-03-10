"""Traceability:
- related_func: FUNC-BF-001-02
- feature: docs/usecases/function/algorithm_execution/UC-FUNC-BF-001-02_探索を実行して最良解を得る.feature
"""

from __future__ import annotations

from py_sprit.domain.algorithm_execution import TerminationCriterion
from tests.support import define_problem, make_problem_inputs


def test_終了条件付きで探索を実行して最良解を得る(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    result = runtime.algorithm_execution.execute_search(
        problem=definition.problem,
        termination_criterion=TerminationCriterion(max_iterations=3),
    )
    assert result.is_success is True
    assert result.best_solution is not None


def test_既定の終了条件で探索を実行して最良解を得る(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    result = runtime.algorithm_execution.execute_search(problem=definition.problem)
    assert result.is_success is True
    assert result.best_solution is not None


def test_技術ログを有効にして探索の反復推移を受け取る(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    result = runtime.algorithm_execution.execute_search(
        problem=definition.problem,
        termination_criterion=TerminationCriterion(max_iterations=3),
        enable_technical_logs=True,
    )
    assert result.is_success is True
    assert result.best_solution is not None
    assert result.technical_log is not None
    assert len(result.technical_log.iterations) == 3
    assert result.technical_log.iterations[0].iteration == 1


def test_候補解を返せないため探索失敗を受け取る(runtime):
    definition = define_problem(runtime, **make_problem_inputs(vehicle_capacity=0, job_count=1))
    result = runtime.algorithm_execution.execute_search(problem=definition.problem)
    assert result.is_success is False
    assert result.reason == "候補解を返せない"
