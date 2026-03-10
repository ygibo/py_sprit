from __future__ import annotations

from py_sprit.domain.problem_definition import FleetSize
from tests.support import make_problem_inputs


def test_problem_definition_services_cover_success_flow(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(**make_problem_inputs())
    assert completeness.is_success is True
    consistency = runtime.problem_definition.validate_problem_model(completeness.next_state)
    assert consistency.is_success is True
    definition = runtime.problem_definition.define_problem_model(consistency.next_state)
    assert definition.is_success is True
    assert definition.problem is not None


def test_problem_definition_services_cover_missing_information(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(
        **make_problem_inputs(job_count=0)
    )
    assert completeness.is_success is False
    assert completeness.reason == "必要情報が不足している"


def test_problem_definition_services_cover_break_infinite_conflict(runtime):
    completeness = runtime.problem_definition.confirm_problem_model_inputs(
        **make_problem_inputs(with_break=True, fleet_size=FleetSize.INFINITE)
    )
    assert completeness.is_success is True
    consistency = runtime.problem_definition.validate_problem_model(completeness.next_state)
    assert consistency.is_success is False
    assert consistency.reason == "Break を含むのに FleetSize が INFINITE である"
