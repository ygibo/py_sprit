from __future__ import annotations

from random import Random

from py_sprit import TerminationCriterion, create_runtime
from py_sprit.domain.algorithm_execution import (
    BestInsertion,
    BestSolutionSelectionService,
    RandomRuin,
    SearchStrategy,
    VehicleRoutingAlgorithm,
    build_greedy_initial_solution,
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


def main() -> int:
    runtime = create_runtime(random_seed=7)

    # This sample compares the standard runtime path with a lower-level custom strategy path.
    vehicle_type = make_vehicle_type("algorithm-type", capacity=2)
    vehicles = (
        make_vehicle("vehicle-1", vehicle_type, end_x=0.0, end_y=0.0),
        make_vehicle("vehicle-2", vehicle_type, end_x=0.0, end_y=0.0),
    )
    jobs = (
        make_service("job-1", x=1.0),
        make_service("job-2", x=2.0),
        make_service("job-3", x=3.0),
    )

    problem = define_problem(
        runtime,
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
    )
    if problem is None:
        return 1

    # First run the default adapter-based execution so there is a baseline to compare against.
    default_result = execute_search(
        runtime,
        problem,
        termination_criterion=TerminationCriterion(max_iterations=5),
        title="Default Search",
    )
    if default_result is None or default_result.best_solution is None:
        return 1
    print_solution_summary(
        default_result.best_solution,
        title="Default Solution Summary",
    )
    print()

    print_section("Algorithm Customization")
    print("This sample uses lower-level internal strategy objects directly.")
    # Then build a custom strategy from lower-level solver objects exported by the package.
    strategy = SearchStrategy(
        ruin=RandomRuin(rng=Random(13), share=0.5),
        insertion=BestInsertion(),
    )
    algorithm = VehicleRoutingAlgorithm(strategy=strategy)
    # The lower-level path requires constructing the initial solution explicitly.
    initial_solution = build_greedy_initial_solution(problem, tuple())
    candidates = algorithm.solve(
        problem=problem,
        initial_solution=initial_solution,
        termination_criterion=TerminationCriterion(max_iterations=25),
        registrations=tuple(),
    )
    best_solution = BestSolutionSelectionService().select(candidates)
    if best_solution is None:
        fail("Algorithm Customization", "customized strategy did not return a best solution")
        return 1
    # The printed parameters make it obvious what changed relative to the default run.
    print("Customized strategy: ruin_share=0.5 max_iterations=25 seed=13")
    print()
    print_solution_summary(best_solution, title="Customized Solution Summary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
