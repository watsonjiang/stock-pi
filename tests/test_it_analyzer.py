import unittest
import logging
import sys
import json
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import MetaData
from stockpi import hq
import time
import datetime
import sqlite3
from stockpi import model, analyzer

LOGGER = logging.getLogger(__name__)

class ItPriceRushAnalyzer(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")
        creator = lambda: sqlite3.connect('file::memory:?cache=shared', uri=True)
        self.db_engine = create_engine('sqlite://', creator=creator, echo=True)
        #self.db_engine = create_engine('sqlite:///stock_db.sqlite3', echo=True)
        model.create_all_tables(self.db_engine)
        self.an = analyzer.PriceRushAnalyzer(self.db_engine, ['sh600580'], 10, 3)

    def test_analyze(self):
        '''测试有异动'''
        hq_hist = model.HqHistory()
        hq_hist.stock_no = '12345'
        hq_hist.price = 10.0
        hq_hist1 = model.HqHistory()
        hq_hist1.stock_no = '12345'
        hq_hist1.price = 20.0
        with sessionmaker(self.db_engine).begin() as session:
            session.add(hq_hist)
            time.sleep(3)
            session.add(hq_hist1)

        self.an.analyze()    
