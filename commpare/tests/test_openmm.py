import mbuild as mb
import subprocess
import parmed as pmd
import foyer
from mbuild.examples import Ethane, Alkane
import hoomd
import simtk.openmm as openmm
import panedr
from commpare.openmm.openmm_utils import build_run_measure_openmm


class TestOpenMM:
    def test_opls(self):
        eth = Alkane(n=10)
        cmpd = mb.fill_box(eth, n_compounds=10, box=[10,10,10])
        ff = foyer.Forcefield(name='oplsaa')
        structure = ff.apply(cmpd)
        df = build_run_measure_openmm(structure)
        assert 'bond' in df
        assert 'angle' in df
        assert 'dihedral' in df
        assert 'nonbond' in df
