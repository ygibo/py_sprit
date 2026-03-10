"""Traceability:
- related_func: FUNC-BF-003-01
- feature: docs/usecases/function/extension_contracts/UC-FUNC-BF-003-01_Constraint の受理可否を確認する.feature
"""

from __future__ import annotations

from tests.support import AlwaysCompatibleConstraint


def test_公開拡張契約に適合するConstraintを受理する(runtime):
    result = runtime.extension_contracts.confirm_constraint_compatibility(
        constraint=AlwaysCompatibleConstraint(),
        purpose="route feasibility",
    )
    assert result.is_success is True


def test_公開契約に適合しないConstraintを受理しない(runtime):
    result = runtime.extension_contracts.confirm_constraint_compatibility(
        constraint=object(),
        purpose="route feasibility",
    )
    assert result.is_success is False
    assert result.reason == "公開契約に適合しない"
