from __future__ import annotations

from dataclasses import dataclass

from py_sprit.presentation.algorithm_execution import AlgorithmExecutionAdapter
from py_sprit.presentation.extension_contracts import ConstraintRegistrationAdapter
from py_sprit.presentation.problem_definition import ProblemDefinitionAdapter
from py_sprit.presentation.solution_visualization import SolutionVisualizationAdapter


@dataclass(slots=True)
class PySpritRuntime:
    problem_definition: ProblemDefinitionAdapter
    extension_contracts: ConstraintRegistrationAdapter
    algorithm_execution: AlgorithmExecutionAdapter
    solution_visualization: SolutionVisualizationAdapter
