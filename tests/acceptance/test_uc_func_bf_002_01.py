"""Traceability:
- related_func: FUNC-BF-002-01
- feature: docs/usecases/function/problem_definition/UC-FUNC-BF-002-01_問題モデル入力を確認する.feature
"""

from __future__ import annotations

from tests.support import make_problem_inputs


def test_必要な構成要素が揃っているため入力確認が完了する(runtime):
    result = runtime.problem_definition.confirm_problem_model_inputs(**make_problem_inputs())
    assert result.is_success is True
    assert result.next_state is not None


def test_必要情報が不足しているため不足内容を確認する(runtime):
    result = runtime.problem_definition.confirm_problem_model_inputs(
        **make_problem_inputs(job_count=0)
    )
    assert result.is_success is False
    assert result.reason == "必要情報が不足している"
