"""Traceability:
- related_func: FUNC-BF-003-03
- feature: docs/usecases/function/extension_contracts/UC-FUNC-BF-003-03_Constraint を登録して利用可能にする.feature
"""

from __future__ import annotations

from py_sprit.domain.extension_contracts import ConstraintTargetDescriptor
from tests.support import AlwaysCompatibleConstraint


def test_Constraintを登録して後続探索で利用可能にする(runtime):
    result = runtime.extension_contracts.register_constraint(
        constraint=AlwaysCompatibleConstraint(),
        purpose="route feasibility",
        target_descriptor=ConstraintTargetDescriptor(target_kind="vehicle_route"),
    )
    assert result.is_success is True
    assert result.next_state is not None


def test_前提条件を満たさないためConstraintを登録しない(runtime):
    result = runtime.extension_contracts.register_constraint(
        constraint=object(),
        purpose="route feasibility",
        target_descriptor=ConstraintTargetDescriptor(target_kind="vehicle_route"),
    )
    assert result.is_success is False
