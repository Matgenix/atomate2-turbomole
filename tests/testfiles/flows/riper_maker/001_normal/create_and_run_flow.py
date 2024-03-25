# -*- coding: utf-8 -*-
# Part of turbomole package.

"""Script to generate data files for riper_maker test "001_normal"."""

from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Structure

from nagare.flows import RiperMaker

riper_maker = RiperMaker(
    define_template="ridft",
    db_file="fake.yaml",
)

ms = Structure.from_file("si.cif")

f = riper_maker.make(ms, periodicity="1D", nkpoints=[2])

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
