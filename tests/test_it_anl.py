import asyncio
import datetime
import logging
import sys
import unittest
from unittest.mock import patch, AsyncMock

from stockpi import anl
from stockpi.db import HqHistory

LOGGER = logging.getLogger(__name__)


class ItPriceRushAnalyzer(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")
        self.an = anl.PriceRushAnalyzer(None, None)

    @patch('stockpi.anl.db_get_hq_hist')
    def test_analyze(self, mock_db_get_hq_hist):
        '''测试有异动'''
        self.an.notice_rush = AsyncMock()

        hq_hist = HqHistory()
        hq_hist.stock_no = 'sh600580'
        hq_hist.price = 10.0
        hq_hist.create_time = datetime.datetime.now()
        hq_hist1 = HqHistory()
        hq_hist1.stock_no = 'sh600580'
        hq_hist1.price = 20.0
        hq_hist1.create_time = datetime.datetime.now()
        mock_db_get_hq_hist.side_effect = [[hq_hist, hq_hist1]]

        asyncio.run(self.an.do_analyze('sh600580'))

        self.an.notice_rush.assert_called_once_with('sh600580', 10.0, 20.0)
