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

    # The second job opens later, so activity timestamps make waiting behavior visible.
    vehicle_type = make_vehicle_type("time-window-type", capacity=2)
    vehicles = (make_vehicle("vehicle-1", vehicle_type, end_x=0.0, end_y=0.0),)
    jobs = (
        make_service("job-early", x=1.0, tw_start=0.0, tw_end=5.0),
        make_service("job-late", x=4.0, tw_start=10.0, tw_end=20.0),
    )

    problem = define_problem(
        runtime,
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
    )
    if problem is None:
        return 1

    # show_activities=True exposes arrival, service start, and service end times.
    result = execute_search(
        runtime,
        problem,
        termination_criterion=TerminationCriterion(max_iterations=15),
    )
    if result is None or result.best_solution is None:
        return 1

    print_solution_summary(result.best_solution, show_activities=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
