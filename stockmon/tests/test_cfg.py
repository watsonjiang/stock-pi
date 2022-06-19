from unittest import TestCase

from stockmon.app import StockMonApplication
from stockmon.model import StockDao
from stockmon.views.cfg import HqCfgView


class TestHqCfgView(TestCase):
    def test_view(self):
        app = StockMonApplication.instance()
        app.stock_dao = StockDao()
        view = HqCfgView()

        view.show()
        app.exec_()