# 股票行情
import logging
import requests
import re
from collections import namedtuple
from datetime import datetime

LOGGER = logging.getLogger(__name__)

TYPE_STOCK_PRICE_INFO = namedtuple('StockPrice', ['stock_no', 'name', 'price', 'update_time'])

STOCK_NO_PATTEN = re.compile(r'.*hq_str_([a-z0-9]+).*')
def match_stock_no(line):
    m = STOCK_NO_PATTEN.match(line)
    if m:
        return m.group(1)

STOCK_HQ_INFO_PATTEN = re.compile(r'.*"(.*)";$')
def match_stock_hq_info(line):
    m = STOCK_HQ_INFO_PATTEN.match(line)
    if m:
        hq_str = m.group(1)
        return hq_str.split(',')

def get_update_time(stock_hq_info):
    date = stock_hq_info[30]
    time = stock_hq_info[31]
    return datetime.strptime('{} {}'.format(date, time), '%Y-%m-%d %H:%M:%S')

def parse_price(sina_price_text):
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
        # match stockNo
        stock_no = match_stock_no(line)
        # match detail
        stock_hq_info = match_stock_hq_info(line)
        if not stock_no or not stock_hq_info:
            LOGGER.warning('parse failed. line:%s', line)
            continue
            
        rst[stock_no] = TYPE_STOCK_PRICE_INFO(stock_no,
            stock_hq_info[0],
            stock_hq_info[3], 
            get_update_time(stock_hq_info))
        
    return rst

def get_price(stock_list):
    '''
    调用新浪股票行情接口，返回股票价格信息.
    @return
    '''
    if not stock_list:
        LOGGER.error('stock list is empty!')
        return []
    url = 'http://hq.sinajs.cn/list={}'.format(','.join(stock_list))
    r = requests.get(url)
    if not r.ok:
        LOGGER.warning("request failed. code:%s body:%s", r.status_code, r.text)
        return []
    LOGGER.debug('request succeed. url:%s body:%s', url, r.text)
    return parse_price(r.text)

