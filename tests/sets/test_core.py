from pathlib import Path

import numpy as np
import pytest
from atomate2.turbomole.sets.base import DefineInputSet, TurbomoleInputSet
from atomate2.turbomole.sets.core import (
    DscfInputGenerator,
    TurbomoleDefineInputGenerator,
    TurbomoleInputGenerator,
)
from monty.tempfile import ScratchDir
from pymatgen.core import Lattice, Molecule, Structure
from turbomoleio.core.molecule import MoleculeSystem
from turbomoleio.core.periodic import PeriodicSystem


# @pytest.mark.skip(reason="I am not sure whether imports are right")
def test_define_input_set_type(mnh2_molecule, si_structure) -> None:
    """
    test that TurbomoleDefineInputGenerator.get_input_set
    accepts only pymatgen Molecule or Structure
    or a turbomoleio MoleculeSystem or PeriodicSystem
    """
    tm_obj = TurbomoleDefineInputGenerator(define_template="ridft")
    with pytest.raises(
        RuntimeError,
        match=r'The "molecule_or_structure" input should be a pymatgen '
        r"Molecule/Structure or a turbomoleio MoleculeSystem/PeriodicSystem.",
    ):
        tm_obj.get_input_set("string")
    with pytest.raises(
        RuntimeError,
        match=r'The "molecule_or_structure" input should be a pymatgen '
        r"Molecule/Structure or a turbomoleio MoleculeSystem/PeriodicSystem.",
    ):
        tm_obj.get_input_set(1.234)

    ds = tm_obj.get_input_set(mnh2_molecule)
    assert isinstance(ds, DefineInputSet)
    assert isinstance(ds.system, MoleculeSystem)

    tm_obj = TurbomoleDefineInputGenerator(define_template="ridft")
    ds = tm_obj.get_input_set(si_structure)
    assert isinstance(ds, DefineInputSet)
    assert isinstance(ds.system, PeriodicSystem)


def test_define_input_set_generator(mnh2_molecule) -> None:
    """
    correct import of TurbomoleDefineInputGenerator
    """
    define_parameters = {
        "dft": "on",
        "basis": "def2-TZVP",
        "functional": "wb97x-v",
        "unpaired_electrons": 1,
    }
    tm_obj = TurbomoleDefineInputGenerator(define_parameters=define_parameters)
    gen_inp = tm_obj.get_input_set(mnh2_molecule)

    assert gen_inp.xc_func == "wb97x-v"
    assert isinstance(gen_inp.system, MoleculeSystem)

    # Read cartesian coordinates and chemical composition from Molecule
    # object and compare to exact ones
    str_coords = gen_inp.inputs["coord"].split()

    read_coords = np.empty((3, 3))
    read_coords[0] = str_coords[1:4]
    read_coords[1] = str_coords[5:8]
    read_coords[2] = str_coords[9:12]
    true_coords = np.array(
        [
            [0.00000000000000, 0.00000000000000, 0.02871816791594],
            [0.00000000000000, 3.15307228962633, -0.35897237463391],
            [0.00000000000000, -3.15307228962633, -0.35897237463391],
        ]
    )
    assert np.allclose(read_coords, true_coords, 1e-6, 1e-9)

    read_composition = [str_coords[4], str_coords[8], str_coords[12]]
    assert read_composition == ["mn", "h", "h"]


def test_define_explicit_insertion() -> None:
    """
    explicit parameters definition in TurbomoleDefineInputGenerator
    overwrites template from turbomoleio
    """

    define_parameters = {
        "charge": 0,
        "coord_file": "file.name",
        "dft": "on",
        "gridsize": "value",
        "ired": "False",
        "method": "dft",
        "ri": True,
        "scfiterlimit": 1234,
        "title": "job_title",
        "unpaired_electrons": 234,
    }

    # Test on CO molecule
    tm_obj_1 = TurbomoleDefineInputGenerator(
        define_template="dscf", define_parameters=define_parameters
    )
    mol_obj = Molecule(["C", "O"], [[0.0, 0.0, 0.0], [0.0, 0.0, 1.2]])
    mol_inp = tm_obj_1.get_input_set(mol_obj)
    mol_dict = dict(mol_inp.define_parameters)

    assert define_parameters.items() <= mol_dict.items()

    with pytest.raises(KeyError):
        assert mol_dict["functional"]

    # Test on Fe crystal
    tm_obj_2 = TurbomoleDefineInputGenerator(
        define_template="dscf", define_parameters=define_parameters
    )
    cry_obj = Structure.from_spacegroup(
        "Im-3m", Lattice.cubic(2.8), ["Fe"], [[0, 0, 0]]
    )
    cry_inp = tm_obj_2.get_input_set(cry_obj)
    cry_dict = dict(cry_inp.define_parameters)

    assert define_parameters.items() <= cry_dict.items()

    with pytest.raises(KeyError):
        assert cry_dict["functional"]


def test_turbomole_inp_gen() -> None:
    turbomol_inp_gen = TurbomoleInputGenerator()
    assert isinstance(turbomol_inp_gen.get_input_set(), TurbomoleInputSet)


def test_Define_input(h2_molecule) -> None:
    define_inp_gen = TurbomoleDefineInputGenerator(define_parameters={})
    dis = define_inp_gen.get_input_set(h2_molecule, unpaired_electrons=6)
    assert isinstance(dis, DefineInputSet)
    assert dis.define_parameters["unpaired_electrons"] == 6
    assert dis.define_parameters["charge"] == 0
    define_inp_gen = TurbomoleDefineInputGenerator(
        define_parameters={"unpaired_electrons": 3, "charge": 5}
    )
    dis = define_inp_gen.get_input_set(h2_molecule, unpaired_electrons=6)
    assert isinstance(dis, DefineInputSet)
    assert dis.define_parameters["unpaired_electrons"] == 6
    assert dis.define_parameters["charge"] == 5
    define_inp_gen = TurbomoleDefineInputGenerator(
        define_parameters={"unpaired_electrons": 3, "charge": 1}
    )
    dis = define_inp_gen.get_input_set(h2_molecule, unpaired_electrons=6, charge=2)
    assert isinstance(dis, DefineInputSet)
    assert dis.define_parameters["unpaired_electrons"] == 6
    assert dis.define_parameters["charge"] == 2
    with pytest.raises(ValueError, match=r"Charge is not close to an integer."):
        define_inp_gen.get_input_set(h2_molecule, charge=1.8)
    define_inp_gen = TurbomoleDefineInputGenerator(
        use_system_charge=False, define_parameters={}
    )
    dis = define_inp_gen.get_input_set(h2_molecule)
    assert "charge" not in dis.define_parameters


def test_Dscf_input() -> None:
    dscf_inp_gen = DscfInputGenerator()
    assert isinstance(dscf_inp_gen.get_input_set(), TurbomoleInputSet)


def test_Dscf_from_prev_output(test_files) -> None:
    dscf_inp_gen = DscfInputGenerator()
    prev_output = (
        test_files
        / "jobs"
        / "define_maker_001"
        / "job_2023-05-11-10-14-21-911069-54300"
    )
    with ScratchDir(".") as scratch_dir:
        dscf_input_set = dscf_inp_gen.get_input_set(prev_output=prev_output)
        assert isinstance(dscf_input_set, TurbomoleInputSet)
        control = Path(scratch_dir) / "control"
        assert control.exists()
