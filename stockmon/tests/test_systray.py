from unittest import TestCase

from stockmon.app import StockMonApplication
from stockmon.views.systray import SysTrayView


class TestSysTrayView(TestCase):
    def test_tray(self):
        '''
        加载tray icon
        '''
        app = StockMonApplication.instance()
        SysTrayView()
        app.exec_()

