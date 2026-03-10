from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4


ALLOWED_TARGET_KINDS = ("job", "vehicle", "vehicle_route", "tour_activity")


@dataclass(frozen=True, slots=True)
class ConstraintPurpose:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("constraint purpose must not be blank")


@dataclass(frozen=True, slots=True)
class ConstraintTargetDescriptor:
    target_kind: str
    target_id: str | None = None


@dataclass(frozen=True, slots=True)
class ConstraintEvaluationContext:
    job: Any = None
    vehicle: Any = None
    vehicle_route: Any = None
    tour_activity: Any = None


@runtime_checkable
class Constraint(Protocol):
    def is_feasible(self, context: ConstraintEvaluationContext) -> bool:
        ...

    def penalty(self, context: ConstraintEvaluationContext) -> float:
        ...


class ConstraintRegistrationStatus(str, Enum):
    REGISTERED = "Registered"
    AVAILABLE_FOR_SEARCH = "AvailableForSearch"


@dataclass(frozen=True, slots=True)
class ConstraintAvailableForSearchEvent:
    name: str = "ConstraintAvailableForSearchEvent"


@dataclass(frozen=True, slots=True)
class ConstraintValidationResult:
    is_success: bool
    constraint: Constraint | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ConstraintTargetResolutionResult:
    is_success: bool
    constraint: Constraint | None
    target_descriptor: ConstraintTargetDescriptor | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ConstraintRegistrationResult:
    is_success: bool
    next_state: "ConstraintRegistration" | None
    registered_constraint: Constraint | None
    event: ConstraintAvailableForSearchEvent | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ConstraintRegistration:
    registration_id: str
    constraint: Constraint
    purpose: ConstraintPurpose
    target_descriptor: ConstraintTargetDescriptor
    status: ConstraintRegistrationStatus = ConstraintRegistrationStatus.REGISTERED

    @classmethod
    def register(
        cls,
        constraint: Constraint,
        purpose: ConstraintPurpose,
        target_descriptor: ConstraintTargetDescriptor,
    ) -> ConstraintRegistrationResult:
        registration = cls(
            registration_id=str(uuid4()),
            constraint=constraint,
            purpose=purpose,
            target_descriptor=target_descriptor,
        )
        return ConstraintRegistrationResult(
            is_success=True,
            next_state=registration,
            registered_constraint=constraint,
        )

    def makeAvailableForSearch(self) -> ConstraintRegistrationResult:
        available = ConstraintRegistration(
            registration_id=self.registration_id,
            constraint=self.constraint,
            purpose=self.purpose,
            target_descriptor=self.target_descriptor,
            status=ConstraintRegistrationStatus.AVAILABLE_FOR_SEARCH,
        )
        return ConstraintRegistrationResult(
            is_success=True,
            next_state=available,
            registered_constraint=self.constraint,
            event=ConstraintAvailableForSearchEvent(),
        )


@dataclass(frozen=True, slots=True)
class ExtensionContractValidator:
    def validate(
        self,
        constraint: object,
        purpose: ConstraintPurpose,
    ) -> ConstraintValidationResult:
        if not isinstance(constraint, Constraint):
            return ConstraintValidationResult(
                is_success=False,
                constraint=None,
                reason="公開契約に適合しない",
            )
        if not purpose.value.strip():
            return ConstraintValidationResult(
                is_success=False,
                constraint=None,
                reason="公開契約に適合しない",
            )
        return ConstraintValidationResult(
            is_success=True,
            constraint=constraint,
        )


@dataclass(frozen=True, slots=True)
class ConstraintTargetResolutionService:
    def resolve(
        self,
        constraint: Constraint,
        target_descriptor: ConstraintTargetDescriptor,
    ) -> ConstraintTargetResolutionResult:
        if target_descriptor.target_kind not in ALLOWED_TARGET_KINDS:
            return ConstraintTargetResolutionResult(
                is_success=False,
                constraint=constraint,
                target_descriptor=None,
                reason="適用対象を特定できない",
            )
        return ConstraintTargetResolutionResult(
            is_success=True,
            constraint=constraint,
            target_descriptor=target_descriptor,
        )


@dataclass(frozen=True, slots=True)
class ConstraintAvailabilityPolicy:
    def allow(
        self,
        registration: ConstraintRegistration,
    ) -> ConstraintRegistrationResult:
        if registration.status is not ConstraintRegistrationStatus.REGISTERED:
            return ConstraintRegistrationResult(
                is_success=False,
                next_state=None,
                registered_constraint=None,
                reason="前提条件を満たさないため Constraint を登録しない",
            )
        return ConstraintRegistrationResult(
            is_success=True,
            next_state=registration,
            registered_constraint=registration.constraint,
        )
