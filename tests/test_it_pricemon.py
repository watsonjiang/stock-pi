import unittest
import logging
import sys

from sqlalchemy.engine import create_engine
from stockpi import PriceMon, hq, model


LOGGER = logging.getLogger(__name__)

class ItPriceMon(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format="%(asctime)s %(levelname)-8s %(message)s")
        self.db_engine = create_engine('sqlite:///:memory:', echo=True)
        model.create_all_tables(self.db_engine)
        self.sina_hq = hq.SinaHq(self.db_engine, ['sh600580'])

    def test_pricemon(self):
        mon = PriceMon([
            'sh600580' #卧龙电驱
        ], 'sqlite:///:memory:')
        mon.mon()
