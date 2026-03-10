# py-sprit

`py-sprit` is a library-first Python VRP project inspired by `jsprit`.  
`py-sprit` は `jsprit` に着想を得た、ライブラリ中心の Python VRP 実装プロジェクトです。

The current executable surface is an in-process runtime with four adapters: `problem_definition`, `extension_contracts`, `algorithm_execution`, and `solution_visualization`.  
現在の実行可能な公開面は、`problem_definition`、`extension_contracts`、`algorithm_execution`、`solution_visualization` の 4 つの adapter を持つ in-process runtime です。

## Overview / 概要

- Library-first, single-process API.
  単一プロセスで使う library-first API です。
- Current primary entrypoint: `create_runtime() -> PySpritRuntime`.
  現在の主な入口は `create_runtime() -> PySpritRuntime` です。
- Designed around the current Step 12 executable subset, not full jsprit parity.
  full jsprit 互換ではなく、現在の Step 12 実行可能 subset を中心に設計されています。

## Current Status / 現在の実装状況

### Supported problem types / 現在対応している問題

- VRP with `Service` jobs.
  `Service` を配送要求とする VRP
- Capacity-constrained VRP.
  容量制約付き VRP
- Time-window-constrained VRP.
  時間窓付き VRP
- Heterogeneous fleet with multiple vehicles, per-type capacities, and fixed costs.
  複数車両、車種別容量、固定費を持つ heterogeneous fleet
- Skill-based assignment using `Vehicle.skills` and `Service.required_skills`.
  `Vehicle.skills` と `Service.required_skills` を使うスキル制約付き割当
- Runtime-registered custom constraints.
  runtime に登録するカスタム constraint

### Current algorithm / 現在の探索アルゴリズム

- Initial solution: greedy `BestInsertion`
  初期解生成: greedy `BestInsertion`
- Improvement loop: `RandomRuin + BestInsertion`
  反復改善: `RandomRuin + BestInsertion`
- Incumbent update rule: improve only when `(unassigned_count, cost)` gets better
  incumbent 更新条件: `(未割当数, cost)` が改善した場合のみ更新
- Default termination: `TerminationCriterion(max_iterations=100)`
  既定の終了条件: `TerminationCriterion(max_iterations=100)`

### Cost components / 評価要素

- `TransportCost`
- `VehicleRoutingActivityCosts`
- `VehicleType.fixed_cost`
- Registered soft-constraint penalties
  登録済み soft constraint penalty
- Unassigned-job penalty
  未割当 job penalty

## Public Runtime API / 公開 runtime API

`PySpritRuntime` exposes these adapters.  
`PySpritRuntime` は次の adapter を公開します。

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
`execute_search(..., enable_technical_logs=True)` を指定すると、iteration 単位の技術ログが `SearchCompletionResult.technical_log` に含まれます。

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

## Custom Constraints / カスタム constraint

Custom constraints are added through the `Constraint` protocol.  
カスタム constraint は `Constraint` protocol で追加します。

```python
is_feasible(context) -> bool
penalty(context) -> float
```

Current target kinds:  
現在の target kind は次の 4 つです。

- `job`
- `vehicle`
- `vehicle_route`
- `tour_activity`

Registered constraints are stored in a runtime-local registry and affect subsequent `execute_search` calls.  
登録した constraint は runtime 単位の registry に保存され、後続の `execute_search` に反映されます。

## Technical Logs / 技術ログ

Technical logs are opt-in and available only through the runtime API.  
技術ログは opt-in であり、runtime API からのみ取得できます。

- Result field: `SearchCompletionResult.technical_log`
  結果フィールド: `SearchCompletionResult.technical_log`
- Summary type: `SearchTechnicalLog`
  サマリ型: `SearchTechnicalLog`
- Per-iteration type: `SearchIterationLog`
  反復ログ型: `SearchIterationLog`
- Scope: initial solution summary, per-iteration candidate metrics, incumbent transitions, elapsed search time
  対象: 初期解サマリ、各 iteration の candidate 指標、incumbent の推移、探索本体の実行時間

## Quick Start / クイックスタート

### Setup / セットアップ

```bash
uv sync --dev
```

### Minimal example / 最小利用例

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

## Examples / サンプル

Run the basic sample:  
基本サンプルの実行:

```bash
uv run python examples/run_basic_sample.py
```

Available examples / 利用可能なサンプル:

- `examples/run_basic_sample.py`
  - Basic end-to-end flow through `problem_definition -> extension_contracts -> algorithm_execution`
  - `problem_definition -> extension_contracts -> algorithm_execution` を 1 回で通す基本例
- `examples/run_capacity_vrp_sample.py`
  - Capacity-constrained example with unassigned jobs
  - 容量制約により未割当 job が発生する例
- `examples/run_time_window_vrp_sample.py`
  - Time-window example showing visit order and waiting behavior
  - 時間窓により訪問順や待機時間が効く例
- `examples/run_skills_vrp_sample.py`
  - Vehicle/job skill matching
  - vehicle と job の skill 割当例
- `examples/run_heterogeneous_fleet_sample.py`
  - Heterogeneous fleet with different fixed costs and capacities
  - 異なる固定費と容量を持つ fleet の例
- `examples/run_constraint_customization_sample.py`
  - Hard/soft constraint registration
  - hard/soft constraint の登録例
- `examples/run_algorithm_customization_sample.py`
  - Standard runtime execution vs lower-level strategy customization
  - 既定 runtime 実行と lower-level strategy 差し替えの比較例
- `examples/run_solomon_c101_sample.py`
  - Medium-sized VRPTW sample using bundled Solomon `C101`
  - 同梱の Solomon `C101` を使う中規模 VRPTW 例
- `examples/run_cvrp_vrpnc1_sample.py`
  - Medium-sized CVRP sample using bundled `vrpnc1`
  - 同梱の `vrpnc1` を使う中規模 CVRP 例
- `examples/run_visualization_sample.py`
  - Writes `VisualizationArtifact`, `RouteMap`, and `RouteAnnotation` SVG files under `artifacts/visualization/`
  - `VisualizationArtifact`、`RouteMap`、`RouteAnnotation` の SVG を `artifacts/visualization/` に書き出す例

## Limitations / 制約と未対応範囲

- The current runnable job type is effectively `Service` only.
  現在の実行可能 job は実質 `Service` のみです。
- `Shipment`, `Pickup`, and `Delivery` types exist but are not executable in search yet.
  `Shipment`、`Pickup`、`Delivery` は型はありますが探索では未対応です。
- `Break` can be defined in the problem model but is rejected at search start.
  `Break` は problem 定義には含められますが、探索開始時に拒否されます。
- `FleetSize.INFINITE` is validated as a type, but search only uses vehicles explicitly provided in `problem.vehicles`.
  `FleetSize.INFINITE` は型と検証上は存在しますが、探索は `problem.vehicles` に与えた車両だけを使います。
- No current support for `StateManager`, `ConstraintManager`, multiple strategy switching, regret insertion, listeners, FastAPI, or DB persistence.
  `StateManager`、`ConstraintManager`、複数戦略切替、regret insertion、listener、FastAPI、DB 永続化は現時点では未対応です。
- Visualization currently supports SVG only.
  可視化は現在 SVG のみ対応です。

## Low-Level Solver Access / lower-level solver 利用

Some lower-level solver objects are exported, including `VehicleRoutingAlgorithm`, but the canonical integration path is still `create_runtime()` and the four adapters.  
`VehicleRoutingAlgorithm` など一部の lower-level solver object は export されていますが、正準の統合入口は引き続き `create_runtime()` と 4 つの adapter です。

## Development / 開発

- Python: `>=3.12`
  Python: `>=3.12`
- Package/dependency management: `uv`
  パッケージ/依存管理: `uv`
- Test command:
  テストコマンド:

```bash
uv run pytest
```

Smoke tests for examples live in `tests/integration/test_examples.py`.  
サンプルの smoke test は `tests/integration/test_examples.py` にあります。

## Documentation / ドキュメント

Design artifacts are available under `docs/`.  
設計成果物は `docs/` 配下にあります。

- `docs/glossary/`
- `docs/context_map/`
- `docs/requirements/`
- `docs/robustness/`
- `docs/domain_model/`
- `docs/state_transition/`
- `docs/sequence/`
- `docs/usecases/`
