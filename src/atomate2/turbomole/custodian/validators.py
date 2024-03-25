# Part of atomate2-turbomole package.

"""Module containing the custodian validators for the atomate2-turbomole package."""

import os
from dataclasses import dataclass

from custodian.custodian import Validator
from turbomoleio.output.data import ScfIterationData


@dataclass
class JobexGeoOptConvergedValidator(Validator):
    """Validator for jobex run.

    Validates that a GEO_OPT_CONVERGED file has been written.
    """

    def check(self, directory="./"):
        """Check for jobex convergence error.

        Returns
        -------
            bool: False if jobex is converged, i.e. a GEO_OPT_CONVERGED file
                is present in the directory, True otherwise
        """
        return not os.path.exists("GEO_OPT_CONVERGED")


@dataclass
class ScfConvergedValidator(Validator):
    """Validator for scf run (ridft or dscf).

    Validates the scf run is converged.
    """

    output_file: str

    def check(self, directory="./"):
        """Check for scf convergence error.

        Returns
        -------
            bool: False if scf run is converged.
        """
        if not os.path.exists(self.output_file):
            return True
        scf_iterations = ScfIterationData.from_file(self.output_file)
        if scf_iterations:
            return not scf_iterations.converged
        # For riper calculations, turbomoleio does not get scf iterations (yet)
        # Just make sure it is converged by reading the output file directly
        with open(self.output_file) as f:
            string = f.read()
        return "SCF converged within " not in string


@dataclass
class NormalEndValidator(Validator):
    """Check for the presence of the "all done" string in the output file."""

    out_file: str

    def check(self, directory="./"):
        """
        Check normal end.

        Return True if an error is found, i.e. output file is not present or
        the "all done" string is not present in the output file.
        """
        if not os.path.isfile(self.out_file):
            return True

        # read bytes since sometimes error file could be corrupted,
        # this will avoid failures due to non utf-8 bytes.
        with open(self.out_file, "rb") as f:
            out = f.read()

        failed = out.rfind(b"all done") < 0

        return failed
