# Part of atomate2-turbomole package.

"""Pytest configuration: fixtures."""

import os
import shutil
from pathlib import Path

import mongomock
import pytest
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Molecule, Structure

module_dir = Path(__file__).resolve().parent
test_files = module_dir / "testfiles"
TEST_FILES = test_files.resolve()

_REF_PATHS = {}


@pytest.fixture(scope="session")
def test_files():
    return TEST_FILES


@pytest.fixture(scope="session")
def ridft_output():
    return Path(TEST_FILES) / "outputs" / "ridft.out"


@pytest.fixture(scope="session")
def dscf_run_dir():
    return Path(TEST_FILES) / "reference_runs" / "dscf"


@pytest.fixture(scope="session")
def riper_run_dir():
    return Path(TEST_FILES) / "reference_runs" / "riper"


@pytest.fixture(scope="session")
def h2_molecule():
    h2_path = Path(TEST_FILES) / "molecules" / "h2.xyz"
    return Molecule.from_file(str(h2_path.resolve()))


@pytest.fixture(scope="session")
def h2o_molecule():
    h2o_path = Path(TEST_FILES) / "molecules" / "h2o.xyz"
    return Molecule.from_file(str(h2o_path.resolve()))


@pytest.fixture(scope="session")
def mnh2_molecule():
    mnh2_path = Path(TEST_FILES) / "molecules" / "MnH2.xyz"
    return Molecule.from_file(str(mnh2_path.resolve()))


@pytest.fixture(scope="session")
def si_structure():
    si_path = Path(TEST_FILES) / "structures" / "si.cif"
    struct = Structure.from_file(str(si_path.resolve()))
    abc = struct.lattice.abc
    angles = struct.lattice.angles
    lattice = Lattice.from_parameters(*abc, *angles, vesta=True)
    struct.lattice = lattice
    return struct


@pytest.fixture(scope="function")
def mongo_collection():
    return mongomock.MongoClient(
        host="localhost",
        port=1234,
        authSource="results_db",
        user="johndoe",
        password="password",
    )["results_db"]["results_collection"]


@pytest.fixture(scope="session")
def turbomole_integration_tests(pytestconfig):
    return pytestconfig.getoption("turbomole_integration")


@pytest.fixture(scope="function")
def mockornot_turbomole(mocker, test_files, turbomole_integration_tests):
    import atomate2.turbomole.custodian.jobs
    import atomate2.turbomole.jobs.core

    if not turbomole_integration_tests:

        def mock_run_turbomole(*args, **kwargs):
            from jobflow import CURRENT_JOB

            name = CURRENT_JOB.job.name
            ref_path = test_files / _REF_PATHS[name]

            copy_tm_files(ref_path)

        mocker.patch.object(
            atomate2.turbomole.jobs.core.DefineRunner,
            "run_full",
            side_effect=mock_run_turbomole,
        )
        mocker.patch.object(
            atomate2.turbomole.custodian.jobs.TMJob, "run", mock_run_turbomole
        )

    # else:
    #     mocker.spy(turbomole.jobs.core.DefineRunner, "run_full")

    def _run(ref_paths):
        _REF_PATHS.update(ref_paths)

    yield _run

    mocker.stopall()
    _REF_PATHS.clear()


def fake_turbomole_run(ref_path, irun=None):
    if irun is not None:
        ref_path = ref_path[irun]
    copy_tm_files(ref_path=ref_path)


def copy_tm_files(ref_path):
    for fname in os.listdir(ref_path):
        fpath = os.path.join(ref_path, fname)
        if os.path.isfile(fpath):
            shutil.copy(fpath, ".")


def pytest_addoption(parser):
    parser.addoption(
        "--turbomole-integration",
        action="store_true",
        default=False,
        help="Run integration tests for turbomole in turbomole. "
        "This basically runs the same tests but without the mocking.",
    )
