# 行情分析
import abc
import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd

from stockpi.db import db_get_company, db_get_hq_hist

LOGGER = logging.getLogger(__name__)

CHECK_INTERVAL_IN_SEC = 30


async def anl_init(stock_list, messenger):
    an = PriceRushAnalyzer(messenger, stock_list, 300, 3)
    all_analyser = CompositeAnalyzer([an])
    while True:  # 独立的分析循环.
        await asyncio.sleep(CHECK_INTERVAL_IN_SEC)
        LOGGER.info("start analyse. stock_list:%s", stock_list)
        await all_analyser.analyze()


class IAnalyzer(abc.ABC):
    '''分析器基类
    '''

    @abc.abstractmethod
    async def analyze(self):
        '''执行分析动作
        '''
        raise NotImplementedError


class CompositeAnalyzer(IAnalyzer):
    '''综合分析
    '''

    def __init__(self, analyzer_list):
        self.analyzer_list = analyzer_list

    async def do_analyze(self):
        for an in self.analyzer_list:
            await an.analyze()

    async def analyze(self):
        await self.do_analyze()


class PriceRushAnalyzer(IAnalyzer):
    ''' 价格异动分析。
        过去n分钟，价格涨跌幅超过百分之m
    '''

    def __init__(self, messenger, stock_list, time_win_in_sec=300, max_rush_in_percent=3):
        self.messenger = messenger
        self.stock_list = stock_list
        self.time_win_in_sec = time_win_in_sec
        self.max_rush_in_percent = max_rush_in_percent

    async def notice_rush(self, stock_no, min_price, max_price):
        company_info = await db_get_company(stock_no)
        now = datetime.now()
        rush_val = (max_price - min_price) / min_price * 100
        msg = f'{now} {company_info.name}({stock_no}) 过去{self.time_win_in_sec}秒价格变动超过{self.max_rush_in_percent}%. rush:{rush_val} min:{min_price} max:{max_price}'
        await self.messenger.send_msg(msg)

    async def do_analyze(self, stock_no):
        hist = await db_get_hq_hist(stock_no)
        hd = map(lambda x: [x.stock_no, x.price, x.create_time], hist)
        df = pd.DataFrame(hd, columns=['stock_no', 'price', 'create_time'])
        df = df.set_index('create_time')
        now = datetime.now()
        start_time = now - timedelta(seconds=self.time_win_in_sec)
        win = df['price'][start_time:now]
        if win.count() > 0:
            min_price = win.min()
            max_price = win.max()
            LOGGER.debug('stock_no %s price min: %s max: %s', stock_no, min_price, max_price)
            if (max_price - min_price) / min_price * 100 > self.max_rush_in_percent:  # 价格变动率
                await self.notice_rush(stock_no, min_price, max_price)

    async def analyze(self):
        ''' 分析
        '''
        LOGGER.debug('-------PriceRushAnalyzer %s', self.stock_list)
        for stock_no in self.stock_list:
            await self.do_analyze(stock_no)
