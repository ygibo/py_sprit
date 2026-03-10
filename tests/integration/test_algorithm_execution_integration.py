from __future__ import annotations

from py_sprit.domain.algorithm_execution import TerminationCriterion
from py_sprit.domain.extension_contracts import ConstraintTargetDescriptor
from tests.support import (
    TourActivityPenaltyConstraint,
    VehicleRouteJobLimitConstraint,
    define_problem,
    make_initial_solution,
    make_problem_inputs,
)


def test_algorithm_execution_services_cover_success_flow(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    acceptance = runtime.algorithm_execution.accept_search_request(problem=definition.problem)
    assert acceptance.is_success is True
    completion = runtime.algorithm_execution.execute_search(
        problem=acceptance,
        enable_technical_logs=True,
    )
    assert completion.is_success is True
    assert completion.technical_log is not None
    returned = runtime.algorithm_execution.return_solution(completion)
    assert returned.is_success is True
    assert returned.best_solution is not None
    assert returned.technical_log == completion.technical_log


def test_algorithm_execution_services_cover_candidate_solution_failure(runtime):
    definition = define_problem(runtime, **make_problem_inputs(vehicle_capacity=0, job_count=1))
    completion = runtime.algorithm_execution.execute_search(
        problem=definition.problem,
        enable_technical_logs=True,
    )
    assert completion.is_success is False
    assert completion.reason == "候補解を返せない"
    assert completion.technical_log is not None
    assert completion.technical_log.final_incumbent_route_count == 0


def test_registered_constraint_affects_next_execute_search(runtime):
    definition = define_problem(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    runtime.extension_contracts.register_constraint(
        constraint=VehicleRouteJobLimitConstraint(limit=0),
        purpose="block every route",
        target_descriptor=ConstraintTargetDescriptor(target_kind="vehicle_route"),
    )
    completion = runtime.algorithm_execution.execute_search(problem=definition.problem)
    assert completion.is_success is False
    assert completion.reason == "候補解を返せない"

    runtime_with_penalty = runtime
    definition_with_penalty = define_problem(runtime_with_penalty, **make_problem_inputs(vehicle_count=1, job_count=1))
    runtime_with_penalty.extension_contracts.register_constraint(
        constraint=TourActivityPenaltyConstraint(5.0),
        purpose="soft penalty",
        target_descriptor=ConstraintTargetDescriptor(target_kind="tour_activity"),
    )
    penalized = runtime_with_penalty.algorithm_execution.execute_search(problem=definition_with_penalty.problem)
    assert penalized.is_success is False or penalized.best_solution is not None


def test_algorithm_execution_accepts_initial_solution(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    initial_solution = make_initial_solution(definition.problem)
    acceptance = runtime.algorithm_execution.accept_search_request(
        problem=definition.problem,
        initial_solution=initial_solution,
    )
    assert acceptance.is_success is True


def test_algorithm_execution_omits_technical_log_by_default(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    completion = runtime.algorithm_execution.execute_search(problem=definition.problem)

    assert completion.is_success is True
    assert completion.best_solution is not None
    assert completion.technical_log is None


def test_algorithm_execution_acceptance_path_returns_iteration_logs(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    acceptance = runtime.algorithm_execution.accept_search_request(
        problem=definition.problem,
        termination_criterion=TerminationCriterion(max_iterations=3),
    )

    assert acceptance.is_success is True

    completion = runtime.algorithm_execution.execute_search(
        problem=acceptance,
        enable_technical_logs=True,
    )

    assert completion.is_success is True
    assert completion.technical_log is not None
    assert len(completion.technical_log.iterations) == acceptance.termination_criterion.max_iterations
