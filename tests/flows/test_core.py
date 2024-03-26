import pytest
from atomate2.turbomole.flows.core import JobexFlowMaker, ScfFlowMaker
from atomate2.turbomole.jobs.core import JobexMaker
from atomate2.turbomole.schemas.task import DefineTaskDocument, TaskDocument
from jobflow import run_locally
from jobflow.core.flow import Flow
from jobflow.core.job import Job
from monty.tempfile import ScratchDir


def test_dscf_flow_maker_001(mockornot_turbomole, h2_molecule):
    maker = ScfFlowMaker.dscf()
    flow = maker.make(h2_molecule)
    uuids = {job.name: job.uuid for job, _ in flow.iterflow()}
    assert len(flow.jobs) == len(uuids)

    mockornot_turbomole(
        {
            "define": "flows/dscf_flow_maker_001/job_2023-05-11-13-50-22-250262-49728",
            "dscf": "flows/dscf_flow_maker_001/job_2023-05-11-13-50-22-323205-41682",
        }
    )

    with ScratchDir("."):
        outputs = run_locally(flow, create_folders=True)
        assert len(outputs) == 2
        assert isinstance(outputs[uuids["define"]][1].output, DefineTaskDocument)
        assert isinstance(outputs[uuids["dscf"]][1].output, TaskDocument)


def test_ScfFlowMaker_no_prev_output(mnh2_molecule, si_structure) -> None:
    """
    With no previous output is provided,
    flow is a list of two jobs = ['define', 'dscf/ridft/riper']
    """

    dscf_flow = ScfFlowMaker.dscf().make(mnh2_molecule)

    assert isinstance(dscf_flow, Flow)
    assert len(dscf_flow.jobs) == 2
    assert all([isinstance(k, Job) for k in dscf_flow.jobs])
    assert dscf_flow.jobs[0].name == "define"
    assert dscf_flow.jobs[1].name == "dscf"

    ridft_flow = ScfFlowMaker.ridft().make(mnh2_molecule)

    assert isinstance(ridft_flow, Flow)
    assert len(ridft_flow.jobs) == 2
    assert all([isinstance(k, Job) for k in ridft_flow.jobs])
    assert ridft_flow.jobs[0].name == "define"
    assert ridft_flow.jobs[1].name == "ridft"

    riper_flow = ScfFlowMaker.riper().make(si_structure)

    assert isinstance(riper_flow, Flow)
    assert len(riper_flow.jobs) == 2
    assert all([isinstance(k, Job) for k in riper_flow.jobs])
    assert riper_flow.jobs[0].name == "define"
    assert riper_flow.jobs[1].name == "riper"


def test_ScfFlowMaker_yes_prev_output(mnh2_molecule) -> None:
    """
    When a previous output is provided, flow is a list of one job = ['dscf']
    """
    flow = ScfFlowMaker.dscf().make(mnh2_molecule, prev_output=1)
    assert isinstance(flow, Flow)
    assert len(flow.jobs) == 1
    assert [isinstance(flow.jobs[0], Job)]
    assert flow.jobs[0].name == "dscf"

    # I would like to test
    # dscf_job.prev_output == 1


def test_jobex_flow_maker_001(mockornot_turbomole, h2_molecule):
    maker = JobexFlowMaker.ridft()
    flow = maker.make(h2_molecule)
    uuids = {job.name: job.uuid for job, _ in flow.iterflow()}
    assert len(flow.jobs) == 2
    assert len(uuids) == 3

    define_output = "flows/jobex_maker/001_ridft/job_2024-03-26-10-34-15-427047-27808"
    ridft_output = "flows/jobex_maker/001_ridft/job_2024-03-26-10-34-15-508771-53106"
    jobex_output = "flows/jobex_maker/001_ridft/job_2024-03-26-10-34-15-582116-20073"
    mockornot_turbomole(
        {
            "define": define_output,
            "ridft": ridft_output,
            "jobex": jobex_output,
        }
    )

    with ScratchDir("."):
        outputs = run_locally(flow, create_folders=True)
        # pp.pprint(outputs.keys())
        # pp.pprint(outputs.values())
        # pp.pprint(outputs[uuids["define"]][1].output)
        # pp.pprint(outputs[uuids["riper"]][1].output)
        # pp.pprint(outputs[uuids["dscf"]][1].output)

        assert len(outputs) == 3
        assert isinstance(outputs[uuids["define"]][1].output, DefineTaskDocument)
        assert isinstance(outputs[uuids["ridft"]][1].output, TaskDocument)
        assert isinstance(outputs[uuids["jobex"]][1].output, TaskDocument)


def test_periodicity(h2_molecule, si_structure) -> None:
    """
    Test whether the right error is raised in case of mistake
    pymatgen.molecule/turbomoleio.molecule_system -> can use only dscf and ridft
    pymatgen.structure/turbomoleio.periodic_system -> can use only riper
    """

    # Test ScfFlowMaker
    with pytest.raises(RuntimeError):
        ScfFlowMaker.dscf().make(si_structure)

    with pytest.raises(RuntimeError):
        ScfFlowMaker.ridft().make(si_structure)

    with pytest.raises(RuntimeError):
        ScfFlowMaker.riper().make(h2_molecule)

    # Test JobexFlowMaker
    with pytest.raises(RuntimeError):
        JobexFlowMaker.dscf().make(si_structure)

    with pytest.raises(RuntimeError):
        JobexFlowMaker.ridft().make(si_structure)

    with pytest.raises(RuntimeError):
        JobexFlowMaker.riper().make(h2_molecule)


def test_JobexFlowMaker_max_cycles() -> None:
    jfm = JobexFlowMaker()
    assert jfm.jobex_maker.max_cycles == 1000
    jfm = JobexFlowMaker(max_cycles=500)
    assert jfm.jobex_maker.max_cycles == 500
    jfm = JobexFlowMaker(jobex_maker=JobexMaker(max_cycles=100))
    assert jfm.jobex_maker.max_cycles == 100
    jfm = JobexFlowMaker(jobex_maker=JobexMaker(max_cycles=100), max_cycles=200)
    assert jfm.jobex_maker.max_cycles == 200


def test_JobexFlowMaker_no_prev_output(mnh2_molecule) -> None:
    """
    When no previous output is provided, and no pre-scf job is required
    by the user, the JobexFlow is a list of
    two jobs: define and jobex
    """

    jobex_flow = JobexFlowMaker.dscf(pre_scf=False).make(mnh2_molecule)

    assert isinstance(jobex_flow, Flow)
    assert len(jobex_flow.jobs) == 2
    assert all([isinstance(k, Job) for k in jobex_flow.jobs])
    assert jobex_flow.jobs[0].name == "define"
    assert jobex_flow.jobs[1].name == "jobex"


"""
    ridft_flow = JobexFlowMaker.ridft().make(mnh2_molecule)

    assert isinstance(ridft_flow, Flow)
    assert len(ridft_flow.jobs) == 2
    assert all([isinstance(k, Job) for k in ridft_flow.jobs])
    assert ridft_flow.jobs[0].name == "define"
    assert ridft_flow.jobs[1].name == "ridft"

    riper_flow = JobexFlowMaker.riper().make(mnh2_molecule)

    assert isinstance(riper_flow, Flow)
    assert len(riper_flow.jobs) == 2
    assert all([isinstance(k, Job) for k in riper_flow.jobs])
    assert riper_flow.jobs[0].name == "define"
    assert riper_flow.jobs[1].name == "riper"
"""
