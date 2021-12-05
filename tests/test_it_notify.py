import unittest
import logging
import sys
from stockpi.notify.dingtalk import DingTalkRobot
from stockpi.notify.feishu import FeishuRobot


LOGGER = logging.getLogger(__name__)


class ItDingTalkNotify(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")
        self.robot = DingTalkRobot(
            ak='076375a42fd3cecfb17141bdd88b2348021ebb961e2e6c5366d1650d0a699357',
            sk='SEC4c34a9f15cdb8431435861140e5713d0179a8d4506a9b64300a41aa872f45ea1'
        )

    def test_send_msg(self):
        self.robot.send_msg('hello world')


class ItFeishuNotify(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)-8s %(message)s")
        self.robot = FeishuRobot(
            ak='55d44b27-640e-4322-bda3-f036fa5558cf',
            sk='hxTZQI5aGfWkHu0FzPBjeh'
        )

    def test_send_msg(self):
        self.robot.send_msg('hello feishu')
