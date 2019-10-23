import os
import glob
import pytest
import parmed as pmd
import commpare
from commpare.tests.base_test import BaseTest

class TestAmberConversion(BaseTest):
    reference_systems = commpare.identify_reference_systems()
    @pytest.mark.skipif('validate' not in reference_systems, 
            reason="Validate package not installed")
    def test_small_systems(self):
        import validate
        path_to_amb_unit_tests = os.path.join(validate.__path__[0],
                'tests/amber/unit_tests')
        # Walk through each unit test folder, loading energy and print out
        unit_dirs = [folder for folder in os.listdir(path_to_amb_unit_tests)
                if os.path.isdir(os.path.join(path_to_amb_unit_tests,folder))]
        for unit_test_dir in unit_dirs:
            print(unit_test_dir)
            os.chdir(os.path.join(path_to_amb_unit_tests, unit_test_dir))
            # Maybe there's a better way to validate the contents of each 
            # unit test directory?
            prmtop_files = glob.glob("*.prmtop")
            crd_files = []
            crd_files.extend(glob.glob("*.crd"))
            crd_files.extend(glob.glob("*.inpcrd"))
            if len(prmtop_files) > 0 and len(crd_files) > 0:
                structure = pmd.load_file(prmtop_files[0], xyz=crd_files[0])
                energies = commpare.spawn_engine_simulations(structure,
                        engines=['openmm', 'gromacs'],
                        hoomd_kwargs={'ref_distance':10, 'ref_energy':1/4.184})
                print(energies)
            print('='*20)
