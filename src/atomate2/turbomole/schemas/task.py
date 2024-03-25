"""Core definition of atomate2-turbomole task document."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from atomate2.turbomole.schemas.calculation import (
    Calculation,
    Status,
)
from atomate2.turbomole.utils import datetime_str
from emmet.core.math import Matrix3D, Vector3D
from emmet.core.structure import MoleculeMetadata
from monty.os import cd
from pydantic import BaseModel, Field
from pymatgen.core.structure import Molecule, Structure
from turbomoleio.core.control import Control, Energy, Gradient
from turbomoleio.core.molecule import MoleculeSystem
from turbomoleio.core.periodic import PeriodicSystem
from turbomoleio.output.data import RunData
from turbomoleio.output.files import BaseData, ScfOutput
from turbomoleio.output.states import States

__all__ = [
    "DefineTaskDocument",
    "TaskDocument",
]

logger = logging.getLogger(__name__)
_DefineTD_T = TypeVar("_DefineTD_T", bound="DefineTaskDocument")
_TD_T = TypeVar("_TD_T", bound="TaskDocument")


# TODO: This was a gigantic copy paste from atomate2
# Cp2kInput is defined in pymatgen, TM Inputs are not defined in TurbomoleIO


class DefineTaskDocument(MoleculeMetadata):
    """Definition of define task document."""

    dir_name: str = Field(None, description="The directory for this define task")
    last_updated: str = Field(
        default_factory=datetime_str,
        description="Timestamp for this task document was last updated",
    )
    completed_at: str = Field(
        None, description="Timestamp for when this task was completed"
    )
    output: dict = Field(None, description="The output of the final calculation")

    # molecule: Molecule = Field(
    #     None, description="Final output molecule from the task"
    # )

    @classmethod
    def from_directory(
        cls: Type[_DefineTD_T],
        dir_name: Union[Path, str],
    ) -> _DefineTD_T:
        """
        Create a task document from a directory containing the output of a define run.

        Parameters
        ----------
        dir_name
            The path to the folder containing the calculation outputs.

        Returns
        -------
        DefineTaskDocument
            A task document for the calculation.
        """
        logger.info(f"Getting task doc in: {dir_name}")

        dir_name = Path(dir_name).absolute()

        with cd(dir_name):
            system = MoleculeSystem.from_file("control", fmt="coord")
            molecule = system.molecule
            control = Control.from_file("control")
            rundata = RunData.from_file("define.log")

        # Remove dummy atoms
        molecule.remove_species(["x", "X", "q", "Q"])

        doc = cls.from_molecule(meta_molecule=molecule)
        ddict = doc.dict()
        data = {
            "molecule": molecule,
            "system": system,
            "dir_name": str(dir_name),
            "completed_at": str(rundata.end_time),
            "output": {"control": control},
        }
        ddict.update(data)
        doc = cls(**ddict)
        # doc = doc.copy(update=data)
        return doc


class InputSummary(BaseModel):
    """Summary of inputs for a Turbomole calculation."""

    structure: Union[Structure, Molecule] = Field(
        None, description="The input structure object"
    )

    xc: str = Field(
        None, description="Exchange-correlation functional used if not the default"
    )

    @classmethod
    def from_turbomole_calc_doc(  # pragma: no cover (not used)
        cls, calc_doc: Calculation
    ) -> "InputSummary":
        """
        Create calculation input summary from a calculation document.

        Parameters
        ----------
        calc_doc
            A Turbomole calculation document.

        Returns
        -------
        InputSummary
            A summary of the input structure and parameters.
        """
        summary = None

        return cls(
            structure=calc_doc.input.structure,
            xc=str(calc_doc.run_type),
            summary=summary,
        )


class OutputSummary(BaseModel):
    """Summary of the outputs for a Turbomole calculation."""

    structure: Union[Structure, Molecule] = Field(
        None, description="The output structure object"
    )
    energy: float = Field(
        None, description="The final total DFT energy for the last calculation"
    )
    energy_per_atom: float = Field(
        None, description="The final DFT energy per atom for the last calculation"
    )
    bandgap: float = Field(None, description="The DFT bandgap for the last calculation")
    cbm: float = Field(None, description="CBM for this calculation")
    vbm: float = Field(None, description="VBM for this calculation")
    forces: List[Vector3D] = Field(
        None, description="Forces on atoms from the last calculation"
    )
    stress: Matrix3D = Field(
        None, description="Stress on the unit cell from the last calculation"
    )

    @classmethod
    def from_turbomole_calc_doc(  # pragma: no cover (not used)
        cls, calc_doc: Calculation
    ) -> "OutputSummary":
        """
        Create a summary of Turbomole calculation outputs.

        Parameters
        ----------
        calc_doc
            A Turbomole calculation document.

        Returns
        -------
        OutputSummary
            The calculation output summary.
        """
        if calc_doc.output.ionic_steps:
            forces = calc_doc.output.ionic_steps[-1].get("forces", None)
            stress = calc_doc.output.ionic_steps[-1].get("stress", None)
        else:
            forces = None
            stress = None
        return cls(
            structure=calc_doc.output.structure,
            energy=calc_doc.output.energy,
            energy_per_atom=calc_doc.output.energy_per_atom,
            bandgap=calc_doc.output.bandgap,
            cbm=calc_doc.output.cbm,
            vbm=calc_doc.output.vbm,
            forces=forces,
            stress=stress,
        )


class TaskDocument(MoleculeMetadata):
    """Definition of Turbomole task document."""

    dir_name: str = Field(None, description="The directory for this Turbomole task")
    last_updated: str = Field(
        default_factory=datetime_str,
        description="Timestamp for this task document was last updated",
    )
    completed_at: str = Field(
        None, description="Timestamp for when this task was completed"
    )
    input: InputSummary = Field(None, description="The input to the first calculation")
    output: OutputSummary = Field(
        None, description="The output of the final calculation"
    )
    structure: Union[Structure, Molecule] = Field(
        None, description="Final output structure from the task"
    )
    state: Status = Field(None, description="State of this task")
    task_label: str = Field(None, description="A description of the task")
    tags: Optional[List[str]] = Field(
        None, description="Metadata tags for this task document"
    )
    author: Optional[str] = Field(
        None, description="Author extracted from transformations"
    )

    """
    TODO: enforce on real cases
    """
    identifier: Optional[dict] = Field(
        None,
        description="Identifier dictionary for known databases "
        "such as Materials Project {'type': 'MP', 'value': 'mp-7500'}",
    )

    calcs_reversed: List[Calculation] = Field(
        default_factory=list,
        description="The inputs and outputs for all Turbomole runs in this task.",
    )
    custodian: Any = Field(
        None,
        description="Information on the custodian settings used to run this "
        "calculation, parsed from a custodian.json file",
    )

    @classmethod
    def from_directory(
        cls: Type[_TD_T],
        dir_name: Union[Path, str],
        output_file: str,
        additional_fields: Dict[str, Any] = None,
        output_cls: BaseData = ScfOutput,
    ) -> _TD_T:
        """
        Create a task document from a directory containing the output of a define run.

        Parameters
        ----------
        dir_name
            The path to the folder containing the calculation outputs.
        output_file
            The output file
        additional_fields
            Dictionary of additional fields to add to output document.
        output_cls
            Class used to parse the output file.

        Returns
        -------
        ScfTaskDocument
            A task document for the calculation.

        Args:
            output_cls:
        """
        logger.info(f"Getting task doc in: {dir_name}")

        additional_fields = {} if additional_fields is None else additional_fields
        dir_name = Path(dir_name).absolute()

        with cd(dir_name):
            control = Control.from_file("control")
            output = output_cls.from_file(output_file)
            scf_states = States.from_file("control")
            energies = Energy.from_file()
            try:
                gradient = Gradient.from_file()
            except FileNotFoundError:
                gradient = None

            periodic = control.show_data_group("periodic")

            if periodic is None:  # pragma: no branch
                attr = "from_molecule"
                ms = MoleculeSystem.from_file("control", fmt="coord")
                molecule = ms.molecule.copy()
                # Remove dummy atoms
                molecule.remove_species(["x", "X", "q", "Q"])
                dat = {
                    "system": ms,
                    "structure": molecule,
                    "meta_molecule": molecule,
                    "input": InputSummary(
                        structure=molecule, xc=output.dft.functional.name
                    ),
                }

            elif int(periodic.strip()) in (
                1,
                2,
                3,
            ):  # pragma: no cover (not implemented)
                attr = "from_structure"
                ps = PeriodicSystem.from_file("control", fmt="coord")
                dat = {
                    "system": ps,
                    "structure": ps.structure,
                    "meta_structure": ps.structure,
                }

            else:  # pragma: no cover (trivial)
                raise ValueError(
                    "periodic should not be present in the control file "
                    "or be one of 1, 2 or 3."
                )
            dat["completed_at"] = str(output.run.end_time)
            dat["state"] = "successful"
            dat["task_label"] = output_cls.__name__

        doc = getattr(cls, attr)(**dat)
        ddict = doc.dict()
        data = {
            "dir_name": str(dir_name),
            "output": {
                "control": control,
                "output": output,
                "energies": energies,
                "gradient": gradient,
                "states": scf_states,
            },
            "energy": energies.total[-1],
            "homo": scf_states.homo,
            "lumo": scf_states.lumo,
        }
        ddict.update(data)
        doc = cls(**ddict)
        # doc = doc.copy(update=data)
        doc = doc.copy(update=additional_fields)
        return doc
