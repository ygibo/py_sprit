from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts" / "visualization"
EXAMPLES = [
    (
        "run_basic_sample.py",
        (
            "== Constraint Registration ==",
            "Route count: 2",
            "Unassigned jobs: 0",
        ),
    ),
    (
        "run_capacity_vrp_sample.py",
        (
            "== Search Execution ==",
            "Route count: 1",
            "Unassigned jobs: 1",
        ),
    ),
    (
        "run_time_window_vrp_sample.py",
        (
            "== Search Execution ==",
            "job-early: arrival=",
            "job-late: arrival=",
        ),
    ),
    (
        "run_skills_vrp_sample.py",
        (
            "== Search Execution ==",
            "vehicle-cold",
            "vehicle-standard",
        ),
    ),
    (
        "run_heterogeneous_fleet_sample.py",
        (
            "== Search Execution ==",
            "vehicle-small",
            "vehicle-large",
        ),
    ),
    (
        "run_constraint_customization_sample.py",
        (
            "== Constraint Registration ==",
            "hard route limit",
            "soft activity penalty",
        ),
    ),
    (
        "run_algorithm_customization_sample.py",
        (
            "== Default Search ==",
            "== Algorithm Customization ==",
            "== Customized Solution Summary ==",
        ),
    ),
    (
        "run_solomon_c101_sample.py",
        (
            "== Instance Loading ==",
            "Instance: Solomon C101",
            "Jobs: 100",
            "Displayed routes: 5",
        ),
    ),
    (
        "run_cvrp_vrpnc1_sample.py",
        (
            "== Instance Loading ==",
            "Instance: CVRP vrpnc1.txt",
            "Jobs: 50",
            "Displayed routes: 5",
        ),
    ),
    (
        "run_visualization_sample.py",
        (
            "== Solution Visualization ==",
            "VisualizationArtifact:",
            "RouteMap:",
            "RouteAnnotation:",
        ),
    ),
    (
        "run_shipment_vrp_sample.py",
        (
            "== Search Execution ==",
            "shipment-1 pickup: arrival=",
            "shipment-1 delivery: arrival=",
        ),
    ),
]


@pytest.mark.parametrize(("script_name", "markers"), EXAMPLES)
def test_example_scripts_smoke(script_name: str, markers: tuple[str, ...]) -> None:
    example = ROOT / "examples" / script_name
    completed = subprocess.run(
        [sys.executable, str(example)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "== Problem Definition ==" in completed.stdout
    assert (
        "== Solution Summary ==" in completed.stdout
        or "== Default Solution Summary ==" in completed.stdout
    )
    for marker in markers:
        assert marker in completed.stdout


@pytest.mark.parametrize("script_name", [name for name, _ in EXAMPLES])
def test_examples_do_not_depend_on_test_helpers(script_name: str) -> None:
    example = ROOT / "examples" / script_name
    content = example.read_text(encoding="utf-8")
    assert "tests.support" not in content


def test_visualization_example_writes_svg_artifacts() -> None:
    example = ROOT / "examples" / "run_visualization_sample.py"
    if ARTIFACT_DIR.exists():
        for path in ARTIFACT_DIR.glob("*.svg"):
            path.unlink()

    completed = subprocess.run(
        [sys.executable, str(example)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "image/svg+xml" in completed.stdout

    for path in (
        ARTIFACT_DIR / "visualization_artifact.svg",
        ARTIFACT_DIR / "route_map_vehicle_1.svg",
        ARTIFACT_DIR / "route_annotation_vehicle_1.svg",
    ):
        assert path.exists()
        assert "<svg" in path.read_text(encoding="utf-8")
