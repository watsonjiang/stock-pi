# pricemon
# 股票价格监控

import logging
import sys
from . import hq, DingRobot
import time
import sqlite3
from datetime import datetime, timedelta

LOGGER = logging.getLogger(__name__)

class PriceMon(object):
    def __init__(self, stock_list):
        '''stock_list  string list. e.g. ['sh600580']
        '''
        self.stock_list = stock_list
        self.db_conn = sqlite3.connect(":memory:")
        self.init_db()
        self.dingRobot = DingRobot( 
                        ak='076375a42fd3cecfb17141bdd88b2348021ebb961e2e6c5366d1650d0a699357',
                        sk='SEC4c34a9f15cdb8431435861140e5713d0179a8d4506a9b64300a41aa872f45ea1'
                     )

    def init_db(self):
        '''初始化数据库
        '''
        sql = '''create table t_hq_hist(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_no varchar(20) NOT NULL,
                    price REAL,
                    ts timestamp DEFAULT CURRENT_TIMESTAMP
                ) 
            '''
        self.db_conn.execute(sql)
        sql = '''create table t_company_info(
                    stock_no varchar(20) PRIMARY KEY,
                    name varchar(50),
                    ts timestamp DEFAULT CURRENT_TIMESTAMP
                )
            '''
        self.db_conn.execute(sql)

    def update_company_info(self, hq_info):
        sql = '''insert or replace into t_company_info(stock_no, name) values(?, ?)
            '''
        self.db_conn.execute(sql, (hq_info.stock_no, hq_info.name))

    def update_price_info(self, hq_info):
        sql = '''insert into t_hq_hist(stock_no, price) values(?, ?)
            '''
        self.db_conn.execute(sql, (hq_info.stock_no, hq_info.price))
        
        expire_time = datetime.utcnow() - timedelta(minutes=1) 
        LOGGER.info('-----expire_time:%s', expire_time)
        sql = '''delete from t_hq_hist where ts < ?'''
        self.db_conn.execute(sql, (expire_time,))
        

    def update_hq(self):
        ''' 获取股票价格，存入存储
        '''
        hq_list = hq.get_price(self.stock_list)
        for stock_no in hq_list.keys():
            hq_info = hq_list[stock_no]
            LOGGER.debug('-----update hq %s', hq_info)
            self.update_company_info(hq_info) 
            self.update_price_info(hq_info)

    def analysis(self):
        ''' 1 过去5分钟价格涨幅超过3%
        '''
        sql = '''select stock_no, price, ts from t_hq_hist where stock_no = ? order by id desc'''
        for stock_no in self.stock_list:
            for row in self.db_conn.execute(sql, (stock_no,)):
                LOGGER.info('----row: %s', tuple(row))

    def mon(self):
        while True:
            try:
                self.update_hq()
                self.analysis()
            except:
                LOGGER.exception("unexpected exception.")
            time.sleep(10)
