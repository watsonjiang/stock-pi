# pricemon
# 股票价格监控

import asyncio
import logging
import sys

from stockpi.anl import anl_init
from stockpi.db import db_init, db_create_hq_subscriber
from stockpi.hq import hq_init
from stockpi.ntf import ntf_init

LOGGER = logging.getLogger(__name__)


def app_init_logging():
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


async def app_init():
    app_init_logging()
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
    asyncio.run(app_main())
