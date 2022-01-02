import unittest
import logging
import sys
import asyncio
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import MetaData
from stockpi import hq
import time
import datetime
from stockpi import model

LOGGER = logging.getLogger(__name__)


class ItSinaHq(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")
        self.db_engine = create_engine('sqlite:///:memory:', echo=True)
        model.create_all_tables(self.db_engine)
        self.sina_hq = hq.SinaHq(self.db_engine, ['sh600580'])

    def test_get_price(self):
        rst = asyncio.get_event_loop().run_until_complete(self.sina_hq.get_price(['sh600580']))
        LOGGER.info('price info %s', rst)

    def test_should_update_hq(self):
        '''测试信息拉取间隔, 10秒一次'''
        i = 0
        while True:
            i = i + 1
            LOGGER.info('----sleep %s should_update_hq %s',
                        i, self.sina_hq.should_update_hq())
            time.sleep(1)

    def test_update_company_info(self):
        '''测试更新公司信息
        '''
        hq_info1 = hq.TYPE_STOCK_PRICE_INFO('sh600580',
                                            '卧龙电器',
                                            50.0,
                                            datetime.datetime.now())
        hq_info2 = hq.TYPE_STOCK_PRICE_INFO('sh600580',
                                            '卧龙电驱',
                                            50.0,
                                            datetime.datetime.now())
        with sessionmaker(self.db_engine)() as session:
            self.sina_hq.update_company_info(session, hq_info1)
            for stock_no, name in session.query(model.CompanyInfo.stock_no, model.CompanyInfo.name).all():
                LOGGER.info('----company info %s - %s', stock_no, name) 
            self.sina_hq.update_company_info(session, hq_info2)
            for stock_no, name in session.query(model.CompanyInfo.stock_no, model.CompanyInfo.name).all():
                LOGGER.info('----company info %s - %s', stock_no, name) 

    def test_update_price_info(self):
        '''测试更新价格信息
        '''
        hq_info1 = hq.TYPE_STOCK_PRICE_INFO('sh600580',
                                            '卧龙电器',
                                            30.0,
                                            datetime.datetime.now())
        hq_info2 = hq.TYPE_STOCK_PRICE_INFO('sh600580',
                                            '卧龙电驱',
                                            50.0,
                                            datetime.datetime.now())
        with sessionmaker(self.db_engine)() as session:
            self.sina_hq.update_price_info(session, hq_info1)
            for stock_no, price, create_time, update_time in session.query(model.HqHistory.stock_no, model.HqHistory.price, model.HqHistory.create_time, model.HqHistory.update_time).all():
                LOGGER.info('----price info %s %s %s %s', stock_no, price, create_time, update_time)
            time.sleep(3)
            self.sina_hq.update_price_info(session, hq_info2)
            for stock_no, price, create_time, update_time in session.query(model.HqHistory.stock_no, model.HqHistory.price, model.HqHistory.create_time, model.HqHistory.update_time).all():
                LOGGER.info('----price info %s %s %s %s', stock_no, price, create_time, update_time)

    def test_reclaim_resource(self):
        '''测试删除过期信息
        '''
        hq_hist = model.HqHistory()
        hq_hist.stock_no = '1234567'
        hq_hist.price = 10.0
        hq_hist.create_time = datetime.datetime.now() - datetime.timedelta(days=2)  #被删除
        hq_hist.update_time = datetime.datetime.now() 
 
        hq_hist1 = model.HqHistory()
        hq_hist1.stock_no = '1234567'
        hq_hist1.price = 10.0
        hq_hist1.create_time = datetime.datetime.now() 
        hq_hist1.update_time = datetime.datetime.now() 
        
        with sessionmaker(self.db_engine)() as session:
            session.add(hq_hist)
            session.add(hq_hist1)
            self.sina_hq.reclaim_resource(session)
            for stock_no, price, create_time, update_time in session.query(model.HqHistory.stock_no, model.HqHistory.price, model.HqHistory.create_time, model.HqHistory.update_time).all():
                LOGGER.info('----price info %s %s %s %s', stock_no, price, create_time, update_time)     
       
