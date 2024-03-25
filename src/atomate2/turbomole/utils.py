# Part of atomate2-turbomole package.

"""Module containing utilities for the atomate2-turbomole package."""

from __future__ import annotations

import re
from datetime import datetime

from monty.json import MSONable
from turbomoleio.input.utils import get_define_template

float_number_re = r"[+-]?[0-9]*[.]?[0-9]+"
timing_re = r"(\d+h|)(\d+m)(" + float_number_re + r"s)"


class JobexTimings(MSONable):
    """Object containing timing information about a jobex run.

    Note: this will be moved and adapted in turbomoleio.
    """

    def __init__(self, steps_timings):
        """Construct JobexTimings.

        Args:
            steps_timings (list): List of the timings for each step.
        """
        self.steps_timings = steps_timings

    @classmethod
    def from_file(cls, filepath="time.stat"):
        """Create JobexTimings from file.

        Args:
            filepath: Path to the "time.stat" file containing timing information.

        Returns
        -------
            JobexTimings instance with the timing information of the jobex calculation.
        """
        with open(filepath) as f:
            string = f.read().strip()

        pattern = (
            r"([\s\S]*?\s+)"  # lazy matching
            r"real\s+"
            + timing_re
            + r"\s+user\s+"
            + timing_re
            + r"\s+sys\s+"
            + timing_re
        )
        match = re.findall(pattern, string)
        steps_timings = []

        for step in match:
            real_t = float(step[3][:-1]) + 60.0 * float(step[2][:-1])
            if step[1]:
                real_t += 3600.0 * float(step[1][:-1])
            user_t = float(step[6][:-1]) + 60.0 * float(step[5][:-1])
            if step[4]:
                user_t += 3600.0 * float(step[4][:-1])
            sys_t = float(step[9][:-1]) + 60.0 * float(step[8][:-1])
            if step[7]:
                sys_t += 3600.0 * float(step[7][:-1])

            sp = [line.strip() for line in step[0].strip().splitlines()]
            if len(sp) == 1:
                details = None
            elif len(sp) == 2:
                details = sp[1]
            else:
                raise RuntimeError(
                    "More than two time.stat lines for a given jobex step"
                )
            step_type = sp[0]
            steps_timings.append(
                {
                    "step": step_type,
                    "details": details,
                    "real": real_t,
                    "user": user_t,
                    "sys": sys_t,
                }
            )
        return cls(steps_timings=steps_timings)

    def total_time(self, time="real", step=None):
        """Get the total time.

        Args:
            time: Which type of time to use.
            step: Which type of step to use.

        Returns
        -------
            float: Time used in seconds.
        """
        if step is not None:
            return sum([s[time] for s in self.steps_timings if s["step"] == step])
        return sum([s[time] for s in self.steps_timings])


def get_define_parameters(define_template=None, define_parameters=None):
    """Get the define parameters based on a template and additional define parameters.

    Args:
        define_template: Name of template to use as basis for define parameters.
        define_parameters: Parameters for turbomoleio's DefineRunner.
    """
    if define_template is None and define_parameters is None:
        raise RuntimeError(
            'Should provide at least one of "define_template" or "define_parameters"'
        )
    dp = get_define_template(define_template) if define_template else {}
    if define_parameters:
        dp.update(define_parameters)
    return dp


def datetime_str() -> str:
    """
    Get a string representation of the current time.

    Returns
    -------
    str
        The current time.
    """
    return str(datetime.utcnow())
