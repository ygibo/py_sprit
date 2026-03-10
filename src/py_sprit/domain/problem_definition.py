from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from py_sprit.domain.shared import (
    Capacity,
    EuclideanTransportCost,
    Location,
    Skills,
    TimeWindow,
    TransportCost,
    VehicleRoutingActivityCosts,
    ZeroVehicleRoutingActivityCosts,
)


class FleetSize(str, Enum):
    FINITE = "FINITE"
    INFINITE = "INFINITE"


class ProblemDefinitionStatus(str, Enum):
    COLLECTING_INPUTS = "CollectingInputs"
    VALIDATED = "Validated"
    DEFINED = "Defined"


@dataclass(frozen=True, slots=True)
class VehicleType:
    id: str
    capacity: Capacity = field(default_factory=Capacity)
    fixed_cost: float = 0.0


@dataclass(frozen=True, slots=True)
class Vehicle:
    id: str
    vehicle_type: VehicleType
    start_location: Location
    end_location: Location | None = None
    earliest_start: float = 0.0
    latest_end: float = float("inf")
    skills: Skills = field(default_factory=Skills)

    def __post_init__(self) -> None:
        if self.latest_end < self.earliest_start:
            raise ValueError("vehicle latest_end must not be before earliest_start")


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    location: Location
    demand: Capacity = field(default_factory=Capacity)
    required_skills: Skills = field(default_factory=Skills)
    time_window: TimeWindow = field(default_factory=TimeWindow)
    service_duration: float = 0.0
    job_type: str = "Job"


@dataclass(frozen=True, slots=True)
class Service(Job):
    job_type: str = "Service"


@dataclass(frozen=True, slots=True)
class Shipment(Job):
    delivery_location: Location | None = None
    job_type: str = "Shipment"


@dataclass(frozen=True, slots=True)
class Pickup(Job):
    job_type: str = "Pickup"


@dataclass(frozen=True, slots=True)
class Delivery(Job):
    job_type: str = "Delivery"


@dataclass(frozen=True, slots=True)
class Break(Job):
    job_type: str = "Break"


@dataclass(frozen=True, slots=True)
class ProblemModelComponents:
    vehicle_types: tuple[VehicleType, ...]
    vehicles: tuple[Vehicle, ...]
    jobs: tuple[Job, ...]
    transport_cost: TransportCost
    activity_costs: VehicleRoutingActivityCosts
    fleet_size: FleetSize
    breaks: tuple[Break, ...] = ()


@dataclass(frozen=True, slots=True)
class VehicleRoutingProblem:
    vehicle_types: tuple[VehicleType, ...]
    vehicles: tuple[Vehicle, ...]
    jobs: tuple[Job, ...]
    transport_cost: TransportCost = field(default_factory=EuclideanTransportCost)
    activity_costs: VehicleRoutingActivityCosts = field(
        default_factory=ZeroVehicleRoutingActivityCosts
    )
    fleet_size: FleetSize = FleetSize.FINITE
    breaks: tuple[Break, ...] = ()
    status: ProblemDefinitionStatus = ProblemDefinitionStatus.COLLECTING_INPUTS
    completeness_confirmed: bool = False
    consistency_confirmed: bool = False

    def validateCompleteness(self) -> "ProblemCompletenessResult":
        return ProblemModelCompletenessValidator().validate(self)

    def validateConsistency(self) -> "ProblemConsistencyResult":
        return ProblemModelConsistencyValidator().validate(self)

    def define(self) -> "ProblemDefinitionResult":
        if not self.completeness_confirmed or not self.consistency_confirmed:
            return ProblemDefinitionResult(
                is_success=False,
                next_state=None,
                problem=None,
                reason="検証済みでない構成要素を含む",
            )
        defined_problem = replace(self, status=ProblemDefinitionStatus.DEFINED)
        return ProblemDefinitionResult(
            is_success=True,
            next_state=defined_problem,
            problem=defined_problem,
        )

    @property
    def supported_jobs(self) -> tuple[Service, ...]:
        return tuple(job for job in self.jobs if isinstance(job, Service))


@dataclass(frozen=True, slots=True)
class ProblemCompletenessResult:
    is_success: bool
    next_state: VehicleRoutingProblem | None
    checked_components: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProblemConsistencyResult:
    is_success: bool
    next_state: VehicleRoutingProblem | None
    checked_components: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProblemDefinitionResult:
    is_success: bool
    next_state: VehicleRoutingProblem | None
    problem: VehicleRoutingProblem | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProblemModelCompletenessValidator:
    def validate(self, problem: VehicleRoutingProblem) -> ProblemCompletenessResult:
        missing: list[str] = []
        if not problem.vehicle_types:
            missing.append("VehicleType")
        if not problem.vehicles:
            missing.append("Vehicle")
        if not problem.jobs:
            missing.append("Job")
        unsupported_job_types = [
            job.job_type
            for job in problem.jobs
            if not isinstance(job, (Service, Break))
        ]
        if unsupported_job_types:
            missing.append("supported Service jobs only")
        if problem.transport_cost is None:
            missing.append("TransportCost")
        if problem.activity_costs is None:
            missing.append("VehicleRoutingActivityCosts")
        checked_components = (
            "VehicleType",
            "Vehicle",
            "Job",
            "TimeWindow",
            "TransportCost",
            "VehicleRoutingActivityCosts",
            "FleetSize",
            "Break",
        )
        if missing:
            return ProblemCompletenessResult(
                is_success=False,
                next_state=problem,
                checked_components=checked_components,
                missing_fields=tuple(missing),
                reason="必要情報が不足している",
            )
        validated_problem = replace(
            problem,
            status=ProblemDefinitionStatus.VALIDATED,
            completeness_confirmed=True,
        )
        return ProblemCompletenessResult(
            is_success=True,
            next_state=validated_problem,
            checked_components=checked_components,
        )


@dataclass(frozen=True, slots=True)
class ProblemModelConsistencyValidator:
    def validate(self, problem: VehicleRoutingProblem) -> ProblemConsistencyResult:
        vehicle_ids = [vehicle.id for vehicle in problem.vehicles]
        if len(vehicle_ids) != len(set(vehicle_ids)):
            return ProblemConsistencyResult(
                is_success=False,
                next_state=problem,
                checked_components=("Vehicle",),
                reason="問題モデル不整合",
            )
        job_ids = [job.id for job in problem.jobs]
        if len(job_ids) != len(set(job_ids)):
            return ProblemConsistencyResult(
                is_success=False,
                next_state=problem,
                checked_components=("Job",),
                reason="問題モデル不整合",
            )
        if problem.breaks and problem.fleet_size is FleetSize.INFINITE:
            return ProblemConsistencyResult(
                is_success=False,
                next_state=problem,
                checked_components=("Break", "FleetSize"),
                reason="Break を含むのに FleetSize が INFINITE である",
            )
        vehicle_type_ids = {vehicle_type.id for vehicle_type in problem.vehicle_types}
        for vehicle in problem.vehicles:
            if vehicle.vehicle_type.id not in vehicle_type_ids:
                return ProblemConsistencyResult(
                    is_success=False,
                    next_state=problem,
                    checked_components=("VehicleType", "Vehicle"),
                    reason="問題モデル不整合",
                )
        validated_problem = replace(
            problem,
            status=ProblemDefinitionStatus.VALIDATED,
            completeness_confirmed=True,
            consistency_confirmed=True,
        )
        return ProblemConsistencyResult(
            is_success=True,
            next_state=validated_problem,
            checked_components=(
                "VehicleType",
                "Vehicle",
                "Job",
                "TimeWindow",
                "TransportCost",
                "VehicleRoutingActivityCosts",
                "FleetSize",
                "Break",
            ),
        )


@dataclass(frozen=True, slots=True)
class VehicleRoutingProblemFactory:
    def create(self, initial_components: ProblemModelComponents) -> VehicleRoutingProblem:
        return VehicleRoutingProblem(
            vehicle_types=tuple(initial_components.vehicle_types),
            vehicles=tuple(initial_components.vehicles),
            jobs=tuple(initial_components.jobs),
            transport_cost=initial_components.transport_cost,
            activity_costs=initial_components.activity_costs,
            fleet_size=initial_components.fleet_size,
            breaks=tuple(initial_components.breaks),
        )


def collect_breaks(jobs: Iterable[Job]) -> tuple[Break, ...]:
    return tuple(job for job in jobs if isinstance(job, Break))
