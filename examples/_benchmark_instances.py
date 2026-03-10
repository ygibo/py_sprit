from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from py_sprit import (
    Capacity,
    FleetSize,
    Location,
    Service,
    TimeWindow,
    Vehicle,
    VehicleRoutingProblemSolution,
    VehicleType,
)


RESOURCE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "jsprit"
    / "jsprit-core"
    / "src"
    / "test"
    / "resources"
    / "com"
    / "graphhopper"
    / "jsprit"
    / "core"
    / "algorithm"
)


@dataclass(frozen=True, slots=True)
class BenchmarkInstance:
    name: str
    source_path: Path
    vehicle_types: tuple[VehicleType, ...]
    vehicles: tuple[Vehicle, ...]
    jobs: tuple[Service, ...]
    fleet_size: FleetSize = FleetSize.FINITE


def load_solomon_instance(
    filename: str,
    *,
    vehicle_count_override: int | None = None,
) -> BenchmarkInstance:
    path = RESOURCE_ROOT / filename
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    name = lines[0]

    vehicle_header = lines.index("VEHICLE")
    vehicle_tokens = lines[vehicle_header + 2].split()
    vehicle_count = int(vehicle_tokens[0]) if vehicle_count_override is None else vehicle_count_override
    capacity = int(vehicle_tokens[1])

    customer_header = lines.index("CUSTOMER")
    customer_rows = [row.split() for row in lines[customer_header + 2 :] if row.split()]

    depot = customer_rows[0]
    depot_location = Location(id="depot", x=float(depot[1]), y=float(depot[2]))
    depot_ready = float(depot[4])
    depot_due = float(depot[5])

    vehicle_type = VehicleType(id=f"{name.lower()}-vehicle-type", capacity=Capacity.single(capacity))
    vehicles = tuple(
        Vehicle(
            id=f"vehicle-{index + 1}",
            vehicle_type=vehicle_type,
            start_location=depot_location,
            end_location=depot_location,
            earliest_start=depot_ready,
            latest_end=depot_due,
        )
        for index in range(vehicle_count)
    )
    jobs = tuple(
        Service(
            id=f"customer-{row[0]}",
            location=Location(id=f"customer-{row[0]}", x=float(row[1]), y=float(row[2])),
            demand=Capacity.single(int(float(row[3]))),
            time_window=TimeWindow(float(row[4]), float(row[5])),
            service_duration=float(row[6]),
        )
        for row in customer_rows[1:]
    )
    return BenchmarkInstance(
        name=f"Solomon {name}",
        source_path=path,
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
    )


def load_cvrp_instance(
    filename: str,
    *,
    vehicle_count_override: int | None = None,
) -> BenchmarkInstance:
    path = RESOURCE_ROOT / filename
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    header = lines[0].split()
    capacity = int(header[1])

    depot_tokens = lines[1].split()
    depot_location = Location(id="depot", x=float(depot_tokens[0]), y=float(depot_tokens[1]))

    customers = [line.split() for line in lines[2:]]
    total_demand = sum(int(float(row[2])) for row in customers)
    vehicle_count = (
        vehicle_count_override
        if vehicle_count_override is not None
        else max(1, math.ceil(total_demand / capacity) + 1)
    )

    vehicle_type = VehicleType(id=f"{filename.lower()}-vehicle-type", capacity=Capacity.single(capacity))
    vehicles = tuple(
        Vehicle(
            id=f"vehicle-{index + 1}",
            vehicle_type=vehicle_type,
            start_location=depot_location,
            end_location=depot_location,
            earliest_start=0.0,
            latest_end=999999.0,
        )
        for index in range(vehicle_count)
    )
    jobs = tuple(
        Service(
            id=f"customer-{index + 1}",
            location=Location(id=f"customer-{index + 1}", x=float(row[0]), y=float(row[1])),
            demand=Capacity.single(int(float(row[2]))),
            time_window=TimeWindow(0.0, 999999.0),
            service_duration=0.0,
        )
        for index, row in enumerate(customers)
    )
    return BenchmarkInstance(
        name=f"CVRP {filename}",
        source_path=path,
        vehicle_types=(vehicle_type,),
        vehicles=vehicles,
        jobs=jobs,
    )


def print_instance_overview(instance: BenchmarkInstance) -> None:
    print(f"Instance: {instance.name}")
    print(f"Source: {instance.source_path.relative_to(Path(__file__).resolve().parents[1])}")
    print(f"Vehicles: {len(instance.vehicles)}")
    print(f"Jobs: {len(instance.jobs)}")


def print_compact_solution_summary(
    solution: VehicleRoutingProblemSolution,
    *,
    max_routes: int = 5,
) -> None:
    print(f"Total cost: {solution.cost:.2f}")
    print(f"Route count: {len(solution.routes)}")
    print(f"Unassigned jobs: {len(solution.unassigned_jobs)}")
    displayed_routes = solution.routes[:max_routes]
    print(f"Displayed routes: {len(displayed_routes)}")
    for route in displayed_routes:
        preview = ", ".join(job.id for job in route.jobs[:5])
        suffix = ""
        if len(route.jobs) > 5:
            suffix = f", ... +{len(route.jobs) - 5} more"
        print(
            f"{route.vehicle.id}: jobs=[{preview}{suffix}] "
            f"count={len(route.jobs)} cost={route.cost:.2f}"
        )
