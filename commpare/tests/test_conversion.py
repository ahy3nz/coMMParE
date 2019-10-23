import pytest

import mbuild as mb
import foyer
from mbuild.examples import Ethane, Alkane

import commpare
from commpare.tests.base_test import BaseTest

class TestConversion(BaseTest):
    def test_conversions(self):
        # Check to see if we can correctly spawn engine simulations
        eth = Alkane(n=10)
        cmpd = mb.fill_box(eth, n_compounds=10, box=[10,10,10])
        ff = foyer.Forcefield(name='oplsaa')
        structure = ff.apply(cmpd)

        df = commpare.spawn_engine_simulations(structure,
                hoomd_kwargs={'ref_distance':10, 'ref_energy':1/4.184})
        assert df is not None
