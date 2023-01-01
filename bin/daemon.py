#!/usr/bin/env python
# 启动一个后台精灵进程,
# 根据配置拉起stock-pi各个模块.

import argparse
import asyncio
import sys

from setproctitle import setproctitle

sys.path.append('..')
from stockpi import Daemon
from stockpi.app import app_init_logging, app_main

PID_FILE = 'pi.pid'


class PiDaemon(Daemon):

    def run(self):
        setproctitle("pi-daemon")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app_init_logging(False)
        asyncio.run(app_main())


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
