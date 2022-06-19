# 股票行情
import abc
import logging
import re
import time
from collections import namedtuple
from datetime import datetime, timedelta

import aiohttp
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import delete

from . import model

LOGGER = logging.getLogger(__name__)

#价格信息结构
TYPE_STOCK_PRICE_INFO = namedtuple('StockPrice', ['stock_no', 'name', 'price', 'update_time'])

REQ_TIMEOUT_IN_SEC = (1, 1)

STOCK_NO_PATTEN = re.compile(r'.*hq_str_([a-z0-9]+).*')

def init(db_engine, stock_list):
    return SinaHq(db_engine, stock_list)

class IHq(abc.ABC):
    '''行情信息获取基类
    '''
    @abc.abstractmethod
    def get_hq(self, code):
        '''获取行情信息
        '''
        raise NotImplementedError

class SinaHq(IHq):
    STOCK_HQ_INFO_PATTEN = re.compile(r'.*"(.*)";$')
    '''新浪行情获取实现
    '''
    def __init__(self, db_engine, stock_list, hq_update_interval_in_sec = 10):
        self.stock_list = stock_list
        self.db_engine = db_engine
        self.session_maker = sessionmaker(bind=db_engine)
        self._last_update_hq_time = time.time()
        self._hq_update_interval_in_sec = hq_update_interval_in_sec

    def should_update_hq(self):
        '''是否更新行情
        '''
        now = time.time()
        if now - self._last_update_hq_time > self._hq_update_interval_in_sec:
            self._last_update_hq_time = now
            return True 
        return False

    async def do_update(self):
        ''' 获取股票价格，存入存储
        '''
        hq_list = await self.get_price(self.stock_list)

        for hq_info in hq_list.values():
            if float(hq_info.price) > 0: #过滤开盘前准备数据
                with self.session_maker.begin() as session:  
                    self.update_company_info(session, hq_info) 
                    self.update_price_info(session, hq_info)

        with self.session_maker.begin() as session:
            self.reclaim_resource(session)

    async def update_hq(self):
        ''' 检查是否需要更新，如果是，更新数据库
        '''
        if self.should_update_hq():
           await self.do_update()
           return True
        return False

    def update_company_info(self, db_session, hq_info):
        '''更新公司信息
        '''
        company_info = db_session.query(model.CompanyInfoEntity).filter(model.CompanyInfoEntity.stock_no == hq_info.stock_no).one_or_none()
        if company_info:
            company_info.name = hq_info.name
        else: 
            company_info = model.CompanyInfoEntity()
            company_info.stock_no = hq_info.stock_no
            company_info.name = hq_info.name
            db_session.add(company_info)

    def update_price_info(self, db_session, hq_info):
        '''更新价格信息
        '''
        hq_hist = model.HqHistoryEntity()
        hq_hist.stock_no = hq_info.stock_no
        hq_hist.price = hq_info.price
        db_session.add(hq_hist)

    def reclaim_resource(self, db_session):
        '''回收过期资源
        '''
        #删除过期行情历史
        expire_time = datetime.utcnow() - timedelta(hours=24)
        del_stat = delete(model.HqHistoryEntity).where(model.HqHistoryEntity.create_time < expire_time)
        db_session.execute(del_stat) 

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
        '''
        解析sina的响应数据
        '''
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
        '''
        调用新浪股票行情接口，返回股票价格信息.
        @return
        '''
        if not stock_list:
            LOGGER.error('stock list is empty!')
            return []
        url = 'http://hq.sinajs.cn/list={}'.format(','.join(stock_list))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                body = await r.text()
                if 200 != r.status:
                    LOGGER.warning("request failed. code:%s body:%s", r.status, body)
                    return []
                else:
                    LOGGER.debug('request succeed. url:%s body:%s', url, body) 
                    return self.parse_price(body)

