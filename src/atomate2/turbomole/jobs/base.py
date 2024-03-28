"""Definition of base turbomole job makers."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import turbomoleio.output.files
from custodian import Custodian
from jobflow import Maker, Response, job

from atomate2.turbomole.custodian.jobs import TMJob
from atomate2.turbomole.schemas.task import TaskDocument
from atomate2.turbomole.sets.base import (
    BaseTurbomoleInputGenerator,
)

logger = logging.getLogger(__name__)

__all__ = ["BaseTurbomoleMaker"]


@dataclass
class BaseTurbomoleMaker(Maker):
    """Base Turbomole job maker."""

    input_set_generator: BaseTurbomoleInputGenerator
    tm_exec: str
    name: str = "base turbomole job"
    command_options: list = field(default_factory=list)
    handlers: list = field(default_factory=list)
    validators: list = field(default_factory=list)
    output_cls_str: str = "ScfOutput"

    def __post_init__(self):
        """Set the output_cls based on the output_cls_str."""
        self.output_cls = getattr(turbomoleio.output.files, self.output_cls_str)

    @job
    def make(self, prev_output=None):
        """Create the dscf job."""
        self.input_set_generator.get_input_set(prev_output=prev_output)

        command_options = self.get_command_options()
        custodian_job = TMJob(executable=self.tm_exec, options=command_options)
        custodian = Custodian(
            handlers=self.handlers,
            validators=self.validators,
            jobs=[custodian_job],
        )
        custodian.run()

        # Parse the outputs
        if self.tm_exec == "jobex":
            output_file = "job.last"
        else:
            output_file = custodian_job.output_file
        doc = TaskDocument.from_directory(
            ".", output_file=output_file, output_cls=self.output_cls
        )

        return Response(output=doc)

    def get_command_options(self):
        """Get the options for the Turbomole executable."""
        return self.command_options
