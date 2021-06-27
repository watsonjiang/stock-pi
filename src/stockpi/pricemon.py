# pricemon
# 股票价格监控

import logging
import time

from . import hq
from . import model
from . import analyzer
from . import notify

LOGGER = logging.getLogger(__name__)

class PriceMon(object):
    def __init__(self, stock_list, db_url):
        '''stock_list  string list. e.g. ['sh600580']
        '''
        self.db_engine = model.init(db_url)
        self.messenger = notify.init()
        self.hq = hq.init(self.db_engine, stock_list)
        self.an = analyzer.init(self.db_engine, stock_list, self.messenger)

    def mon(self):
        #主循环，数据更新 10秒一次
        while True:
            try:
                self.hq.update_hq()
                self.an.analyze()
            except:
                LOGGER.exception("unexpected exception.")
            time.sleep(1)
