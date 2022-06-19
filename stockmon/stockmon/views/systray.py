from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu

from stockmon.app import StockMonApplication


class SysTrayView(QSystemTrayIcon):
    def __init__(self):
        super(SysTrayView, self).__init__()
        self.init()

    def init(self):
        icon = QIcon("stock.png")
        self.setIcon(icon)
        self.setVisible(True)
        menu = self.build_ctx_menu()
        self.setContextMenu(menu)

    def build_ctx_menu(self):
        menu = QMenu()
        quit_action = menu.addAction('Quit')
        quit_action.triggered.connect(StockMonApplication.instance().quit)
        return menu


