from __future__ import annotations

from py_sprit import (
    Capacity,
    ConstraintEvaluationContext,
    ConstraintTargetDescriptor,
    FleetSize,
    Location,
    Service,
    TerminationCriterion,
    TimeWindow,
    Vehicle,
    VehicleType,
    create_runtime,
)


class MaxJobsPerRouteConstraint:
    # Keep at most one job on each route so the sample visibly uses both vehicles.
    def __init__(self, limit: int) -> None:
        self.limit = limit

    def is_feasible(self, context: ConstraintEvaluationContext) -> bool:
        route = context.vehicle_route
        if route is None:
            return True
        return len(route.jobs) <= self.limit

    def penalty(self, context: ConstraintEvaluationContext) -> float:
        return 0.0


def _make_vehicle_type() -> VehicleType:
    # One shared vehicle type keeps the sample focused on the runtime flow, not fleet modeling.
    return VehicleType(id="vehicle-type-1", capacity=Capacity.single(2))


def _make_vehicle(vehicle_id: str, vehicle_type: VehicleType) -> Vehicle:
    # Both vehicles start and end at the same depot so route output stays easy to compare.
    depot = Location(id="depot", x=0.0, y=0.0)
    return Vehicle(
        id=vehicle_id,
        vehicle_type=vehicle_type,
        start_location=depot,
        end_location=depot,
        earliest_start=0.0,
        latest_end=100.0,
    )


def _make_service(job_id: str, x: float) -> Service:
    # Service is the current runnable job type in the executable subset.
    return Service(
        id=job_id,
        location=Location(id=job_id, x=x, y=0.0),
        demand=Capacity.single(1),
        time_window=TimeWindow(0.0, 100.0),
        service_duration=0.0,
    )


def _print_section(title: str) -> None:
    print(f"== {title} ==")


def _fail(stage: str, reason: str | None) -> int:
    print(f"{stage}: FAILED")
    print(f"Reason: {reason or 'unknown failure'}")
    return 1


def main() -> int:
    runtime = create_runtime(random_seed=7)

    # Prepare a minimal problem that still exercises all three contexts.
    vehicle_type = _make_vehicle_type()
    vehicles = (
        _make_vehicle("vehicle-1", vehicle_type),
        _make_vehicle("vehicle-2", vehicle_type),
    )
    jobs = (
        _make_service("job-1", 1.0),
        _make_service("job-2", 2.0),
    )

    # 1. Define a searchable VehicleRoutingProblem.
    _print_section("Problem Definition")
    completeness = runtime.problem_definition.confirm_problem_model_inputs(
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
        fleet_size=FleetSize.FINITE,
    )
    if not completeness.is_success or completeness.next_state is None:
        return _fail("Problem Definition", completeness.reason)
    print("Input check: OK")

    consistency = runtime.problem_definition.validate_problem_model(
        completeness.next_state
    )
    if not consistency.is_success or consistency.next_state is None:
        return _fail("Problem Definition", consistency.reason)
    print("Consistency check: OK")

    definition = runtime.problem_definition.define_problem_model(
        consistency.next_state
    )
    if not definition.is_success or definition.problem is None:
        return _fail("Problem Definition", definition.reason)
    problem = definition.problem
    print(
        f"Defined problem: vehicles={len(problem.vehicles)} jobs={len(problem.jobs)} "
        f"fleet_size={problem.fleet_size.value}"
    )
    print()

    # 2. Register a constraint that will affect the next search execution.
    _print_section("Constraint Registration")
    constraint = MaxJobsPerRouteConstraint(limit=1)
    # Route-level targeting makes the effect easy to observe in the final solution.
    target_descriptor = ConstraintTargetDescriptor(target_kind="vehicle_route")
    compatibility = runtime.extension_contracts.confirm_constraint_compatibility(
        constraint=constraint,
        purpose="one job per route",
    )
    if not compatibility.is_success or compatibility.constraint is None:
        return _fail("Constraint Registration", compatibility.reason)
    print("Compatibility check: OK")

    resolution = runtime.extension_contracts.resolve_constraint_target(
        constraint=compatibility.constraint,
        target_descriptor=target_descriptor,
    )
    if not resolution.is_success or resolution.target_descriptor is None:
        return _fail("Constraint Registration", resolution.reason)
    print(
        f"Target resolution: OK ({resolution.target_descriptor.target_kind})"
    )

    registration = runtime.extension_contracts.register_constraint(
        constraint=constraint,
        purpose="one job per route",
        target_descriptor=target_descriptor,
    )
    if not registration.is_success or registration.next_state is None:
        return _fail("Constraint Registration", registration.reason)
    print(f"Registration status: {registration.next_state.status.value}")
    print()

    # 3. Accept and execute the search with the registered constraint in effect.
    _print_section("Search Execution")
    # A short run is enough because the sample is tiny and deterministic under a fixed seed.
    termination = TerminationCriterion(max_iterations=25)
    acceptance = runtime.algorithm_execution.accept_search_request(
        problem=problem,
        termination_criterion=termination,
    )
    if not acceptance.is_success:
        return _fail("Search Execution", acceptance.reason)
    print(
        "Search accepted: "
        f"max_iterations={acceptance.termination_criterion.max_iterations}"
    )

    completion = runtime.algorithm_execution.execute_search(problem=acceptance)
    if not completion.is_success:
        return _fail("Search Execution", completion.reason)
    returned = runtime.algorithm_execution.return_solution(completion)
    if not returned.is_success or returned.best_solution is None:
        return _fail("Search Execution", returned.reason)
    print("Search completed: OK")
    print()

    # 4. Print the final solution in a human-readable form.
    solution = returned.best_solution
    _print_section("Solution Summary")
    print(f"Total cost: {solution.cost:.2f}")
    print(f"Route count: {len(solution.routes)}")
    print(f"Unassigned jobs: {len(solution.unassigned_jobs)}")
    for route in solution.routes:
        job_ids = ", ".join(job.id for job in route.jobs) or "-"
        print(
            f"{route.vehicle.id}: jobs=[{job_ids}] cost={route.cost:.2f} "
            f"end_time={route.end_time:.2f}"
        )
    if solution.unassigned_jobs:
        print(
            "Unassigned job ids: "
            + ", ".join(job.id for job in solution.unassigned_jobs)
        )
    else:
        print("Unassigned job ids: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
