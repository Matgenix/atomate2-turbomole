# # Part of turbomole package.
#
# """Tests of the custodian jobs in the turbomole package."""
#
# import subprocess
#
# import pytest
# from monty.tempfile import ScratchDir
#
# import turbomole.custodian_jobs
# from turbomole.custodian_jobs import Dscf, Jobex, Ricc2, Ridft, Riper, Statpt
#
#
# def test_jbx_job(mocker):
#     mock = mocker.patch.object(turbomole.custodian_jobs, "subprocess", autospec=True)
#     job = Jobex()
#     assert job.options == ["-time"]
#     job = Jobex(jobex_time=True, options=["-time"])
#     assert job.options == ["-time"]
#     job = Jobex(jobex_time=True, options="-time")
#     assert job.options == ["-time"]
#     job = Jobex(options="-rijk")
#     assert "-time" in job.options
#     assert "-rijk" in job.options
#     with ScratchDir("."):
#         p = job.run()
#         assert isinstance(p, subprocess.Popen)
#     mock.Popen.assert_called_once()
#
#     job = Jobex(jobex_time=False, options=["-level", "cc2"])
#     assert "-time" not in job.options
#     assert "-level" in job.options
#     assert "cc2" in job.options
#
#     with pytest.raises(TypeError):
#         Jobex(options=5)
#
#     for jb_cls in [
#         Ridft,
#         Riper,
#         Dscf,
#         Ricc2,
#         Statpt,
#     ]:
#         mock.reset_mock()
#         jb = jb_cls()
#         with ScratchDir("."):
#             p = jb.run()
#             assert isinstance(p, subprocess.Popen)
#         mock.Popen.assert_called_once()
#
#         jb = jb_cls(options="-proper")
#         assert len(jb.options) == 1
#         assert "-proper" in jb.options
#
#         jb = jb_cls(options=["-opt", "optabc"])
#         assert len(jb.options) == 2
#         assert "-opt" in jb.options
#         assert "optabc" in jb.options
#
#         with pytest.raises(TypeError):
#             jb_cls(options=5)
