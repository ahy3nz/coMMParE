import mbuild as mb
import foyer
from mbuild.examples import Ethane, Alkane
import commpare.openmm


class TestOpenMM:
    def test_opls(self):
        eth = Alkane(n=10)
        cmpd = mb.fill_box(eth, n_compounds=10, box=[10,10,10])
        ff = foyer.Forcefield(name='oplsaa')
        structure = ff.apply(cmpd)
        df = commpare.openmm.build_run_measure_openmm(structure)
        assert 'bond' in df
        assert 'angle' in df
        assert 'dihedral' in df
        assert 'nonbond' in df
