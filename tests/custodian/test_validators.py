# Part of atomate2-turbomole package.

"""Tests of the validators in the atomate2-turbomole package."""

import os
import shutil

from atomate2.turbomole.custodian.validators import (
    JobexGeoOptConvergedValidator,
    NormalEndValidator,
    ScfConvergedValidator,
)
from monty.tempfile import ScratchDir


def test_jbx_validator():
    jbx_validator = JobexGeoOptConvergedValidator()
    with ScratchDir("."):
        with open("GEO_OPT_CONVERGED", "w") as f:
            f.write("converged")
        assert jbx_validator.check() is False

    with ScratchDir("."):
        with open("GEO_OPT_RUNNING", "w") as f:
            f.write("running")
        assert jbx_validator.check() is True

    with ScratchDir("."):
        assert jbx_validator.check() is True


def test_normalend_validator(test_files):
    normalend_validator = NormalEndValidator(out_file="ridft.out")
    with ScratchDir("."):
        assert normalend_validator.check() is True

    with ScratchDir("."):
        shutil.copy(os.path.join(test_files, "outputs", "ridft.out"), ".")
        assert normalend_validator.check() is False

    with ScratchDir("."):
        shutil.copy(
            os.path.join(test_files, "outputs", "ridft_stopped.out"), "ridft.out"
        )
        assert normalend_validator.check() is True


def test_scfconv_validator(test_files):
    scfconv_validator = ScfConvergedValidator(output_file="ridft.out")
    with ScratchDir("."):
        assert scfconv_validator.check() is True

    with ScratchDir("."):
        shutil.copy(os.path.join(test_files, "outputs", "ridft.out"), ".")
        assert scfconv_validator.check() is False

    with ScratchDir("."):
        shutil.copy(
            os.path.join(test_files, "outputs", "ridft_unconverged.out"), "ridft.out"
        )
        assert scfconv_validator.check() is True

    scfconv_validator = ScfConvergedValidator(output_file="riper.out")
    with ScratchDir("."):
        assert scfconv_validator.check() is True

    with ScratchDir("."):
        shutil.copy(os.path.join(test_files, "outputs", "riper.out"), ".")
        assert scfconv_validator.check() is False

    with ScratchDir("."):
        shutil.copy(
            os.path.join(test_files, "outputs", "riper_unconverged.out"), "riper.out"
        )
        assert scfconv_validator.check() is True
