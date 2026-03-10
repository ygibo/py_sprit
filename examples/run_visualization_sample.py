from __future__ import annotations

from pathlib import Path

from py_sprit import TerminationCriterion
from py_sprit import TerminationCriterion, VisualizationOptions, create_runtime

from _shared import (
    define_problem,
    execute_search,
    make_service,
    make_vehicle,
    make_vehicle_type,
    print_section,
    print_solution_summary,
)
from _benchmark_instances import load_solomon_instance


ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "artifacts" / "visualization"


def _write_svg(name: str, content: str) -> Path:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / name
    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    runtime = create_runtime(random_seed=7)

    instance = load_solomon_instance("C101.txt")

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
        termination_criterion=TerminationCriterion(max_iterations=100),
        title="Search Execution"
    )
    if result is None or result.best_solution is None:
        return 1
    solution = result.best_solution
    print_solution_summary(solution)
    print()

    print_section("Solution Visualization")
    options = VisualizationOptions(show_timestamps=True)

    artifact_generation = runtime.solution_visualization.generate_visualization_artifact(
        solution=solution,
        options=options,
    )
    artifact_result = runtime.solution_visualization.return_visualization_artifact(
        artifact_generation
    )
    if not artifact_result.is_success or artifact_result.available_artifact is None:
        print(f"VisualizationArtifact: FAILED ({artifact_result.reason})")
        return 1
    artifact_path = _write_svg(
        "visualization_artifact.svg",
        artifact_result.available_artifact.content,
    )
    print(
        "VisualizationArtifact: "
        f"{artifact_path} ({artifact_result.available_artifact.media_type})"
    )

    route_map_generation = runtime.solution_visualization.generate_route_map(
        solution=solution,
        vehicle_id="vehicle-1",
    )
    route_map_result = runtime.solution_visualization.return_route_map(
        route_map_generation
    )
    if not route_map_result.is_success or route_map_result.available_route_map is None:
        print(f"RouteMap: FAILED ({route_map_result.reason})")
        return 1
    route_map_path = _write_svg(
        "route_map_vehicle_1.svg",
        route_map_result.available_route_map.content,
    )
    print(f"RouteMap: {route_map_path} ({route_map_result.available_route_map.media_type})")

    annotation_generation = runtime.solution_visualization.generate_route_annotation(
        solution=solution,
        vehicle_id="vehicle-1",
        options=options,
    )
    annotation_result = runtime.solution_visualization.return_route_annotation(
        annotation_generation
    )
    if (
        not annotation_result.is_success
        or annotation_result.available_route_annotation is None
    ):
        print(f"RouteAnnotation: FAILED ({annotation_result.reason})")
        return 1
    annotation_path = _write_svg(
        "route_annotation_vehicle_1.svg",
        annotation_result.available_route_annotation.content,
    )
    print(
        "RouteAnnotation: "
        f"{annotation_path} ({annotation_result.available_route_annotation.media_type})"
    )
    print("Annotation entries:")
    for entry in annotation_result.available_route_annotation.entries:
        print(f"  - {entry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
