#!/usr/bin/env python
import logging, sys
from logging.handlers import TimedRotatingFileHandler
from stockpi import PriceMon, Daemon
import argparse

STOCK_LIST = ['sh600580', 'sh600316', 'sz002603', 'sz000568']

PID_FILE = 'pricemon.pid'
LOG_FILE = 'pricemon.log'
LOG_LEVEL = logging.DEBUG
STOCK_DB = 'sqlite:///stock_db.sqlite3'

def init_logging():
    logging.basicConfig(stream=sys.stdout,
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)-8s %(message)s")

def init_logging_file():
    handler = TimedRotatingFileHandler(LOG_FILE, when='D')
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)

class Launcher(Daemon):
    def run(self):
        pricemon = PriceMon(STOCK_LIST, STOCK_DB)
        pricemon.mon()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', help='start|stop|restart|run')
    args = parser.parse_args()
    if args.cmd == 'start':
        init_logging_file()
        Launcher(PID_FILE).start()
    elif args.cmd == 'stop':
        Launcher(PID_FILE).stop()
    elif args.cmd == 'restart':
        Launcher(PID_FILE).restart()
    elif args.cmd == 'run':
        init_logging()
        Launcher(PID_FILE).run()
    else:
        print('error: Invalid cmd argument.', args.cmd)
        parser.print_help()