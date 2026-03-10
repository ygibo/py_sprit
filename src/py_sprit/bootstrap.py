from __future__ import annotations

from random import Random

from py_sprit.application.algorithm_execution import (
    AcceptSearchRequestService,
    ExecuteSearchService,
    ReturnSolutionService,
)
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
from py_sprit.application.extension_contracts import (
    ConfirmConstraintCompatibilityService,
    RegisterConstraintService,
    ResolveConstraintTargetService,
)
from py_sprit.application.problem_definition import (
    ConfirmProblemModelInputsService,
    DefineProblemModelService,
    ValidateProblemModelService,
)
from py_sprit.domain.algorithm_execution import (
    BestSolutionSelectionService,
    ProblemDefinitionGateway,
    SearchExecutionService,
    SearchResultAssemblyPolicy,
    SearchStartPolicy,
    SolutionModelGateway,
)
from py_sprit.domain.extension_contracts import (
    ConstraintAvailabilityPolicy,
    ConstraintTargetResolutionService,
    ExtensionContractValidator,
)
from py_sprit.domain.problem_definition import (
    ProblemModelCompletenessValidator,
    ProblemModelConsistencyValidator,
    VehicleRoutingProblemFactory,
)
from py_sprit.domain.solution_visualization import (
    AlgorithmExecutionGateway,
    CoordinateAvailabilityPolicy,
    RouteAnnotationGenerationService as DomainRouteAnnotationGenerationService,
    RouteAnnotationOptionPolicy,
    RouteAnnotationTargetPolicy,
    RouteMapGenerationService as DomainRouteMapGenerationService,
    RouteMapTargetPolicy,
    VisualizationArtifactAssemblyPolicy,
    VisualizationArtifactGenerationService as DomainVisualizationArtifactGenerationService,
    VisualizationInputPolicy,
)
from py_sprit.infrastructure.gateways import (
    InMemoryAlgorithmExecutionVisualizationGateway,
    InMemoryExtensionContractsRegistryGateway,
    InMemoryProblemDefinitionGateway,
    InMemorySolutionModelGateway,
)
from py_sprit.presentation.algorithm_execution import (
    AlgorithmExecutionAdapter,
    SearchExecutionController,
    SearchExecutionPresenter,
)
from py_sprit.presentation.extension_contracts import (
    ConstraintRegistrationAdapter,
    ConstraintRegistrationController,
    ConstraintRegistrationPresenter,
)
from py_sprit.presentation.problem_definition import (
    ProblemDefinitionAdapter,
    ProblemDefinitionController,
    ProblemDefinitionPresenter,
)
from py_sprit.presentation.solution_visualization import (
    SolutionVisualizationAdapter,
    SolutionVisualizationController,
    SolutionVisualizationPresenter,
)
from py_sprit.runtime import PySpritRuntime


def create_runtime(*, random_seed: int | None = 0) -> PySpritRuntime:
    rng = Random(random_seed)
    registry_gateway = InMemoryExtensionContractsRegistryGateway()
    problem_gateway = InMemoryProblemDefinitionGateway()
    solution_gateway = InMemorySolutionModelGateway()
    visualization_gateway = InMemoryAlgorithmExecutionVisualizationGateway()

    problem_factory = VehicleRoutingProblemFactory()
    completeness_validator = ProblemModelCompletenessValidator()
    consistency_validator = ProblemModelConsistencyValidator()

    extension_validator = ExtensionContractValidator()
    target_resolution_service = ConstraintTargetResolutionService()
    availability_policy = ConstraintAvailabilityPolicy()

    search_start_policy = SearchStartPolicy()
    best_solution_selection_service = BestSolutionSelectionService()
    search_result_assembly_policy = SearchResultAssemblyPolicy()
    search_execution_service = SearchExecutionService(
        rng=rng,
        registry_gateway=registry_gateway,
    )
    visualization_input_policy = VisualizationInputPolicy()
    visualization_artifact_generation_service = DomainVisualizationArtifactGenerationService()
    visualization_artifact_assembly_policy = VisualizationArtifactAssemblyPolicy()
    route_map_target_policy = RouteMapTargetPolicy()
    coordinate_availability_policy = CoordinateAvailabilityPolicy()
    route_map_generation_service = DomainRouteMapGenerationService(
        coordinate_policy=coordinate_availability_policy,
    )
    route_annotation_target_policy = RouteAnnotationTargetPolicy()
    route_annotation_option_policy = RouteAnnotationOptionPolicy()
    route_annotation_generation_service = DomainRouteAnnotationGenerationService(
        option_policy=route_annotation_option_policy,
    )

    problem_definition_controller = ProblemDefinitionController(
        confirm_problem_model_inputs_service=ConfirmProblemModelInputsService(
            factory=problem_factory,
            completeness_validator=completeness_validator,
        ),
        validate_problem_model_service=ValidateProblemModelService(
            consistency_validator=consistency_validator,
        ),
        define_problem_model_service=DefineProblemModelService(),
        presenter=ProblemDefinitionPresenter(),
    )

    constraint_registration_controller = ConstraintRegistrationController(
        confirm_constraint_compatibility_service=ConfirmConstraintCompatibilityService(
            validator=extension_validator,
        ),
        resolve_constraint_target_service=ResolveConstraintTargetService(
            resolver=target_resolution_service,
        ),
        register_constraint_service=RegisterConstraintService(
            validator=extension_validator,
            resolver=target_resolution_service,
            availability_policy=availability_policy,
            registry_gateway=registry_gateway,
        ),
        presenter=ConstraintRegistrationPresenter(),
    )

    accept_search_request_service = AcceptSearchRequestService(
        problem_definition_gateway=ProblemDefinitionGateway(problem_gateway),
        search_start_policy=search_start_policy,
    )
    search_execution_controller = SearchExecutionController(
        accept_search_request_service=accept_search_request_service,
        execute_search_service=ExecuteSearchService(
            accept_service=accept_search_request_service,
            search_execution_service=search_execution_service,
            best_solution_selection_service=best_solution_selection_service,
            search_result_assembly_policy=search_result_assembly_policy,
        ),
        return_solution_service=ReturnSolutionService(
            solution_model_gateway=SolutionModelGateway(solution_gateway),
        ),
        presenter=SearchExecutionPresenter(),
    )
    algorithm_execution_gateway = AlgorithmExecutionGateway(visualization_gateway)
    solution_visualization_controller = SolutionVisualizationController(
        confirm_visualization_input_service=ConfirmVisualizationInputService(
            algorithm_execution_gateway=algorithm_execution_gateway,
            input_policy=visualization_input_policy,
        ),
        generate_visualization_artifact_service=GenerateVisualizationArtifactService(
            confirm_service=ConfirmVisualizationInputService(
                algorithm_execution_gateway=algorithm_execution_gateway,
                input_policy=visualization_input_policy,
            ),
            generation_service=visualization_artifact_generation_service,
        ),
        return_visualization_artifact_service=ReturnVisualizationArtifactService(
            assembly_policy=visualization_artifact_assembly_policy,
        ),
        accept_route_map_review_target_service=AcceptRouteMapReviewTargetService(
            algorithm_execution_gateway=algorithm_execution_gateway,
            target_policy=route_map_target_policy,
        ),
        generate_route_map_service=GenerateRouteMapService(
            accept_service=AcceptRouteMapReviewTargetService(
                algorithm_execution_gateway=algorithm_execution_gateway,
                target_policy=route_map_target_policy,
            ),
            generation_service=route_map_generation_service,
        ),
        return_route_map_service=ReturnRouteMapService(),
        accept_route_annotation_review_target_service=AcceptRouteAnnotationReviewTargetService(
            algorithm_execution_gateway=algorithm_execution_gateway,
            target_policy=route_annotation_target_policy,
        ),
        generate_route_annotation_service=GenerateRouteAnnotationService(
            accept_service=AcceptRouteAnnotationReviewTargetService(
                algorithm_execution_gateway=algorithm_execution_gateway,
                target_policy=route_annotation_target_policy,
            ),
            generation_service=route_annotation_generation_service,
        ),
        return_route_annotation_service=ReturnRouteAnnotationService(),
        presenter=SolutionVisualizationPresenter(),
    )

    return PySpritRuntime(
        problem_definition=ProblemDefinitionAdapter(problem_definition_controller),
        extension_contracts=ConstraintRegistrationAdapter(constraint_registration_controller),
        algorithm_execution=AlgorithmExecutionAdapter(search_execution_controller),
        solution_visualization=SolutionVisualizationAdapter(solution_visualization_controller),
    )
