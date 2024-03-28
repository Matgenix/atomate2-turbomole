# Part of atomate2-turbomole package.

"""Tests of the custodian jobs in the atomate2-turbomole package."""

import subprocess

import pytest
from monty.tempfile import ScratchDir

import atomate2.turbomole.custodian.jobs
from atomate2.turbomole.custodian.jobs import TMJob


def test_tm_job():
    job = TMJob("/some/fake/executable")
    assert job.executable == "/some/fake/executable"
    assert job.output_file == "executable.out"
    assert job.stderr_file == "executable.err"
    assert isinstance(job.options, list)

    job = TMJob("/some/fake/executable", output_file="myoutput.out")
    assert job.executable == "/some/fake/executable"
    assert job.output_file == "myoutput.out"
    assert job.stderr_file == "executable.err"
    assert isinstance(job.options, list)

    job = TMJob(
        "/some/fake/executable", stderr_file="myerr.err", options="-ri abc -time"
    )
    assert job.executable == "/some/fake/executable"
    assert job.output_file == "executable.out"
    assert job.stderr_file == "myerr.err"
    assert isinstance(job.options, list)
    assert job.options == ["-ri", "abc", "-time"]
    with pytest.raises(TypeError):
        TMJob(executable="/some/fake/executable", options=5)


@pytest.mark.parametrize("tm_exec", ["dscf", "ridft", "ricc2", "riper", "statpt"])
def test_tm_job_clsmethods(mocker, tm_exec):
    mock = mocker.patch.object(
        atomate2.turbomole.custodian.jobs, "subprocess", autospec=True
    )
    mock.reset_mock()
    jb_clsmethod = getattr(TMJob, tm_exec)
    jb = jb_clsmethod()
    with ScratchDir("."):
        p = jb.run()
        assert isinstance(p, subprocess.Popen)
    mock.Popen.assert_called_once()

    jb = jb_clsmethod(options="-proper")
    assert len(jb.options) == 1
    assert "-proper" in jb.options

    jb = jb_clsmethod(options=["-opt", "optabc"])
    assert len(jb.options) == 2
    assert "-opt" in jb.options
    assert "optabc" in jb.options

    with pytest.raises(TypeError):
        jb_clsmethod(options=5)


def test_tm_job_jobex(mocker):
    mock = mocker.patch.object(
        atomate2.turbomole.custodian.jobs, "subprocess", autospec=True
    )
    job = TMJob.jobex()
    assert job.options == ["-time"]
    job = TMJob.jobex(jobex_time=True, options=["-time"])
    assert job.options == ["-time"]
    job = TMJob.jobex(jobex_time=True, options="-time")
    assert job.options == ["-time"]
    with pytest.raises(
        ValueError,
        match=r"Explicitly asked jobex_time=False while -time option is set.",
    ):
        TMJob.jobex(jobex_time=False, options="-time")
    job = TMJob.jobex(options="-rijk")
    assert set(job.options) == {"-time", "-rijk"}

    with ScratchDir("."):
        p = job.run()
        assert isinstance(p, subprocess.Popen)
    mock.Popen.assert_called_once()

    job = TMJob.jobex(jobex_time=False, options=["-level", "cc2"])
    assert "-time" not in job.options
    assert "-level" in job.options
    assert "cc2" in job.options

    with pytest.raises(TypeError):
        TMJob.jobex(options=5)
