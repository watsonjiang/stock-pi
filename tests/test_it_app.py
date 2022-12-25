import asyncio
import logging
import sys
import unittest

from stockpi.app import app_main


class ItApp(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")

    def test_main(self):
        asyncio.run(app_main())
