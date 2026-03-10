from __future__ import annotations

from py_sprit.domain.extension_contracts import ConstraintTargetDescriptor
from tests.support import AlwaysCompatibleConstraint


def test_constraint_registration_services_cover_success_flow(runtime):
    validation = runtime.extension_contracts.confirm_constraint_compatibility(
        constraint=AlwaysCompatibleConstraint(),
        purpose="route feasibility",
    )
    assert validation.is_success is True
    resolution = runtime.extension_contracts.resolve_constraint_target(
        constraint=validation.constraint,
        target_descriptor=ConstraintTargetDescriptor(target_kind="vehicle_route"),
    )
    assert resolution.is_success is True
    registration = runtime.extension_contracts.register_constraint(
        constraint=validation.constraint,
        purpose="route feasibility",
        target_descriptor=resolution.target_descriptor,
    )
    assert registration.is_success is True
    assert registration.next_state is not None


def test_constraint_registration_services_cover_invalid_contract(runtime):
    validation = runtime.extension_contracts.confirm_constraint_compatibility(
        constraint=object(),
        purpose="route feasibility",
    )
    assert validation.is_success is False
    assert validation.reason == "公開契約に適合しない"


def test_constraint_registration_services_cover_unknown_target(runtime):
    validation = runtime.extension_contracts.confirm_constraint_compatibility(
        constraint=AlwaysCompatibleConstraint(),
        purpose="route feasibility",
    )
    resolution = runtime.extension_contracts.resolve_constraint_target(
        constraint=validation.constraint,
        target_descriptor=ConstraintTargetDescriptor(target_kind="unknown"),
    )
    assert resolution.is_success is False
    assert resolution.reason == "適用対象を特定できない"
