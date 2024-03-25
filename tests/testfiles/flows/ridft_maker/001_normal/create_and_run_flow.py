# -*- coding: utf-8 -*-
# Part of turbomole package.

"""Script to generate data files for ridft_maker test "001_normal"."""

from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Molecule

from nagare.flows import RidftMaker

dscf_maker = RidftMaker()

ms = Molecule.from_file("h2.xyz")

f = dscf_maker.make(ms)

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
