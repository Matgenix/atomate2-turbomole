# -*- coding: utf-8 -*-
# Part of turbomole package.

"""Script to generate data files for scan_maker test "004_relaxed_scan_ridft"."""

import numpy as np
from jobflow.managers.local import run_locally
from monty.os import cd, makedirs_p
from pymatgen.core.structure import Molecule
from turbomoleio.core.molecule import MoleculeSystem

from nagare.flows import ScanMaker

scan_maker = ScanMaker.relaxed_scan(
    define_template="ridft",
    db_file="fake.yaml",
)

mlc = Molecule.from_file("h2o.xyz")

scanning = np.arange(start=-0.15, stop=0.151, step=0.05)
oh1_vector = mlc[1].coords - mlc[0].coords
oh2_vector = mlc[2].coords - mlc[0].coords
oh1_unitvector = oh1_vector / np.linalg.norm(oh1_vector)
oh2_unitvector = oh2_vector / np.linalg.norm(oh2_vector)
oh_dist = np.linalg.norm(oh1_vector)

scan_values = []
molecule_systems = []
for iscan, scan in enumerate(scanning, start=1):
    mol = mlc.copy()
    mol.translate_sites([1], scan * oh1_unitvector)
    mol.translate_sites([2], scan * oh2_unitvector)
    molsys = MoleculeSystem(molecule=mol)
    molsys.add_distance(0, 1, status="f")
    molsys.add_distance(0, 2, status="f")
    scan_values.append(oh_dist + scan)
    molecule_systems.append(molsys)


f = scan_maker.make(molecule_systems, scan_values=scan_values)

makedirs_p("run")
with cd("run"):
    run_locally(f, create_folders=True)
