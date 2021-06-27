# 行情分析
import logging
from collections import namedtuple
from datetime import datetime, timedelta
import time
import abc
import pandas as pd
from sqlalchemy.orm.session import sessionmaker
from stockpi.model import HqHistory

LOGGER = logging.getLogger(__name__)


def init(db_engine, stock_list, messenger):
    an = PriceRushAnalyzer(db_engine, stock_list, 300, 3)
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

    def __init__(self, analyzer_list, analyze_interval_in_sec=60):
        self.analyzer_list = analyzer_list
        self._analyze_interval_in_sec = analyze_interval_in_sec
        self._last_analyze_time = 0

    def do_analyze(self):
        for an in self.analyzer_list:
            an.analyze()

    def should_analyze(self):
        '''是否分析
        '''
        now = time.time()
        if now - self._last_analyze_time > self._analyze_interval_in_sec:
            self._last_analyze_time = now
            return True
        return False

    def analyze(self):
        if self.should_analyze():
            self.do_analyze()


class PriceRushAnalyzer(IAnalyzer):
    ''' 价格异动分析。
        过去n分钟，价格涨跌幅超过百分之m
    '''

    def __init__(self, db_engine, stock_list, time_win_in_sec, max_rush_in_percent):
        self.db_engine = db_engine
        self.stock_list = stock_list
        self.time_win_in_sec = time_win_in_sec
        self.max_rush_in_percent = max_rush_in_percent

    def analyze(self):
        ''' 分析
        '''
        LOGGER.info('-------PriceRushAnalyzer %s', self.stock_list)
        df = pd.read_sql_table(HqHistory.__tablename__, self.db_engine, parse_dates=['create_time', 'update_time'], index_col='id')
        start_time = datetime.now() - timedelta(seconds=self.time_win_in_sec)
        print(df.columns)
        print(df['price'])
        print(df['create_time'])
        #print(df.between_time(start_time.time(), datetime.now().time()).count())
        #print(df.loc[(df['create_time'] > start_time)].count())
        #LOGGER.info('--------desc: %s', price_series.count())
        #LOGGER.info('--------max: %s min: %s', price_series.max(), price_series.min())