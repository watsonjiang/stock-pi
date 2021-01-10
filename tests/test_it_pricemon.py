import unittest
import logging
import sys
from stock import PriceMon


LOGGER = logging.getLogger(__name__)

class ItPriceMon(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format="%(asctime)s %(levelname)-8s %(message)s")

    def test_pricemon(self):
        mon = PriceMon([
            'sh600580' #卧龙电驱
        ])
        mon.mon()
