import os.path
import sys

from PyQt5.QtWidgets import QApplication


class StockMonApplication():
    """
    扩展app类,以便未来能够在app实例上附带应用其它属性.
    """
    _instance = None
    DIR_RESOURCE = 'resources'

    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.stock_dao = None
        self.hq_dao = None
        self.init()

    def init(self):
        # 防止缩小到系统栏时整个程序被杀掉
        self.qt_app.setQuitOnLastWindowClosed(False)


    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = StockMonApplication()

        return cls._instance

    @classmethod
    def get_base_dir(cls):
        """
        应用根目录.
        """
        return os.path.dirname(__file__)

    @classmethod
    def get_res_path(cls, filename):
        """
        获取资源文件绝对地址.
        """
        return os.path.join(cls.get_base_dir(), cls.DIR_RESOURCE, filename)

    def get_stock_dao(self):
        return self.stock_dao

    def get_hq_dao(self):
        return self.hq_dao
