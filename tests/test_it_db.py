import logging
import sys
import unittest

from stockpi.db import db_init

LOGGER = logging.getLogger(__name__)


class ItDb(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")

    def test_init(self):
        db_init('sqlite+aiosqlite:///stock-pi.db')
