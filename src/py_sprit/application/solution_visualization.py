from __future__ import annotations

from dataclasses import dataclass

from py_sprit.domain.algorithm_execution import VehicleRoutingProblemSolution
from py_sprit.domain.solution_visualization import (
    AlgorithmExecutionGateway,
    RouteAnnotationAvailabilityResult,
    RouteAnnotationGenerationResult,
    RouteAnnotationGenerationService,
    RouteAnnotationReviewTargetAcceptanceResult,
    RouteAnnotationTargetPolicy,
    RouteMapAvailabilityResult,
    RouteMapGenerationResult,
    RouteMapGenerationService,
    RouteMapReviewTargetAcceptanceResult,
    RouteMapTargetPolicy,
    VisualizationArtifactAssemblyPolicy,
    VisualizationArtifactAvailabilityResult,
    VisualizationArtifactGenerationResult,
    VisualizationArtifactGenerationService,
    VisualizationFormat,
    VisualizationInputConfirmationResult,
    VisualizationInputPolicy,
    VisualizationOptions,
)


@dataclass(slots=True)
class ConfirmVisualizationInputService:
    algorithm_execution_gateway: AlgorithmExecutionGateway
    input_policy: VisualizationInputPolicy

    def execute(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        format: VisualizationFormat = VisualizationFormat.SVG,
        options: VisualizationOptions | None = None,
    ) -> VisualizationInputConfirmationResult:
        resolved_solution = self.algorithm_execution_gateway.resolveSolution(solution)
        return self.input_policy.evaluate(resolved_solution, format, options)


@dataclass(slots=True)
class GenerateVisualizationArtifactService:
    confirm_service: ConfirmVisualizationInputService
    generation_service: VisualizationArtifactGenerationService

    def execute(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        format: VisualizationFormat = VisualizationFormat.SVG,
        options: VisualizationOptions | None = None,
    ) -> VisualizationArtifactGenerationResult:
        confirmation = self.confirm_service.execute(
            solution=solution,
            format=format,
            options=options,
        )
        if not confirmation.is_success or confirmation.next_state is None:
            return VisualizationArtifactGenerationResult(
                is_success=False,
                next_state=None,
                generated_artifact=None,
                reason=confirmation.reason,
            )
        return self.generation_service.generate(confirmation.next_state)


@dataclass(slots=True)
class ReturnVisualizationArtifactService:
    assembly_policy: VisualizationArtifactAssemblyPolicy

    def execute(
        self,
        generation_result: VisualizationArtifactGenerationResult,
    ) -> VisualizationArtifactAvailabilityResult:
        if not generation_result.is_success or generation_result.next_state is None:
            return VisualizationArtifactAvailabilityResult(
                is_success=False,
                next_state=None,
                available_artifact=None,
                reason=generation_result.reason or "生成済みの VisualizationArtifact が存在しない",
            )
        return self.assembly_policy.makeAvailable(generation_result.next_state)


@dataclass(slots=True)
class AcceptRouteMapReviewTargetService:
    algorithm_execution_gateway: AlgorithmExecutionGateway
    target_policy: RouteMapTargetPolicy

    def execute(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
    ) -> RouteMapReviewTargetAcceptanceResult:
        resolved_solution = self.algorithm_execution_gateway.resolveSolution(solution)
        return self.target_policy.accept(resolved_solution, vehicle_id)


@dataclass(slots=True)
class GenerateRouteMapService:
    accept_service: AcceptRouteMapReviewTargetService
    generation_service: RouteMapGenerationService

    def execute(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
        options: VisualizationOptions | None = None,
    ) -> RouteMapGenerationResult:
        accepted = self.accept_service.execute(solution=solution, vehicle_id=vehicle_id)
        if not accepted.is_success or accepted.next_state is None:
            return RouteMapGenerationResult(
                is_success=False,
                next_state=None,
                generated_route_map=None,
                reason=accepted.reason,
            )
        return self.generation_service.generate(accepted.next_state, options)


@dataclass(slots=True)
class ReturnRouteMapService:
    def execute(self, generation_result: RouteMapGenerationResult) -> RouteMapAvailabilityResult:
        if not generation_result.is_success or generation_result.next_state is None:
            return RouteMapAvailabilityResult(
                is_success=False,
                next_state=None,
                available_route_map=None,
                reason=generation_result.reason or "生成済みの RouteMap が存在しない",
            )
        return generation_result.next_state.makeRouteMapAvailable()


@dataclass(slots=True)
class AcceptRouteAnnotationReviewTargetService:
    algorithm_execution_gateway: AlgorithmExecutionGateway
    target_policy: RouteAnnotationTargetPolicy

    def execute(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
        options: VisualizationOptions | None = None,
    ) -> RouteAnnotationReviewTargetAcceptanceResult:
        resolved_solution = self.algorithm_execution_gateway.resolveSolution(solution)
        return self.target_policy.accept(resolved_solution, vehicle_id, options)


@dataclass(slots=True)
class GenerateRouteAnnotationService:
    accept_service: AcceptRouteAnnotationReviewTargetService
    generation_service: RouteAnnotationGenerationService

    def execute(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
        options: VisualizationOptions | None = None,
    ) -> RouteAnnotationGenerationResult:
        accepted = self.accept_service.execute(
            solution=solution,
            vehicle_id=vehicle_id,
            options=options,
        )
        if not accepted.is_success or accepted.next_state is None:
            return RouteAnnotationGenerationResult(
                is_success=False,
                next_state=None,
                generated_route_annotation=None,
                reason=accepted.reason,
            )
        return self.generation_service.generate(accepted.next_state, options)


@dataclass(slots=True)
class ReturnRouteAnnotationService:
    def execute(
        self,
        generation_result: RouteAnnotationGenerationResult,
    ) -> RouteAnnotationAvailabilityResult:
        if not generation_result.is_success or generation_result.next_state is None:
            return RouteAnnotationAvailabilityResult(
                is_success=False,
                next_state=None,
                available_route_annotation=None,
                reason=generation_result.reason or "生成済みの RouteAnnotation が存在しない",
            )
        return generation_result.next_state.makeRouteAnnotationAvailable()


__all__ = [
    "AcceptRouteAnnotationReviewTargetService",
    "AcceptRouteMapReviewTargetService",
    "ConfirmVisualizationInputService",
    "GenerateRouteAnnotationService",
    "GenerateRouteMapService",
    "GenerateVisualizationArtifactService",
    "ReturnRouteAnnotationService",
    "ReturnRouteMapService",
    "ReturnVisualizationArtifactService",
]
