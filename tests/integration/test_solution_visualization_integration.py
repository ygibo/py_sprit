from __future__ import annotations

from tests.support import make_problem_inputs, make_solution, make_solution_with_nonfinite_location


def test_runtime_bootstraps_solution_visualization_adapter(runtime):
    assert hasattr(runtime, "solution_visualization")


def test_visualization_artifact_flow_succeeds(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=2, job_count=2))
    confirmation = runtime.solution_visualization.confirm_visualization_input(solution=solution)
    assert confirmation.is_success is True

    generation = runtime.solution_visualization.generate_visualization_artifact(solution=solution)
    assert generation.is_success is True
    assert generation.generated_artifact is not None
    assert generation.generated_artifact.media_type == "image/svg+xml"
    assert "<svg" in generation.generated_artifact.content

    returned = runtime.solution_visualization.return_visualization_artifact(generation)
    assert returned.is_success is True
    assert returned.available_artifact is not None
    assert returned.event is not None


def test_route_map_flow_supports_selected_vehicle(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=2, job_count=2))
    accepted = runtime.solution_visualization.accept_route_map_review_target(
        solution=solution,
        vehicle_id="vehicle-1",
    )
    assert accepted.is_success is True
    assert accepted.selected_vehicle_ids == ("vehicle-1",)

    generation = runtime.solution_visualization.generate_route_map(
        solution=solution,
        vehicle_id="vehicle-1",
    )
    assert generation.is_success is True
    assert generation.generated_route_map is not None
    assert generation.generated_route_map.vehicle_ids == ("vehicle-1",)

    returned = runtime.solution_visualization.return_route_map(generation)
    assert returned.is_success is True
    assert returned.available_route_map is not None
    assert returned.event is not None


def test_route_annotation_flow_supports_annotation_entries(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=2))
    accepted = runtime.solution_visualization.accept_route_annotation_review_target(
        solution=solution,
    )
    assert accepted.is_success is True

    generation = runtime.solution_visualization.generate_route_annotation(solution=solution)
    assert generation.is_success is True
    assert generation.generated_route_annotation is not None
    assert generation.generated_route_annotation.entries

    returned = runtime.solution_visualization.return_route_annotation(generation)
    assert returned.is_success is True
    assert returned.available_route_annotation is not None
    assert returned.event is not None


def test_solution_visualization_flow_supports_shipment_stops(runtime):
    solution = make_solution(runtime, **make_problem_inputs(job_count=0, include_shipment=True))

    route_map = runtime.solution_visualization.generate_route_map(solution=solution)
    assert route_map.is_success is True
    assert route_map.generated_route_map is not None
    assert "shipment-1 pickup" in route_map.generated_route_map.content
    assert "shipment-1 delivery" in route_map.generated_route_map.content

    route_annotation = runtime.solution_visualization.generate_route_annotation(
        solution=solution
    )
    assert route_annotation.is_success is True
    assert route_annotation.generated_route_annotation is not None
    assert route_annotation.generated_route_annotation.entries == (
        "vehicle-1 stop 1: shipment-1 pickup",
        "vehicle-1 stop 2: shipment-1 delivery",
    )


def test_generation_failure_propagates_to_return_services(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    broken_solution = make_solution_with_nonfinite_location(solution)
    generation = runtime.solution_visualization.generate_visualization_artifact(
        solution=broken_solution,
    )
    assert generation.is_success is False

    returned = runtime.solution_visualization.return_visualization_artifact(generation)
    assert returned.is_success is False
    assert returned.reason == "地図化に必要な座標が不足している"
