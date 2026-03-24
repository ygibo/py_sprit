# py-sprit

`py-sprit` is a library-first Python VRP project inspired by `jsprit`.

The current executable surface is an in-process runtime with four adapters:

- `problem_definition`
- `extension_contracts`
- `algorithm_execution`
- `solution_visualization`

## Overview

- Library-first, single-process API
- Primary entrypoint: `create_runtime() -> PySpritRuntime`
- Focused on the current executable subset rather than full jsprit parity

## Current Status

### Supported problem types

- VRP with `Service` jobs
- VRP with `Shipment` jobs
- Capacity-constrained VRP
- Time-window-constrained VRP
- Heterogeneous fleet with multiple vehicles, per-type capacities, and fixed costs
- Skill-based assignment using `Vehicle.skills` and job `required_skills`
- Runtime-registered custom constraints

### Current algorithm

- Initial solution: greedy `BestInsertion`
- Improvement loop: `RandomRuin + BestInsertion`
- Incumbent update rule: improve only when `(unassigned_count, cost)` gets better
- Default termination: `TerminationCriterion(max_iterations=100)`

### Cost components

- `TransportCost`
- `VehicleRoutingActivityCosts`
- `VehicleType.fixed_cost`
- Registered soft-constraint penalties
- Unassigned-job penalty

### Current shipment subset

- `Shipment` is now runnable through the runtime API
- A `Shipment` produces two `TourActivity` entries: `pickup` and `delivery`
- `Shipment.delivery_location` is required
- The current subset reuses one `demand`, `time_window`, `service_duration`, and `required_skills` definition across both stops

## Public Runtime API

`PySpritRuntime` exposes these adapters.

### `runtime.problem_definition`

- `confirm_problem_model_inputs`
- `validate_problem_model`
- `define_problem_model`

### `runtime.extension_contracts`

- `confirm_constraint_compatibility`
- `resolve_constraint_target`
- `register_constraint`

### `runtime.algorithm_execution`

- `accept_search_request`
- `execute_search`
- `return_solution`

`execute_search(..., enable_technical_logs=True)` adds iteration-level technical logs to `SearchCompletionResult.technical_log`.

### `runtime.solution_visualization`

- `confirm_visualization_input`
- `generate_visualization_artifact`
- `return_visualization_artifact`
- `accept_route_map_review_target`
- `generate_route_map`
- `return_route_map`
- `accept_route_annotation_review_target`
- `generate_route_annotation`
- `return_route_annotation`

## Custom Constraints

Custom constraints are added through the `Constraint` protocol:

```python
is_feasible(context) -> bool
penalty(context) -> float
```

Current target kinds:

- `job`
- `vehicle`
- `vehicle_route`
- `tour_activity`

Registered constraints are stored in a runtime-local registry and affect subsequent `execute_search` calls.

## Technical Logs

Technical logs are opt-in and available only through the runtime API.

- Result field: `SearchCompletionResult.technical_log`
- Summary type: `SearchTechnicalLog`
- Per-iteration type: `SearchIterationLog`
- Scope: initial solution summary, per-iteration candidate metrics, incumbent transitions, elapsed search time

## Quick Start

### Setup

```bash
uv sync --dev
```

### Minimal example

```python
from py_sprit import (
    Capacity,
    FleetSize,
    Location,
    Service,
    TimeWindow,
    Vehicle,
    VehicleType,
    create_runtime,
)

runtime = create_runtime()

vehicle_type = VehicleType(id="type-1", capacity=Capacity.single(2))
vehicle = Vehicle(
    id="vehicle-1",
    vehicle_type=vehicle_type,
    start_location=Location(id="depot", x=0.0, y=0.0),
    end_location=Location(id="depot", x=0.0, y=0.0),
)
job = Service(
    id="job-1",
    location=Location(id="job-1", x=1.0, y=0.0),
    demand=Capacity.single(1),
    time_window=TimeWindow(0.0, 100.0),
)

completeness = runtime.problem_definition.confirm_problem_model_inputs(
    vehicle_types=(vehicle_type,),
    vehicles=(vehicle,),
    jobs=(job,),
    fleet_size=FleetSize.FINITE,
)
consistency = runtime.problem_definition.validate_problem_model(completeness.next_state)
definition = runtime.problem_definition.define_problem_model(consistency.next_state)
completion = runtime.algorithm_execution.execute_search(
    problem=definition.problem,
    enable_technical_logs=True,
)
returned = runtime.algorithm_execution.return_solution(completion)

if completion.technical_log is not None:
    print(len(completion.technical_log.iterations))
```

## Examples

Run the basic sample:

```bash
uv run python examples/run_basic_sample.py
```

Available examples:

- `examples/run_basic_sample.py`
  Basic end-to-end flow through `problem_definition -> extension_contracts -> algorithm_execution`
- `examples/run_capacity_vrp_sample.py`
  Capacity-constrained example with unassigned jobs
- `examples/run_time_window_vrp_sample.py`
  Time-window example showing visit order and waiting behavior
- `examples/run_skills_vrp_sample.py`
  Vehicle/job skill matching
- `examples/run_heterogeneous_fleet_sample.py`
  Heterogeneous fleet with different fixed costs and capacities
- `examples/run_constraint_customization_sample.py`
  Hard/soft constraint registration
- `examples/run_algorithm_customization_sample.py`
  Standard runtime execution vs lower-level strategy customization
- `examples/run_solomon_c101_sample.py`
  Medium-sized VRPTW sample using bundled Solomon `C101`
- `examples/run_cvrp_vrpnc1_sample.py`
  Medium-sized CVRP sample using bundled `vrpnc1`
- `examples/run_visualization_sample.py`
  Writes `VisualizationArtifact`, `RouteMap`, and `RouteAnnotation` SVG files under `artifacts/visualization/`
- `examples/run_shipment_vrp_sample.py`
  Shipment-aware example showing pickup and delivery activities in the returned route

## Limitations

- Runnable job types are currently `Service` and `Shipment`
- `Pickup` and `Delivery` types exist but are not executable in search yet
- `Break` can be defined in the problem model but is rejected at search start
- The current `Shipment` subset uses one shared operational profile across pickup and delivery stops rather than separate per-stop fields
- `FleetSize.INFINITE` is validated as a type, but search only uses vehicles explicitly provided in `problem.vehicles`
- No current support for `StateManager`, `ConstraintManager`, multiple strategy switching, regret insertion, listeners, FastAPI, or DB persistence
- Visualization currently supports SVG only

## Low-Level Solver Access

Some lower-level solver objects are exported, including `VehicleRoutingAlgorithm`, but the canonical integration path is still `create_runtime()` and the four adapters.

## Development

- Python: `>=3.12`
- Package and dependency management: `uv`

Run tests with:

```bash
uv run pytest
```

Smoke tests for examples live in `tests/integration/test_examples.py`.

## Documentation

Design artifacts are available under `docs/`:

- `docs/glossary/`
- `docs/context_map/`
- `docs/requirements/`
- `docs/robustness/`
- `docs/domain_model/`
- `docs/state_transition/`
- `docs/sequence/`
- `docs/usecases/`
