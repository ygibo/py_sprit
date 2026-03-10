from __future__ import annotations

from py_sprit import TerminationCriterion, create_runtime

from _shared import (
    define_problem,
    execute_search,
    make_service,
    make_vehicle,
    make_vehicle_type,
    print_solution_summary,
)


def main() -> int:
    runtime = create_runtime(random_seed=7)

    # The heavy job can only fit on the large vehicle, so fleet heterogeneity changes the assignment.
    small_type = make_vehicle_type("small-type", capacity=1, fixed_cost=0.0)
    large_type = make_vehicle_type("large-type", capacity=2, fixed_cost=2.0)
    vehicles = (
        make_vehicle("vehicle-small", small_type, end_x=0.0, end_y=0.0),
        make_vehicle("vehicle-large", large_type, end_x=0.0, end_y=0.0),
    )
    jobs = (
        make_service("job-heavy", x=2.0, demand=2),
        make_service("job-light", x=1.0, demand=1),
    )

    problem = define_problem(
        runtime,
        vehicle_types=(small_type, large_type),
        vehicles=vehicles,
        jobs=jobs,
    )
    if problem is None:
        return 1

    # The search should prefer the only capacity-feasible allocation even with different fixed costs.
    result = execute_search(
        runtime,
        problem,
        termination_criterion=TerminationCriterion(max_iterations=15),
    )
    if result is None or result.best_solution is None:
        return 1

    print_solution_summary(result.best_solution)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
