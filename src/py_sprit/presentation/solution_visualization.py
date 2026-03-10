from __future__ import annotations

from dataclasses import dataclass

from py_sprit.application.solution_visualization import (
    AcceptRouteAnnotationReviewTargetService,
    AcceptRouteMapReviewTargetService,
    ConfirmVisualizationInputService,
    GenerateRouteAnnotationService,
    GenerateRouteMapService,
    GenerateVisualizationArtifactService,
    ReturnRouteAnnotationService,
    ReturnRouteMapService,
    ReturnVisualizationArtifactService,
)
from py_sprit.domain.algorithm_execution import VehicleRoutingProblemSolution
from py_sprit.domain.solution_visualization import (
    RouteAnnotationAvailabilityResult,
    RouteAnnotationGenerationResult,
    RouteAnnotationReviewTargetAcceptanceResult,
    RouteMapAvailabilityResult,
    RouteMapGenerationResult,
    RouteMapReviewTargetAcceptanceResult,
    VisualizationArtifactAvailabilityResult,
    VisualizationArtifactGenerationResult,
    VisualizationFormat,
    VisualizationInputConfirmationResult,
    VisualizationOptions,
)


@dataclass(slots=True)
class SolutionVisualizationPresenter:
    def present_input_confirmation_result(
        self,
        result: VisualizationInputConfirmationResult,
    ) -> VisualizationInputConfirmationResult:
        return result

    def present_visualization_artifact_generation_result(
        self,
        result: VisualizationArtifactGenerationResult,
    ) -> VisualizationArtifactGenerationResult:
        return result

    def present_visualization_artifact_availability_result(
        self,
        result: VisualizationArtifactAvailabilityResult,
    ) -> VisualizationArtifactAvailabilityResult:
        return result

    def present_route_map_review_target_acceptance_result(
        self,
        result: RouteMapReviewTargetAcceptanceResult,
    ) -> RouteMapReviewTargetAcceptanceResult:
        return result

    def present_route_map_generation_result(
        self,
        result: RouteMapGenerationResult,
    ) -> RouteMapGenerationResult:
        return result

    def present_route_map_availability_result(
        self,
        result: RouteMapAvailabilityResult,
    ) -> RouteMapAvailabilityResult:
        return result

    def present_route_annotation_review_target_acceptance_result(
        self,
        result: RouteAnnotationReviewTargetAcceptanceResult,
    ) -> RouteAnnotationReviewTargetAcceptanceResult:
        return result

    def present_route_annotation_generation_result(
        self,
        result: RouteAnnotationGenerationResult,
    ) -> RouteAnnotationGenerationResult:
        return result

    def present_route_annotation_availability_result(
        self,
        result: RouteAnnotationAvailabilityResult,
    ) -> RouteAnnotationAvailabilityResult:
        return result


@dataclass(slots=True)
class SolutionVisualizationController:
    confirm_visualization_input_service: ConfirmVisualizationInputService
    generate_visualization_artifact_service: GenerateVisualizationArtifactService
    return_visualization_artifact_service: ReturnVisualizationArtifactService
    accept_route_map_review_target_service: AcceptRouteMapReviewTargetService
    generate_route_map_service: GenerateRouteMapService
    return_route_map_service: ReturnRouteMapService
    accept_route_annotation_review_target_service: AcceptRouteAnnotationReviewTargetService
    generate_route_annotation_service: GenerateRouteAnnotationService
    return_route_annotation_service: ReturnRouteAnnotationService
    presenter: SolutionVisualizationPresenter

    def confirm_visualization_input(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        format: VisualizationFormat = VisualizationFormat.SVG,
        options: VisualizationOptions | None = None,
    ) -> VisualizationInputConfirmationResult:
        result = self.confirm_visualization_input_service.execute(
            solution=solution,
            format=format,
            options=options,
        )
        return self.presenter.present_input_confirmation_result(result)

    def generate_visualization_artifact(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        format: VisualizationFormat = VisualizationFormat.SVG,
        options: VisualizationOptions | None = None,
    ) -> VisualizationArtifactGenerationResult:
        result = self.generate_visualization_artifact_service.execute(
            solution=solution,
            format=format,
            options=options,
        )
        return self.presenter.present_visualization_artifact_generation_result(result)

    def return_visualization_artifact(
        self,
        generation_result: VisualizationArtifactGenerationResult,
    ) -> VisualizationArtifactAvailabilityResult:
        result = self.return_visualization_artifact_service.execute(generation_result)
        return self.presenter.present_visualization_artifact_availability_result(result)

    def accept_route_map_review_target(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
    ) -> RouteMapReviewTargetAcceptanceResult:
        result = self.accept_route_map_review_target_service.execute(
            solution=solution,
            vehicle_id=vehicle_id,
        )
        return self.presenter.present_route_map_review_target_acceptance_result(result)

    def generate_route_map(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
        options: VisualizationOptions | None = None,
    ) -> RouteMapGenerationResult:
        result = self.generate_route_map_service.execute(
            solution=solution,
            vehicle_id=vehicle_id,
            options=options,
        )
        return self.presenter.present_route_map_generation_result(result)

    def return_route_map(
        self,
        generation_result: RouteMapGenerationResult,
    ) -> RouteMapAvailabilityResult:
        result = self.return_route_map_service.execute(generation_result)
        return self.presenter.present_route_map_availability_result(result)

    def accept_route_annotation_review_target(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
        options: VisualizationOptions | None = None,
    ) -> RouteAnnotationReviewTargetAcceptanceResult:
        result = self.accept_route_annotation_review_target_service.execute(
            solution=solution,
            vehicle_id=vehicle_id,
            options=options,
        )
        return self.presenter.present_route_annotation_review_target_acceptance_result(result)

    def generate_route_annotation(
        self,
        *,
        solution: VehicleRoutingProblemSolution | None,
        vehicle_id: str | None = None,
        options: VisualizationOptions | None = None,
    ) -> RouteAnnotationGenerationResult:
        result = self.generate_route_annotation_service.execute(
            solution=solution,
            vehicle_id=vehicle_id,
            options=options,
        )
        return self.presenter.present_route_annotation_generation_result(result)

    def return_route_annotation(
        self,
        generation_result: RouteAnnotationGenerationResult,
    ) -> RouteAnnotationAvailabilityResult:
        result = self.return_route_annotation_service.execute(generation_result)
        return self.presenter.present_route_annotation_availability_result(result)


@dataclass(slots=True)
class SolutionVisualizationAdapter:
    controller: SolutionVisualizationController

    def confirm_visualization_input(self, **kwargs: object) -> VisualizationInputConfirmationResult:
        return self.controller.confirm_visualization_input(**kwargs)

    def generate_visualization_artifact(
        self,
        **kwargs: object,
    ) -> VisualizationArtifactGenerationResult:
        return self.controller.generate_visualization_artifact(**kwargs)

    def return_visualization_artifact(
        self,
        generation_result: VisualizationArtifactGenerationResult,
    ) -> VisualizationArtifactAvailabilityResult:
        return self.controller.return_visualization_artifact(generation_result)

    def accept_route_map_review_target(
        self,
        **kwargs: object,
    ) -> RouteMapReviewTargetAcceptanceResult:
        return self.controller.accept_route_map_review_target(**kwargs)

    def generate_route_map(self, **kwargs: object) -> RouteMapGenerationResult:
        return self.controller.generate_route_map(**kwargs)

    def return_route_map(
        self,
        generation_result: RouteMapGenerationResult,
    ) -> RouteMapAvailabilityResult:
        return self.controller.return_route_map(generation_result)

    def accept_route_annotation_review_target(
        self,
        **kwargs: object,
    ) -> RouteAnnotationReviewTargetAcceptanceResult:
        return self.controller.accept_route_annotation_review_target(**kwargs)

    def generate_route_annotation(
        self,
        **kwargs: object,
    ) -> RouteAnnotationGenerationResult:
        return self.controller.generate_route_annotation(**kwargs)

    def return_route_annotation(
        self,
        generation_result: RouteAnnotationGenerationResult,
    ) -> RouteAnnotationAvailabilityResult:
        return self.controller.return_route_annotation(generation_result)
