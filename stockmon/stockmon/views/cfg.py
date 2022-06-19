from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QCompleter
from PyQt5.uic import loadUi

from stockmon.app import StockMonApplication


class HqCfgView(QDialog):

    def __init__(self):
        super(HqCfgView, self).__init__()
        self.stock_dao = StockMonApplication.instance().get_stock_dao()
        self.init()

    def init(self):
        ui_path = StockMonApplication.get_res_path('win_cfg.ui')
        loadUi(ui_path, self)
        self.setWindowIcon(QIcon(StockMonApplication.get_res_path('stock.png')))
        self.setWindowFlags(self.windowFlags() & ~ Qt.WindowContextHelpButtonHint)
        self.add_btn.clicked.connect(self.on_add)
        all_codes = [s.code for s in self.stock_dao.get_all()]
        completer = QCompleter(all_codes)
        self.stock_input.setCompleter(completer)
        self.stock_list.itemDoubleClicked.connect(self.on_remove)

    def on_add(self):
        """
        添加股票代码
        """
        code = self.stock_input.text()
        s = self.stock_dao.get_by_code(code)
        item = QListWidgetItem(s.name)
        self.stock_list.addItem(item)

    def on_remove(self, item:QListWidgetItem):
        idx = self.stock_list.row(item)
        self.stock_list.takeItem(idx)
