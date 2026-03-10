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

    # One vehicle with capacity 1 and two jobs of demand 1 forces one unassigned job.
    vehicle_type = make_vehicle_type("small-type", capacity=1)
    vehicles = (make_vehicle("vehicle-1", vehicle_type, end_x=0.0, end_y=0.0),)
    jobs = (
        make_service("job-1", x=1.0, demand=1),
        make_service("job-2", x=2.0, demand=1),
    )

    problem = define_problem(
        runtime,
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
    )
    if problem is None:
        return 1

    # A small iteration count is enough because the capacity conflict is structural.
    result = execute_search(
        runtime,
        problem,
        termination_criterion=TerminationCriterion(max_iterations=10),
    )
    if result is None or result.best_solution is None:
        return 1

    # This sample is meant to show a feasible route plus an unassigned job.
    print_solution_summary(result.best_solution)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
