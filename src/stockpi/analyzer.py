#行情分析
import logging
import requests
import re
from collections import namedtuple
from datetime import datetime

from sqlalchemy.sql.expression import select

from stockpi.model import HqHistory

LOGGER = logging.getLogger(__name__)

class PriceRushAnalyser:
    ''' 价格异动分析。
        过去n分钟，价格涨跌幅超过百分之m
    '''
    def __init__(self, time_win_in_sec, max_rush_in_percent):
        self.time_win_in_sec = time_win_in_sec
        self.max_rush_in_percent = max_rush_in_percent

    def analysis(self, stock_no, db_session):
        ''' 分析
        '''
        select(HqHistory).filter_by()