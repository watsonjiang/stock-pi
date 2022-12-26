import asyncio
import logging
import sys
import unittest
from datetime import datetime

from stockpi import hq
from stockpi.hq import _is_market_open

LOGGER = logging.getLogger(__name__)


class ItSinaHq(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")
        self.sina_hq = hq.SinaHq(['sh600580'])

    def test_update_hq(self):
        async def test_sub(hq_info):
            LOGGER.info('hq info %s', hq_info)

        asyncio.run(self.sina_hq.update_hq(test_sub))

    def test_is_market_open(self):
        dt = datetime(2022, 12, 26, 10, 0, 0)
        self.assertTrue(_is_market_open(dt))
        dt = datetime(2022, 12, 26, 18, 0, 0)
        self.assertFalse(_is_market_open(dt))
        dt = datetime(2022, 12, 25, 10, 0, 0)
        self.assertFalse(_is_market_open(dt))
