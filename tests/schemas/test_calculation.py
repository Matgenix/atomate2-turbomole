# Part of atomate2-turbomole package.

"""Tests of the schemas calculations in the atomate2-turbomole package."""

import pytest
from pydantic import ValidationError

from atomate2.turbomole.schemas.calculation import Calculation


def test_Calculation() -> None:
    calc = Calculation(dir_name="/tmp")
    assert isinstance(calc, Calculation)

    # the number of run_type are limited
    with pytest.raises(ValidationError):
        Calculation(run_type="Unknown")
