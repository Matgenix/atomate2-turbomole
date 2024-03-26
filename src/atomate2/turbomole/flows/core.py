"""Definition of core Turbomole flow makers."""
from dataclasses import dataclass, field
from typing import Optional, Union

from atomate2.turbomole.jobs.core import (
    DefineMaker,
    DscfMaker,
    JobexMaker,
    RidftMaker,
    RiperMaker,
)
from jobflow import Flow, Maker
from pymatgen.core.structure import Molecule, Structure
from turbomoleio.core.molecule import MoleculeSystem
from turbomoleio.core.periodic import PeriodicSystem


def check_periodicity_consistence(
    scf_maker: Union[DscfMaker, RidftMaker, RiperMaker] = None,
    system: Union[Molecule, MoleculeSystem, Structure, PeriodicSystem] = None,
):
    """Check the system periodicity and the consistency of the maker.

    If system is Molecule or MoleculeSystem, self.scf_maker can only be Dscf or Ridft,
    else if system is a Structure or a PeriodicSystem, self.scf_maker must be Riper.

    Args:
        scf_maker: maker object from atomate2-turbomole
        system: pymatgen Molecule/Structure object or turbomoleio
            MoleculeSystem/PeriodicSystem object.

    Return:
        None
    """
    if isinstance(system, (Molecule, MoleculeSystem)):
        if not isinstance(scf_maker, (DscfMaker, RidftMaker)):
            raise RuntimeError(
                "Inconsistent choice for make() in your Flow:\n"
                "scf_maker for Molecule/MoleculeSystem\n"
                "must be DscfMaker or RidftMaker.\n"
                f"Here the scf_maker is:\n{scf_maker}"
            )
    elif isinstance(system, (Structure, PeriodicSystem)):  # pragma: no branch (trivial)
        if not isinstance(scf_maker, RiperMaker):
            raise RuntimeError(
                "Inconsistent choice for make() in your Flow:\n"
                "scf_maker for Structure/PeriodicSystem\n"
                "must be RiperMaker.\n"
                f"Here the scf_maker is:\n{scf_maker}"
            )
    else:  # pragma: no cover (trivial)
        raise RuntimeError(
            "System can only be Molecule, MoleculeSystem,"
            "Structure or PeriodicSystem.\n"
            f"Here the system is of type {type(system)}"
        )


@dataclass
class ScfFlowMaker(Maker):
    """
    Maker for a define + scf flow.

    Args:
        define_maker: Maker for define.
        scf_maker: Maker for dscf/ridft/riper job.
    """

    name: str = "Scf Flow Maker"
    define_maker: DefineMaker = field(
        default_factory=lambda: DefineMaker.from_define_template("ridft")
    )
    scf_maker: Union[DscfMaker, RidftMaker, RiperMaker] = field(
        default_factory=lambda: RidftMaker()
    )

    def make(
        self,
        system,
        charge=None,
        unpaired_electrons=None,
        prev_output=None,
    ):
        """
        Make a define+scf flow.

        Parameters
        ----------
        system
            either a pymatgen Molecule or Structure or a
            turbomoleio MoleculeSystem or PeriodicSystem.
        charge
            charge of the system.
        unpaired_electrons
            number of unpaired electrons.
        prev_output
            a previous output to start from.

        Returns
        -------
            Flow: jobflow Flow performing define and scf sequentially.
        """
        check_periodicity_consistence(self.scf_maker, system)

        if prev_output is None:
            define_job = self.define_maker.make(
                system, charge=charge, unpaired_electrons=unpaired_electrons
            )
            scf_job = self.scf_maker.make(prev_output=define_job.output.dir_name)
            jobs = [define_job, scf_job]
        else:
            scf_job = self.scf_maker.make(prev_output=prev_output)
            jobs = [scf_job]

        flow = Flow(jobs, output=scf_job.output)
        return flow

    @classmethod
    def dscf(cls, define_parameters=None, **kwargs):
        """Create Scf flow using dscf."""
        return cls(
            define_maker=DefineMaker.from_define_template(
                "dscf", define_parameters=define_parameters
            ),
            scf_maker=DscfMaker(),
            **kwargs,
        )

    @classmethod
    def ridft(cls, define_parameters=None, **kwargs):
        """Create Scf flow using ridft."""
        return cls(
            define_maker=DefineMaker.from_define_template(
                "ridft", define_parameters=define_parameters
            ),
            scf_maker=RidftMaker(),
            **kwargs,
        )

    @classmethod
    def riper(cls, define_parameters=None, **kwargs):
        """Create Scf flow using riper."""
        return cls(
            define_maker=DefineMaker.from_define_template(
                "ridft", define_parameters=define_parameters
            ),
            scf_maker=RiperMaker(),
            **kwargs,
        )


@dataclass
class JobexFlowMaker(Maker):
    """
    Maker for a define + jobex flow.

    Args:
        define_maker: Maker for define.
        jobex_maker: Maker for jobex job.
        scf_maker: Maker for scf job.

    Options:
        max_cycles: max number of Jobex (geometry relaxation) cycles. If not provided,
            the value from the jobex_maker is used (by default: 1000). If both
            jobex_maker and max_cycles are provided, max_cycles takes precedence.
        pre_scf:
            if True:
                The flow will be: ScfFlow + JobexJob
            else:
                The flow will be: DefineJob + JobexJob

        post_scf:
            if True:
                The flow will end with a ScfJob.
                Since Jobex = [dscf, grad, statpt], the final energy will not be
                exactly the same. With this option on, a final scf is performed
                so that the energy in control is rewritten consistently.
            else:
                The final energy in control is the one from the N-1 step, while
                the one in Jobex output (geometry step N) is slightly different.
    """

    name: str = "Jobex Flow Maker"
    define_maker: DefineMaker = field(
        default_factory=lambda: DefineMaker.from_define_template("ridft")
    )
    max_cycles: Optional[int] = None
    jobex_maker: JobexMaker = field(default_factory=lambda: JobexMaker(max_cycles=1000))
    scf_maker: Union[DscfMaker, RidftMaker, RiperMaker] = field(
        default_factory=lambda: RidftMaker()
    )
    pre_scf_flow_maker: ScfFlowMaker = field(default_factory=lambda: ScfFlowMaker())
    pre_scf: bool = True
    post_scf: bool = False

    def __post_init__(self):
        """Post init modification of inner makers."""
        if self.max_cycles is not None:
            self.jobex_maker.max_cycles = self.max_cycles

    def make(
        self,
        system,
        charge=None,
        unpaired_electrons=None,
        prev_output=None,
    ):
        """
        Make a define + jobex + final scf flow.

        Parameters
        ----------
        system
            either a pymatgen Molecule or Structure or a
            turbomoleio MoleculeSystem or PeriodicSystem.
        charge
            charge of the system.
        unpaired_electrons
            number of unpaired electrons.
        prev_output
            a previous output to start from.

        Returns
        -------
            Flow: jobflow Flow performing sequentially:
                - a define job
                - a jobex job (with or without --riper option for periodic systems)
                - a final scf job (dscf or ridft) to make the output energy consistent
        """
        check_periodicity_consistence(self.scf_maker, system)

        if prev_output is None:  # pragma: no branch (trivial)
            if self.pre_scf:  # pragma: no cover (to be done)
                init_scf_flow = self.pre_scf_flow_maker.make(
                    system, charge=charge, unpaired_electrons=unpaired_electrons
                )
                jobex_job = self.jobex_maker.make(
                    prev_output=init_scf_flow.output.dir_name
                )
                jobs = [init_scf_flow, jobex_job]
            else:
                define_job = self.define_maker.make(
                    system, charge=charge, unpaired_electrons=unpaired_electrons
                )
                jobex_job = self.jobex_maker.make(
                    prev_output=define_job.output.dir_name
                )
                jobs = [define_job, jobex_job]
        else:  # pragma: no cover (to be done)
            jobex_job = self.jobex_maker.make(prev_output=prev_output)
            jobs = [jobex_job]

        if self.post_scf:  # pragma: no cover (to be done)
            post_scf_job = self.scf_maker.make(prev_output=jobex_job)
            jobs.append(post_scf_job)
            flow_output = post_scf_job.output
        else:
            flow_output = jobex_job.output

        # TODO: see if we want to store more than just the final job
        #  i.e. only the post scf if it's there or also the jobex and
        #  possibly the pre-dscf/ridft and define jobs.
        flow = Flow(jobs, output=flow_output)
        return flow

    @classmethod
    def dscf(cls, define_parameters=None, **kwargs):
        """Create Scf flow using dscf."""
        pre_scf_flow_maker = ScfFlowMaker.dscf(define_parameters=define_parameters)
        return cls(
            define_maker=DefineMaker.from_define_template(
                "dscf", define_parameters=define_parameters
            ),
            pre_scf_flow_maker=pre_scf_flow_maker,
            scf_maker=DscfMaker(),
            **kwargs,
        )

    @classmethod
    def ridft(cls, define_parameters=None, **kwargs):
        """Create Scf flow using ridft."""
        pre_scf_flow_maker = ScfFlowMaker.ridft(define_parameters=define_parameters)
        return cls(
            define_maker=DefineMaker.from_define_template(
                "ridft", define_parameters=define_parameters
            ),
            pre_scf_flow_maker=pre_scf_flow_maker,
            scf_maker=RidftMaker(),
            **kwargs,
        )

    @classmethod
    def riper(cls, define_parameters=None, **kwargs):
        """Create Scf flow using riper."""
        pre_scf_flow_maker = ScfFlowMaker.riper(define_parameters=define_parameters)
        return cls(
            define_maker=DefineMaker.from_define_template(
                "ridft", define_parameters=define_parameters
            ),
            pre_scf_flow_maker=pre_scf_flow_maker,
            scf_maker=RiperMaker(),
            **kwargs,
        )
