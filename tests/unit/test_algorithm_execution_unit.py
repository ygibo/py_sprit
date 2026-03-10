from __future__ import annotations

from dataclasses import replace
from random import Random

from py_sprit.domain.algorithm_execution import (
    BestSolutionSelectionService,
    SearchExecutionService,
    SearchStartPolicy,
    TerminationCriterion,
    build_search_technical_log,
)
from py_sprit.infrastructure.gateways import InMemoryExtensionContractsRegistryGateway
from tests.support import define_problem, make_initial_solution, make_problem_inputs


def test_search_start_policy_accepts_defined_problem(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    result = SearchStartPolicy().evaluate(
        problem=definition.problem,
        initial_solution=None,
        termination_criterion=TerminationCriterion(max_iterations=3),
    )
    assert result.is_success is True
    assert result.next_state is not None


def test_best_solution_selection_rejects_all_unassigned_candidates():
    definition = define_problem(__import__("py_sprit.bootstrap", fromlist=["create_runtime"]).create_runtime(), **make_problem_inputs(vehicle_capacity=0))
    service = SearchExecutionService(
        rng=Random(1),
        registry_gateway=InMemoryExtensionContractsRegistryGateway(),
    )
    candidates = service.run(
        problem=definition.problem,
        termination_criterion=TerminationCriterion(max_iterations=2),
        initial_solution=None,
    )
    assert BestSolutionSelectionService().select(candidates) is None


def test_search_execution_service_returns_solution_with_unassigned_jobs(runtime):
    definition = define_problem(runtime, **make_problem_inputs(vehicle_capacity=1, job_count=2))
    service = SearchExecutionService(
        rng=Random(2),
        registry_gateway=InMemoryExtensionContractsRegistryGateway(),
    )
    candidates = service.run(
        problem=definition.problem,
        termination_criterion=TerminationCriterion(max_iterations=2),
        initial_solution=None,
    )
    best = BestSolutionSelectionService().select(candidates)
    assert best is not None
    assert len(best.routes) == 1
    assert len(best.unassigned_jobs) == 1


def test_build_search_technical_log_records_iteration_count(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    service = SearchExecutionService(
        rng=Random(3),
        registry_gateway=InMemoryExtensionContractsRegistryGateway(),
    )
    termination = TerminationCriterion(max_iterations=4)
    candidates = service.run(
        problem=definition.problem,
        termination_criterion=termination,
        initial_solution=None,
    )

    technical_log = build_search_technical_log(
        problem=definition.problem,
        termination_criterion=termination,
        initial_solution=None,
        candidate_solutions=candidates,
        constraint_registration_count=0,
        elapsed_ms=1.25,
    )

    assert technical_log is not None
    assert len(technical_log.iterations) == 4
    assert technical_log.max_iterations == 4
    assert technical_log.used_provided_initial_solution is False


def test_build_search_technical_log_marks_only_improving_candidates_as_incumbent(runtime):
    definition = define_problem(runtime, **make_problem_inputs())
    initial_solution = make_initial_solution(definition.problem)
    worse_candidate = replace(initial_solution, cost=initial_solution.cost + 5.0)
    better_candidate = replace(initial_solution, cost=initial_solution.cost - 5.0)

    technical_log = build_search_technical_log(
        problem=definition.problem,
        termination_criterion=TerminationCriterion(max_iterations=2),
        initial_solution=initial_solution,
        candidate_solutions=(initial_solution, worse_candidate, better_candidate),
        constraint_registration_count=0,
        elapsed_ms=2.5,
    )

    assert technical_log is not None
    assert technical_log.used_provided_initial_solution is True
    assert [iteration.accepted_as_incumbent for iteration in technical_log.iterations] == [
        False,
        True,
    ]
    assert technical_log.iterations[-1].incumbent_cost_after_iteration == better_candidate.cost
    assert technical_log.final_incumbent_cost == better_candidate.cost
