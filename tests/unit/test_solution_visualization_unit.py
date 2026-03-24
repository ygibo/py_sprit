from __future__ import annotations

from py_sprit.domain.solution_visualization import (
    RouteAnnotationGenerationResult,
    RouteMapGenerationResult,
    VisualizationArtifactGenerationResult,
)
from tests.support import make_problem_inputs, make_solution, make_solution_with_nonfinite_location


def test_visualization_input_accepts_svg_by_default(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=2, job_count=2))
    result = runtime.solution_visualization.confirm_visualization_input(solution=solution)
    assert result.is_success is True
    assert result.next_state is not None


def test_visualization_input_rejects_unsupported_format(runtime):
    solution = make_solution(runtime, **make_problem_inputs())
    result = runtime.solution_visualization.confirm_visualization_input(
        solution=solution,
        format="PNG",  # type: ignore[arg-type]
    )
    assert result.is_success is False


def test_visualization_artifact_generation_fails_with_nonfinite_location(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=1))
    broken_solution = make_solution_with_nonfinite_location(solution)
    result = runtime.solution_visualization.generate_visualization_artifact(
        solution=broken_solution,
    )
    assert result.is_success is False
    assert result.reason == "地図化に必要な座標が不足している"


def test_route_map_target_accepts_all_routes_when_vehicle_id_is_none(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=2, job_count=2))
    result = runtime.solution_visualization.accept_route_map_review_target(solution=solution)
    assert result.is_success is True
    assert result.next_state is not None
    assert result.selected_vehicle_ids == tuple(
        route.vehicle.id for route in solution.routes
    )


def test_route_map_generation_can_target_single_route(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=2, job_count=2))
    result = runtime.solution_visualization.generate_route_map(
        solution=solution,
        vehicle_id="vehicle-1",
    )
    assert result.is_success is True
    assert result.generated_route_map is not None
    assert result.generated_route_map.vehicle_ids == ("vehicle-1",)


def test_route_annotation_entries_follow_activity_order(runtime):
    solution = make_solution(runtime, **make_problem_inputs(vehicle_count=1, job_count=2))
    result = runtime.solution_visualization.generate_route_annotation(
        solution=solution,
        options=None,
    )
    assert result.is_success is True
    assert result.generated_route_annotation is not None
    assert result.generated_route_annotation.entries == tuple(
        f"{route.vehicle.id} stop {activity.position + 1}: {activity.job.id}"
        for route in solution.routes
        for activity in route.activities
    )


def test_route_visualization_labels_shipment_pickup_and_delivery(runtime):
    solution = make_solution(runtime, **make_problem_inputs(job_count=0, include_shipment=True))

    route_map = runtime.solution_visualization.generate_route_map(solution=solution)
    assert route_map.is_success is True
    assert route_map.generated_route_map is not None
    assert "shipment-1 pickup" in route_map.generated_route_map.content
    assert "shipment-1 delivery" in route_map.generated_route_map.content

    annotation = runtime.solution_visualization.generate_route_annotation(solution=solution)
    assert annotation.is_success is True
    assert annotation.generated_route_annotation is not None
    assert annotation.generated_route_annotation.entries == (
        "vehicle-1 stop 1: shipment-1 pickup",
        "vehicle-1 stop 2: shipment-1 delivery",
    )


def test_return_visualization_artifact_fails_without_generated_artifact(runtime):
    result = runtime.solution_visualization.return_visualization_artifact(
        VisualizationArtifactGenerationResult(
            is_success=False,
            next_state=None,
            generated_artifact=None,
            reason="生成済みの VisualizationArtifact が存在しない",
        )
    )
    assert result.is_success is False


def test_return_route_map_fails_without_generated_route_map(runtime):
    result = runtime.solution_visualization.return_route_map(
        RouteMapGenerationResult(
            is_success=False,
            next_state=None,
            generated_route_map=None,
            reason="生成済みの RouteMap が存在しない",
        )
    )
    assert result.is_success is False


def test_return_route_annotation_fails_without_generated_route_annotation(runtime):
    result = runtime.solution_visualization.return_route_annotation(
        RouteAnnotationGenerationResult(
            is_success=False,
            next_state=None,
            generated_route_annotation=None,
            reason="生成済みの RouteAnnotation が存在しない",
        )
    )
    assert result.is_success is False
