from __future__ import annotations

from py_sprit import FleetSize, create_runtime

from _shared import (
    define_problem,
    execute_search,
    make_service,
    make_shipment,
    make_vehicle,
    make_vehicle_type,
    print_solution_summary,
)


def main() -> int:
    runtime = create_runtime(random_seed=11)

    vehicle_type = make_vehicle_type("vehicle-type-1", capacity=3)
    vehicles = (
        make_vehicle("vehicle-1", vehicle_type, end_x=0.0, end_y=0.0),
        make_vehicle("vehicle-2", vehicle_type, end_x=0.0, end_y=0.0),
    )
    jobs = (
        make_service("service-1", x=1.0, y=0.0, demand=1),
        make_shipment(
            "shipment-1",
            pickup_x=3.0,
            pickup_y=1.0,
            delivery_x=6.0,
            delivery_y=1.0,
            demand=1,
        ),
    )

    problem = define_problem(
        runtime,
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
        fleet_size=FleetSize.FINITE,
    )
    if problem is None:
        return 1

    result = execute_search(runtime, problem, title="Search Execution")
    if result is None or result.best_solution is None:
        return 1

    print_solution_summary(
        result.best_solution,
        show_activities=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
