import json
from pathlib import Path

import jobflow
import numpy as np
import pytest
from jobflow import run_locally
from monty.serialization import MontyDecoder, MontyEncoder
from monty.tempfile import ScratchDir
from turbomoleio.core.control import Energy

from atomate2.turbomole.jobs.core import DefineMaker, DscfMaker
from atomate2.turbomole.sets.core import TurbomoleDefineInputGenerator


def test_jobs():
    # Make sure the make methods return a jobflow.Job object
    for job_maker_cls in (
        DefineMaker,
        DscfMaker,
    ):
        # Note that the signature of the job functions is not "correct" here.
        # Indeed, the job decorator does not check that the arguments are correct
        # This might change in the future in jobflow.
        # For now this is sufficient here as we only check that we indeed
        # get a Job object.
        m = job_maker_cls()
        assert isinstance(m.make(), jobflow.Job)


def test_define_maker_001(mockornot_turbomole, h2_molecule):
    define_maker = DefineMaker()
    assert define_maker.input_set_generator.define_template == "ridft"
    assert define_maker.input_set_generator.define_parameters == {}
    define_job = define_maker.make(h2_molecule)

    mockornot_turbomole(
        {"define": "jobs/define_maker_001/job_2023-05-11-10-14-21-911069-54300"}
    )

    with ScratchDir("."):
        outputs = run_locally(define_job, create_folders=True)
        run_path = Path(outputs[define_job.uuid][1].output.dir_name)
        coord_path = run_path / "coord"
        assert coord_path.exists()
        with open(coord_path) as f:
            coord_lines = f.read().splitlines()
            read_coords = np.empty((2, 3))
            read_coords[0] = coord_lines[1].split()[0:3]
            read_coords[1] = coord_lines[2].split()[0:3]
            true_coords = np.array(
                [
                    [0.0, 0.0, -0.69919866611153],
                    [0.0, 0.0, 0.69919866611153],
                ]
            )
            assert np.allclose(read_coords, true_coords, 1e-6, 1e-9)
            assert coord_lines[1].split()[3] == "h"
            assert coord_lines[2].split()[3] == "h"
        with open(run_path / "control") as f:
            control_string = f.read()
            assert "functional b-p" in control_string
            assert "$rij" in control_string


def test_define_maker_002(mockornot_turbomole, h2_molecule):
    define_maker = DefineMaker.from_define_template(
        "dscf", define_parameters={"functional": "pbe"}
    )
    assert define_maker.input_set_generator.define_template == "dscf"
    assert define_maker.input_set_generator.define_parameters == {"functional": "pbe"}
    define_job = define_maker.make(h2_molecule)

    mockornot_turbomole(
        {"define": "jobs/define_maker_002/job_2023-05-11-12-44-35-468615-49328"}
    )

    with ScratchDir("."):
        outputs = run_locally(define_job, create_folders=True)
        run_path = Path(outputs[define_job.uuid][1].output.dir_name)
        with open(run_path / "control") as f:
            control_string = f.read()
            assert "functional pbe" in control_string
            assert "$rij" not in control_string


def test_dscf_maker_001(test_files, mockornot_turbomole, h2_molecule):
    dscf_maker = DscfMaker()
    dscf_json_string = json.dumps(dscf_maker, cls=MontyEncoder)
    dscf_maker_from_json = json.loads(dscf_json_string, cls=MontyDecoder)
    assert dscf_maker_from_json == dscf_maker
    define_path = (
        test_files / "jobs/define_maker_002/job_2023-05-11-12-44-35-468615-49328"
    )
    dscf_job = dscf_maker.make(prev_output=define_path)

    mockornot_turbomole(
        {"dscf": "jobs/dscf_maker_001/job_2023-05-11-13-08-14-583157-21573"}
    )

    with ScratchDir("."):
        outputs = run_locally(dscf_job, create_folders=True)
        run_path = Path(outputs[dscf_job.uuid][1].output.dir_name)
        energy_path = run_path / "energy"
        assert energy_path.exists()
        energy = Energy.from_file(energy_path)
        assert energy.n_steps == 1
        assert energy.total == pytest.approx(-1.157417569358)


def test_missing_template(h2_molecule):
    """TODO: take a decision whether to validate the values for define_templates"""
    tm_dig = TurbomoleDefineInputGenerator(define_template="missing_template")
    with pytest.raises(ValueError):
        tm_dig.get_input_set(system=h2_molecule)
