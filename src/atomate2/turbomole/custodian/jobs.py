# Part of atomate2-turbomole package.

"""Module containing the custodian jobs for the atomate2-turbomole package."""

import shlex
import subprocess
from pathlib import Path

from custodian.custodian import Job


class TMJob(Job):
    """A job to run one of the TM executables."""

    def __init__(self, executable, output_file=None, stderr_file=None, options=None):
        """Construct the custodian Job.

        Args:
            executable: Turbomole executable.
            output_file: Filename to use for the stdout.
            stderr_file: Filename to use for the stderr.
            options: Options for jobex (e.g. "-rijk", ["-level", "cc2"], "-time", ...).
        """
        self.executable = executable
        self.output_file = output_file or Path(self.executable).name + ".out"
        self.stderr_file = stderr_file or Path(self.executable).name + ".err"
        if options is None:
            self.options = []
        elif isinstance(options, str):
            self.options = shlex.split(options)
        elif isinstance(options, list):
            self.options = list(options) or []
        else:
            raise TypeError(
                f'"options" should be a string, a list or None, '
                f"while it is {type(options)}"
            )

    def setup(self, directory="./"):
        """Set up the custodian job. Nothing at this stage."""
        pass  # pragma: no cover

    def run(self, directory="./"):
        """
        Run the selected executable.

        Returns
        -------
            a Popen process
        """
        cmd = [self.executable, *self.options]

        with open(self.output_file, "w") as f_out, open(
            self.stderr_file, "w", buffering=1
        ) as f_err:
            p = subprocess.Popen(cmd, stdout=f_out, stderr=f_err)
        return p

    def postprocess(self, directory="./"):
        """Postprocess the custodian job. Nothing at this stage."""
        pass  # pragma: no cover

    @classmethod
    def dscf(cls, **kwargs):
        """Create custodian TMJob for dscf."""
        return cls(executable="dscf", **kwargs)

    @classmethod
    def ridft(cls, **kwargs):
        """Create custodian TMJob for ridft."""
        return cls(executable="ridft", **kwargs)

    @classmethod
    def jobex(cls, jobex_time=True, **kwargs):
        """Create custodian TMJob for jobex."""
        options = kwargs.pop("options", [])
        if isinstance(options, str):
            options = options = shlex.split(options)
        if jobex_time and "-time" not in options:
            options.append("-time")
        if not jobex_time and "-time" in options:
            raise ValueError(
                "Explicitly asked jobex_time=False while -time option is set."
            )
        return cls(executable="jobex", options=options, **kwargs)

    @classmethod
    def ricc2(cls, **kwargs):
        """Create custodian TMJob for ricc2."""
        return cls(executable="ricc2", **kwargs)

    @classmethod
    def riper(cls, **kwargs):
        """Create custodian TMJob for riper."""
        return cls(executable="riper", **kwargs)

    @classmethod
    def statpt(cls, **kwargs):
        """Create custodian TMJob for statpt."""
        return cls(executable="statpt", **kwargs)
