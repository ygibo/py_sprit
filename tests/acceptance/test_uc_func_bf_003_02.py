"""Traceability:
- related_func: FUNC-BF-003-02
- feature: docs/usecases/function/extension_contracts/UC-FUNC-BF-003-02_Constraint の適用対象を確定する.feature
"""

from __future__ import annotations

from py_sprit.domain.extension_contracts import ConstraintTargetDescriptor
from tests.support import AlwaysCompatibleConstraint


def test_Constraintの適用対象を特定する(runtime):
    result = runtime.extension_contracts.resolve_constraint_target(
        constraint=AlwaysCompatibleConstraint(),
        target_descriptor=ConstraintTargetDescriptor(target_kind="job", target_id="job-1"),
    )
    assert result.is_success is True
    assert result.target_descriptor is not None


def test_Constraintの適用対象を特定できない(runtime):
    result = runtime.extension_contracts.resolve_constraint_target(
        constraint=AlwaysCompatibleConstraint(),
        target_descriptor=ConstraintTargetDescriptor(target_kind="unknown"),
    )
    assert result.is_success is False
    assert result.reason == "適用対象を特定できない"
