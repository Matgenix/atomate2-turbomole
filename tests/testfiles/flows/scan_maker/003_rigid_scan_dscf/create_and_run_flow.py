# -*- coding: utf-8 -*-
# Part of turbomole package.

"""Script to generate data files for scan_maker test "003_rigid_scan_dscf"."""

import numpy as np
from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Molecule
from turbomoleio.core.molecule import MoleculeSystem

from nagare.flows import ScanMaker

scan_maker = ScanMaker.rigid_scan(
    define_template="dscf",
    db_file="fake.yaml",
)

mlc = Molecule.from_file("h2.xyz")

scanning = np.arange(start=-0.15, stop=0.1501, step=0.05)

scan_values = []
molecule_systems = []
for iscan, scan in enumerate(scanning, start=1):
    mol = mlc.copy()
    scan_values.append(0.74 + scan)
    mol.translate_sites([0], [0, 0, -scan / 2])
    mol.translate_sites([1], [0, 0, scan / 2])
    molsys = MoleculeSystem(molecule=mol)
    molsys.add_distance(0, 1, status="f")
    molecule_systems.append(molsys)

f = scan_maker.make(molecule_systems, scan_values=scan_values)

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
