# 行情分析
import logging
from collections import namedtuple
from datetime import datetime, timedelta
import abc
import pandas as pd
from sqlalchemy.orm.session import sessionmaker
from stockpi.model import CompanyInfo, HqHistory
from sqlalchemy.sql import select

LOGGER = logging.getLogger(__name__)


def init(db_engine, stock_list, messenger):
    an = PriceRushAnalyzer(db_engine, messenger, stock_list, 300, 3)
    return CompositeAnalyzer([an])


class IAnalyzer(abc.ABC):
    '''分析器基类
    '''
    @abc.abstractmethod
    def analyze(self):
        '''执行分析动作
        '''
        raise NotImplementedError


class CompositeAnalyzer(IAnalyzer):
    '''综合分析
    '''

    def __init__(self, analyzer_list):
        self.analyzer_list = analyzer_list

    def do_analyze(self):
        for an in self.analyzer_list:
            an.analyze()

    def analyze(self):
        self.do_analyze()


class PriceRushAnalyzer(IAnalyzer):
    ''' 价格异动分析。
        过去n分钟，价格涨跌幅超过百分之m
    '''

    def __init__(self, db_engine, messenger, stock_list, time_win_in_sec=300, max_rush_in_percent=3):
        self.db_engine = db_engine
        self.messenger = messenger
        self.stock_list = stock_list
        self.time_win_in_sec = time_win_in_sec
        self.max_rush_in_percent = max_rush_in_percent

    def notice_rush(self, stock_no, min_price, max_price):
        with sessionmaker(self.db_engine)() as session:
            company_info = session.query(CompanyInfo).filter(CompanyInfo.stock_no == stock_no).one_or_none()
            now = datetime.now()
            rush_val = (max_price - min_price) / min_price * 100
            msg = f'{now} {company_info.name}({stock_no}) 过去{self.time_win_in_sec}秒价格变动超过{self.max_rush_in_percent}%. rush:{rush_val} min:{min_price} max:{max_price}'
            self.messenger.send_msg(msg)

    def do_analyze(self, stock_no):
        st = select(HqHistory).where(HqHistory.stock_no == stock_no)
        df = pd.read_sql_query(st, self.db_engine, parse_dates=['create_time', 'update_time'])
        df = df.set_index('create_time')
        now = datetime.utcnow()
        start_time = now - timedelta(seconds=self.time_win_in_sec)
        win = df['price'][start_time:now]
        #LOGGER.info('-----start_time:%s  now:%s', start_time, datetime.utcnow())
        #LOGGER.info('----win %s', win)
        if win.count() > 0:
            min_price = win.min()
            max_price = win.max()
            LOGGER.debug('stock_no %s price min: %s max: %s', stock_no, min_price, max_price)
            if (max_price - min_price) / min_price * 100 > self.max_rush_in_percent: #价格变动率
                self.notice_rush(stock_no, min_price, max_price)

    def analyze(self):
        ''' 分析
        '''
        LOGGER.debug('-------PriceRushAnalyzer %s', self.stock_list)
        for stock_no in self.stock_list:
            self.do_analyze(stock_no)