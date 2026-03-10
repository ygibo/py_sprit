from __future__ import annotations

from py_sprit.domain.problem_definition import (
    FleetSize,
    ProblemModelComponents,
    ProblemDefinitionStatus,
    ProblemModelCompletenessValidator,
    ProblemModelConsistencyValidator,
    VehicleRoutingProblemFactory,
)
from py_sprit.domain.shared import EuclideanTransportCost, TimeWindow, ZeroVehicleRoutingActivityCosts
from tests.support import make_problem_inputs


def test_time_window_rejects_invalid_range():
    try:
        TimeWindow(5.0, 4.0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid time window must raise")


def test_problem_can_be_completed_validated_and_defined():
    inputs = make_problem_inputs()
    problem = VehicleRoutingProblemFactory().create(
        initial_components=ProblemModelComponents(
            vehicle_types=inputs["vehicle_types"],
            vehicles=inputs["vehicles"],
            jobs=inputs["jobs"],
            transport_cost=EuclideanTransportCost(),
            activity_costs=ZeroVehicleRoutingActivityCosts(),
            fleet_size=inputs["fleet_size"],
            breaks=inputs["breaks"],
        )
    )
    completeness = ProblemModelCompletenessValidator().validate(problem)
    assert completeness.is_success is True
    assert completeness.next_state is not None
    assert completeness.next_state.status is ProblemDefinitionStatus.VALIDATED

    consistency = ProblemModelConsistencyValidator().validate(completeness.next_state)
    assert consistency.is_success is True
    assert consistency.next_state is not None

    definition = consistency.next_state.define()
    assert definition.is_success is True
    assert definition.problem is not None
    assert definition.problem.status is ProblemDefinitionStatus.DEFINED


def test_problem_consistency_rejects_break_with_infinite_fleet():
    inputs = make_problem_inputs(with_break=True, fleet_size=FleetSize.INFINITE)
    problem = VehicleRoutingProblemFactory().create(
        initial_components=ProblemModelComponents(
            vehicle_types=inputs["vehicle_types"],
            vehicles=inputs["vehicles"],
            jobs=inputs["jobs"] + inputs["breaks"],
            transport_cost=EuclideanTransportCost(),
            activity_costs=ZeroVehicleRoutingActivityCosts(),
            fleet_size=inputs["fleet_size"],
            breaks=inputs["breaks"],
        )
    )
    completeness = ProblemModelCompletenessValidator().validate(problem)
    assert completeness.is_success is True
    consistency = ProblemModelConsistencyValidator().validate(completeness.next_state)
    assert consistency.is_success is False
    assert consistency.reason == "Break を含むのに FleetSize が INFINITE である"


def test_problem_consistency_rejects_duplicate_job_ids():
    inputs = make_problem_inputs(job_count=1)
    duplicate_job = inputs["jobs"][0]
    problem = VehicleRoutingProblemFactory().create(
        initial_components=ProblemModelComponents(
            vehicle_types=inputs["vehicle_types"],
            vehicles=inputs["vehicles"],
            jobs=(duplicate_job, duplicate_job),
            transport_cost=EuclideanTransportCost(),
            activity_costs=ZeroVehicleRoutingActivityCosts(),
            fleet_size=inputs["fleet_size"],
            breaks=inputs["breaks"],
        )
    )
    completeness = ProblemModelCompletenessValidator().validate(problem)
    assert completeness.is_success is True
    consistency = ProblemModelConsistencyValidator().validate(completeness.next_state)
    assert consistency.is_success is False
    assert consistency.reason == "問題モデル不整合"
