"""Module defining core atomate2-turbomole input set generators."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np
from atomate2.turbomole.sets.base import (
    BaseTurbomoleInputGenerator,
    DefineInputSet,
    TurbomoleInputSet,
)
from atomate2.turbomole.utils import get_define_parameters
from pymatgen.core import Molecule, Structure
from turbomoleio.core.control import cpc
from turbomoleio.core.molecule import MoleculeSystem
from turbomoleio.core.periodic import PeriodicSystem


@dataclass
class TurbomoleDefineInputGenerator(BaseTurbomoleInputGenerator):
    """A class to generate Turbomole input sets."""

    define_template: str | None = None
    define_parameters: dict = field(default_factory=dict)
    user_define_parameters_settings: dict = field(default_factory=dict)
    user_datagroups_settings: dict = field(default_factory=dict)
    use_system_charge: bool = True
    use_system_multiplicity: bool = False

    def get_input_set(
        self,
        system: MoleculeSystem | PeriodicSystem | Molecule | Structure,
        charge=None,
        unpaired_electrons=None,
    ) -> DefineInputSet:  # type: ignore
        """
        Generate a DefineInputSet object.

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
            a DefineInputSet object

        TODO: can we use pydantic to make sure system is of the correct kind?
        """
        # Define the system
        if isinstance(system, Molecule):
            system = MoleculeSystem(system)
        elif isinstance(system, Structure):
            system = PeriodicSystem(system)
        elif not isinstance(  # pragma: no branch (trivial)
            system, (MoleculeSystem, PeriodicSystem)
        ):
            raise RuntimeError(
                'The "molecule_or_structure" input should be a pymatgen '
                "Molecule/Structure or a turbomoleio MoleculeSystem/PeriodicSystem."
            )

        # Get the define parameters
        dp = get_define_parameters(self.define_template, self.define_parameters)
        if unpaired_electrons is not None:
            dp["unpaired_electrons"] = unpaired_electrons
        elif self.use_system_multiplicity:  # pragma: no branch (trivial)
            raise NotImplementedError(
                "multiplicity from the system not yet implemented."
            )
        if charge is not None:
            dp["charge"] = charge
        elif dp.get("charge", None) is None and self.use_system_charge:
            dp["charge"] = system._molecule_or_structure.charge
        # Charges should be integers
        if dp.get("charge", None) is not None:
            int_charge = int(np.around(dp["charge"]))
            if not np.isclose(int_charge, dp["charge"]):
                raise ValueError("Charge is not close to an integer.")
            dp["charge"] = int_charge

        # The exchange-correlation functional should be set outside of define as it
        # does not know about libxc functionals
        func = dp.pop("functional", None)

        return DefineInputSet(
            inputs={
                "coord": system.to_coord_string(),
                "define_parameters.json": json.dumps(dp),
                "datagroups.json": json.dumps(self.user_datagroups_settings),
            },
            xc_func=func,
            datagroups=self.user_datagroups_settings,
            define_parameters=dp,
            system=system,
        )


@dataclass
class TurbomoleInputGenerator(BaseTurbomoleInputGenerator):
    """A class to generate Turbomole input sets."""

    def get_input_set(self, prev_output=None) -> TurbomoleInputSet:  # type: ignore
        """
        Generate a TurbomoleInputSet object.

        TODO: what kind of file is prev_output?
        """
        if prev_output is not None:
            cpc(".", control_dir=prev_output)
        return TurbomoleInputSet()


@dataclass
class DscfInputGenerator(TurbomoleInputGenerator):
    """A class to generate Turbomole input sets."""

    def get_input_set(self, prev_output=None) -> TurbomoleInputSet:  # type: ignore
        """
        Generate a TurbomoleInputSet object.

        TODO: what kind of file is prev_output?
        """
        if prev_output is not None:
            cpc(".", control_dir=prev_output)
        return TurbomoleInputSet()
