# pricemon
# 股票价格监控

import logging
import time
from datetime import datetime, timedelta

from sqlalchemy.sql.expression import delete
from . import dingtalk
from . import hq
from . import model

LOGGER = logging.getLogger(__name__)

class PriceMon(object):
    def __init__(self, stock_list):
        '''stock_list  string list. e.g. ['sh600580']
        '''
        self.stock_list = stock_list
        self.db_session_maker = model.init_session_maker('sqlite:///stock_db.sqlite3')
        self.dingRobot = dingtalk.DingRobot( 
                        ak='076375a42fd3cecfb17141bdd88b2348021ebb961e2e6c5366d1650d0a699357',
                        sk='SEC4c34a9f15cdb8431435861140e5713d0179a8d4506a9b64300a41aa872f45ea1'
                     )
        self._last_update_hq_time = 0
        self._last_anaysis_time = 0

    def update_company_info(self, db_session, hq_info):
        company_info = model.CompanyInfo()
        company_info.stock_no = hq_info.stock_no
        company_info.name = hq_info.name
        db_session.add(company_info)

    def update_price_info(self, db_session, hq_info):
        hq_hist = model.HqHistory()
        hq_hist.stock_no = hq_info.stock_no
        hq_hist.price = hq_info.price
        db_session.add(hq_hist)

    def update_hq(self, db_session):
        ''' 获取股票价格，存入存储
        '''
        hq_list = hq.get_price(self.stock_list)
        for stock_no in hq_list.keys():
            hq_info = hq_list[stock_no]
            self.update_company_info(db_session, hq_info) 
            self.update_price_info(db_session, hq_info)

    def analysis_1(self):
        ''' 1 过去5分钟价格涨幅超过3%
        '''
        for stock_no in self.stock_list:
            sql = '''select stock_no, price, ts 
                     from t_hq_hist where stock_no = ?

                  '''
            for row in self.db_conn.execute(sql, (stock_no,)):
                LOGGER.info('----row: %s', tuple(row))

    def analysis(self, db_session):
        ''' 分析
        '''
        for stock_no in self.stock_list:
            sql = '''select stock_no, price, ts 
                     from t_hq_hist where stock_no = ?

                  '''
            for row in self.db_conn.execute(sql, (stock_no,)):
                LOGGER.info('----row: %s', tuple(row))

    def reclaim_resurce(self, db_session):
        '''回收过期资源
        '''
        #删除过期行情历史
        expire_time = datetime.utcnow() - timedelta(hours=24)
        del_stat = delete(model.HqHistory).where(model.HqHistory.create_time < expire_time)
        db_session.delete(del_stat) 

    def should_update_hq(self):
        now = time.time()
        if now - self._last_update_hq_time > 10000:
            return True 
        return False

    def should_do_analysis(self):
        now = time.time()
        if now - self._last_anaysis_time > 60000:
            return True
        return False

    def mon(self):
        #主循环，数据更新 10秒一次
        while True:
            try:
                if self.should_update_hq():
                    with self.db_session_maker.begin() as db_session:
                        self.update_hq(db_session)
                        self.reclaim_resurce(db_session)
  
                if self.should_do_analysis():
                    with self.db_session_maker.begin() as db_session:
                        self.analysis(db_session)
            except:
                LOGGER.exception("unexpected exception.")
            time.sleep(1)
