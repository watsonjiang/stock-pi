# pricemon
# 股票价格监控

import logging
import time
import asyncio

from . import hq
from . import model
from . import analyzer
from . import notify
from . import lcd

LOGGER = logging.getLogger(__name__)

class PriceMon(object):
    def __init__(self, stock_list, db_url):
        '''stock_list  string list. e.g. ['sh600580']
        '''
        self.db_engine = model.init(db_url)
        self.messenger = notify.init()
        self.hq = hq.init(self.db_engine, stock_list)
        self.an = analyzer.init(self.db_engine, stock_list, self.messenger)
        self.lcd_mgr = lcd.init(self.db_engine, stock_list)

    async def timer_task_check_hq(self):
        ''' 每秒更新一次行情信息
        '''
        while True:
            is_updated = await self.hq.update_hq()
            if is_updated:
                self.an.analyze()
            await asyncio.sleep(1)

    def mon(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.messenger.main_loop())
        loop.create_task(self.timer_task_check_hq())
        loop.create_task(self.lcd_mgr.timer_loop())
        loop.create_task(self.lcd_mgr.control_loop())
        #主循环
        try:
            loop.run_forever()
        except:
            LOGGER.exception("unexpected exception.")
        finally:
            loop.close()

        #     try:
        #         self.hq.update_hq()
        #         self.an.analyze()
        #         self.lcd_mgr.render_screen()
        #     except:
        #         LOGGER.exception("unexpected exception.")
        #     time.sleep(1)
