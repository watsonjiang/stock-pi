import unittest
import logging
import sys
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import MetaData
from stockpi import hq
import sqlite3
from stockpi import analyzer, model, notify
from unittest.mock import MagicMock
import asyncio

LOGGER = logging.getLogger(__name__)

class ItPriceRushAnalyzer(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")
        creator = lambda: sqlite3.connect('file::memory:?cache=shared', uri=True)
        self.db_engine = create_engine('sqlite://', creator=creator, echo=True)
        #self.db_engine = create_engine('sqlite:///stock_db.sqlite3')
        model.create_all_tables(self.db_engine)
        messenger = notify.DummyMessenger()
        self.an = analyzer.PriceRushAnalyzer(self.db_engine, messenger, ['sh600580', 'sz000568'], 300, 3)

    def test_analyze(self):
        '''测试有异动'''
        self.an.notice_rush = MagicMock()

        hq_hist = model.HqHistory()
        hq_hist.stock_no = 'sh600580'
        hq_hist.price = 10.0
        hq_hist1 = model.HqHistory()
        hq_hist1.stock_no = 'sh600580'
        hq_hist1.price = 20.0
        with sessionmaker(self.db_engine).begin() as session:
            session.add(hq_hist)
            session.add(hq_hist1)

        self.an.analyze()
        
        self.an.notice_rush.assert_called_once_with('sh600580', 10.0, 20.0)
