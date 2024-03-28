"""Core definitions of Turbomole calculation documents."""

from typing import Any, Dict, List, Union

from jobflow.utils import ValueEnum
from pydantic import BaseModel, Field
from pymatgen.core.structure import Molecule, Structure

from atomate2.turbomole.schemas.calc_types import CalcType, RunType, TaskType


class Status(ValueEnum):
    """Turbomole calculation state."""

    SUCCESS = "successful"
    FAILED = "failed"


class TurbomoleObject(ValueEnum):
    """Types of Turbomole data objects."""

    ENERGY = "energy"


class CalculationInput(BaseModel):
    """Summary of inputs for a Turbomole calculation."""

    structure: Union[Structure, Molecule] = Field(
        None, description="The input structure/molecule object"
    )

    turbomole_input: Dict = Field(
        None, description="The Turbomole input used for this task"
    )

    dft: Dict = Field(
        None,
        description="DFT parameters used in the last calc of this task.",
    )

    turbomole_global: Dict = Field(
        None,
        description="Turbomole global parameters used in the last calc of this task.",
    )


class CalculationOutput(BaseModel):
    """Document defining Turbomole calculation outputs."""

    energy: float = Field(
        None, description="The final total DFT energy for the calculation"
    )
    energy_per_atom: float = Field(
        None, description="The final DFT energy per atom for the calculation"
    )
    structure: Union[Structure, Molecule] = Field(
        None, description="The final structure/molecule from the calculation"
    )
    efermi: float = Field(
        None, description="The Fermi level from the calculation in eV"
    )
    is_metal: bool = Field(None, description="Whether the system is metallic")
    bandgap: float = Field(None, description="The band gap from the calculation in eV")
    cbm: float = Field(
        None,
        description="The conduction band minimum in eV (if system is not metallic)",
    )
    vbm: float = Field(
        None, description="The valence band maximum in eV (if system is not metallic)"
    )
    ionic_steps: List[Dict[str, Any]] = Field(
        None, description="Energy, forces, and structure for each ionic step"
    )


class Calculation(BaseModel):
    """Full Turbomole calculation inputs and outputs."""

    dir_name: str = Field(
        None, description="The directory for this Turbomole calculation"
    )
    turbomole_version: str = Field(
        None, description="Turbomole version used to perform the calculation"
    )
    has_completed: Status = Field(
        None, description="Whether Turbomole completed the calculation successfully"
    )
    input: CalculationInput = Field(
        None, description="Turbomole input settings for the calculation"
    )
    output: CalculationOutput = Field(
        None, description="The Turbomole calculation output"
    )
    completed_at: str = Field(
        None, description="Timestamp for when the calculation was completed"
    )
    task_name: str = Field(
        None, description="Name of task given by custodian (e.g., relax1, relax2)"
    )
    output_file_paths: Dict[str, str] = Field(
        None,
        description="Paths (relative to dir_name) of the Turbomole output files "
        "associated with this calculation",
    )
    # bader: Dict = Field(None, description="Output from the bader software")
    run_type: RunType = Field(
        None, description="Calculation run type (e.g., HF, HSE06, PBE)"
    )
    task_type: TaskType = Field(
        None, description="Calculation task type (e.g., Structure Optimization)."
    )
    calc_type: CalcType = Field(
        None, description="Return calculation type (run type + task_type)."
    )
