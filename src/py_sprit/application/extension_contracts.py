from __future__ import annotations

from dataclasses import dataclass

from py_sprit.domain.extension_contracts import (
    Constraint,
    ConstraintAvailabilityPolicy,
    ConstraintPurpose,
    ConstraintRegistration,
    ConstraintRegistrationResult,
    ConstraintTargetDescriptor,
    ConstraintTargetResolutionResult,
    ConstraintTargetResolutionService,
    ConstraintValidationResult,
    ExtensionContractValidator,
)


@dataclass(slots=True)
class ConfirmConstraintCompatibilityService:
    validator: ExtensionContractValidator

    def execute(
        self,
        *,
        constraint: object,
        purpose: str | ConstraintPurpose,
    ) -> ConstraintValidationResult:
        normalized_purpose = purpose if isinstance(purpose, ConstraintPurpose) else ConstraintPurpose(purpose)
        return self.validator.validate(constraint, normalized_purpose)


@dataclass(slots=True)
class ResolveConstraintTargetService:
    resolver: ConstraintTargetResolutionService

    def execute(
        self,
        *,
        constraint: Constraint,
        target_descriptor: ConstraintTargetDescriptor,
    ) -> ConstraintTargetResolutionResult:
        return self.resolver.resolve(constraint, target_descriptor)


@dataclass(slots=True)
class RegisterConstraintService:
    validator: ExtensionContractValidator
    resolver: ConstraintTargetResolutionService
    availability_policy: ConstraintAvailabilityPolicy
    registry_gateway: object

    def execute(
        self,
        *,
        constraint: object,
        purpose: str | ConstraintPurpose,
        target_descriptor: ConstraintTargetDescriptor,
    ) -> ConstraintRegistrationResult:
        normalized_purpose = purpose if isinstance(purpose, ConstraintPurpose) else ConstraintPurpose(purpose)
        validation = self.validator.validate(constraint, normalized_purpose)
        if not validation.is_success or validation.constraint is None:
            return ConstraintRegistrationResult(
                is_success=False,
                next_state=None,
                registered_constraint=None,
                reason=validation.reason,
            )
        resolution = self.resolver.resolve(validation.constraint, target_descriptor)
        if not resolution.is_success or resolution.target_descriptor is None:
            return ConstraintRegistrationResult(
                is_success=False,
                next_state=None,
                registered_constraint=validation.constraint,
                reason=resolution.reason,
            )
        registration_result = ConstraintRegistration.register(
            validation.constraint,
            normalized_purpose,
            resolution.target_descriptor,
        )
        if not registration_result.is_success or registration_result.next_state is None:
            return registration_result
        availability = self.availability_policy.allow(registration_result.next_state)
        if not availability.is_success or availability.next_state is None:
            return availability
        available = availability.next_state.makeAvailableForSearch()
        if not available.is_success or available.next_state is None:
            return available
        self.registry_gateway.register(available.next_state)
        return available
