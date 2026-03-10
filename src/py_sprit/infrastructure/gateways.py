from __future__ import annotations

from dataclasses import dataclass, field

from py_sprit.domain.algorithm_execution import (
    SearchCompletionResult,
    TourActivity,
    VehicleRoute,
    VehicleRoutingProblemSolution,
)
from py_sprit.domain.extension_contracts import ConstraintRegistration
from py_sprit.domain.problem_definition import Break, ProblemDefinitionStatus, VehicleRoutingProblem


@dataclass(slots=True)
class InMemoryExtensionContractsRegistryGateway:
    _registrations: list[ConstraintRegistration] = field(default_factory=list)

    def register(self, registration: ConstraintRegistration) -> None:
        self._registrations = [
            existing
            for existing in self._registrations
            if existing.registration_id != registration.registration_id
        ]
        self._registrations.append(registration)

    def available_registrations(self) -> tuple[ConstraintRegistration, ...]:
        return tuple(self._registrations)


@dataclass(slots=True)
class InMemoryProblemDefinitionGateway:
    def confirm_searchable(self, problem: VehicleRoutingProblem) -> bool:
        if problem.status is not ProblemDefinitionStatus.DEFINED:
            return False
        return not any(isinstance(job, Break) for job in problem.jobs)


@dataclass(slots=True)
class InMemorySolutionModelGateway:
    def return_solution(self, result: SearchCompletionResult) -> SearchCompletionResult:
        return result


@dataclass(slots=True)
class InMemoryAlgorithmExecutionVisualizationGateway:
    def resolve_solution(
        self,
        solution: VehicleRoutingProblemSolution | None,
    ) -> VehicleRoutingProblemSolution | None:
        return solution

    def resolve_routes(
        self,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
    ) -> tuple[VehicleRoute, ...]:
        if solution is None:
            return ()
        if vehicle_id is None:
            return solution.routes
        return tuple(route for route in solution.routes if route.vehicle.id == vehicle_id)

    def resolve_activities(
        self,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
    ) -> tuple[TourActivity, ...]:
        routes = self.resolve_routes(solution, vehicle_id)
        return tuple(activity for route in routes for activity in route.activities)
