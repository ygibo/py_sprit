from __future__ import annotations

from dataclasses import dataclass

from py_sprit.application.algorithm_execution import (
    AcceptSearchRequestService,
    ExecuteSearchService,
    ReturnSolutionService,
)
from py_sprit.domain.algorithm_execution import (
    SearchAcceptanceResult,
    SearchCompletionResult,
    TerminationCriterion,
    VehicleRoutingProblemSolution,
)
from py_sprit.domain.problem_definition import VehicleRoutingProblem


@dataclass(slots=True)
class SearchExecutionPresenter:
    def present_acceptance_result(
        self,
        result: SearchAcceptanceResult,
    ) -> SearchAcceptanceResult:
        return result

    def present_completion_result(
        self,
        result: SearchCompletionResult,
    ) -> SearchCompletionResult:
        return result

    def present_solution_result(
        self,
        result: SearchCompletionResult,
    ) -> SearchCompletionResult:
        return result


@dataclass(slots=True)
class SearchExecutionController:
    accept_search_request_service: AcceptSearchRequestService
    execute_search_service: ExecuteSearchService
    return_solution_service: ReturnSolutionService
    presenter: SearchExecutionPresenter

    def accept_search_request(
        self,
        *,
        problem: VehicleRoutingProblem,
        initial_solution: VehicleRoutingProblemSolution | None = None,
        termination_criterion: TerminationCriterion | None = None,
    ) -> SearchAcceptanceResult:
        result = self.accept_search_request_service.execute(
            problem=problem,
            initial_solution=initial_solution,
            termination_criterion=termination_criterion,
        )
        return self.presenter.present_acceptance_result(result)

    def execute_search(
        self,
        *,
        problem: VehicleRoutingProblem | SearchAcceptanceResult,
        initial_solution: VehicleRoutingProblemSolution | None = None,
        termination_criterion: TerminationCriterion | None = None,
        enable_technical_logs: bool = False,
    ) -> SearchCompletionResult:
        result = self.execute_search_service.execute(
            problem=problem,
            initial_solution=initial_solution,
            termination_criterion=termination_criterion,
            enable_technical_logs=enable_technical_logs,
        )
        return self.presenter.present_completion_result(result)

    def return_solution(
        self,
        completion_result: SearchCompletionResult,
    ) -> SearchCompletionResult:
        result = self.return_solution_service.execute(completion_result)
        return self.presenter.present_solution_result(result)


@dataclass(slots=True)
class AlgorithmExecutionAdapter:
    controller: SearchExecutionController

    def accept_search_request(self, **kwargs: object) -> SearchAcceptanceResult:
        return self.controller.accept_search_request(**kwargs)

    def execute_search(
        self,
        *,
        problem: VehicleRoutingProblem | SearchAcceptanceResult,
        initial_solution: VehicleRoutingProblemSolution | None = None,
        termination_criterion: TerminationCriterion | None = None,
        enable_technical_logs: bool = False,
    ) -> SearchCompletionResult:
        return self.controller.execute_search(
            problem=problem,
            initial_solution=initial_solution,
            termination_criterion=termination_criterion,
            enable_technical_logs=enable_technical_logs,
        )

    def return_solution(
        self,
        completion_result: SearchCompletionResult,
    ) -> SearchCompletionResult:
        return self.controller.return_solution(completion_result)
