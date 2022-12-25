#!/usr/bin/env python
# 启动一个后台精灵进程,
# 根据配置拉起stock-pi各个模块.

import argparse
import asyncio
import sys

from setproctitle import setproctitle

sys.path.append('../src')
from stockpi import Daemon

PID_FILE = '/var/run/stock-pi/pi-daemon.pid'

STOCK_DB = 'sqlite+aiosqlite:///stock_pi.sqlite3'

STOCK_LIST = ['sh600580']


class PiDaemon(Daemon):
    async def aio_main(self):
        await hq_init(STOCK_LIST, )

    def run(self):
        setproctitle("pi-daemon")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.run(self.aio_main)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', help='start|stop|restart', choices=['start', 'stop', 'restart'])
    args = parser.parse_args()
    if args.cmd == 'start':
        PiDaemon(PID_FILE).start()
    elif args.cmd == 'stop':
        PiDaemon(PID_FILE).stop()
    elif args.cmd == 'restart':
        PiDaemon(PID_FILE).restart()
    else:
        print('error: Invalid cmd argument.', args.cmd)
        parser.print_help()
