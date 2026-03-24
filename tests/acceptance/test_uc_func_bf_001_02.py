"""Traceability:
- related_func: FUNC-BF-001-02
- feature: docs/usecases/function/algorithm_execution/UC-FUNC-BF-001-02_探索を実行して最良解を得る.feature
"""

from __future__ import annotations

from py_sprit.domain.algorithm_execution import TerminationCriterion, TourActivityKind
from tests.support import define_problem, make_problem_inputs


def test_search_executes_with_explicit_termination(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    result = runtime.algorithm_execution.execute_search(
        problem=definition.problem,
        termination_criterion=TerminationCriterion(max_iterations=3),
    )
    assert result.is_success is True
    assert result.best_solution is not None


def test_search_executes_with_default_termination(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    result = runtime.algorithm_execution.execute_search(problem=definition.problem)
    assert result.is_success is True
    assert result.best_solution is not None


def test_search_returns_technical_logs_when_enabled(runtime):
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


def test_search_handles_runnable_shipment_and_returns_pickup_delivery_activities(runtime):
    definition = define_problem(runtime, **make_problem_inputs(job_count=0, include_shipment=True))
    result = runtime.algorithm_execution.execute_search(
        problem=definition.problem,
        enable_technical_logs=True,
    )

    assert result.is_success is True
    assert result.best_solution is not None
    assert result.technical_log is not None
    assert result.technical_log.initial_route_count >= 1
    route = result.best_solution.routes[0]
    assert [activity.activity_kind for activity in route.activities] == [
        TourActivityKind.PICKUP,
        TourActivityKind.DELIVERY,
    ]


def test_search_fails_when_no_candidate_solution_can_be_returned(runtime):
    definition = define_problem(runtime, **make_problem_inputs(vehicle_capacity=0, job_count=1))
    result = runtime.algorithm_execution.execute_search(problem=definition.problem)
    assert result.is_success is False
    assert result.reason == "候補解を返せない"
