from __future__ import annotations

from py_sprit import TerminationCriterion, create_runtime

from _benchmark_instances import (
    load_cvrp_instance,
    print_compact_solution_summary,
    print_instance_overview,
)
from _shared import define_problem, execute_search, print_section


def main() -> int:
    runtime = create_runtime(random_seed=7)

    # vrpnc1 is a larger CVRP-style instance with no time windows.
    instance = load_cvrp_instance("vrpnc1.txt")

    print_section("Instance Loading")
    print_instance_overview(instance)
    print()

    problem = define_problem(
        runtime,
        vehicle_types=instance.vehicle_types,
        vehicles=instance.vehicles,
        jobs=instance.jobs,
        fleet_size=instance.fleet_size,
    )
    if problem is None:
        return 1

    result = execute_search(
        runtime,
        problem,
        termination_criterion=TerminationCriterion(max_iterations=5),
    )
    if result is None or result.best_solution is None:
        return 1

    print_section("Solution Summary")
    print_compact_solution_summary(result.best_solution, max_routes=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
