from __future__ import annotations

from dataclasses import dataclass

from py_sprit.application.extension_contracts import (
    ConfirmConstraintCompatibilityService,
    RegisterConstraintService,
    ResolveConstraintTargetService,
)
from py_sprit.domain.extension_contracts import (
    Constraint,
    ConstraintRegistrationResult,
    ConstraintTargetDescriptor,
    ConstraintTargetResolutionResult,
    ConstraintValidationResult,
)


@dataclass(slots=True)
class ConstraintRegistrationPresenter:
    def present_validation_result(
        self,
        result: ConstraintValidationResult,
    ) -> ConstraintValidationResult:
        return result

    def present_target_resolution_result(
        self,
        result: ConstraintTargetResolutionResult,
    ) -> ConstraintTargetResolutionResult:
        return result

    def present_registration_result(
        self,
        result: ConstraintRegistrationResult,
    ) -> ConstraintRegistrationResult:
        return result


@dataclass(slots=True)
class ConstraintRegistrationController:
    confirm_constraint_compatibility_service: ConfirmConstraintCompatibilityService
    resolve_constraint_target_service: ResolveConstraintTargetService
    register_constraint_service: RegisterConstraintService
    presenter: ConstraintRegistrationPresenter

    def confirm_constraint_compatibility(
        self,
        *,
        constraint: object,
        purpose: str,
    ) -> ConstraintValidationResult:
        result = self.confirm_constraint_compatibility_service.execute(
            constraint=constraint,
            purpose=purpose,
        )
        return self.presenter.present_validation_result(result)

    def resolve_constraint_target(
        self,
        *,
        constraint: Constraint,
        target_descriptor: ConstraintTargetDescriptor,
    ) -> ConstraintTargetResolutionResult:
        result = self.resolve_constraint_target_service.execute(
            constraint=constraint,
            target_descriptor=target_descriptor,
        )
        return self.presenter.present_target_resolution_result(result)

    def register_constraint(
        self,
        *,
        constraint: object,
        purpose: str,
        target_descriptor: ConstraintTargetDescriptor,
    ) -> ConstraintRegistrationResult:
        result = self.register_constraint_service.execute(
            constraint=constraint,
            purpose=purpose,
            target_descriptor=target_descriptor,
        )
        return self.presenter.present_registration_result(result)


@dataclass(slots=True)
class ConstraintRegistrationAdapter:
    controller: ConstraintRegistrationController

    def confirm_constraint_compatibility(self, **kwargs: object) -> ConstraintValidationResult:
        return self.controller.confirm_constraint_compatibility(**kwargs)

    def resolve_constraint_target(self, **kwargs: object) -> ConstraintTargetResolutionResult:
        return self.controller.resolve_constraint_target(**kwargs)

    def register_constraint(self, **kwargs: object) -> ConstraintRegistrationResult:
        return self.controller.register_constraint(**kwargs)
