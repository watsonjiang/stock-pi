import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidget, QListWidgetItem
from PyQt5.uic import loadUi

from stockmon.app import StockMonApplication


class HqListView(QDialog):
    HQ_PATTERN = '{:8}\t{:4.2f}\t{:4.2f}%'

    def __init__(self):
        super(HqListView, self).__init__()
        self.init()

    def init(self):
        ui_path = StockMonApplication.get_res_path('win_hq.ui')
        loadUi(ui_path, self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.init_list_widget(self.hq_info_list)

    def init_list_widget(self, w: QListWidget):
        w.itemClicked.connect(self.on_item_clicked)
        header = QListWidgetItem('{}\t{}\t{}'.format('股票', '价格', '涨幅'))
        header.setBackground(Qt.lightGray)
        header.setForeground(Qt.black)

        w.addItem(header)
        item = QListWidgetItem(HqListView.HQ_PATTERN.format('卧龙电驱', 13.4, 5.23))
        item.setData(Qt.UserRole, 'wldq')
        item.setForeground(Qt.darkRed)
        w.addItem(item)
        item = QListWidgetItem(HqListView.HQ_PATTERN.format('以岭药业', 32.43, 4.22))
        item.setForeground(Qt.darkGreen)
        item.setData(Qt.UserRole, 'ylyy')
        w.addItem(item)

    def on_item_clicked(self, item:QListWidgetItem):
        data = item.data(Qt.UserRole)
        if 'wldq' == data:
            webbrowser.open_new_tab('www.sina.com.cn')
        elif 'ylyy' == data:
            webbrowser.open_new_tab('www.baidu.com')

