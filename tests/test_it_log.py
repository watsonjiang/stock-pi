import logging
import sys
import time
import unittest
from logging.handlers import SocketHandler

LOGGER = logging.getLogger(__name__)


class ItPiLog(unittest.TestCase):

    def setUp(self):
        console_handler = logging.StreamHandler(stream=sys.stdout)
        sock_handler = SocketHandler("/var/run/stock-pi/log.sock", None)
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s",
                            handlers=(console_handler, sock_handler)
                            )
        LOGGER.error('--------setup')

    def test_log(self):
        for i in range(0, 10):
            LOGGER.error('---------log log')
            time.sleep(1)
