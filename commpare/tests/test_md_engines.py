import commpare
from commpare.tests.base_test import BaseTest
class TestEngines(BaseTest):

    def test_check(self):
        found_engines = commpare.identify_engines()
        assert found_engines is not None

