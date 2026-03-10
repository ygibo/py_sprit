from __future__ import annotations

from py_sprit import (
    ConstraintEvaluationContext,
    ConstraintTargetDescriptor,
    TerminationCriterion,
    create_runtime,
)

from _shared import (
    define_problem,
    execute_search,
    fail,
    make_service,
    make_vehicle,
    make_vehicle_type,
    print_section,
    print_solution_summary,
)


class MaxJobsPerRouteConstraint:
    def __init__(self, limit: int) -> None:
        self.limit = limit

    def is_feasible(self, context: ConstraintEvaluationContext) -> bool:
        # This is a hard constraint: once the route exceeds the limit, insertion is rejected.
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
        # This is a soft constraint: keep every activity feasible but make job-2 more expensive.
        return self.penalty_value if context.tour_activity is not None else 0.0


def _register_constraint(
    runtime,
    *,
    constraint: object,
    purpose: str,
    target_descriptor: ConstraintTargetDescriptor,
) -> bool:
    # Samples register constraints through the three public extension_contracts steps.
    compatibility = runtime.extension_contracts.confirm_constraint_compatibility(
        constraint=constraint,
        purpose=purpose,
    )
    if not compatibility.is_success or compatibility.constraint is None:
        fail("Constraint Registration", compatibility.reason)
        return False

    resolution = runtime.extension_contracts.resolve_constraint_target(
        constraint=compatibility.constraint,
        target_descriptor=target_descriptor,
    )
    if not resolution.is_success or resolution.target_descriptor is None:
        fail("Constraint Registration", resolution.reason)
        return False

    registration = runtime.extension_contracts.register_constraint(
        constraint=constraint,
        purpose=purpose,
        target_descriptor=target_descriptor,
    )
    if not registration.is_success or registration.next_state is None:
        fail("Constraint Registration", registration.reason)
        return False

    print(
        f"{purpose}: status={registration.next_state.status.value} "
        f"target={target_descriptor.target_kind}"
    )
    return True


def main() -> int:
    runtime = create_runtime(random_seed=7)

    # Two vehicles and two jobs keep the output compact while still showing both hard and soft effects.
    vehicle_type = make_vehicle_type("constraint-type", capacity=2)
    vehicles = (
        make_vehicle("vehicle-1", vehicle_type, end_x=0.0, end_y=0.0),
        make_vehicle("vehicle-2", vehicle_type, end_x=0.0, end_y=0.0),
    )
    jobs = (
        make_service("job-1", x=1.0),
        make_service("job-2", x=2.0),
    )

    problem = define_problem(
        runtime,
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
    )
    if problem is None:
        return 1

    print_section("Constraint Registration")
    # The hard constraint makes route splitting visible.
    if not _register_constraint(
        runtime,
        constraint=MaxJobsPerRouteConstraint(limit=1),
        purpose="hard route limit",
        target_descriptor=ConstraintTargetDescriptor(target_kind="vehicle_route"),
    ):
        return 1
    if not _register_constraint(
        runtime,
        constraint=TourActivityPenaltyConstraint(penalty_value=5.0),
        purpose="soft activity penalty",
        target_descriptor=ConstraintTargetDescriptor(
            target_kind="tour_activity",
            target_id="job-2",
        ),
    ):
        return 1
    print()

    result = execute_search(
        runtime,
        problem,
        termination_criterion=TerminationCriterion(max_iterations=20),
    )
    if result is None or result.best_solution is None:
        return 1

    # The resulting plan reflects both the hard feasibility rule and the soft penalty.
    print_solution_summary(result.best_solution)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
