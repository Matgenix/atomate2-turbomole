"""Script to generate data files for jobex_maker test "001_ridft"."""

from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Molecule

from atomate2.turbomole.flows.core import JobexFlowMaker

jbx_maker = JobexFlowMaker.ridft()

ms = Molecule.from_file("h2.xyz")

f = jbx_maker.make(ms)

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
