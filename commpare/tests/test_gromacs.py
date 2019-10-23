import mbuild as mb
import foyer
from mbuild.examples import Ethane, Alkane
import commpare.gromacs

from commpare.tests.base_test import BaseTest


class TestGromacs(BaseTest):
    def test_opls(self):
        eth = Alkane(n=10)
        cmpd = mb.fill_box(eth, n_compounds=10, box=[10,10,10])
        ff = foyer.Forcefield(name='oplsaa')
        structure = ff.apply(cmpd)
        df = commpare.gromacs.build_run_measure_gromacs(structure)
        assert 'bond' in df
        assert 'angle' in df
        assert 'dihedral' in df
        assert 'nonbond' in df
