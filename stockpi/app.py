# pricemon
# 股票价格监控

import asyncio
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from stockpi.anl import anl_init
from stockpi.db import db_init, db_create_hq_subscriber
from stockpi.hq import hq_init
from stockpi.ntf import ntf_init

LOGGER = logging.getLogger(__name__)


def app_init_logging(log_to_console=False):
    handlers = [TimedRotatingFileHandler('pi.log', when='D', backupCount=5)]
    if log_to_console:
        handlers.append(logging.StreamHandler(stream=sys.stdout))
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        handlers=handlers)


async def app_init():
    asyncio.create_task(db_init())
    s = db_create_hq_subscriber()
    asyncio.create_task(hq_init(['sh600580'], s))
    messenger = ntf_init()
    asyncio.create_task(anl_init(['sh600580'], messenger))


async def app_main():
    """
    主程序入口.
    """
    await app_init()
    # 主循环
    try:
        while True:
            await asyncio.sleep(1)
    except:
        LOGGER.exception("unexpected exception.")


if __name__ == "__main__":
    app_init_logging(True)
    asyncio.run(app_main())
