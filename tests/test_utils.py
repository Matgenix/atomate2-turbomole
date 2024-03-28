# Part of atomate2-turbomole package.

"""Tests of the utility functions in the atomate2-turbomole package."""

import os

import pytest

from atomate2.turbomole.utils import JobexTimings, get_define_parameters


def test_jbx_timings(test_files):
    # time.stat file from "jobex -riper -time" (relaxation with riper,
    # i.e. periodic system)
    jbx_timings = JobexTimings.from_file(
        os.path.join(test_files, "jobex", "time.stat_riper")
    )
    assert len(jbx_timings.steps_timings) == 7
    assert jbx_timings.steps_timings[0]["step"] == "scf_energy"
    assert jbx_timings.steps_timings[0]["details"] is None
    assert jbx_timings.steps_timings[3]["step"] == "statpt"
    assert jbx_timings.steps_timings[3]["details"] == "statpt ended normally"
    assert jbx_timings.total_time() == pytest.approx(1.089)
    assert jbx_timings.total_time(time="real") == pytest.approx(1.089)
    assert jbx_timings.total_time(time="user") == pytest.approx(1.032)
    assert jbx_timings.total_time(time="sys") == pytest.approx(0.045)
    assert jbx_timings.total_time(time="sys", step="nonexistent") == pytest.approx(0.0)
    assert jbx_timings.total_time(time="real", step="scf_energy") == pytest.approx(
        1.044
    )
    assert jbx_timings.total_time(time="user", step="statpt") == pytest.approx(0.034)

    # time.stat file from "jobex -ri -level cc2 -time" (relaxation with MP2)
    jbx_timings = JobexTimings.from_file(
        os.path.join(test_files, "jobex", "time.stat_mp2")
    )
    assert jbx_timings.steps_timings[0]["user"] == pytest.approx(1030.948)
    assert jbx_timings.total_time() == pytest.approx(491.805)
    assert jbx_timings.total_time("user") == pytest.approx(2595.512)
    assert len(jbx_timings.steps_timings) == 7

    # time.stat file from standard "jobex -time" (relaxation with dscf)
    jbx_timings = JobexTimings.from_file(
        os.path.join(test_files, "jobex", "time.stat_dscf")
    )
    assert len(jbx_timings.steps_timings) == 7
    assert jbx_timings.total_time(step="scf_energy") == pytest.approx(0.531)

    # fake time.stat file with hours
    jbx_timings = JobexTimings.from_file(
        os.path.join(test_files, "jobex", "time.stat_hours")
    )
    assert len(jbx_timings.steps_timings) == 3
    assert jbx_timings.total_time(step="scf_energy") == pytest.approx(12926.528)
    assert jbx_timings.total_time(time="user", step="scf_energy") == pytest.approx(
        454320.507
    )
    assert jbx_timings.total_time(time="sys", step="statpt") == pytest.approx(
        136800.002
    )

    # fake time.stat with more than 2 lines for the step type and details
    with pytest.raises(
        RuntimeError, match=r"More than two time\.stat lines for a given jobex step"
    ):
        JobexTimings.from_file(os.path.join(test_files, "jobex", "time.stat_raise"))


def test_get_define_parameters():
    with pytest.raises(
        RuntimeError,
        match=r"Should provide at least one of "
        r'"define_template" or "define_parameters"',
    ):
        get_define_parameters(define_template=None, define_parameters=None)
