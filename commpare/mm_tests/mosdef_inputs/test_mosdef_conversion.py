import os
import glob
import pytest
import parmed as pmd
import commpare
from commpare.tests.base_test import BaseTest

class TestMosdefConversion(BaseTest):

    def load_smiles():
        smiles = []
        with open('smiles.txt', 'r') as fi:
            for line in fi:
                if line.startswith('#'):
                    continue
                smiles.append(line.strip())
        return smiles


    reference_systems = commpare.identify_reference_systems()
    @pytest.mark.skipif('foyer' in reference_systems, 
            reason="foyer package not installed")
    def test_small_systems(self):
        import foyer
        # These tests are gro/top files 
        path_to_foyer_unit_tests = os.path.join(foyer.__path__[0],
                'opls_validation/')
        # Walk through each unit test folder, loading energy and print out
        unit_dirs = [folder for folder in os.listdir(path_to_foyer_unit_tests)
                if (os.path.isdir(os.path.join(path_to_foyer_unit_tests,folder))
                    and 'oplsaa.ff' not in folder)]
        for unit_test_dir in unit_dirs:
            print(unit_test_dir)
            os.chdir(os.path.join(path_to_foyer_unit_tests, unit_test_dir))
            top_file = glob.glob("*.top")[0]
            gro_file = glob.glob("*.gro")[0]
            structure = pmd.load_file(top_file, xyz=gro_file)
            energies = commpare.spawn_engine_simulations(structure,
                    hoomd_kwargs={'ref_distance':10, 'ref_energy':1/4.184})
            print(energies)
            print('='*20)

    @pytest.mark.skipif('foyer' not in reference_systems, 
            reason="foyer package not installed")
    @pytest.mark.parametrize("smiles", load_smiles())
    def test_smiles(self, smiles):
        import foyer
        import mbuild as mb
        # These tests are smiles strings 
        cmpd = mb.load(smiles, smiles=True) 
        ff = foyer.Forcefield(name='oplsaa')
        structure = ff.apply(cmpd)
        # Enlarge box to avoid cutoff issues
        structure.box = [100, 100, 100, 90, 90, 90]
        energies = commpare.spawn_engine_simulations(structure,
                hoomd_kwargs={'ref_distance':10, 'ref_energy':1/4.184})
        print(energies)
        print('='*20)
