# -*- coding: utf-8 -*-
# Part of turbomole package.

"""Script to generate data files for jobex_maker test "006_riper"."""

from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Structure

from nagare.flows import JobexMaker

jbx_maker = JobexMaker(
    define_template="ridft",
    db_file="fake.yaml",
    max_cycles=30,
    jobex_options=["-time"],
)

ms = Structure.from_file("si.cif")

f = jbx_maker.make(ms, periodicity="1D", nkpoints=[2])

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
