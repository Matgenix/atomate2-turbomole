# -*- coding: utf-8 -*-
# Part of turbomole package.

"""Script to generate data files for jobex_maker test "002_database"."""

from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Molecule

from nagare.flows import JobexMaker

# One should put a proper dbfile.yaml here in order to run this flow
jbx_maker = JobexMaker(
    define_template="ridft",
    db_file="dbfile.yaml",
    max_cycles=30,
    jobex_options=["-time"],
)

ms = Molecule.from_file("h2.xyz")

f = jbx_maker.make(ms)

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
