from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from html import escape
from math import isfinite

from py_sprit.domain.algorithm_execution import (
    TourActivity,
    VehicleRoute,
    VehicleRoutingProblemSolution,
)
from py_sprit.domain.shared import Location


class VisualizationFormat(str, Enum):
    SVG = "SVG"


@dataclass(frozen=True, slots=True)
class VisualizationOptions:
    width: int = 960
    height: int = 640
    padding: int = 32
    show_labels: bool = True
    show_timestamps: bool = False

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("visualization width and height must be positive")
        if self.padding < 0:
            raise ValueError("visualization padding must be non-negative")


@dataclass(frozen=True, slots=True)
class VisualizationArtifact:
    format: VisualizationFormat
    content: str
    media_type: str = "image/svg+xml"


@dataclass(frozen=True, slots=True)
class RouteMap:
    format: VisualizationFormat
    content: str
    vehicle_ids: tuple[str, ...]
    media_type: str = "image/svg+xml"


@dataclass(frozen=True, slots=True)
class RouteAnnotation:
    format: VisualizationFormat
    content: str
    entries: tuple[str, ...]
    vehicle_ids: tuple[str, ...]
    media_type: str = "image/svg+xml"


class VisualizationArtifactRequestStatus(str, Enum):
    INPUT_CONFIRMED = "InputConfirmed"
    ARTIFACT_GENERATED = "ArtifactGenerated"
    ARTIFACT_AVAILABLE = "ArtifactAvailable"


class RouteMapReviewStatus(str, Enum):
    TARGET_ACCEPTED = "TargetAccepted"
    ROUTE_MAP_GENERATED = "RouteMapGenerated"
    ROUTE_MAP_AVAILABLE = "RouteMapAvailable"


class RouteAnnotationReviewStatus(str, Enum):
    TARGET_ACCEPTED = "TargetAccepted"
    ROUTE_ANNOTATION_GENERATED = "RouteAnnotationGenerated"
    ROUTE_ANNOTATION_AVAILABLE = "RouteAnnotationAvailable"


@dataclass(frozen=True, slots=True)
class VisualizationArtifactAvailableEvent:
    name: str = "VisualizationArtifactAvailableEvent"


@dataclass(frozen=True, slots=True)
class RouteMapAvailableEvent:
    name: str = "RouteMapAvailableEvent"


@dataclass(frozen=True, slots=True)
class RouteAnnotationAvailableEvent:
    name: str = "RouteAnnotationAvailableEvent"


@dataclass(frozen=True, slots=True)
class VisualizationInputConfirmationResult:
    is_success: bool
    next_state: VisualizationArtifactRequest | None
    solution: VehicleRoutingProblemSolution | None
    format: VisualizationFormat | None
    options: VisualizationOptions | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class VisualizationArtifactGenerationResult:
    is_success: bool
    next_state: VisualizationArtifactRequest | None
    generated_artifact: VisualizationArtifact | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class VisualizationArtifactAvailabilityResult:
    is_success: bool
    next_state: VisualizationArtifactRequest | None
    available_artifact: VisualizationArtifact | None
    event: VisualizationArtifactAvailableEvent | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class RouteMapReviewTargetAcceptanceResult:
    is_success: bool
    next_state: RouteMapReview | None
    selected_vehicle_ids: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class RouteMapGenerationResult:
    is_success: bool
    next_state: RouteMapReview | None
    generated_route_map: RouteMap | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class RouteMapAvailabilityResult:
    is_success: bool
    next_state: RouteMapReview | None
    available_route_map: RouteMap | None
    event: RouteMapAvailableEvent | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class RouteAnnotationReviewTargetAcceptanceResult:
    is_success: bool
    next_state: RouteAnnotationReview | None
    selected_vehicle_ids: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class RouteAnnotationGenerationResult:
    is_success: bool
    next_state: RouteAnnotationReview | None
    generated_route_annotation: RouteAnnotation | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class RouteAnnotationAvailabilityResult:
    is_success: bool
    next_state: RouteAnnotationReview | None
    available_route_annotation: RouteAnnotation | None
    event: RouteAnnotationAvailableEvent | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class VisualizationArtifactRequest:
    solution: VehicleRoutingProblemSolution
    format: VisualizationFormat
    options: VisualizationOptions
    artifact: VisualizationArtifact | None = None
    status: VisualizationArtifactRequestStatus = (
        VisualizationArtifactRequestStatus.INPUT_CONFIRMED
    )

    @classmethod
    def confirmInput(
        cls,
        solution: VehicleRoutingProblemSolution,
        format: VisualizationFormat,
        options: VisualizationOptions,
    ) -> VisualizationInputConfirmationResult:
        request = cls(solution=solution, format=format, options=options)
        return VisualizationInputConfirmationResult(
            is_success=True,
            next_state=request,
            solution=solution,
            format=format,
            options=options,
        )

    def generateArtifact(
        self,
        artifact: VisualizationArtifact,
    ) -> VisualizationArtifactGenerationResult:
        generated = replace(
            self,
            artifact=artifact,
            status=VisualizationArtifactRequestStatus.ARTIFACT_GENERATED,
        )
        return VisualizationArtifactGenerationResult(
            is_success=True,
            next_state=generated,
            generated_artifact=artifact,
        )

    def makeArtifactAvailable(self) -> VisualizationArtifactAvailabilityResult:
        if self.artifact is None:
            return VisualizationArtifactAvailabilityResult(
                is_success=False,
                next_state=None,
                available_artifact=None,
                reason="生成済みの VisualizationArtifact が存在しない",
            )
        available = replace(
            self,
            status=VisualizationArtifactRequestStatus.ARTIFACT_AVAILABLE,
        )
        return VisualizationArtifactAvailabilityResult(
            is_success=True,
            next_state=available,
            available_artifact=self.artifact,
            event=VisualizationArtifactAvailableEvent(),
        )


@dataclass(frozen=True, slots=True)
class RouteMapReview:
    solution: VehicleRoutingProblemSolution
    vehicle_ids: tuple[str, ...]
    route_map: RouteMap | None = None
    status: RouteMapReviewStatus = RouteMapReviewStatus.TARGET_ACCEPTED

    @classmethod
    def acceptTarget(
        cls,
        solution: VehicleRoutingProblemSolution,
        vehicle_ids: tuple[str, ...],
    ) -> RouteMapReviewTargetAcceptanceResult:
        review = cls(solution=solution, vehicle_ids=vehicle_ids)
        return RouteMapReviewTargetAcceptanceResult(
            is_success=True,
            next_state=review,
            selected_vehicle_ids=vehicle_ids,
        )

    def generateRouteMap(self, route_map: RouteMap) -> RouteMapGenerationResult:
        generated = replace(
            self,
            route_map=route_map,
            status=RouteMapReviewStatus.ROUTE_MAP_GENERATED,
        )
        return RouteMapGenerationResult(
            is_success=True,
            next_state=generated,
            generated_route_map=route_map,
        )

    def makeRouteMapAvailable(self) -> RouteMapAvailabilityResult:
        if self.route_map is None:
            return RouteMapAvailabilityResult(
                is_success=False,
                next_state=None,
                available_route_map=None,
                reason="生成済みの RouteMap が存在しない",
            )
        available = replace(self, status=RouteMapReviewStatus.ROUTE_MAP_AVAILABLE)
        return RouteMapAvailabilityResult(
            is_success=True,
            next_state=available,
            available_route_map=self.route_map,
            event=RouteMapAvailableEvent(),
        )


@dataclass(frozen=True, slots=True)
class RouteAnnotationReview:
    solution: VehicleRoutingProblemSolution
    vehicle_ids: tuple[str, ...]
    options: VisualizationOptions | None = None
    route_annotation: RouteAnnotation | None = None
    status: RouteAnnotationReviewStatus = RouteAnnotationReviewStatus.TARGET_ACCEPTED

    @classmethod
    def acceptTarget(
        cls,
        solution: VehicleRoutingProblemSolution,
        vehicle_ids: tuple[str, ...],
        options: VisualizationOptions | None = None,
    ) -> RouteAnnotationReviewTargetAcceptanceResult:
        review = cls(solution=solution, vehicle_ids=vehicle_ids, options=options)
        return RouteAnnotationReviewTargetAcceptanceResult(
            is_success=True,
            next_state=review,
            selected_vehicle_ids=vehicle_ids,
        )

    def generateRouteAnnotation(
        self,
        route_annotation: RouteAnnotation,
    ) -> RouteAnnotationGenerationResult:
        generated = replace(
            self,
            route_annotation=route_annotation,
            status=RouteAnnotationReviewStatus.ROUTE_ANNOTATION_GENERATED,
        )
        return RouteAnnotationGenerationResult(
            is_success=True,
            next_state=generated,
            generated_route_annotation=route_annotation,
        )

    def makeRouteAnnotationAvailable(self) -> RouteAnnotationAvailabilityResult:
        if self.route_annotation is None:
            return RouteAnnotationAvailabilityResult(
                is_success=False,
                next_state=None,
                available_route_annotation=None,
                reason="生成済みの RouteAnnotation が存在しない",
            )
        available = replace(
            self,
            status=RouteAnnotationReviewStatus.ROUTE_ANNOTATION_AVAILABLE,
        )
        return RouteAnnotationAvailabilityResult(
            is_success=True,
            next_state=available,
            available_route_annotation=self.route_annotation,
            event=RouteAnnotationAvailableEvent(),
        )


@dataclass(frozen=True, slots=True)
class VisualizationInputPolicy:
    def evaluate(
        self,
        solution: VehicleRoutingProblemSolution | None,
        format: VisualizationFormat,
        options: VisualizationOptions | None,
    ) -> VisualizationInputConfirmationResult:
        normalized_options = options or VisualizationOptions()
        if solution is None:
            return VisualizationInputConfirmationResult(
                is_success=False,
                next_state=None,
                solution=None,
                format=format,
                options=normalized_options,
                reason="VehicleRoutingProblemSolution を参照できない",
            )
        if format != VisualizationFormat.SVG:
            return VisualizationInputConfirmationResult(
                is_success=False,
                next_state=None,
                solution=solution,
                format=format,
                options=normalized_options,
                reason="VisualizationFormat として SVG のみ対応している",
            )
        return VisualizationArtifactRequest.confirmInput(
            solution=solution,
            format=VisualizationFormat.SVG,
            options=normalized_options,
        )


@dataclass(frozen=True, slots=True)
class VisualizationArtifactGenerationService:
    def generate(
        self,
        request: VisualizationArtifactRequest,
    ) -> VisualizationArtifactGenerationResult:
        if not _has_finite_locations(request.solution.routes):
            return VisualizationArtifactGenerationResult(
                is_success=False,
                next_state=None,
                generated_artifact=None,
                reason="地図化に必要な座標が不足している",
            )
        artifact = VisualizationArtifact(
            format=request.format,
            content=_render_solution_svg(routes=request.solution.routes, options=request.options),
        )
        return request.generateArtifact(artifact)


@dataclass(frozen=True, slots=True)
class VisualizationArtifactAssemblyPolicy:
    def makeAvailable(
        self,
        request: VisualizationArtifactRequest,
    ) -> VisualizationArtifactAvailabilityResult:
        return request.makeArtifactAvailable()


@dataclass(frozen=True, slots=True)
class RouteMapTargetPolicy:
    def accept(
        self,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
    ) -> RouteMapReviewTargetAcceptanceResult:
        if solution is None:
            return RouteMapReviewTargetAcceptanceResult(
                is_success=False,
                next_state=None,
                reason="確認対象の経路が存在しない",
            )
        vehicle_ids = _selected_vehicle_ids(solution.routes, vehicle_id)
        if not vehicle_ids:
            return RouteMapReviewTargetAcceptanceResult(
                is_success=False,
                next_state=None,
                reason="確認対象の経路が存在しない",
            )
        return RouteMapReview.acceptTarget(solution, vehicle_ids)


@dataclass(frozen=True, slots=True)
class CoordinateAvailabilityPolicy:
    def is_available(self, routes: tuple[VehicleRoute, ...]) -> bool:
        return _has_finite_locations(routes)


@dataclass(frozen=True, slots=True)
class RouteMapGenerationService:
    coordinate_policy: CoordinateAvailabilityPolicy

    def generate(
        self,
        review: RouteMapReview,
        options: VisualizationOptions | None = None,
    ) -> RouteMapGenerationResult:
        normalized_options = options or VisualizationOptions()
        routes = _select_routes(review.solution.routes, review.vehicle_ids)
        if not self.coordinate_policy.is_available(routes):
            return RouteMapGenerationResult(
                is_success=False,
                next_state=None,
                generated_route_map=None,
                reason="Location.x / y が不足している",
            )
        route_map = RouteMap(
            format=VisualizationFormat.SVG,
            content=_render_solution_svg(routes=routes, options=normalized_options),
            vehicle_ids=review.vehicle_ids,
        )
        return review.generateRouteMap(route_map)


@dataclass(frozen=True, slots=True)
class RouteAnnotationTargetPolicy:
    def accept(
        self,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
        options: VisualizationOptions | None = None,
    ) -> RouteAnnotationReviewTargetAcceptanceResult:
        if solution is None:
            return RouteAnnotationReviewTargetAcceptanceResult(
                is_success=False,
                next_state=None,
                reason="注記対象の TourActivity が存在しない",
            )
        vehicle_ids = _selected_vehicle_ids(solution.routes, vehicle_id)
        if not vehicle_ids:
            return RouteAnnotationReviewTargetAcceptanceResult(
                is_success=False,
                next_state=None,
                reason="注記対象の TourActivity が存在しない",
            )
        routes = _select_routes(solution.routes, vehicle_ids)
        if not any(route.activities for route in routes):
            return RouteAnnotationReviewTargetAcceptanceResult(
                is_success=False,
                next_state=None,
                reason="注記対象の TourActivity が存在しない",
            )
        return RouteAnnotationReview.acceptTarget(solution, vehicle_ids, options=options)


@dataclass(frozen=True, slots=True)
class RouteAnnotationOptionPolicy:
    def normalize(self, options: VisualizationOptions | None) -> VisualizationOptions:
        return options or VisualizationOptions()


@dataclass(frozen=True, slots=True)
class RouteAnnotationGenerationService:
    option_policy: RouteAnnotationOptionPolicy

    def generate(
        self,
        review: RouteAnnotationReview,
        options: VisualizationOptions | None = None,
    ) -> RouteAnnotationGenerationResult:
        normalized_options = self.option_policy.normalize(options or review.options)
        routes = _select_routes(review.solution.routes, review.vehicle_ids)
        entries = _build_route_annotation_entries(
            routes=routes,
            show_timestamps=normalized_options.show_timestamps,
        )
        if not entries:
            return RouteAnnotationGenerationResult(
                is_success=False,
                next_state=None,
                generated_route_annotation=None,
                reason="注記に必要な経路情報が揃っていない",
            )
        route_annotation = RouteAnnotation(
            format=VisualizationFormat.SVG,
            content=_render_annotation_svg(entries, normalized_options),
            entries=entries,
            vehicle_ids=review.vehicle_ids,
        )
        return review.generateRouteAnnotation(route_annotation)


@dataclass(slots=True)
class AlgorithmExecutionGateway:
    gateway: object

    def resolveSolution(
        self,
        solution: VehicleRoutingProblemSolution | None,
    ) -> VehicleRoutingProblemSolution | None:
        return self.gateway.resolve_solution(solution)

    def resolveRoutes(
        self,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
    ) -> tuple[VehicleRoute, ...]:
        return self.gateway.resolve_routes(solution, vehicle_id)

    def resolveActivities(
        self,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
    ) -> tuple[TourActivity, ...]:
        return self.gateway.resolve_activities(solution, vehicle_id)


def _selected_vehicle_ids(
    routes: tuple[VehicleRoute, ...],
    vehicle_id: str | None,
) -> tuple[str, ...]:
    if vehicle_id is None:
        return tuple(route.vehicle.id for route in routes)
    return tuple(route.vehicle.id for route in routes if route.vehicle.id == vehicle_id)


def _select_routes(
    routes: tuple[VehicleRoute, ...],
    vehicle_ids: tuple[str, ...],
) -> tuple[VehicleRoute, ...]:
    allowed = set(vehicle_ids)
    return tuple(route for route in routes if route.vehicle.id in allowed)


def _has_finite_locations(routes: tuple[VehicleRoute, ...]) -> bool:
    locations: list[Location] = []
    for route in routes:
        locations.append(route.vehicle.start_location)
        locations.extend(activity.job.location for activity in route.activities)
        if route.vehicle.end_location is not None:
            locations.append(route.vehicle.end_location)
    return bool(locations) and all(
        isfinite(location.x) and isfinite(location.y) for location in locations
    )


def _build_route_annotation_entries(
    *,
    routes: tuple[VehicleRoute, ...],
    show_timestamps: bool,
) -> tuple[str, ...]:
    entries: list[str] = []
    for route in routes:
        for activity in route.activities:
            if not (
                isfinite(activity.arrival_time)
                and isfinite(activity.service_start_time)
                and isfinite(activity.service_end_time)
            ):
                return ()
            line = f"{route.vehicle.id} stop {activity.position + 1}: {activity.job.id}"
            if show_timestamps:
                line += (
                    f" arrival={activity.arrival_time:.2f}"
                    f" start={activity.service_start_time:.2f}"
                    f" end={activity.service_end_time:.2f}"
                )
            entries.append(line)
    return tuple(entries)


def _render_annotation_svg(
    entries: tuple[str, ...],
    options: VisualizationOptions,
) -> str:
    line_height = 20
    width = options.width
    height = max(options.height, options.padding * 2 + line_height * max(1, len(entries) + 1))
    y = options.padding + line_height
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white" />',
        f'<text x="{options.padding}" y="{y}" font-size="16" font-family="monospace" fill="#111827">Route Annotation</text>',
    ]
    for entry in entries:
        y += line_height
        parts.append(
            f'<text x="{options.padding}" y="{y}" font-size="14" font-family="monospace" fill="#374151">{escape(entry)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def _render_solution_svg(
    *,
    routes: tuple[VehicleRoute, ...],
    options: VisualizationOptions,
) -> str:
    locations = _collect_route_locations(routes)
    if not locations:
        return _render_annotation_svg(("No routes",), options)

    min_x = min(location.x for location in locations)
    max_x = max(location.x for location in locations)
    min_y = min(location.y for location in locations)
    max_y = max(location.y for location in locations)
    range_x = max(max_x - min_x, 1.0)
    range_y = max(max_y - min_y, 1.0)
    usable_width = max(options.width - (options.padding * 2), 1)
    usable_height = max(options.height - (options.padding * 2), 1)

    def scale(location: Location) -> tuple[float, float]:
        x = options.padding + ((location.x - min_x) / range_x) * usable_width
        y = options.height - (
            options.padding + ((location.y - min_y) / range_y) * usable_height
        )
        return x, y

    palette = (
        "#1d4ed8",
        "#059669",
        "#dc2626",
        "#7c3aed",
        "#ea580c",
        "#0891b2",
        "#be123c",
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{options.width}" height="{options.height}" viewBox="0 0 {options.width} {options.height}">',
        f'<rect x="0" y="0" width="{options.width}" height="{options.height}" fill="white" />',
    ]
    for index, route in enumerate(routes):
        color = palette[index % len(palette)]
        path_locations = [route.vehicle.start_location]
        path_locations.extend(activity.job.location for activity in route.activities)
        if route.vehicle.end_location is not None:
            path_locations.append(route.vehicle.end_location)
        points = [scale(location) for location in path_locations]
        if len(points) >= 2:
            point_spec = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
            parts.append(
                f'<polyline points="{point_spec}" fill="none" stroke="{color}" stroke-width="2.5" opacity="0.9" />'
            )

        start_x, start_y = scale(route.vehicle.start_location)
        parts.append(
            f'<rect x="{start_x - 5:.2f}" y="{start_y - 5:.2f}" width="10" height="10" fill="{color}" />'
        )
        if options.show_labels:
            parts.append(
                f'<text x="{start_x + 8:.2f}" y="{start_y - 8:.2f}" font-size="12" font-family="sans-serif" fill="{color}">{escape(route.vehicle.id)}</text>'
            )

        for activity in route.activities:
            x, y = scale(activity.job.location)
            parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="{color}" stroke="white" stroke-width="1" />'
            )
            if options.show_labels:
                label = f"{activity.position + 1}:{activity.job.id}"
                parts.append(
                    f'<text x="{x + 6:.2f}" y="{y - 6:.2f}" font-size="11" font-family="sans-serif" fill="#111827">{escape(label)}</text>'
                )
            if options.show_timestamps:
                stamp = (
                    f"a={activity.arrival_time:.1f} "
                    f"s={activity.service_start_time:.1f}"
                )
                parts.append(
                    f'<text x="{x + 6:.2f}" y="{y + 12:.2f}" font-size="10" font-family="monospace" fill="#4b5563">{escape(stamp)}</text>'
                )

        if route.vehicle.end_location is not None:
            end_x, end_y = scale(route.vehicle.end_location)
            parts.append(
                f'<rect x="{end_x - 4:.2f}" y="{end_y - 4:.2f}" width="8" height="8" fill="white" stroke="{color}" stroke-width="2" />'
            )

    parts.append("</svg>")
    return "".join(parts)


def _collect_route_locations(routes: tuple[VehicleRoute, ...]) -> tuple[Location, ...]:
    locations: list[Location] = []
    for route in routes:
        locations.append(route.vehicle.start_location)
        locations.extend(activity.job.location for activity in route.activities)
        if route.vehicle.end_location is not None:
            locations.append(route.vehicle.end_location)
    return tuple(locations)
