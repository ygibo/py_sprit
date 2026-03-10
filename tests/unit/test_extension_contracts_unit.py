from __future__ import annotations

from py_sprit.domain.extension_contracts import (
    ConstraintAvailabilityPolicy,
    ConstraintPurpose,
    ConstraintRegistration,
    ConstraintRegistrationStatus,
    ConstraintTargetDescriptor,
    ConstraintTargetResolutionService,
    ExtensionContractValidator,
)
from tests.support import AlwaysCompatibleConstraint


def test_constraint_validation_accepts_protocol_compatible_constraint():
    result = ExtensionContractValidator().validate(
        AlwaysCompatibleConstraint(),
        ConstraintPurpose("route feasibility"),
    )
    assert result.is_success is True
    assert result.constraint is not None


def test_constraint_target_resolution_rejects_unknown_target_kind():
    result = ConstraintTargetResolutionService().resolve(
        AlwaysCompatibleConstraint(),
        ConstraintTargetDescriptor(target_kind="unknown"),
    )
    assert result.is_success is False
    assert result.reason == "適用対象を特定できない"


def test_constraint_registration_becomes_available_for_search():
    registration = ConstraintRegistration.register(
        AlwaysCompatibleConstraint(),
        ConstraintPurpose("route feasibility"),
        ConstraintTargetDescriptor(target_kind="vehicle_route"),
    )
    assert registration.is_success is True
    assert registration.next_state is not None
    assert registration.next_state.status is ConstraintRegistrationStatus.REGISTERED

    availability = ConstraintAvailabilityPolicy().allow(registration.next_state)
    assert availability.is_success is True
    available = availability.next_state.makeAvailableForSearch()
    assert available.is_success is True
    assert available.next_state is not None
    assert available.next_state.status is ConstraintRegistrationStatus.AVAILABLE_FOR_SEARCH
    assert available.event is not None
