from unittest import TestCase

from stockmon.app import StockMonApplication
from stockmon.model import StockDao
from stockmon.views.hq import HqListView


class TestHqListView(TestCase):
    def test_view(self):
        app = StockMonApplication.instance()
        app.stock_dao = StockDao()
        view = HqListView()

        view.show()
        app.exec_()