from __future__ import annotations

from dataclasses import dataclass

from py_sprit.domain.problem_definition import (
    Break,
    FleetSize,
    ProblemCompletenessResult,
    ProblemConsistencyResult,
    ProblemDefinitionResult,
    ProblemModelComponents,
    ProblemModelCompletenessValidator,
    ProblemModelConsistencyValidator,
    Vehicle,
    VehicleRoutingProblem,
    VehicleRoutingProblemFactory,
    VehicleType,
    collect_breaks,
)
from py_sprit.domain.shared import (
    EuclideanTransportCost,
    TransportCost,
    VehicleRoutingActivityCosts,
    ZeroVehicleRoutingActivityCosts,
)
from py_sprit.domain.problem_definition import Job


@dataclass(slots=True)
class ConfirmProblemModelInputsService:
    factory: VehicleRoutingProblemFactory
    completeness_validator: ProblemModelCompletenessValidator

    def execute(
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
        explicit_breaks = breaks or collect_breaks(jobs)
        all_jobs = tuple(jobs) + tuple(b for b in explicit_breaks if b not in jobs)
        problem = self.factory.create(
            ProblemModelComponents(
                vehicle_types=vehicle_types,
                vehicles=vehicles,
                jobs=all_jobs,
                transport_cost=transport_cost or EuclideanTransportCost(),
                activity_costs=activity_costs or ZeroVehicleRoutingActivityCosts(),
                fleet_size=fleet_size,
                breaks=explicit_breaks,
            )
        )
        return self.completeness_validator.validate(problem)


@dataclass(slots=True)
class ValidateProblemModelService:
    consistency_validator: ProblemModelConsistencyValidator

    def execute(
        self,
        problem: VehicleRoutingProblem,
    ) -> ProblemConsistencyResult:
        return self.consistency_validator.validate(problem)


@dataclass(slots=True)
class DefineProblemModelService:
    def execute(
        self,
        problem: VehicleRoutingProblem,
    ) -> ProblemDefinitionResult:
        return problem.define()
