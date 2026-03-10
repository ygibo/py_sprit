from __future__ import annotations

from dataclasses import dataclass, replace
from time import perf_counter

from py_sprit.domain.algorithm_execution import (
    BestSolutionSelectionService,
    ProblemDefinitionGateway,
    SearchAcceptanceResult,
    SearchCompletionResult,
    SearchExecutionService,
    SearchResultAssemblyPolicy,
    SearchStartPolicy,
    SolutionModelGateway,
    TerminationCriterion,
    VehicleRoutingProblemSolution,
    build_search_technical_log,
)
from py_sprit.domain.problem_definition import VehicleRoutingProblem


@dataclass(slots=True)
class AcceptSearchRequestService:
    problem_definition_gateway: ProblemDefinitionGateway
    search_start_policy: SearchStartPolicy

    def execute(
        self,
        *,
        problem: VehicleRoutingProblem,
        initial_solution: VehicleRoutingProblemSolution | None = None,
        termination_criterion: TerminationCriterion | None = None,
    ) -> SearchAcceptanceResult:
        normalized_termination = termination_criterion or TerminationCriterion()
        if not self.problem_definition_gateway.confirmSearchable(problem):
            return SearchAcceptanceResult(
                is_success=False,
                next_state=None,
                accepted_problem=None,
                initial_solution=initial_solution,
                termination_criterion=normalized_termination,
                reason="問題モデルが探索可能状態でない",
            )
        return self.search_start_policy.evaluate(
            problem=problem,
            initial_solution=initial_solution,
            termination_criterion=normalized_termination,
        )


@dataclass(slots=True)
class ExecuteSearchService:
    accept_service: AcceptSearchRequestService
    search_execution_service: SearchExecutionService
    best_solution_selection_service: BestSolutionSelectionService
    search_result_assembly_policy: SearchResultAssemblyPolicy

    def execute(
        self,
        *,
        problem: VehicleRoutingProblem | SearchAcceptanceResult,
        initial_solution: VehicleRoutingProblemSolution | None = None,
        termination_criterion: TerminationCriterion | None = None,
        enable_technical_logs: bool = False,
    ) -> SearchCompletionResult:
        if isinstance(problem, SearchAcceptanceResult):
            acceptance = problem
        else:
            acceptance = self.accept_service.execute(
                problem=problem,
                initial_solution=initial_solution,
                termination_criterion=termination_criterion,
            )
        if not acceptance.is_success or acceptance.next_state is None or acceptance.accepted_problem is None:
            return SearchCompletionResult(
                is_success=False,
                next_state=None,
                best_solution=None,
                reason=acceptance.reason,
            )
        normalized_termination = acceptance.termination_criterion or TerminationCriterion()
        constraint_registration_count = 0
        if enable_technical_logs:
            constraint_registration_count = self.search_execution_service.count_available_registrations()
        started_at = perf_counter()
        candidate_solutions = self.search_execution_service.run(
            problem=acceptance.accepted_problem,
            termination_criterion=normalized_termination,
            initial_solution=acceptance.initial_solution,
        )
        elapsed_ms = (perf_counter() - started_at) * 1000.0
        technical_log = None
        if enable_technical_logs:
            technical_log = build_search_technical_log(
                problem=acceptance.accepted_problem,
                termination_criterion=normalized_termination,
                initial_solution=acceptance.initial_solution,
                candidate_solutions=candidate_solutions,
                constraint_registration_count=constraint_registration_count,
                elapsed_ms=elapsed_ms,
            )
        best_solution = self.best_solution_selection_service.select(candidate_solutions)
        if best_solution is None:
            return SearchCompletionResult(
                is_success=False,
                next_state=None,
                best_solution=None,
                technical_log=technical_log,
                reason="候補解を返せない",
            )
        completion = acceptance.next_state.complete(best_solution)
        if technical_log is not None:
            completion = replace(completion, technical_log=technical_log)
        return self.search_result_assembly_policy.assemble(completion)


@dataclass(slots=True)
class ReturnSolutionService:
    solution_model_gateway: SolutionModelGateway

    def execute(
        self,
        completion_result: SearchCompletionResult,
    ) -> SearchCompletionResult:
        if not completion_result.is_success or completion_result.best_solution is None:
            return SearchCompletionResult(
                is_success=False,
                next_state=None,
                best_solution=None,
                reason="確定済みの解がないため解を受け取れない",
            )
        return self.solution_model_gateway.returnSolution(completion_result)
