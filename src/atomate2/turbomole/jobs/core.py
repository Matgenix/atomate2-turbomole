"""Definition of core Turbomole job makers."""

import copy
import os
import shutil
from dataclasses import dataclass, field

from jobflow import Maker, Response, job
from monty.os import cd, makedirs_p
from turbomoleio import DefineRunner, MoleculeSystem
from turbomoleio.core.control import cdg, mdgo, sdg

from atomate2.turbomole.custodian.validators import (
    JobexGeoOptConvergedValidator,
    ScfConvergedValidator,
)
from atomate2.turbomole.jobs.base import BaseTurbomoleMaker
from atomate2.turbomole.schemas.task import DefineTaskDocument
from atomate2.turbomole.sets.core import (
    BaseTurbomoleInputGenerator,
    TurbomoleDefineInputGenerator,
    TurbomoleInputGenerator,
)


@dataclass
class DefineMaker(Maker):
    """Base maker for Turbomole's define jobs."""

    input_set_generator: TurbomoleDefineInputGenerator = field(
        default_factory=lambda: TurbomoleDefineInputGenerator(define_template="ridft")
    )
    name: str = "define"
    metric_options = (3, 2, 1, -1, -2, -3)
    define_timeout = 5

    @classmethod
    def from_define_template(cls, define_template, define_parameters=None):
        """Initialize the define maker using a define template."""
        # TODO: allow tuning the rest also ?
        define_parameters = define_parameters or {}
        return cls(
            TurbomoleDefineInputGenerator(
                define_template=define_template, define_parameters=define_parameters
            )
        )

    @job
    def make(self, system, charge=None, unpaired_electrons=None):
        """Create define job for a given system.

        Parameters
        ----------
        system
            either a pymatgen Molecule or Structure or a
            turbomoleio MoleculeSystem or PeriodicSystem.
        charge
            charge of the system.
        unpaired_electrons
            number of unpaired electrons.

        Returns
        -------
            a jobflow Job to run define with the desired options for the given system,
            charge and number of unpaired electrons.
        """
        dis = self.input_set_generator.get_input_set(
            system, charge=charge, unpaired_electrons=unpaired_electrons
        )
        if not isinstance(dis.system, MoleculeSystem):
            raise NotImplementedError()

        # Run define
        try:
            self.run_define(define_input_set=dis)
        except RuntimeError:  # pragma: no cover (tricky to test)
            return Response(stop_jobflow=True)

        # Update datagroups and functional
        self.update_datagroups_functional(
            datagroups=dis.datagroups, functional=dis.xc_func
        )

        # Parse the outputs
        doc = DefineTaskDocument.from_directory(".")

        return Response(output=doc)

    def run_define(self, define_input_set):
        """Run define."""
        define_parameters = define_input_set.define_parameters
        dr_succeeded = False
        define_parameters = copy.deepcopy(define_parameters)

        for metric in self.metric_options:  # pragma: no branch (trivial)
            metric_dir = f"define_metric_{metric}"
            makedirs_p(metric_dir)
            try:
                with cd(metric_dir):
                    define_input_set.write_input(directory=".")
                    define_parameters["metric"] = metric
                    dr = DefineRunner(parameters=define_parameters, timeout=60)
                    dr.run_full()
                dr_succeeded = True
            except BaseException:  # pragma: no cover (tricky)
                pass

            if dr_succeeded:  # pragma: no branch (trivial)
                # Move the files of the succeeded define run to the main directory
                files = os.listdir(metric_dir)
                for f in files:
                    if os.path.exists(f):  # pragma: no cover (tricky)
                        raise FileExistsError(
                            f'Will not copy "{f}" file as it already exists.'
                        )
                    shutil.move(os.path.join(metric_dir, f), f)
                break

        if not dr_succeeded:  # pragma: no cover (tricky)
            raise RuntimeError(
                "Running define went wrong with all the different metrics."
            )

        return metric

    def update_datagroups_functional(self, datagroups, functional):
        """Update the datagroups and functional."""
        if datagroups:  # pragma: no cover (trivial)
            for dg, db in datagroups.items():
                cdg(dg, db)

        # Setup exchange-correlation functional
        if functional:  # pragma: no branch (trivial)
            if functional == "b97m-v":  # pragma: no cover (trivial)
                mdgo("dft", {"functional": "functional libxc 254"})
            else:
                mdgo("dft", {"functional": f"functional {functional}"})
            # DO the Self-Consistent Non-Local (doscnl) density-based
            # vanderwaals corrections. This is needed to compute the gradients.
            if functional in [  # pragma: no cover (trivial)
                "wb97x-v",
                "wb97m-v",
                "b97m-v",
            ]:
                cdg("doscnl", "")


@dataclass
class DscfMaker(BaseTurbomoleMaker):
    """Base maker for dscf jobs."""

    input_set_generator: BaseTurbomoleInputGenerator = field(
        default_factory=TurbomoleInputGenerator
    )
    tm_exec: str = "dscf"
    name: str = "dscf"
    handlers: list = field(default_factory=list)
    validators: list = field(
        default_factory=lambda: [ScfConvergedValidator(output_file="dscf.out")]
    )


@dataclass
class RidftMaker(BaseTurbomoleMaker):
    """Base maker for ridft jobs."""

    input_set_generator: BaseTurbomoleInputGenerator = field(
        default_factory=TurbomoleInputGenerator
    )
    tm_exec: str = "ridft"
    name: str = "ridft"
    handlers: list = field(default_factory=list)
    validators: list = field(
        default_factory=lambda: [ScfConvergedValidator(output_file="ridft.out")]
    )


@dataclass
class RiperMaker(BaseTurbomoleMaker):
    """Base maker for riper jobs."""

    input_set_generator: BaseTurbomoleInputGenerator = field(
        default_factory=TurbomoleInputGenerator
    )
    tm_exec: str = "riper"
    name: str = "riper"
    handlers: list = field(default_factory=list)
    validators: list = field(
        default_factory=lambda: [ScfConvergedValidator(output_file="riper.out")]
    )


@dataclass
class JobexMaker(BaseTurbomoleMaker):
    """Base maker for jobex jobs."""

    input_set_generator: BaseTurbomoleInputGenerator = field(
        default_factory=TurbomoleInputGenerator
    )
    tm_exec: str = "jobex"
    name: str = "jobex"
    command_options: list = field(default_factory=list)
    handlers: list = field(default_factory=list)
    validators: list = field(default_factory=lambda: [JobexGeoOptConvergedValidator()])
    max_cycles: int = 100
    output_cls_str: str = "JobexOutput"

    def get_command_options(self):  # pragma: no cover (to be done)
        """Get the options for the jobex executable."""
        command_options = list(self.command_options)
        rij = sdg("rij")
        if rij is not None:
            command_options.append("-ri")
        rik = sdg("rik")
        if rik is not None:
            command_options.append("-rijk")
        if self.max_cycles is not None:
            command_options.extend(["-c", f"{self.max_cycles}"])
        periodic = sdg("periodic")
        if periodic is not None:
            if int(periodic.strip()) in (1, 2, 3):
                command_options.append("-riper")
            else:
                raise ValueError(
                    "periodic should not be present in the control file "
                    "or be one of 1, 2 or 3."
                )
        return command_options
