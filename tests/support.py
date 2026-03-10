from __future__ import annotations

from dataclasses import replace
from math import nan

from py_sprit.domain.algorithm_execution import build_greedy_initial_solution
from py_sprit.domain.extension_contracts import ConstraintEvaluationContext, ConstraintTargetDescriptor
from py_sprit.domain.problem_definition import (
    Break,
    FleetSize,
    Service,
    Shipment,
    Vehicle,
    VehicleType,
)
from py_sprit.domain.shared import Capacity, Location, Skills, TimeWindow


def make_location(location_id: str, x: float, y: float) -> Location:
    return Location(id=location_id, x=x, y=y)


def make_vehicle_type(type_id: str = "vehicle-type", capacity: int = 2) -> VehicleType:
    return VehicleType(id=type_id, capacity=Capacity.single(capacity))


def make_vehicle(
    vehicle_id: str = "vehicle-1",
    *,
    vehicle_type: VehicleType | None = None,
    latest_end: float = 100.0,
    skills: tuple[str, ...] = (),
) -> Vehicle:
    vehicle_type = vehicle_type or make_vehicle_type()
    return Vehicle(
        id=vehicle_id,
        vehicle_type=vehicle_type,
        start_location=make_location(f"{vehicle_id}-start", 0.0, 0.0),
        end_location=make_location(f"{vehicle_id}-end", 0.0, 0.0),
        earliest_start=0.0,
        latest_end=latest_end,
        skills=Skills(frozenset(skills)),
    )


def make_service(
    service_id: str,
    *,
    x: float,
    y: float,
    demand: int = 1,
    tw_end: float = 100.0,
    service_duration: float = 0.0,
    required_skills: tuple[str, ...] = (),
) -> Service:
    return Service(
        id=service_id,
        location=make_location(service_id, x, y),
        demand=Capacity.single(demand),
        required_skills=Skills(frozenset(required_skills)),
        time_window=TimeWindow(0.0, tw_end),
        service_duration=service_duration,
    )


def make_break(break_id: str = "break-1") -> Break:
    return Break(
        id=break_id,
        location=make_location(break_id, 0.0, 0.0),
        time_window=TimeWindow(0.0, 10.0),
    )


def make_problem_inputs(
    *,
    vehicle_count: int = 1,
    job_count: int = 2,
    vehicle_capacity: int = 2,
    demand: int = 1,
    with_break: bool = False,
    include_shipment: bool = False,
    fleet_size: FleetSize = FleetSize.FINITE,
) -> dict[str, object]:
    vehicle_type = make_vehicle_type(capacity=vehicle_capacity)
    vehicles = tuple(
        make_vehicle(f"vehicle-{index + 1}", vehicle_type=vehicle_type)
        for index in range(vehicle_count)
    )
    jobs = tuple(
        make_service(f"job-{index + 1}", x=float(index + 1), y=0.0, demand=demand)
        for index in range(job_count)
    )
    if include_shipment:
        jobs = jobs + (
            Shipment(
                id="shipment-1",
                location=make_location("shipment-pickup", 5.0, 0.0),
                delivery_location=make_location("shipment-delivery", 10.0, 0.0),
            ),
        )
    breaks = (make_break(),) if with_break else ()
    return {
        "vehicle_types": (vehicle_type,),
        "vehicles": vehicles,
        "jobs": jobs,
        "fleet_size": fleet_size,
        "breaks": breaks,
    }


def define_problem(runtime, **kwargs):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(**kwargs)
    assert completeness.next_state is not None
    consistency = runtime.problem_definition.validate_problem_model(completeness.next_state)
    assert consistency.next_state is not None
    return runtime.problem_definition.define_problem_model(consistency.next_state)


def solve_problem(runtime, **kwargs):
    definition = define_problem(runtime, **kwargs)
    completion = runtime.algorithm_execution.execute_search(problem=definition.problem)
    return runtime.algorithm_execution.return_solution(completion)


def make_solution(runtime, **kwargs):
    returned = solve_problem(runtime, **kwargs)
    assert returned.is_success is True
    assert returned.best_solution is not None
    return returned.best_solution


def make_solution_with_nonfinite_location(solution):
    route = solution.routes[0]
    broken_job = replace(
        route.jobs[0],
        location=Location(id=f"{route.jobs[0].id}-broken", x=nan, y=route.jobs[0].location.y),
    )
    broken_activity = replace(route.activities[0], job=broken_job)
    broken_route = replace(
        route,
        jobs=(broken_job, *route.jobs[1:]),
        activities=(broken_activity, *route.activities[1:]),
    )
    return replace(solution, routes=(broken_route, *solution.routes[1:]))


def make_initial_solution(problem):
    return build_greedy_initial_solution(problem, tuple())


class AlwaysCompatibleConstraint:
    def is_feasible(self, context: ConstraintEvaluationContext) -> bool:
        return True

    def penalty(self, context: ConstraintEvaluationContext) -> float:
        return 0.0


class VehicleRouteJobLimitConstraint:
    def __init__(self, limit: int) -> None:
        self.limit = limit

    def is_feasible(self, context: ConstraintEvaluationContext) -> bool:
        route = context.vehicle_route
        if route is None:
            return True
        return len(route.jobs) <= self.limit

    def penalty(self, context: ConstraintEvaluationContext) -> float:
        return 0.0


class TourActivityPenaltyConstraint:
    def __init__(self, penalty_value: float) -> None:
        self.penalty_value = penalty_value

    def is_feasible(self, context: ConstraintEvaluationContext) -> bool:
        return True

    def penalty(self, context: ConstraintEvaluationContext) -> float:
        return self.penalty_value if context.tour_activity is not None else 0.0


def make_vehicle_route_target(target_id: str | None = None) -> ConstraintTargetDescriptor:
    return ConstraintTargetDescriptor(target_kind="vehicle_route", target_id=target_id)


def make_tour_activity_target(target_id: str | None = None) -> ConstraintTargetDescriptor:
    return ConstraintTargetDescriptor(target_kind="tour_activity", target_id=target_id)
