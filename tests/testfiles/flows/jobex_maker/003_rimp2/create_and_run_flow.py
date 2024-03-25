# -*- coding: utf-8 -*-
# Part of turbomole package.

"""Script to generate data files for jobex_maker test "001_default"."""

from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Molecule

from nagare.flows import JobexMaker

jbx_maker = JobexMaker.rimp2()

ms = Molecule.from_file("MnH2.xyz")

f = jbx_maker.make(ms, unpaired_electrons=4, charge=1)

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
