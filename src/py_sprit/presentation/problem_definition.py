from __future__ import annotations

from dataclasses import dataclass

from py_sprit.application.problem_definition import (
    ConfirmProblemModelInputsService,
    DefineProblemModelService,
    ValidateProblemModelService,
)
from py_sprit.domain.problem_definition import (
    Break,
    FleetSize,
    Job,
    ProblemCompletenessResult,
    ProblemConsistencyResult,
    ProblemDefinitionResult,
    Vehicle,
    VehicleRoutingProblem,
    VehicleType,
)
from py_sprit.domain.shared import TransportCost, VehicleRoutingActivityCosts


@dataclass(slots=True)
class ProblemDefinitionPresenter:
    def present_completeness_result(
        self,
        result: ProblemCompletenessResult,
    ) -> ProblemCompletenessResult:
        return result

    def present_consistency_result(
        self,
        result: ProblemConsistencyResult,
    ) -> ProblemConsistencyResult:
        return result

    def present_definition_result(
        self,
        result: ProblemDefinitionResult,
    ) -> ProblemDefinitionResult:
        return result


@dataclass(slots=True)
class ProblemDefinitionController:
    confirm_problem_model_inputs_service: ConfirmProblemModelInputsService
    validate_problem_model_service: ValidateProblemModelService
    define_problem_model_service: DefineProblemModelService
    presenter: ProblemDefinitionPresenter

    def confirm_problem_model_inputs(
        self,
        *,
        vehicle_types: tuple[VehicleType, ...],
        vehicles: tuple[Vehicle, ...],
        jobs: tuple[Job, ...],
        transport_cost: TransportCost | None = None,
        activity_costs: VehicleRoutingActivityCosts | None = None,
        fleet_size: FleetSize = FleetSize.FINITE,
        breaks: tuple[Break, ...] | None = None,
    ) -> ProblemCompletenessResult:
        result = self.confirm_problem_model_inputs_service.execute(
            vehicle_types=vehicle_types,
            vehicles=vehicles,
            jobs=jobs,
            transport_cost=transport_cost,
            activity_costs=activity_costs,
            fleet_size=fleet_size,
            breaks=breaks,
        )
        return self.presenter.present_completeness_result(result)

    def validate_problem_model(
        self,
        problem: VehicleRoutingProblem,
    ) -> ProblemConsistencyResult:
        result = self.validate_problem_model_service.execute(problem)
        return self.presenter.present_consistency_result(result)

    def define_problem_model(
        self,
        problem: VehicleRoutingProblem,
    ) -> ProblemDefinitionResult:
        result = self.define_problem_model_service.execute(problem)
        return self.presenter.present_definition_result(result)


@dataclass(slots=True)
class ProblemDefinitionAdapter:
    controller: ProblemDefinitionController

    def confirm_problem_model_inputs(self, **kwargs: object) -> ProblemCompletenessResult:
        return self.controller.confirm_problem_model_inputs(**kwargs)

    def validate_problem_model(
        self,
        problem: VehicleRoutingProblem,
    ) -> ProblemConsistencyResult:
        return self.controller.validate_problem_model(problem)

    def define_problem_model(
        self,
        problem: VehicleRoutingProblem,
    ) -> ProblemDefinitionResult:
        return self.controller.define_problem_model(problem)
