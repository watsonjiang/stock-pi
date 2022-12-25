import asyncio
import logging
import sys
import unittest

from stockpi import hq

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
       