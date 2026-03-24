from __future__ import annotations

from py_sprit import (
    Capacity,
    FleetSize,
    Job,
    Location,
    SearchCompletionResult,
    Service,
    Shipment,
    Skills,
    TerminationCriterion,
    TourActivity,
    TourActivityKind,
    TimeWindow,
    Vehicle,
    VehicleRoute,
    VehicleRoutingProblem,
    VehicleRoutingProblemSolution,
    VehicleType,
)


def make_vehicle_type(
    type_id: str,
    *,
    capacity: int,
    fixed_cost: float = 0.0,
) -> VehicleType:
    # Most samples vary only capacity and fixed cost, so keep vehicle type creation small.
    return VehicleType(
        id=type_id,
        capacity=Capacity.single(capacity),
        fixed_cost=fixed_cost,
    )


def make_vehicle(
    vehicle_id: str,
    vehicle_type: VehicleType,
    *,
    start_x: float = 0.0,
    start_y: float = 0.0,
    end_x: float | None = None,
    end_y: float | None = None,
    latest_end: float = 100.0,
    skills: tuple[str, ...] = (),
) -> Vehicle:
    # Helpers default to a depot at the origin unless a separate end location is needed.
    start_location = Location(id=f"{vehicle_id}-start", x=start_x, y=start_y)
    end_location = None
    if end_x is not None and end_y is not None:
        end_location = Location(id=f"{vehicle_id}-end", x=end_x, y=end_y)
    return Vehicle(
        id=vehicle_id,
        vehicle_type=vehicle_type,
        start_location=start_location,
        end_location=end_location,
        earliest_start=0.0,
        latest_end=latest_end,
        skills=Skills(frozenset(skills)),
    )


def make_service(
    job_id: str,
    *,
    x: float,
    y: float = 0.0,
    demand: int = 1,
    tw_start: float = 0.0,
    tw_end: float = 100.0,
    service_duration: float = 0.0,
    required_skills: tuple[str, ...] = (),
) -> Service:
    # Samples use Service because it is the current runnable job type.
    return Service(
        id=job_id,
        location=Location(id=job_id, x=x, y=y),
        demand=Capacity.single(demand),
        required_skills=Skills(frozenset(required_skills)),
        time_window=TimeWindow(tw_start, tw_end),
        service_duration=service_duration,
    )


def make_shipment(
    job_id: str,
    *,
    pickup_x: float,
    pickup_y: float = 0.0,
    delivery_x: float,
    delivery_y: float = 0.0,
    demand: int = 1,
    tw_start: float = 0.0,
    tw_end: float = 100.0,
    service_duration: float = 0.0,
    required_skills: tuple[str, ...] = (),
) -> Shipment:
    # Shipment reuses one demand/time-window/service profile for both pickup and delivery stops.
    return Shipment(
        id=job_id,
        location=Location(id=f"{job_id}-pickup", x=pickup_x, y=pickup_y),
        delivery_location=Location(
            id=f"{job_id}-delivery",
            x=delivery_x,
            y=delivery_y,
        ),
        demand=Capacity.single(demand),
        required_skills=Skills(frozenset(required_skills)),
        time_window=TimeWindow(tw_start, tw_end),
        service_duration=service_duration,
    )


def print_section(title: str) -> None:
    print(f"== {title} ==")


def fail(stage: str, reason: str | None) -> None:
    print(f"{stage}: FAILED")
    print(f"Reason: {reason or 'unknown failure'}")


def define_problem(
    runtime,
    *,
    vehicle_types: tuple[VehicleType, ...],
    vehicles: tuple[Vehicle, ...],
    jobs: tuple[Job, ...],
    fleet_size: FleetSize = FleetSize.FINITE,
) -> VehicleRoutingProblem | None:
    # All samples walk the public problem_definition adapter in the same order.
    print_section("Problem Definition")
    completeness = runtime.problem_definition.confirm_problem_model_inputs(
        vehicle_types=vehicle_types,
        vehicles=vehicles,
        jobs=jobs,
        fleet_size=fleet_size,
    )
    if not completeness.is_success or completeness.next_state is None:
        fail("Problem Definition", completeness.reason)
        return None
    print("Input check: OK")

    consistency = runtime.problem_definition.validate_problem_model(
        completeness.next_state
    )
    if not consistency.is_success or consistency.next_state is None:
        fail("Problem Definition", consistency.reason)
        return None
    print("Consistency check: OK")

    definition = runtime.problem_definition.define_problem_model(
        consistency.next_state
    )
    if not definition.is_success or definition.problem is None:
        fail("Problem Definition", definition.reason)
        return None
    problem = definition.problem
    print(
        f"Defined problem: vehicles={len(problem.vehicles)} jobs={len(problem.jobs)} "
        f"fleet_size={problem.fleet_size.value}"
    )
    print()
    return problem


def execute_search(
    runtime,
    problem: VehicleRoutingProblem,
    *,
    termination_criterion: TerminationCriterion | None = None,
    initial_solution: VehicleRoutingProblemSolution | None = None,
    title: str = "Search Execution",
) -> SearchCompletionResult | None:
    # Search is always executed through the public algorithm_execution adapter.
    print_section(title)
    acceptance = runtime.algorithm_execution.accept_search_request(
        problem=problem,
        initial_solution=initial_solution,
        termination_criterion=termination_criterion,
    )
    if not acceptance.is_success:
        fail(title, acceptance.reason)
        return None
    normalized_termination = acceptance.termination_criterion or TerminationCriterion()
    print(f"Search accepted: max_iterations={normalized_termination.max_iterations}")

    completion = runtime.algorithm_execution.execute_search(problem=acceptance)
    if not completion.is_success:
        fail(title, completion.reason)
        return None

    returned = runtime.algorithm_execution.return_solution(completion)
    if not returned.is_success or returned.best_solution is None:
        fail(title, returned.reason)
        return None
    print("Search completed: OK")
    print()
    return returned


def print_solution_summary(
    solution: VehicleRoutingProblemSolution,
    *,
    title: str = "Solution Summary",
    show_activities: bool = False,
) -> None:
    # Keep the summary format stable so sample output and smoke tests stay aligned.
    print_section(title)
    print(f"Total cost: {solution.cost:.2f}")
    print(f"Route count: {len(solution.routes)}")
    print(f"Unassigned jobs: {len(solution.unassigned_jobs)}")
    for route in solution.routes:
        _print_route(route, show_activities=show_activities)
    if solution.unassigned_jobs:
        print(
            "Unassigned job ids: "
            + ", ".join(job.id for job in solution.unassigned_jobs)
        )
    else:
        print("Unassigned job ids: none")


def _print_route(route: VehicleRoute, *, show_activities: bool) -> None:
    job_ids = ", ".join(job.id for job in route.jobs) or "-"
    print(
        f"{route.vehicle.id}: jobs=[{job_ids}] cost={route.cost:.2f} "
        f"end_time={route.end_time:.2f}"
    )
    if not show_activities:
        return
    # Activity details are useful only for samples where time behavior matters.
    for activity in route.activities:
        label = _activity_label(activity)
        print(
            "  "
            f"{label}: arrival={activity.arrival_time:.2f} "
            f"start={activity.service_start_time:.2f} "
            f"end={activity.service_end_time:.2f}"
        )


def _activity_label(activity: TourActivity) -> str:
    if activity.activity_kind is TourActivityKind.PICKUP:
        return f"{activity.job.id} pickup"
    if activity.activity_kind is TourActivityKind.DELIVERY:
        return f"{activity.job.id} delivery"
    return activity.job.id
