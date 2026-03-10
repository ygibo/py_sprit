from __future__ import annotations

import pytest

from py_sprit.bootstrap import create_runtime


@pytest.fixture
def runtime():
    return create_runtime(random_seed=7)
