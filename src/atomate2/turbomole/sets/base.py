"""Module defining base atomate2-turbomole input set and generator."""
import logging
from dataclasses import dataclass

from pymatgen.io.core import InputGenerator, InputSet

__all__ = [
    "DefineInputSet",
    "TurbomoleInputSet",
    "BaseTurbomoleInputGenerator",
]

logger = logging.getLogger(__name__)


class DefineInputSet(InputSet):
    """A class to represent a set of Turbomole's define inputs."""

    pass


class TurbomoleInputSet(InputSet):
    """A class to represent a set of Turbomole inputs."""

    pass


@dataclass
class BaseTurbomoleInputGenerator(InputGenerator):
    """Base input generator for Turbolole."""

    pass
