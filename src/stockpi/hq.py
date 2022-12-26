# 股票行情
import abc
import asyncio
import logging
import re
from collections import namedtuple
from datetime import datetime, time

import aiohttp

LOGGER = logging.getLogger(__name__)

# 价格信息结构
TYPE_STOCK_PRICE_INFO = namedtuple('StockPrice', ['stock_no', 'name', 'price', 'update_time'])

REQ_TIMEOUT_IN_SEC = (1, 1)

STOCK_NO_PATTEN = re.compile(r'.*hq_str_([a-z0-9]+).*')

HQ_UPDATE_INTERVAL_IN_SEC = 10


async def hq_init(stock_list, subscriber):
    hq = SinaHq(stock_list)
    while True:  # 行情信息主循环.
        await asyncio.sleep(HQ_UPDATE_INTERVAL_IN_SEC)
        if _is_market_open(datetime.now()):
            await hq.update_hq(subscriber)


def _is_market_open(dt):
    if 0 <= dt.weekday() < 5:
        t = dt.time()
        if time(hour=9, minute=30, second=0) < t < time(hour=12, minute=0, second=0):
            return True
        if time(hour=13, minute=30, second=0) < t < time(hour=15, minute=0, second=0):
            return True
    return False


class IHq(abc.ABC):
    '''行情信息获取基类
    '''

    @abc.abstractmethod
    def update_hq(self, subscriber):
        '''获取行情信息并通知给subscriber
        '''
        raise NotImplementedError


class SinaHq(IHq):
    """新浪行情获取
    """

    STOCK_HQ_INFO_PATTEN = re.compile(r'.*"(.*)";$')

    def __init__(self, stock_list):
        self.stock_list = stock_list

    async def update_hq(self, subscriber):
        """ 获取股票价格, 通知给subscriber
        """
        hq_list = await self.get_price(self.stock_list)

        for hq_info in hq_list.values():
            if subscriber:
                await subscriber(hq_info)

    def match_stock_no(self, line):
        m = STOCK_NO_PATTEN.match(line)
        if m:
            return m.group(1)

    def match_stock_hq_info(self, line):
        m = SinaHq.STOCK_HQ_INFO_PATTEN.match(line)
        if m:
            hq_str = m.group(1)
            return hq_str.split(',')

    def get_update_time(self, stock_hq_info):
        date = stock_hq_info[30]
        time = stock_hq_info[31]
        return datetime.strptime('{} {}'.format(date, time), '%Y-%m-%d %H:%M:%S')

    def parse_price(self, sina_price_text):
        """
        解析sina的响应数据
        """
        rst = {}
        lines = sina_price_text.split('\n')
        # line by line
        for line in lines:
            line = line.strip('\n')
            if not line:
                # empty line
                continue
            # match stockNojson
            stock_no = self.match_stock_no(line)
            # match detail
            stock_hq_info = self.match_stock_hq_info(line)
            if not stock_no or not stock_hq_info:
                LOGGER.warning('parse failed. line:%s', line)
                continue
                
            rst[stock_no] = TYPE_STOCK_PRICE_INFO(stock_no,
                stock_hq_info[0],
                stock_hq_info[3], 
                self.get_update_time(stock_hq_info))
            LOGGER.info('got price info %s - %s', stock_no, rst[stock_no]) 
        return rst

    async def get_price(self, stock_list):
        """
        调用新浪股票行情接口，返回股票价格信息.
        @return
        """
        if not stock_list:
            LOGGER.error('stock list is empty!')
            return []
        url = 'http://hq.sinajs.cn/list={}'.format(','.join(stock_list))
        headers = {"Referer": "http://finance.sina.com.cn"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as r:
                body = await r.text()
                if 200 != r.status:
                    LOGGER.warning("request failed. code:%s body:%s", r.status, body)
                    return []
                else:
                    LOGGER.debug('request succeed. url:%s body:%s', url, body)
                    return self.parse_price(body)
