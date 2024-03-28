import pytest
from pydantic import ValidationError

from atomate2.turbomole.schemas.task import InputSummary, TaskDocument


def test_InputSummary(si_structure) -> None:
    inp_summ = InputSummary()

    assert inp_summ.structure is None
    assert inp_summ.xc is None

    with pytest.raises(ValidationError):
        InputSummary(structure=123)

    """trying to do something meaningful here
    inp_summ_si = InputSummary(structure=si_structure)
    """


def test_from_directory_arguments(ridft_output) -> None:
    """2 required positional arguments: dir_name and output_file"""
    with pytest.raises(TypeError):
        TaskDocument.from_directory()

    """missing control file"""
    with pytest.raises(FileNotFoundError):
        TaskDocument.from_directory(dir_name="/tmp", output_file=ridft_output)


def test_from_directory_molecule(dscf_run_dir) -> None:
    TaskDocument.from_directory(dir_name=dscf_run_dir, output_file="dscf.out")


@pytest.mark.skip(
    reason="Turbomoleio issue #39 " "PeriodicSystems from file does not work"
)
def test_from_directory_structure(riper_run_dir) -> None:
    TaskDocument.from_directory(dir_name=riper_run_dir, output_file="riper.out")
